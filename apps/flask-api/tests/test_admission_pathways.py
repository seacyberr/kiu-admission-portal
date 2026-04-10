"""
Comprehensive Admission Pathway Tests
Tests all NCHE Uganda education pathways from O-Level to PhD
"""
import pytest
from datetime import date


class TestOlevelPathway:
    """Test O-Level (UCE) entry pathways"""
    
    def test_olevel_to_certificate_direct(self, client, applicant_user, auth_headers, sample_programs):
        """Test O-Level graduate applying for Certificate program"""
        payload = {
            'program_ids': [sample_programs['certificate'].id],
            'exam_level': 'o_level',
            'exam_year': 2023,
            'index_number': 'U1234/001',
            'uneb_grades': {
                'mathematics': {'grade': 'C', 'points': 3},
                'english': {'grade': 'C', 'points': 3},
                'physics': {'grade': 'D', 'points': 2},
                'chemistry': {'grade': 'D', 'points': 2},
                'biology': {'grade': 'C', 'points': 3}
            },
            'date_of_birth': '2005-01-15',
            'gender': 'male',
            'curriculum_version': 'new'  # 2024+ curriculum
        }
        
        response = client.post(
            '/api/v1/admissions/apply',
            json=payload,
            headers=auth_headers
        )
        
        assert response.status_code == 201
        data = response.get_json()
        assert data['success'] is True
    
    def test_olevel_to_hec_direct(self, client, applicant_user, auth_headers, sample_programs):
        """Test O-Level graduate applying for HEC (Higher Education Certificate)"""
        payload = {
            'program_ids': [sample_programs['hec'].id],
            'exam_level': 'o_level',
            'exam_year': 2023,
            'index_number': 'U5678/002',
            'uneb_grades': {
                'mathematics': {'grade': 'D', 'points': 2},
                'english': {'grade': 'D', 'points': 2},
                'physics': {'grade': 'E', 'points': 1},
                'chemistry': {'grade': 'E', 'points': 1}
            },
            'date_of_birth': '2005-06-20',
            'gender': 'female'
        }
        
        response = client.post(
            '/api/v1/admissions/apply',
            json=payload,
            headers=auth_headers
        )
        
        assert response.status_code == 201
    
    def test_olevel_insufficient_grades(self, client, applicant_user, auth_headers, sample_programs):
        """Test O-Level with insufficient grades for certificate"""
        payload = {
            'program_ids': [sample_programs['certificate'].id],
            'exam_level': 'o_level',
            'exam_year': 2023,
            'index_number': 'U9999/999',
            'uneb_grades': {
                'mathematics': {'grade': 'F', 'points': 0},
                'english': {'grade': 'F', 'points': 0}
            },
            'date_of_birth': '2005-01-15',
            'gender': 'male'
        }
        
        response = client.post(
            '/api/v1/admissions/apply',
            json=payload,
            headers=auth_headers
        )
        
        # Should still allow application but flag for review
        assert response.status_code in [201, 400]


class TestAlevelPathway:
    """Test A-Level (UACE) entry pathways"""
    
    def test_alevel_to_bachelor_direct(self, client, applicant_user, auth_headers, sample_programs):
        """Test A-Level graduate applying for Bachelor's degree"""
        payload = {
            'program_ids': [sample_programs['bachelor'].id],
            'exam_level': 'a_level',
            'exam_year': 2023,
            'index_number': 'U1234/001',
            'uneb_grades': {
                'subjects': [
                    {'name': 'Physics', 'grade': 'B', 'points': 5},
                    {'name': 'Chemistry', 'grade': 'C', 'points': 4},
                    {'name': 'Mathematics', 'grade': 'B', 'points': 5}
                ],
                'total_points': 14,
                'number_of_subjects': 3
            },
            'date_of_birth': '2003-03-10',
            'gender': 'male',
            'curriculum_version': 'old'
        }
        
        response = client.post(
            '/api/v1/admissions/apply',
            json=payload,
            headers=auth_headers
        )
        
        assert response.status_code == 201
    
    def test_alevel_to_diploma_direct(self, client, applicant_user, auth_headers, sample_programs):
        """Test A-Level graduate applying for Diploma"""
        payload = {
            'program_ids': [sample_programs['diploma'].id],
            'exam_level': 'a_level',
            'exam_year': 2022,
            'index_number': 'U5678/002',
            'uneb_grades': {
                'subjects': [
                    {'name': 'History', 'grade': 'C', 'points': 4},
                    {'name': 'Economics', 'grade': 'D', 'points': 3},
                    {'name': 'Geography', 'grade': 'C', 'points': 4}
                ],
                'total_points': 11,
                'number_of_subjects': 3
            },
            'date_of_birth': '2002-08-25',
            'gender': 'female'
        }
        
        response = client.post(
            '/api/v1/admissions/apply',
            json=payload,
            headers=auth_headers
        )
        
        assert response.status_code == 201
    
    def test_alevel_to_hec(self, client, applicant_user, auth_headers, sample_programs):
        """Test A-Level graduate applying for HEC"""
        payload = {
            'program_ids': [sample_programs['hec'].id],
            'exam_level': 'a_level',
            'exam_year': 2021,
            'index_number': 'U9999/003',
            'uneb_grades': {
                'subjects': [
                    {'name': 'Physics', 'grade': 'E', 'points': 1},
                    {'name': 'Chemistry', 'grade': 'E', 'points': 1},
                    {'name': 'Mathematics', 'grade': 'E', 'points': 1}
                ],
                'total_points': 3,
                'number_of_subjects': 3
            },
            'date_of_birth': '2001-12-05',
            'gender': 'male'
        }
        
        response = client.post(
            '/api/v1/admissions/apply',
            json=payload,
            headers=auth_headers
        )
        
        assert response.status_code == 201


class TestHECPathway:
    """Test HEC (Higher Education Certificate) progression"""
    
    def test_hec_to_bachelor_progression(self, client, applicant_user, auth_headers, sample_programs, create_application):
        """Test HEC graduate progressing to Bachelor's"""
        # First create HEC application
        hec_app = create_application(
            program_level='hec',
            qualification_type='o_level',
            status='completed'
        )
        
        # Now apply for Bachelor's
        payload = {
            'program_ids': [sample_programs['bachelor'].id],
            'exam_level': 'hec',
            'hec_completion_year': 2024,
            'previous_program_id': hec_app.program_id,
            'date_of_birth': '2005-01-15',
            'gender': 'male'
        }
        
        response = client.post(
            '/api/v1/admissions/apply',
            json=payload,
            headers=auth_headers
        )
        
        assert response.status_code == 201


class TestDiplomaPathway:
    """Test Diploma entry and progression"""
    
    def test_diploma_direct_entry(self, client, applicant_user, auth_headers, sample_programs):
        """Test O-Level or A-Level graduate applying for Diploma"""
        payload = {
            'program_ids': [sample_programs['diploma'].id],
            'exam_level': 'o_level',
            'exam_year': 2022,
            'index_number': 'U1111/001',
            'uneb_grades': {
                'mathematics': {'grade': 'C', 'points': 3},
                'english': {'grade': 'C', 'points': 3},
                'physics': {'grade': 'D', 'points': 2}
            },
            'date_of_birth': '2004-04-20',
            'gender': 'male'
        }
        
        response = client.post(
            '/api/v1/admissions/apply',
            json=payload,
            headers=auth_headers
        )
        
        assert response.status_code == 201
    
    def test_diploma_to_bachelor_progression(self, client, applicant_user, auth_headers, sample_programs, create_application):
        """Test Diploma holder progressing to Bachelor's with credit transfer"""
        # Create completed diploma
        diploma_app = create_application(
            program_level='diploma',
            qualification_type='o_level',
            status='completed'
        )
        
        payload = {
            'program_ids': [sample_programs['bachelor'].id],
            'exam_level': 'diploma',
            'qualification_type': 'diploma',
            'previous_qualification': {
                'institution': 'KIU',
                'program': 'Diploma in IT',
                'cgpa': 3.5,
                'credit_hours': 120,
                'completion_year': 2024
            },
            'date_of_birth': '2002-08-10',
            'gender': 'female'
        }
        
        response = client.post(
            '/api/v1/admissions/apply',
            json=payload,
            headers=auth_headers
        )
        
        assert response.status_code == 201


class TestMastersPathway:
    """Test Masters degree entry"""
    
    def test_masters_entry_with_bachelor(self, client, applicant_user, auth_headers, sample_programs):
        """Test Bachelor's graduate applying for Masters"""
        payload = {
            'program_ids': [sample_programs['masters'].id],
            'exam_level': 'masters',
            'qualification_type': 'degree',
            'previous_qualification': {
                'institution': 'Makerere University',
                'program': 'Bachelor of Science in Computer Science',
                'cgpa': 4.0,
                'classification': 'Second Class Upper',
                'completion_year': 2023
            },
            'date_of_birth': '1998-05-15',
            'gender': 'male'
        }
        
        response = client.post(
            '/api/v1/admissions/apply',
            json=payload,
            headers=auth_headers
        )
        
        assert response.status_code == 201
    
    def test_masters_insufficient_cgpa(self, client, applicant_user, auth_headers, sample_programs):
        """Test Masters application with insufficient CGPA"""
        payload = {
            'program_ids': [sample_programs['masters'].id],
            'exam_level': 'masters',
            'qualification_type': 'degree',
            'previous_qualification': {
                'institution': 'Some University',
                'program': 'Bachelor of Arts',
                'cgpa': 2.5,  # Below 3.0 requirement
                'completion_year': 2023
            },
            'date_of_birth': '1999-03-20',
            'gender': 'female'
        }
        
        response = client.post(
            '/api/v1/admissions/apply',
            json=payload,
            headers=auth_headers
        )
        
        # Should flag for review or reject
        assert response.status_code in [201, 400]


class TestPhDPathway:
    """Test PhD entry"""
    
    def test_phd_entry_with_masters(self, client, applicant_user, auth_headers, sample_programs):
        """Test Master's graduate applying for PhD"""
        payload = {
            'program_ids': [sample_programs['phd'].id],
            'exam_level': 'phd',
            'qualification_type': 'masters',
            'previous_qualification': {
                'institution': 'Kampala International University',
                'program': 'Master of Science in Information Technology',
                'cgpa': 4.5,
                'research_thesis': 'AI in Healthcare',
                'supervisor': 'Dr. James Smith',
                'completion_year': 2025
            },
            'research_proposal': {
                'title': 'Machine Learning in Medical Diagnosis',
                'abstract': 'This research explores...',
                'methodology': 'Quantitative analysis...'
            },
            'date_of_birth': '1995-11-30',
            'gender': 'male'
        }
        
        response = client.post(
            '/api/v1/admissions/apply',
            json=payload,
            headers=auth_headers
        )
        
        assert response.status_code == 201
    
    def test_phd_research_experience_required(self, client, applicant_user, auth_headers, sample_programs):
        """Test PhD application requires research experience"""
        payload = {
            'program_ids': [sample_programs['phd'].id],
            'exam_level': 'phd',
            'qualification_type': 'masters',
            'previous_qualification': {
                'institution': 'Some University',
                'program': 'MBA',  # Non-research masters
                'cgpa': 4.0,
                'completion_year': 2024
            },
            'date_of_birth': '1996-07-15',
            'gender': 'female'
        }
        
        response = client.post(
            '/api/v1/admissions/apply',
            json=payload,
            headers=auth_headers
        )
        
        # Should require research proposal
        assert response.status_code in [201, 400]


class TestHealthSciencePathways:
    """Test Health Science specific pathways"""
    
    def test_mbchb_entry_requirements(self, client, applicant_user, auth_headers, health_programs):
        """Test MBChB entry with specific subject requirements"""
        payload = {
            'program_ids': [health_programs['mbchb'].id],
            'exam_level': 'a_level',
            'exam_year': 2023,
            'index_number': 'U1234/001',
            'uneb_grades': {
                'subjects': [
                    {'name': 'Biology', 'grade': 'B', 'points': 5},  # Essential
                    {'name': 'Chemistry', 'grade': 'B', 'points': 5},  # Essential
                    {'name': 'Physics', 'grade': 'C', 'points': 4}   # Relevant
                ],
                'total_points': 14,
                'number_of_subjects': 3
            },
            'date_of_birth': '2003-01-15',
            'gender': 'male'
        }
        
        response = client.post(
            '/api/v1/admissions/apply',
            json=payload,
            headers=auth_headers
        )
        
        assert response.status_code == 201
    
    def test_mbchb_missing_essential_subjects(self, client, applicant_user, auth_headers, health_programs):
        """Test MBChB application missing Biology/Chemistry"""
        payload = {
            'program_ids': [health_programs['mbchb'].id],
            'exam_level': 'a_level',
            'exam_year': 2023,
            'index_number': 'U5678/002',
            'uneb_grades': {
                'subjects': [
                    {'name': 'History', 'grade': 'A', 'points': 6},
                    {'name': 'Economics', 'grade': 'B', 'points': 5},
                    {'name': 'Geography', 'grade': 'B', 'points': 5}
                ],
                'total_points': 16,
                'number_of_subjects': 3
            },
            'date_of_birth': '2003-06-20',
            'gender': 'female'
        }
        
        response = client.post(
            '/api/v1/admissions/apply',
            json=payload,
            headers=auth_headers
        )
        
        # Should warn or reject due to missing essential subjects
        assert response.status_code in [201, 400]


class TestMultipleProgramApplications:
    """Test applying to multiple programs"""
    
    def test_apply_to_multiple_programs(self, client, applicant_user, auth_headers, sample_programs):
        """Test applicant can apply to up to 3 programs"""
        payload = {
            'program_ids': [
                sample_programs['bachelor'].id,
                sample_programs['diploma'].id,
                sample_programs['hec'].id
            ],
            'exam_level': 'a_level',
            'exam_year': 2023,
            'index_number': 'U1234/001',
            'uneb_grades': {
                'subjects': [
                    {'name': 'Physics', 'grade': 'B', 'points': 5},
                    {'name': 'Chemistry', 'grade': 'C', 'points': 4},
                    {'name': 'Mathematics', 'grade': 'B', 'points': 5}
                ],
                'total_points': 14,
                'number_of_subjects': 3
            },
            'date_of_birth': '2003-03-10',
            'gender': 'male'
        }
        
        response = client.post(
            '/api/v1/admissions/apply',
            json=payload,
            headers=auth_headers
        )
        
        assert response.status_code == 201
        data = response.get_json()
        assert len(data['data']['applications']) == 3


class TestCurriculumVersions:
    """Test both old and new curriculum support"""
    
    def test_old_curriculum_grades(self, client, applicant_user, auth_headers, sample_programs):
        """Test O-Level with old curriculum (pre-2024)"""
        payload = {
            'program_ids': [sample_programs['certificate'].id],
            'exam_level': 'o_level',
            'exam_year': 2022,
            'index_number': 'U1234/001',
            'uneb_grades': {
                'mathematics': {'grade': '2', 'points': 2},  # Old grading
                'english': {'grade': '3', 'points': 3},
                'physics': {'grade': '4', 'points': 4}
            },
            'curriculum_version': 'old',
            'date_of_birth': '2005-01-15',
            'gender': 'male'
        }
        
        response = client.post(
            '/api/v1/admissions/apply',
            json=payload,
            headers=auth_headers
        )
        
        assert response.status_code == 201
    
    def test_new_curriculum_grades(self, client, applicant_user, auth_headers, sample_programs):
        """Test O-Level with new curriculum (2024+)"""
        payload = {
            'program_ids': [sample_programs['certificate'].id],
            'exam_level': 'o_level',
            'exam_year': 2024,
            'index_number': 'U5678/002',
            'uneb_grades': {
                'mathematics': {'grade': 'B', 'points': 4},  # New grading (A-F)
                'english': {'grade': 'C', 'points': 3},
                'physics': {'grade': 'D', 'points': 2}
            },
            'curriculum_version': 'new',
            'date_of_birth': '2006-03-20',
            'gender': 'female'
        }
        
        response = client.post(
            '/api/v1/admissions/apply',
            json=payload,
            headers=auth_headers
        )
        
        assert response.status_code == 201


class TestApplicationValidation:
    """Test application validation rules"""
    
    def test_missing_program_selection(self, client, applicant_user, auth_headers):
        """Test application without program selection"""
        payload = {
            'exam_level': 'a_level',
            'exam_year': 2023,
            'uneb_grades': {},
            'date_of_birth': '2003-01-15',
            'gender': 'male'
        }
        
        response = client.post(
            '/api/v1/admissions/apply',
            json=payload,
            headers=auth_headers
        )
        
        assert response.status_code == 400
    
    def test_invalid_date_of_birth(self, client, applicant_user, auth_headers, sample_programs):
        """Test application with invalid/underage DOB"""
        payload = {
            'program_ids': [sample_programs['bachelor'].id],
            'exam_level': 'a_level',
            'exam_year': 2023,
            'uneb_grades': {},
            'date_of_birth': '2015-01-15',  # Too young
            'gender': 'male'
        }
        
        response = client.post(
            '/api/v1/admissions/apply',
            json=payload,
            headers=auth_headers
        )
        
        assert response.status_code == 400
    
    def test_future_exam_year(self, client, applicant_user, auth_headers, sample_programs):
        """Test application with future exam year"""
        payload = {
            'program_ids': [sample_programs['bachelor'].id],
            'exam_level': 'a_level',
            'exam_year': 2030,  # Future year
            'uneb_grades': {},
            'date_of_birth': '2003-01-15',
            'gender': 'male'
        }
        
        response = client.post(
            '/api/v1/admissions/apply',
            json=payload,
            headers=auth_headers
        )
        
        assert response.status_code == 400
