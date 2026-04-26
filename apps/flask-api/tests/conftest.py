"""
Minimal pytest configuration for KIU Admission Portal tests.
"""
import pytest
import os

# Set test environment
os.environ["FLASK_ENV"] = "testing"
os.environ["UPLOAD_FOLDER"] = "/tmp/test_uploads"

from app import create_app, db


@pytest.fixture
def app():
    """Create application for testing."""
    app = create_app()
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    app.config["WTF_CSRF_ENABLED"] = False
    
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()


@pytest.fixture
def client(app):
    """Create test client."""
    return app.test_client()
