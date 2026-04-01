"""API v1 blueprint."""
from flask import Blueprint

v1_bp = Blueprint("v1", __name__)

# Import all v1 routes
from routes.v1 import auth, admission, career, opportunities, users, docs