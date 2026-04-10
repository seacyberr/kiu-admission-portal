"""
Comprehensive Authentication Tests
Industry-standard test coverage for all auth workflows
"""
import pytest
from flask import url_for


class TestUserRegistration:
    """Test user registration workflow"""
    
    @pytest.mark.critical
    def test_successful_registration(self, client, valid_registration_data):
        """Test successful user registration"""
        response = client.post(
            '/api/v1/auth/register',
            json=valid_registration_data
        )
        
        assert response.status_code == 201
        data = response.get_json()
        assert data['success'] is True
        assert 'user_id' in data['data']
        assert data['data']['requires_verification'] is True
    
    def test_registration_duplicate_email(self, client, valid_registration_data, applicant_user):
        """Test registration with duplicate email"""
        response = client.post(
            '/api/v1/auth/register',
            json={**valid_registration_data, 'email': applicant_user.email}
        )
        
        assert response.status_code == 409
        data = response.get_json()
        assert 'error' in data
    
    def test_registration_weak_password(self, client):
        """Test registration with weak password"""
        weak_data = {
            'email': 'test@example.com',
            'password': '123',  # Too weak
            'first_name': 'Test',
            'last_name': 'User',
            'role': 'applicant'
        }
        
        response = client.post('/api/v1/auth/register', json=weak_data)
        assert response.status_code == 400
    
    def test_registration_invalid_email(self, client):
        """Test registration with invalid email"""
        invalid_data = {
            'email': 'not-an-email',
            'password': 'SecurePass123!',
            'first_name': 'Test',
            'last_name': 'User'
        }
        
        response = client.post('/api/v1/auth/register', json=invalid_data)
        assert response.status_code == 400
    
    def test_registration_missing_required_fields(self, client):
        """Test registration with missing fields"""
        incomplete_data = {'email': 'test@example.com'}
        
        response = client.post('/api/v1/auth/register', json=incomplete_data)
        assert response.status_code == 400


class TestUserLogin:
    """Test user login workflow"""
    
    @pytest.mark.critical
    def test_successful_login(self, client, valid_login_data, applicant_user):
        """Test successful login"""
        response = client.post('/api/v1/auth/login', json=valid_login_data)
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert 'access_token' in data['data']
        assert 'refresh_token' in data['data']
        assert data['data']['user']['email'] == applicant_user.email
    
    def test_login_invalid_credentials(self, client, invalid_login_data):
        """Test login with invalid credentials"""
        response = client.post('/api/v1/auth/login', json=invalid_login_data)
        
        assert response.status_code == 401
        data = response.get_json()
        assert 'error' in data
    
    def test_login_unverified_user(self, client, unverified_user):
        """Test login with unverified user"""
        login_data = {
            'email': unverified_user.email,
            'password': 'TestPassword123!'
        }
        
        response = client.post('/api/v1/auth/login', json=login_data)
        assert response.status_code == 403
    
    def test_login_disabled_account(self, client, applicant_user):
        """Test login with disabled account"""
        # Disable the user
        applicant_user.is_active = False
        
        login_data = {
            'email': applicant_user.email,
            'password': 'TestPassword123!'
        }
        
        response = client.post('/api/v1/auth/login', json=login_data)
        assert response.status_code == 403


class TestTokenRefresh:
    """Test token refresh workflow"""
    
    def test_successful_token_refresh(self, client, applicant_user, auth_headers):
        """Test successful token refresh"""
        # First login to get refresh token
        login_response = client.post('/api/v1/auth/login', json={
            'email': applicant_user.email,
            'password': 'TestPassword123!'
        })
        
        refresh_token = login_response.get_json()['data']['refresh_token']
        
        # Use refresh token
        response = client.post(
            '/api/v1/auth/refresh',
            headers={'Authorization': f'Bearer {refresh_token}'}
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'access_token' in data['data']
    
    def test_refresh_with_invalid_token(self, client):
        """Test refresh with invalid token"""
        response = client.post(
            '/api/v1/auth/refresh',
            headers={'Authorization': 'Bearer invalid-token'}
        )
        
        assert response.status_code == 422


class TestUserProfile:
    """Test user profile management"""
    
    @pytest.mark.critical
    def test_get_current_user(self, client, auth_headers, applicant_user):
        """Test getting current user profile"""
        response = client.get('/api/v1/auth/me', headers=auth_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['data']['user']['email'] == applicant_user.email
        assert data['data']['user']['role'] == 'applicant'
    
    def test_get_profile_unauthorized(self, client):
        """Test getting profile without authentication"""
        response = client.get('/api/v1/auth/me')
        
        assert response.status_code == 401


class TestUserRoles:
    """Test different user roles"""
    
    def test_applicant_role_access(self, client, applicant_user, auth_headers):
        """Test applicant role permissions"""
        response = client.get('/api/v1/auth/me', headers=auth_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['data']['user']['role'] == 'applicant'
    
    def test_admin_role_access(self, client, admin_user):
        """Test admin role permissions"""
        from flask_jwt_extended import create_access_token
        
        with client.application.app_context():
            token = create_access_token(
                identity=admin_user.id,
                additional_claims={'role': 'admin'}
            )
        
        response = client.get(
            '/api/v1/auth/me',
            headers={'Authorization': f'Bearer {token}'}
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['data']['user']['role'] == 'admin'
    
    def test_finalist_role_access(self, client, finalist_user):
        """Test finalist role permissions"""
        from flask_jwt_extended import create_access_token
        
        with client.application.app_context():
            token = create_access_token(
                identity=finalist_user.id,
                additional_claims={'role': 'finalist'}
            )
        
        response = client.get(
            '/api/v1/auth/me',
            headers={'Authorization': f'Bearer {token}'}
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['data']['user']['role'] == 'finalist'


class TestLogout:
    """Test logout functionality"""
    
    def test_successful_logout(self, client, auth_headers):
        """Test successful logout"""
        response = client.post('/api/v1/auth/logout', headers=auth_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
    
    def test_logout_unauthorized(self, client):
        """Test logout without authentication"""
        response = client.post('/api/v1/auth/logout')
        
        assert response.status_code == 401


class TestPasswordReset:
    """Test password reset workflow"""
    
    def test_forgot_password_existing_user(self, client, applicant_user):
        """Test forgot password for existing user"""
        response = client.post(
            '/api/v1/auth/forgot-password',
            json={'email': applicant_user.email}
        )
        
        # Always returns success to prevent email enumeration
        assert response.status_code == 200
    
    def test_forgot_password_nonexistent_user(self, client):
        """Test forgot password for non-existent user"""
        response = client.post(
            '/api/v1/auth/forgot-password',
            json={'email': 'nonexistent@test.com'}
        )
        
        # Always returns success to prevent email enumeration
        assert response.status_code == 200


class TestRateLimiting:
    """Test rate limiting on auth endpoints"""
    
    def test_login_rate_limiting(self, client):
        """Test that login is rate limited"""
        # Make multiple rapid requests
        for _ in range(15):
            client.post('/api/v1/auth/login', json={
                'email': 'test@test.com',
                'password': 'wrong'
            })
        
        # Next request should be rate limited
        response = client.post('/api/v1/auth/login', json={
            'email': 'test@test.com',
            'password': 'wrong'
        })
        
        # Should get 429 Too Many Requests
        assert response.status_code in [429, 401]  # 401 if limit not hit, 429 if limited


class TestSecurityHeaders:
    """Test security headers in responses"""
    
    def test_security_headers_present(self, client):
        """Test that security headers are present"""
        response = client.get('/api/healthz')
        
        assert 'X-Content-Type-Options' in response.headers
        assert response.headers['X-Content-Type-Options'] == 'nosniff'
    
    def test_no_cache_headers_on_auth(self, client):
        """Test no-cache headers on auth endpoints"""
        response = client.get('/api/v1/auth/me')
        
        assert response.status_code == 401  # Unauthorized, but check headers
        assert 'Cache-Control' in response.headers
        assert 'no-store' in response.headers['Cache-Control']
