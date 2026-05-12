"""
Core Functionality Tests for KIU Admission Portal
Clean test suite covering essential features only.
"""
import pytest
from app import create_app, db
from models import User, Program, AdmissionApplication


class TestHealth:
    """Health check endpoint"""
    
    @pytest.fixture
    def app(self):
        app = create_app()
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        with app.app_context():
            db.create_all()
            yield app
            db.drop_all()
    
    @pytest.fixture
    def client(self, app):
        return app.test_client()
    
    def test_health_check(self, client):
        response = client.get('/api/health')
        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'ok'
        assert data['service'] == 'kiu-portal-api'


class TestAuth:
    """Authentication flows"""
    
    @pytest.fixture
    def app(self):
        app = create_app()
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        with app.app_context():
            db.create_all()
            yield app
            db.drop_all()
    
    @pytest.fixture
    def client(self, app):
        return app.test_client()
    
    def test_register_success(self, client):
        response = client.post('/api/auth/register', json={
            'email': 'test@example.com',
            'password': 'SecurePass123!',
            'first_name': 'Test',
            'last_name': 'User'
        })
        assert response.status_code == 201
        data = response.get_json()
        assert data['data']['email'] == 'test@example.com'
        assert data['data']['needsVerification'] is True
    
    def test_register_duplicate_email(self, client):
        # First registration
        client.post('/api/auth/register', json={
            'email': 'duplicate@example.com',
            'password': 'SecurePass123!',
            'first_name': 'Test',
            'last_name': 'User'
        })
        # Duplicate attempt
        response = client.post('/api/auth/register', json={
            'email': 'duplicate@example.com',
            'password': 'SecurePass123!',
            'first_name': 'Test',
            'last_name': 'User'
        })
        assert response.status_code == 409
    
    def test_login_success(self, client, app):
        # Create verified user
        with app.app_context():
            user = User(email='login@test.com', first_name='Test', last_name='User', role='applicant')
            user.set_password('SecurePass123!')
            user.is_verified = True
            db.session.add(user)
            db.session.commit()
        
        response = client.post('/api/auth/login', json={
            'email': 'login@test.com',
            'password': 'SecurePass123!'
        })
        assert response.status_code == 200
        data = response.get_json()
        assert 'accessToken' in data['data']
    
    def test_login_invalid_credentials(self, client):
        response = client.post('/api/auth/login', json={
            'email': 'nonexistent@example.com',
            'password': 'WrongPass123!'
        })
        assert response.status_code == 401


class TestPrograms:
    """Program listing and retrieval"""
    
    @pytest.fixture
    def app(self):
        app = create_app()
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        with app.app_context():
            db.create_all()
            # Seed test programs
            programs = [
                Program(name="Bachelor of Computer Science", faculty="Science", level="bachelors", campus="kampala"),
                Program(name="Diploma in Business", faculty="Business", level="diploma", campus="kampala"),
                Program(name="Certificate in ICT", faculty="Computing", level="certificate", campus="kampala"),
            ]
            for p in programs:
                db.session.add(p)
            db.session.commit()
            yield app
            db.drop_all()
    
    @pytest.fixture
    def client(self, app):
        return app.test_client()
    
    def test_list_all_programs(self, client):
        response = client.get('/api/admission/programs')
        assert response.status_code == 200
        data = response.get_json()
        assert len(data['data']['programs']) == 3
    
    def test_list_programs_by_level(self, client):
        response = client.get('/api/admission/programs?level=bachelors')
        assert response.status_code == 200
        data = response.get_json()
        programs = data['data']['programs']
        assert len(programs) == 1
        assert programs[0]['name'] == "Bachelor of Computer Science"
    
    def test_program_has_no_code_field(self, client):
        response = client.get('/api/admission/programs')
        data = response.get_json()
        program = data['data']['programs'][0]
        assert 'code' not in program
        assert 'tuition' not in program
        assert 'fees' not in program


class TestApplications:
    """Application submission flow"""
    
    @pytest.fixture
    def app(self):
        app = create_app()
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        with app.app_context():
            db.create_all()
            # Create test program
            program = Program(name="Bachelor of Science", faculty="Science", level="bachelors", campus="kampala")
            db.session.add(program)
            db.session.commit()
            yield app
            db.drop_all()
    
    @pytest.fixture
    def client(self, app):
        return app.test_client()
    
    @pytest.fixture
    def auth_client(self, client, app):
        """Create verified user and return authenticated client"""
        with app.app_context():
            user = User(email='applicant@test.com', first_name='Test', last_name='User', role='applicant')
            user.set_password('SecurePass123!')
            user.is_verified = True
            db.session.add(user)
            db.session.commit()
        
        # Login to get token
        response = client.post('/api/auth/login', json={
            'email': 'applicant@test.com',
            'password': 'SecurePass123!'
        })
        token = response.get_json()['data']['access_token']
        
        class AuthClient:
            def __init__(self, client, token):
                self.client = client
                self.token = token
            
            def post(self, path, **kwargs):
                headers = kwargs.pop('headers', {})
                headers['Authorization'] = f'Bearer {self.token}'
                return self.client.post(path, headers=headers, **kwargs)
            
            def get(self, path, **kwargs):
                headers = kwargs.pop('headers', {})
                headers['Authorization'] = f'Bearer {self.token}'
                return self.client.get(path, headers=headers, **kwargs)
        
        return AuthClient(client, token)
    
    def test_create_application_requires_auth(self, client):
        response = client.post('/api/admission/applications', json={
            'programIds': [1],
            'examLevel': 'a_level',
            'examYear': 2020,
            'indexNumber': 'U0001/001',
            'unebGrades': {'alevel': [{'subject': 'Physics', 'grade': 'A', 'subjectType': 'principal'}]},
            'dateOfBirth': '2000-01-01',
            'gender': 'male',
            'nationality': 'Ugandan'
        })
        assert response.status_code == 401


class TestModels:
    """Database model validation"""
    
    @pytest.fixture
    def app(self):
        app = create_app()
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        with app.app_context():
            db.create_all()
            yield app
            db.drop_all()
    
    def test_program_creation(self, app):
        with app.app_context():
            program = Program(
                name="Test Program",
                faculty="Test Faculty",
                level="bachelors",
                campus="kampala"
            )
            db.session.add(program)
            db.session.commit()
            
            # Verify program was created
            fetched = Program.query.first()
            assert fetched.name == "Test Program"
            assert fetched.level == "bachelors"
            
            # Verify to_dict output
            data = fetched.to_dict()
            assert 'id' in data
            assert 'name' in data
            assert 'code' not in data  # Should not have code field
            assert 'fees_local_per_semester' not in data  # Should not have fees
    
    def test_user_creation(self, app):
        with app.app_context():
            user = User(email="user@test.com", first_name="Test", last_name="User", role="applicant")
            user.set_password("TestPass123!")
            db.session.add(user)
            db.session.commit()
            
            fetched = User.query.first()
            assert fetched.email == "user@test.com"
            assert fetched.check_password("TestPass123!")
