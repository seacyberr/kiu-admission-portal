import os
import random
import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta

import jwt
from flask import Blueprint, request, jsonify, current_app
from models import db, User, OtpCode

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
    jwt_secret = current_app.config.get("SECRET_KEY", "")
    payload = {
        "userId": user_id,
        "role": role,
        "exp": datetime.utcnow() + timedelta(days=7),
    }
    return jwt.encode(payload, jwt_secret, algorithm="HS256")


def verify_token(token):
    jwt_secret = current_app.config.get("SECRET_KEY", "")
    return jwt.decode(token, jwt_secret, algorithms=["HS256"])


def get_current_user():
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return None, "No token provided"
    token = auth_header[7:]
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


def _print_otp_to_terminal(email, otp, full_name=""):
    """Always dump OTP to terminal so dev can use it during testing."""
    if os.environ.get("FLASK_ENV", "").lower() == "production":
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

    if len(password) < 6:
        return jsonify({"error": "Validation error", "message": "Password must be at least 6 characters"}), 400

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
    return jsonify({
        "message": "Email verified successfully. Welcome to KIU Portal!",
        "user": user.to_dict(),
        "token": token,
    }), 200


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

    token = generate_token(user.id, user.role)
    return jsonify({"user": user.to_dict(), "token": token}), 200


@auth_bp.route("/logout", methods=["POST"])
def logout():
    return jsonify({"message": "Logged out successfully"}), 200


@auth_bp.route("/me", methods=["GET"])
def me():
    user, error = get_current_user()
    if error:
        return jsonify({"error": "Unauthorized", "message": error}), 401
    return jsonify(user.to_dict()), 200
