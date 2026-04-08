from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
try:
    from flask_bcrypt import Bcrypt  # type: ignore
except ModuleNotFoundError:
    Bcrypt = None  # type: ignore

from werkzeug.security import check_password_hash, generate_password_hash

db = SQLAlchemy()
bcrypt = Bcrypt() if Bcrypt else None


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.Text, nullable=False)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20))
    national_id = db.Column(db.String(50))
    role = db.Column(db.String(20), nullable=False, default="applicant")
    is_verified = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def set_password(self, password):
        if bcrypt:
            self.password_hash = bcrypt.generate_password_hash(password).decode("utf-8")
        else:
            # Fallback for environments missing flask-bcrypt (dev/smoke-test).
            self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        if bcrypt:
            return bcrypt.check_password_hash(self.password_hash, password)
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            "id": self.id,
            "email": self.email,
            "firstName": self.first_name,
            "lastName": self.last_name,
            "phone": self.phone,
            "role": self.role,
            "nationalId": self.national_id,
            "isVerified": self.is_verified,
            "createdAt": self.created_at.isoformat() if self.created_at else None,
        }


class OtpCode(db.Model):
    __tablename__ = "otp_codes"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    code = db.Column(db.String(6), nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False)
    is_used = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship("User", backref=db.backref("otp_codes", cascade="all, delete-orphan"))


class RefreshToken(db.Model):
    __tablename__ = "refresh_tokens"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    token = db.Column(db.String(255), unique=True, nullable=False, index=True)
    expires_at = db.Column(db.DateTime, nullable=False)
    is_revoked = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_agent = db.Column(db.Text)
    ip_address = db.Column(db.String(45))

    user = db.relationship("User", backref=db.backref("refresh_tokens", cascade="all, delete-orphan"))


class Program(db.Model):
    __tablename__ = "programs"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    code = db.Column(db.String(20), unique=True, nullable=False)
    faculty = db.Column(db.String(255), nullable=False)
    department = db.Column(db.String(255))
    level = db.Column(db.String(20), nullable=False)
    duration = db.Column(db.String(50))
    description = db.Column(db.Text)
    entry_requirements = db.Column(db.Text)
    min_olevel_points = db.Column(db.Integer)
    min_alevel_points = db.Column(db.Integer)
    available_slots = db.Column(db.Integer, default=100)
    campus = db.Column(db.String(50), nullable=False, default="kampala")  # 'kampala' or 'western'
    fees_local = db.Column(db.Integer)  # Tuition fees for local/East African students (UGX)
    fees_international = db.Column(db.Integer)  # Tuition fees for international students (USD)
    functional_fees_local = db.Column(db.Integer)  # Functional fees for local students (UGX)
    functional_fees_international = db.Column(db.Integer)  # Functional fees for international students (USD)

    def to_dict(self, nationality=None):
        """Return program dict, showing appropriate fees based on nationality."""
        # Determine if student is local (East African) or international
        is_local = True  # Default to local
        if nationality:
            ea_countries = ["ugandan", "uganda", "kenyan", "kenya", "tanzanian", "tanzania", 
                          "rwandan", "rwanda", "burundian", "burundi", "south sudanese", 
                          "south sudan", "east african"]
            is_local = nationality.lower().strip() in ea_countries
        
        # Calculate fees based on nationality
        tuition_fees = self.fees_local if is_local else self.fees_international
        functional_fees = self.functional_fees_local if is_local else self.functional_fees_international
        total_fees = (tuition_fees or 0) + (functional_fees or 0)
        
        return {
            "id": self.id,
            "name": self.name,
            "code": self.code,
            "faculty": self.faculty,
            "department": self.department,
            "level": self.level,
            "duration": self.duration,
            "description": self.description,
            "entryRequirements": self.entry_requirements,
            "minOlevelPoints": self.min_olevel_points,
            "minAlevelPoints": self.min_alevel_points,
            "availableSlots": self.available_slots,
            "campus": self.campus,
            "feesLocal": self.fees_local,
            "feesInternational": self.fees_international,
            "functionalFeesLocal": self.functional_fees_local,
            "functionalFeesInternational": self.functional_fees_international,
            "tuitionFees": tuition_fees,
            "functionalFees": functional_fees,
            "totalFees": total_fees,
            "feesCurrency": "UGX" if is_local else "USD",
        }


class AdmissionApplication(db.Model):
    __tablename__ = "admission_applications"

    id = db.Column(db.Integer, primary_key=True)
    application_number = db.Column(db.String(30), unique=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    program_id = db.Column(db.Integer, db.ForeignKey("programs.id"), nullable=False)
    status = db.Column(db.String(30), nullable=False, default="pending")

    # Program choices (up to 3 programs as JSON array of IDs)
    program_choices = db.Column(db.JSON, nullable=False, default=list)

    # UNEB details (stored as structured JSON)
    exam_level = db.Column(db.String(20), nullable=False)
    exam_year = db.Column(db.Integer, nullable=False)
    index_number = db.Column(db.String(50), nullable=False)
    # uneb_grades format:
    # { "olevel": [{"subject":"Mathematics","grade":"D1","points":1},...],
    #   "alevel": [{"subject":"Mathematics","grade":"A","points":6,"subjectType":"principal"},...] }
    uneb_grades = db.Column(db.JSON, nullable=False, default=dict)

    # Uploaded files
    olevel_certificate_path = db.Column(db.Text)
    alevel_certificate_path = db.Column(db.Text)
    diploma_certificate_path = db.Column(db.Text)
    hec_certificate_path = db.Column(db.Text)
    national_certificate_path = db.Column(db.Text)
    bachelors_degree_path = db.Column(db.Text)
    masters_degree_path = db.Column(db.Text)

    # Personal info
    personal_statement = db.Column(db.Text)
    date_of_birth = db.Column(db.Date, nullable=False)
    gender = db.Column(db.String(20), nullable=False)
    nationality = db.Column(db.String(100), default="Ugandan")
    district = db.Column(db.String(100))
    session_of_study = db.Column(db.String(20))  # 'day', 'evening', or 'weekend'

    # Final-year student verification
    is_final_year = db.Column(db.Boolean, default=False)
    expected_graduation_year = db.Column(db.Integer)
    current_year_of_study = db.Column(db.Integer)
    student_number = db.Column(db.String(50))

    # Next of kin
    next_of_kin_name = db.Column(db.String(200))
    next_of_kin_phone = db.Column(db.String(20))
    next_of_kin_relationship = db.Column(db.String(50))

    admin_notes = db.Column(db.Text)
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = db.relationship("User", backref="admission_applications", lazy="joined")
    program = db.relationship("Program", backref="admission_applications", lazy="joined")

    def to_dict(self):
        return {
            "id": self.id,
            "applicationNumber": self.application_number,
            "userId": self.user_id,
            "programId": self.program_id,
            "program": self.program.to_dict() if self.program else None,
            "programChoices": self.program_choices or [],
            "status": self.status,
            "examLevel": self.exam_level,
            "examYear": self.exam_year,
            "indexNumber": self.index_number,
            "unebGrades": self.uneb_grades,
            "olevelCertificatePath": self.olevel_certificate_path,
            "alevelCertificatePath": self.alevel_certificate_path,
            "diplomaCertificatePath": self.diploma_certificate_path,
            "hecCertificatePath": self.hec_certificate_path,
            "personalStatement": self.personal_statement,
            "dateOfBirth": self.date_of_birth.isoformat() if self.date_of_birth else None,
            "gender": self.gender,
            "nationality": self.nationality,
            "district": self.district,
            "sessionOfStudy": self.session_of_study,
            "isFinalYear": self.is_final_year,
            "expectedGraduationYear": self.expected_graduation_year,
            "currentYearOfStudy": self.current_year_of_study,
            "studentNumber": self.student_number,
            "nextOfKinName": self.next_of_kin_name,
            "nextOfKinPhone": self.next_of_kin_phone,
            "nextOfKinRelationship": self.next_of_kin_relationship,
            "adminNotes": self.admin_notes,
            "submittedAt": self.submitted_at.isoformat() if self.submitted_at else None,
            "updatedAt": self.updated_at.isoformat() if self.updated_at else None,
            "applicantName": f"{self.user.first_name} {self.user.last_name}" if self.user else None,
            "applicantEmail": self.user.email if self.user else None,
        }


class ApplicationStatusHistory(db.Model):
    __tablename__ = "application_status_history"

    id = db.Column(db.Integer, primary_key=True)
    application_id = db.Column(db.Integer, db.ForeignKey("admission_applications.id"), nullable=False)
    status = db.Column(db.String(30), nullable=False)
    notes = db.Column(db.Text)
    changed_by_user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    application = db.relationship("AdmissionApplication", backref="status_history")
    changed_by = db.relationship("User")

    def to_dict(self):
        return {
            "id": self.id,
            "status": self.status,
            "notes": self.notes,
            "changedBy": self.changed_by.to_dict() if self.changed_by else None,
            "createdAt": self.created_at.isoformat()
        }


class FinalistProfile(db.Model):
    __tablename__ = "finalist_profiles"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), unique=True, nullable=False)
    program_id = db.Column(db.Integer, db.ForeignKey("programs.id"), nullable=False)
    student_number = db.Column(db.String(50), nullable=False)
    year_of_study = db.Column(db.Integer, nullable=False)
    graduation_year = db.Column(db.Integer)
    gpa = db.Column(db.Float)
    skills = db.Column(db.JSON, default=list)
    bio = db.Column(db.Text)
    linkedin_url = db.Column(db.Text)
    cv_url = db.Column(db.Text)
    is_finalist = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = db.relationship("User", backref="finalist_profile", lazy="joined")
    program = db.relationship("Program", backref="finalist_profiles", lazy="joined")

    def to_dict(self):
        return {
            "id": self.id,
            "userId": self.user_id,
            "programId": self.program_id,
            "program": self.program.to_dict() if self.program else None,
            "studentNumber": self.student_number,
            "yearOfStudy": self.year_of_study,
            "graduationYear": self.graduation_year,
            "gpa": self.gpa,
            "skills": self.skills or [],
            "bio": self.bio,
            "linkedinUrl": self.linkedin_url,
            "cvUrl": self.cv_url,
            "isFinalist": self.is_finalist,
        }


class CareerPath(db.Model):
    __tablename__ = "career_paths"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    related_programs = db.Column(db.JSON, default=list)
    skills = db.Column(db.JSON, default=list)
    potential_roles = db.Column(db.JSON, default=list)
    average_salary_range = db.Column(db.String(100))
    growth_outlook = db.Column(db.String(100))
    industry_field = db.Column(db.String(100), nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "relatedPrograms": self.related_programs or [],
            "skills": self.skills or [],
            "potentialRoles": self.potential_roles or [],
            "averageSalaryRange": self.average_salary_range,
            "growthOutlook": self.growth_outlook,
            "industryField": self.industry_field,
        }


class Opportunity(db.Model):
    __tablename__ = "opportunities"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    organization = db.Column(db.String(255), nullable=False)
    type = db.Column(db.String(20), nullable=False)
    description = db.Column(db.Text, nullable=False)
    requirements = db.Column(db.Text, nullable=False)
    required_programs = db.Column(db.JSON, default=list)
    required_skills = db.Column(db.JSON, default=list)
    location = db.Column(db.String(255))
    salary_range = db.Column(db.String(100))
    application_deadline = db.Column(db.Date, nullable=False)
    contact_email = db.Column(db.String(255))
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    posted_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self, applicant_count=None):
        return {
            "id": self.id,
            "title": self.title,
            "organization": self.organization,
            "type": self.type,
            "description": self.description,
            "requirements": self.requirements,
            "requiredPrograms": self.required_programs or [],
            "requiredSkills": self.required_skills or [],
            "location": self.location,
            "salaryRange": self.salary_range,
            "applicationDeadline": self.application_deadline.isoformat() if self.application_deadline else None,
            "contactEmail": self.contact_email,
            "isActive": self.is_active,
            "postedAt": self.posted_at.isoformat() if self.posted_at else None,
            "updatedAt": self.updated_at.isoformat() if self.updated_at else None,
            "applicantCount": applicant_count if applicant_count is not None else OpportunityApplication.query.filter_by(opportunity_id=self.id).count(),
        }


class OpportunityApplication(db.Model):
    __tablename__ = "opportunity_applications"

    id = db.Column(db.Integer, primary_key=True)
    opportunity_id = db.Column(db.Integer, db.ForeignKey("opportunities.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    status = db.Column(db.String(30), nullable=False, default="applied")
    cover_letter = db.Column(db.Text, nullable=False)
    cv_url = db.Column(db.Text)
    additional_info = db.Column(db.Text)
    admin_notes = db.Column(db.Text)
    applied_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = db.relationship("User", backref="opportunity_applications", lazy="joined")
    opportunity = db.relationship("Opportunity", backref="applications", lazy="joined")

    def to_dict(self):
        return {
            "id": self.id,
            "opportunityId": self.opportunity_id,
            "opportunity": self.opportunity.to_dict() if self.opportunity else None,
            "userId": self.user_id,
            "status": self.status,
            "coverLetter": self.cover_letter,
            "cvUrl": self.cv_url,
            "additionalInfo": self.additional_info,
            "adminNotes": self.admin_notes,
            "appliedAt": self.applied_at.isoformat() if self.applied_at else None,
            "updatedAt": self.updated_at.isoformat() if self.updated_at else None,
            "applicantName": f"{self.user.first_name} {self.user.last_name}" if self.user else None,
            "applicantEmail": self.user.email if self.user else None,
        }


class Notification(db.Model):
    __tablename__ = "notifications"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    message = db.Column(db.Text, nullable=False)
    notification_type = db.Column(db.String(50), nullable=False)  # 'application_status', 'new_opportunity', 'deadline', 'general'
    is_read = db.Column(db.Boolean, default=False, nullable=False)
    link = db.Column(db.String(255))  # Optional link to related content
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship("User", backref="notifications", lazy="joined")

    def to_dict(self):
        return {
            "id": self.id,
            "userId": self.user_id,
            "title": self.title,
            "message": self.message,
            "type": self.notification_type,
            "isRead": self.is_read,
            "link": self.link,
            "createdAt": self.created_at.isoformat() if self.created_at else None,
        }
