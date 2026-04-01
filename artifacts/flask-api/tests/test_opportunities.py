"""Tests for opportunities endpoints."""
import pytest
from models import db, Opportunity
from datetime import date, timedelta


class TestOpportunities:
    """Test opportunity endpoints."""

    def test_list_opportunities(self, client):
        """Test listing opportunities."""
        response = client.get("/api/opportunities")
        assert response.status_code == 200
        data = response.get_json()
        assert "opportunities" in data

    def test_list_opportunities_with_type_filter(self, client, app):
        """Test listing opportunities with type filter."""
        with app.app_context():
            opp = Opportunity(
                title="Test Job",
                organization="Test Org",
                type="job",
                description="Test description",
                requirements="Test requirements",
                application_deadline=date.today() + timedelta(days=30),
                is_active=True,
            )
            db.session.add(opp)
            db.session.commit()

        response = client.get("/api/opportunities?type=job")
        assert response.status_code == 200

    def test_get_opportunity(self, client, app):
        """Test getting a specific opportunity."""
        with app.app_context():
            opp = Opportunity(
                title="Test Job",
                organization="Test Org",
                type="job",
                description="Test description",
                requirements="Test requirements",
                application_deadline=date.today() + timedelta(days=30),
                is_active=True,
            )
            db.session.add(opp)
            db.session.commit()
            opp_id = opp.id

        response = client.get(f"/api/opportunities/{opp_id}")
        assert response.status_code == 200

    def test_get_opportunity_not_found(self, client):
        """Test getting non-existent opportunity."""
        response = client.get("/api/opportunities/99999")
        assert response.status_code == 404

    def test_create_opportunity_admin(self, client, admin_headers):
        """Test creating opportunity as admin."""
        response = client.post("/api/opportunities", json={
            "title": "New Job",
            "organization": "New Org",
            "type": "job",
            "description": "New description",
            "requirements": "New requirements",
            "applicationDeadline": "2026-12-31",
        }, headers=admin_headers)
        assert response.status_code == 201

    def test_create_opportunity_forbidden(self, client, auth_headers):
        """Test creating opportunity as non-admin."""
        response = client.post("/api/opportunities", json={
            "title": "New Job",
            "organization": "New Org",
            "type": "job",
            "description": "New description",
            "requirements": "New requirements",
            "applicationDeadline": "2026-12-31",
        }, headers=auth_headers)
        assert response.status_code == 403
