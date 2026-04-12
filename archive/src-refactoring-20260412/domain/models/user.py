"""
User Domain Model - Core user entity with authentication
"""
from datetime import datetime, timezone
from typing import Optional, List
import uuid

from src.core.extensions import db, bcrypt


class User(db.Model):
    """User entity for applicants, finalists, and administrators"""
    
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.String(36), unique=True, default=lambda: str(uuid.uuid4()))
    
    # Authentication
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    
    # Profile
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    
    # Role-based access
    role = db.Column(db.String(20), nullable=False, default='applicant')  # applicant, finalist, admin
    
    # Status
    is_verified = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    
    # Metadata
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    last_login = db.Column(db.DateTime, nullable=True)
    
    # OTP for verification
    otp_code = db.Column(db.String(6), nullable=True)
    otp_expires_at = db.Column(db.DateTime, nullable=True)
    
    # Relationships
    applications = db.relationship('AdmissionApplication', backref='applicant', lazy='dynamic')
    
    def set_password(self, password: str):
        """Hash and set password"""
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
    
    def check_password(self, password: str) -> bool:
        """Verify password against hash"""
        return bcrypt.check_password_hash(self.password_hash, password)
    
    @property
    def full_name(self) -> str:
        """Return full name"""
        return f"{self.first_name} {self.last_name}"
    
    def to_dict(self, include_sensitive: bool = False) -> dict:
        """Serialize to dictionary"""
        data = {
            'id': self.id,
            'public_id': self.public_id,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'full_name': self.full_name,
            'phone': self.phone,
            'role': self.role,
            'is_verified': self.is_verified,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None,
        }
        
        if include_sensitive:
            data['updated_at'] = self.updated_at.isoformat() if self.updated_at else None
        
        return data
    
    def __repr__(self):
        return f"<User {self.email} ({self.role})>"
