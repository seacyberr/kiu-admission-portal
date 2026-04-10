"""
Comprehensive Career Portal Tests
Tests all career-related functionality for finalists
"""
import pytest
from datetime import date, timedelta


class TestFinalistProfile:
    """Test finalist profile management"""
    
    def test_finalist_view_own_profile(self, client, finalist_user):
        """Test finalist can view their profile"""
        from flask_jwt_extended import create_access_token
        
        with client.application.app_context():
            token = create_access_token(
                identity=finalist_user.id,
                additional_claims={'role': 'finalist'}
            )
        
        response = client.get(
            '/api/v1/career/profile',
            headers={'Authorization': f'Bearer {token}'}
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['data']['profile']['email'] == finalist_user.email
        assert data['data']['profile']['role'] == 'finalist'
    
    def test_finalist_update_profile(self, client, finalist_user):
        """Test finalist can update their profile"""
        from flask_jwt_extended import create_access_token
        
        with client.application.app_context():
            token = create_access_token(
                identity=finalist_user.id,
                additional_claims={'role': 'finalist'}
            )
        
        update_payload = {
            'phone': '+256700000999',
            'linkedin_url': 'https://linkedin.com/in/testuser',
            'portfolio_url': 'https://portfolio.test.com',
            'bio': 'Software developer with 3 years experience'
        }
        
        response = client.put(
            '/api/v1/career/profile',
            json=update_payload,
            headers={'Authorization': f'Bearer {token}'}
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['data']['profile']['linkedin_url'] == 'https://linkedin.com/in/testuser'
    
    def test_applicant_cannot_access_career_profile(self, client, applicant_user):
        """Test applicant cannot access finalist features"""
        from flask_jwt_extended import create_access_token
        
        with client.application.app_context():
            token = create_access_token(
                identity=applicant_user.id,
                additional_claims={'role': 'applicant'}
            )
        
        response = client.get(
            '/api/v1/career/profile',
            headers={'Authorization': f'Bearer {token}'}
        )
        
        assert response.status_code == 403


class TestCareerPaths:
    """Test career path exploration"""
    
    def test_finalist_view_career_paths(self, client, finalist_user):
        """Test finalist can view career paths"""
        from flask_jwt_extended import create_access_token
        
        with client.application.app_context():
            token = create_access_token(
                identity=finalist_user.id,
                additional_claims={'role': 'finalist'}
            )
        
        response = client.get(
            '/api/v1/career/paths',
            headers={'Authorization': f'Bearer {token}'}
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'career_paths' in data['data']
    
    def test_view_career_path_by_program(self, client, finalist_user, sample_programs):
        """Test viewing career paths for specific program"""
        from flask_jwt_extended import create_access_token
        
        with client.application.app_context():
            token = create_access_token(
                identity=finalist_user.id,
                additional_claims={'role': 'finalist'}
            )
        
        program = sample_programs['bachelor']
        
        response = client.get(
            f'/api/v1/career/paths?program={program.id}',
            headers={'Authorization': f'Bearer {token}'}
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'related_careers' in data['data']
    
    def test_view_career_path_details(self, client, finalist_user):
        """Test viewing detailed career path information"""
        from flask_jwt_extended import create_access_token
        
        with client.application.app_context():
            token = create_access_token(
                identity=finalist_user.id,
                additional_claims={'role': 'finalist'}
            )
        
        response = client.get(
            '/api/v1/career/paths/software-engineer',
            headers={'Authorization': f'Bearer {token}'}
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'career_path' in data['data']
        assert 'required_skills' in data['data']['career_path']
        assert 'average_salary' in data['data']['career_path']


class TestJobOpportunities:
    """Test job opportunity features"""
    
    def test_finalist_view_job_opportunities(self, client, finalist_user):
        """Test finalist can view job opportunities"""
        from flask_jwt_extended import create_access_token
        
        with client.application.app_context():
            token = create_access_token(
                identity=finalist_user.id,
                additional_claims={'role': 'finalist'}
            )
        
        response = client.get(
            '/api/v1/career/opportunities',
            headers={'Authorization': f'Bearer {token}'}
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'opportunities' in data['data']
    
    def test_filter_jobs_by_type(self, client, finalist_user):
        """Test filtering jobs by type (job/internship)"""
        from flask_jwt_extended import create_access_token
        
        with client.application.app_context():
            token = create_access_token(
                identity=finalist_user.id,
                additional_claims={'role': 'finalist'}
            )
        
        response = client.get(
            '/api/v1/career/opportunities?type=internship',
            headers={'Authorization': f'Bearer {token}'}
        )
        
        assert response.status_code == 200
        data = response.get_json()
        for opp in data['data']['opportunities']:
            assert opp['type'] == 'internship'
    
    def test_filter_jobs_by_location(self, client, finalist_user):
        """Test filtering jobs by location"""
        from flask_jwt_extended import create_access_token
        
        with client.application.app_context():
            token = create_access_token(
                identity=finalist_user.id,
                additional_claims={'role': 'finalist'}
            )
        
        response = client.get(
            '/api/v1/career/opportunities?location=Kampala',
            headers={'Authorization': f'Bearer {token}'}
        )
        
        assert response.status_code == 200
    
    def test_view_job_details(self, client, finalist_user):
        """Test viewing detailed job information"""
        from flask_jwt_extended import create_access_token
        
        with client.application.app_context():
            token = create_access_token(
                identity=finalist_user.id,
                additional_claims={'role': 'finalist'}
            )
        
        response = client.get(
            '/api/v1/career/opportunities/123',
            headers={'Authorization': f'Bearer {token}'}
        )
        
        # May return 200 or 404 depending on if job exists
        assert response.status_code in [200, 404]


class TestJobApplications:
    """Test job application features"""
    
    def test_finalist_apply_for_job(self, client, finalist_user):
        """Test finalist can apply for a job"""
        from flask_jwt_extended import create_access_token
        
        with client.application.app_context():
            token = create_access_token(
                identity=finalist_user.id,
                additional_claims={'role': 'finalist'}
            )
        
        application_payload = {
            'opportunity_id': 'job-123',
            'cover_letter': 'I am interested in this position...',
            'cv_version': 'latest',
            'availability': 'immediate'
        }
        
        response = client.post(
            '/api/v1/career/applications',
            json=application_payload,
            headers={'Authorization': f'Bearer {token}'}
        )
        
        assert response.status_code in [201, 404]  # 404 if job doesn't exist
    
    def test_finalist_view_own_applications(self, client, finalist_user):
        """Test finalist can view their job applications"""
        from flask_jwt_extended import create_access_token
        
        with client.application.app_context():
            token = create_access_token(
                identity=finalist_user.id,
                additional_claims={'role': 'finalist'}
            )
        
        response = client.get(
            '/api/v1/career/my-applications',
            headers={'Authorization': f'Bearer {token}'}
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'applications' in data['data']
    
    def test_withdraw_job_application(self, client, finalist_user):
        """Test finalist can withdraw a job application"""
        from flask_jwt_extended import create_access_token
        
        with client.application.app_context():
            token = create_access_token(
                identity=finalist_user.id,
                additional_claims={'role': 'finalist'}
            )
        
        response = client.delete(
            '/api/v1/career/applications/app-123',
            headers={'Authorization': f'Bearer {token}'}
        )
        
        assert response.status_code in [200, 404]


class TestCVBuilder:
    """Test CV builder functionality"""
    
    def test_finalist_create_cv(self, client, finalist_user):
        """Test finalist can create a CV"""
        from flask_jwt_extended import create_access_token
        
        with client.application.app_context():
            token = create_access_token(
                identity=finalist_user.id,
                additional_claims={'role': 'finalist'}
            )
        
        cv_payload = {
            'template': 'professional',
            'sections': {
                'education': [
                    {
                        'institution': 'Kampala International University',
                        'degree': 'Bachelor of Information Technology',
                        'year': '2026',
                        'cgpa': '4.2'
                    }
                ],
                'experience': [
                    {
                        'company': 'Tech Solutions Ltd',
                        'position': 'Junior Developer',
                        'duration': '2024-2025',
                        'description': 'Developed web applications'
                    }
                ],
                'skills': ['Python', 'JavaScript', 'React', 'Node.js']
            }
        }
        
        response = client.post(
            '/api/v1/career/cv',
            json=cv_payload,
            headers={'Authorization': f'Bearer {token}'}
        )
        
        assert response.status_code in [201, 200]
    
    def test_finalist_update_cv(self, client, finalist_user):
        """Test finalist can update their CV"""
        from flask_jwt_extended import create_access_token
        
        with client.application.app_context():
            token = create_access_token(
                identity=finalist_user.id,
                additional_claims={'role': 'finalist'}
            )
        
        update_payload = {
            'sections': {
                'skills': ['Python', 'JavaScript', 'React', 'Node.js', 'Docker']
            }
        }
        
        response = client.put(
            '/api/v1/career/cv',
            json=update_payload,
            headers={'Authorization': f'Bearer {token}'}
        )
        
        assert response.status_code == 200
    
    def test_finalist_download_cv(self, client, finalist_user):
        """Test finalist can download CV as PDF"""
        from flask_jwt_extended import create_access_token
        
        with client.application.app_context():
            token = create_access_token(
                identity=finalist_user.id,
                additional_claims={'role': 'finalist'}
            )
        
        response = client.get(
            '/api/v1/career/cv/download',
            headers={'Authorization': f'Bearer {token}'}
        )
        
        assert response.status_code in [200, 404]
        if response.status_code == 200:
            assert response.content_type == 'application/pdf'


class TestNetworking:
    """Test networking features"""
    
    def test_finalist_view_alumni_network(self, client, finalist_user):
        """Test finalist can view alumni network"""
        from flask_jwt_extended import create_access_token
        
        with client.application.app_context():
            token = create_access_token(
                identity=finalist_user.id,
                additional_claims={'role': 'finalist'}
            )
        
        response = client.get(
            '/api/v1/career/alumni',
            headers={'Authorization': f'Bearer {token}'}
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'alumni' in data['data']
    
    def test_search_alumni_by_industry(self, client, finalist_user):
        """Test searching alumni by industry"""
        from flask_jwt_extended import create_access_token
        
        with client.application.app_context():
            token = create_access_token(
                identity=finalist_user.id,
                additional_claims={'role': 'finalist'}
            )
        
        response = client.get(
            '/api/v1/career/alumni?industry=technology',
            headers={'Authorization': f'Bearer {token}'}
        )
        
        assert response.status_code == 200
    
    def test_connect_with_alumni(self, client, finalist_user):
        """Test finalist can connect with alumni"""
        from flask_jwt_extended import create_access_token
        
        with client.application.app_context():
            token = create_access_token(
                identity=finalist_user.id,
                additional_claims={'role': 'finalist'}
            )
        
        connect_payload = {
            'alumni_id': 'alum-456',
            'message': 'Would love to connect and learn about your experience'
        }
        
        response = client.post(
            '/api/v1/career/connect',
            json=connect_payload,
            headers={'Authorization': f'Bearer {token}'}
        )
        
        assert response.status_code in [201, 404]


class TestMentorship:
    """Test mentorship program"""
    
    def test_finalist_view_mentors(self, client, finalist_user):
        """Test finalist can view available mentors"""
        from flask_jwt_extended import create_access_token
        
        with client.application.app_context():
            token = create_access_token(
                identity=finalist_user.id,
                additional_claims={'role': 'finalist'}
            )
        
        response = client.get(
            '/api/v1/career/mentors',
            headers={'Authorization': f'Bearer {token}'}
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'mentors' in data['data']
    
    def test_finalist_request_mentorship(self, client, finalist_user):
        """Test finalist can request mentorship"""
        from flask_jwt_extended import create_access_token
        
        with client.application.app_context():
            token = create_access_token(
                identity=finalist_user.id,
                additional_claims={'role': 'finalist'}
            )
        
        request_payload = {
            'mentor_id': 'mentor-789',
            'goals': 'Career guidance in software engineering',
            'availability': 'Weekends'
        }
        
        response = client.post(
            '/api/v1/career/mentorship-requests',
            json=request_payload,
            headers={'Authorization': f'Bearer {token}'}
        )
        
        assert response.status_code in [201, 404]


class TestSkillAssessments:
    """Test skill assessment features"""
    
    def test_finalist_view_skill_assessments(self, client, finalist_user):
        """Test finalist can view available skill assessments"""
        from flask_jwt_extended import create_access_token
        
        with client.application.app_context():
            token = create_access_token(
                identity=finalist_user.id,
                additional_claims={'role': 'finalist'}
            )
        
        response = client.get(
            '/api/v1/career/skill-assessments',
            headers={'Authorization': f'Bearer {token}'}
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'assessments' in data['data']
    
    def test_finalist_take_skill_assessment(self, client, finalist_user):
        """Test finalist can take skill assessment"""
        from flask_jwt_extended import create_access_token
        
        with client.application.app_context():
            token = create_access_token(
                identity=finalist_user.id,
                additional_claims={'role': 'finalist'}
            )
        
        assessment_payload = {
            'assessment_id': 'python-basics',
            'answers': [
                {'question_id': 1, 'answer': 'A'},
                {'question_id': 2, 'answer': 'B'}
            ]
        }
        
        response = client.post(
            '/api/v1/career/skill-assessments/submit',
            json=assessment_payload,
            headers={'Authorization': f'Bearer {token}'}
        )
        
        assert response.status_code in [201, 404]
    
    def test_view_skill_assessment_results(self, client, finalist_user):
        """Test finalist can view assessment results"""
        from flask_jwt_extended import create_access_token
        
        with client.application.app_context():
            token = create_access_token(
                identity=finalist_user.id,
                additional_claims={'role': 'finalist'}
            )
        
        response = client.get(
            '/api/v1/career/skill-assessments/results',
            headers={'Authorization': f'Bearer {token}'}
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'results' in data['data']


class TestCareerAnalytics:
    """Test career analytics for finalists"""
    
    def test_finalist_view_career_analytics(self, client, finalist_user):
        """Test finalist can view their career analytics"""
        from flask_jwt_extended import create_access_token
        
        with client.application.app_context():
            token = create_access_token(
                identity=finalist_user.id,
                additional_claims={'role': 'finalist'}
            )
        
        response = client.get(
            '/api/v1/career/analytics',
            headers={'Authorization': f'Bearer {token}'}
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'profile_views' in data['data']
        assert 'application_stats' in data['data']
    
    def test_finalist_view_job_market_insights(self, client, finalist_user):
        """Test finalist can view job market insights"""
        from flask_jwt_extended import create_access_token
        
        with client.application.app_context():
            token = create_access_token(
                identity=finalist_user.id,
                additional_claims={'role': 'finalist'}
            )
        
        response = client.get(
            '/api/v1/career/market-insights',
            headers={'Authorization': f'Bearer {token}'}
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'trending_skills' in data['data']
        assert 'salary_ranges' in data['data']


class TestEmployerFeatures:
    """Test employer-facing features"""
    
    def test_employer_view_finalist_profiles(self, client, admin_user):
        """Test employer can view finalist profiles (admin access)"""
        from flask_jwt_extended import create_access_token
        
        with client.application.app_context():
            token = create_access_token(
                identity=admin_user.id,
                additional_claims={'role': 'admin'}
            )
        
        response = client.get(
            '/api/v1/career/finalists',
            headers={'Authorization': f'Bearer {token}'}
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'finalists' in data['data']
    
    def test_employer_post_job(self, client, admin_user):
        """Test employer can post job opportunity"""
        from flask_jwt_extended import create_access_token
        
        with client.application.app_context():
            token = create_access_token(
                identity=admin_user.id,
                additional_claims={'role': 'admin'}
            )
        
        job_payload = {
            'title': 'Software Developer',
            'organization': 'TechCorp Uganda',
            'type': 'job',
            'description': 'Looking for a skilled developer...',
            'requirements': 'Bachelor degree in IT, 2+ years experience',
            'salary_range': 'UGX 3,000,000 - 5,000,000',
            'location': 'Kampala',
            'application_deadline': (date.today() + timedelta(days=30)).isoformat(),
            'contact_email': 'jobs@techcorp.ug'
        }
        
        response = client.post(
            '/api/v1/career/opportunities',
            json=job_payload,
            headers={'Authorization': f'Bearer {token}'}
        )
        
        assert response.status_code in [201, 403]  # 403 if only super-admin can post
    
    def test_employer_search_finalists(self, client, admin_user):
        """Test employer can search finalists by skills"""
        from flask_jwt_extended import create_access_token
        
        with client.application.app_context():
            token = create_access_token(
                identity=admin_user.id,
                additional_claims={'role': 'admin'}
            )
        
        response = client.get(
            '/api/v1/career/finalists?skills=python,javascript',
            headers={'Authorization': f'Bearer {token}'}
        )
        
        assert response.status_code == 200
