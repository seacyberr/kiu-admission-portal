"""Tests for authentication endpoints."""
import pytest


class TestRegister:
    """Test user registration."""

    def test_register_success(self, client):
        """Test successful registration."""
        response = client.post("/api/auth/register", json={
            "email": "newuser@example.com",
            "password": "Secure123!",
            "firstName": "John",
            "lastName": "Doe",
        })
        assert response.status_code == 201
        data = response.get_json()
        assert data["needsVerification"] is True

    def test_register_duplicate_email(self, client, test_user_email, test_user):
        """Test registration with existing email."""
        _ = test_user  # Ensure user exists in database
        response = client.post("/api/auth/register", json={
            "email": test_user_email,
            "password": "Secure123!",
            "firstName": "John",
            "lastName": "Doe",
        })
        assert response.status_code == 409

    def test_register_weak_password(self, client):
        """Test registration with weak password."""
        response = client.post("/api/auth/register", json={
            "email": "weak@example.com",
            "password": "weak",
            "firstName": "John",
            "lastName": "Doe",
        })
        assert response.status_code == 400

    def test_register_missing_fields(self, client):
        """Test registration with missing fields."""
        response = client.post("/api/auth/register", json={
            "email": "test@example.com",
        })
        assert response.status_code == 400


class TestLogin:
    """Test user login."""

    def test_login_success(self, client, verified_user_email, verified_user):
        """Test successful login."""
        _ = verified_user  # Ensure user exists in database
        response = client.post("/api/auth/login", json={
            "email": verified_user_email,
            "password": "TestPass123",
        })
        assert response.status_code == 200
        data = response.get_json()
        assert "accessToken" in data
        assert "refreshToken" in data

    def test_login_wrong_password(self, client, verified_user_email, verified_user):
        """Test login with wrong password."""
        _ = verified_user  # Ensure user exists in database
        response = client.post("/api/auth/login", json={
            "email": verified_user_email,
            "password": "WrongPass123",
        })
        assert response.status_code == 401

    def test_login_unverified(self, client, test_user_email, test_user):
        """Test login with unverified account."""
        _ = test_user  # Ensure user exists in database
        response = client.post("/api/auth/login", json={
            "email": test_user_email,
            "password": "TestPass123",
        })
        assert response.status_code == 403


class TestVerifyOtp:
    """Test OTP verification."""

    def test_verify_otp_success(self, client, test_user_email, test_otp, test_user, app):
        """Test successful OTP verification."""
        _ = test_user  # Ensure user exists in database
        # Get the OTP code within app context to avoid DetachedInstanceError
        with app.app_context():
            from models import OtpCode, User
            user = User.query.filter_by(email=test_user_email).first()
            otp = OtpCode.query.filter_by(user_id=user.id, is_used=False).first()
            otp_code = otp.code
        
        response = client.post("/api/auth/verify-otp", json={
            "email": test_user_email,
            "code": otp_code,
        })
        assert response.status_code == 200
        data = response.get_json()
        assert "token" in data

    def test_verify_otp_invalid(self, client, test_user_email, test_user):
        """Test invalid OTP."""
        _ = test_user  # Ensure user exists in database
        response = client.post("/api/auth/verify-otp", json={
            "email": test_user_email,
            "code": "000000",
        })
        assert response.status_code == 422


class TestRefreshToken:
    """Test token refresh."""

    def test_refresh_success(self, client, verified_user_email, verified_user):
        """Test successful token refresh."""
        _ = verified_user  # Ensure user exists in database
        login_resp = client.post("/api/auth/login", json={
            "email": verified_user_email,
            "password": "TestPass123",
        })
        refresh_token = login_resp.get_json()["refreshToken"]

        response = client.post("/api/auth/refresh", json={
            "refreshToken": refresh_token,
        })
        assert response.status_code == 200
        data = response.get_json()
        assert "accessToken" in data

    def test_refresh_invalid_token(self, client):
        """Test refresh with invalid token."""
        response = client.post("/api/auth/refresh", json={
            "refreshToken": "invalid-token",
        })
        assert response.status_code == 401


class TestLogout:
    """Test logout clears cookie-backed session."""

    def test_logout_clears_session(self, client, verified_user_email, verified_user):
        _ = verified_user
        login_resp = client.post("/api/auth/login", json={
            "email": verified_user_email,
            "password": "TestPass123",
        })
        assert login_resp.status_code == 200
        assert client.get("/api/auth/me").status_code == 200
        out = client.post("/api/auth/logout")
        assert out.status_code == 200
        assert client.get("/api/auth/me").status_code == 401


class TestMe:
    """Test get current user."""

    def test_me_success(self, client, auth_headers):
        """Test getting current user."""
        response = client.get("/api/auth/me", headers=auth_headers)
        assert response.status_code == 200

    def test_me_unauthorized(self, client):
        """Test getting current user without auth."""
        response = client.get("/api/auth/me")
        assert response.status_code == 401
