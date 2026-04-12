"""
Authentication Service - Handles user authentication, tokens, and sessions
Separates business logic from HTTP layer (Single Responsibility Principle)
"""
import jwt
import hashlib
import logging
from datetime import datetime, timedelta
from typing import Tuple, Optional, Dict, Any
from flask import current_app
from models import db, User, RefreshToken

log = logging.getLogger(__name__)


class AuthService:
    """Service layer for authentication operations"""
    
    JWT_ACCESS_TOKEN_HOURS = 8
    
    @staticmethod
    def generate_token(user_id: int, role: str) -> str:
        """Generate JWT access token"""
        jwt_secret = current_app.config.get("SECRET_KEY", "")
        payload = {
            "userId": user_id,
            "role": role,
            "exp": datetime.utcnow() + timedelta(hours=AuthService.JWT_ACCESS_TOKEN_HOURS),
            "type": "access",
        }
        return jwt.encode(payload, jwt_secret, algorithm="HS256")
    
    @staticmethod
    def verify_token(token: str) -> Dict[str, Any]:
        """Verify and decode JWT token"""
        jwt_secret = current_app.config.get("SECRET_KEY", "")
        return jwt.decode(token, jwt_secret, algorithms=["HS256"])
    
    @staticmethod
    def get_current_user_from_token(token: str) -> Tuple[Optional[User], Optional[str]]:
        """Get user from token, handling all error cases"""
        if not token:
            return None, "No token provided"
        try:
            payload = AuthService.verify_token(token)
            user = db.session.get(User, payload["userId"])
            if not user:
                return None, "User not found"
            return user, None
        except jwt.ExpiredSignatureError:
            return None, "Token expired"
        except jwt.InvalidTokenError:
            return None, "Invalid token"
    
    @classmethod
    def authenticate_user(cls, email: str, password: str) -> Tuple[Optional[User], Optional[str]]:
        """Authenticate user with credentials"""
        user = User.query.filter_by(email=email).first()
        if not user or not user.check_password(password):
            return None, "Invalid credentials"
        if not user.is_verified:
            return None, "EMAIL_NOT_VERIFIED"
        return user, None
    
    @classmethod
    def create_session(cls, user: User, user_agent: str = "", ip_address: str = "") -> Tuple[str, str]:
        """Create new session with access and refresh tokens"""
        access_token = cls.generate_token(user.id, user.role)
        refresh_token = cls._generate_refresh_token(user.id, user_agent, ip_address)
        return access_token, refresh_token
    
    @staticmethod
    def _generate_refresh_token(user_id: int, user_agent: str = "", ip_address: str = "") -> str:
        """Generate and store refresh token"""
        import secrets
        token = secrets.token_urlsafe(64)
        rt = RefreshToken(
            user_id=user_id,
            token=token,
            expires_at=datetime.utcnow() + timedelta(days=7),
            user_agent=user_agent,
            ip_address=ip_address,
        )
        db.session.add(rt)
        db.session.commit()
        return token
    
    @classmethod
    def refresh_session(cls, refresh_token_value: str, user_agent: str = "", ip_address: str = "") -> Tuple[Optional[Dict], Optional[str]]:
        """Rotate tokens - revoke old, issue new"""
        rt = RefreshToken.query.filter_by(token=refresh_token_value, is_revoked=False).first()
        if not rt:
            return None, "Invalid refresh token"
        
        if rt.expires_at < datetime.utcnow():
            rt.is_revoked = True
            db.session.commit()
            return None, "Refresh token expired"
        
        # Rotate token
        rt.is_revoked = True
        user = rt.user
        new_access = cls.generate_token(user.id, user.role)
        new_refresh = cls._generate_refresh_token(user.id, user_agent, ip_address)
        db.session.commit()
        
        return {
            "user": user.to_dict(),
            "access_token": new_access,
            "refresh_token": new_refresh
        }, None
    
    @staticmethod
    def revoke_refresh_token(refresh_token_value: str) -> bool:
        """Revoke a specific refresh token"""
        rt = RefreshToken.query.filter_by(token=refresh_token_value, is_revoked=False).first()
        if rt:
            rt.is_revoked = True
            db.session.commit()
            return True
        return False
    
    @staticmethod
    def hash_email_for_logging(email: str) -> str:
        """Hash email for privacy-compliant logging"""
        return hashlib.sha256(email.encode()).hexdigest()[:8]


class AuthError(Exception):
    """Authentication-specific errors"""
    def __init__(self, message: str, error_code: str = None, status_code: int = 401):
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        super().__init__(message)
