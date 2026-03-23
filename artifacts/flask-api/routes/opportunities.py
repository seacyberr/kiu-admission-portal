from flask import Blueprint, request, jsonify
from datetime import datetime, date
from models import db, Opportunity, OpportunityApplication
from routes.auth import get_current_user

opportunities_bp = Blueprint("opportunities", __name__)


@opportunities_bp.route("", methods=["GET"])
def list_opportunities():
    opp_type = request.args.get("type")
    field = request.args.get("field")
    page = int(request.args.get("page", 1))
    limit = int(request.args.get("limit", 20))

    query = Opportunity.query.filter_by(is_active=True)
    if opp_type:
        query = query.filter_by(type=opp_type)
    if field:
        query = query.filter(Opportunity.required_programs.contains([field]))

    total = query.count()
    opps = query.order_by(Opportunity.posted_at.desc()).offset((page - 1) * limit).limit(limit).all()

    return jsonify({
        "opportunities": [o.to_dict() for o in opps],
        "total": total,
        "page": page,
        "limit": limit,
    }), 200


@opportunities_bp.route("", methods=["POST"])
def create_opportunity():
    user, error = get_current_user()
    if error:
        return jsonify({"error": "Unauthorized", "message": error}), 401
    if user.role != "admin":
        return jsonify({"error": "Forbidden", "message": "Admin access required"}), 403

    data = request.get_json()
    required = ["title", "organization", "type", "description", "requirements", "applicationDeadline"]
    for field in required:
        if field not in data:
            return jsonify({"error": "Validation error", "message": f"{field} is required"}), 400

    try:
        deadline = date.fromisoformat(data["applicationDeadline"])
    except ValueError:
        return jsonify({"error": "Validation error", "message": "Invalid applicationDeadline format"}), 400

    opp = Opportunity(
        title=data["title"],
        organization=data["organization"],
        type=data["type"],
        description=data["description"],
        requirements=data["requirements"],
        required_programs=data.get("requiredPrograms", []),
        required_skills=data.get("requiredSkills", []),
        location=data.get("location"),
        salary_range=data.get("salaryRange"),
        application_deadline=deadline,
        contact_email=data.get("contactEmail"),
        is_active=data.get("isActive", True),
    )
    db.session.add(opp)
    db.session.commit()
    return jsonify(opp.to_dict()), 201


@opportunities_bp.route("/<int:opp_id>", methods=["GET"])
def get_opportunity(opp_id):
    opp = Opportunity.query.get(opp_id)
    if not opp:
        return jsonify({"error": "Not found", "message": "Opportunity not found"}), 404
    return jsonify(opp.to_dict()), 200


@opportunities_bp.route("/<int:opp_id>", methods=["PATCH"])
def update_opportunity(opp_id):
    user, error = get_current_user()
    if error:
        return jsonify({"error": "Unauthorized", "message": error}), 401
    if user.role != "admin":
        return jsonify({"error": "Forbidden", "message": "Admin access required"}), 403

    opp = Opportunity.query.get(opp_id)
    if not opp:
        return jsonify({"error": "Not found", "message": "Opportunity not found"}), 404

    data = request.get_json()
    for field, attr in [
        ("title", "title"), ("organization", "organization"), ("type", "type"),
        ("description", "description"), ("requirements", "requirements"),
        ("location", "location"), ("salaryRange", "salary_range"),
        ("contactEmail", "contact_email"), ("isActive", "is_active"),
        ("requiredPrograms", "required_programs"), ("requiredSkills", "required_skills"),
    ]:
        if field in data:
            setattr(opp, attr, data[field])

    if "applicationDeadline" in data:
        opp.application_deadline = date.fromisoformat(data["applicationDeadline"])

    opp.updated_at = datetime.utcnow()
    db.session.commit()
    return jsonify(opp.to_dict()), 200


@opportunities_bp.route("/<int:opp_id>", methods=["DELETE"])
def delete_opportunity(opp_id):
    user, error = get_current_user()
    if error:
        return jsonify({"error": "Unauthorized", "message": error}), 401
    if user.role != "admin":
        return jsonify({"error": "Forbidden", "message": "Admin access required"}), 403

    opp = Opportunity.query.get(opp_id)
    if not opp:
        return jsonify({"error": "Not found", "message": "Opportunity not found"}), 404

    db.session.delete(opp)
    db.session.commit()
    return "", 204


@opportunities_bp.route("/<int:opp_id>/apply", methods=["POST"])
def apply_for_opportunity(opp_id):
    user, error = get_current_user()
    if error:
        return jsonify({"error": "Unauthorized", "message": error}), 401

    opp = Opportunity.query.get(opp_id)
    if not opp or not opp.is_active:
        return jsonify({"error": "Not found", "message": "Opportunity not found or no longer active"}), 404

    existing = OpportunityApplication.query.filter_by(opportunity_id=opp_id, user_id=user.id).first()
    if existing:
        return jsonify({"error": "Conflict", "message": "You have already applied for this opportunity"}), 409

    data = request.get_json()
    if not data or not data.get("coverLetter"):
        return jsonify({"error": "Validation error", "message": "coverLetter is required"}), 400

    app = OpportunityApplication(
        opportunity_id=opp_id,
        user_id=user.id,
        cover_letter=data["coverLetter"],
        cv_url=data.get("cvUrl"),
        additional_info=data.get("additionalInfo"),
    )
    db.session.add(app)
    db.session.commit()
    return jsonify(app.to_dict()), 201


@opportunities_bp.route("/applications/my", methods=["GET"])
def my_applications():
    user, error = get_current_user()
    if error:
        return jsonify({"error": "Unauthorized", "message": error}), 401

    apps = OpportunityApplication.query.filter_by(user_id=user.id).order_by(
        OpportunityApplication.applied_at.desc()
    ).all()

    return jsonify({"applications": [a.to_dict() for a in apps], "total": len(apps)}), 200


@opportunities_bp.route("/applications/<int:app_id>", methods=["PATCH"])
def update_application_status(app_id):
    user, error = get_current_user()
    if error:
        return jsonify({"error": "Unauthorized", "message": error}), 401
    if user.role != "admin":
        return jsonify({"error": "Forbidden", "message": "Admin access required"}), 403

    app = OpportunityApplication.query.get(app_id)
    if not app:
        return jsonify({"error": "Not found", "message": "Application not found"}), 404

    data = request.get_json()
    valid_statuses = ["applied", "shortlisted", "interview_scheduled", "accepted", "rejected"]
    new_status = data.get("status")
    if new_status not in valid_statuses:
        return jsonify({"error": "Validation error", "message": f"Status must be one of {valid_statuses}"}), 400

    app.status = new_status
    if "adminNotes" in data:
        app.admin_notes = data["adminNotes"]
    app.updated_at = datetime.utcnow()
    db.session.commit()
    return jsonify(app.to_dict()), 200
