"""Unit tests for auth and admission routes."""
import pytest
import json
from datetime import datetime, date, timedelta
import os

# Set test environment variables BEFORE importing app
os.environ["JWT_SECRET"] = "test-secret-key-for-testing-only"
os.environ["FLASK_ENV"] = "testing"
os.environ["DATABASE_URL"] = "sqlite:///:memory:"
os.environ["SEED_DATABASE"] = "false"

from app import create_app
from models import db, User, Program, AdmissionApplication, OtpCode


@pytest.fixture
def app():
    """Create test application."""
    import tempfile
    
    # Create a temporary database file for each test
    db_fd, db_path = tempfile.mkstemp(suffix='.db')
    
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()
        db.engine.dispose()
    
    # Clean up temporary database file
    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture(autouse=True)
def cleanup_database(app):
    """Clean up database before each test."""
    with app.app_context():
        # Delete all data from tables
        for table in reversed(db.metadata.sorted_tables):
            db.session.execute(table.delete())
        db.session.commit()
    yield


@pytest.fixture
def client(app):
    """Create test client."""
    return app.test_client()


@pytest.fixture
def sample_user(app):
    """Create a verified applicant user."""
    with app.app_context():
        import uuid
        unique_id = uuid.uuid4().hex[:8]
        unique_email = f"applicant-{unique_id}@test.com"
        user = User(
            email=unique_email,
            first_name="Test",
            last_name="Applicant",
            role="applicant",
            is_verified=True,
        )
        user.set_password("TestPass123!")
        db.session.add(user)
        db.session.commit()
        return {"id": user.id, "email": unique_email}


@pytest.fixture
def sample_program(app):
    """Create a sample program for testing."""
    with app.app_context():
        import uuid
        unique_code = f"TCS{uuid.uuid4().hex[:6].upper()}"
        program = Program(
            name='Test Computer Science',
            code=unique_code,
            faculty='Science',
            level='degree',
            duration='4 years',
            campus='kampala',
            min_olevel_points=20,
            min_alevel_points=6
        )
        db.session.add(program)
        db.session.commit()
        return program.id


@pytest.fixture
def admin_user(app):
    """Create an admin user for testing."""
    with app.app_context():
        user = User(
            email='admin@example.com',
            first_name='Admin',
            last_name='User',
            role='admin',
            is_verified=True
        )
        user.set_password('AdminPass123')
        db.session.add(user)
        db.session.commit()
        return user.id


class TestAuthRoutes:
    """Tests for authentication routes."""
    
    def test_register_success(self, client):
        """Test successful user registration."""
        response = client.post('/api/auth/register', json={
            'email': 'newuser@test.com',
            'password': 'NewPass123!',
            'firstName': 'New',
            'lastName': 'User',
            'role': 'applicant'
        })
        
        assert response.status_code == 201
        data = response.get_json()
        assert data['email'] == 'newuser@test.com'
        assert data['needsVerification'] is True
        assert 'message' in data
    
    def test_register_missing_fields(self, client):
        """Test registration with missing required fields."""
        response = client.post('/api/auth/register', json={
            'email': 'incomplete@test.com',
            'password': 'Test123!'
        })
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
    
    def test_register_invalid_email(self, client):
        """Test registration with invalid email format."""
        response = client.post('/api/auth/register', json={
            'email': 'invalid-email',
            'password': 'Password123',
            'firstName': 'Jane',
            'lastName': 'Smith'
        })
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'Invalid email address' in data['message']
    
    def test_register_weak_password(self, client):
        """Test registration with weak password."""
        response = client.post('/api/auth/register', json={
            'email': 'test@example.com',
            'password': 'weak',  # Too short, no uppercase, no digit
            'firstName': 'Jane',
            'lastName': 'Smith'
        })
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'Password must be at least 8 characters' in data['message']
    
    def test_register_duplicate_email(self, client, sample_user):
        """Test registration with existing email."""
        response = client.post('/api/auth/register', json={
            'email': sample_user['email'],  # Already exists
            'password': 'Password123',
            'firstName': 'Jane',
            'lastName': 'Smith'
        })
        
        assert response.status_code == 409
        data = response.get_json()
        assert 'already exists' in data['message']
    
    def test_login_success(self, client, sample_user):
        """Test successful login."""
        response = client.post('/api/auth/login', json={
            'email': sample_user['email'],
            'password': 'TestPass123!'
        })
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'user' in data
        assert data['user']['email'] == sample_user['email']
        # Token is set as httpOnly cookie
        assert 'Set-Cookie' in response.headers
    
    def test_login_invalid_credentials(self, client, sample_user):
        """Test login with invalid credentials."""
        response = client.post('/api/auth/login', json={
            'email': 'test@example.com',
            'password': 'WrongPassword'
        })
        
        assert response.status_code == 401
        data = response.get_json()
        assert 'Invalid email or password' in data['message']
    
    def test_login_nonexistent_user(self, client):
        """Test login with non-existent user."""
        response = client.post('/api/auth/login', json={
            'email': 'nonexistent@example.com',
            'password': 'Password123'
        })
        
        assert response.status_code == 401
        data = response.get_json()
        assert 'Invalid email or password' in data['message']
    
    def test_verify_otp_success(self, client, app):
        """Test successful OTP verification."""
        # Create a fresh unverified user for this test
        with app.app_context():
            user = User(
                email='verify_otp@example.com',
                first_name='Verify',
                last_name='Test',
                role='applicant',
                is_verified=False
            )
            user.set_password('Password123')
            db.session.add(user)
            db.session.flush()
            
            otp = OtpCode(
                user_id=user.id,
                code='123456',
                expires_at=datetime.utcnow() + timedelta(minutes=10),
                is_used=False
            )
            db.session.add(otp)
            db.session.commit()
        
        response = client.post('/api/auth/verify-otp', json={
            'email': 'verify_otp@example.com',
            'code': '123456'
        })
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'Email verified successfully' in data['message']
    
    def test_verify_otp_invalid_code(self, client, app):
        """Test OTP verification with invalid code."""
        # Create a fresh unverified user
        with app.app_context():
            user = User(
                email='otp_invalid@example.com',
                first_name='OTP',
                last_name='Test',
                role='applicant',
                is_verified=False
            )
            user.set_password('Password123')
            db.session.add(user)
            db.session.commit()
        
        response = client.post('/api/auth/verify-otp', json={
            'email': 'otp_invalid@example.com',
            'code': '000000'  # Invalid code
        })
        
        assert response.status_code == 422
        data = response.get_json()
        assert 'Invalid OTP' in data['error']
    
    def test_verify_otp_expired(self, client, app):
        """Test OTP verification with expired code."""
        # Create a fresh unverified user with expired OTP
        with app.app_context():
            user = User(
                email='otp_expired@example.com',
                first_name='OTP',
                last_name='Test',
                role='applicant',
                is_verified=False
            )
            user.set_password('Password123')
            db.session.add(user)
            db.session.flush()
            
            otp = OtpCode(
                user_id=user.id,
                code='654321',
                expires_at=datetime.utcnow() - timedelta(minutes=1),  # Expired
                is_used=False
            )
            db.session.add(otp)
            db.session.commit()
        
        response = client.post('/api/auth/verify-otp', json={
            'email': 'otp_expired@example.com',
            'code': '654321'
        })
        
        assert response.status_code == 410
        data = response.get_json()
        assert 'OTP expired' in data['error']
    
    def test_me_authenticated(self, client, sample_user):
        """Test /me endpoint with authenticated user."""
        # Login first - cookie is automatically stored in client
        client.post('/api/auth/login', json={
            'email': sample_user['email'],
            'password': 'TestPass123!'
        })
        
        # Access /me - cookie is automatically sent
        response = client.get('/api/auth/me')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['email'] == sample_user['email']
    
    def test_me_unauthenticated(self, client):
        """Test /me endpoint without authentication."""
        response = client.get('/api/auth/me')
        
        assert response.status_code == 401
        data = response.get_json()
        assert 'Unauthorized' in data['error']


class TestAdmissionRoutes:
    """Test admission routes."""
    
    def test_list_programs(self, client, sample_program):
        """Test listing all programs."""
        response = client.get('/api/admission/programs')
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'programs' in data
        assert len(data['programs']) >= 1
    
    def test_list_programs_with_filter(self, client, sample_program):
        """Test listing programs with level filter."""
        response = client.get('/api/admission/programs?level=degree')
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'programs' in data
        # All returned programs should be degree level
        for program in data['programs']:
            assert program['level'] == 'degree'
    
    def test_get_program_success(self, client, sample_program):
        """Test getting a specific program."""
        response = client.get(f'/api/admission/programs/{sample_program}')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['name'] == 'Test Computer Science'
        assert data['code'].startswith('TCS')
    
    def test_get_program_not_found(self, client):
        """Test getting a non-existent program."""
        response = client.get('/api/admission/programs/99999')
        
        assert response.status_code == 404
        data = response.get_json()
        assert 'Program not found' in data['message']
    
    def test_create_application_success(self, client, sample_user, sample_program):
        """Test successful application creation."""
        # Login first - cookie is automatically stored
        client.post('/api/auth/login', json={
            'email': sample_user['email'],
            'password': 'TestPass123!'
        })
        
        # Create application - cookie is automatically sent
        response = client.post('/api/admission/applications', json={
            'programIds': [sample_program],
            'examLevel': 'a_level',
            'examYear': 2023,
            'indexNumber': 'U0001/001',
            'unebGrades': {
                'olevel': [
                    {'subject': 'Mathematics', 'grade': 'D1', 'points': 1},
                    {'subject': 'English', 'grade': 'D2', 'points': 2},
                    {'subject': 'Physics', 'grade': 'D3', 'points': 3},
                    {'subject': 'Chemistry', 'grade': 'D4', 'points': 4},
                    {'subject': 'Biology', 'grade': 'D5', 'points': 5}
                ],
                'alevel': [
                    {'subject': 'Mathematics', 'grade': 'A', 'points': 6, 'subjectType': 'principal'},
                    {'subject': 'Physics', 'grade': 'B', 'points': 5, 'subjectType': 'principal'},
                    {'subject': 'General Paper', 'grade': 'C', 'points': 4, 'subjectType': 'subsidiary'}
                ]
            },
            'dateOfBirth': '2000-01-15',
            'gender': 'male'
        })
        
        assert response.status_code == 201
        data = response.get_json()
        assert 'applicationNumber' in data
        assert data['status'] == 'pending'
    
    def test_create_application_unauthenticated(self, client, sample_program):
        """Test creating application without authentication."""
        response = client.post('/api/admission/applications', json={
            'programIds': [sample_program],
            'examLevel': 'a_level',
            'examYear': 2023,
            'indexNumber': 'U0001/001',
            'unebGrades': {},
            'dateOfBirth': '2000-01-15',
            'gender': 'male'
        })
        
        assert response.status_code == 401
    
    def test_create_application_missing_fields(self, client, sample_user, sample_program):
        """Test creating application with missing required fields."""
        # Login first - cookie is automatically stored
        client.post('/api/auth/login', json={
            'email': sample_user['email'],
            'password': 'TestPass123!'
        })
        
        # Create application - cookie is automatically sent
        response = client.post('/api/admission/applications', json={
            'programIds': [sample_program],
            # Missing examLevel, examYear, indexNumber, etc.
        })
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
    
    def test_create_application_duplicate(self, client, sample_user, sample_program):
        """Test creating duplicate application."""
        # Login first - cookie is automatically stored
        client.post('/api/auth/login', json={
            'email': sample_user['email'],
            'password': 'TestPass123!'
        })
        
        # Create first application with proper grades (2 principal subjects required)
        client.post('/api/admission/applications', json={
            'programIds': [sample_program],
            'examLevel': 'a_level',
            'examYear': 2023,
            'indexNumber': 'U0001/001',
            'unebGrades': {
                'olevel': [
                    {'subject': 'Math', 'grade': 'D1'},
                    {'subject': 'English', 'grade': 'D2'},
                    {'subject': 'Physics', 'grade': 'D3'},
                    {'subject': 'Chemistry', 'grade': 'D4'},
                    {'subject': 'Biology', 'grade': 'D5'}
                ],
                'alevel': [
                    {'subject': 'Math', 'grade': 'A', 'subjectType': 'principal'},
                    {'subject': 'Physics', 'grade': 'B', 'subjectType': 'principal'}
                ]
            },
            'dateOfBirth': '2000-01-15',
            'gender': 'male'
        })
        
        # Try to create second application
        response = client.post('/api/admission/applications', json={
            'programIds': [sample_program],
            'examLevel': 'a_level',
            'examYear': 2023,
            'indexNumber': 'U0001/002',
            'unebGrades': {
                'olevel': [
                    {'subject': 'Math', 'grade': 'D1'},
                    {'subject': 'English', 'grade': 'D2'},
                    {'subject': 'Physics', 'grade': 'D3'},
                    {'subject': 'Chemistry', 'grade': 'D4'},
                    {'subject': 'Biology', 'grade': 'D5'}
                ],
                'alevel': [
                    {'subject': 'Math', 'grade': 'A', 'subjectType': 'principal'},
                    {'subject': 'Physics', 'grade': 'B', 'subjectType': 'principal'}
                ]
            },
            'dateOfBirth': '2000-01-15',
            'gender': 'male'
        })
        
        assert response.status_code == 409
        data = response.get_json()
        assert 'already submitted' in data['message']
    
    def test_get_my_application(self, client, sample_user, sample_program):
        """Test getting user's own application."""
        # Login first - cookie is automatically stored
        client.post('/api/auth/login', json={
            'email': sample_user['email'],
            'password': 'TestPass123!'
        })
        
        # Create application with proper grades (2 principal subjects required)
        client.post('/api/admission/applications', json={
            'programIds': [sample_program],
            'examLevel': 'a_level',
            'examYear': 2023,
            'indexNumber': 'U0001/001',
            'unebGrades': {
                'olevel': [
                    {'subject': 'Math', 'grade': 'D1'},
                    {'subject': 'English', 'grade': 'D2'},
                    {'subject': 'Physics', 'grade': 'D3'},
                    {'subject': 'Chemistry', 'grade': 'D4'},
                    {'subject': 'Biology', 'grade': 'D5'}
                ],
                'alevel': [
                    {'subject': 'Math', 'grade': 'A', 'subjectType': 'principal'},
                    {'subject': 'Physics', 'grade': 'B', 'subjectType': 'principal'}
                ]
            },
            'dateOfBirth': '2000-01-15',
            'gender': 'male'
        })
        
        # Get application
        response = client.get('/api/admission/applications/mine')
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'application' in data
        assert data['application'] is not None
    
    def test_get_my_application_none(self, client, sample_user):
        """Test getting application when none exists."""
        # Login first - cookie is automatically stored
        client.post('/api/auth/login', json={
            'email': sample_user['email'],
            'password': 'TestPass123!'
        })
        
        response = client.get('/api/admission/applications/mine')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['application'] is None
    
    def test_list_applications_admin(self, client, admin_user, sample_user, sample_program):
        """Test listing applications as admin."""
        # Login as admin - cookie is automatically stored
        client.post('/api/auth/login', json={
            'email': 'admin@example.com',
            'password': 'AdminPass123'
        })
        
        response = client.get('/api/admission/applications')
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'applications' in data
        assert 'total' in data
    
    def test_list_applications_non_admin(self, client, sample_user):
        """Test listing applications as non-admin (should fail)."""
        # Login as regular user - cookie is automatically stored
        client.post('/api/auth/login', json={
            'email': sample_user['email'],
            'password': 'TestPass123!'
        })
        
        response = client.get('/api/admission/applications')
        
        assert response.status_code == 403
    
    def test_update_application_status_admin(self, client, admin_user, sample_user, sample_program):
        """Test updating application status as admin."""
        # Login as regular user and create application
        client.post('/api/auth/login', json={
            'email': sample_user['email'],
            'password': 'TestPass123!'
        })
        
        create_response = client.post('/api/admission/applications', json={
            'programIds': [sample_program],
            'examLevel': 'a_level',
            'examYear': 2023,
            'indexNumber': 'U0001/001',
            'unebGrades': {
                'olevel': [
                    {'subject': 'Math', 'grade': 'D1'},
                    {'subject': 'English', 'grade': 'D2'},
                    {'subject': 'Physics', 'grade': 'D3'},
                    {'subject': 'Chemistry', 'grade': 'D4'},
                    {'subject': 'Biology', 'grade': 'D5'}
                ],
                'alevel': [
                    {'subject': 'Math', 'grade': 'A', 'subjectType': 'principal'},
                    {'subject': 'Physics', 'grade': 'B', 'subjectType': 'principal'}
                ]
            },
            'dateOfBirth': '2000-01-15',
            'gender': 'male'
        })
        app_id = create_response.get_json()['id']
        
        # Login as admin and update status - cookie is automatically stored
        client.post('/api/auth/login', json={
            'email': 'admin@example.com',
            'password': 'AdminPass123'
        })
        
        response = client.patch(f'/api/admission/applications/{app_id}/status', json={
            'status': 'accepted',
            'adminNotes': 'Application accepted'
        })
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'accepted'
        assert data['adminNotes'] == 'Application accepted'
