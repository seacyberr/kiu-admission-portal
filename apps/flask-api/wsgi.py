"""
WSGI entry point for production deployment (Gunicorn, uWSGI, etc.)
"""
from app import create_app

app = create_app()
