"""
OTP Service - Handles OTP generation, validation, and lifecycle
Separates OTP logic from authentication routes
"""
import random
import logging
from datetime import datetime, timedelta
from typing import Optional, Tuple
from models import db, User, OtpCode

log = logging.getLogger(__name__)


class OTPService:
    """Service layer for OTP operations"""
    
    OTP_EXPIRY_MINUTES = 10
    OTP_RESEND_COOLDOWN_SECONDS = 60
    
    @staticmethod
    def generate_otp() -> str:
        """Generate 6-digit OTP"""
        return str(random.randint(100000, 999999))
    
    @classmethod
    def create_otp_for_user(cls, user: User) -> OtpCode:
        """Create new OTP for user, invalidating old ones"""
        # Invalidate existing unused OTPs
        OtpCode.query.filter_by(user_id=user.id, is_used=False).update({"is_used": True})
        db.session.flush()
        
        code = cls.generate_otp()
        otp = OtpCode(
            user_id=user.id,
            code=code,
            expires_at=datetime.utcnow() + timedelta(minutes=cls.OTP_EXPIRY_MINUTES),
            is_used=False,
        )
        db.session.add(otp)
        db.session.commit()
        return otp
    
    @classmethod
    def verify_otp(cls, user_id: int, code: str) -> Tuple[bool, Optional[str]]:
        """
        Verify OTP for user
        Returns: (is_valid, error_message)
        """
        otp = (
            OtpCode.query
            .filter_by(user_id=user_id, code=code, is_used=False)
            .filter(OtpCode.expires_at > datetime.utcnow())
            .first()
        )
        
        if not otp:
            # Check if expired
            expired = OtpCode.query.filter_by(
                user_id=user_id, code=code, is_used=False
            ).first()
            if expired:
                return False, "OTP_EXPIRED"
            return False, "Invalid OTP"
        
        # Mark as used
        otp.is_used = True
        db.session.commit()
        return True, None
    
    @classmethod
    def can_resend_otp(cls, user_id: int) -> Tuple[bool, int]:
        """
        Check if OTP can be resent (cooldown period)
        Returns: (can_resend, seconds_remaining)
        """
        recent = (
            OtpCode.query
            .filter_by(user_id=user_id, is_used=False)
            .filter(OtpCode.created_at > datetime.utcnow() - timedelta(seconds=cls.OTP_RESEND_COOLDOWN_SECONDS))
            .first()
        )
        
        if not recent:
            return True, 0
        
        seconds_left = int(
            (recent.created_at + timedelta(seconds=cls.OTP_RESEND_COOLDOWN_SECONDS)
             - datetime.utcnow()).total_seconds()
        )
        return False, max(0, seconds_left)
    
    @classmethod
    def get_expiry_minutes(cls) -> int:
        """Get OTP expiry time in minutes"""
        return cls.OTP_EXPIRY_MINUTES


class OTPError(Exception):
    """OTP-specific errors"""
    def __init__(self, message: str, error_code: str = None):
        self.message = message
        self.error_code = error_code
        super().__init__(message)
