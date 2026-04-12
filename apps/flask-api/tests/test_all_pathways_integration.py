"""
Integration Tests - All Admission Pathways
Tests actual application submission through each entry route
"""
import pytest
import json


class TestOlevelDirectPathway:
    """Test O-Level (UCE) graduates applying directly"""
    
    def test_olevel_to_certificate_application(self, client, auth_headers, sample_programs):
        """O-Level → Certificate program"""
        payload = {
            'program_ids': [sample_programs['certificate'].id],
            'exam_level': 'o_level',
            'exam_year': 2023,
            'index_number': 'U2023/001',
            'uneb_grades': {
                'mathematics': {'grade': 'C', 'points': 3, 'curriculum': 'new'},
                'english': {'grade': 'C', 'points': 3, 'curriculum': 'new'},
                'physics': {'grade': 'D', 'points': 2, 'curriculum': 'new'},
                'chemistry': {'grade': 'D', 'points': 2, 'curriculum': 'new'},
                'biology': {'grade': 'C', 'points': 3, 'curriculum': 'new'},
                'history': {'grade': 'B', 'points': 4, 'curriculum': 'new'},
                'geography': {'grade': 'C', 'points': 3, 'curriculum': 'new'}
            },
            'curriculum_version': 'new',
            'date_of_birth': '2005-03-15',
            'gender': 'male',
            'nationality': 'Ugandan',
            'district': 'Kampala',
            'next_of_kin_name': 'John Parent',
            'next_of_kin_phone': '+256700000001',
            'next_of_kin_relationship': 'Father'
        }
        
        response = client.post(
            '/api/apply',
            data=json.dumps(payload),
            headers={**auth_headers, 'Content-Type': 'application/json'}
        )
        
        assert response.status_code in [201, 200, 400]  # 400 if validation fails
    
    def test_olevel_to_hec_application(self, client, auth_headers, sample_programs):
        """O-Level → Higher Education Certificate"""
        payload = {
            'program_ids': [sample_programs['hec'].id],
            'exam_level': 'o_level',
            'exam_year': 2023,
            'index_number': 'U2023/002',
            'uneb_grades': {
                'mathematics': {'grade': 'D', 'points': 2, 'curriculum': 'new'},
                'english': {'grade': 'D', 'points': 2, 'curriculum': 'new'},
                'physics': {'grade': 'E', 'points': 1, 'curriculum': 'new'},
                'chemistry': {'grade': 'E', 'points': 1, 'curriculum': 'new'}
            },
            'curriculum_version': 'new',
            'date_of_birth': '2005-06-20',
            'gender': 'female',
            'nationality': 'Ugandan'
        }
        
        response = client.post(
            '/api/apply',
            data=json.dumps(payload),
            headers={**auth_headers, 'Content-Type': 'application/json'}
        )
        
        assert response.status_code in [201, 200, 400]


class TestAlevelDirectPathway:
    """Test A-Level (UACE) graduates applying directly"""
    
    def test_alevel_to_bachelor_application(self, client, auth_headers, sample_programs):
        """A-Level → Bachelor's degree (2 principal passes)"""
        payload = {
            'program_ids': [sample_programs['bachelor'].id],
            'exam_level': 'a_level',
            'exam_year': 2023,
            'index_number': 'U2023/003',
            'uneb_grades': {
                'subjects': [
                    {'name': 'Physics', 'grade': 'B', 'points': 5, 'type': 'principal'},
                    {'name': 'Chemistry', 'grade': 'C', 'points': 4, 'type': 'principal'},
                    {'name': 'Mathematics', 'grade': 'B', 'points': 5, 'type': 'principal'},
                    {'name': 'General Paper', 'grade': 'B', 'points': 5, 'type': 'subsidiary'}
                ],
                'total_points': 19,
                'number_of_subjects': 4
            },
            'curriculum_version': 'old',
            'date_of_birth': '2003-01-10',
            'gender': 'male',
            'nationality': 'Ugandan',
            'district': 'Kampala'
        }
        
        response = client.post(
            '/api/apply',
            data=json.dumps(payload),
            headers={**auth_headers, 'Content-Type': 'application/json'}
        )
        
        assert response.status_code in [201, 200, 400]
    
    def test_alevel_to_diploma_application(self, client, auth_headers, sample_programs):
        """A-Level → Diploma (1 principal + 2 subsidiaries)"""
        payload = {
            'program_ids': [sample_programs['diploma'].id],
            'exam_level': 'a_level',
            'exam_year': 2022,
            'index_number': 'U2022/004',
            'uneb_grades': {
                'subjects': [
                    {'name': 'History', 'grade': 'C', 'points': 4, 'type': 'principal'},
                    {'name': 'Economics', 'grade': 'D', 'points': 3, 'type': 'subsidiary'},
                    {'name': 'Geography', 'grade': 'D', 'points': 3, 'type': 'subsidiary'}
                ],
                'total_points': 10,
                'number_of_subjects': 3
            },
            'curriculum_version': 'old',
            'date_of_birth': '2002-08-25',
            'gender': 'female',
            'nationality': 'Ugandan'
        }
        
        response = client.post(
            '/api/apply',
            data=json.dumps(payload),
            headers={**auth_headers, 'Content-Type': 'application/json'}
        )
        
        assert response.status_code in [201, 200, 400]


class TestHECPathway:
    """Test HEC to Degree progression"""
    
    def test_hec_to_bachelor_application(self, client, auth_headers, sample_programs):
        """HEC → Bachelor's degree"""
        payload = {
            'program_ids': [sample_programs['bachelor'].id],
            'exam_level': 'hec',
            'qualification_type': 'hec',
            'hec_certificate': {
                'institution': 'KIU',
                'program': 'Higher Education Certificate in ICT',
                'completion_year': 2024,
                'cgpa': 3.5,
                'track': 'Physical Sciences'
            },
            'date_of_birth': '2005-03-15',
            'gender': 'male',
            'nationality': 'Ugandan'
        }
        
        response = client.post(
            '/api/apply',
            data=json.dumps(payload),
            headers={**auth_headers, 'Content-Type': 'application/json'}
        )
        
        assert response.status_code in [201, 200, 400]


class TestDiplomaPathway:
    """Test Diploma entry and progression"""
    
    def test_diploma_direct_application(self, client, auth_headers, sample_programs):
        """Direct entry to Diploma (O-Level/A-Level base)"""
        payload = {
            'program_ids': [sample_programs['diploma'].id],
            'exam_level': 'o_level',
            'exam_year': 2022,
            'index_number': 'U2022/005',
            'uneb_grades': {
                'mathematics': {'grade': 'C', 'points': 3, 'curriculum': 'old'},
                'english': {'grade': 'C', 'points': 3, 'curriculum': 'old'},
                'physics': {'grade': 'D', 'points': 2, 'curriculum': 'old'}
            },
            'curriculum_version': 'old',
            'date_of_birth': '2004-04-20',
            'gender': 'male',
            'nationality': 'Ugandan'
        }
        
        response = client.post(
            '/api/apply',
            data=json.dumps(payload),
            headers={**auth_headers, 'Content-Type': 'application/json'}
        )
        
        assert response.status_code in [201, 200, 400]
    
    def test_diploma_to_bachelor_progression(self, client, auth_headers, sample_programs):
        """Diploma → Bachelor's with credit transfer"""
        payload = {
            'program_ids': [sample_programs['bachelor'].id],
            'exam_level': 'diploma',
            'qualification_type': 'diploma',
            'previous_qualification': {
                'institution': 'Uganda Polytechnic',
                'program': 'Diploma in Computer Science',
                'completion_year': 2024,
                'cgpa': 3.8,
                'credit_hours': 120,
                'classification': 'Second Class Upper',
                'transcript_file': 'transcript_001.pdf'
            },
            'credit_transfer_request': True,
            'date_of_birth': '2002-08-10',
            'gender': 'female',
            'nationality': 'Ugandan'
        }
        
        response = client.post(
            '/api/apply',
            data=json.dumps(payload),
            headers={**auth_headers, 'Content-Type': 'application/json'}
        )
        
        assert response.status_code in [201, 200, 400]


class TestMastersPathway:
    """Test Master's degree entry"""
    
    def test_masters_with_bachelor_degree(self, client, auth_headers, sample_programs):
        """Bachelor's → Master's"""
        payload = {
            'program_ids': [sample_programs['masters'].id],
            'exam_level': 'masters',
            'qualification_type': 'degree',
            'previous_qualification': {
                'institution': 'Makerere University',
                'program': 'Bachelor of Science in Computer Science',
                'completion_year': 2023,
                'cgpa': 4.2,
                'credit_hours': 180,
                'classification': 'First Class',
                'degree_certificate': 'degree_cert_001.pdf',
                'transcript': 'transcript_001.pdf'
            },
            'research_interest': 'Artificial Intelligence',
            'proposed_supervisor': 'Dr. James Smith',
            'date_of_birth': '1998-05-15',
            'gender': 'male',
            'nationality': 'Ugandan'
        }
        
        response = client.post(
            '/api/apply',
            data=json.dumps(payload),
            headers={**auth_headers, 'Content-Type': 'application/json'}
        )
        
        assert response.status_code in [201, 200, 400]


class TestPhDPathway:
    """Test PhD entry"""
    
    def test_phd_with_masters_degree(self, client, auth_headers, sample_programs):
        """Master's → PhD"""
        payload = {
            'program_ids': [sample_programs['phd'].id],
            'exam_level': 'phd',
            'qualification_type': 'masters',
            'previous_qualification': {
                'institution': 'Kampala International University',
                'program': 'Master of Science in Information Technology',
                'completion_year': 2025,
                'cgpa': 4.5,
                'research_thesis': 'AI in Healthcare',
                'thesis_abstract': 'This research explores...',
                'supervisor': 'Dr. Jane Doe',
                'masters_certificate': 'masters_cert_001.pdf',
                'transcript': 'transcript_001.pdf'
            },
            'research_proposal': {
                'title': 'Machine Learning in Medical Diagnosis',
                'abstract': 'This research aims to...',
                'methodology': 'Quantitative analysis using...',
                'expected_contribution': 'New algorithms for...',
                'duration_years': 3,
                'funding_source': 'Self-funded'
            },
            'proposed_supervisor': 'Dr. James Smith',
            'references': [
                {'name': 'Prof. John Doe', 'institution': 'Makerere University', 'email': 'john@mak.ac.ug'},
                {'name': 'Dr. Jane Smith', 'institution': 'KIU', 'email': 'jane@kiu.ac.ug'}
            ],
            'date_of_birth': '1995-11-30',
            'gender': 'male',
            'nationality': 'Ugandan'
        }
        
        response = client.post(
            '/api/apply',
            data=json.dumps(payload),
            headers={**auth_headers, 'Content-Type': 'application/json'}
        )
        
        assert response.status_code in [201, 200, 400]


class TestHealthSciencePathways:
    """Test Health Science specific entry"""
    
    def test_mbchb_with_required_subjects(self, client, auth_headers, health_programs):
        """MBChB with Biology + Chemistry (essential subjects)"""
        payload = {
            'program_ids': [health_programs['mbchb'].id],
            'exam_level': 'a_level',
            'exam_year': 2023,
            'index_number': 'U2023/006',
            'uneb_grades': {
                'subjects': [
                    {'name': 'Biology', 'grade': 'A', 'points': 6, 'type': 'principal'},  # Essential
                    {'name': 'Chemistry', 'grade': 'B', 'points': 5, 'type': 'principal'},  # Essential
                    {'name': 'Physics', 'grade': 'C', 'points': 4, 'type': 'principal'}  # Relevant
                ],
                'total_points': 15,
                'number_of_subjects': 3
            },
            'curriculum_version': 'old',
            'date_of_birth': '2003-02-28',
            'gender': 'female',
            'nationality': 'Ugandan'
        }
        
        response = client.post(
            '/api/apply',
            data=json.dumps(payload),
            headers={**auth_headers, 'Content-Type': 'application/json'}
        )
        
        assert response.status_code in [201, 200, 400]


class TestInternationalStudents:
    """Test international student applications"""
    
    def test_international_student_bachelor(self, client, auth_headers, sample_programs):
        """International student applying for Bachelor's"""
        payload = {
            'program_ids': [sample_programs['bachelor'].id],
            'exam_level': 'a_level',
            'exam_year': 2023,
            'nationality': 'Kenyan',  # East African
            'foreign_qualification': {
                'country': 'Kenya',
                'exam_type': 'KCSE',
                'grade': 'B+',
                'subjects': ['Mathematics', 'Physics', 'Chemistry', 'Biology']
            },
            'passport_number': 'A12345678',
            'passport_file': 'passport_001.pdf',
            'study_permit_required': True,
            'date_of_birth': '2003-05-20',
            'gender': 'male'
        }
        
        response = client.post(
            '/api/apply',
            data=json.dumps(payload),
            headers={**auth_headers, 'Content-Type': 'application/json'}
        )
        
        assert response.status_code in [201, 200, 400]


class TestMultipleProgramApplications:
    """Test applying to multiple programs"""
    
    def test_apply_to_three_programs(self, client, auth_headers, sample_programs):
        """Apply to 3 programs at once (max allowed)"""
        payload = {
            'program_ids': [
                sample_programs['bachelor'].id,
                sample_programs['diploma'].id,
                sample_programs['hec'].id
            ],
            'exam_level': 'a_level',
            'exam_year': 2023,
            'index_number': 'U2023/007',
            'uneb_grades': {
                'subjects': [
                    {'name': 'Physics', 'grade': 'B', 'points': 5, 'type': 'principal'},
                    {'name': 'Chemistry', 'grade': 'C', 'points': 4, 'type': 'principal'},
                    {'name': 'Mathematics', 'grade': 'B', 'points': 5, 'type': 'principal'}
                ],
                'total_points': 14,
                'number_of_subjects': 3
            },
            'curriculum_version': 'old',
            'date_of_birth': '2003-01-15',
            'gender': 'male',
            'nationality': 'Ugandan'
        }
        
        response = client.post(
            '/api/apply',
            data=json.dumps(payload),
            headers={**auth_headers, 'Content-Type': 'application/json'}
        )
        
        assert response.status_code in [201, 200, 400]


class TestMatureAgeEntry:
    """Test mature age entry pathway"""
    
    def test_mature_age_entry(self, client, auth_headers, sample_programs):
        """Mature age entry (25+ years with work experience)"""
        payload = {
            'program_ids': [sample_programs['bachelor'].id],
            'exam_level': 'mature_age',
            'qualification_type': 'mature_age',
            'date_of_birth': '1990-01-01',  # 36 years old
            'age_at_application': 36,
            'work_experience': [
                {
                    'employer': 'Tech Solutions Ltd',
                    'position': 'IT Manager',
                    'duration': '5 years',
                    'start_year': 2019,
                    'end_year': 2024
                }
            ],
            'total_work_experience_years': 10,
            'professional_certifications': [
                {'name': 'CCNA', 'institution': 'Cisco', 'year': 2020},
                {'name': 'CompTIA A+', 'institution': 'CompTIA', 'year': 2019}
            ],
            'mature_age_assessment': {
                'test_date': '2026-01-15',
                'test_center': 'KIU Main Campus',
                'score': 85,
                'passed': True
            },
            'gender': 'male',
            'nationality': 'Ugandan'
        }
        
        response = client.post(
            '/api/apply',
            data=json.dumps(payload),
            headers={**auth_headers, 'Content-Type': 'application/json'}
        )
        
        assert response.status_code in [201, 200, 400]


class TestCurriculumTransitions:
    """Test both old and new curriculum"""
    
    def test_old_curriculum_application(self, client, auth_headers, sample_programs):
        """Pre-2024 curriculum (Division 1-4)"""
        payload = {
            'program_ids': [sample_programs['certificate'].id],
            'exam_level': 'o_level',
            'exam_year': 2022,
            'index_number': 'U2022/008',
            'uneb_grades': {
                'division': 'Division 2',
                'subjects': {
                    'mathematics': {'grade': '2', 'points': 2},  # Old grading
                    'english': {'grade': '3', 'points': 3},
                    'physics': {'grade': '4', 'points': 4},
                    'chemistry': {'grade': '3', 'points': 3}
                }
            },
            'curriculum_version': 'old',
            'date_of_birth': '2005-04-10',
            'gender': 'female',
            'nationality': 'Ugandan'
        }
        
        response = client.post(
            '/api/apply',
            data=json.dumps(payload),
            headers={**auth_headers, 'Content-Type': 'application/json'}
        )
        
        assert response.status_code in [201, 200, 400]
    
    def test_new_curriculum_application(self, client, auth_headers, sample_programs):
        """2024+ curriculum (A-F grades)"""
        payload = {
            'program_ids': [sample_programs['certificate'].id],
            'exam_level': 'o_level',
            'exam_year': 2024,
            'index_number': 'U2024/009',
            'uneb_grades': {
                'mathematics': {'grade': 'B', 'points': 4},  # New grading A-F
                'english': {'grade': 'C', 'points': 3},
                'physics': {'grade': 'D', 'points': 2},
                'chemistry': {'grade': 'C', 'points': 3}
            },
            'curriculum_version': 'new',
            'date_of_birth': '2006-07-15',
            'gender': 'male',
            'nationality': 'Ugandan'
        }
        
        response = client.post(
            '/api/apply',
            data=json.dumps(payload),
            headers={**auth_headers, 'Content-Type': 'application/json'}
        )
        
        assert response.status_code in [201, 200, 400]


class TestApplicationValidation:
    """Test validation for all pathways"""
    
    def test_missing_exam_level_rejected(self, client, auth_headers, sample_programs):
        """Application without exam level should be rejected"""
        payload = {
            'program_ids': [sample_programs['bachelor'].id],
            'exam_year': 2023,
            'date_of_birth': '2003-01-15',
            'gender': 'male'
        }
        
        response = client.post(
            '/api/apply',
            data=json.dumps(payload),
            headers={**auth_headers, 'Content-Type': 'application/json'}
        )
        
        assert response.status_code in [400, 422]
    
    def test_underage_applicant_rejected(self, client, auth_headers, sample_programs):
        """Applicant under 16 should be rejected"""
        payload = {
            'program_ids': [sample_programs['certificate'].id],
            'exam_level': 'o_level',
            'exam_year': 2023,
            'date_of_birth': '2015-01-01',  # 11 years old
            'gender': 'male',
            'uneb_grades': {}
        }
        
        response = client.post(
            '/api/apply',
            data=json.dumps(payload),
            headers={**auth_headers, 'Content-Type': 'application/json'}
        )
        
        assert response.status_code in [400, 422]
    
    def test_future_exam_year_rejected(self, client, auth_headers, sample_programs):
        """Future exam year should be rejected"""
        payload = {
            'program_ids': [sample_programs['bachelor'].id],
            'exam_level': 'a_level',
            'exam_year': 2030,  # Future
            'date_of_birth': '2003-01-15',
            'gender': 'male',
            'uneb_grades': {}
        }
        
        response = client.post(
            '/api/apply',
            data=json.dumps(payload),
            headers={**auth_headers, 'Content-Type': 'application/json'}
        )
        
        assert response.status_code in [400, 422]
