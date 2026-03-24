import os
import uuid
from flask import Blueprint, request, jsonify, current_app
from datetime import datetime, date
import random
import string
from werkzeug.utils import secure_filename
from models import db, AdmissionApplication, Program, User
from routes.auth import get_current_user

admission_bp = Blueprint("admission", __name__)

ALLOWED_EXTENSIONS = {"pdf", "jpg", "jpeg", "png"}


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
    level = request.args.get("level")
    query = Program.query
    if level:
        query = query.filter_by(level=level)
    programs = query.order_by(Program.faculty, Program.name).all()
    return jsonify({"programs": [p.to_dict() for p in programs]}), 200


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
    user, error = get_current_user()
    if error:
        return jsonify({"error": "Unauthorized", "message": error}), 401

    if user.role not in ("applicant",):
        return jsonify({"error": "Forbidden", "message": "Only applicants can submit admission applications"}), 403

    data = request.get_json()
    if not data:
        return jsonify({"error": "Bad request", "message": "No JSON body"}), 400

    required = ["programId", "examLevel", "examYear", "indexNumber", "unebGrades", "dateOfBirth", "gender"]
    for field in required:
        if field not in data:
            return jsonify({"error": "Validation error", "message": f"{field} is required"}), 400

    program = db.session.get(Program, data["programId"])
    if not program:
        return jsonify({"error": "Not found", "message": "Program not found"}), 404

    existing = AdmissionApplication.query.filter_by(user_id=user.id).first()
    if existing:
        return jsonify({"error": "Conflict", "message": "You have already submitted an application"}), 409

    exam_level = data["examLevel"]
    if exam_level not in ("o_level", "a_level"):
        return jsonify({"error": "Validation error", "message": "examLevel must be 'o_level' or 'a_level'"}), 400

    # Degree programs require A-Level
    if program.level == "degree" and exam_level == "o_level":
        return jsonify({
            "error": "Validation error",
            "message": "Degree programs require A-Level (UACE) qualifications. Diploma programs accept O-Level."
        }), 422

    try:
        dob = date.fromisoformat(data["dateOfBirth"])
    except (ValueError, TypeError):
        return jsonify({"error": "Validation error", "message": "Invalid dateOfBirth format (use YYYY-MM-DD)"}), 400

    uneb_grades = data.get("unebGrades", {})
    if not isinstance(uneb_grades, dict):
        return jsonify({"error": "Validation error", "message": "unebGrades must be an object with 'olevel' and/or 'alevel' arrays"}), 400

    # Validate minimum subjects
    olevel_grades = uneb_grades.get("olevel", [])
    alevel_grades = uneb_grades.get("alevel", [])

    if exam_level == "o_level" and len(olevel_grades) < 5:
        return jsonify({"error": "Validation error", "message": "O-Level requires at least 5 subjects"}), 422

    if exam_level == "a_level":
        if len(olevel_grades) < 5:
            return jsonify({"error": "Validation error", "message": "Please provide your O-Level (UCE) results as well"}), 422
        principals = [s for s in alevel_grades if s.get("subjectType") == "principal"]
        if len(principals) < 2:
            return jsonify({"error": "Validation error", "message": "A-Level requires at least 2 principal subjects"}), 422

    app_number = generate_application_number()
    while AdmissionApplication.query.filter_by(application_number=app_number).first():
        app_number = generate_application_number()

    application = AdmissionApplication(
        application_number=app_number,
        user_id=user.id,
        program_id=program.id,
        exam_level=exam_level,
        exam_year=int(data["examYear"]),
        index_number=data["indexNumber"],
        uneb_grades=uneb_grades,
        personal_statement=data.get("personalStatement", ""),
        date_of_birth=dob,
        gender=data["gender"],
        nationality=data.get("nationality", "Ugandan"),
        district=data.get("district", ""),
        next_of_kin_name=data.get("nextOfKinName", ""),
        next_of_kin_phone=data.get("nextOfKinPhone", ""),
        next_of_kin_relationship=data.get("nextOfKinRelationship", ""),
        status="pending",
    )
    db.session.add(application)
    db.session.commit()

    return jsonify(application.to_dict()), 201


@admission_bp.route("/applications/<int:app_id>/certificate", methods=["POST"])
def upload_certificate(app_id):
    """Upload O-Level or A-Level academic certificate for an existing application."""
    user, error = get_current_user()
    if error:
        return jsonify({"error": "Unauthorized", "message": error}), 401

    application = db.session.get(AdmissionApplication, app_id)
    if not application:
        return jsonify({"error": "Not found", "message": "Application not found"}), 404

    if application.user_id != user.id and user.role != "admin":
        return jsonify({"error": "Forbidden", "message": "You can only upload certificates for your own application"}), 403

    cert_type = request.form.get("type", "olevel")  # 'olevel' or 'alevel'
    if cert_type not in ("olevel", "alevel"):
        return jsonify({"error": "Validation error", "message": "type must be 'olevel' or 'alevel'"}), 400

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
    else:
        application.alevel_certificate_path = url_path

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
    db.session.commit()

    return jsonify(application.to_dict()), 200


@admission_bp.route("/analytics", methods=["GET"])
def get_analytics():
    user, error = get_current_user()
    if error:
        return jsonify({"error": "Unauthorized", "message": error}), 401
    if user.role != "admin":
        return jsonify({"error": "Forbidden"}), 403

    from sqlalchemy import func
    total = AdmissionApplication.query.count()
    by_status = db.session.query(
        AdmissionApplication.status, func.count(AdmissionApplication.id)
    ).group_by(AdmissionApplication.status).all()
    by_program = db.session.query(
        Program.name, func.count(AdmissionApplication.id)
    ).join(AdmissionApplication).group_by(Program.name).all()

    return jsonify({
        "total": total,
        "byStatus": {s: c for s, c in by_status},
        "byProgram": [{"program": p, "count": c} for p, c in by_program],
    }), 200
