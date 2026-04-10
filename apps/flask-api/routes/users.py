from flask import Blueprint, jsonify, request
from models import db, User, AdmissionApplication
from routes.auth import get_current_user
from datetime import datetime

users_bp = Blueprint("users", __name__)


def check_admin_access():
    """Verify user is admin"""
    user, error = get_current_user()
    if error:
        return None, (jsonify({"error": "Unauthorized", "message": error}), 401)
    if user.role != "admin":
        return None, (jsonify({"error": "Forbidden", "message": "Admin access required"}), 403)
    return user, None


@users_bp.route("", methods=["GET"])
def list_users():
    user, error = check_admin_access()
    if error:
        return error

    page = request.args.get("page", 1, type=int)
    per_page = min(request.args.get("perPage", 20, type=int), 100)
    role_filter = request.args.get("role")
    search = request.args.get("search", "")
    is_verified = request.args.get("isVerified")

    query = User.query

    if role_filter:
        query = query.filter(User.role == role_filter)
    if is_verified is not None:
        query = query.filter(User.is_verified == (is_verified.lower() == "true"))
    if search:
        query = query.filter(
            (User.first_name.ilike(f"%{search}%")) |
            (User.last_name.ilike(f"%{search}%")) |
            (User.email.ilike(f"%{search}%"))
        )

    paginated = query.order_by(User.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    return jsonify({
        "users": [u.to_dict() for u in paginated.items],
        "total": paginated.total,
        "page": page,
        "perPage": per_page,
        "pages": paginated.pages
    }), 200


@users_bp.route("/<int:user_id>", methods=["GET"])
def get_user(user_id):
    """Get detailed user information including applications"""
    user, error = check_admin_access()
    if error:
        return error

    target_user = User.query.get_or_404(user_id)

    # Get user's applications
    applications = AdmissionApplication.query.filter_by(user_id=user_id).all()

    user_data = target_user.to_dict()
    user_data["applications"] = [app.to_dict() for app in applications]
    user_data["applications_count"] = len(applications)

    return jsonify(user_data), 200


@users_bp.route("/<int:user_id>/role", methods=["PATCH"])
def update_user_role(user_id):
    """Update user role"""
    admin_user, error = check_admin_access()
    if error:
        return error

    target_user = User.query.get_or_404(user_id)
    data = request.get_json()

    new_role = data.get("role")
    valid_roles = ["applicant", "admin", "staff", "reviewer"]

    if new_role not in valid_roles:
        return jsonify({
            "error": "Invalid role",
            "message": f"Role must be one of: {', '.join(valid_roles)}"
        }), 400

    # Prevent self-demotion from admin
    if target_user.id == admin_user.id and new_role != "admin":
        return jsonify({
            "error": "Forbidden",
            "message": "Cannot change your own admin role"
        }), 403

    target_user.role = new_role
    target_user.updated_at = datetime.utcnow()
    db.session.commit()

    return jsonify({
        "message": f"User role updated to {new_role}",
        "user": target_user.to_dict()
    }), 200


@users_bp.route("/<int:user_id>/status", methods=["PATCH"])
def update_user_status(user_id):
    """Update user verification status"""
    admin_user, error = check_admin_access()
    if error:
        return error

    target_user = User.query.get_or_404(user_id)
    data = request.get_json()

    is_verified = data.get("isVerified")
    if is_verified is None:
        return jsonify({"error": "Missing field", "message": "isVerified is required"}), 400

    target_user.is_verified = bool(is_verified)
    target_user.updated_at = datetime.utcnow()
    db.session.commit()

    status = "verified" if target_user.is_verified else "unverified"
    return jsonify({
        "message": f"User marked as {status}",
        "user": target_user.to_dict()
    }), 200


@users_bp.route("/<int:user_id>", methods=["DELETE"])
def delete_user(user_id):
    """Delete a user account"""
    admin_user, error = check_admin_access()
    if error:
        return error

    target_user = User.query.get_or_404(user_id)

    # Prevent self-deletion
    if target_user.id == admin_user.id:
        return jsonify({
            "error": "Forbidden",
            "message": "Cannot delete your own account"
        }), 403

    # Check if user has applications
    applications_count = AdmissionApplication.query.filter_by(user_id=user_id).count()

    db.session.delete(target_user)
    db.session.commit()

    return jsonify({
        "message": "User deleted successfully",
        "deleted_applications": applications_count
    }), 200


# ============================================================================
# BULK OPERATIONS
# ============================================================================

@users_bp.route("/bulk/verify", methods=["POST"])
def bulk_verify_users():
    """Bulk verify multiple users"""
    admin_user, error = check_admin_access()
    if error:
        return error

    data = request.get_json()
    user_ids = data.get("user_ids", [])

    if not user_ids or not isinstance(user_ids, list):
        return jsonify({"error": "Missing field", "message": "user_ids array is required"}), 400

    updated_count = 0
    not_found = []

    for user_id in user_ids:
        user = User.query.get(user_id)
        if user:
            user.is_verified = True
            user.updated_at = datetime.utcnow()
            updated_count += 1
        else:
            not_found.append(user_id)

    db.session.commit()

    return jsonify({
        "message": f"{updated_count} users verified successfully",
        "updated_count": updated_count,
        "not_found": not_found
    }), 200


@users_bp.route("/bulk/role", methods=["POST"])
def bulk_update_role():
    """Bulk update role for multiple users"""
    admin_user, error = check_admin_access()
    if error:
        return error

    data = request.get_json()
    user_ids = data.get("user_ids", [])
    new_role = data.get("role")

    valid_roles = ["applicant", "admin", "staff", "reviewer"]
    if new_role not in valid_roles:
        return jsonify({
            "error": "Invalid role",
            "message": f"Role must be one of: {', '.join(valid_roles)}"
        }), 400

    if not user_ids or not isinstance(user_ids, list):
        return jsonify({"error": "Missing field", "message": "user_ids array is required"}), 400

    # Prevent changing own role through bulk
    if admin_user.id in user_ids:
        return jsonify({
            "error": "Forbidden",
            "message": "Cannot change your own role through bulk operation"
        }), 403

    updated_count = 0
    not_found = []

    for user_id in user_ids:
        user = User.query.get(user_id)
        if user:
            user.role = new_role
            user.updated_at = datetime.utcnow()
            updated_count += 1
        else:
            not_found.append(user_id)

    db.session.commit()

    return jsonify({
        "message": f"{updated_count} users updated to role: {new_role}",
        "updated_count": updated_count,
        "not_found": not_found
    }), 200


@users_bp.route("/bulk/delete", methods=["POST"])
def bulk_delete_users():
    """Bulk delete multiple users"""
    admin_user, error = check_admin_access()
    if error:
        return error

    data = request.get_json()
    user_ids = data.get("user_ids", [])

    if not user_ids or not isinstance(user_ids, list):
        return jsonify({"error": "Missing field", "message": "user_ids array is required"}), 400

    # Prevent self-deletion
    if admin_user.id in user_ids:
        return jsonify({
            "error": "Forbidden",
            "message": "Cannot delete your own account through bulk operation"
        }), 403

    deleted_count = 0
    not_found = []

    for user_id in user_ids:
        user = User.query.get(user_id)
        if user:
            db.session.delete(user)
            deleted_count += 1
        else:
            not_found.append(user_id)

    db.session.commit()

    return jsonify({
        "message": f"{deleted_count} users deleted successfully",
        "deleted_count": deleted_count,
        "not_found": not_found
    }), 200


@users_bp.route("/bulk/export", methods=["POST"])
def bulk_export_users():
    """Export user data to CSV"""
    import csv
    import io
    from flask import Response

    admin_user, error = check_admin_access()
    if error:
        return error

    data = request.get_json() or {}
    user_ids = data.get("user_ids", [])
    role_filter = data.get("role")

    # Build query
    query = User.query
    if user_ids:
        query = query.filter(User.id.in_(user_ids))
    if role_filter:
        query = query.filter(User.role == role_filter)

    users = query.order_by(User.created_at.desc()).all()

    # Prepare CSV data
    output = io.StringIO()
    writer = csv.writer(output)

    # Header
    writer.writerow([
        "ID", "Email", "First Name", "Last Name", "Phone",
        "Role", "Verified", "National ID", "Created At"
    ])

    # Data rows
    for user in users:
        writer.writerow([
            user.id,
            user.email,
            user.first_name,
            user.last_name,
            user.phone or "",
            user.role,
            "Yes" if user.is_verified else "No",
            user.national_id or "",
            user.created_at.isoformat() if user.created_at else ""
        ])

    response = Response(output.getvalue(), mimetype="text/csv")
    response.headers["Content-Disposition"] = "attachment; filename=users_export.csv"
    return response
