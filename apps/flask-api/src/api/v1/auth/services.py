"""
Authentication Services - Business logic for authentication operations
"""
import random
import string
import re
from typing import Tuple, Optional

from flask import current_app
from src.core.extensions import db
from src.domain.models.user import User


def create_user(email: str, password: str, first_name: str, last_name: str, 
                phone: str = None, role: str = 'applicant') -> User:
    """Create new user account"""
    user = User(
        email=email.lower().strip(),
        first_name=first_name.strip(),
        last_name=last_name.strip(),
        phone=phone.strip() if phone else None,
        role=role
    )
    user.set_password(password)
    
    db.session.add(user)
    db.session.commit()
    
    return user


def authenticate_user(email: str, password: str) -> Optional[User]:
    """Authenticate user with email and password"""
    user = User.query.filter_by(email=email.lower().strip()).first()
    if user and user.check_password(password):
        return user
    return None


def generate_otp(length: int = 6) -> str:
    """Generate random OTP code"""
    return ''.join(random.choices(string.digits, k=length))


def verify_user_email(user: User, otp: str) -> bool:
    """Verify user email with OTP"""
    from datetime import datetime, timezone
    
    if user.otp_code == otp and user.otp_expires_at > datetime.now(timezone.utc):
        user.is_verified = True
        user.otp_code = None
        user.otp_expires_at = None
        db.session.commit()
        return True
    return False


def validate_password_strength(password: str) -> Tuple[bool, str]:
    """
    Validate password meets strength requirements
    Returns: (is_valid, error_message)
    """
    if len(password) < 8:
        return False, "Password must be at least 8 characters"
    
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"
    
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"
    
    if not re.search(r'\d', password):
        return False, "Password must contain at least one digit"
    
    return True, ""


def send_otp_email(email: str, otp: str, first_name: str):
    """Send OTP verification email"""
    # TODO: Implement actual email sending via SMTP or email service
    current_app.logger.info(f"OTP for {email}: {otp}")
    # In production, use Flask-Mail or external service


def send_password_reset_email(email: str, reset_token: str, first_name: str):
    """Send password reset email"""
    current_app.logger.info(f"Password reset for {email}: {reset_token}")
    # In production, send actual email with reset link
