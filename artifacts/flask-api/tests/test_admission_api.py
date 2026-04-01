"""Tests for admission application API endpoint."""
import pytest
import json
from models import db, User, Program


@pytest.fixture
def test_user(app):
    """Create a test user for admission tests."""
    with app.app_context():
        user = User(
            email="applicant@test.com",
            first_name="Test",
            last_name="Applicant",
            role="applicant",
            is_verified=True
        )
        user.set_password("testpass123")
        db.session.add(user)
        db.session.commit()
        return user.id


@pytest.fixture
def degree_program(app):
    """Create a degree program for testing."""
    with app.app_context():
        program = Program(
            name="Bachelor of Science in Computer Science",
            code="BSCS",
            faculty="Faculty of Science",
            level="degree",
            duration="4 years",
            description="Computer Science degree program",
            entry_requirements="A-Level with 2 principal passes",
            min_olevel_points=32,
            min_alevel_points=8,
            available_slots=100,
            campus="kampala"
        )
        db.session.add(program)
        db.session.commit()
        return program.id


def test_al_level_degree_old_curriculum_application(client, test_user, degree_program):
    """Test A-Level degree application with old curriculum."""
    # Login to get JWT token
    login_response = client.post("/api/auth/login", json={
        "email": "applicant@test.com",
        "password": "testpass123"
    })
    assert login_response.status_code == 200
    token = login_response.get_json()["accessToken"]

    # Submit A-Level degree application with old curriculum
    response = client.post(
        "/api/admission/applications",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "programIds": [degree_program],
            "examLevel": "a_level",
            "examYear": 2020,
            "indexNumber": "U0001/001",
            "unebGrades": {
                "olevel": [
                    {"subject": "Mathematics", "grade": "D1", "points": 1},
                    {"subject": "English Language", "grade": "D2", "points": 2},
                    {"subject": "Physics", "grade": "C3", "points": 3},
                    {"subject": "Chemistry", "grade": "C4", "points": 4},
                    {"subject": "Biology", "grade": "C5", "points": 5}
                ],
                "alevel": [
                    {"subject": "Mathematics", "grade": "A", "points": 6, "subjectType": "principal"},
                    {"subject": "Physics", "grade": "B", "points": 5, "subjectType": "principal"},
                    {"subject": "General Paper", "grade": "C", "points": 4, "subjectType": "subsidiary"}
                ]
            },
            "dateOfBirth": "2000-04-04",
            "gender": "male",
            "nationality": "Ugandan",
            "district": "Kampala",
            "nextOfKinName": "John Doe",
            "nextOfKinPhone": "0701240315",
            "nextOfKinRelationship": "Father"
        }
    )

    assert response.status_code == 201
    data = response.get_json()
    assert data["examLevel"] == "a_level"
    assert data["status"] == "pending"


def test_al_level_degree_new_curriculum_application(client, test_user, degree_program):
    """Test A-Level degree application with new curriculum."""
    # Login to get JWT token
    login_response = client.post("/api/auth/login", json={
        "email": "applicant@test.com",
        "password": "testpass123"
    })
    assert login_response.status_code == 200
    token = login_response.get_json()["accessToken"]

    # Submit A-Level degree application with new curriculum
    response = client.post(
        "/api/admission/applications",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "programIds": [degree_program],
            "examLevel": "a_level",
            "examYear": 2020,
            "indexNumber": "U0001/002",
            "unebGrades": {
                "olevel": [
                    {"subject": "Mathematics", "grade": "D1", "points": 1},
                    {"subject": "English Language", "grade": "D2", "points": 2},
                    {"subject": "Physics", "grade": "D3", "points": 3},
                    {"subject": "Chemistry", "grade": "D4", "points": 4},
                    {"subject": "Biology", "grade": "D5", "points": 5}
                ],
                "alevel": [
                    {"subject": "Mathematics", "grade": "A", "points": 6, "subjectType": "principal"},
                    {"subject": "Physics", "grade": "B", "points": 5, "subjectType": "principal"},
                    {"subject": "General Paper", "grade": "C", "points": 4, "subjectType": "subsidiary"}
                ]
            },
            "dateOfBirth": "1999-05-15",
            "gender": "female",
            "nationality": "Ugandan",
            "district": "Wakiso",
            "nextOfKinName": "Jane Doe",
            "nextOfKinPhone": "0701240316",
            "nextOfKinRelationship": "Mother"
        }
    )

    assert response.status_code == 201
    data = response.get_json()
    assert data["examLevel"] == "a_level"
    assert data["status"] == "pending"


def test_invalid_date_format_rejected(client, test_user, degree_program):
    """Test that invalid date format is properly rejected."""
    # Login to get JWT token
    login_response = client.post("/api/auth/login", json={
        "email": "applicant@test.com",
        "password": "testpass123"
    })
    assert login_response.status_code == 200
    token = login_response.get_json()["accessToken"]

    # Submit application with invalid date format
    response = client.post(
        "/api/admission/applications",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "programIds": [degree_program],
            "examLevel": "a_level",
            "examYear": 2020,
            "indexNumber": "U0001/003",
            "unebGrades": {
                "olevel": [
                    {"subject": "Mathematics", "grade": "D1", "points": 1},
                    {"subject": "English Language", "grade": "D2", "points": 2},
                    {"subject": "Physics", "grade": "C3", "points": 3},
                    {"subject": "Chemistry", "grade": "C4", "points": 4},
                    {"subject": "Biology", "grade": "C5", "points": 5}
                ],
                "alevel": [
                    {"subject": "Mathematics", "grade": "A", "points": 6, "subjectType": "principal"},
                    {"subject": "Physics", "grade": "B", "points": 5, "subjectType": "principal"},
                    {"subject": "General Paper", "grade": "C", "points": 4, "subjectType": "subsidiary"}
                ]
            },
            "dateOfBirth": "04/04/2000",  # Invalid format - should be YYYY-MM-DD
            "gender": "male",
            "nationality": "Ugandan",
            "district": "Kampala",
            "nextOfKinName": "John Doe",
            "nextOfKinPhone": "0701240315",
            "nextOfKinRelationship": "Father"
        }
    )

    assert response.status_code == 400
    data = response.get_json()
    assert "error" in data
    assert "Invalid dateOfBirth format" in data["message"]


def test_o_level_degree_rejected(client, test_user):
    """Test that O-Level only is rejected for degree programs."""
    # Create a degree program for testing
    with client.application.app_context():
        degree_program = Program(
            name="Bachelor of Business Administration",
            code="BBA",
            faculty="Faculty of Business",
            level="degree",
            duration="3 years",
            description="Business administration degree program",
            entry_requirements="A-Level with 2 principal passes",
            min_olevel_points=32,
            min_alevel_points=8,
            available_slots=100,
            campus="kampala"
        )
        db.session.add(degree_program)
        db.session.commit()
        degree_program_id = degree_program.id

    # Login to get JWT token
    login_response = client.post("/api/auth/login", json={
        "email": "applicant@test.com",
        "password": "testpass123"
    })
    assert login_response.status_code == 200
    token = login_response.get_json()["accessToken"]

    # Try to submit degree application with O-Level only - should be rejected
    response = client.post(
        "/api/admission/applications",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "programIds": [degree_program_id],  # This is a degree program
            "examLevel": "o_level",  # O-Level only - should be rejected for degree
            "examYear": 2020,
            "indexNumber": "U0001/004",
            "unebGrades": {
                "olevel": [
                    {"subject": "Mathematics", "grade": "D1", "points": 1},
                    {"subject": "English Language", "grade": "D2", "points": 2},
                    {"subject": "Physics", "grade": "C3", "points": 3},
                    {"subject": "Chemistry", "grade": "C4", "points": 4},
                    {"subject": "Biology", "grade": "C5", "points": 5}
                ]
            },
            "dateOfBirth": "1999-06-20",
            "gender": "male",
            "nationality": "Ugandan",
            "district": "Kampala",
            "nextOfKinName": "John Doe",
            "nextOfKinPhone": "0701240315",
            "nextOfKinRelationship": "Father"
        }
    )

    # Should be rejected because O-Level is not sufficient for degree programs
    assert response.status_code == 422
    data = response.get_json()
    assert "error" in data
    assert "O-Level alone is not accepted" in data["message"]
