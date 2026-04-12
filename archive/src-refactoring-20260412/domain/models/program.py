"""
Academic Program Domain Model
"""
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any

from src.core.extensions import db


class Program(db.Model):
    """Academic program/degree offering"""
    
    __tablename__ = 'programs'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Basic Info
    code = db.Column(db.String(20), unique=True, nullable=False, index=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    
    # Classification
    level = db.Column(db.String(20), nullable=False, index=True)  # certificate, diploma, bachelor, masters, phd
    category = db.Column(db.String(30), nullable=True)  # health, business, computing, engineering, etc.
    faculty = db.Column(db.String(100), nullable=True)
    
    # Campus
    campus = db.Column(db.String(20), nullable=False, default='kampala')  # kampala, western, both
    
    # Duration
    duration_years = db.Column(db.Integer, nullable=True)
    duration_semesters = db.Column(db.Integer, nullable=True)
    
    # Fees (per semester)
    tuition_ugx = db.Column(db.Numeric(12, 2), nullable=True)
    tuition_usd = db.Column(db.Numeric(10, 2), nullable=True)
    functional_fee_ugx = db.Column(db.Numeric(12, 2), nullable=True)
    functional_fee_usd = db.Column(db.Numeric(10, 2), nullable=True)
    
    # Entry Requirements
    entry_requirements = db.Column(db.JSON, nullable=True)  # { min_points: int, essential_subjects: [], etc. }
    
    # HEC Track (if applicable)
    hec_track = db.Column(db.String(20), nullable=True)  # arts, biological, physical
    
    # Capacity
    max_enrollment = db.Column(db.Integer, nullable=True)
    current_enrollment = db.Column(db.Integer, default=0)
    
    # Status
    is_active = db.Column(db.Boolean, default=True)
    is_admission_open = db.Column(db.Boolean, default=True)
    
    # Metadata
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Relationships
    applications = db.relationship('AdmissionApplication', backref='program', lazy='dynamic')
    
    @property
    def total_fee_ugx(self) -> Optional[float]:
        """Calculate total fee per semester in UGX"""
        if self.tuition_ugx and self.functional_fee_ugx:
            return float(self.tuition_ugx) + float(self.functional_fee_ugx)
        return None
    
    @property
    def total_fee_usd(self) -> Optional[float]:
        """Calculate total fee per semester in USD"""
        if self.tuition_usd and self.functional_fee_usd:
            return float(self.tuition_usd) + float(self.functional_fee_usd)
        return None
    
    def to_dict(self, include_fees: bool = True) -> dict:
        """Serialize to dictionary"""
        data = {
            'id': self.id,
            'code': self.code,
            'name': self.name,
            'description': self.description,
            'level': self.level,
            'category': self.category,
            'faculty': self.faculty,
            'campus': self.campus,
            'duration_years': self.duration_years,
            'duration_semesters': self.duration_semesters,
            'hec_track': self.hec_track,
            'entry_requirements': self.entry_requirements,
            'is_active': self.is_active,
            'is_admission_open': self.is_admission_open,
        }
        
        if include_fees:
            data.update({
                'tuition_ugx': float(self.tuition_ugx) if self.tuition_ugx else None,
                'tuition_usd': float(self.tuition_usd) if self.tuition_usd else None,
                'functional_fee_ugx': float(self.functional_fee_ugx) if self.functional_fee_ugx else None,
                'functional_fee_usd': float(self.functional_fee_usd) if self.functional_fee_usd else None,
                'total_per_semester_ugx': self.total_fee_ugx,
                'total_per_semester_usd': self.total_fee_usd,
            })
        
        return data
    
    def __repr__(self):
        return f"<Program {self.code}: {self.name}>"


class Intake(db.Model):
    """Academic intake/semester"""
    
    __tablename__ = 'intakes'
    
    id = db.Column(db.Integer, primary_key=True)
    
    name = db.Column(db.String(50), nullable=False)  # "September 2026", "January 2027"
    academic_year = db.Column(db.String(20), nullable=False)  # "2026/2027"
    semester = db.Column(db.String(20), nullable=False)  # "Semester 1", "Semester 2"
    
    # Dates
    start_date = db.Column(db.Date, nullable=True)
    end_date = db.Column(db.Date, nullable=True)
    
    # Application Window
    application_opens = db.Column(db.Date, nullable=True)
    application_deadline = db.Column(db.Date, nullable=True)
    
    # Status
    is_active = db.Column(db.Boolean, default=True)
    is_admission_open = db.Column(db.Boolean, default=True)
    
    # Metadata
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'name': self.name,
            'academic_year': self.academic_year,
            'semester': self.semester,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'application_opens': self.application_opens.isoformat() if self.application_opens else None,
            'application_deadline': self.application_deadline.isoformat() if self.application_deadline else None,
            'is_active': self.is_active,
            'is_admission_open': self.is_admission_open,
        }
    
    def __repr__(self):
        return f"<Intake {self.name}>"
