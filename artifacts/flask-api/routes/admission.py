from flask import Blueprint, request, jsonify
from datetime import datetime, date
import random
import string
from models import db, AdmissionApplication, Program, User
from routes.auth import get_current_user

admission_bp = Blueprint("admission", __name__)


def generate_application_number():
    year = datetime.now().year
    suffix = "".join(random.choices(string.digits, k=6))
    return f"KIU/{year}/{suffix}"


@admission_bp.route("/applications", methods=["POST"])
def create_application():
    user, error = get_current_user()
    if error:
        return jsonify({"error": "Unauthorized", "message": error}), 401

    data = request.get_json()
    if not data:
        return jsonify({"error": "Bad request", "message": "No JSON body"}), 400

    required = ["programId", "examLevel", "examYear", "indexNumber", "unebGrades", "dateOfBirth", "gender"]
    for field in required:
        if field not in data:
            return jsonify({"error": "Validation error", "message": f"{field} is required"}), 400

    program = Program.query.get(data["programId"])
    if not program:
        return jsonify({"error": "Not found", "message": "Program not found"}), 404

    existing = AdmissionApplication.query.filter_by(user_id=user.id).first()
    if existing:
        return jsonify({"error": "Conflict", "message": "You have already submitted an application"}), 409

    try:
        dob = date.fromisoformat(data["dateOfBirth"])
    except ValueError:
        return jsonify({"error": "Validation error", "message": "Invalid dateOfBirth format"}), 400

    app_number = generate_application_number()
    while AdmissionApplication.query.filter_by(application_number=app_number).first():
        app_number = generate_application_number()

    application = AdmissionApplication(
        application_number=app_number,
        user_id=user.id,
        program_id=data["programId"],
        exam_level=data["examLevel"],
        exam_year=data["examYear"],
        index_number=data["indexNumber"],
        uneb_grades=data["unebGrades"],
        personal_statement=data.get("personalStatement"),
        date_of_birth=dob,
        gender=data["gender"],
        nationality=data.get("nationality", "Ugandan"),
        district=data.get("district"),
        next_of_kin_name=data.get("nextOfKinName"),
        next_of_kin_phone=data.get("nextOfKinPhone"),
        next_of_kin_relationship=data.get("nextOfKinRelationship"),
    )
    db.session.add(application)
    db.session.commit()
    return jsonify(application.to_dict()), 201


@admission_bp.route("/applications", methods=["GET"])
def list_applications():
    user, error = get_current_user()
    if error:
        return jsonify({"error": "Unauthorized", "message": error}), 401
    if user.role != "admin":
        return jsonify({"error": "Forbidden", "message": "Admin access required"}), 403

    status = request.args.get("status")
    page = int(request.args.get("page", 1))
    limit = int(request.args.get("limit", 20))

    query = AdmissionApplication.query
    if status:
        query = query.filter_by(status=status)

    total = query.count()
    applications = query.order_by(AdmissionApplication.submitted_at.desc()).offset((page - 1) * limit).limit(limit).all()

    return jsonify({
        "applications": [a.to_dict() for a in applications],
        "total": total,
        "page": page,
        "limit": limit,
    }), 200


@admission_bp.route("/applications/my", methods=["GET"])
def get_my_application():
    user, error = get_current_user()
    if error:
        return jsonify({"error": "Unauthorized", "message": error}), 401

    application = AdmissionApplication.query.filter_by(user_id=user.id).first()
    if not application:
        return jsonify({"error": "Not found", "message": "No application found"}), 404

    return jsonify(application.to_dict()), 200


@admission_bp.route("/applications/<int:app_id>", methods=["GET"])
def get_application(app_id):
    user, error = get_current_user()
    if error:
        return jsonify({"error": "Unauthorized", "message": error}), 401

    application = AdmissionApplication.query.get(app_id)
    if not application:
        return jsonify({"error": "Not found", "message": "Application not found"}), 404

    if user.role != "admin" and application.user_id != user.id:
        return jsonify({"error": "Forbidden", "message": "Access denied"}), 403

    return jsonify(application.to_dict()), 200


@admission_bp.route("/applications/<int:app_id>", methods=["PATCH"])
def update_application_status(app_id):
    user, error = get_current_user()
    if error:
        return jsonify({"error": "Unauthorized", "message": error}), 401
    if user.role != "admin":
        return jsonify({"error": "Forbidden", "message": "Admin access required"}), 403

    application = AdmissionApplication.query.get(app_id)
    if not application:
        return jsonify({"error": "Not found", "message": "Application not found"}), 404

    data = request.get_json()
    valid_statuses = ["pending", "under_review", "accepted", "rejected", "waitlisted"]
    new_status = data.get("status")
    if new_status not in valid_statuses:
        return jsonify({"error": "Validation error", "message": f"Status must be one of {valid_statuses}"}), 400

    application.status = new_status
    if "adminNotes" in data:
        application.admin_notes = data["adminNotes"]
    application.updated_at = datetime.utcnow()
    db.session.commit()

    return jsonify(application.to_dict()), 200


@admission_bp.route("/programs", methods=["GET"])
def list_programs():
    faculty = request.args.get("faculty")
    level = request.args.get("level")

    query = Program.query
    if faculty:
        query = query.filter(Program.faculty.ilike(f"%{faculty}%"))
    if level:
        query = query.filter_by(level=level)

    programs = query.order_by(Program.faculty, Program.name).all()
    return jsonify({"programs": [p.to_dict() for p in programs], "total": len(programs)}), 200
