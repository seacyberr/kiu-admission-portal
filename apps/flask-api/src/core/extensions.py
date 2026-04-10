"""
Flask Extensions - Centralized extension instances
"""
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from flask_limiting import Limiter
from flask_limiting.util import get_remote_address

# Initialize extensions without app (app factory pattern)
db = SQLAlchemy()
bcrypt = Bcrypt()
cors = CORS()
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)
