from flask import Blueprint, request, jsonify
from datetime import datetime
from models import db, CareerPath, FinalistProfile, Program
from routes.auth import get_current_user

career_bp = Blueprint("career", __name__)


@career_bp.route("/paths", methods=["GET"])
def list_career_paths():
    program_name = request.args.get("program")
    faculty = request.args.get("faculty")
    page = int(request.args.get("page", 1))
    limit = int(request.args.get("limit", 20))

    query = CareerPath.query
    if program_name:
        # Cross-compatible JSON array search (works on both MySQL and PostgreSQL)
        # Uses LIKE with JSON substring pattern instead of PostgreSQL-specific @>
        query = query.filter(CareerPath.related_programs.like(f'%"{program_name}"%'))
    if faculty:
        query = query.filter_by(industry_field=faculty)

    total = query.count()
    paths = query.offset((page - 1) * limit).limit(limit).all()
    return jsonify({
        "careerPaths": [p.to_dict() for p in paths],
        "total": total,
        "page": page,
        "limit": limit,
    }), 200


@career_bp.route("/my-profile", methods=["GET"])
def get_my_profile():
    user, error = get_current_user()
    if error:
        return jsonify({"error": "Unauthorized", "message": error}), 401

    profile = FinalistProfile.query.filter_by(user_id=user.id).first()
    if not profile:
        return jsonify({"error": "Not found", "message": "Finalist profile not found"}), 404

    return jsonify(profile.to_dict()), 200


@career_bp.route("/my-profile", methods=["PUT"])
def upsert_my_profile():
    user, error = get_current_user()
    if error:
        return jsonify({"error": "Unauthorized", "message": error}), 401

    data = request.get_json()
    if not data:
        return jsonify({"error": "Bad request", "message": "No JSON body"}), 400

    required = ["programId", "studentNumber", "yearOfStudy"]
    for field in required:
        if field not in data:
            return jsonify({"error": "Validation error", "message": f"{field} is required"}), 400

    program = Program.query.get(data["programId"])
    if not program:
        return jsonify({"error": "Not found", "message": "Program not found"}), 404

    profile = FinalistProfile.query.filter_by(user_id=user.id).first()
    if not profile:
        profile = FinalistProfile(user_id=user.id)
        db.session.add(profile)

    profile.program_id = data["programId"]
    profile.student_number = data["studentNumber"]
    profile.year_of_study = data["yearOfStudy"]
    profile.graduation_year = data.get("graduationYear")
    profile.gpa = data.get("gpa")
    profile.skills = data.get("skills", [])
    profile.bio = data.get("bio")
    profile.linkedin_url = data.get("linkedinUrl")
    profile.cv_url = data.get("cvUrl")
    profile.is_finalist = True
    profile.updated_at = datetime.utcnow()

    db.session.commit()
    return jsonify(profile.to_dict()), 200
