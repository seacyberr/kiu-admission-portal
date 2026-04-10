"""
Comprehensive Admin Operations Tests
Tests all administrative workflows and functionalities
"""
import pytest
from datetime import date, datetime


class TestAdminApplicationReview:
    """Test application review workflows"""
    
    def test_admin_view_all_applications(self, client, admin_auth_headers, create_application):
        """Test admin can view all applications"""
        # Create multiple applications
        app1 = create_application(status='submitted')
        app2 = create_application(status='under_review')
        app3 = create_application(status='accepted')
        
        response = client.get(
            '/api/v1/admin/applications',
            headers=admin_auth_headers
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert len(data['data']['applications']) >= 3
    
    def test_admin_filter_applications_by_status(self, client, admin_auth_headers, create_application):
        """Test filtering applications by status"""
        create_application(status='submitted')
        create_application(status='accepted')
        create_application(status='rejected')
        
        response = client.get(
            '/api/v1/admin/applications?status=submitted',
            headers=admin_auth_headers
        )
        
        assert response.status_code == 200
        data = response.get_json()
        for app in data['data']['applications']:
            assert app['status'] == 'submitted'
    
    def test_admin_search_applications(self, client, admin_auth_headers, create_application, applicant_user):
        """Test searching applications by applicant name"""
        create_application()
        
        response = client.get(
            f'/api/v1/admin/applications?search={applicant_user.first_name}',
            headers=admin_auth_headers
        )
        
        assert response.status_code == 200
    
    def test_admin_view_single_application(self, client, admin_auth_headers, create_application):
        """Test admin can view single application details"""
        app = create_application(status='submitted')
        
        response = client.get(
            f'/api/v1/admin/applications/{app.id}',
            headers=admin_auth_headers
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['data']['application']['id'] == app.id
    
    def test_non_admin_cannot_view_all_applications(self, client, auth_headers):
        """Test non-admin cannot access admin endpoints"""
        response = client.get(
            '/api/v1/admin/applications',
            headers=auth_headers
        )
        
        assert response.status_code == 403


class TestApplicationDecisionWorkflow:
    """Test application decision workflows"""
    
    def test_admin_accept_application(self, client, admin_auth_headers, create_application):
        """Test admin can accept an application"""
        app = create_application(status='under_review')
        
        decision_payload = {
            'decision': 'accept',
            'notes': 'Qualified applicant with excellent grades'
        }
        
        response = client.post(
            f'/api/v1/admin/applications/{app.id}/decision',
            json=decision_payload,
            headers=admin_auth_headers
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['data']['application']['status'] == 'accepted'
    
    def test_admin_reject_application(self, client, admin_auth_headers, create_application):
        """Test admin can reject an application with reason"""
        app = create_application(status='under_review')
        
        decision_payload = {
            'decision': 'reject',
            'notes': 'Does not meet minimum entry requirements',
            'reason_code': 'insufficient_grades'
        }
        
        response = client.post(
            f'/api/v1/admin/applications/{app.id}/decision',
            json=decision_payload,
            headers=admin_auth_headers
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['data']['application']['status'] == 'rejected'
        assert data['data']['application']['status_reason'] is not None
    
    def test_admin_waitlist_application(self, client, admin_auth_headers, create_application):
        """Test admin can waitlist an application"""
        app = create_application(status='under_review')
        
        decision_payload = {
            'decision': 'waitlist',
            'notes': 'Qualified but program is full'
        }
        
        response = client.post(
            f'/api/v1/admin/applications/{app.id}/decision',
            json=decision_payload,
            headers=admin_auth_headers
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['data']['application']['status'] == 'waitlisted'
    
    def test_admin_request_documents(self, client, admin_auth_headers, create_application):
        """Test admin can request additional documents"""
        app = create_application(status='submitted')
        
        request_payload = {
            'document_type': 'transcript',
            'notes': 'Please upload certified academic transcript'
        }
        
        response = client.post(
            f'/api/v1/admin/applications/{app.id}/request-documents',
            json=request_payload,
            headers=admin_auth_headers
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['data']['application']['status'] == 'documents_pending'


class TestInterviewScheduling:
    """Test interview scheduling workflows"""
    
    def test_admin_schedule_interview(self, client, admin_auth_headers, create_application):
        """Test admin can schedule an interview"""
        app = create_application(status='under_review')
        
        interview_payload = {
            'interview_date': '2026-07-15T10:00:00',
            'location': 'KIU Main Campus, Room 205',
            'interviewer': 'Dr. Jane Smith',
            'notes': 'Bring original certificates'
        }
        
        response = client.post(
            f'/api/v1/admin/applications/{app.id}/schedule-interview',
            json=interview_payload,
            headers=admin_auth_headers
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['data']['application']['status'] == 'interview_scheduled'
        assert 'interview_date' in data['data']['application']
    
    def test_admin_update_interview(self, client, admin_auth_headers, create_application):
        """Test admin can reschedule an interview"""
        app = create_application(status='interview_scheduled')
        
        update_payload = {
            'interview_date': '2026-07-20T14:00:00',
            'location': 'KIU Main Campus, Room 301',
            'notes': 'Rescheduled due to conflict'
        }
        
        response = client.put(
            f'/api/v1/admin/applications/{app.id}/interview',
            json=update_payload,
            headers=admin_auth_headers
        )
        
        assert response.status_code == 200
    
    def test_admin_record_interview_notes(self, client, admin_auth_headers, create_application):
        """Test admin can record interview notes"""
        app = create_application(status='interview_scheduled')
        
        notes_payload = {
            'interview_notes': 'Strong candidate, good communication skills',
            'recommendation': 'accept'
        }
        
        response = client.post(
            f'/api/v1/admin/applications/{app.id}/interview-notes',
            json=notes_payload,
            headers=admin_auth_headers
        )
        
        assert response.status_code == 200


class TestProgramManagement:
    """Test program management by admin"""
    
    def test_admin_create_program(self, client, admin_auth_headers):
        """Test admin can create new program"""
        program_payload = {
            'code': 'NEW-PROG',
            'name': 'New Test Program',
            'level': 'bachelor',
            'faculty': 'Science and Technology',
            'campus': 'kampala',
            'duration_years': 3,
            'duration_semesters': 6,
            'tuition_ugx': 1_800_000,
            'functional_fee_ugx': 353_000,
            'entry_requirements': {
                'min_points': 10,
                'essential_subjects': ['Mathematics', 'Physics'],
                'min_principal_passes': 2
            }
        }
        
        response = client.post(
            '/api/v1/admin/programs',
            json=program_payload,
            headers=admin_auth_headers
        )
        
        assert response.status_code == 201
        data = response.get_json()
        assert data['data']['program']['code'] == 'NEW-PROG'
    
    def test_admin_update_program(self, client, admin_auth_headers, sample_programs):
        """Test admin can update existing program"""
        program = sample_programs['bachelor']
        
        update_payload = {
            'tuition_ugx': 2_000_000,  # Updated fee
            'is_admission_open': False  # Close admissions
        }
        
        response = client.put(
            f'/api/v1/admin/programs/{program.id}',
            json=update_payload,
            headers=admin_auth_headers
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['data']['program']['tuition_ugx'] == 2_000_000
        assert data['data']['program']['is_admission_open'] is False
    
    def test_admin_deactivate_program(self, client, admin_auth_headers, sample_programs):
        """Test admin can deactivate a program"""
        program = sample_programs['certificate']
        
        response = client.delete(
            f'/api/v1/admin/programs/{program.id}',
            headers=admin_auth_headers
        )
        
        assert response.status_code == 200
        
        # Verify program is deactivated
        get_response = client.get(f'/api/v1/programs/{program.id}')
        assert get_response.get_json()['data']['program']['is_active'] is False
    
    def test_non_admin_cannot_create_program(self, client, auth_headers):
        """Test non-admin cannot create programs"""
        program_payload = {
            'code': 'UNAUTH-PROG',
            'name': 'Unauthorized Program',
            'level': 'bachelor'
        }
        
        response = client.post(
            '/api/v1/admin/programs',
            json=program_payload,
            headers=auth_headers
        )
        
        assert response.status_code == 403


class TestIntakeManagement:
    """Test admission intake management"""
    
    def test_admin_create_intake(self, client, admin_auth_headers):
        """Test admin can create new intake"""
        intake_payload = {
            'name': 'January 2027',
            'academic_year': '2026/2027',
            'semester': 'Semester 2',
            'start_date': '2027-01-15',
            'end_date': '2027-05-30',
            'application_opens': '2026-09-01',
            'application_deadline': '2027-01-10'
        }
        
        response = client.post(
            '/api/v1/admin/intakes',
            json=intake_payload,
            headers=admin_auth_headers
        )
        
        assert response.status_code == 201
        data = response.get_json()
        assert data['data']['intake']['name'] == 'January 2027'
    
    def test_admin_close_intake(self, client, admin_auth_headers, active_intake):
        """Test admin can close an intake"""
        response = client.post(
            f'/api/v1/admin/intakes/{active_intake.id}/close',
            headers=admin_auth_headers
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['data']['intake']['is_admission_open'] is False
    
    def test_admin_extend_deadline(self, client, admin_auth_headers, active_intake):
        """Test admin can extend application deadline"""
        extension_payload = {
            'new_deadline': '2026-09-15',
            'reason': 'High demand, extending for 2 more weeks'
        }
        
        response = client.put(
            f'/api/v1/admin/intakes/{active_intake.id}/deadline',
            json=extension_payload,
            headers=admin_auth_headers
        )
        
        assert response.status_code == 200


class TestReportsAndAnalytics:
    """Test admin reports and analytics"""
    
    def test_admin_view_application_statistics(self, client, admin_auth_headers, create_application):
        """Test admin can view application statistics"""
        # Create applications with different statuses
        create_application(status='submitted')
        create_application(status='accepted')
        create_application(status='rejected')
        
        response = client.get(
            '/api/v1/admin/statistics/applications',
            headers=admin_auth_headers
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'total_applications' in data['data']
        assert 'by_status' in data['data']
        assert 'by_program' in data['data']
    
    def test_admin_view_enrollment_report(self, client, admin_auth_headers, create_application):
        """Test admin can view enrollment report"""
        create_application(status='accepted')
        create_application(status='enrolled')
        
        response = client.get(
            '/api/v1/admin/reports/enrollment',
            headers=admin_auth_headers
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'enrollment_by_program' in data['data']
    
    def test_admin_export_applications(self, client, admin_auth_headers, create_application):
        """Test admin can export applications to CSV/Excel"""
        create_application(status='submitted')
        
        response = client.get(
            '/api/v1/admin/applications/export?format=csv',
            headers=admin_auth_headers
        )
        
        assert response.status_code == 200
        assert response.content_type in ['text/csv', 'application/vnd.ms-excel']


class TestUserManagement:
    """Test user management by admin"""
    
    def test_admin_view_all_users(self, client, admin_auth_headers, applicant_user, admin_user):
        """Test admin can view all users"""
        response = client.get(
            '/api/v1/admin/users',
            headers=admin_auth_headers
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert len(data['data']['users']) >= 2
    
    def test_admin_filter_users_by_role(self, client, admin_auth_headers, applicant_user, admin_user):
        """Test admin can filter users by role"""
        response = client.get(
            '/api/v1/admin/users?role=applicant',
            headers=admin_auth_headers
        )
        
        assert response.status_code == 200
        data = response.get_json()
        for user in data['data']['users']:
            assert user['role'] == 'applicant'
    
    def test_admin_deactivate_user(self, client, admin_auth_headers, applicant_user):
        """Test admin can deactivate a user"""
        response = client.post(
            f'/api/v1/admin/users/{applicant_user.id}/deactivate',
            headers=admin_auth_headers
        )
        
        assert response.status_code == 200
        
        # Verify user cannot login
        login_response = client.post('/api/v1/auth/login', json={
            'email': applicant_user.email,
            'password': 'TestPassword123!'
        })
        assert login_response.status_code == 403
    
    def test_admin_activate_user(self, client, admin_auth_headers, applicant_user):
        """Test admin can reactivate a deactivated user"""
        # First deactivate
        applicant_user.is_active = False
        
        response = client.post(
            f'/api/v1/admin/users/{applicant_user.id}/activate',
            headers=admin_auth_headers
        )
        
        assert response.status_code == 200
    
    def test_admin_change_user_role(self, client, admin_auth_headers, applicant_user):
        """Test admin can change user role"""
        role_payload = {
            'new_role': 'finalist',
            'reason': 'Completed degree, now a finalist'
        }
        
        response = client.put(
            f'/api/v1/admin/users/{applicant_user.id}/role',
            json=role_payload,
            headers=admin_auth_headers
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['data']['user']['role'] == 'finalist'


class TestAuditLogs:
    """Test audit logging functionality"""
    
    def test_admin_view_audit_logs(self, client, admin_auth_headers, create_application):
        """Test admin can view audit logs"""
        app = create_application()
        
        # Make some changes to generate logs
        client.post(
            f'/api/v1/admin/applications/{app.id}/decision',
            json={'decision': 'accept'},
            headers=admin_auth_headers
        )
        
        response = client.get(
            f'/api/v1/admin/applications/{app.id}/audit-log',
            headers=admin_auth_headers
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert len(data['data']['logs']) > 0
    
    def test_audit_log_records_admin_actions(self, client, admin_auth_headers, create_application, admin_user):
        """Test that admin actions are recorded in audit log"""
        app = create_application()
        
        client.post(
            f'/api/v1/admin/applications/{app.id}/decision',
            json={'decision': 'accept', 'notes': 'Approved'},
            headers=admin_auth_headers
        )
        
        # Check log contains admin action
        response = client.get(
            f'/api/v1/admin/applications/{app.id}/audit-log',
            headers=admin_auth_headers
        )
        
        data = response.get_json()
        latest_log = data['data']['logs'][0]
        assert latest_log['action'] == 'application_decision'
        assert latest_log['admin_id'] == admin_user.id


class TestFeeManagement:
    """Test fee structure management"""
    
    def test_admin_update_program_fees(self, client, admin_auth_headers, sample_programs):
        """Test admin can update program fees"""
        program = sample_programs['bachelor']
        
        fee_payload = {
            'tuition_ugx': 1_750_000,
            'functional_fee_ugx': 400_000,
            'effective_date': '2026-09-01',
            'reason': 'Annual fee adjustment'
        }
        
        response = client.put(
            f'/api/v1/admin/programs/{program.id}/fees',
            json=fee_payload,
            headers=admin_auth_headers
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['data']['program']['tuition_ugx'] == 1_750_000
    
    def test_admin_view_fee_history(self, client, admin_auth_headers, sample_programs):
        """Test admin can view fee change history"""
        program = sample_programs['bachelor']
        
        response = client.get(
            f'/api/v1/admin/programs/{program.id}/fee-history',
            headers=admin_auth_headers
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'fee_changes' in data['data']
