"""Admin Routes for KIU Admission Portal

Provides admin dashboard and management endpoints
"""

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from models import db, User, AdmissionApplication, Program
from routes.auth import get_current_user
from datetime import datetime, timedelta
from utils.api_response import success_response, paginated_response, unauthorized, forbidden, error_response
from utils.decorators import require_auth, require_admin
from sqlalchemy.orm import joinedload

admin_bp = Blueprint("admin", __name__)


def check_admin_access():
    """Verify user is admin"""
    user, error = get_current_user()
    if error:
        return None, unauthorized(error)
    if user.role != "admin":
        return None, forbidden("Admin access required")
    return user, None


@admin_bp.route("/dashboard", methods=["GET"])
@jwt_required()
@require_admin
def get_dashboard():
    """Get admin dashboard statistics"""
    user, error = check_admin_access()
    if error:
        return error
    
    # Get statistics
    total_users = User.query.count()
    total_applications = AdmissionApplication.query.count()
    pending_applications = AdmissionApplication.query.filter_by(status="pending").count()
    total_programs = Program.query.count()
    
    # Recent applications with eager loading to prevent N+1 queries
    recent_applications = (
        AdmissionApplication.query
        .options(joinedload(AdmissionApplication.user), joinedload(AdmissionApplication.program))
        .order_by(AdmissionApplication.created_at.desc())
        .limit(5)
        .all()
    )

    return success_response({
        "statistics": {
            "total_users": total_users,
            "total_applications": total_applications,
            "pending_applications": pending_applications,
            "total_programs": total_programs
        },
        "recent_applications": [
            {
                "id": app.id,
                "applicant_name": f"{app.user.first_name} {app.user.last_name}" if app.user else "Unknown",
                "program": app.program.name if app.program else "Unknown",
                "status": app.status,
                "created_at": app.created_at.isoformat() if app.created_at else None
            }
            for app in recent_applications
        ]
    })


@admin_bp.route("/users", methods=["GET"])
@jwt_required()
@require_admin
def get_admin_users():
    """Get all users for admin"""
    user, error = check_admin_access()
    if error:
        return error
    
    page = request.args.get("page", 1, type=int)
    per_page = min(request.args.get("perPage", 20, type=int), 100)
    role_filter = request.args.get("role")
    search = request.args.get("search", "")
    
    query = User.query
    
    if role_filter:
        query = query.filter(User.role == role_filter)
    if search:
        # Sanitize search term to prevent LIKE injection
        sanitized_search = search.replace("%", "").replace("_", "").replace("[", "").replace("]", "")
        search_pattern = f"%{sanitized_search}%"
        query = query.filter(
            (User.first_name.ilike(search_pattern)) |
            (User.last_name.ilike(search_pattern)) |
            (User.email.ilike(search_pattern))
        )
    
    paginated = query.order_by(User.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return paginated_response(
        items=[u.to_dict() for u in paginated.items],
        total=paginated.total,
        page=page,
        per_page=per_page,
        data_key="users"
    )


@admin_bp.route("/applications", methods=["GET"])
@jwt_required()
@require_admin
def get_admin_applications():
    """Get all applications for admin"""
    user, error = check_admin_access()
    if error:
        return error
    
    page = request.args.get("page", 1, type=int)
    per_page = min(request.args.get("perPage", 20, type=int), 100)
    status_filter = request.args.get("status")
    
    query = AdmissionApplication.query
    
    if status_filter:
        query = query.filter(AdmissionApplication.status == status_filter)
    
    paginated = query.order_by(AdmissionApplication.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return paginated_response(
        items=[app.to_dict() for app in paginated.items],
        total=paginated.total,
        page=page,
        per_page=per_page,
        data_key="applications"
    )


@admin_bp.route("/programs", methods=["GET"])
@jwt_required()
@require_admin
def get_admin_programs():
    """Get all programs for admin"""
    user, error = check_admin_access()
    if error:
        return error
    
    programs = Program.query.all()
    
    return success_response({"programs": [p.to_dict() for p in programs]})


@admin_bp.route("/statistics", methods=["GET"])
@jwt_required()
@require_admin
def get_admin_statistics():
    """Get detailed statistics for admin"""
    user, error = check_admin_access()
    if error:
        return error
    
    # User statistics
    total_users = User.query.count()
    users_by_role = db.session.query(User.role, db.func.count(User.id)).group_by(User.role).all()
    
    # Application statistics
    total_applications = AdmissionApplication.query.count()
    applications_by_status = db.session.query(
        AdmissionApplication.status, 
        db.func.count(AdmissionApplication.id)
    ).group_by(AdmissionApplication.status).all()
    
    # Recent activity (last 30 days)
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    recent_users = User.query.filter(User.created_at >= thirty_days_ago).count()
    recent_applications = AdmissionApplication.query.filter(
        AdmissionApplication.created_at >= thirty_days_ago
    ).count()
    
    return success_response({
        "users": {
            "total": total_users,
            "by_role": dict(users_by_role),
            "recent": recent_users
        },
        "applications": {
            "total": total_applications,
            "by_status": dict(applications_by_status),
            "recent": recent_applications
        }
    })


@admin_bp.route("/applications/<int:application_id>/status", methods=["PATCH"])
@require_auth
@require_admin
def update_application_status(application_id):
    """Update application status (accept, reject, review)."""
    from models import AdmissionApplication

    data = request.get_json()
    new_status = data.get("status")
    admin_notes = data.get("adminNotes", "")

    valid_statuses = ["pending", "under_review", "accepted", "rejected"]
    if new_status not in valid_statuses:
        return error_response(f"Invalid status. Must be one of: {', '.join(valid_statuses)}", 400)

    application = AdmissionApplication.query.get(application_id)
    if not application:
        return error_response("Application not found", 404)

    application.status = new_status
    if admin_notes:
        application.admin_notes = admin_notes

    db.session.commit()

    return success_response({
        "id": application.id,
        "status": application.status,
        "adminNotes": application.admin_notes
    }, message=f"Application status updated to {new_status}")
