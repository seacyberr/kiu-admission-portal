"""Pytest configuration and fixtures."""
import pytest
import os
os.environ["DATABASE_URL"] = "sqlite:///:memory:"
os.environ["SEED_DATABASE"] = "false"
os.environ["JWT_SECRET"] = "test-secret-key"
os.environ["FLASK_ENV"] = "testing"

from app import create_app
from models import db, User, OtpCode, Program
from datetime import datetime, timedelta


@pytest.fixture
def app():
    """Create application for testing."""
    app = create_app()
    app.config["TESTING"] = True
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """Create test client."""
    return app.test_client()


@pytest.fixture
def test_user_email():
    return "test@example.com"

@pytest.fixture
def test_user(app, test_user_email):
    """Create a test user."""
    with app.app_context():
        user = User(
            email=test_user_email,
            first_name="Test",
            last_name="User",
            role="applicant",
            is_verified=False,
        )
        user.set_password("TestPass123")
        db.session.add(user)
        db.session.commit()
        return user


@pytest.fixture
def verified_user_email():
    return "verified@example.com"

@pytest.fixture
def verified_user(app, verified_user_email):
    """Create a verified test user."""
    with app.app_context():
        user = User(
            email=verified_user_email,
            first_name="Verified",
            last_name="User",
            role="applicant",
            is_verified=True,
        )
        user.set_password("TestPass123")
        db.session.add(user)
        db.session.commit()
        return user


@pytest.fixture
def admin_user_email():
    return "admin@example.com"

@pytest.fixture
def admin_user(app, admin_user_email):
    """Create an admin user."""
    with app.app_context():
        user = User(
            email=admin_user_email,
            first_name="Admin",
            last_name="User",
            role="admin",
            is_verified=True,
        )
        user.set_password("AdminPass123")
        db.session.add(user)
        db.session.commit()
        return user


@pytest.fixture
def test_otp(app, test_user_email, test_user):
    """Create a test OTP."""
    # Ensure user exists
    _ = test_user
    with app.app_context():
        user = User.query.filter_by(email=test_user_email).first()
        otp = OtpCode(
            user_id=user.id,
            code="123456",
            expires_at=datetime.utcnow() + timedelta(minutes=10),
            is_used=False,
        )
        db.session.add(otp)
        db.session.commit()
        return otp


@pytest.fixture
def auth_headers(client, verified_user_email, verified_user):
    """Get auth headers for verified user."""
    # Ensure user exists in database
    _ = verified_user
    response = client.post("/api/auth/login", json={
        "email": verified_user_email,
        "password": "TestPass123",
    })
    token = response.get_json()["accessToken"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def admin_headers(client, admin_user_email, admin_user):
    """Get auth headers for admin user."""
    # Ensure user exists in database
    _ = admin_user
    response = client.post("/api/auth/login", json={
        "email": admin_user_email,
        "password": "AdminPass123",
    })
    token = response.get_json()["accessToken"]
    return {"Authorization": f"Bearer {token}"}
