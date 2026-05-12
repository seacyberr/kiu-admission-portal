import os
import uuid
import re
import logging
from flask import Blueprint, request, jsonify, current_app, g
from flask_jwt_extended import jwt_required
from datetime import datetime, date
import random
import string
from functools import wraps
from werkzeug.utils import secure_filename
from models import db, AdmissionApplication, Program, User
from sqlalchemy.orm import joinedload
from routes.auth import get_current_user

logger = logging.getLogger(__name__)
from services.qualification_service import UgandaQualificationService

# Maintain backward compatibility
UgandaQualificationChecker = UgandaQualificationService
from utils.error_handlers import (
    handle_kiu_error, validate_json_payload, ValidationError, 
    NotFoundError, ConflictError, sanitize_input, validate_phone,
    log_application_action
)
from utils.caching import (
    cache_manager, cache_program_list, cache_user_data, 
    cache_application_status, invalidate_user_cache, invalidate_program_cache
)
from utils.database import atomic_transaction, get_or_404
from utils.api_response import success_response, paginated_response, bad_request, unauthorized, forbidden, not_found, created


def sanitize_text(text):
    if not text or not isinstance(text, str):
        return text
    text = text.strip()
    text = re.sub(r'<[^>]*>', '', text)
    text = re.sub(r'javascript:', '', text, flags=re.IGNORECASE)
    text = re.sub(r'on\w+\s*=', '', text, flags=re.IGNORECASE)
    if len(text) > 5000:
        text = text[:5000]
    return text


admission_bp = Blueprint("admission", __name__)

ALLOWED_EXTENSIONS = {"pdf", "jpg", "jpeg", "png"}

# Maps multipart field `type` → AdmissionApplication column (avoids mismatched suffixes).
CERT_UPLOAD_FIELDS = {
    "olevel": "olevel_certificate_path",
    "alevel": "alevel_certificate_path",
    "diploma": "diploma_certificate_path",
    "hec": "hec_certificate_path",
    "national_certificate": "national_certificate_path",
    "bachelors": "bachelors_degree_path",
    "masters": "masters_degree_path",
}

# ── UNEB Grading System ──────────────────────────────────────────────────────
VALID_OLEVEL_GRADES = [
    "D1", "D2", "D3", "D4", "D5", "D6", "D7", "D8", "F",  # new curriculum
    "C3", "C4", "C5", "C6", "P7", "P8", "F9",              # old curriculum
]
VALID_ALEVEL_GRADES = ["A", "B", "C", "D", "E", "O", "F"]

# BUG FIX: old OLEVEL_GRADE_POINTS only had old-curriculum grades (C3–F9).
# New curriculum grades D3–D8 and F were valid but had no points mapping,
# so calculate_olevel_points() returned 0 for those grades, making every
# new-curriculum student appear to have a perfect aggregate and bypassing
# the minimum-points validation entirely.
OLEVEL_GRADE_POINTS = {
    # New curriculum (2024+)
    "D1": 1, "D2": 2, "D3": 3, "D4": 4, "D5": 5, "D6": 6, "D7": 7, "D8": 8, "F": 9,
    # Old curriculum
    "C3": 3, "C4": 4, "C5": 5, "C6": 6, "P7": 7, "P8": 8, "F9": 9,
}
ALEVEL_GRADE_POINTS = {"A": 6, "B": 5, "C": 4, "D": 3, "E": 2, "O": 1, "F": 0}

# Explicit sort order for program levels (degree first as intended)
_LEVEL_ORDER = {"degree": 1, "masters": 2, "phd": 3, "hec": 4, "diploma": 5}


def calculate_olevel_points(olevel_grades):
    total = 0
    for entry in olevel_grades:
        grade = entry.get("grade", "").upper()
        total += OLEVEL_GRADE_POINTS.get(grade, 9)   # unknown grade = worst (9)
    return total


def calculate_alevel_points(alevel_grades):
    total = 0
    for entry in alevel_grades:
        grade = entry.get("grade", "").upper()
        subject_type = entry.get("subjectType", "").lower()
        if subject_type == "principal":
            total += ALEVEL_GRADE_POINTS.get(grade, 0)
    return total


def validate_uneb_grades(uneb_grades, exam_level):
    errors = []
    for entry in uneb_grades.get("olevel", []):
        grade = entry.get("grade", "").upper()
        subject = entry.get("subject", "")
        if not subject:
            errors.append("Each O-Level grade entry must have a 'subject' field")
        if grade not in VALID_OLEVEL_GRADES:
            errors.append(f"Invalid O-Level grade '{grade}' for {subject}. Valid: {', '.join(VALID_OLEVEL_GRADES)}")
    for entry in uneb_grades.get("alevel", []):
        grade = entry.get("grade", "").upper()
        subject = entry.get("subject", "")
        subject_type = entry.get("subjectType", "").lower()
        if not subject:
            errors.append("Each A-Level grade entry must have a 'subject' field")
        if grade not in VALID_ALEVEL_GRADES:
            errors.append(f"Invalid A-Level grade '{grade}' for {subject}. Valid: {', '.join(VALID_ALEVEL_GRADES)}")
        if subject_type not in ("principal", "subsidiary"):
            errors.append(f"A-Level subjectType for {subject} must be 'principal' or 'subsidiary'")
    return errors


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def generate_application_number():
    year = datetime.now().year
    suffix = "".join(random.choices(string.digits, k=6))
    return f"KIU/{year}/{suffix}"


# ---------------------------------------------------------------------------
# Programs
# ---------------------------------------------------------------------------

@admission_bp.route("/programs", methods=["GET"])
def list_programs():
    """
    List all academic programs.

    BUG FIX (ordering): Program.level.desc() ordered alphabetically
    descending, giving hec > diploma > degree — the opposite of what was
    intended.  Now uses an explicit integer sort key via CASE expression
    so "degree" always sorts first.
    """
    from sqlalchemy import case

    level = request.args.get("level")
    campus = request.args.get("campus")

    query = Program.query
    if level:
        query = query.filter_by(level=level)
    if campus:
        query = query.filter_by(campus=campus)

    # BUG FIX: explicit ordering by intent — degree first, then masters/phd,
    # then hec/diploma.  SQLAlchemy case() maps each level string to an
    # integer priority so ORDER BY is deterministic regardless of DB collation.
    level_order = case(
        {
            "degree": 1,
            "masters": 2,
            "phd": 3,
            "hec": 4,
            "diploma": 5,
        },
        value=Program.level,
        else_=6,
    )
    programs = query.order_by(level_order, Program.campus, Program.faculty, Program.name).all()

    return success_response({"programs": [p.to_dict() for p in programs]})


@admission_bp.route("/programs/<int:program_id>", methods=["GET"])
def get_program(program_id):
    program = db.session.get(Program, program_id)
    if not program:
        return not_found("Program not found")
    return success_response(program.to_dict())


# ---------------------------------------------------------------------------
# Applications
# ---------------------------------------------------------------------------

@admission_bp.route("/applications", methods=["POST"])
@jwt_required()
@handle_kiu_error
@validate_json_payload(required_fields=["programIds", "examLevel", "examYear", "indexNumber", "unebGrades", "dateOfBirth", "gender"])
def create_application():
    user, error = get_current_user()
    if error:
        raise ValidationError(error)
    if user.role not in ("applicant",):
        raise ValidationError("Only applicants can submit admission applications")

    data = request.get_json()

    program_ids = data.get("programIds", [])
    if not isinstance(program_ids, list) or len(program_ids) == 0:
        raise ValidationError("At least one program must be selected")
    if len(program_ids) > 3:
        raise ValidationError("Maximum 3 program choices allowed")

    programs = []
    for pid in program_ids:
        prog = db.session.get(Program, pid)
        if not prog:
            raise NotFoundError(f"Program ID {pid} not found")
        programs.append(prog)

    program = programs[0]

    existing = AdmissionApplication.query.filter_by(user_id=user.id).first()
    if existing:
        raise ConflictError("You have already submitted an application")

    exam_level_raw = data.get("examLevel", "").lower().strip()
    # Normalize exam level aliases
    exam_level_map = {
        "o_level": "o_level", "olevel": "o_level", "uce": "o_level",
        "a_level": "a_level", "alevel": "a_level", "uace": "a_level",
        "diploma": "diploma",
        "hec": "hec",
        "masters": "masters", "master": "masters",
        "phd": "phd", "doctorate": "phd"
    }
    exam_level = exam_level_map.get(exam_level_raw, exam_level_raw)
    valid_exam_levels = ("o_level", "a_level", "diploma", "hec", "masters", "phd")
    if exam_level not in valid_exam_levels:
        raise ValidationError(f"examLevel must be one of: {', '.join(valid_exam_levels)}", "examLevel", exam_level)

    if program.level == "degree" and exam_level == "o_level":
        raise ValidationError("Degree programs require A-Level, Diploma, or HEC qualifications.")
    if program.level == "masters" and exam_level not in ("a_level", "diploma", "hec", "masters"):
        raise ValidationError("Masters programs require a bachelor's degree qualification.")
    if program.level == "phd" and exam_level not in ("masters", "phd"):
        raise ValidationError("PhD programs require a master's degree qualification.")

    try:
        dob = date.fromisoformat(data["dateOfBirth"])
    except (ValueError, TypeError):
        raise ValidationError("Invalid dateOfBirth format (use YYYY-MM-DD)", "dateOfBirth", data.get("dateOfBirth"))

    uneb_grades = data.get("unebGrades", {})
    if not isinstance(uneb_grades, dict):
        raise ValidationError("unebGrades must be an object", "unebGrades")

    grade_errors = validate_uneb_grades(uneb_grades, exam_level)
    if grade_errors:
        raise ValidationError("; ".join(grade_errors))

    olevel_grades = uneb_grades.get("olevel", [])
    alevel_grades = uneb_grades.get("alevel", [])

    if exam_level == "o_level" and len(olevel_grades) < 5:
        raise ValidationError("O-Level (UCE) requires at least 5 subjects")
    if exam_level == "a_level":
        if len(olevel_grades) < 5:
            raise ValidationError("Please provide your O-Level (UCE) results as well")
        principals = [s for s in alevel_grades if s.get("subjectType", "").lower() == "principal"]
        if len(principals) < 2:
            raise ValidationError("A-Level (UACE) requires at least 2 principal subjects")

    olevel_points = calculate_olevel_points(olevel_grades)
    alevel_points = calculate_alevel_points(alevel_grades) if exam_level == "a_level" else None

    if exam_level in ("o_level", "a_level") and program.min_olevel_points is not None:
        if olevel_points > program.min_olevel_points:
            raise ValidationError(
                f"Your O-Level aggregate ({olevel_points}) does not meet the minimum "
                f"requirement for {program.name} (aggregate ≤ {program.min_olevel_points})."
            )
    if exam_level == "a_level" and program.min_alevel_points is not None:
        if (alevel_points or 0) < program.min_alevel_points:
            raise ValidationError(
                f"Your A-Level points ({alevel_points or 0}) do not meet the minimum "
                f"requirement for {program.name} ({program.min_alevel_points}+ points)."
            )

    app_number = generate_application_number()
    while AdmissionApplication.query.filter_by(application_number=app_number).first():
        app_number = generate_application_number()

    nationality = sanitize_input(data.get("nationality", "Ugandan"))
    district = sanitize_input(data.get("district", ""))
    next_of_kin_name = sanitize_input(data.get("nextOfKinName", ""))
    next_of_kin_phone = sanitize_input(data.get("nextOfKinPhone", ""))
    next_of_kin_relationship = sanitize_input(data.get("nextOfKinRelationship", ""))
    student_number = sanitize_input(data.get("studentNumber", ""))
    personal_statement = sanitize_input(data.get("personalStatement", ""), max_length=2000)

    # Validate phone number if provided
    if next_of_kin_phone and not validate_phone(next_of_kin_phone):
        raise ValidationError("Invalid next of kin phone number format", "nextOfKinPhone", next_of_kin_phone)

    application = AdmissionApplication(
        application_number=app_number,
        user_id=user.id,
        program_id=program.id,
        program_choices=program_ids,
        exam_level=exam_level,
        exam_year=int(data["examYear"]),
        index_number=sanitize_input(data["indexNumber"]),
        uneb_grades=uneb_grades,
        personal_statement=personal_statement,
        date_of_birth=dob,
        gender=data["gender"],
        nationality=nationality,
        district=district,
        session_of_study=data.get("sessionOfStudy"),
        is_final_year=data.get("isFinalYear", False),
        expected_graduation_year=data.get("expectedGraduationYear"),
        current_year_of_study=data.get("currentYearOfStudy"),
        student_number=student_number,
        next_of_kin_name=next_of_kin_name,
        next_of_kin_phone=next_of_kin_phone,
        next_of_kin_relationship=next_of_kin_relationship,
        status="pending",
    )
    try:
        with atomic_transaction():
            db.session.add(application)
            # Auto-committed on success, auto-rolled back on exception
        
        # Log successful application creation (outside transaction)
        log_application_action(
            action="created",
            application_id=application.id,
            user_id=user.id,
            details={
                "program_ids": program_ids,
                "exam_level": exam_level,
                "application_number": app_number
            }
        )
        
        return created(application.to_dict(), message="Application created successfully")
        
    except Exception as e:
        logger.error(f"Failed to create application: {str(e)}", exc_info=True)
        raise ValidationError(f"Failed to save application: {str(e)}")


@admission_bp.route("/applications/<int:app_id>/certificate", methods=["POST"])
@jwt_required()
@handle_kiu_error
def upload_certificate(app_id):
    user, error = get_current_user()
    if error:
        raise ValidationError(error)

    application = db.session.get(AdmissionApplication, app_id)
    if not application:
        raise NotFoundError("Application not found")
    if application.user_id != user.id and user.role != "admin":
        raise ValidationError("Access denied")

    cert_type = request.form.get("type", "olevel")
    if cert_type not in CERT_UPLOAD_FIELDS:
        allowed = ", ".join(sorted(CERT_UPLOAD_FIELDS.keys()))
        raise ValidationError(f"type must be one of: {allowed}", "type", cert_type)

    if "file" not in request.files:
        raise ValidationError("No file provided")

    file = request.files["file"]
    if not file or file.filename == "":
        raise ValidationError("Empty file")
    if not allowed_file(file.filename):
        raise ValidationError("Only PDF, JPG, JPEG, PNG allowed")

    # Validate file extension against allowed types
    if "." not in file.filename:
        raise ValidationError("File must have an extension", "file", file.filename)
    ext = file.filename.rsplit(".", 1)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise ValidationError(f"Invalid file extension '.{ext}'. Allowed: {', '.join(ALLOWED_EXTENSIONS)}", "file", ext)

    try:
        # Generate safe filename - use only validated extension from user input
        # UUID ensures uniqueness, no user input in filename base
        unique_name = f"{app_id}_{cert_type}_{uuid.uuid4().hex[:8]}.{ext}"
        cert_dir = os.path.join(current_app.config["UPLOAD_FOLDER"], "certificates")
        os.makedirs(cert_dir, exist_ok=True)
        save_path = os.path.join(cert_dir, secure_filename(unique_name))
        file.save(save_path)

        url_path = f"/api/uploads/certificates/{secure_filename(unique_name)}"
        
        with atomic_transaction():
            setattr(application, CERT_UPLOAD_FIELDS[cert_type], url_path)
            # Auto-committed on success
        
        # Log successful certificate upload (outside transaction)
        log_application_action(
            action="certificate_uploaded",
            application_id=app_id,
            user_id=user.id,
            details={
                "certificate_type": cert_type,
                "file_name": file.filename,
                "file_size": os.path.getsize(save_path)
            }
        )
        
        return success_response({
            "path": url_path,
            "application": application.to_dict(),
        }, message=f"{cert_type.upper()} certificate uploaded successfully")
        
    except Exception as e:
        logger.error(f"Failed to upload certificate: {str(e)}", exc_info=True)
        raise ValidationError(f"Failed to upload certificate: {str(e)}")


@admission_bp.route("/applications/mine", methods=["GET"])
@jwt_required()
@handle_kiu_error
def get_my_application():
    user, error = get_current_user()
    if error:
        raise ValidationError(error)
    # Use eager loading to prevent N+1 queries
    application = (
        AdmissionApplication.query
        .options(joinedload(AdmissionApplication.program))
        .filter_by(user_id=user.id)
        .first()
    )
    return success_response({"application": application.to_dict() if application else None})


@admission_bp.route("/applications/<int:app_id>", methods=["GET"])
@jwt_required()
@handle_kiu_error
def get_application(app_id):
    user, error = get_current_user()
    if error:
        raise ValidationError(error)
    # Use eager loading to prevent N+1 queries
    application = (
        AdmissionApplication.query
        .options(joinedload(AdmissionApplication.program))
        .filter_by(id=app_id)
        .first()
    )
    if not application:
        raise NotFoundError("Application not found")
    if application.user_id != user.id and user.role != "admin":
        raise ValidationError("Access denied")
    return success_response(application.to_dict())


@admission_bp.route("/applications", methods=["GET"])
@jwt_required()
@handle_kiu_error
def list_applications():
    user, error = get_current_user()
    if error:
        raise ValidationError(error)
    if user.role != "admin":
        raise ValidationError("Access denied")

    page = request.args.get("page", 1, type=int)
    per_page = min(request.args.get("perPage", 20, type=int), 100)
    status_filter = request.args.get("status")
    search = request.args.get("search", "")

    # Use eager loading to prevent N+1 queries
    query = (
        AdmissionApplication.query
        .join(User)
        .options(joinedload(AdmissionApplication.program))
        .options(joinedload(AdmissionApplication.user))
    )
    if status_filter:
        query = query.filter(AdmissionApplication.status == status_filter)
    if search:
        # Sanitize search term to prevent LIKE injection
        sanitized_search = search.replace("%", "").replace("_", "").replace("[", "").replace("]", "")
        search_pattern = f"%{sanitized_search}%"
        query = query.filter(
            (User.first_name.ilike(search_pattern)) |
            (User.last_name.ilike(search_pattern)) |
            (User.email.ilike(search_pattern)) |
            (AdmissionApplication.application_number.ilike(search_pattern))
        )

    paginated = query.order_by(AdmissionApplication.submitted_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    return paginated_response(
        items=[a.to_dict() for a in paginated.items],
        total=paginated.total,
        page=page,
        per_page=per_page,
        data_key="applications"
    )


@admission_bp.route("/applications/statistics", methods=["GET"])
@jwt_required()
@handle_kiu_error
def get_application_statistics():
    """Get application statistics for admin dashboard"""
    # Check admin role
    user, error = get_current_user()
    if error or not user or user.role not in ["admin", "admissions_officer"]:
        raise ValidationError("Admin access required")
    
    # Get all applications with eager loading to prevent N+1 queries
    applications = AdmissionApplication.query.options(
        joinedload(AdmissionApplication.program)
    ).all()
    
    # Calculate statistics
    total = len(applications)
    by_status = {}
    by_qualification = {}
    by_program = {}
    
    for app in applications:
        # By status
        status = app.status or "pending"
        by_status[status] = by_status.get(status, 0) + 1
        
        # By qualification type
        qual = app.exam_level or "unknown"
        by_qualification[qual] = by_qualification.get(qual, 0) + 1
        
        # By program
        program_name = app.program.name if app.program else "Unknown"
        by_program[program_name] = by_program.get(program_name, 0) + 1
    
    # Recent applications (last 30 days)
    from datetime import datetime, timedelta
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    recent_count = AdmissionApplication.query.filter(
        AdmissionApplication.created_at >= thirty_days_ago
    ).count()
    
    return success_response({
        "total": total,
        "by_status": by_status,
        "by_qualification": by_qualification,
        "by_program": dict(sorted(by_program.items(), key=lambda x: x[1], reverse=True)[:10]),  # Top 10
        "recent_30_days": recent_count,
        "generated_at": datetime.utcnow().isoformat()
    })


@admission_bp.route("/applications/<int:app_id>/status", methods=["PATCH"])
@jwt_required()
@handle_kiu_error
def update_application_status(app_id):
    user, error = get_current_user()
    if error:
        raise ValidationError(error)
    if user.role != "admin":
        raise ValidationError("Access denied")

    application = db.session.get(AdmissionApplication, app_id)
    if not application:
        raise NotFoundError("Application not found")

    data = request.get_json() or {}
    new_status = data.get("status")
    valid_statuses = ["pending", "under_review", "accepted", "rejected", "waitlisted"]
    if new_status not in valid_statuses:
        raise ValidationError(f"status must be one of: {', '.join(valid_statuses)}", "status", new_status)

    application.status = new_status
    if "adminNotes" in data:
        application.admin_notes = data["adminNotes"]

    if "programId" in data:
        new_program_id = data["programId"]
        prog = db.session.get(Program, new_program_id)
        if not prog:
            raise NotFoundError("Program not found")
        if application.program_choices and new_program_id not in application.program_choices:
            raise ValidationError("Selected program must be one of the applicant's choices")
        application.program_id = new_program_id

    try:
        db.session.commit()
        
        # Log status update
        log_application_action(
            action="status_updated",
            application_id=app_id,
            user_id=user.id,
            details={
                "new_status": new_status,
                "admin_notes": data.get("adminNotes", ""),
                "program_changed": "programId" in data
            }
        )
        
        return success_response(application.to_dict(), message="Application status updated")
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Failed to update application status: {str(e)}", exc_info=True)
        raise ValidationError(f"Failed to update application: {str(e)}")


@admission_bp.route("/check-qualifications", methods=["POST"])
def check_qualifications():
    """
    Check qualifications against official NCHE/UHEQF standards
    Returns eligibility status, met requirements, missing requirements and recommended pathways
    """
    data = request.get_json()
    if not data:
        return bad_request("No JSON body provided")
    
    olevel_grades = data.get("olevelGrades", [])
    alevel_grades = data.get("alevelGrades", [])
    program_level = data.get("programLevel")
    
    result = UgandaQualificationChecker.get_recommended_pathways(olevel_grades, alevel_grades)
    
    # If specific program level is provided, check eligibility
    if program_level:
        olevel_result = UgandaQualificationChecker.validate_olevel(olevel_grades)
        alevel_result = UgandaQualificationChecker.validate_alevel(alevel_grades) if alevel_grades else None
        
        eligible, message = UgandaQualificationChecker.check_program_eligibility(
            program_level,
            olevel_result,
            alevel_result,
            has_diploma = data.get("hasDiploma", False),
            has_hec = data.get("hasHec", False)
        )
        
        result["programEligibility"] = {
            "level": program_level,
            "eligible": eligible,
            "message": message
        }
    
    return success_response(result)


@admission_bp.route("/analytics", methods=["GET"])
@jwt_required()
def get_analytics():
    """Admin analytics with dropout prediction and program demand trends."""
    user, error = get_current_user()
    if error:
        return unauthorized(error)
    if user.role != "admin":
        return forbidden("Admin access required")

    from sqlalchemy import func, extract

    total = AdmissionApplication.query.count()
    by_status = db.session.query(
        AdmissionApplication.status, func.count(AdmissionApplication.id)
    ).group_by(AdmissionApplication.status).all()
    by_program = db.session.query(
        Program.name, func.count(AdmissionApplication.id)
    ).join(AdmissionApplication).group_by(Program.name).all()

    # BUG FIX: eager-load program and user relationships to avoid N+1 queries
    from sqlalchemy.orm import joinedload
    applications = (
        AdmissionApplication.query
        .options(joinedload(AdmissionApplication.program), joinedload(AdmissionApplication.user))
        .all()
    )

    dropout_risk_apps = []
    for app in applications:
        # BUG FIX: replaced deprecated Program.query.get() with db.session.get()
        program = app.program   # already eager-loaded
        if not program:
            continue

        alevel_grades = app.uneb_grades.get("alevel", []) if app.uneb_grades else []
        principal_grades = [g for g in alevel_grades if g.get("subjectType", "").lower() == "principal"]
        total_points = sum(ALEVEL_GRADE_POINTS.get(g.get("grade", "").upper(), 0) for g in principal_grades)

        risk_level = "low"
        risk_factors = []

        if program.min_alevel_points and total_points < program.min_alevel_points:
            risk_level = "high"
            risk_factors.append(f"A-Level points ({total_points}) below minimum ({program.min_alevel_points})")

        has_gp = any(g.get("subject", "").lower() in ["general paper", "gp"] for g in alevel_grades)
        if not has_gp and program.name in ["Bachelor of Laws - Day", "Bachelor of Laws - Weekend/Evening", "BA International Relations and Diplomatic Studies", "Bachelor of Public Administration"]:
            risk_level = "high" if risk_level == "high" else "medium"
            risk_factors.append("Missing General Paper for program that requires it")

        competitive_programs = ["Bachelor of Medicine and Bachelor of Surgery (MBChB)", "Bachelor of Dental Surgery", "Bachelor of Pharmacy", "Bachelor of Laws - Day", "Bachelor of Laws - Weekend/Evening"]
        if program.name in competitive_programs and total_points < 12:
            risk_level = "high" if risk_level == "high" else "medium"
            risk_factors.append(f"Competitive program ({program.name}) with low points")

        if risk_level != "low":
            dropout_risk_apps.append({
                "applicationId": app.id,
                "applicationNumber": app.application_number,
                "studentName": f"{app.user.first_name} {app.user.last_name}" if app.user else "Unknown",
                "program": program.name,
                "totalPoints": total_points,
                "minRequired": program.min_alevel_points,
                "riskLevel": risk_level,
                "riskFactors": risk_factors,
                "status": app.status,
            })

    current_year = datetime.now().year
    monthly_trends = []
    for month in range(1, 13):
        count = AdmissionApplication.query.filter(
            extract('year', AdmissionApplication.submitted_at) == current_year,
            extract('month', AdmissionApplication.submitted_at) == month
        ).count()
        monthly_trends.append({
            "month": month,
            "monthName": datetime(current_year, month, 1).strftime("%B"),
            "applications": count,
        })

    top_programs = db.session.query(
        Program.name,
        Program.faculty,
        func.count(AdmissionApplication.id).label('application_count')
    ).join(AdmissionApplication).group_by(
        Program.id, Program.name, Program.faculty
    ).order_by(func.count(AdmissionApplication.id).desc()).limit(10).all()

    nche_compliance = {"withGeneralPaper": 0, "withoutGeneralPaper": 0, "sufficientPoints": 0, "insufficientPoints": 0}

    for app in applications:
        alevel_grades = app.uneb_grades.get("alevel", []) if app.uneb_grades else []
        has_gp = any(g.get("subject", "").lower() in ["general paper", "gp"] for g in alevel_grades)
        nche_compliance["withGeneralPaper" if has_gp else "withoutGeneralPaper"] += 1

        principal_grades = [g for g in alevel_grades if g.get("subjectType", "").lower() == "principal"]
        total_points = sum(ALEVEL_GRADE_POINTS.get(g.get("grade", "").upper(), 0) for g in principal_grades)
        nche_compliance["sufficientPoints" if total_points >= 6 else "insufficientPoints"] += 1

    gender_distribution = db.session.query(
        AdmissionApplication.gender, func.count(AdmissionApplication.id)
    ).group_by(AdmissionApplication.gender).all()

    session_distribution = db.session.query(
        AdmissionApplication.session_of_study, func.count(AdmissionApplication.id)
    ).group_by(AdmissionApplication.session_of_study).all()

    return success_response({
        "summary": {
            "totalApplications": total,
            "byStatus": {s: c for s, c in by_status},
            "byProgram": [{"program": p, "count": c} for p, c in by_program],
        },
        "dropoutRisk": {
            "totalAtRisk": len(dropout_risk_apps),
            "highRisk": len([a for a in dropout_risk_apps if a["riskLevel"] == "high"]),
            "mediumRisk": len([a for a in dropout_risk_apps if a["riskLevel"] == "medium"]),
            "applications": dropout_risk_apps[:20],
        },
        "programDemand": {
            "monthlyTrends": monthly_trends,
            "topPrograms": [
                {"name": p.name, "faculty": p.faculty, "applications": p.application_count}
                for p in top_programs
            ],
        },
        "ncheCompliance": nche_compliance,
        "demographics": {
            "genderDistribution": {g: c for g, c in gender_distribution},
            "sessionDistribution": {s or "Not specified": c for s, c in session_distribution},
        },
        "generatedAt": datetime.utcnow().isoformat(),
    })


# ---------------------------------------------------------------------------
# Application Wizard API - Multi-step Application Submission
# ---------------------------------------------------------------------------

@admission_bp.route("/applications/wizard", methods=["POST"])
@handle_kiu_error
def create_application_wizard():
    """
    Create application from wizard data (all 6 steps combined)
    Supports all NCHE qualification types: UACE, HEC, Diploma, National Certificate
    """
    user, error = get_current_user()
    if error:
        raise ValidationError(error)
    if user.role not in ("applicant",):
        raise ValidationError("Only applicants can submit admission applications")

    data = request.get_json()
    if not data:
        raise ValidationError("Request body is required")

    # Check for existing application
    existing = AdmissionApplication.query.filter_by(user_id=user.id).first()
    if existing:
        raise ConflictError("You have already submitted an application")

    # Validate required fields from all steps
    required_fields = ["personalInfo", "contactInfo", "educationInfo", "programChoices"]
    for field in required_fields:
        if field not in data:
            raise ValidationError(f"Missing required field: {field}")

    # Extract data
    personal_info = data["personalInfo"]
    contact_info = data["contactInfo"]
    education_info = data["educationInfo"]
    program_choices = data["programChoices"]
    documents = data.get("documents", {})

    # Validate program choices
    if not isinstance(program_choices, list) or len(program_choices) == 0:
        raise ValidationError("At least one program must be selected")
    if len(program_choices) > 3:
        raise ValidationError("Maximum 3 program choices allowed")

    programs = []
    for pid in program_choices:
        prog = db.session.get(Program, pid)
        if not prog:
            raise NotFoundError(f"Program ID {pid} not found")
        programs.append(prog)

    first_program = programs[0]

    # Validate and normalize qualification type
    qualification_type_raw = education_info.get("qualificationType", "").lower().strip()
    # Reject ambiguous 'certificate' - force users to be explicit
    if qualification_type_raw == "certificate":
        raise ValidationError(
            "Ambiguous qualification type 'certificate'. Please use one of:\n"
            "• 'national_certificate' - if you hold a 2-year vocational/technical qualification\n"
            "• 'uce' or 'uace' - if you're referring to your O-Level/A-Level certificate\n"
            "Do not use 'certificate' alone as it is unclear."
        )
    # Normalize aliases: olevel = uce, alevel = uace
    qualification_map = {
        "uace": "uace", "alevel": "uace", "a_level": "uace",
        "uce": "uce", "olevel": "uce", "o_level": "uce",
        "hec": "hec",
        "diploma": "diploma",
        "national_certificate": "national_certificate",
        "bachelors": "bachelors", "bachelor": "bachelors", "degree": "bachelors",
        "masters": "masters", "master": "masters"
    }
    qualification_type = qualification_map.get(qualification_type_raw, qualification_type_raw)
    valid_qualifications = ("uace", "uce", "hec", "diploma", "national_certificate", "bachelors", "masters")
    if qualification_type not in valid_qualifications:
        raise ValidationError(f"Invalid qualification type. Must be one of: {', '.join(valid_qualifications)}")

    # Validate based on qualification type
    if qualification_type == "uace":
        uace_data = education_info.get("uace", {})
        if not uace_data.get("subjects") or len(uace_data.get("subjects", [])) < 2:
            raise ValidationError("UACE requires at least 2 principal subjects")
        
        uce_data = education_info.get("uce", {})
        if not uce_data.get("subjects") or len(uce_data.get("subjects", [])) < 5:
            raise ValidationError("UCE requires at least 5 subjects")

    elif qualification_type == "uce":
        # UCE-only entry for Certificate/Diploma programs
        uce_data = education_info.get("uce", {})
        if not uce_data.get("subjects") or len(uce_data.get("subjects", [])) < 5:
            raise ValidationError("UCE requires at least 5 subjects for admission")
        
        # UCE-only applicants can only enter Certificate or Diploma programs
        if first_program.level in ("degree", "masters", "phd"):
            raise ValidationError("UCE alone only qualifies for Certificate or Diploma programs. Degree programs require UACE, HEC, or Diploma.")

    elif qualification_type == "hec":
        hec_track = education_info.get("hecTrack")
        if hec_track not in ("arts", "biological", "physical"):
            raise ValidationError("HEC track must be 'arts', 'biological', or 'physical'")

    elif qualification_type == "national_certificate":
        # National Certificate - 2-year vocational qualification from technical institute
        nat_cert_info = education_info.get("nationalCertificate", {})
        if not nat_cert_info.get("institution"):
            raise ValidationError("National Certificate institution is required (e.g., technical institute name)")
        if not nat_cert_info.get("field"):
            raise ValidationError("National Certificate field is required (e.g., 'Automotive Engineering')")
        # National Certificate holders can only enter Certificate or Diploma programs (NOT Bachelor's directly)
        if first_program.level in ("degree", "masters", "phd"):
            raise ValidationError("National Certificate holders can only enter Certificate or Diploma programs. To enter Bachelor's, you must first complete a Diploma program.")
        elif first_program.level == "diploma":
            # National Certificate → Diploma is valid progression
            pass
        elif first_program.level == "certificate":
            # National Certificate → Certificate program is also valid
            pass

    elif qualification_type == "diploma":
        # Diploma - university/college qualification
        diploma_info = education_info.get("diploma", {})
        if not diploma_info.get("institution"):
            raise ValidationError("Diploma institution is required (e.g., university or college name)")
        if not diploma_info.get("program"):
            raise ValidationError("Diploma program name is required")

    # Generate application number
    app_number = generate_application_number()
    while AdmissionApplication.query.filter_by(application_number=app_number).first():
        app_number = generate_application_number()

    # Parse date of birth
    try:
        dob = date.fromisoformat(personal_info.get("dateOfBirth")) if personal_info.get("dateOfBirth") else None
    except (ValueError, TypeError):
        dob = None

    # Build UNEB grades structure if applicable
    uneb_grades = {}
    if qualification_type == "uace":
        uace_data = education_info.get("uace", {})
        uce_data = education_info.get("uce", {})
        uneb_grades = {
            "olevel": uce_data.get("subjects", []),
            "alevel": uace_data.get("subjects", [])
        }
    elif qualification_type == "uce":
        # UCE-only applicants
        uce_data = education_info.get("uce", {})
        uneb_grades = {
            "olevel": uce_data.get("subjects", []),
            "alevel": []
        }

    # Create application
    application = AdmissionApplication(
        application_number=app_number,
        user_id=user.id,
        program_id=first_program.id,
        program_choices=program_choices,
        exam_level=qualification_type,
        exam_year=education_info.get("examYear", datetime.now().year),
        index_number=education_info.get("indexNumber", ""),
        uneb_grades=uneb_grades,
        personal_statement=personal_info.get("personalStatement", "")[:2000],
        date_of_birth=dob,
        gender=personal_info.get("gender", ""),
        nationality=sanitize_input(personal_info.get("nationality", "Ugandan")),
        district=sanitize_input(contact_info.get("district", "")),
        session_of_study=contact_info.get("sessionOfStudy"),
        
        # HEC tracking
        hec_track=education_info.get("hecTrack") if qualification_type == "hec" else None,
        hec_institution=education_info.get("hecInstitution") if qualification_type == "hec" else None,
        hec_completion_year=education_info.get("hecCompletionYear") if qualification_type == "hec" else None,
        hec_gpa=education_info.get("hecGpa") if qualification_type == "hec" else None,
        
        # National Certificate tracking (vocational qualification from technical institute)
        national_certificate_institution=education_info.get("nationalCertificate", {}).get("institution") if qualification_type == "national_certificate" else None,
        national_certificate_field=education_info.get("nationalCertificate", {}).get("field") if qualification_type == "national_certificate" else None,
        national_certificate_completion_year=education_info.get("nationalCertificate", {}).get("completionYear") if qualification_type == "national_certificate" else None,
        
        # Diploma tracking (university/college qualification)
        diploma_institution=education_info.get("diploma", {}).get("institution") if qualification_type == "diploma" else None,
        diploma_program=education_info.get("diploma", {}).get("program") if qualification_type == "diploma" else None,
        diploma_completion_year=education_info.get("diploma", {}).get("completionYear") if qualification_type == "diploma" else None,
        diploma_class=education_info.get("diploma", {}).get("class") if qualification_type == "diploma" else None,
        
        # Previous degree tracking (for postgraduate)
        previous_degree_type="bachelors" if qualification_type == "bachelors" else ("masters" if qualification_type == "masters" else None),
        previous_degree_institution=education_info.get("previousDegree", {}).get("institution") if qualification_type in ("bachelors", "masters") else None,
        previous_degree_program=education_info.get("previousDegree", {}).get("program") if qualification_type in ("bachelors", "masters") else None,
        previous_degree_year=education_info.get("previousDegree", {}).get("year") if qualification_type in ("bachelors", "masters") else None,
        previous_degree_gpa=education_info.get("previousDegree", {}).get("gpa") if qualification_type in ("bachelors", "masters") else None,
        
        # Next of kin
        next_of_kin_name=sanitize_input(contact_info.get("nextOfKinName", "")),
        next_of_kin_phone=sanitize_input(contact_info.get("nextOfKinPhone", "")),
        next_of_kin_relationship=sanitize_input(contact_info.get("nextOfKinRelationship", "")),
        
        status="pending"
    )

    try:
        db.session.add(application)
        db.session.commit()
        
        # Log application creation
        log_application_action(
            action="created_via_wizard",
            application_id=application.id,
            user_id=user.id,
            details={
                "program_ids": program_choices,
                "qualification_type": qualification_type,
                "application_number": app_number
            }
        )
        
        return created(application.to_dict(), message="Application submitted successfully")
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Failed to create wizard application: {str(e)}", exc_info=True)
        raise ValidationError(f"Failed to save application: {str(e)}")


@admission_bp.route("/applications/wizard/save-draft", methods=["POST"])
@handle_kiu_error
def save_application_draft():
    """
    Save draft application data (for auto-save feature)
    Does not validate completeness - just stores current progress
    """
    user, error = get_current_user()
    if error:
        raise ValidationError(error)
    if user.role not in ("applicant",):
        raise ValidationError("Only applicants can save drafts")

    data = request.get_json()
    if not data:
        raise ValidationError("Request body is required")

    # Store draft in cache/session (simplified - in production use Redis/sessions)
    draft_key = f"application_draft:{user.id}"
    cache_manager.set(draft_key, data, ttl=3600 * 24 * 7)  # 7 days
    
    return success_response({"savedAt": datetime.utcnow().isoformat()}, message="Draft saved")


@admission_bp.route("/applications/wizard/draft", methods=["GET"])
@handle_kiu_error
def get_application_draft():
    """Retrieve saved draft application data"""
    user, error = get_current_user()
    if error:
        raise ValidationError(error)

    draft_key = f"application_draft:{user.id}"
    draft = cache_manager.get(draft_key)
    
    if not draft:
        return success_response({"draft": None})
    
    return success_response({
        "draft": draft,
        "retrievedAt": datetime.utcnow().isoformat()
    })


# Payment system removed - application fees not required per original proposal
