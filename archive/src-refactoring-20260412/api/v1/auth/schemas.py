"""
Authentication API Schemas - Pydantic models for request/response validation
"""
from typing import Optional
from pydantic import BaseModel, EmailStr, validator, Field


class RegisterRequest(BaseModel):
    """User registration request"""
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)
    first_name: str = Field(..., min_length=2, max_length=100)
    last_name: str = Field(..., min_length=2, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    role: Optional[str] = Field(default='applicant', pattern='^(applicant|finalist)$')
    
    @validator('password')
    def password_complexity(cls, v):
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        return v


class LoginRequest(BaseModel):
    """User login request"""
    email: EmailStr
    password: str = Field(..., min_length=1)
    remember_me: Optional[bool] = False


class VerifyOtpRequest(BaseModel):
    """Email verification request"""
    email: EmailStr
    otp: str = Field(..., min_length=6, max_length=6, pattern='^[0-9]{6}$')


class PasswordResetRequest(BaseModel):
    """Password reset request"""
    email: EmailStr


class ChangePasswordRequest(BaseModel):
    """Change password request"""
    current_password: str = Field(..., min_length=1)
    new_password: str = Field(..., min_length=8, max_length=128)
    
    @validator('new_password')
    def password_complexity(cls, v):
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        return v


class TokenResponse(BaseModel):
    """JWT token response"""
    access_token: str
    refresh_token: str
    token_type: str = "Bearer"
    expires_in: int


class UserProfileResponse(BaseModel):
    """User profile response"""
    id: int
    public_id: str
    email: EmailStr
    first_name: str
    last_name: str
    full_name: str
    phone: Optional[str]
    role: str
    is_verified: bool
    created_at: str
