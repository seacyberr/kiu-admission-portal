"""
Admission Application Domain Model
"""
from datetime import datetime, timezone
from enum import Enum
from typing import Optional, Dict, Any
import uuid

from src.core.extensions import db


class ApplicationStatus(str, Enum):
    """Application status states"""
    DRAFT = "draft"
    SUBMITTED = "submitted"
    UNDER_REVIEW = "under_review"
    DOCUMENTS_PENDING = "documents_pending"
    INTERVIEW_SCHEDULED = "interview_scheduled"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    WAITLISTED = "waitlisted"
    ENROLLED = "enrolled"


class AdmissionApplication(db.Model):
    """Admission application entity"""
    
    __tablename__ = 'admission_applications'
    
    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.String(36), unique=True, default=lambda: str(uuid.uuid4()))
    
    # References
    applicant_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    program_id = db.Column(db.Integer, db.ForeignKey('programs.id'), nullable=False)
    intake_id = db.Column(db.Integer, db.ForeignKey('intakes.id'), nullable=True)
    
    # Entry Qualification
    entry_level = db.Column(db.String(20), nullable=False)  # certificate, diploma, bachelor, masters, phd
    qualification_type = db.Column(db.String(20), nullable=False)  # o_level, a_level, diploma, degree, etc.
    
    # UNEB/Academic Details (stored as JSON for flexibility)
    academic_records = db.Column(db.JSON, nullable=True)  # { subjects: [], grades: [], year: int, index_number: str }
    
    # Curriculum Version (for Uganda dual curriculum)
    curriculum_version = db.Column(db.String(10), default='old')  # 'old' or 'new'
    
    # HEC Track (if applicable)
    hec_track = db.Column(db.String(20), nullable=True)  # arts, biological, physical
    
    # Personal Information
    date_of_birth = db.Column(db.Date, nullable=True)
    gender = db.Column(db.String(10), nullable=True)
    nationality = db.Column(db.String(50), default='Ugandan')
    district = db.Column(db.String(50), nullable=True)
    
    # Next of Kin
    next_of_kin_name = db.Column(db.String(100), nullable=True)
    next_of_kin_phone = db.Column(db.String(20), nullable=True)
    next_of_kin_relationship = db.Column(db.String(20), nullable=True)
    
    # Documents
    documents = db.Column(db.JSON, nullable=True)  # { certificate_url: str, transcript_url: str, ... }
    
    # Personal Statement
    personal_statement = db.Column(db.Text, nullable=True)
    
    # Application Status
    status = db.Column(db.String(30), default=ApplicationStatus.DRAFT.value, index=True)
    status_reason = db.Column(db.Text, nullable=True)  # Reason for rejection/waitlist
    
    # Payment
    application_fee_paid = db.Column(db.Boolean, default=False)
    application_fee_amount = db.Column(db.Numeric(10, 2), nullable=True)
    payment_reference = db.Column(db.String(100), nullable=True)
    
    # Admin Review
    reviewed_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    reviewed_at = db.Column(db.DateTime, nullable=True)
    reviewer_notes = db.Column(db.Text, nullable=True)
    
    # Interview
    interview_date = db.Column(db.DateTime, nullable=True)
    interview_notes = db.Column(db.Text, nullable=True)
    
    # Metadata
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    submitted_at = db.Column(db.DateTime, nullable=True)
    
    def submit(self):
        """Mark application as submitted"""
        self.status = ApplicationStatus.SUBMITTED.value
        self.submitted_at = datetime.now(timezone.utc)
    
    def update_status(self, status: ApplicationStatus, reason: str = None, reviewer_id: int = None):
        """Update application status"""
        self.status = status.value
        self.status_reason = reason
        if reviewer_id:
            self.reviewed_by = reviewer_id
            self.reviewed_at = datetime.now(timezone.utc)
    
    def to_dict(self, include_admin: bool = False) -> dict:
        """Serialize to dictionary"""
        data = {
            'id': self.id,
            'public_id': self.public_id,
            'applicant_id': self.applicant_id,
            'program_id': self.program_id,
            'entry_level': self.entry_level,
            'qualification_type': self.qualification_type,
            'curriculum_version': self.curriculum_version,
            'hec_track': self.hec_track,
            'academic_records': self.academic_records,
            'date_of_birth': self.date_of_birth.isoformat() if self.date_of_birth else None,
            'gender': self.gender,
            'nationality': self.nationality,
            'district': self.district,
            'status': self.status,
            'application_fee_paid': self.application_fee_paid,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'submitted_at': self.submitted_at.isoformat() if self.submitted_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
        
        if include_admin:
            data.update({
                'reviewed_by': self.reviewed_by,
                'reviewed_at': self.reviewed_at.isoformat() if self.reviewed_at else None,
                'reviewer_notes': self.reviewer_notes,
                'interview_date': self.interview_date.isoformat() if self.interview_date else None,
                'interview_notes': self.interview_notes,
            })
        
        return data
    
    def __repr__(self):
        return f"<AdmissionApplication {self.public_id} ({self.status})>"
