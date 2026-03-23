from flask import Blueprint, request, jsonify
import jwt
import os
from datetime import datetime, timedelta
from models import db, User

auth_bp = Blueprint("auth", __name__)

JWT_SECRET = os.environ.get("JWT_SECRET", "kiu-portal-secret-key-2024")


def generate_token(user_id, role):
    payload = {
        "userId": user_id,
        "role": role,
        "exp": datetime.utcnow() + timedelta(days=7),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm="HS256")


def verify_token(token):
    return jwt.decode(token, JWT_SECRET, algorithms=["HS256"])


def get_current_user():
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return None, "No token provided"
    token = auth_header[7:]
    try:
        payload = verify_token(token)
        user = User.query.get(payload["userId"])
        if not user:
            return None, "User not found"
        return user, None
    except jwt.ExpiredSignatureError:
        return None, "Token expired"
    except jwt.InvalidTokenError:
        return None, "Invalid token"


@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Bad request", "message": "No JSON body provided"}), 400

    email = data.get("email", "").strip().lower()
    password = data.get("password", "")
    first_name = data.get("firstName", "").strip()
    last_name = data.get("lastName", "").strip()
    phone = data.get("phone", "")
    national_id = data.get("nationalId", "")
    role = data.get("role", "applicant")

    if not email or not password or not first_name or not last_name:
        return jsonify({"error": "Validation error", "message": "email, password, firstName and lastName are required"}), 400

    if len(password) < 6:
        return jsonify({"error": "Validation error", "message": "Password must be at least 6 characters"}), 400

    if role not in ("applicant", "finalist", "admin"):
        role = "applicant"

    existing = User.query.filter_by(email=email).first()
    if existing:
        return jsonify({"error": "Conflict", "message": "An account with this email already exists"}), 409

    user = User(
        email=email,
        first_name=first_name,
        last_name=last_name,
        phone=phone or None,
        national_id=national_id or None,
        role=role,
    )
    user.set_password(password)
    db.session.add(user)
    db.session.commit()

    token = generate_token(user.id, user.role)
    return jsonify({"user": user.to_dict(), "token": token}), 201


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Bad request", "message": "No JSON body provided"}), 400

    email = data.get("email", "").strip().lower()
    password = data.get("password", "")

    if not email or not password:
        return jsonify({"error": "Validation error", "message": "email and password are required"}), 400

    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        return jsonify({"error": "Unauthorized", "message": "Invalid email or password"}), 401

    token = generate_token(user.id, user.role)
    return jsonify({"user": user.to_dict(), "token": token}), 200


@auth_bp.route("/logout", methods=["POST"])
def logout():
    return jsonify({"message": "Logged out successfully"}), 200


@auth_bp.route("/me", methods=["GET"])
def me():
    user, error = get_current_user()
    if error:
        return jsonify({"error": "Unauthorized", "message": error}), 401
    return jsonify(user.to_dict()), 200
