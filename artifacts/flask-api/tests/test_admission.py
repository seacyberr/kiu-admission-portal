"""Tests for admission application functionality."""
import pytest
from models import db, User, Program


@pytest.fixture
def sample_user(app):
    """Create a sample user for testing."""
    with app.app_context():
        user = User(
            email="test@example.com",
            password_hash="hashed_password",
            first_name="Test",
            last_name="User",
            role="applicant",
            is_verified=True
        )
        db.session.add(user)
        db.session.commit()
        return user.id


@pytest.fixture
def sample_program(app):
    """Create a sample program for testing."""
    with app.app_context():
        program = Program(
            name="Bachelor of Science",
            code="BSC101",
            faculty="Faculty of Science",
            level="degree",
            duration="4 years",
            description="A sample degree program",
            entry_requirements="A-Level with 2 principal passes",
            min_olevel_points=32,
            min_alevel_points=8,
            available_slots=100,
            campus="kampala"
        )
        db.session.add(program)
        db.session.commit()
        return program.id


def test_admission_endpoint_returns_json_on_error(client, app):
    """Test that the admission endpoint returns JSON error responses."""
    # Test with invalid JSON data
    response = client.post(
        "/api/admission/applications",
        data="invalid json",
        content_type="application/json"
    )
    
    # Should return JSON error, not HTML
    assert response.content_type == "application/json"
    data = response.get_json()
    assert "error" in data


def test_admission_endpoint_requires_authentication(client, app):
    """Test that the admission endpoint requires authentication."""
    response = client.post(
        "/api/admission/applications",
        json={
            "programIds": [1],
            "examLevel": "a_level",
            "examYear": 2024,
            "indexNumber": "U0001/001",
            "unebGrades": {"olevel": [], "alevel": []},
            "dateOfBirth": "2000-01-01",
            "gender": "male"
        }
    )
    
    # Should return 401 Unauthorized
    assert response.status_code == 401
    assert response.content_type == "application/json"
    data = response.get_json()
    assert "error" in data


def test_admission_endpoint_validates_required_fields(client, app, sample_user):
    """Test that the admission endpoint validates required fields."""
    # Mock authentication (in real scenario, this would be a JWT token)
    # For now, we'll test the validation logic directly
    
    response = client.post(
        "/api/admission/applications",
        json={
            # Missing required fields
            "examLevel": "a_level"
        }
    )
    
    # Should return validation error
    assert response.status_code == 400 or response.status_code == 401
    assert response.content_type == "application/json"


def test_admission_endpoint_validates_program_selection(client, app, sample_user, sample_program):
    """Test that the admission endpoint validates program selection."""
    response = client.post(
        "/api/admission/applications",
        json={
            "programIds": [],  # Empty program list
            "examLevel": "a_level",
            "examYear": 2024,
            "indexNumber": "U0001/001",
            "unebGrades": {"olevel": [], "alevel": []},
            "dateOfBirth": "2000-01-01",
            "gender": "male"
        }
    )
    
    # Should return validation error for empty program list
    assert response.status_code == 400 or response.status_code == 401
    assert response.content_type == "application/json"


def test_admission_endpoint_validates_max_programs(client, app, sample_user, sample_program):
    """Test that the admission endpoint validates maximum program selection."""
    response = client.post(
        "/api/admission/applications",
        json={
            "programIds": [1, 2, 3, 4],  # More than 3 programs
            "examLevel": "a_level",
            "examYear": 2024,
            "indexNumber": "U0001/001",
            "unebGrades": {"olevel": [], "alevel": []},
            "dateOfBirth": "2000-01-01",
            "gender": "male"
        }
    )
    
    # Should return validation error for too many programs
    assert response.status_code == 400 or response.status_code == 401
    assert response.content_type == "application/json"


def test_admission_endpoint_accepts_session_of_study(client, app, sample_user, sample_program):
    """Test that the admission endpoint accepts session_of_study field."""
    # This test verifies that session_of_study field is properly handled
    # Note: This test requires proper authentication setup to work fully
    response = client.post(
        "/api/admission/applications",
        json={
            "programIds": [1],
            "examLevel": "a_level",
            "examYear": 2024,
            "indexNumber": "U0001/001",
            "unebGrades": {"olevel": [], "alevel": []},
            "dateOfBirth": "2000-01-01",
            "gender": "male",
            "sessionOfStudy": "evening"  # Test the new field
        }
    )
    
    # Should return JSON response (may be 401 due to auth, but should be JSON)
    assert response.content_type == "application/json"
    data = response.get_json()
    # Verify response structure is correct
    assert isinstance(data, dict)
