import os
import random
import secrets
import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from functools import wraps

import jwt
from flask import Blueprint, request, jsonify, current_app, g
from models import db, User, OtpCode, RefreshToken

log = logging.getLogger(__name__)

auth_bp = Blueprint("auth", __name__)

BREVO_SMTP_HOST = "smtp-relay.brevo.com"
BREVO_SMTP_PORT = 587
BREVO_SMTP_USER = os.environ.get("BREVO_SMTP_USER", "")
BREVO_SMTP_KEY  = os.environ.get("BREVO_SMTP_KEY",  "")
EMAIL_FROM      = "KIU Portal <noreply@kiu.ac.ug>"

OTP_EXPIRY_MINUTES          = 10
OTP_RESEND_COOLDOWN_SECONDS = 60

# ---------------------------------------------------------------------------
# BUG FIX — JWT lifetime
# The original value was 15 minutes.  With that setting, every navigation
# click after the first quarter-hour hit an expired JWT → 401 on any API
# call → fetch-patch redirected to /login → the login page called logout
# (a bug introduced in the previous patch) → full session wipe on every
# navigation.  8 hours covers a full working session.  The 7-day refresh
# token handles longer sessions transparently.
# ---------------------------------------------------------------------------
JWT_ACCESS_TOKEN_HOURS = 8

# ---------------------------------------------------------------------------
# User-based rate limiting
# ---------------------------------------------------------------------------

_ip_counters: dict = {}


def _get_redis():
    try:
        import redis as redis_lib
        url = os.environ.get("RATE_LIMIT_STORAGE_URI", "")
        if url.startswith("redis://") or url.startswith("rediss://"):
            return redis_lib.from_url(url, socket_connect_timeout=1)
    except Exception:
        pass
    return None


def user_rate_limit(max_requests: int = 100, window_seconds: int = 3600):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            user     = getattr(g, "current_user", None)
            identity = f"user:{user.id}" if user else (request.remote_addr or "unknown")
            slot     = int(datetime.utcnow().timestamp()) // window_seconds
            key      = f"rl:{f.__name__}:{identity}:{slot}"
            try:
                r = _get_redis()
                if r is not None:
                    count = r.incr(key)
                    if count == 1:
                        r.expire(key, window_seconds)
                else:
                    _ip_counters[key] = _ip_counters.get(key, 0) + 1
                    count = _ip_counters[key]
                if count > max_requests:
                    return jsonify({
                        "error": "Rate limited",
                        "message": (
                            f"Too many requests. Max {max_requests} per "
                            f"{window_seconds // 60} minutes."
                        ),
                        "retryAfter": window_seconds,
                    }), 429
            except Exception:
                pass  # fail open
            return f(*args, **kwargs)
        return wrapper
    return decorator


# ---------------------------------------------------------------------------
# Token helpers
# ---------------------------------------------------------------------------

def generate_token(user_id, role):
    jwt_secret = current_app.config.get("SECRET_KEY", "")
    payload = {
        "userId": user_id,
        "role":   role,
        "exp":    datetime.utcnow() + timedelta(hours=JWT_ACCESS_TOKEN_HOURS),
        "type":   "access",
    }
    return jwt.encode(payload, jwt_secret, algorithm="HS256")


def generate_refresh_token(user_id):
    token = secrets.token_urlsafe(64)
    rt    = RefreshToken(
        user_id=user_id,
        token=token,
        expires_at=datetime.utcnow() + timedelta(days=7),
        user_agent=request.headers.get("User-Agent", ""),
        ip_address=request.remote_addr,
    )
    db.session.add(rt)
    db.session.commit()
    return token


def _set_auth_cookie(response, token):
    is_prod = os.environ.get("FLASK_ENV", "").lower() == "production"
    response.set_cookie(
        "auth_token",
        value=token,
        httponly=True,
        secure=is_prod,
        samesite="Strict",
        max_age=JWT_ACCESS_TOKEN_HOURS * 3600,
        path="/",
    )
    return response


def _set_refresh_cookie(response, token):
    is_prod = os.environ.get("FLASK_ENV", "").lower() == "production"
    response.set_cookie(
        "refresh_token",
        value=token,
        httponly=True,
        secure=is_prod,
        samesite="Strict",
        max_age=7 * 24 * 3600,
        path="/",   # path="/" so fetch-patch can reach /api/auth/refresh with it
    )
    return response


def _clear_auth_cookies(response):
    response.delete_cookie("auth_token",    path="/")
    response.delete_cookie("refresh_token", path="/")
    return response


def verify_token(token):
    jwt_secret = current_app.config.get("SECRET_KEY", "")
    return jwt.decode(token, jwt_secret, algorithms=["HS256"])


def get_current_user():
    token = request.cookies.get("auth_token")
    if not token:
        ah = request.headers.get("Authorization", "")
        if ah.startswith("Bearer "):
            token = ah[7:]
    if not token:
        return None, "No token provided"
    try:
        payload = verify_token(token)
        user    = db.session.get(User, payload["userId"])
        if not user:
            return None, "User not found"
        return user, None
    except jwt.ExpiredSignatureError:
        return None, "Token expired"
    except jwt.InvalidTokenError:
        return None, "Invalid token"


# ---------------------------------------------------------------------------
# OTP helpers
# ---------------------------------------------------------------------------

def _generate_otp():
    return str(random.randint(100000, 999999))


def _otp_debug_enabled() -> bool:
    raw = os.environ.get("OTP_DEBUG", "").strip().lower()
    if raw == "":
        return os.environ.get("FLASK_ENV", "").lower() != "production"
    return raw in ("1", "true", "yes", "on")


def _print_otp_to_terminal(email, otp, full_name=""):
    if not _otp_debug_enabled():
        return
    line = "=" * 56
    msg  = f"\n{line}\n  KIU PORTAL — OTP VERIFICATION CODE\n{line}\n"
    if full_name:
        msg += f"  Name    : {full_name}\n"
    msg += (
        f"  Email   : {email}\n"
        f"  OTP     : {otp}\n"
        f"  Expires : {OTP_EXPIRY_MINUTES} minutes\n"
        f"{line}\n"
    )
    print(msg, flush=True)


def _send_otp_email(to_email, otp, full_name=""):
    if not BREVO_SMTP_KEY:
        log.warning("BREVO_SMTP_KEY not set — email not sent (see terminal for OTP)")
        return False
    greeting  = f"Dear {full_name}," if full_name else "Hello,"
    html_body = f"""
    <div style="font-family:Arial,sans-serif;max-width:480px;margin:0 auto;padding:32px;
                border:1px solid #e5e7eb;border-radius:12px;">
      <h2 style="color:#1e3a5f;text-align:center;">Kampala International University</h2>
      <p style="color:#374151;">{greeting}</p>
      <p style="color:#374151;">Your One-Time Password (OTP):</p>
      <div style="text-align:center;margin:32px 0;">
        <span style="font-size:40px;font-weight:bold;letter-spacing:12px;color:#1e3a5f;
                     background:#f0f4ff;padding:16px 32px;border-radius:8px;
                     display:inline-block;">{otp}</span>
      </div>
      <p style="color:#6b7280;font-size:14px;">
        Expires in <strong>{OTP_EXPIRY_MINUTES} minutes</strong>. Do not share it.
      </p>
    </div>
    """
    msg = MIMEMultipart("alternative")
    msg["Subject"] = "Your KIU Portal Verification Code"
    msg["From"]    = EMAIL_FROM
    msg["To"]      = to_email
    msg.attach(MIMEText(html_body, "html"))
    try:
        with smtplib.SMTP(BREVO_SMTP_HOST, BREVO_SMTP_PORT, timeout=10) as smtp:
            smtp.ehlo(); smtp.starttls()
            smtp.login(BREVO_SMTP_USER, BREVO_SMTP_KEY)
            smtp.sendmail(EMAIL_FROM, to_email, msg.as_string())
        log.info("Email sent to %s via Brevo", to_email)
        return True
    except Exception as exc:
        log.error("Brevo email failed for %s: %s", to_email, exc)
        return False


def _create_and_dispatch_otp(user):
    OtpCode.query.filter_by(user_id=user.id, is_used=False).update({"is_used": True})
    db.session.flush()
    code = _generate_otp()
    otp  = OtpCode(
        user_id=user.id, code=code,
        expires_at=datetime.utcnow() + timedelta(minutes=OTP_EXPIRY_MINUTES),
        is_used=False,
    )
    db.session.add(otp)
    db.session.commit()
    full_name = f"{user.first_name} {user.last_name}"
    _print_otp_to_terminal(user.email, code, full_name)
    _send_otp_email(user.email, code, full_name)
    return otp


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Bad request", "message": "No JSON body provided"}), 400

    email       = data.get("email",       "").strip().lower()
    password    = data.get("password",    "")
    first_name  = data.get("firstName",   "").strip()
    last_name   = data.get("lastName",    "").strip()
    phone       = data.get("phone",       "")
    national_id = data.get("nationalId",  "")
    role        = data.get("role",        "applicant")

    if not email or not password or not first_name or not last_name:
        return jsonify({"error": "Validation error",
                        "message": "email, password, firstName and lastName are required"}), 400

    from email_validator import validate_email, EmailNotValidError
    try:
        validate_email(email, check_deliverability=False)
    except EmailNotValidError:
        return jsonify({"error": "Validation error", "message": "Invalid email address"}), 400

    if len(password) < 8:
        return jsonify({"error": "Validation error",
                        "message": "Password must be at least 8 characters"}), 400
    if not any(c.isupper() for c in password):
        return jsonify({"error": "Validation error",
                        "message": "Password must contain at least one uppercase letter"}), 400
    if not any(c.islower() for c in password):
        return jsonify({"error": "Validation error",
                        "message": "Password must contain at least one lowercase letter"}), 400
    if not any(c.isdigit() for c in password):
        return jsonify({"error": "Validation error",
                        "message": "Password must contain at least one digit"}), 400

    if role not in ("applicant", "finalist"):
        role = "applicant"

    if User.query.filter_by(email=email).first():
        return jsonify({"error": "Conflict",
                        "message": "An account with this email already exists"}), 409

    user = User(
        email=email, first_name=first_name, last_name=last_name,
        phone=phone or None, national_id=national_id or None,
        role=role, is_verified=False,
    )
    user.set_password(password)
    db.session.add(user)
    db.session.flush()
    _create_and_dispatch_otp(user)

    return jsonify({
        "message": "Account created. Please check your email (or terminal) for your 6-digit OTP.",
        "email": email,
        "needsVerification": True,
    }), 201


@auth_bp.route("/verify-otp", methods=["POST"])
def verify_otp():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Bad request", "message": "No JSON body"}), 400

    email = data.get("email", "").strip().lower()
    code  = data.get("code",  "").strip()

    if not email or not code:
        return jsonify({"error": "Validation error", "message": "email and code are required"}), 400

    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"error": "Not found", "message": "No account found for this email"}), 404

    if user.is_verified:
        return jsonify({"message": "Already verified. Please sign in."}), 200

    otp = (
        OtpCode.query
        .filter_by(user_id=user.id, code=code, is_used=False)
        .filter(OtpCode.expires_at > datetime.utcnow())
        .first()
    )
    if not otp:
        expired = OtpCode.query.filter_by(user_id=user.id, code=code, is_used=False).first()
        if expired:
            return jsonify({"error": "OTP expired",
                            "message": "This code has expired. Please request a new one."}), 410
        return jsonify({"error": "Invalid OTP",
                        "message": "Incorrect verification code."}), 422

    otp.is_used      = True
    user.is_verified = True
    db.session.commit()

    access_token  = generate_token(user.id, user.role)
    refresh_token = generate_refresh_token(user.id)

    response = jsonify({
        "message": "Email verified successfully. You can now sign in.",
        "token": access_token,
        "user": user.to_dict()
    })
    _set_auth_cookie(response, access_token)
    _set_refresh_cookie(response, refresh_token)
    return response, 200


@auth_bp.route("/resend-otp", methods=["POST"])
def resend_otp():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Bad request", "message": "No JSON body"}), 400

    email = data.get("email", "").strip().lower()
    if not email:
        return jsonify({"error": "Validation error", "message": "email is required"}), 400

    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"message": "If this email is registered, a new OTP has been sent."}), 200
    if user.is_verified:
        return jsonify({"error": "Already verified",
                        "message": "This account is already verified."}), 409

    recent = (
        OtpCode.query.filter_by(user_id=user.id, is_used=False)
        .filter(OtpCode.created_at > datetime.utcnow() - timedelta(seconds=OTP_RESEND_COOLDOWN_SECONDS))
        .first()
    )
    if recent:
        seconds_left = int(
            (recent.created_at + timedelta(seconds=OTP_RESEND_COOLDOWN_SECONDS)
             - datetime.utcnow()).total_seconds()
        )
        return jsonify({
            "error": "Rate limited",
            "message": f"Please wait {seconds_left} seconds before requesting a new code.",
            "retryAfter": seconds_left,
        }), 429

    _create_and_dispatch_otp(user)
    return jsonify({"message": "A new OTP has been sent. Check your email or terminal."}), 200


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Bad request", "message": "No JSON body provided"}), 400

    email    = data.get("email",    "").strip().lower()
    password = data.get("password", "")

    if not email or not password:
        return jsonify({"error": "Validation error",
                        "message": "email and password are required"}), 400

    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        return jsonify({"error": "Unauthorized",
                        "message": "Invalid email or password"}), 401

    if not user.is_verified:
        recent = (
            OtpCode.query.filter_by(user_id=user.id, is_used=False)
            .filter(OtpCode.created_at > datetime.utcnow()
                    - timedelta(seconds=OTP_RESEND_COOLDOWN_SECONDS))
            .first()
        )
        if not recent:
            _create_and_dispatch_otp(user)
        return jsonify({
            "error": "Email not verified",
            "message": "Please verify your email. A new OTP has been sent.",
            "email": user.email,
            "needsVerification": True,
        }), 403

    access_token  = generate_token(user.id, user.role)
    refresh_token = generate_refresh_token(user.id)

    response = jsonify({
        "user": user.to_dict(),
        "accessToken": access_token,
        "refreshToken": refresh_token
    })
    _set_auth_cookie(response, access_token)
    _set_refresh_cookie(response, refresh_token)
    return response, 200


@auth_bp.route("/refresh", methods=["POST"])
def refresh_token_route():
    """
    Silent token refresh.

    BUG FIX: The original implementation expected { "refreshToken": "..." }
    in the request body, but the JS client never stored that value — refresh
    always returned 401.  The refresh token is now stored in an httpOnly
    cookie (set by /login) and read here automatically by the browser.
    """
    rt_value = request.cookies.get("refresh_token")
    if not rt_value:
        # Fallback for API clients that still send token in body
        body     = request.get_json(silent=True) or {}
        rt_value = body.get("refreshToken")

    if not rt_value:
        return jsonify({"error": "Unauthorized", "message": "No refresh token provided"}), 401

    rt = RefreshToken.query.filter_by(token=rt_value, is_revoked=False).first()
    if not rt:
        return jsonify({"error": "Unauthorized", "message": "Invalid refresh token"}), 401

    if rt.expires_at < datetime.utcnow():
        rt.is_revoked = True
        db.session.commit()
        return jsonify({"error": "Unauthorized", "message": "Refresh token expired"}), 401

    # Token rotation — revoke old, issue new pair
    rt.is_revoked = True
    user          = rt.user
    new_access    = generate_token(user.id, user.role)
    new_refresh   = generate_refresh_token(user.id)
    db.session.commit()

    response = jsonify({
        "user": user.to_dict(),
        "accessToken": new_access,
        "refreshToken": new_refresh
    })
    _set_auth_cookie(response, new_access)
    _set_refresh_cookie(response, new_refresh)
    return response, 200


@auth_bp.route("/me", methods=["GET"])
def me():
    user, error = get_current_user()
    if error:
        return jsonify({"error": "Unauthorized", "message": error}), 401
    return jsonify(user.to_dict()), 200


@auth_bp.route("/logout", methods=["POST"])
def logout():
    """
    Clear auth cookies and revoke only the current session's refresh token.

    BUG FIX: The previous implementation revoked ALL refresh tokens for the
    user, logging them out of every device at once.  Now only the token
    from the current request's cookie is revoked.
    """
    user, _ = get_current_user()
    if user:
        rt_value = request.cookies.get("refresh_token")
        if rt_value:
            rt = RefreshToken.query.filter_by(
                token=rt_value, is_revoked=False
            ).first()
            if rt:
                rt.is_revoked = True
                db.session.commit()

    response = jsonify({"message": "Logged out"})
    return _clear_auth_cookies(response), 200


@auth_bp.route("/forgot-password", methods=["POST"])
@user_rate_limit(max_requests=5, window_seconds=300)
def forgot_password():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Bad request", "message": "No JSON body"}), 400

    email = data.get("email", "").strip().lower()
    if not email:
        return jsonify({"error": "Validation error", "message": "email is required"}), 400

    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({
            "message": "If this email is registered, a password reset OTP has been sent."
        }), 200

    recent = (
        OtpCode.query.filter_by(user_id=user.id, is_used=False)
        .filter(OtpCode.created_at > datetime.utcnow()
                - timedelta(seconds=OTP_RESEND_COOLDOWN_SECONDS))
        .first()
    )
    if recent:
        seconds_left = int(
            (recent.created_at + timedelta(seconds=OTP_RESEND_COOLDOWN_SECONDS)
             - datetime.utcnow()).total_seconds()
        )
        return jsonify({
            "error": "Rate limited",
            "message": f"Please wait {seconds_left} seconds before requesting a new code.",
            "retryAfter": seconds_left,
        }), 429

    _create_and_dispatch_otp(user)
    return jsonify({
        "message": "If this email is registered, a password reset OTP has been sent.",
        "email": email,
    }), 200


@auth_bp.route("/reset-password", methods=["POST"])
@user_rate_limit(max_requests=3, window_seconds=300)
def reset_password():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Bad request", "message": "No JSON body"}), 400

    email    = data.get("email",    "").strip().lower()
    code     = data.get("code",     "").strip()
    password = data.get("password", "")

    if not email or not code or not password:
        return jsonify({"error": "Validation error",
                        "message": "email, code, and password are required"}), 400

    if len(password) < 8:
        return jsonify({"error": "Validation error",
                        "message": "Password must be at least 8 characters"}), 400
    if not any(c.isupper() for c in password):
        return jsonify({"error": "Validation error",
                        "message": "Password must contain at least one uppercase letter"}), 400
    if not any(c.islower() for c in password):
        return jsonify({"error": "Validation error",
                        "message": "Password must contain at least one lowercase letter"}), 400
    if not any(c.isdigit() for c in password):
        return jsonify({"error": "Validation error",
                        "message": "Password must contain at least one digit"}), 400

    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"error": "Not found",
                        "message": "No account found for this email"}), 404

    otp = (
        OtpCode.query
        .filter_by(user_id=user.id, code=code, is_used=False)
        .filter(OtpCode.expires_at > datetime.utcnow())
        .first()
    )
    if not otp:
        expired = OtpCode.query.filter_by(user_id=user.id, code=code, is_used=False).first()
        if expired:
            return jsonify({"error": "OTP expired",
                            "message": "This code has expired. Please request a new one."}), 410
        return jsonify({"error": "Invalid OTP",
                        "message": "Incorrect verification code."}), 422

    otp.is_used      = True
    user.set_password(password)
    user.is_verified = True
    db.session.commit()

    return jsonify({
        "message": "Password reset successful. You can now login with your new password.",
        "email": email,
    }), 200
