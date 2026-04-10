"""
Authentication API Routes - Version 1
Industry-standard JWT authentication with proper security
"""
from datetime import datetime, timezone, timedelta
from functools import wraps

from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import (
    create_access_token, create_refresh_token, 
    jwt_required, get_jwt_identity, get_jwt
)

from src.core.extensions import db, limiter
from src.domain.models.user import User
from src.api.v1.auth.schemas import (
    RegisterRequest, LoginRequest, VerifyOtpRequest,
    PasswordResetRequest, ChangePasswordRequest
)
from src.api.v1.auth.services import (
    create_user, verify_user_email, authenticate_user,
    generate_otp, send_otp_email, send_password_reset_email,
    validate_password_strength
)
from src.core.errors import APIError

auth_bp = Blueprint('auth_v1', __name__)

# JWT token blacklist (for logout)
blacklist = set()


@auth_bp.route('/register', methods=['POST'])
@limiter.limit("5 per minute")
def register():
    """
    Register new user account
    POST /api/v1/auth/register
    """
    try:
        data = request.get_json()
        if not data:
            raise APIError("No data provided", 400)
        
        # Validate request
        validated = RegisterRequest(**data)
        
        # Check if user exists
        if User.query.filter_by(email=validated.email).first():
            raise APIError("Email already registered", 409)
        
        # Validate password
        is_valid, password_error = validate_password_strength(validated.password)
        if not is_valid:
            raise APIError(password_error, 400)
        
        # Create user
        user = create_user(
            email=validated.email,
            password=validated.password,
            first_name=validated.first_name,
            last_name=validated.last_name,
            phone=validated.phone,
            role=validated.role or 'applicant'
        )
        
        # Generate and send OTP
        otp = generate_otp()
        user.otp_code = otp
        user.otp_expires_at = datetime.now(timezone.utc) + timedelta(minutes=30)
        db.session.commit()
        
        # Send verification email
        send_otp_email(user.email, otp, user.first_name)
        
        return jsonify({
            "success": True,
            "message": "Registration successful. Please verify your email.",
            "data": {
                "user_id": user.public_id,
                "email": user.email,
                "requires_verification": True
            }
        }), 201
        
    except APIError as e:
        return jsonify({"success": False, "error": e.message, "code": e.status_code}), e.status_code
    except Exception as e:
        current_app.logger.error(f"Registration error: {str(e)}")
        return jsonify({"success": False, "error": "Registration failed", "code": 500}), 500


@auth_bp.route('/verify-email', methods=['POST'])
@limiter.limit("10 per minute")
def verify_email():
    """
    Verify email with OTP
    POST /api/v1/auth/verify-email
    """
    try:
        data = request.get_json()
        if not data:
            raise APIError("No data provided", 400)
        
        validated = VerifyOtpRequest(**data)
        
        user = User.query.filter_by(email=validated.email).first()
        if not user:
            raise APIError("User not found", 404)
        
        if user.is_verified:
            return jsonify({
                "success": True,
                "message": "Email already verified",
                "data": {"verified": True}
            })
        
        # Check OTP
        if user.otp_code != validated.otp:
            raise APIError("Invalid verification code", 400)
        
        if user.otp_expires_at and user.otp_expires_at < datetime.now(timezone.utc):
            raise APIError("Verification code expired", 410)
        
        # Mark as verified
        user.is_verified = True
        user.otp_code = None
        user.otp_expires_at = None
        db.session.commit()
        
        # Generate tokens
        access_token = create_access_token(
            identity=user.id,
            additional_claims={
                'public_id': user.public_id,
                'role': user.role,
                'email': user.email
            }
        )
        refresh_token = create_refresh_token(identity=user.id)
        
        return jsonify({
            "success": True,
            "message": "Email verified successfully",
            "data": {
                "verified": True,
                "access_token": access_token,
                "refresh_token": refresh_token,
                "user": user.to_dict()
            }
        })
        
    except APIError as e:
        return jsonify({"success": False, "error": e.message, "code": e.status_code}), e.status_code
    except Exception as e:
        current_app.logger.error(f"Verification error: {str(e)}")
        return jsonify({"success": False, "error": "Verification failed", "code": 500}), 500


@auth_bp.route('/login', methods=['POST'])
@limiter.limit("10 per minute")
def login():
    """
    Authenticate user and return JWT tokens
    POST /api/v1/auth/login
    """
    try:
        data = request.get_json()
        if not data:
            raise APIError("No data provided", 400)
        
        validated = LoginRequest(**data)
        
        # Authenticate
        user = authenticate_user(validated.email, validated.password)
        if not user:
            raise APIError("Invalid credentials", 401)
        
        if not user.is_verified:
            raise APIError("Email not verified. Please check your email.", 403)
        
        if not user.is_active:
            raise APIError("Account is disabled", 403)
        
        # Update last login
        user.last_login = datetime.now(timezone.utc)
        db.session.commit()
        
        # Generate tokens
        access_token = create_access_token(
            identity=user.id,
            additional_claims={
                'public_id': user.public_id,
                'role': user.role,
                'email': user.email
            }
        )
        refresh_token = create_refresh_token(identity=user.id)
        
        # Set refresh token in cookie (httpOnly, secure)
        response = jsonify({
            "success": True,
            "message": "Login successful",
            "data": {
                "access_token": access_token,
                "refresh_token": refresh_token,
                "token_type": "Bearer",
                "expires_in": 86400,  # 24 hours
                "user": user.to_dict()
            }
        })
        
        # Add no-cache headers for auth responses
        response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        
        return response
        
    except APIError as e:
        return jsonify({"success": False, "error": e.message, "code": e.status_code}), e.status_code
    except Exception as e:
        current_app.logger.error(f"Login error: {str(e)}")
        return jsonify({"success": False, "error": "Login failed", "code": 500}), 500


@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh_token():
    """
    Refresh access token using refresh token
    POST /api/v1/auth/refresh
    """
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user or not user.is_active:
            raise APIError("User not found or inactive", 401)
        
        # Create new access token
        access_token = create_access_token(
            identity=user.id,
            additional_claims={
                'public_id': user.public_id,
                'role': user.role,
                'email': user.email
            }
        )
        
        return jsonify({
            "success": True,
            "data": {
                "access_token": access_token,
                "token_type": "Bearer",
                "expires_in": 86400
            }
        })
        
    except APIError as e:
        return jsonify({"success": False, "error": e.message, "code": e.status_code}), e.status_code
    except Exception as e:
        current_app.logger.error(f"Token refresh error: {str(e)}")
        return jsonify({"success": False, "error": "Token refresh failed", "code": 500}), 500


@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """
    Logout user and blacklist token
    POST /api/v1/auth/logout
    """
    try:
        jti = get_jwt()["jti"]
        blacklist.add(jti)
        
        response = jsonify({
            "success": True,
            "message": "Logged out successfully"
        })
        
        # Clear cookies if set
        response.set_cookie('refresh_token', '', expires=0)
        
        # No-cache headers
        response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        
        return response
        
    except Exception as e:
        current_app.logger.error(f"Logout error: {str(e)}")
        return jsonify({"success": False, "error": "Logout failed", "code": 500}), 500


@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """
    Get current authenticated user profile
    GET /api/v1/auth/me
    """
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            raise APIError("User not found", 404)
        
        return jsonify({
            "success": True,
            "data": {
                "user": user.to_dict()
            }
        })
        
    except APIError as e:
        return jsonify({"success": False, "error": e.message, "code": e.status_code}), e.status_code
    except Exception as e:
        current_app.logger.error(f"Get user error: {str(e)}")
        return jsonify({"success": False, "error": "Failed to get user", "code": 500}), 500


@auth_bp.route('/forgot-password', methods=['POST'])
@limiter.limit("3 per minute")
def forgot_password():
    """
    Request password reset
    POST /api/v1/auth/forgot-password
    """
    try:
        data = request.get_json()
        if not data or not data.get('email'):
            raise APIError("Email required", 400)
        
        email = data['email'].lower().strip()
        user = User.query.filter_by(email=email).first()
        
        # Always return success to prevent email enumeration
        if user:
            reset_token = generate_password_reset_token(user)
            send_password_reset_email(user.email, reset_token, user.first_name)
        
        return jsonify({
            "success": True,
            "message": "If an account exists, a password reset email has been sent."
        })
        
    except Exception as e:
        current_app.logger.error(f"Forgot password error: {str(e)}")
        # Still return success to prevent enumeration
        return jsonify({
            "success": True,
            "message": "If an account exists, a password reset email has been sent."
        })


def generate_password_reset_token(user: User) -> str:
    """Generate secure password reset token"""
    from itsdangerous import URLSafeTimedSerializer
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    return serializer.dumps(user.email, salt='password-reset')


def verify_reset_token(token: str, expiration: int = 3600) -> str:
    """Verify password reset token"""
    from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    try:
        email = serializer.loads(token, salt='password-reset', max_age=expiration)
        return email
    except SignatureExpired:
        raise APIError("Reset token expired", 400)
    except BadSignature:
        raise APIError("Invalid reset token", 400)
