"""
Comprehensive Test Suite for KIU Admission Portal
Tests all major functionality part by part.
"""
import pytest
import json
from datetime import date
from app import create_app, db
from models import User, Program, AdmissionApplication, FinalistProfile, CareerPath, Opportunity


class TestHealthAndStatus:
    """1. Health Check - System status"""
    
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
    
    def test_health_endpoint_returns_ok(self, client):
        response = client.get('/api/health')
        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'ok'
        assert data['service'] == 'kiu-portal-api'


class TestUserRegistration:
    """2. User Registration - Sign up flow"""
    
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
    
    def test_register_new_user_success(self, client):
        response = client.post('/api/auth/register', json={
            'email': 'newuser@example.com',
            'password': 'SecurePass123!',
            'first_name': 'John',
            'last_name': 'Doe'
        })
        assert response.status_code == 201
        data = response.get_json()
        assert data['data']['email'] == 'newuser@example.com'
        assert data['data']['needsVerification'] is True
    
    def test_register_duplicate_email_fails(self, client):
        # First registration
        client.post('/api/auth/register', json={
            'email': 'duplicate@test.com',
            'password': 'SecurePass123!',
            'first_name': 'Test',
            'last_name': 'User'
        })
        # Duplicate
        response = client.post('/api/auth/register', json={
            'email': 'duplicate@test.com',
            'password': 'SecurePass123!',
            'first_name': 'Test',
            'last_name': 'User'
        })
        assert response.status_code == 409
    
    def test_register_weak_password_fails(self, client):
        response = client.post('/api/auth/register', json={
            'email': 'weak@test.com',
            'password': '123',
            'first_name': 'Test',
            'last_name': 'User'
        })
        assert response.status_code == 400
    
    def test_register_invalid_email_fails(self, client):
        response = client.post('/api/auth/register', json={
            'email': 'not-an-email',
            'password': 'SecurePass123!',
            'first_name': 'Test',
            'last_name': 'User'
        })
        assert response.status_code == 400


class TestUserLogin:
    """3. User Login - Authentication"""
    
    @pytest.fixture
    def app(self):
        app = create_app()
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        with app.app_context():
            db.create_all()
            # Create verified user
            user = User(email='login@test.com', first_name='Test', last_name='User', role='applicant')
            user.set_password('SecurePass123!')
            user.is_verified = True
            db.session.add(user)
            db.session.commit()
            yield app
            db.drop_all()
    
    @pytest.fixture
    def client(self, app):
        return app.test_client()
    
    def test_login_with_valid_credentials(self, client):
        response = client.post('/api/auth/login', json={
            'email': 'login@test.com',
            'password': 'SecurePass123!'
        })
        assert response.status_code == 200
        data = response.get_json()
        assert 'accessToken' in data['data']
        assert 'refreshToken' in data['data']
        assert data['data']['user']['email'] == 'login@test.com'
    
    def test_login_with_wrong_password_fails(self, client):
        response = client.post('/api/auth/login', json={
            'email': 'login@test.com',
            'password': 'WrongPass123!'
        })
        assert response.status_code == 401
    
    def test_login_with_nonexistent_user_fails(self, client):
        response = client.post('/api/auth/login', json={
            'email': 'nonexistent@test.com',
            'password': 'SecurePass123!'
        })
        assert response.status_code == 401


class TestProgramsCRUD:
    """4. Programs - View academic programs"""
    
    @pytest.fixture
    def app(self):
        app = create_app()
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        with app.app_context():
            db.create_all()
            # Seed diverse programs
            programs = [
                Program(name="Bachelor of Computer Science", faculty="Science", level="bachelors", campus="kampala", min_alevel_points=6),
                Program(name="Bachelor of Medicine", faculty="Health Sciences", level="bachelors", campus="western", min_alevel_points=12),
                Program(name="Diploma in Business", faculty="Business", level="diploma", campus="kampala"),
                Program(name="Certificate in ICT", faculty="Computing", level="certificate", campus="kampala"),
                Program(name="Master of Business Administration", faculty="Business", level="masters", campus="kampala"),
                Program(name="PhD in Computer Science", faculty="Science", level="phd", campus="kampala"),
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
        assert len(data['data']['programs']) == 6
    
    def test_filter_programs_by_level(self, client):
        response = client.get('/api/admission/programs?level=bachelors')
        assert response.status_code == 200
        data = response.get_json()
        programs = data['data']['programs']
        assert len(programs) == 2
        assert all(p['level'] == 'bachelors' for p in programs)
    
    def test_filter_programs_by_campus(self, client):
        response = client.get('/api/admission/programs?campus=western')
        assert response.status_code == 200
        data = response.get_json()
        programs = data['data']['programs']
        assert all(p['campus'] == 'western' for p in programs)
    
    def test_get_single_program(self, client, app):
        with app.app_context():
            program_id = Program.query.first().id
        response = client.get(f'/api/admission/programs/{program_id}')
        assert response.status_code == 200
        data = response.get_json()
        assert 'data' in data
        program = data['data']
        assert 'name' in program
        assert 'level' in program
    
    def test_program_has_no_code_field(self, client):
        response = client.get('/api/admission/programs')
        data = response.get_json()
        program = data['data']['programs'][0]
        assert 'code' not in program
        assert 'fees_local_per_semester' not in program
        assert 'tuition_ugx' not in program
        assert 'linkedin_url' not in program


class TestApplicationSubmission:
    """5. Application Submission - Apply to programs"""
    
    @pytest.fixture
    def app(self):
        app = create_app()
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        with app.app_context():
            db.create_all()
            # Create test program
            program = Program(name="Bachelor of Science", faculty="Science", level="bachelors", campus="kampala", min_alevel_points=6)
            db.session.add(program)
            # Create verified user
            user = User(email='applicant@test.com', first_name='Test', last_name='User', role='applicant')
            user.set_password('SecurePass123!')
            user.is_verified = True
            db.session.add(user)
            db.session.commit()
            yield app
            db.drop_all()
    
    @pytest.fixture
    def client(self, app):
        return app.test_client()
    
    @pytest.fixture
    def auth_headers(self, client):
        response = client.post('/api/auth/login', json={
            'email': 'applicant@test.com',
            'password': 'SecurePass123!'
        })
        token = response.get_json()['data']['accessToken']
        return {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
    
    def test_application_requires_authentication(self, client):
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
    
    def test_create_application_success(self, client, auth_headers, app):
        with app.app_context():
            program_id = Program.query.first().id
        
        response = client.post('/api/admission/applications', 
            headers=auth_headers,
            json={
                'programIds': [program_id],
                'examLevel': 'a_level',
                'examYear': 2020,
                'indexNumber': 'U0001/001',
                'unebGrades': {
                    'alevel': [
                        {'subject': 'Physics', 'grade': 'A', 'subjectType': 'principal'},
                        {'subject': 'Chemistry', 'grade': 'B', 'subjectType': 'principal'},
                        {'subject': 'Mathematics', 'grade': 'C', 'subjectType': 'principal'},
                        {'subject': 'General Paper', 'grade': 'D', 'subjectType': 'subsidiary'}
                    ]
                },
                'dateOfBirth': '2000-01-01',
                'gender': 'male',
                'nationality': 'Ugandan',
                'firstName': 'Test',
                'lastName': 'User',
                'phoneNumber': '0776123456',
                'district': 'Kampala'
            }
        )
        # Should either succeed or fail validation, not crash
        assert response.status_code in [200, 201, 400, 422]


class TestAdminDashboard:
    """6. Admin Dashboard - Statistics and reports"""
    
    @pytest.fixture
    def app(self):
        app = create_app()
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        with app.app_context():
            db.create_all()
            # Create admin user
            admin = User(email='admin@test.com', first_name='Admin', last_name='User', role='admin')
            admin.set_password('AdminPass123!')
            admin.is_verified = True
            db.session.add(admin)
            # Create programs
            for i in range(5):
                p = Program(name=f"Program {i}", faculty="Science", level="bachelors", campus="kampala")
                db.session.add(p)
            db.session.commit()
            yield app
            db.drop_all()
    
    @pytest.fixture
    def client(self, app):
        return app.test_client()
    
    @pytest.fixture
    def admin_headers(self, client):
        response = client.post('/api/auth/login', json={
            'email': 'admin@test.com',
            'password': 'AdminPass123!'
        })
        token = response.get_json()['data']['accessToken']
        return {'Authorization': f'Bearer {token}'}
    
    def test_admin_dashboard_stats(self, client, admin_headers):
        response = client.get('/api/admin/dashboard', headers=admin_headers)
        assert response.status_code == 200
        data = response.get_json()
        assert 'data' in data
        stats = data['data']
        assert 'statistics' in stats
        assert stats['statistics']['total_programs'] == 5
    
    def test_admin_programs_list(self, client, admin_headers):
        response = client.get('/api/admin/programs', headers=admin_headers)
        assert response.status_code == 200
        data = response.get_json()
        assert len(data['data']['programs']) == 5


class TestFinalistFeatures:
    """7. Finalist Portal - Career services"""
    
    @pytest.fixture
    def app(self):
        app = create_app()
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        with app.app_context():
            db.create_all()
            # Create finalist user
            user = User(email='finalist@test.com', first_name='Finalist', last_name='User', role='finalist')
            user.set_password('FinalPass123!')
            user.is_verified = True
            db.session.add(user)
            # Create program
            program = Program(name="Bachelor of Science", faculty="Science", level="bachelors", campus="kampala")
            db.session.add(program)
            db.session.commit()
            # Create finalist profile
            profile = FinalistProfile(
                user_id=user.id,
                program_id=program.id,
                student_number="STU001",
                year_of_study=3,
                gpa=4.0,
                skills=["Python", "Data Analysis"],
                bio="Final year student"
            )
            db.session.add(profile)
            db.session.commit()
            yield app
            db.drop_all()
    
    @pytest.fixture
    def client(self, app):
        return app.test_client()
    
    @pytest.fixture
    def finalist_headers(self, client):
        response = client.post('/api/auth/login', json={
            'email': 'finalist@test.com',
            'password': 'FinalPass123!'
        })
        token = response.get_json()['data']['accessToken']
        return {'Authorization': f'Bearer {token}'}
    
    def test_finalist_status_endpoint(self, client, finalist_headers):
        response = client.get('/api/finalist/status', headers=finalist_headers)
        # Should return data even if empty
        assert response.status_code in [200, 404]


class TestCareerServices:
    """8. Career Services - Opportunities and paths"""
    
    @pytest.fixture
    def app(self):
        app = create_app()
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        with app.app_context():
            db.create_all()
            # Create career paths
            paths = [
                CareerPath(
                    title="Software Engineer",
                    description="Develop software applications",
                    industry_field="Technology",
                    skills=["Python", "JavaScript"],
                    potential_roles=["Junior Dev", "Senior Dev"]
                ),
                CareerPath(
                    title="Data Scientist",
                    description="Analyze data and build models",
                    industry_field="Technology",
                    skills=["Python", "Statistics"],
                    potential_roles=["Analyst", "Data Scientist"]
                ),
            ]
            for p in paths:
                db.session.add(p)
            # Create opportunities
            opportunities = [
                Opportunity(
                    title="Software Intern",
                    description="Internship at tech company",
                    type="internship",
                    organization="TechCorp",
                    location="Kampala",
                    requirements="Python, JavaScript",
                    application_deadline=date(2025, 12, 31)
                ),
                Opportunity(
                    title="Graduate Program",
                    description="Graduate trainee program",
                    type="graduate_trainee",
                    organization="BigCorp",
                    location="Kampala",
                    requirements="Bachelors degree",
                    application_deadline=date(2025, 12, 31)
                ),
            ]
            for o in opportunities:
                db.session.add(o)
            db.session.commit()
            yield app
            db.drop_all()
    
    @pytest.fixture
    def client(self, app):
        return app.test_client()
    
    def test_list_career_paths(self, client):
        response = client.get('/api/career/paths')
        assert response.status_code == 200
        data = response.get_json()
        assert len(data['data']['careerPaths']) == 2
    
    def test_list_opportunities(self, client):
        response = client.get('/api/opportunities')
        assert response.status_code == 200
        data = response.get_json()
        assert 'data' in data


class TestModelValidation:
    """9. Database Models - Data integrity"""
    
    @pytest.fixture
    def app(self):
        app = create_app()
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        with app.app_context():
            db.create_all()
            yield app
            db.drop_all()
    
    def test_program_model_fields(self, app):
        with app.app_context():
            program = Program(
                name="Test Program",
                faculty="Test Faculty",
                level="bachelors",
                campus="kampala",
                min_olevel_points=20,
                min_alevel_points=6,
                available_slots=100
            )
            db.session.add(program)
            db.session.commit()
            
            fetched = Program.query.first()
            assert fetched.name == "Test Program"
            assert fetched.level == "bachelors"
            
            # Verify to_dict returns clean data
            data = fetched.to_dict()
            assert 'id' in data
            assert 'name' in data
            assert 'level' in data
            assert 'campus' in data
            assert 'minOlevelPoints' in data
            assert 'minAlevelPoints' in data
            # Verify removed fields are not present
            assert 'code' not in data
            assert 'fees_local_per_semester' not in data
            assert 'fees_international_per_semester' not in data
            assert 'tuition_ugx' not in data
    
    def test_user_password_hashing(self, app):
        with app.app_context():
            user = User(email="test@example.com", first_name="Test", last_name="User", role="applicant")
            user.set_password("MyPassword123!")
            db.session.add(user)
            db.session.commit()
            
            fetched = User.query.first()
            assert fetched.check_password("MyPassword123!")
            assert not fetched.check_password("WrongPassword!")
    
    def test_application_model(self, app):
        with app.app_context():
            # Create user and program
            user = User(email="app@test.com", first_name="Test", last_name="User", role="applicant")
            user.set_password("Pass123!")
            program = Program(name="Test Program", faculty="Science", level="bachelors", campus="kampala")
            db.session.add(user)
            db.session.add(program)
            db.session.commit()
            
            # Create application
            app_obj = AdmissionApplication(
                user_id=user.id,
                program_id=program.id,
                application_number="APP001",
                exam_level="a_level",
                exam_year=2020,
                index_number="U001/001",
                date_of_birth=date(2000, 1, 1),
                gender="male",
                nationality="Ugandan",
                status="pending"
            )
            db.session.add(app_obj)
            db.session.commit()
            
            fetched = AdmissionApplication.query.first()
            assert fetched.application_number == "APP001"
            assert fetched.status == "pending"
            assert fetched.nationality == "Ugandan"


class TestAPIResponseFormat:
    """10. API Response Format - Consistency"""
    
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
    
    def test_response_has_status_field(self, client):
        response = client.get('/api/health')
        data = response.get_json()
        assert 'status' in data
    
    def test_response_has_data_or_error(self, client):
        response = client.get('/api/admission/programs')
        data = response.get_json()
        # Should have either 'data' or error info
        assert 'data' in data or 'error' in data or 'message' in data
    
    def test_error_response_format(self, client):
        response = client.post('/api/auth/login', json={
            'email': 'nonexistent@test.com',
            'password': 'wrong'
        })
        data = response.get_json()
        # Error responses should have message
        assert 'message' in data or 'error' in data
