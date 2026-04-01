import os
import random
import secrets
import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta

import jwt
from flask import Blueprint, request, jsonify, current_app
from models import db, User, OtpCode, RefreshToken

log = logging.getLogger(__name__)

auth_bp = Blueprint("auth", __name__)

# Brevo SMTP configuration
BREVO_SMTP_HOST = "smtp-relay.brevo.com"
BREVO_SMTP_PORT = 587
BREVO_SMTP_USER = os.environ.get("BREVO_SMTP_USER", "")
BREVO_SMTP_KEY = os.environ.get("BREVO_SMTP_KEY", "")
EMAIL_FROM = "KIU Portal <noreply@kiu.ac.ug>"

OTP_EXPIRY_MINUTES = 10
OTP_RESEND_COOLDOWN_SECONDS = 60


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def generate_token(user_id, role):
    """Generate short-lived access token (15 minutes)."""
    jwt_secret = current_app.config.get("SECRET_KEY", "")
    payload = {
        "userId": user_id,
        "role": role,
        "exp": datetime.utcnow() + timedelta(minutes=15),
        "type": "access",
    }
    return jwt.encode(payload, jwt_secret, algorithm="HS256")


def generate_refresh_token(user_id):
    """Generate long-lived refresh token (7 days) and store in database."""
    token = secrets.token_urlsafe(64)
    expires_at = datetime.utcnow() + timedelta(days=7)
    
    refresh_token = RefreshToken(
        user_id=user_id,
        token=token,
        expires_at=expires_at,
        user_agent=request.headers.get("User-Agent", ""),
        ip_address=request.remote_addr,
    )
    db.session.add(refresh_token)
    db.session.commit()
    
    return token


def _set_auth_cookie(response, token):
    """Set JWT token as httpOnly cookie."""
    is_production = os.environ.get("FLASK_ENV", "").lower() == "production"
    response.set_cookie(
        "auth_token",
        value=token,
        httponly=True,
        secure=is_production,
        samesite="Strict",
        max_age=7 * 24 * 60 * 60,  # 7 days
        path="/",
    )
    return response


def _clear_auth_cookie(response):
    """Remove auth cookie."""
    response.delete_cookie("auth_token", path="/")
    return response


def verify_token(token):
    jwt_secret = current_app.config.get("SECRET_KEY", "")
    return jwt.decode(token, jwt_secret, algorithms=["HS256"])


def get_current_user():
    """Get current user from httpOnly cookie or Authorization header."""
    token = None

    # Priority 1: httpOnly cookie
    token = request.cookies.get("auth_token")

    # Priority 2: Authorization header (backward compatibility)
    if not token:
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            token = auth_header[7:]

    if not token:
        return None, "No token provided"

    try:
        payload = verify_token(token)
        user = db.session.get(User, payload["userId"])
        if not user:
            return None, "User not found"
        return user, None
    except jwt.ExpiredSignatureError:
        return None, "Token expired"
    except jwt.InvalidTokenError:
        return None, "Invalid token"


def _generate_otp():
    return str(random.randint(100000, 999999))


def _otp_debug_enabled() -> bool:
    """
    Controls whether OTP codes are printed to terminal.

    Recommended:
    - `OTP_DEBUG=false` in production
    - `OTP_DEBUG=true` only during local testing

    Backwards compatible behavior:
    - If `OTP_DEBUG` is not set, print only when `FLASK_ENV != production`.
    """

    otp_debug_raw = os.environ.get("OTP_DEBUG", "").strip().lower()
    if otp_debug_raw == "":
        return os.environ.get("FLASK_ENV", "").lower() != "production"
    return otp_debug_raw in ("1", "true", "yes", "on")


def _print_otp_to_terminal(email, otp, full_name=""):
    """Print OTP to terminal only when debugging is enabled."""
    if not _otp_debug_enabled():
        return
    line = "=" * 56
    msg = (
        f"\n{line}\n"
        f"  KIU PORTAL — OTP VERIFICATION CODE\n"
        f"{line}\n"
    )
    if full_name:
        msg += f"  Name    : {full_name}\n"
    msg += (
        f"  Email   : {email}\n"
        f"  OTP     : {otp}\n"
        f"  Expires : {OTP_EXPIRY_MINUTES} minutes\n"
        f"{line}\n"
    )
    print(msg, flush=True)
    log.info("OTP generated for %s (terminal output)", email)


def _send_otp_email(to_email, otp, full_name=""):
    """Send OTP via Brevo SMTP. Silently skips if key not configured."""
    if not BREVO_SMTP_KEY:
        log.warning("BREVO_SMTP_KEY not set — email not sent (see terminal for OTP)")
        return False

    greeting = f"Dear {full_name}," if full_name else "Hello,"

    html_body = f"""
    <div style="font-family:Arial,sans-serif;max-width:480px;margin:0 auto;padding:32px;
                border:1px solid #e5e7eb;border-radius:12px;">
      <div style="text-align:center;margin-bottom:24px;">
        <h2 style="color:#1e3a5f;margin:0;">Kampala International University</h2>
        <p style="color:#6b7280;margin:4px 0 0;">Admission &amp; Career Portal</p>
      </div>
      <p style="color:#374151;">{greeting}</p>
      <p style="color:#374151;">
        Your One-Time Password (OTP) for verifying your KIU Portal account is:
      </p>
      <div style="text-align:center;margin:32px 0;">
        <span style="font-size:40px;font-weight:bold;letter-spacing:12px;
                     color:#1e3a5f;background:#f0f4ff;padding:16px 32px;
                     border-radius:8px;display:inline-block;">{otp}</span>
      </div>
      <p style="color:#6b7280;font-size:14px;">
        This code expires in <strong>{OTP_EXPIRY_MINUTES} minutes</strong>.
        Do not share it with anyone.
      </p>
      <hr style="border:none;border-top:1px solid #e5e7eb;margin:24px 0;">
      <p style="color:#9ca3af;font-size:12px;text-align:center;">
        Kampala International University · Kansanga, Kampala, Uganda<br>
        admissions@kiu.ac.ug
      </p>
    </div>
    """

    msg = MIMEMultipart("alternative")
    msg["Subject"] = "Your KIU Portal Verification Code"
    msg["From"] = EMAIL_FROM
    msg["To"] = to_email
    msg.attach(MIMEText(html_body, "html"))

    try:
        with smtplib.SMTP(BREVO_SMTP_HOST, BREVO_SMTP_PORT, timeout=10) as smtp:
            smtp.ehlo()
            smtp.starttls()
            smtp.login(BREVO_SMTP_USER, BREVO_SMTP_KEY)
            smtp.sendmail(EMAIL_FROM, to_email, msg.as_string())
        log.info("Email sent to %s via Brevo", to_email)
        return True
    except Exception as exc:
        log.error("Brevo email failed for %s: %s", to_email, exc)
        return False


def _create_and_dispatch_otp(user):
    """Invalidate old OTPs, create a fresh one, print + email it."""
    # Invalidate all previous unused OTPs for this user
    OtpCode.query.filter_by(user_id=user.id, is_used=False).update({"is_used": True})
    db.session.flush()

    code = _generate_otp()
    otp = OtpCode(
        user_id=user.id,
        code=code,
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
    """
    Register a new user account.
    
    Creates a new applicant or finalist account and sends an OTP for email verification.
    
    Request Body:
        email (str): Valid email address
        password (str): Minimum 6 characters
        firstName (str): User's first name
        lastName (str): User's last name
        phone (str, optional): Phone number
        nationalId (str, optional): National ID
        role (str, optional): "applicant" or "finalist" (default: "applicant")
    
    Returns:
        201: Account created, OTP sent
        400: Validation error
        409: Email already exists
    
    Example:
        POST /api/auth/register
        {
            "email": "student@example.com",
            "password": "secure123",
            "firstName": "John",
            "lastName": "Doe"
        }
    """
    data = request.get_json()
    if not data:
        return jsonify({"error": "Bad request", "message": "No JSON body provided"}), 400

    email = data.get("email", "").strip().lower()
    password = data.get("password", "")
    first_name = data.get("firstName", "").strip()
    last_name = data.get("lastName", "").strip()
    phone = data.get("phone", "")
    national_id = data.get("nationalId", "")
    role = data.get("role", "applicant")

    if not email or not password or not first_name or not last_name:
        return jsonify({"error": "Validation error", "message": "email, password, firstName and lastName are required"}), 400

    # Validate email format (basic check — don't require DNS resolution for dev)
    from email_validator import validate_email, EmailNotValidError
    try:
        validate_email(email, check_deliverability=False)
    except EmailNotValidError:
        return jsonify({"error": "Validation error", "message": "Invalid email address"}), 400

    # Password complexity requirements
    if len(password) < 8:
        return jsonify({"error": "Validation error", "message": "Password must be at least 8 characters"}), 400
    if not any(c.isupper() for c in password):
        return jsonify({"error": "Validation error", "message": "Password must contain at least one uppercase letter"}), 400
    if not any(c.islower() for c in password):
        return jsonify({"error": "Validation error", "message": "Password must contain at least one lowercase letter"}), 400
    if not any(c.isdigit() for c in password):
        return jsonify({"error": "Validation error", "message": "Password must contain at least one digit"}), 400

    # Prevent self-registration as admin
    if role not in ("applicant", "finalist"):
        role = "applicant"

    existing = User.query.filter_by(email=email).first()
    if existing:
        log.info("Registration attempt for existing email: %s", email)
        return jsonify({"error": "Conflict", "message": "An account with this email already exists"}), 409

    user = User(
        email=email,
        first_name=first_name,
        last_name=last_name,
        phone=phone or None,
        national_id=national_id or None,
        role=role,
        is_verified=False,
    )
    user.set_password(password)
    db.session.add(user)
    db.session.flush()  # Get user.id before commit

    _create_and_dispatch_otp(user)

    return jsonify({
        "message": "Account created. Please check your email (or terminal) for your 6-digit OTP.",
        "email": email,
        "needsVerification": True,
    }), 201


@auth_bp.route("/verify-otp", methods=["POST"])
def verify_otp():
    """
    Verify email with OTP code.
    
    Validates the 6-digit OTP sent during registration and marks the account as verified.
    
    Request Body:
        email (str): User's email address
        code (str): 6-digit OTP code
    
    Returns:
        200: Email verified, returns JWT token
        404: Email not found
        410: OTP expired
        422: Invalid OTP code
    
    Example:
        POST /api/auth/verify-otp
        {
            "email": "student@example.com",
            "code": "123456"
        }
    """
    data = request.get_json()
    if not data:
        return jsonify({"error": "Bad request", "message": "No JSON body"}), 400

    email = data.get("email", "").strip().lower()
    code = data.get("code", "").strip()

    if not email or not code:
        return jsonify({"error": "Validation error", "message": "email and code are required"}), 400

    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"error": "Not found", "message": "No account found for this email"}), 404

    if user.is_verified:
        token = generate_token(user.id, user.role)
        return jsonify({"message": "Already verified", "user": user.to_dict(), "token": token}), 200

    otp = (
        OtpCode.query
        .filter_by(user_id=user.id, code=code, is_used=False)
        .filter(OtpCode.expires_at > datetime.utcnow())
        .first()
    )

    if not otp:
        # Check if code exists but is expired
        expired = OtpCode.query.filter_by(user_id=user.id, code=code, is_used=False).first()
        if expired:
            return jsonify({"error": "OTP expired", "message": "This code has expired. Please request a new one."}), 410
        return jsonify({"error": "Invalid OTP", "message": "Incorrect verification code. Please check and try again."}), 422

    # Mark OTP as used and verify user
    otp.is_used = True
    user.is_verified = True
    db.session.commit()

    token = generate_token(user.id, user.role)
    response = jsonify({
        "message": "Email verified successfully. Welcome to KIU Portal!",
        "user": user.to_dict(),
        "token": token,
    })
    _set_auth_cookie(response, token)
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
        # Return 200 to prevent email enumeration
        return jsonify({"message": "If this email is registered, a new OTP has been sent."}), 200

    if user.is_verified:
        return jsonify({"error": "Already verified", "message": "This account is already verified."}), 409

    # Rate limiting: check if a fresh OTP was created within the cooldown window
    recent = (
        OtpCode.query
        .filter_by(user_id=user.id, is_used=False)
        .filter(OtpCode.created_at > datetime.utcnow() - timedelta(seconds=OTP_RESEND_COOLDOWN_SECONDS))
        .first()
    )
    if recent:
        seconds_left = int((recent.created_at + timedelta(seconds=OTP_RESEND_COOLDOWN_SECONDS) - datetime.utcnow()).total_seconds())
        return jsonify({
            "error": "Rate limited",
            "message": f"Please wait {seconds_left} seconds before requesting a new code.",
            "retryAfter": seconds_left,
        }), 429

    _create_and_dispatch_otp(user)
    return jsonify({"message": "A new OTP has been sent. Check your email or terminal."}), 200


@auth_bp.route("/login", methods=["POST"])
def login():
    """
    Authenticate user and obtain JWT token.
    
    Validates credentials and returns a JWT token for accessing protected endpoints.
    If the account is not verified, a new OTP is sent and verification is required.
    
    Request Body:
        email (str): User's email address
        password (str): User's password
    
    Returns:
        200: Login successful, returns user data and JWT token
        401: Invalid credentials
        403: Email not verified (new OTP sent)
    
    Example:
        POST /api/auth/login
        {
            "email": "student@example.com",
            "password": "secure123"
        }
    """
    data = request.get_json()
    if not data:
        return jsonify({"error": "Bad request", "message": "No JSON body provided"}), 400

    email = data.get("email", "").strip().lower()
    password = data.get("password", "")

    if not email or not password:
        return jsonify({"error": "Validation error", "message": "email and password are required"}), 400

    user = User.query.filter_by(email=email).first()

    # Deliberately vague on invalid credentials to prevent enumeration
    if not user or not user.check_password(password):
        return jsonify({"error": "Unauthorized", "message": "Invalid email or password"}), 401

    # Unverified user: resend OTP and prompt verification
    if not user.is_verified:
        # Check resend cooldown before auto-resending
        recent = (
            OtpCode.query
            .filter_by(user_id=user.id, is_used=False)
            .filter(OtpCode.created_at > datetime.utcnow() - timedelta(seconds=OTP_RESEND_COOLDOWN_SECONDS))
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

    access_token = generate_token(user.id, user.role)
    refresh_token_str = generate_refresh_token(user.id)
    response = jsonify({
        "user": user.to_dict(),
        "accessToken": access_token,
        "refreshToken": refresh_token_str,
    })
    _set_auth_cookie(response, access_token)
    return response, 200


@auth_bp.route("/refresh", methods=["POST"])
def refresh_token():
    """
    Refresh access token using a valid refresh token.
    
    Implements token rotation: the old refresh token is revoked and a new one is issued.
    
    Request Body:
        refreshToken (str): Valid refresh token
    
    Returns:
        200: New access token and refresh token
        401: Invalid or expired refresh token
    """
    data = request.get_json()
    if not data:
        return jsonify({"error": "Bad request", "message": "No JSON body provided"}), 400
    
    refresh_token_str = data.get("refreshToken")
    if not refresh_token_str:
        return jsonify({"error": "Validation error", "message": "refreshToken is required"}), 400
    
    # Find the refresh token in database
    refresh_token = RefreshToken.query.filter_by(
        token=refresh_token_str,
        is_revoked=False,
    ).first()
    
    if not refresh_token:
        return jsonify({"error": "Unauthorized", "message": "Invalid refresh token"}), 401
    
    # Check if expired
    if refresh_token.expires_at < datetime.utcnow():
        refresh_token.is_revoked = True
        db.session.commit()
        return jsonify({"error": "Unauthorized", "message": "Refresh token expired"}), 401
    
    # Revoke the old refresh token (rotation)
    refresh_token.is_revoked = True
    
    # Generate new tokens
    user = refresh_token.user
    new_access_token = generate_token(user.id, user.role)
    new_refresh_token = generate_refresh_token(user.id)
    
    db.session.commit()
    
    response = jsonify({
        "accessToken": new_access_token,
        "refreshToken": new_refresh_token,
        "user": user.to_dict(),
    })
    _set_auth_cookie(response, new_access_token)
    return response, 200


@auth_bp.route("/me", methods=["GET"])
def me():
    user, error = get_current_user()
    if error:
        return jsonify({"error": "Unauthorized", "message": error}), 401
    return jsonify(user.to_dict()), 200
