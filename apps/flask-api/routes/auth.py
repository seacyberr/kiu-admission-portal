"""
Authentication Routes - Flask-JWT-Extended Implementation
Industry-standard JWT authentication with proper security
"""
import os
import logging
from datetime import datetime, timedelta
from functools import wraps

from flask import Blueprint, request, jsonify, g
from flask_jwt_extended import (
    create_access_token, create_refresh_token, jwt_required,
    get_jwt_identity, get_jwt, set_access_cookies, set_refresh_cookies,
    unset_jwt_cookies
)

from models import db, User, OtpCode
from services.otp_service import OTPService
from services.email_service import EmailService
from utils.rate_limiting import auth_rate_limit
from utils.api_response import success_response, fail_response, bad_request, unauthorized, created

from email_validator import validate_email, EmailNotValidError

log = logging.getLogger(__name__)
auth_bp = Blueprint("auth", __name__)

OTP_RESEND_COOLDOWN_SECONDS = 60


def get_current_user():
    """Get current user from JWT token (optional - works without JWT context)"""
    try:
        user_id = get_jwt_identity()
        if not user_id:
            return None, "No valid token"
    except RuntimeError:
        # No JWT context - this is OK for optional auth routes
        return None, "No valid token"
    
    user = User.query.get(user_id)
    if not user:
        return None, "User not found"
    
    g.current_user = user
    return user, None


def user_rate_limit(max_requests=100, window_seconds=3600):
    """Rate limiting decorator using cache"""
    from utils.caching import cache_manager
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            user = getattr(g, "current_user", None)
            identity = f"user:{user.id}" if user else (request.remote_addr or "unknown")
            slot = int(datetime.utcnow().timestamp()) // window_seconds
            key = f"rl:{f.__name__}:{identity}:{slot}"
            try:
                count = cache_manager.get(key, 0) + 1
                cache_manager.set(key, count, ttl=window_seconds)
                if count > max_requests:
                    return jsonify({
                        "error": "Rate limited",
                        "message": f"Too many requests. Max {max_requests} per {window_seconds // 60} minutes.",
                        "retryAfter": window_seconds,
                    }), 429
            except Exception:
                pass
            return f(*args, **kwargs)
        return wrapper
    return decorator


def _print_otp_to_terminal(email, otp, full_name=""):
    """Print OTP to terminal for debugging"""
    raw = os.environ.get("OTP_DEBUG", "").strip().lower()
    if raw == "" and os.environ.get("FLASK_ENV", "").lower() == "production":
        return
    if raw not in ("", "1", "true", "yes", "on"):
        return
    
    line = "=" * 56
    msg = f"\n{line}\n  KIU PORTAL — OTP VERIFICATION CODE\n{line}\n"
    if full_name:
        msg += f"  Name    : {full_name}\n"
    msg += f"  Email   : {email}\n  OTP     : {otp}\n  Expires : 10 minutes\n{line}\n"
    print(msg, flush=True)


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@auth_bp.route("/register", methods=["POST"])
@auth_rate_limit
def register():
    data = request.get_json()
    if not data:
        return bad_request("No JSON body provided")

    email       = data.get("email",       "").strip().lower()
    password    = data.get("password",    "")
    # Support both camelCase (frontend) and snake_case (backend/tests)
    first_name  = data.get("firstName",   data.get("first_name",   "")).strip()
    last_name   = data.get("lastName",    data.get("last_name",    "")).strip()
    phone       = data.get("phone",       data.get("phone",        ""))
    national_id = data.get("nationalId",  data.get("national_id",   ""))
    role        = data.get("role",        "applicant")

    # Validation
    errors = {}
    if not email:
        errors["email"] = "Required"
    if not password:
        errors["password"] = "Required"
    if not first_name:
        errors["firstName"] = "Required"
    if not last_name:
        errors["lastName"] = "Required"
    
    if errors:
        return bad_request("Missing required fields", errors=errors)

    from email_validator import validate_email, EmailNotValidError
    try:
        validate_email(email, check_deliverability=False)
    except EmailNotValidError:
        return bad_request("Invalid email address", errors={"email": "Invalid format"})

    # Password validation
    pwd_errors = []
    if len(password) < 8:
        pwd_errors.append("at least 8 characters")
    if not any(c.isupper() for c in password):
        pwd_errors.append("one uppercase letter")
    if not any(c.islower() for c in password):
        pwd_errors.append("one lowercase letter")
    if not any(c.isdigit() for c in password):
        pwd_errors.append("one digit")
    
    if pwd_errors:
        return bad_request(
            f"Password must contain {', '.join(pwd_errors)}",
            errors={"password": f"Must contain {', '.join(pwd_errors)}"}
        )

    if role not in ("applicant", "finalist"):
        role = "applicant"

    if User.query.filter_by(email=email).first():
        return fail_response("An account with this email already exists", error_code="EMAIL_EXISTS", status_code=409)

    user = User(
        email=email, first_name=first_name, last_name=last_name,
        phone=phone or None, national_id=national_id or None,
        role=role, is_verified=False,
    )
    user.set_password(password)
    db.session.add(user)
    db.session.flush()
    
    # Use OTP Service
    otp = OTPService.create_otp_for_user(user)
    full_name = f"{user.first_name} {user.last_name}"
    _print_otp_to_terminal(user.email, otp.code, full_name)
    EmailService.send_otp_email(user.email, otp.code, full_name)

    return created(
        {"email": email, "needsVerification": True},
        message="Account created. Please check your email (or terminal) for your 6-digit OTP."
    )


@auth_bp.route("/verify-otp", methods=["POST"])
def verify_otp():
    data = request.get_json()
    if not data:
        return bad_request("No JSON body provided")

    email = data.get("email", "").strip().lower()
    code  = data.get("code",  "").strip()

    if not email or not code:
        return bad_request("email and code are required", errors={
            "email": "Required" if not email else None,
            "code": "Required" if not code else None
        })

    user = User.query.filter_by(email=email).first()
    if not user:
        return not_found("No account found for this email")

    if user.is_verified:
        return success_response({}, message="Already verified. Please sign in.")

    # Use OTP Service
    is_valid, error = OTPService.verify_otp(user.id, code)
    if not is_valid:
        if error == "OTP_EXPIRED":
            return fail_response(
                "This code has expired. Please request a new one.",
                error_code="OTP_EXPIRED",
                status_code=410
            )
        return bad_request("Incorrect verification code", errors={"code": "Invalid OTP"})

    # OTP valid - verify user and create session
    user.is_verified = True
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Failed to verify user: {e}")
        return bad_request("Failed to verify account")

    # Create JWT tokens using Flask-JWT-Extended (identity must be string)
    access_token = create_access_token(identity=str(user.id), additional_claims={"role": user.role, "email": user.email})
    refresh_token = create_refresh_token(identity=str(user.id))

    resp, status = success_response({
        "accessToken": access_token,
        "refreshToken": refresh_token,
        "user": user.to_dict()
    }, message="Email verified successfully. You can now sign in.")
    
    # Set cookies (modifies response in-place)
    set_access_cookies(resp, access_token)
    set_refresh_cookies(resp, refresh_token)
    return resp, status


@auth_bp.route("/resend-otp", methods=["POST"])
def resend_otp():
    data = request.get_json()
    if not data:
        return bad_request("No JSON body provided")

    email = data.get("email", "").strip().lower()
    if not email:
        return bad_request("email is required", errors={"email": "Required"})

    user = User.query.filter_by(email=email).first()
    if not user:
        # Security: Don't reveal if email exists
        return success_response({}, message="If this email is registered, a new OTP has been sent.")
    if user.is_verified:
        return fail_response("This account is already verified", error_code="ALREADY_VERIFIED", status_code=409)

    # Check cooldown using OTP Service
    can_resend, seconds_left = OTPService.can_resend_otp(user.id)
    if not can_resend:
        response = fail_response(
            f"Please wait {seconds_left} seconds before requesting a new code.",
            error_code="RATE_LIMITED",
            status_code=429
        )
        response.headers['Retry-After'] = str(seconds_left)
        return response

    # Create and send new OTP
    otp = OTPService.create_otp_for_user(user)
    full_name = f"{user.first_name} {user.last_name}"
    _print_otp_to_terminal(user.email, otp.code, full_name)
    EmailService.send_otp_email(user.email, otp.code, full_name)
    
    return success_response({}, message="A new OTP has been sent. Check your email or terminal.")


@auth_bp.route("/login", methods=["POST"])
@auth_rate_limit
def login():
    """Authenticate user with strict input validation"""
    data = request.get_json(silent=True) or {}
    
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")
    
    # Validation
    if not email or not password:
        return bad_request("email and password are required")

    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        # Generic error to prevent user enumeration
        return fail_response("Invalid credentials", status_code=401)

    if not user.is_verified:
        # Check if we should send new OTP
        can_resend, _ = OTPService.can_resend_otp(user.id)
        if can_resend:
            otp = OTPService.create_otp_for_user(user)
            full_name = f"{user.first_name} {user.last_name}"
            _print_otp_to_terminal(user.email, otp.code, full_name)
            EmailService.send_otp_email(user.email, otp.code, full_name)
        
        resp, status = fail_response(
            "Please verify your email. A new OTP has been sent.",
            error_code="EMAIL_NOT_VERIFIED",
            status_code=403
        )
        resp.headers['X-Needs-Verification'] = 'true'
        return resp, status

    # Create JWT tokens using Flask-JWT-Extended (identity must be string)
    access_token = create_access_token(
        identity=str(user.id),
        additional_claims={"role": user.role, "email": user.email}
    )
    refresh_token = create_refresh_token(identity=str(user.id))

    resp, status = success_response(
        data={
            "user": user.to_dict(),
            "accessToken": access_token,
            "refreshToken": refresh_token
        },
        meta={
            "tokenType": "Bearer",
            "expiresIn": 8 * 3600
        }
    )
    set_access_cookies(resp, access_token)
    set_refresh_cookies(resp, refresh_token)
    return resp, status


@auth_bp.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh_token_route():
    """
    Silent token refresh using Flask-JWT-Extended.
    Requires valid refresh token from cookie or header.
    """
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user or not user.is_verified:
        return unauthorized("User not found or not verified")
    
    # Create new access token (identity must be string)
    access_token = create_access_token(
        identity=str(user.id),
        additional_claims={"role": user.role, "email": user.email}
    )
    refresh_token = create_refresh_token(identity=str(user.id))
    
    resp, status = success_response({
        "user": user.to_dict(),
        "accessToken": access_token,
        "refreshToken": refresh_token
    })
    set_access_cookies(resp, access_token)
    set_refresh_cookies(resp, refresh_token)
    return resp, status


@auth_bp.route("/me", methods=["GET"])
@jwt_required()
def me():
    """Get current authenticated user"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user:
        return unauthorized("User not found")
    
    return success_response(user.to_dict())


@auth_bp.route("/logout", methods=["POST"])
@jwt_required()
def logout():
    """
    Logout user by revoking JWT token via blocklist.
    """
    from utils.caching import cache_manager
    jti = get_jwt()["jti"]
    
    # Add token to blocklist (cache with TTL matching token expiry)
    cache_manager.set(f"jwt_blacklist:{jti}", True, ttl=8*3600)
    
    resp, status = success_response({}, message="Logged out successfully")
    unset_jwt_cookies(resp)
    return resp, status


@auth_bp.route("/forgot-password", methods=["POST"])
@user_rate_limit(max_requests=5, window_seconds=300)
def forgot_password():
    data = request.get_json()
    if not data:
        return bad_request("No JSON body provided")

    email = data.get("email", "").strip().lower()
    if not email:
        return bad_request("email is required", errors={"email": "Required"})

    user = User.query.filter_by(email=email).first()
    if not user:
        # Return success even if user not found (security - don't reveal if email exists)
        return success_response({}, message="If this email is registered, a password reset OTP has been sent.")

    # Check cooldown using OTP Service
    can_resend, seconds_left = OTPService.can_resend_otp(user.id)
    if not can_resend:
        response = fail_response(
            f"Please wait {seconds_left} seconds before requesting a new code.",
            error_code="RATE_LIMITED",
            status_code=429
        )
        response.headers['Retry-After'] = str(seconds_left)
        return response

    # Create and send OTP
    otp = OTPService.create_otp_for_user(user)
    full_name = f"{user.first_name} {user.last_name}"
    _print_otp_to_terminal(user.email, otp.code, full_name)
    EmailService.send_otp_email(user.email, otp.code, full_name)
    
    return success_response({}, message="If this email is registered, a password reset OTP has been sent.")


@auth_bp.route("/reset-password", methods=["POST"])
@user_rate_limit(max_requests=3, window_seconds=300)
def reset_password():
    data = request.get_json()
    if not data:
        return bad_request("No JSON body provided")

    email    = data.get("email",    "").strip().lower()
    code     = data.get("code",     "").strip()
    password = data.get("password", "")

    if not email or not code or not password:
        return bad_request("email, code, and password are required", errors={
            "email": "Required" if not email else None,
            "code": "Required" if not code else None,
            "password": "Required" if not password else None
        })

    errors = {}
    if len(password) < 8:
        errors["password"] = "Password must be at least 8 characters"
    if not any(c.isupper() for c in password):
        errors["password"] = errors.get("password", "") + " Must contain at least one uppercase letter."
    if not any(c.islower() for c in password):
        errors["password"] = errors.get("password", "") + " Must contain at least one lowercase letter."
    if not any(c.isdigit() for c in password):
        errors["password"] = errors.get("password", "") + " Must contain at least one digit."
    
    if errors:
        return bad_request("Password validation failed", errors=errors)

    user = User.query.filter_by(email=email).first()
    if not user:
        return not_found("No account found for this email")

    # Verify OTP using service
    is_valid, error = OTPService.verify_otp(user.id, code)
    if not is_valid:
        if error == "OTP_EXPIRED":
            return fail_response(
                "This code has expired. Please request a new one.",
                error_code="OTP_EXPIRED",
                status_code=410
            )
        return bad_request("Incorrect verification code", errors={"code": "Invalid OTP"})

    # Reset password
    user.set_password(password)
    user.is_verified = True
    try:
        db.session.commit()
        return success_response(
            {"email": email},
            message="Password reset successful. You can now login with your new password."
        )
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Failed to reset password: {e}")
        return bad_request("Failed to reset password")
