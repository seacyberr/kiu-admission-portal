"""Integration tests for full user flows."""
import pytest
import json


class TestRegistrationAndVerificationFlow:
    """Test the complete registration and OTP verification flow."""

    def test_register_verify_login_flow(self, client):
        """Test: Register → Verify OTP → Login → Get Profile."""
        # Step 1: Register
        register_response = client.post("/api/auth/register", json={
            "email": "integration@test.com",
            "password": "testpass123",
            "firstName": "Integration",
            "lastName": "Test"
        })
        assert register_response.status_code == 201
        register_data = register_response.get_json()
        assert register_data["needsVerification"] is True

        # Step 2: Get OTP from database (simulating terminal output)
        from models import OtpCode, User
        with client.application.app_context():
            user = User.query.filter_by(email="integration@test.com").first()
            otp = OtpCode.query.filter_by(user_id=user.id, is_used=False).first()
            otp_code = otp.code

        # Step 3: Verify OTP
        verify_response = client.post("/api/auth/verify-otp", json={
            "email": "integration@test.com",
            "code": otp_code
        })
        assert verify_response.status_code == 200
        verify_data = verify_response.get_json()
        assert "token" in verify_data
        token = verify_data["token"]

        # Step 4: Login (should work now)
        login_response = client.post("/api/auth/login", json={
            "email": "integration@test.com",
            "password": "testpass123"
        })
        assert login_response.status_code == 200
        login_data = login_response.get_json()
        assert "token" in login_data

        # Step 5: Get profile
        me_response = client.get("/api/auth/me", headers={
            "Authorization": f"Bearer {token}"
        })
        assert me_response.status_code == 200
        me_data = me_response.get_json()
        assert me_data["email"] == "integration@test.com"


class TestAdmissionApplicationFlow:
    """Test the complete admission application flow."""

    def test_apply_and_review_flow(self, client):
        """Test: Create user → Apply → Admin reviews → Update status."""
        from models import db, User, Program

        # Setup: Create verified applicant
        with client.application.app_context():
            applicant = User(
                email="applicant@integration.com",
                first_name="Test",
                last_name="Applicant",
                role="applicant",
                is_verified=True
            )
            applicant.set_password("testpass123")
            db.session.add(applicant)

            program = Program(
                name="Test Program",
                code="TP101",
                faculty="Test Faculty",
                level="degree",
                duration="3 years",
                available_slots=50
            )
            db.session.add(program)
            db.session.commit()
            program_id = program.id

        # Step 1: Applicant logs in
        login_response = client.post("/api/auth/login", json={
            "email": "applicant@integration.com",
            "password": "testpass123"
        })
        assert login_response.status_code == 200
        token = login_response.get_json()["token"]

        # Step 2: Submit application
        app_response = client.post("/api/admission/applications",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "programIds": [program_id],
                "examLevel": "a_level",
                "examYear": 2023,
                "indexNumber": "U1234/001",
                "unebGrades": {
                    "olevel": [
                        {"subject": "Math", "grade": "D1", "points": 1},
                        {"subject": "English", "grade": "D2", "points": 2},
                        {"subject": "Physics", "grade": "C3", "points": 3},
                        {"subject": "Chemistry", "grade": "C4", "points": 4},
                        {"subject": "Biology", "grade": "C5", "points": 5}
                    ],
                    "alevel": [
                        {"subject": "Math", "grade": "A", "points": 6, "subjectType": "principal"},
                        {"subject": "Physics", "grade": "B", "points": 5, "subjectType": "principal"}
                    ]
                },
                "dateOfBirth": "2000-01-15",
                "gender": "male",
                "nationality": "Ugandan",
                "district": "Kampala"
            }
        )
        assert app_response.status_code == 201
        app_data = app_response.get_json()
        assert app_data["status"] == "pending"
        app_id = app_data["id"]

        # Step 3: Create admin and review
        with client.application.app_context():
            admin = User(
                email="admin@integration.com",
                first_name="Admin",
                last_name="User",
                role="admin",
                is_verified=True
            )
            admin.set_password("adminpass123")
            db.session.add(admin)
            db.session.commit()

        admin_login = client.post("/api/auth/login", json={
            "email": "admin@integration.com",
            "password": "adminpass123"
        })
        admin_token = admin_login.get_json()["token"]

        # Step 4: Admin updates status
        update_response = client.patch(
            f"/api/admission/applications/{app_id}/status",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={"status": "accepted", "adminNotes": "Excellent results"}
        )
        assert update_response.status_code == 200
        update_data = update_response.get_json()
        assert update_data["status"] == "accepted"


class TestOpportunityApplicationFlow:
    """Test the opportunity listing and application flow."""

    def test_browse_and_apply_opportunity(self, client):
        """Test: List opportunities → View details → Apply."""
        from models import db, User, Opportunity
        from datetime import date, timedelta

        # Setup: Create opportunity
        with client.application.app_context():
            opp = Opportunity(
                title="Test Internship",
                organization="Test Corp",
                type="internship",
                description="A test internship",
                requirements="Final year student",
                application_deadline=date.today() + timedelta(days=30),
                is_active=True
            )
            db.session.add(opp)

            applicant = User(
                email="jobseeker@test.com",
                first_name="Job",
                last_name="Seeker",
                role="finalist",
                is_verified=True
            )
            applicant.set_password("testpass123")
            db.session.add(applicant)
            db.session.commit()
            opp_id = opp.id

        # Step 1: Login as finalist
        login_response = client.post("/api/auth/login", json={
            "email": "jobseeker@test.com",
            "password": "testpass123"
        })
        token = login_response.get_json()["token"]

        # Step 2: List opportunities
        list_response = client.get("/api/opportunities")
        assert list_response.status_code == 200
        opps = list_response.get_json()["opportunities"]
        assert len(opps) > 0

        # Step 3: View opportunity details
        detail_response = client.get(f"/api/opportunities/{opp_id}")
        assert detail_response.status_code == 200

        # Step 4: Apply for opportunity
        apply_response = client.post(
            f"/api/opportunities/{opp_id}/apply",
            headers={"Authorization": f"Bearer {token}"},
            json={"coverLetter": "I am very interested in this position..."}
        )
        assert apply_response.status_code == 201

        # Step 5: Check my applications
        my_apps = client.get(
            "/api/opportunities/applications/my",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert my_apps.status_code == 200
        apps = my_apps.get_json()["applications"]
        assert len(apps) == 1