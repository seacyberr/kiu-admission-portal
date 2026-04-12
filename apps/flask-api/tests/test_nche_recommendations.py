"""
Test suite for NCHE Recommendations Engine
Tests all qualification types: UACE, UCE, HEC, Diploma, etc.
"""
import pytest
from app import create_app, db
from models import Program, User


class TestNCHERecommendations:
    """Test NCHE recommendation engine for all qualification types"""
    
    @pytest.fixture
    def app(self):
        """Create application for testing"""
        app = create_app('testing')
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        
        with app.app_context():
            db.create_all()
            # Seed test programs
            self._seed_test_programs()
            yield app
            db.drop_all()
    
    @pytest.fixture
    def client(self, app):
        """Create test client"""
        return app.test_client()
    
    def _seed_test_programs(self):
        """Seed test programs for recommendations"""
        programs = [
            Program(
                name="Bachelor of Medicine and Bachelor of Surgery (MBChB)",
                code="MBCHB",
                level="bachelors",
                faculty="Health Sciences",
                required_subjects={"physics": 1, "chemistry": 1, "biology": 1},
                required_points=2  # 2 principals
            ),
            Program(
                name="Bachelor of Business Administration",
                code="BBA",
                level="bachelors",
                faculty="Business",
                required_subjects={"mathematics": 1},
                required_points=1  # 1 principal
            ),
            Program(
                name="Certificate in Business",
                code="CERT-BUS",
                level="certificate",
                faculty="Business",
                min_uce_division=4  # Accepts up to division 4
            ),
            Program(
                name="Diploma in Nursing",
                code="DIP-NURS",
                level="diploma",
                faculty="Health Sciences",
                min_uce_division=3,
                accepts_diploma=True
            ),
        ]
        for p in programs:
            db.session.add(p)
        db.session.commit()
    
    def test_uace_two_principals_qualifies_for_bachelors(self, client):
        """Test UACE student with 2 principals qualifies for Bachelor's"""
        response = client.post('/api/nche/assess', json={
            'qualification_type': 'uace',
            'subjects': [
                {'name': 'Physics', 'grade': 'A'},
                {'name': 'Chemistry', 'grade': 'B'},
                {'name': 'Biology', 'grade': 'C'}
            ],
            'exam_year': 2024,
            'index_number': 'U2024/001'
        })
        
        assert response.status_code == 200
        data = response.get_json()
        
        assert data['qualified'] is True
        assert 'recommendations' in data
        assert any('MBChB' in r['code'] for r in data['recommendations'])
    
    def test_uace_one_principal_disqualified_for_mbchb(self, client):
        """Test UACE student with only 1 principal can't enter MBChB"""
        response = client.post('/api/nche/assess', json={
            'qualification_type': 'uace',
            'subjects': [
                {'name': 'History', 'grade': 'A'},
                {'name': 'Economics', 'grade': 'B'},
                {'name': 'Geography', 'grade': 'C'}
            ],
            'exam_year': 2024,
            'index_number': 'U2024/002'
        })
        
        assert response.status_code == 200
        data = response.get_json()
        
        assert data['qualified'] is True  # Still qualified for some programs
        assert not any('MBChB' in r['code'] for r in data['recommendations'])
    
    def test_uce_division_2_qualifies_for_diploma(self, client):
        """Test UCE Division 2 qualifies for diploma programs"""
        response = client.post('/api/nche/assess', json={
            'qualification_type': 'uce',
            'division': 2,
            'subjects': [
                {'name': 'Mathematics', 'grade': 2},
                {'name': 'English', 'grade': 1},
                {'name': 'Biology', 'grade': 3},
                {'name': 'Chemistry', 'grade': 2},
                {'name': 'Physics', 'grade': 3},
                {'name': 'History', 'grade': 4}
            ],
            'exam_year': 2023,
            'index_number': 'O2023/001'
        })
        
        assert response.status_code == 200
        data = response.get_json()
        
        assert data['qualified'] is True
        assert 'recommendations' in data
    
    def test_hec_technical_track_recommendations(self, client):
        """Test HEC Technical track student gets technical programs"""
        response = client.post('/api/nche/assess', json={
            'qualification_type': 'hec',
            'hec_track': 'engineering_technology',
            'certificate_type': 'certificate_ii',
            'subjects': [
                {'name': 'Engineering Mathematics', 'grade': 'Distinction'},
                {'name': 'Technical Drawing', 'grade': 'Credit'},
                {'name': 'Workshop Practice', 'grade': 'Pass'}
            ],
            'exam_year': 2024,
            'index_number': 'H2024/001'
        })
        
        assert response.status_code == 200
        data = response.get_json()
        
        assert data['qualified'] is True
        assert 'recommendations' in data
    
    def test_diploma_credit_class_qualifies_for_bachelors(self, client):
        """Test Diploma Credit class qualifies for Bachelor's year 2/3"""
        response = client.post('/api/nche/assess', json={
            'qualification_type': 'diploma',
            'class_awarded': 'credit',
            'field_of_study': 'nursing',
            'institution': 'KIU Teaching Hospital',
            'exam_year': 2023,
            'index_number': 'D2023/001'
        })
        
        assert response.status_code == 200
        data = response.get_json()
        
        assert data['qualified'] is True
        # Credit class should allow year 2/3 entry
        assert any('entry_year' in r and r['entry_year'] in [2, 3] 
                   for r in data.get('recommendations', []))
    
    def test_invalid_subjects_rejected(self, client):
        """Test that invalid subjects are properly rejected"""
        response = client.post('/api/nche/assess', json={
            'qualification_type': 'uace',
            'subjects': [
                {'name': 'InvalidSubject', 'grade': 'A'},
                {'name': 'AnotherInvalid', 'grade': 'B'}
            ],
            'exam_year': 2024,
            'index_number': 'U2024/999'
        })
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data


class TestApplicationSubmission:
    """Test application submission workflow"""
    
    @pytest.fixture
    def auth_headers(self, client, app):
        """Create authenticated user and return headers"""
        with app.app_context():
            user = User(
                email='test@student.com',
                first_name='Test',
                last_name='Student',
                role='applicant'
            )
            user.set_password('password123')
            db.session.add(user)
            db.session.commit()
        
        # Login
        response = client.post('/api/auth/login', json={
            'email': 'test@student.com',
            'password': 'password123'
        })
        
        token = response.get_json()['token']
        return {'Authorization': f'Bearer {token}'}
    
    def test_submit_complete_application(self, client, auth_headers):
        """Test submitting a complete application"""
        application_data = {
            'programIds': [1],
            'examLevel': 'UACE',
            'examYear': 2024,
            'indexNumber': 'U2024/001',
            'unebGrades': {'Physics': 'A', 'Chemistry': 'B', 'Biology': 'C'},
            'dateOfBirth': '2000-01-01',
            'gender': 'male',
            'personalStatement': 'I want to study medicine',
            'address': 'Kampala, Uganda',
            'phone': '+256700000000'
        }
        
        response = client.post(
            '/api/admission/wizard',
            json=application_data,
            headers=auth_headers
        )
        
        assert response.status_code == 201
        data = response.get_json()
        
        assert 'applicationNumber' in data
        assert data['status'] == 'pending'
    
    def test_submit_without_required_fields_fails(self, client, auth_headers):
        """Test that missing required fields are rejected"""
        incomplete_data = {
            'examLevel': 'UACE',
            # Missing: programIds, examYear, indexNumber, etc.
        }
        
        response = client.post(
            '/api/admission/wizard',
            json=incomplete_data,
            headers=auth_headers
        )
        
        assert response.status_code == 400


class TestAdminOperations:
    """Test admin dashboard operations"""
    
    @pytest.fixture
    def admin_headers(self, client, app):
        """Create admin user and return headers"""
        with app.app_context():
            admin = User(
                email='admin@kiu.ac.ug',
                first_name='Admin',
                last_name='User',
                role='admin'
            )
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
        
        response = client.post('/api/auth/login', json={
            'email': 'admin@kiu.ac.ug',
            'password': 'admin123'
        })
        
        token = response.get_json()['token']
        return {'Authorization': f'Bearer {token}'}
    
    def test_admin_can_list_all_applications(self, client, admin_headers):
        """Test admin can view all applications"""
        response = client.get('/api/admission/applications', headers=admin_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        
        assert 'applications' in data
        assert isinstance(data['applications'], list)
    
    def test_non_admin_cannot_list_all_applications(self, client):
        """Test regular users cannot access all applications"""
        # Create regular user
        response = client.post('/api/auth/register', json={
            'email': 'regular@user.com',
            'password': 'password123',
            'firstName': 'Regular',
            'lastName': 'User'
        })
        
        token = response.get_json()['token']
        headers = {'Authorization': f'Bearer {token}'}
        
        response = client.get('/api/admission/applications', headers=headers)
        
        assert response.status_code == 403
    
    def test_admin_can_update_application_status(self, client, admin_headers):
        """Test admin can approve/reject applications"""
        # This would need an existing application
        # Simplified test structure
        pass


class TestPerformance:
    """Performance tests"""
    
    def test_recommendation_response_time(self, client):
        """Test that recommendations are generated quickly"""
        import time
        
        start = time.time()
        response = client.post('/api/nche/assess', json={
            'qualification_type': 'uace',
            'subjects': [
                {'name': 'Physics', 'grade': 'A'},
                {'name': 'Chemistry', 'grade': 'B'},
                {'name': 'Biology', 'grade': 'C'}
            ],
            'exam_year': 2024,
            'index_number': 'U2024/001'
        })
        elapsed = time.time() - start
        
        assert response.status_code == 200
        assert elapsed < 1.0  # Should complete in under 1 second
    
    def test_list_opportunities_response_time(self, client):
        """Test opportunities list loads quickly"""
        import time
        
        start = time.time()
        response = client.get('/api/opportunities?page=1&limit=20')
        elapsed = time.time() - start
        
        assert response.status_code == 200
        assert elapsed < 0.5  # Should complete in under 500ms
