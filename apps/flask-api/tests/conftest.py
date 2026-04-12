"""
Pytest Configuration - Comprehensive Test Fixtures
Industry-standard test setup for KIU Admission Portal
"""
import pytest
import os
import json
from datetime import datetime, timedelta
from typing import Dict, Any, Generator

# Test environment configuration
os.environ["DATABASE_URL"] = "sqlite:///:memory:"
os.environ["SEED_DATABASE"] = "false"
os.environ["JWT_SECRET"] = "test-secret-key-for-testing-only"
os.environ["FLASK_ENV"] = "testing"
os.environ["UPLOAD_FOLDER"] = "/tmp/test_uploads"

from app import create_app
from models import db, User, Program, AdmissionApplication
from services.kiu_programs_database import KIU_PROGRAMS_DB


def pytest_collection_modifyitems(config, items):
    """Configure test collection - organize by markers and priority."""
    # Priority test mapping - tests that are CRITICAL (must always pass)
    critical_patterns = [
        "test_successful_registration",
        "test_login_success",
        "test_token_refresh",
        "test_olevel_to_certificate",
        "test_alevel_to_bachelor",
        "test_apply_with_valid_data",
        "test_accept_application",
        "test_reject_application",
        "test_password_hashing",
        "test_applicant_role_access",
        "test_admin_role_access",
        "test_db_connection",
        "test_user_model",
        "test_program_model",
    ]
    
    # Important patterns - should run in CI
    important_patterns = [
        "test_alevel_to_diploma",
        "test_hec_to_bachelor",
        "test_diploma_progression",
        "test_masters_entry",
        "test_phd_entry",
        "test_health_science",
        "test_multiple_applications",
        "test_interview_scheduling",
        "test_rate_limiting",
        "test_validation",
        "test_finalist_profile",
        "test_job_applications",
    ]
    
    # Add markers for test organization
    for item in items:
        nodeid = item.nodeid.lower()
        
        # Category markers
        if "test_auth" in nodeid:
            item.add_marker(pytest.mark.auth)
        elif "test_admission" in nodeid:
            item.add_marker(pytest.mark.admission)
        elif "test_admin" in nodeid:
            item.add_marker(pytest.mark.admin)
        elif "test_career" in nodeid:
            item.add_marker(pytest.mark.career)
        elif "test_pathway" in nodeid:
            item.add_marker(pytest.mark.pathway)
        
        # Priority markers
        if any(pattern in nodeid for pattern in critical_patterns):
            item.add_marker(pytest.mark.critical)
        elif any(pattern in nodeid for pattern in important_patterns):
            item.add_marker(pytest.mark.important)
        else:
            item.add_marker(pytest.mark.extended)


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
    """Create a test user (unverified) for OTP tests."""
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


# ============================================================================
# APPLICATION FIXTURES
# ============================================================================

@pytest.fixture
def app() -> Generator:
    """
    Create Flask application for testing.
    Yields configured app with in-memory database.
    """
    app = create_app()
    app.config["TESTING"] = True
    app.config["WTF_CSRF_ENABLED"] = False
    
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """Create test HTTP client."""
    return app.test_client()


@pytest.fixture
def app_context(app):
    """Provide application context for database operations."""
    with app.app_context():
        yield app


# ============================================================================
# USER FIXTURES - All User Types
# ============================================================================

@pytest.fixture
def user_data() -> Dict[str, Any]:
    """Standard user registration data."""
    return {
        "email": "test.user@example.com",
        "password": "TestPassword123!",
        "first_name": "Test",
        "last_name": "User",
        "phone": "+256700000001",
        "role": "applicant"
    }


@pytest.fixture
def create_user(app_context, user_data):
    """Factory fixture to create verified users."""
    def _create_user(verified=True, role="applicant", **overrides):
        data = {**user_data, **overrides}
        data["role"] = role
        
        user = User(
            email=data["email"],
            first_name=data["first_name"],
            last_name=data["last_name"],
            phone=data.get("phone"),
            role=role,
            is_verified=verified
        )
        user.set_password(data["password"])
        db.session.add(user)
        db.session.commit()
        return user
    return _create_user


@pytest.fixture
def applicant_user(create_user):
    """Create a verified applicant user."""
    return create_user(role="applicant", email="applicant@test.com")


@pytest.fixture
def finalist_user(create_user):
    """Create a verified finalist user."""
    return create_user(role="finalist", email="finalist@test.com")


@pytest.fixture
def admin_user(create_user):
    """Create a verified admin user."""
    return create_user(role="admin", email="admin@test.com")


@pytest.fixture
def unverified_user(create_user):
    """Create an unverified user."""
    return create_user(verified=False, email="unverified@test.com")


# ============================================================================
# AUTHENTICATION FIXTURES
# ============================================================================

@pytest.fixture
def auth_headers(app_context, applicant_user) -> Dict[str, str]:
    """Generate valid JWT authorization headers for authenticated requests."""
    from flask_jwt_extended import create_access_token
    
    token = create_access_token(
        identity=applicant_user.id,
        additional_claims={"role": applicant_user.role, "email": applicant_user.email}
    )
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }


@pytest.fixture
def admin_auth_headers(app_context, admin_user) -> Dict[str, str]:
    """Generate admin JWT authorization headers."""
    from flask_jwt_extended import create_access_token
    
    token = create_access_token(
        identity=admin_user.id,
        additional_claims={"role": admin_user.role, "email": admin_user.email}
    )
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }


@pytest.fixture
def finalist_auth_headers(app_context, finalist_user) -> Dict[str, str]:
    """Generate finalist JWT authorization headers for career portal tests."""
    from flask_jwt_extended import create_access_token
    
    token = create_access_token(
        identity=finalist_user.id,
        additional_claims={"role": finalist_user.role, "email": finalist_user.email}
    )
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }


# ============================================================================
# PROGRAM FIXTURES
# ============================================================================

@pytest.fixture
def create_program(app_context):
    """Factory fixture to create academic programs."""
    def _create_program(
        code: str,
        name: str,
        level: str,
        campus: str = "kampala",
        faculty: str = "Science",
        **kwargs
    ):
        program = Program(
            code=code,
            name=name,
            level=level,
            campus=campus,
            faculty=faculty,
            **kwargs
        )
        db.session.add(program)
        db.session.commit()
        return program
    return _create_program


@pytest.fixture
def sample_programs(create_program):
    """Create sample programs for all education levels."""
    programs = {
        "certificate": create_program(
            code="CERT-IT",
            name="Certificate in Information Technology",
            level="certificate",
            tuition_ugx=550000
        ),
        "diploma": create_program(
            code="DIT",
            name="Diploma in Information Technology",
            level="diploma",
            tuition_ugx=950000
        ),
        "bachelor": create_program(
            code="BIT",
            name="Bachelor of Information Technology",
            level="bachelor",
            tuition_ugx=1_500_000
        ),
        "masters": create_program(
            code="MIT",
            name="Master of Information Technology",
            level="masters",
            tuition_ugx=2_500_000
        ),
        "phd": create_program(
            code="PHD-CS",
            name="PhD in Computer Science",
            level="phd",
            tuition_ugx=3_000_000
        ),
        "hec": create_program(
            code="HEC-ICT",
            name="Higher Education Certificate in ICT",
            level="hec",
            tuition_ugx=0
        )
    }
    return programs


@pytest.fixture
def health_programs(create_program):
    """Create health science programs with higher fees."""
    return {
        "mbchb": create_program(
            code="MBChB",
            name="Bachelor of Medicine and Bachelor of Surgery",
            level="bachelor",
            category="health",
            campus="western",
            tuition_ugx=7_085_000,
            functional_fee_ugx=700_000
        ),
        "bpharm": create_program(
            code="BPharm",
            name="Bachelor of Pharmacy",
            level="bachelor",
            category="health",
            campus="western",
            tuition_ugx=4_160_000,
            functional_fee_ugx=700_000
        )
    }


# ============================================================================
# INTAKE FIXTURES
# ============================================================================

@pytest.fixture
def active_intake(app_context):
    """Create an active admission intake."""
    from datetime import date
    
    intake = Intake(
        name="September 2026",
        academic_year="2026/2027",
        semester="Semester 1",
        start_date=date(2026, 9, 1),
        end_date=date(2026, 12, 15),
        application_opens=date(2026, 1, 1),
        application_deadline=date(2026, 8, 15),
        is_active=True,
        is_admission_open=True
    )
    db.session.add(intake)
    db.session.commit()
    return intake


# ============================================================================
# APPLICATION FIXTURES
# ============================================================================

@pytest.fixture
def create_application(app_context, applicant_user, sample_programs, active_intake):
    """Factory fixture to create admission applications."""
    def _create_application(
        program_level: str = "bachelor",
        qualification_type: str = "a_level",
        status: str = "draft",
        **kwargs
    ):
        program = sample_programs.get(program_level, sample_programs["bachelor"])
        
        application = AdmissionApplication(
            applicant_id=applicant_user.id,
            program_id=program.id,
            intake_id=active_intake.id,
            entry_level=program_level,
            qualification_type=qualification_type,
            status=status,
            academic_records=kwargs.get("academic_records", {}),
            curriculum_version=kwargs.get("curriculum_version", "old"),
            date_of_birth=kwargs.get("date_of_birth"),
            gender=kwargs.get("gender", "male"),
            nationality=kwargs.get("nationality", "Ugandan"),
            district=kwargs.get("district", "Kampala"),
            next_of_kin_name=kwargs.get("next_of_kin_name", "Parent Name"),
            next_of_kin_phone=kwargs.get("next_of_kin_phone", "+256700000002"),
            next_of_kin_relationship=kwargs.get("next_of_kin_relationship", "Parent"),
            personal_statement=kwargs.get("personal_statement", "I want to study at KIU")
        )
        db.session.add(application)
        db.session.commit()
        return application
    return _create_application


# ============================================================================
# PATHWAY-SPECIFIC FIXTURES
# ============================================================================

@pytest.fixture
def o_level_grades():
    """Sample O-Level (UCE) grades."""
    return {
        "mathematics": "C",
        "english": "B",
        "physics": "B",
        "chemistry": "C",
        "biology": "B",
        "history": "A",
        "geography": "B",
        "commerce": "A"
    }


@pytest.fixture
def a_level_grades():
    """Sample A-Level (UACE) grades."""
    return {
        "subjects": [
            {"name": "Physics", "grade": "B", "points": 5},
            {"name": "Chemistry", "grade": "C", "points": 4},
            {"name": "Mathematics", "grade": "B", "points": 5}
        ],
        "total_points": 14,
        "number_of_subjects": 3
    }


@pytest.fixture
def diploma_transcript():
    """Sample diploma transcript data."""
    return {
        "institution": "Uganda Polytechnic",
        "program": "Diploma in Computer Science",
        "completion_year": 2024,
        "cgpa": 3.8,
        "credit_hours": 120,
        "classification": "Second Class Upper"
    }


@pytest.fixture
def degree_transcript():
    """Sample degree transcript for masters entry."""
    return {
        "institution": "Makerere University",
        "program": "Bachelor of Science in Computer Science",
        "completion_year": 2023,
        "cgpa": 4.2,
        "credit_hours": 180,
        "classification": "First Class"
    }


@pytest.fixture
def masters_transcript():
    """Sample masters transcript for PhD entry."""
    return {
        "institution": "Kampala International University",
        "program": "Master of Science in Information Technology",
        "completion_year": 2025,
        "cgpa": 4.5,
        "research_thesis": "AI in Healthcare",
        "supervisor": "Dr. James Smith"
    }


# ============================================================================
# TEST DATA FIXTURES
# ============================================================================

@pytest.fixture
def valid_registration_data():
    """Valid user registration payload."""
    return {
        "email": "new.user@example.com",
        "password": "SecurePass123!",
        "firstName": "New",
        "lastName": "User",
        "phone": "+256700000003",
        "role": "applicant"
    }


@pytest.fixture
def valid_login_data(user_data):
    """Valid login credentials."""
    return {
        "email": user_data["email"],
        "password": user_data["password"]
    }


@pytest.fixture
def invalid_login_data():
    """Invalid login credentials for negative testing."""
    return {
        "email": "nonexistent@example.com",
        "password": "WrongPassword123!"
    }


@pytest.fixture
def application_payload(sample_programs):
    """Standard application submission payload."""
    return {
        "program_ids": [sample_programs["bachelor"].id],
        "exam_level": "a_level",
        "exam_year": 2023,
        "index_number": "U1234/001",
        "uneb_grades": {
            "physics": {"grade": "B", "points": 5},
            "chemistry": {"grade": "C", "points": 4},
            "mathematics": {"grade": "B", "points": 5}
        },
        "date_of_birth": "2000-01-15",
        "gender": "male"
    }


# ============================================================================
# MOCK FIXTURES
# ============================================================================

@pytest.fixture(autouse=True)
def mock_email_service(monkeypatch):
    """Mock email service to prevent actual emails during testing."""
    def mock_send_email(*args, **kwargs):
        return True
    
    monkeypatch.setattr("services.email_service.EmailService.send_otp_email", mock_send_email)


# SMS service mock removed - not currently implemented
# @pytest.fixture(autouse=True)
# def mock_sms_service(monkeypatch):
#     """Mock SMS service to prevent actual SMS during testing."""
#     pass


# ============================================================================
# CLEANUP FIXTURES
# ============================================================================

@pytest.fixture(autouse=True)
def cleanup_uploads():
    """Clean up test uploads after each test."""
    yield
    import shutil
    upload_dir = "/tmp/test_uploads"
    if os.path.exists(upload_dir):
        shutil.rmtree(upload_dir, ignore_errors=True)


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
        from models import OtpCode
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
    data = response.get_json()
    token = data["data"]["accessToken"]
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
    data = response.get_json()
    token = data["data"]["accessToken"]
    return {"Authorization": f"Bearer {token}"}
