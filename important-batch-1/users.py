from flask import Blueprint, jsonify
from models import User
from routes.auth import get_current_user

users_bp = Blueprint("users", __name__)


@users_bp.route("", methods=["GET"])
def list_users():
    user, error = get_current_user()
    if error:
        return jsonify({"error": "Unauthorized", "message": error}), 401
    if user.role != "admin":
        return jsonify({"error": "Forbidden", "message": "Admin access required"}), 403

    users = User.query.order_by(User.created_at.desc()).all()
    return jsonify({"users": [u.to_dict() for u in users], "total": len(users)}), 200
