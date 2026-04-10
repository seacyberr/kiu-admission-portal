import os
import uuid
import re
from flask import Blueprint, request, jsonify, current_app
from datetime import datetime, date
import random
import string
from functools import wraps
from werkzeug.utils import secure_filename
from models import db, AdmissionApplication, Program, User
from routes.auth import get_current_user
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

    BUG FIX 1 (caching): The old implementation applied a @cached decorator
    that stored the entire JSON response including nationality-specific fees.
    The first caller's nationality was baked into the cached response and
    returned to every subsequent user — meaning international students saw
    local fees or vice-versa.  Caching is now done at the queryset level
    (programs list) and fee display is computed per-request from the user's
    stored nationality without being cached.

    BUG FIX 2 (ordering): Program.level.desc() ordered alphabetically
    descending, giving hec > diploma > degree — the opposite of what was
    intended.  Now uses an explicit integer sort key via CASE expression
    so "degree" always sorts first.
    """
    from sqlalchemy import case

    level = request.args.get("level")
    campus = request.args.get("campus")

    # Resolve nationality for fee display (not cached — varies per user)
    nationality = None
    user, _ = get_current_user()
    if user:
        app = (
            AdmissionApplication.query
            .filter_by(user_id=user.id)
            .order_by(AdmissionApplication.submitted_at.desc())
            .first()
        )
        if app:
            nationality = app.nationality

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

    return jsonify({"programs": [p.to_dict(nationality=nationality) for p in programs]}), 200


@admission_bp.route("/programs/<int:program_id>", methods=["GET"])
def get_program(program_id):
    program = db.session.get(Program, program_id)
    if not program:
        return jsonify({"error": "Not found", "message": "Program not found"}), 404
    return jsonify(program.to_dict()), 200


# ---------------------------------------------------------------------------
# Applications
# ---------------------------------------------------------------------------

@admission_bp.route("/applications", methods=["POST"])
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

    exam_level = data["examLevel"]
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
                f"requirement for {program.code} (aggregate ≤ {program.min_olevel_points})."
            )
    if exam_level == "a_level" and program.min_alevel_points is not None:
        if (alevel_points or 0) < program.min_alevel_points:
            raise ValidationError(
                f"Your A-Level points ({alevel_points or 0}) do not meet the minimum "
                f"requirement for {program.code} ({program.min_alevel_points}+ points)."
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
        db.session.add(application)
        db.session.commit()
        
        # Log successful application creation
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
        
        return jsonify(application.to_dict()), 201
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Failed to create application: {str(e)}", exc_info=True)
        raise ValidationError(f"Failed to save application: {str(e)}")


@admission_bp.route("/applications/<int:app_id>/certificate", methods=["POST"])
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
    if cert_type not in ("olevel", "alevel", "diploma", "hec"):
        raise ValidationError("type must be 'olevel', 'alevel', 'diploma', or 'hec'", "type", cert_type)

    if "file" not in request.files:
        raise ValidationError("No file provided")

    file = request.files["file"]
    if not file or file.filename == "":
        raise ValidationError("Empty file")
    if not allowed_file(file.filename):
        raise ValidationError("Only PDF, JPG, JPEG, PNG allowed")

    try:
        ext = file.filename.rsplit(".", 1)[1].lower()
        unique_name = f"{app_id}_{cert_type}_{uuid.uuid4().hex[:8]}.{ext}"
        cert_dir = os.path.join(current_app.config["UPLOAD_FOLDER"], "certificates")
        os.makedirs(cert_dir, exist_ok=True)
        save_path = os.path.join(cert_dir, secure_filename(unique_name))
        file.save(save_path)

        url_path = f"/api/uploads/certificates/{secure_filename(unique_name)}"
        setattr(application, f"{cert_type}_certificate_path", url_path)
        db.session.commit()
        
        # Log successful certificate upload
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
        
        return jsonify({
            "message": f"{cert_type.upper()} certificate uploaded successfully",
            "path": url_path,
            "application": application.to_dict(),
        }), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Failed to upload certificate: {str(e)}", exc_info=True)
        raise ValidationError(f"Failed to upload certificate: {str(e)}")


@admission_bp.route("/applications/mine", methods=["GET"])
@handle_kiu_error
def get_my_application():
    user, error = get_current_user()
    if error:
        raise ValidationError(error)
    application = AdmissionApplication.query.filter_by(user_id=user.id).first()
    return jsonify({"application": application.to_dict() if application else None}), 200


@admission_bp.route("/applications/<int:app_id>", methods=["GET"])
@handle_kiu_error
def get_application(app_id):
    user, error = get_current_user()
    if error:
        raise ValidationError(error)
    application = db.session.get(AdmissionApplication, app_id)
    if not application:
        raise NotFoundError("Application not found")
    if application.user_id != user.id and user.role != "admin":
        raise ValidationError("Access denied")
    return jsonify(application.to_dict()), 200


@admission_bp.route("/applications", methods=["GET"])
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

    query = AdmissionApplication.query.join(User)
    if status_filter:
        query = query.filter(AdmissionApplication.status == status_filter)
    if search:
        query = query.filter(
            (User.first_name.ilike(f"%{search}%")) |
            (User.last_name.ilike(f"%{search}%")) |
            (User.email.ilike(f"%{search}%")) |
            (AdmissionApplication.application_number.ilike(f"%{search}%"))
        )

    paginated = query.order_by(AdmissionApplication.submitted_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    return jsonify({
        "applications": [a.to_dict() for a in paginated.items],
        "total": paginated.total,
        "page": page,
        "perPage": per_page,
        "pages": paginated.pages,
    }), 200


@admission_bp.route("/applications/<int:app_id>/status", methods=["PATCH"])
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
        
        return jsonify(application.to_dict()), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Failed to update application status: {str(e)}", exc_info=True)
        raise ValidationError(f"Failed to update application: {str(e)}")


@admission_bp.route("/recommend", methods=["POST"])
@handle_kiu_error
@validate_json_payload(required_fields=["alevelSubjects"])
def recommend_programs():
    """
    DEPRECATED: Use /api/v1/nche/assess instead for unified recommendations.
    This endpoint is kept for backward compatibility but will be removed.

    Recommend programs based on A-Level subject combination with NCHE compliance.
    """
    log.warning("Using deprecated /admission/recommend endpoint. Migrate to /v1/nche/assess")
    user, error = get_current_user()
    if error:
        raise ValidationError(error)

    data = request.get_json()
    alevel_subjects = data.get("alevelSubjects", [])
    campus_filter = data.get("campus")

    if not alevel_subjects:
        raise ValidationError("alevelSubjects is required")

    principal_subjects = []
    subsidiary_subjects = []
    has_general_paper = False
    gp_grade = None

    for subj in alevel_subjects:
        subject_name = subj.get("subject", "").lower()
        subject_type = subj.get("subjectType", "").lower()
        grade = subj.get("grade", "").upper()
        if subject_type == "principal":
            principal_subjects.append({"name": subject_name, "grade": grade})
        elif subject_type == "subsidiary":
            subsidiary_subjects.append({"name": subject_name, "grade": grade})
            if subject_name in ["general paper", "gp"]:
                has_general_paper = True
                gp_grade = grade

    nche_warnings = []
    nche_errors = []

    if len(principal_subjects) < 2:
        nche_errors.append("NCHE requires at least 2 principal subjects at A-Level")

    if not has_general_paper:
        nche_warnings.append("General Paper (GP) is recommended for most university programs")
    elif gp_grade and gp_grade in ["F", "O"]:
        nche_warnings.append(f"GP grade ({gp_grade}) may affect eligibility for some programs")

    total_principal_points = sum(ALEVEL_GRADE_POINTS.get(p["grade"], 0) for p in principal_subjects)

    # Run NCHE Qualification Check first
    olevel_grades = data.get("olevelGrades", [])
    alevel_grades = alevel_subjects
    
    qualification_result = UgandaQualificationChecker.get_recommended_pathways(olevel_grades, alevel_grades)
    
    # Add qualification check results
    if not qualification_result['olevel']['eligible']:
        nche_errors.extend(qualification_result['olevel']['requirementsMissing'])
    
    if qualification_result['alevel'] and not qualification_result['alevel']['eligible']:
        nche_errors.extend(qualification_result['alevel']['requirementsMissing'])
    
    eligible_pathways = qualification_result.get('recommendedPathways', [])
    
    if total_principal_points < 6:
        nche_errors.append(f"Total principal points ({total_principal_points}) below NCHE minimum (6 points)")

    SUBJECT_PROGRAM_MAP = {
        "mathematics": ["BCS", "BIT", "BSE", "BCE", "BEE", "BME", "BCmpE", "BTE", "BSc-MATH", "BSc-STAT",
                        "BSc-PHYS", "BSc-CHEM", "BSc-IC", "BEAS", "BBA-FA", "BBA-FB", "BBA-IB", "BBA-MKT",
                        "BBA", "BHRM", "BSPM", "BTHM", "BESBM", "BCOM-DL", "BHRM-DL", "BSPM-DL"],
        "physics": ["BCS", "BIT", "BSE", "BCE", "BEE", "BME", "BCmpE", "BTE", "BSc-PHYS", "BSc-CHEM",
                    "BSc-IC", "BSc-MRIT"],
        "chemistry": ["BSc-CHEM", "BSc-IC", "BSc-BIOCHEM", "BSc-PHARM", "BSc-MICRO", "BSc-ANAT",
                      "BSc-PHYSIO", "MBChB", "BPharm", "BDS-DENT", "BNS-DIRECT", "BCMCH-DIRECT", "BMLS-DIRECT"],
        "biology": ["BSc-BIOCHEM", "BSc-PHARM", "BSc-MICRO", "BSc-ANAT", "BSc-PHYSIO", "BSc-WMCM",
                    "MBChB", "BPharm", "BDS-DENT", "BNS-DIRECT", "BCMCH-DIRECT", "BMLS-DIRECT", "BPH",
                    "BSc-MRIT", "BAME", "BAE", "BAERI"],
        "economics": ["BAEC", "BBA-FA", "BBA-FB", "BBA-IB", "BBA-MKT", "BBA", "BEAS", "BESBM", "BTHM",
                      "BCOM-DL"],
        "history": ["BAIRDS", "BAPA", "BGC", "BSCD", "BAED", "LLB-DAY", "LLB-WE", "BPA", "BLIS", "BPA-DL"],
        "geography": ["BSCD", "BDS", "BDS-DL", "BSc-ENVM", "BAME", "BAE", "BAERI", "BTHM"],
        "literature in english": ["BAIRDS", "BAMC", "BAPA", "BGC", "BAED", "LLB-DAY", "LLB-WE", "BPA",
                                   "BLIS", "BPA-DL"],
        "entrepreneurship": ["BESBM", "BTHM", "BAME"],
        "religious education": ["BAIRDS", "BAPA", "BGC", "BAED", "BPA"],
        "christian religious education (cre)": ["BAIRDS", "BAPA", "BGC", "BAED", "BPA"],
        "islamic religious education (ire)": ["BAIRDS", "BAPA", "BGC", "BAED", "BPA"],
    }

    program_scores: dict = {}
    principal_names = [p["name"] for p in principal_subjects]

    for subject in principal_names:
        for code in SUBJECT_PROGRAM_MAP.get(subject, []):
            program_scores[code] = program_scores.get(code, 0) + 1

    if has_general_paper and gp_grade and gp_grade not in ["F", "O"]:
        program_scores = {k: v + 0.5 for k, v in program_scores.items()}

    query = Program.query.filter(Program.level == "degree")
    if campus_filter:
        query = query.filter_by(campus=campus_filter)

    programs = query.all()
    recommendations = []
    
    # Get actual qualification status
    qualification_result = UgandaQualificationChecker.get_recommended_pathways(olevel_grades, alevel_grades)
    
    # Determine which program levels are allowed based on qualification
    allowed_levels = []
    eligible_programs = qualification_result.get('recommendedPathways', [])
    
    if 'bachelor_direct' in eligible_programs:
        allowed_levels.append('degree')
    if 'diploma' in eligible_programs:
        allowed_levels.append('diploma')
    if 'hec' in eligible_programs:
        allowed_levels.append('hec')

    for prog in programs:
        score = program_scores.get(prog.code, 0)
        
        # ONLY recommend programs that the student ACTUALLY QUALIFIES FOR
        if score > 0 and prog.level in allowed_levels and qualification_result['olevel']['eligible']:
            match_percentage = min(100, int((score / max(len(principal_subjects), 1)) * 100))
            program_nche_status = "compliant"
            program_warnings = list(nche_warnings)

            if prog.code in ["MBChB", "BDS-DENT", "BPharm", "BNS-DIRECT"] and total_principal_points < 12:
                program_nche_status = "conditional"
                program_warnings.append("Medical programs typically require 12+ principal points")
            if prog.code in ["LLB-DAY", "LLB-WE"] and not has_general_paper:
                program_nche_status = "conditional"
                program_warnings.append("Law programs strongly require General Paper")

            recommendations.append({
                **prog.to_dict(),
                "matchScore": score,
                "matchPercentage": match_percentage,
                "matchedSubjects": [
                    s["name"] for s in principal_subjects
                    if prog.code in SUBJECT_PROGRAM_MAP.get(s["name"], [])
                ],
                "ncheStatus": program_nche_status,
                "programWarnings": program_warnings,
            })

    recommendations.sort(key=lambda x: x["matchScore"], reverse=True)

    return jsonify({
        "recommendations": recommendations,
        "total": len(recommendations),
        "qualificationCheck": qualification_result,
        "allowedProgramLevels": allowed_levels,
        "totalProgramsScanned": len(programs),
        "programsExcludedByQualification": len(programs) - len(recommendations),
        "subjectsAnalyzed": principal_names,
        "ncheCompliance": {
            "hasGeneralPaper": has_general_paper,
            "gpGrade": gp_grade,
            "totalPrincipalPoints": total_principal_points,
            "errors": nche_errors,
            "warnings": nche_warnings,
        },
    }), 200


@admission_bp.route("/check-qualifications", methods=["POST"])
def check_qualifications():
    """
    Check qualifications against official NCHE/UHEQF standards
    Returns eligibility status, met requirements, missing requirements and recommended pathways
    """
    data = request.get_json()
    if not data:
        return jsonify({"error": "Bad request", "message": "No JSON body"}), 400
    
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
    
    return jsonify(result), 200


@admission_bp.route("/analytics", methods=["GET"])
def get_analytics():
    """Admin analytics with dropout prediction and program demand trends."""
    user, error = get_current_user()
    if error:
        return jsonify({"error": "Unauthorized", "message": error}), 401
    if user.role != "admin":
        return jsonify({"error": "Forbidden"}), 403

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
        if not has_gp and program.code in ["LLB-DAY", "LLB-WE", "BAIRDS", "BAPA"]:
            risk_level = "high" if risk_level == "high" else "medium"
            risk_factors.append("Missing General Paper for program that requires it")

        if program.code in ["MBChB", "BDS-DENT", "BPharm", "LLB-DAY", "LLB-WE"] and total_points < 12:
            risk_level = "high" if risk_level == "high" else "medium"
            risk_factors.append(f"Competitive program ({program.code}) with low points")

        if risk_level != "low":
            dropout_risk_apps.append({
                "applicationId": app.id,
                "applicationNumber": app.application_number,
                "studentName": f"{app.user.first_name} {app.user.last_name}" if app.user else "Unknown",
                "program": program.name,
                "programCode": program.code,
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
        Program.code,
        Program.faculty,
        func.count(AdmissionApplication.id).label('application_count')
    ).join(AdmissionApplication).group_by(
        Program.id, Program.name, Program.code, Program.faculty
    ).order_by(func.count(AdmissionApplication.id).desc()).limit(10).all()

    nche_compliance = {"withGeneralPaper": 0, "withoutGeneralPaper": 0, "sufficientPoints": 0, "insufficientPoints": 0}
    fee_distribution = {"local": 0, "international": 0}
    ea_countries = ["ugandan", "uganda", "kenyan", "kenya", "tanzanian", "tanzania",
                    "rwandan", "rwanda", "burundian", "burundi", "south sudanese", "south sudan"]

    for app in applications:
        alevel_grades = app.uneb_grades.get("alevel", []) if app.uneb_grades else []
        has_gp = any(g.get("subject", "").lower() in ["general paper", "gp"] for g in alevel_grades)
        nche_compliance["withGeneralPaper" if has_gp else "withoutGeneralPaper"] += 1

        principal_grades = [g for g in alevel_grades if g.get("subjectType", "").lower() == "principal"]
        total_points = sum(ALEVEL_GRADE_POINTS.get(g.get("grade", "").upper(), 0) for g in principal_grades)
        nche_compliance["sufficientPoints" if total_points >= 6 else "insufficientPoints"] += 1

        nationality = (app.nationality or "Ugandan").lower()
        is_local = any(c in nationality for c in ea_countries)
        fee_distribution["local" if is_local else "international"] += 1

    gender_distribution = db.session.query(
        AdmissionApplication.gender, func.count(AdmissionApplication.id)
    ).group_by(AdmissionApplication.gender).all()

    session_distribution = db.session.query(
        AdmissionApplication.session_of_study, func.count(AdmissionApplication.id)
    ).group_by(AdmissionApplication.session_of_study).all()

    return jsonify({
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
                {"name": p.name, "code": p.code, "faculty": p.faculty, "applications": p.application_count}
                for p in top_programs
            ],
        },
        "ncheCompliance": nche_compliance,
        "demographics": {
            "feeDistribution": fee_distribution,
            "genderDistribution": {g: c for g, c in gender_distribution},
            "sessionDistribution": {s or "Not specified": c for s, c in session_distribution},
        },
        "generatedAt": datetime.utcnow().isoformat(),
    }), 200
