"""Tests for health and system endpoints."""
import pytest


class TestHealth:
    """Test health check endpoints."""

    def test_healthz(self, client):
        """Test health check endpoint."""
        response = client.get("/api/healthz")
        assert response.status_code == 200
        data = response.get_json()
        assert data["status"] == "ok"
        assert data["service"] == "kiu-portal-api"

    def test_readyz(self, client):
        """Test readiness check endpoint."""
        response = client.get("/api/readyz")
        assert response.status_code == 200
        data = response.get_json()
        assert data["status"] == "ok"

    def test_not_found(self, client):
        """Test 404 error handler."""
        response = client.get("/api/nonexistent")
        assert response.status_code == 404
        data = response.get_json()
        assert data["error"] == "Not found"

    def test_method_not_allowed(self, client):
        """Test 405 error handler."""
        response = client.delete("/api/healthz")
        assert response.status_code == 405


class TestMetrics:
    """Test metrics endpoint."""

    def test_metrics_endpoint(self, client):
        """Test Prometheus metrics endpoint."""
        response = client.get("/metrics")
        assert response.status_code == 200
        assert b"kiu_http_requests_total" in response.data
