import os
import uuid
import re
from flask import Blueprint, request, jsonify, current_app
from datetime import datetime, date
import random
import string
from functools import wraps
from werkzeug.utils import secure_filename
from flask_caching import Cache
from models import db, AdmissionApplication, Program, User
from routes.auth import get_current_user


def sanitize_text(text):
    """Sanitize user-provided text to prevent XSS and injection attacks.
    
    - Strips leading/trailing whitespace
    - Removes potentially dangerous HTML/script tags
    - Limits length to prevent abuse
    """
    if not text or not isinstance(text, str):
        return text
    
    # Strip whitespace
    text = text.strip()
    
    # Remove HTML tags (basic XSS prevention)
    text = re.sub(r'<[^>]*>', '', text)
    
    # Remove potential script injections
    text = re.sub(r'javascript:', '', text, flags=re.IGNORECASE)
    text = re.sub(r'on\w+\s*=', '', text, flags=re.IGNORECASE)
    
    # Limit length
    max_length = 5000
    if len(text) > max_length:
        text = text[:max_length]
    
    return text

admission_bp = Blueprint("admission", __name__)

# Cache decorator for static data
def cached(timeout=300, key_prefix=""):
    """Cache decorator for functions returning JSON-serializable data.
    
    Uses Flask-Caching's memoize functionality for reliable caching.
    Falls back gracefully if caching is unavailable.
    """
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            try:
                # Use Flask-Caching's built-in memoize
                cache = current_app.extensions.get('cache')
                if cache is None:
                    return f(*args, **kwargs)
                
                # Build cache key from function name and arguments
                cache_key = f"{key_prefix}:{f.__name__}:{hash(str(args) + str(sorted(kwargs.items())))}"
                result = cache.get(cache_key)
                if result is not None:
                    return result
                
                result = f(*args, **kwargs)
                cache.set(cache_key, result, timeout=timeout)
                return result
            except Exception:
                # Fail open: if caching fails, just call the function
                return f(*args, **kwargs)
        return wrapper
    return decorator

ALLOWED_EXTENSIONS = {"pdf", "jpg", "jpeg", "png"}

# ── UNEB Grading System ──────────────────────────────────────────────────────
# O-Level (UCE): D1 (best) → D9 (worst). Pass: D1-D6 (points: 1-6)
# A-Level (UACE): A (6 pts), B (5), C (4), D (3), E (2), O (1), F (0, fail)

VALID_OLEVEL_GRADES = ["D1", "D2", "D3", "D4", "D5", "D6", "D7", "D8", "F", "C3", "C4", "C5", "C6", "P7", "P8", "F9"]
VALID_ALEVEL_GRADES = ["A", "B", "C", "D", "E", "O", "F"]
VALID_MASTERS_QUALIFICATIONS = ["distinction", "merit", "pass", "first_class", "second_class_upper", "second_class_lower", "third_class"]
VALID_PHD_QUALIFICATIONS = ["distinction", "merit", "pass", "first_class", "second_class_upper", "second_class_lower", "third_class"]

# O-Level grade to points (lower is better for admission)
OLEVEL_GRADE_POINTS = {"D1": 1, "D2": 2, "C3": 3, "C4": 4, "C5": 5, "C6": 6, "P7": 7, "P8": 8, "F9": 9}
# A-Level grade to points (higher is better for admission)
ALEVEL_GRADE_POINTS = {"A": 6, "B": 5, "C": 4, "D": 3, "E": 2, "O": 1, "F": 0}


def calculate_olevel_points(olevel_grades):
    """Calculate total O-Level points (sum of all subject points)."""
    total = 0
    for grade_entry in olevel_grades:
        grade = grade_entry.get("grade", "").upper()
        if grade in OLEVEL_GRADE_POINTS:
            total += OLEVEL_GRADE_POINTS[grade]
    return total


def calculate_alevel_points(alevel_grades):
    """Calculate total A-Level points (sum of principal subject points only)."""
    total = 0
    for grade_entry in alevel_grades:
        grade = grade_entry.get("grade", "").upper()
        subject_type = grade_entry.get("subjectType", "").lower()
        if grade in ALEVEL_GRADE_POINTS and subject_type == "principal":
            total += ALEVEL_GRADE_POINTS[grade]
    return total


def validate_uneb_grades(uneb_grades, exam_level):
    """Validate UNEB grades are valid and meet minimum requirements."""
    errors = []

    # Validate O-Level grades
    olevel_grades = uneb_grades.get("olevel", [])
    for grade_entry in olevel_grades:
        grade = grade_entry.get("grade", "").upper()
        subject = grade_entry.get("subject", "")
        if grade not in VALID_OLEVEL_GRADES:
            errors.append(f"Invalid O-Level grade '{grade}' for {subject}. Valid grades: {', '.join(VALID_OLEVEL_GRADES)}")
        if not subject:
            errors.append("Each O-Level grade entry must have a 'subject' field")

    # Validate A-Level grades
    alevel_grades = uneb_grades.get("alevel", [])
    for grade_entry in alevel_grades:
        grade = grade_entry.get("grade", "").upper()
        subject = grade_entry.get("subject", "")
        subject_type = grade_entry.get("subjectType", "").lower()
        if grade not in VALID_ALEVEL_GRADES:
            errors.append(f"Invalid A-Level grade '{grade}' for {subject}. Valid grades: {', '.join(VALID_ALEVEL_GRADES)}")
        if subject_type not in ("principal", "subsidiary"):
            errors.append(f"A-Level subject type for {subject} must be 'principal' or 'subsidiary'")
        if not subject:
            errors.append("Each A-Level grade entry must have a 'subject' field")

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
@cached(timeout=300, key_prefix="programs")
def list_programs():
    """
    List all academic programs.
    
    Returns all available programs with optional filtering by level and campus.
    Results are cached for 5 minutes.
    
    Query Parameters:
        level (str, optional): Filter by program level - "degree", "diploma", "hec", "masters", or "phd"
        campus (str, optional): Filter by campus - "kampala" or "western"
    
    Returns:
        200: List of programs
    
    Example:
        GET /api/admission/programs
        GET /api/admission/programs?level=degree&campus=kampala
    """
    level = request.args.get("level")
    campus = request.args.get("campus")
    
    # Get nationality from authenticated user for fee display
    nationality = None
    user, _ = get_current_user()
    if user:
        # Try to get nationality from user's most recent application
        app = AdmissionApplication.query.filter_by(user_id=user.id).order_by(AdmissionApplication.submitted_at.desc()).first()
        if app:
            nationality = app.nationality
    
    query = Program.query
    
    # Apply filters if provided
    if level:
        query = query.filter_by(level=level)
    if campus:
        query = query.filter_by(campus=campus)
    
    # Sort by level (degree first, then diploma, then hec), 
    # then campus (kampala first, then western),
    # then faculty, then program name
    programs = query.order_by(
        Program.level.desc(),  # degree > diploma > hec (alphabetically)
        Program.campus,        # kampala < western (alphabetically)
        Program.faculty,
        Program.name
    ).all()
    
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
def create_application():
    """
    Submit a new admission application.
    
    Creates a new admission application for the authenticated user. Each user can only
    submit one application. Supports up to 3 program choices.
    
    Request Body:
        programIds (list[int]): List of program IDs (1-3 choices, first is primary)
        examLevel (str): "o_level", "a_level", "diploma", "hec", "masters", or "phd"
        examYear (int): Year exams were taken
        indexNumber (str): UNEB index number
        unebGrades (dict): O-Level and/or A-Level grades
        dateOfBirth (str): Date in YYYY-MM-DD format
        gender (str): "male" or "female"
        nationality (str, optional): Default "Ugandan"
        district (str, optional): Home district
        personalStatement (str, optional): Personal statement
    
    Returns:
        201: Application created successfully
        400: Validation error
        409: User already has an application
        422: Does not meet program requirements
    
    Example:
        POST /api/admission/applications
        {
            "programIds": [1, 2, 3],
            "examLevel": "a_level",
            "examYear": 2023,
            "indexNumber": "U0001/001",
            "unebGrades": {
                "olevel": [{"subject": "Math", "grade": "D1", "points": 1}],
                "alevel": [{"subject": "Math", "grade": "A", "points": 6, "subjectType": "principal"}]
            },
            "dateOfBirth": "2000-01-15",
            "gender": "male"
        }
    """
    user, error = get_current_user()
    if error:
        return jsonify({"error": "Unauthorized", "message": error}), 401

    if user.role not in ("applicant",):
        return jsonify({"error": "Forbidden", "message": "Only applicants can submit admission applications"}), 403

    data = request.get_json()
    if not data:
        return jsonify({"error": "Bad request", "message": "No JSON body"}), 400

    required = ["programIds", "examLevel", "examYear", "indexNumber", "unebGrades", "dateOfBirth", "gender"]
    for field in required:
        if field not in data:
            return jsonify({"error": "Validation error", "message": f"{field} is required"}), 400

    # Validate program selection (up to 3 choices)
    program_ids = data.get("programIds", [])
    if not isinstance(program_ids, list) or len(program_ids) == 0:
        return jsonify({"error": "Validation error", "message": "At least one program must be selected"}), 400
    if len(program_ids) > 3:
        return jsonify({"error": "Validation error", "message": "Maximum 3 program choices allowed"}), 400

    # Validate all selected programs exist
    programs = []
    for pid in program_ids:
        program = db.session.get(Program, pid)
        if not program:
            return jsonify({"error": "Not found", "message": f"Program ID {pid} not found"}), 404
        programs.append(program)

    # Use first choice as primary program
    program = programs[0]

    existing = AdmissionApplication.query.filter_by(user_id=user.id).first()
    if existing:
        return jsonify({"error": "Conflict", "message": "You have already submitted an application"}), 409

    exam_level = data["examLevel"]
    valid_exam_levels = ("o_level", "a_level", "diploma", "hec", "masters", "phd")
    if exam_level not in valid_exam_levels:
        return jsonify({
            "error": "Validation error",
            "message": "examLevel must be one of: 'o_level', 'a_level', 'diploma', 'hec', 'masters', 'phd'"
        }), 400

    # Degree vs non-degree qualification gating (portal UI-only guidance + backend safety)
    if program.level == "degree":
        # Degree programs accept A-Level, Diploma, or HEC qualifications
        # O-Level alone is not sufficient for degree programs
        if exam_level == "o_level":
            return jsonify({
                "error": "Validation error",
                "message": "Degree programs require A-Level, Diploma, or HEC qualifications. O-Level alone is not accepted."
            }), 422
    elif program.level == "masters":
        # Masters programs require a bachelor's degree qualification
        if exam_level not in ("a_level", "diploma", "hec", "masters"):
            return jsonify({
                "error": "Validation error",
                "message": "Masters programs require a bachelor's degree qualification (A-Level, Diploma, HEC, or Masters level)."
            }), 422
    elif program.level == "phd":
        # PhD programs require a master's degree qualification
        if exam_level not in ("masters", "phd"):
            return jsonify({
                "error": "Validation error",
                "message": "PhD programs require a master's degree qualification."
            }), 422
    else:
        # Diploma/HEC programmes primarily accept O-Level, but can also accept other qualifications
        # This allows flexibility for students with different educational backgrounds
        pass  # Allow all exam levels for diploma/HEC programs

    try:
        dob = date.fromisoformat(data["dateOfBirth"])
    except (ValueError, TypeError):
        return jsonify({"error": "Validation error", "message": "Invalid dateOfBirth format (use YYYY-MM-DD)"}), 400

    uneb_grades = data.get("unebGrades", {})
    if not isinstance(uneb_grades, dict):
        return jsonify({"error": "Validation error", "message": "unebGrades must be an object with 'olevel' and/or 'alevel' arrays"}), 400

    # Validate UNEB grades format
    grade_errors = validate_uneb_grades(uneb_grades, exam_level)
    if grade_errors:
        return jsonify({"error": "Validation error", "message": "; ".join(grade_errors)}), 422

    # Validate minimum subjects
    olevel_grades = uneb_grades.get("olevel", [])
    alevel_grades = uneb_grades.get("alevel", [])

    if exam_level == "o_level" and len(olevel_grades) < 5:
        return jsonify({"error": "Validation error", "message": "O-Level (UCE) requires at least 5 subjects"}), 422

    if exam_level == "a_level":
        if len(olevel_grades) < 5:
            return jsonify({"error": "Validation error", "message": "Please provide your O-Level (UCE) results as well"}), 422
        principals = [s for s in alevel_grades if s.get("subjectType", "").lower() == "principal"]
        if len(principals) < 2:
            return jsonify({"error": "Validation error", "message": "A-Level (UACE) requires at least 2 principal subjects"}), 422

    # Calculate points for validation
    olevel_points = calculate_olevel_points(olevel_grades)
    alevel_points = calculate_alevel_points(alevel_grades) if exam_level == "a_level" else None

    # Program entry threshold checks
    # Only enforce numeric thresholds when O-Level / A-Level is actually provided.
    if exam_level in ("o_level", "a_level") and program.min_olevel_points is not None and olevel_points > program.min_olevel_points:
        return jsonify({
            "error": "Validation error",
            "message": (
                f"Your O-Level aggregate ({olevel_points}) does not meet the minimum "
                f"requirement for {program.code} (aggregate <= {program.min_olevel_points})."
            ),
        }), 422
    if exam_level == "a_level" and program.min_alevel_points is not None:
        if (alevel_points or 0) < program.min_alevel_points:
            return jsonify({
                "error": "Validation error",
                "message": (
                    f"Your A-Level points ({alevel_points or 0}) do not meet the minimum "
                    f"requirement for {program.code} ({program.min_alevel_points}+ points)."
                ),
            }), 422

    app_number = generate_application_number()
    while AdmissionApplication.query.filter_by(application_number=app_number).first():
        app_number = generate_application_number()

    # Determine if local or international student
    nationality = data.get("nationality", "Ugandan")
    is_local = nationality.lower() in ("ugandan", "uganda", "east african", "kenyan", "kenya", "tanzanian", "tanzania", "rwandan", "rwanda", "burundian", "burundi", "south sudanese", "south sudan")

    application = AdmissionApplication(
        application_number=app_number,
        user_id=user.id,
        program_id=program.id,
        program_choices=program_ids,  # Store all 3 choices
        exam_level=exam_level,
        exam_year=int(data["examYear"]),
        index_number=sanitize_text(data["indexNumber"]),
        uneb_grades=uneb_grades,
        personal_statement=sanitize_text(data.get("personalStatement", "")),
        date_of_birth=dob,
        gender=data["gender"],
        nationality=sanitize_text(nationality),
        district=sanitize_text(data.get("district", "")),
        session_of_study=data.get("sessionOfStudy"),
        # Final-year student verification
        is_final_year=data.get("isFinalYear", False),
        expected_graduation_year=data.get("expectedGraduationYear"),
        current_year_of_study=data.get("currentYearOfStudy"),
        student_number=sanitize_text(data.get("studentNumber", "")),
        # Next of kin
        next_of_kin_name=sanitize_text(data.get("nextOfKinName", "")),
        next_of_kin_phone=sanitize_text(data.get("nextOfKinPhone", "")),
        next_of_kin_relationship=sanitize_text(data.get("nextOfKinRelationship", "")),
        status="pending",
    )
    db.session.add(application)
    db.session.commit()

    return jsonify(application.to_dict()), 201


@admission_bp.route("/applications/<int:app_id>/certificate", methods=["POST"])
def upload_certificate(app_id):
    """Upload academic certificate for an existing application."""
    user, error = get_current_user()
    if error:
        return jsonify({"error": "Unauthorized", "message": error}), 401

    application = db.session.get(AdmissionApplication, app_id)
    if not application:
        return jsonify({"error": "Not found", "message": "Application not found"}), 404

    if application.user_id != user.id and user.role != "admin":
        return jsonify({"error": "Forbidden", "message": "You can only upload certificates for your own application"}), 403

    cert_type = request.form.get("type", "olevel")  # 'olevel' | 'alevel' | 'diploma' | 'hec'
    if cert_type not in ("olevel", "alevel", "diploma", "hec"):
        return jsonify({"error": "Validation error", "message": "type must be 'olevel', 'alevel', 'diploma', or 'hec'"}), 400

    if "file" not in request.files:
        return jsonify({"error": "Bad request", "message": "No file provided (field name: 'file')"}), 400

    file = request.files["file"]
    if not file or file.filename == "":
        return jsonify({"error": "Bad request", "message": "Empty file"}), 400

    if not allowed_file(file.filename):
        return jsonify({"error": "Unsupported file type", "message": "Only PDF, JPG, JPEG, PNG files are allowed"}), 415

    # Generate unique filename
    ext = file.filename.rsplit(".", 1)[1].lower()
    unique_name = f"{app_id}_{cert_type}_{uuid.uuid4().hex[:8]}.{ext}"
    cert_dir = os.path.join(current_app.config["UPLOAD_FOLDER"], "certificates")
    os.makedirs(cert_dir, exist_ok=True)
    save_path = os.path.join(cert_dir, secure_filename(unique_name))
    file.save(save_path)

    url_path = f"/api/uploads/certificates/{secure_filename(unique_name)}"

    if cert_type == "olevel":
        application.olevel_certificate_path = url_path
    elif cert_type == "alevel":
        application.alevel_certificate_path = url_path
    elif cert_type == "diploma":
        application.diploma_certificate_path = url_path
    elif cert_type == "hec":
        application.hec_certificate_path = url_path

    db.session.commit()
    return jsonify({
        "message": f"{cert_type.upper()} certificate uploaded successfully",
        "path": url_path,
        "application": application.to_dict(),
    }), 200


@admission_bp.route("/applications/mine", methods=["GET"])
def get_my_application():
    user, error = get_current_user()
    if error:
        return jsonify({"error": "Unauthorized", "message": error}), 401
    application = AdmissionApplication.query.filter_by(user_id=user.id).first()
    if not application:
        return jsonify({"application": None}), 200
    return jsonify({"application": application.to_dict()}), 200


@admission_bp.route("/applications/<int:app_id>", methods=["GET"])
def get_application(app_id):
    user, error = get_current_user()
    if error:
        return jsonify({"error": "Unauthorized", "message": error}), 401
    application = db.session.get(AdmissionApplication, app_id)
    if not application:
        return jsonify({"error": "Not found", "message": "Application not found"}), 404
    if application.user_id != user.id and user.role != "admin":
        return jsonify({"error": "Forbidden"}), 403
    return jsonify(application.to_dict()), 200


@admission_bp.route("/applications", methods=["GET"])
def list_applications():
    user, error = get_current_user()
    if error:
        return jsonify({"error": "Unauthorized", "message": error}), 401
    if user.role != "admin":
        return jsonify({"error": "Forbidden"}), 403

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
def update_application_status(app_id):
    user, error = get_current_user()
    if error:
        return jsonify({"error": "Unauthorized", "message": error}), 401
    if user.role != "admin":
        return jsonify({"error": "Forbidden"}), 403

    application = db.session.get(AdmissionApplication, app_id)
    if not application:
        return jsonify({"error": "Not found", "message": "Application not found"}), 404

    data = request.get_json() or {}
    new_status = data.get("status")
    valid_statuses = ["pending", "under_review", "accepted", "rejected", "waitlisted"]
    if new_status not in valid_statuses:
        return jsonify({"error": "Validation error", "message": f"status must be one of: {', '.join(valid_statuses)}"}), 400

    application.status = new_status
    if "adminNotes" in data:
        application.admin_notes = data["adminNotes"]
    
    # Allow admin to update the assigned program
    if "programId" in data:
        new_program_id = data["programId"]
        # Verify the program exists
        program = db.session.get(Program, new_program_id)
        if not program:
            return jsonify({"error": "Not found", "message": "Program not found"}), 404
        
        # Verify the program is in the applicant's choices
        if application.program_choices and new_program_id not in application.program_choices:
            return jsonify({"error": "Validation error", "message": "Selected program must be one of the applicant's choices"}), 400
        
        application.program_id = new_program_id
    
    db.session.commit()

    return jsonify(application.to_dict()), 200


@admission_bp.route("/recommend", methods=["POST"])
def recommend_programs():
    """
    Recommend programs based on A-Level subject combination with NCHE compliance.
    
    Request Body:
        alevelSubjects (list): List of A-Level subjects with grades
            [{"subject": "Mathematics", "grade": "A", "subjectType": "principal"}, ...]
            Must include General Paper (GP) as subsidiary subject
        campus (str, optional): Filter by campus - "kampala" or "western"
    
    Returns:
        200: List of recommended programs with match score and NCHE compliance status
    """
    user, error = get_current_user()
    if error:
        return jsonify({"error": "Unauthorized", "message": error}), 401

    data = request.get_json()
    if not data:
        return jsonify({"error": "Bad request", "message": "No JSON body"}), 400

    alevel_subjects = data.get("alevelSubjects", [])
    campus_filter = data.get("campus")

    if not alevel_subjects:
        return jsonify({"error": "Validation error", "message": "alevelSubjects is required"}), 400

    # Extract principal and subsidiary subjects
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
            # Check for General Paper (GP)
            if subject_name in ["general paper", "gp"]:
                has_general_paper = True
                gp_grade = grade

    # NCHE Compliance Validation
    nche_warnings = []
    nche_errors = []
    
    # Rule 1: Must have at least 3 principal subjects
    if len(principal_subjects) < 3:
        nche_errors.append("NCHE requires at least 3 principal subjects at A-Level")
    
    # Rule 2: General Paper is strongly recommended
    if not has_general_paper:
        nche_warnings.append("General Paper (GP) is recommended for most university programs")
    elif gp_grade and gp_grade in ["F", "O"]:
        nche_warnings.append(f"GP grade ({gp_grade}) may affect eligibility for some programs")
    
    # Rule 3: Check for minimum points based on NCHE guidelines
    # A=6, B=5, C=4, D=3, E=2, O=1, F=0
    ALEVEL_GRADE_POINTS = {"A": 6, "B": 5, "C": 4, "D": 3, "E": 2, "O": 1, "F": 0}
    total_principal_points = sum(ALEVEL_GRADE_POINTS.get(p["grade"], 0) for p in principal_subjects)
    
    if total_principal_points < 6:  # Minimum 3 principals with at least E each (3 × 2 = 6 points)
        nche_errors.append(f"Total principal points ({total_principal_points}) below NCHE minimum (6 points)")

    # Define subject-to-program mapping based on Ugandan university requirements
    SUBJECT_PROGRAM_MAP = {
        "mathematics": ["BCS", "BIT", "BSE", "BCE", "BEE", "BME", "BCmpE", "BTE", "BSc-MATH", "BSc-STAT", "BSc-PHYS", "BSc-CHEM", "BSc-IC", "BEAS", "BBA-FA", "BBA-FB", "BBA-IB", "BBA-MKT", "BBA", "BHRM", "BSPM", "BTHM", "BESBM", "BCOM-DL", "BHRM-DL", "BSPM-DL"],
        "physics": ["BCS", "BIT", "BSE", "BCE", "BEE", "BME", "BCmpE", "BTE", "BSc-PHYS", "BSc-CHEM", "BSc-IC", "BSc-MRIT"],
        "chemistry": ["BSc-CHEM", "BSc-IC", "BSc-BIOCHEM", "BSc-PHARM", "BSc-MICRO", "BSc-ANAT", "BSc-PHYSIO", "MBChB", "BPharm", "BDS-DENT", "BNS-DIRECT", "BCMCH-DIRECT", "BMLS-DIRECT"],
        "biology": ["BSc-BIOCHEM", "BSc-PHARM", "BSc-MICRO", "BSc-ANAT", "BSc-PHYSIO", "BSc-WMCM", "MBChB", "BPharm", "BDS-DENT", "BNS-DIRECT", "BCMCH-DIRECT", "BMLS-DIRECT", "BPH", "BSc-PHYSIO", "BSc-MRIT", "BAME", "BAE", "BAERI"],
        "economics": ["BAEC", "BBA-FA", "BBA-FB", "BBA-IB", "BBA-MKT", "BBA", "BEAS", "BESBM", "BTHM", "BCOM-DL"],
        "history": ["BAIRDS", "BAPA", "BGC", "BSCD", "BAED", "LLB-DAY", "LLB-WE", "BPA", "BLIS", "BPA-DL"],
        "geography": ["BSCD", "BDS", "BDS-DL", "BSc-ENVM", "BAME", "BAE", "BAERI", "BTHM"],
        "literature": ["BAIRDS", "BAMC", "BAPA", "BGC", "BAED", "LLB-DAY", "LLB-WE", "BPA", "BLIS", "BPA-DL"],
        "entrepreneurship": ["BESBM", "BTHM", "BAME"],
        "religious education": ["BAIRDS", "BAPA", "BGC", "BAED", "BPA"],
        "general paper": [],  # GP doesn't directly map to programs but affects eligibility
        "subsidiary mathematics": ["BCS", "BIT", "BSE", "BCE", "BEE", "BME", "BCmpE", "BTE"],
        "subsidiary physics": ["BCS", "BIT", "BSE", "BCE", "BEE", "BME", "BCmpE", "BTE"],
    }

    # Calculate match scores (only from principal subjects)
    program_scores = {}
    principal_names = [p["name"] for p in principal_subjects]
    
    for subject in principal_names:
        matching_codes = SUBJECT_PROGRAM_MAP.get(subject, [])
        for code in matching_codes:
            program_scores[code] = program_scores.get(code, 0) + 1
    
    # Bonus for having GP (affects many programs positively)
    if has_general_paper and gp_grade and gp_grade not in ["F", "O"]:
        for code in program_scores:
            program_scores[code] += 0.5  # Small bonus for having passed GP

    # Get programs from database
    query = Program.query.filter(Program.level == "degree")
    if campus_filter:
        query = query.filter_by(campus=campus_filter)

    programs = query.all()
    recommendations = []

    for program in programs:
        score = program_scores.get(program.code, 0)
        if score > 0:
            # Calculate match percentage
            match_percentage = min(100, int((score / max(len(principal_subjects), 1)) * 100))
            
            # Determine NCHE compliance for this specific program
            program_nche_status = "compliant"
            program_warnings = []
            
            # Some programs have stricter requirements
            if program.code in ["MBChB", "BDS-DENT", "BPharm", "BNS-DIRECT"]:
                # Medical programs require higher points
                if total_principal_points < 12:
                    program_nche_status = "conditional"
                    program_warnings.append("Medical programs typically require 12+ principal points")
            
            if program.code in ["LLB-DAY", "LLB-WE"]:
                # Law requires good GP
                if not has_general_paper:
                    program_nche_status = "conditional"
                    program_warnings.append("Law programs strongly require General Paper")
            
            recommendations.append({
                **program.to_dict(),
                "matchScore": score,
                "matchPercentage": match_percentage,
                "matchedSubjects": [s["name"] for s in principal_subjects if program.code in SUBJECT_PROGRAM_MAP.get(s["name"], [])],
                "ncheStatus": program_nche_status,
                "programWarnings": program_warnings
            })

    # Sort by match score (descending)
    recommendations.sort(key=lambda x: x["matchScore"], reverse=True)

    return jsonify({
        "recommendations": recommendations,
        "total": len(recommendations),
        "subjectsAnalyzed": principal_names,
        "ncheCompliance": {
            "hasGeneralPaper": has_general_paper,
            "gpGrade": gp_grade,
            "totalPrincipalPoints": total_principal_points,
            "errors": nche_errors,
            "warnings": nche_warnings
        }
    }), 200


@admission_bp.route("/analytics", methods=["GET"])
def get_analytics():
    """
    Get advanced admission analytics with dropout prediction and program demand trends.
    
    Returns comprehensive analytics including:
    - Application statistics by status and program
    - Dropout risk prediction based on program mismatch
    - Program demand trends over time
    - NCHE compliance statistics
    - Fee distribution (local vs international)
    """
    user, error = get_current_user()
    if error:
        return jsonify({"error": "Unauthorized", "message": error}), 401
    if user.role != "admin":
        return jsonify({"error": "Forbidden"}), 403

    from sqlalchemy import func, extract
    from datetime import datetime, timedelta
    
    # Basic statistics
    total = AdmissionApplication.query.count()
    by_status = db.session.query(
        AdmissionApplication.status, func.count(AdmissionApplication.id)
    ).group_by(AdmissionApplication.status).all()
    by_program = db.session.query(
        Program.name, func.count(AdmissionApplication.id)
    ).join(AdmissionApplication).group_by(Program.name).all()
    
    # Dropout risk prediction: Applications where student's points don't meet program minimum
    dropout_risk_apps = []
    applications = AdmissionApplication.query.all()
    
    for app in applications:
        program = Program.query.get(app.program_id)
        if not program:
            continue
            
        # Calculate student's points
        alevel_grades = app.uneb_grades.get("alevel", []) if app.uneb_grades else []
        principal_grades = [g for g in alevel_grades if g.get("subjectType", "").lower() == "principal"]
        
        ALEVEL_GRADE_POINTS = {"A": 6, "B": 5, "C": 4, "D": 3, "E": 2, "O": 1, "F": 0}
        total_points = sum(ALEVEL_GRADE_POINTS.get(g.get("grade", "").upper(), 0) for g in principal_grades)
        
        # Check if student meets minimum requirements
        risk_level = "low"
        risk_factors = []
        
        if program.min_alevel_points and total_points < program.min_alevel_points:
            risk_level = "high"
            risk_factors.append(f"A-Level points ({total_points}) below minimum ({program.min_alevel_points})")
        
        # Check for missing GP
        has_gp = any(g.get("subject", "").lower() in ["general paper", "gp"] for g in alevel_grades)
        if not has_gp and program.code in ["LLB-DAY", "LLB-WE", "BAIRDS", "BAPA"]:
            risk_level = "high" if risk_level == "high" else "medium"
            risk_factors.append("Missing General Paper for program that requires it")
        
        # Check program mismatch (student applied for competitive program with low points)
        competitive_programs = ["MBChB", "BDS-DENT", "BPharm", "LLB-DAY", "LLB-WE"]
        if program.code in competitive_programs and total_points < 12:
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
                "status": app.status
            })
    
    # Program demand trends (by month for current year)
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
            "applications": count
        })
    
    # Top programs by demand
    top_programs = db.session.query(
        Program.name,
        Program.code,
        Program.faculty,
        func.count(AdmissionApplication.id).label('application_count')
    ).join(AdmissionApplication).group_by(
        Program.id, Program.name, Program.code, Program.faculty
    ).order_by(
        func.count(AdmissionApplication.id).desc()
    ).limit(10).all()
    
    # NCHE compliance statistics
    nche_compliance = {
        "withGeneralPaper": 0,
        "withoutGeneralPaper": 0,
        "sufficientPoints": 0,
        "insufficientPoints": 0
    }
    
    for app in applications:
        alevel_grades = app.uneb_grades.get("alevel", []) if app.uneb_grades else []
        has_gp = any(g.get("subject", "").lower() in ["general paper", "gp"] for g in alevel_grades)
        
        if has_gp:
            nche_compliance["withGeneralPaper"] += 1
        else:
            nche_compliance["withoutGeneralPaper"] += 1
        
        principal_grades = [g for g in alevel_grades if g.get("subjectType", "").lower() == "principal"]
        ALEVEL_GRADE_POINTS = {"A": 6, "B": 5, "C": 4, "D": 3, "E": 2, "O": 1, "F": 0}
        total_points = sum(ALEVEL_GRADE_POINTS.get(g.get("grade", "").upper(), 0) for g in principal_grades)
        
        if total_points >= 6:  # NCHE minimum
            nche_compliance["sufficientPoints"] += 1
        else:
            nche_compliance["insufficientPoints"] += 1
    
    # Fee distribution (local vs international)
    fee_distribution = {
        "local": 0,
        "international": 0
    }
    
    for app in applications:
        nationality = (app.nationality or "Ugandan").lower()
        ea_countries = ["ugandan", "uganda", "kenyan", "kenya", "tanzanian", "tanzania", 
                       "rwandan", "rwanda", "burundian", "burundi", "south sudanese", "south sudan"]
        if any(country in nationality for country in ea_countries):
            fee_distribution["local"] += 1
        else:
            fee_distribution["international"] += 1
    
    # Gender distribution
    gender_distribution = db.session.query(
        AdmissionApplication.gender,
        func.count(AdmissionApplication.id)
    ).group_by(AdmissionApplication.gender).all()
    
    # Session of study distribution
    session_distribution = db.session.query(
        AdmissionApplication.session_of_study,
        func.count(AdmissionApplication.id)
    ).group_by(AdmissionApplication.session_of_study).all()

    return jsonify({
        "summary": {
            "totalApplications": total,
            "byStatus": {s: c for s, c in by_status},
            "byProgram": [{"program": p, "count": c} for p, c in by_program]
        },
        "dropoutRisk": {
            "totalAtRisk": len(dropout_risk_apps),
            "highRisk": len([a for a in dropout_risk_apps if a["riskLevel"] == "high"]),
            "mediumRisk": len([a for a in dropout_risk_apps if a["riskLevel"] == "medium"]),
            "applications": dropout_risk_apps[:20]  # Return top 20 at-risk applications
        },
        "programDemand": {
            "monthlyTrends": monthly_trends,
            "topPrograms": [
                {
                    "name": p.name,
                    "code": p.code,
                    "faculty": p.faculty,
                    "applications": p.application_count
                } for p in top_programs
            ]
        },
        "ncheCompliance": nche_compliance,
        "demographics": {
            "feeDistribution": fee_distribution,
            "genderDistribution": {g: c for g, c in gender_distribution},
            "sessionDistribution": {s or "Not specified": c for s, c in session_distribution}
        },
        "generatedAt": datetime.utcnow().isoformat()
    }), 200
