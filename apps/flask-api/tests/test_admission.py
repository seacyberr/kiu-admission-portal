"""Tests for admission endpoints."""
import pytest
from models import db, Program


class TestPrograms:
    """Test program endpoints."""

    def test_list_programs(self, client, app):
        """Test listing programs."""
        # Create a test program first
        with app.app_context():
            prog = Program(name="Test", code="TST", faculty="Test", level="degree", campus="kampala")
            db.session.add(prog)
            db.session.commit()

        response = client.get("/api/admission/programs")
        assert response.status_code == 200
        data = response.get_json()
        assert "programs" in data

    def test_list_programs_with_filter(self, client, app):
        """Test listing programs with level filter."""
        with app.app_context():
            prog = Program(name="Test", code="TST", faculty="Test", level="degree", campus="kampala")
            db.session.add(prog)
            db.session.commit()

        response = client.get("/api/admission/programs?level=degree")
        assert response.status_code == 200

    def test_get_program(self, client, app):
        """Test getting a specific program."""
        with app.app_context():
            prog = Program(name="Test", code="TST", faculty="Test", level="degree", campus="kampala")
            db.session.add(prog)
            db.session.commit()
            prog_id = prog.id

        response = client.get(f"/api/admission/programs/{prog_id}")
        assert response.status_code == 200

    def test_get_program_not_found(self, client):
        """Test getting non-existent program."""
        response = client.get("/api/admission/programs/99999")
        assert response.status_code == 404


class TestApplications:
    """Test application endpoints."""

    def test_create_application_unauthorized(self, client):
        """Test creating application without auth."""
        response = client.post("/api/admission/applications", json={
            "programIds": [1],
            "examLevel": "a_level",
        })
        assert response.status_code == 401

    def test_get_my_application_empty(self, client, auth_headers):
        """Test getting application when none exists."""
        response = client.get("/api/admission/applications/mine", headers=auth_headers)
        assert response.status_code == 200
        data = response.get_json()
        assert data["application"] is None

    def test_list_applications_admin(self, client, admin_headers):
        """Test listing applications as admin."""
        response = client.get("/api/admission/applications", headers=admin_headers)
        assert response.status_code == 200
        data = response.get_json()
        assert "applications" in data

    def test_list_applications_forbidden(self, client, auth_headers):
        """Test listing applications as non-admin."""
        response = client.get("/api/admission/applications", headers=auth_headers)
        assert response.status_code == 403

    def test_analytics_admin(self, client, admin_headers):
        """Test getting analytics as admin."""
        response = client.get("/api/admission/analytics", headers=admin_headers)
        assert response.status_code == 200
        data = response.get_json()
        assert "total" in data
