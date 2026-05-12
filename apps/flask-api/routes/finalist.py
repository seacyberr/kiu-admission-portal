"""Finalist Routes for KIU Admission Portal

Provides finalist portal endpoints for admitted students
"""

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from models import db, User, AdmissionApplication, FinalistProfile, Program
from routes.auth import get_current_user
from datetime import datetime
from utils.api_response import success_response, paginated_response, bad_request, unauthorized, forbidden, not_found, created
from utils.decorators import require_auth

finalist_bp = Blueprint("finalist", __name__)


def check_finalist_access():
    """Verify user is a finalist (admitted applicant)"""
    user, error = get_current_user()
    if error:
        return None, unauthorized(error)
    
    # Check if user has an approved application (is a finalist)
    approved_app = AdmissionApplication.query.filter_by(
        user_id=user.id, status="approved"
    ).first()
    
    if not approved_app and user.role != "admin":
        return None, forbidden("Finalist access required. Your application has not been approved yet.")
    
    return user, None, approved_app


@finalist_bp.route("/profile", methods=["GET"])
@jwt_required()
def get_finalist_profile():
    """Get finalist profile information"""
    result = check_finalist_access()
    if len(result) == 2:
        return result
    user, error, approved_app = result
    
    # Get or create finalist profile
    profile = FinalistProfile.query.filter_by(user_id=user.id).first()
    if not profile:
        profile = FinalistProfile(user_id=user.id, application_id=approved_app.id)
        db.session.add(profile)
        db.session.commit()
    
    return success_response({
        "user": user.to_dict(),
        "application": approved_app.to_dict() if approved_app else None,
        "profile": profile.to_dict() if profile else None
    })


@finalist_bp.route("/status", methods=["GET"])
@jwt_required()
def get_finalist_status():
    """Get finalist admission status"""
    result = check_finalist_access()
    if len(result) == 2:
        return result
    user, error, approved_app = result
    
    return success_response({
        "admission_status": "approved" if approved_app else "pending",
        "program": approved_app.program_name if approved_app else None,
        "enrollment_status": approved_app.enrollment_status if approved_app else "not_enrolled",
        "enrollment_date": approved_app.enrollment_date.isoformat() if approved_app and approved_app.enrollment_date else None,
        "next_steps": [
            "Complete student ID registration",
            "Submit required documents",
            "Attend orientation"
        ] if approved_app else ["Wait for admission decision"]
    })


@finalist_bp.route("/documents", methods=["GET"])
@jwt_required()
def get_finalist_documents():
    """Get required documents for finalist"""
    result = check_finalist_access()
    if len(result) == 2:
        return result
    user, error, approved_app = result
    
    required_documents = [
        {"name": "Birth Certificate", "required": True, "submitted": False},
        {"name": "O-Level Certificate", "required": True, "submitted": False},
        {"name": "A-Level Certificate", "required": True, "submitted": False},
        {"name": "National ID/Passport", "required": True, "submitted": False},
        {"name": "Medical Examination Form", "required": True, "submitted": False},
        {"name": "Passport Photos (4)", "required": True, "submitted": False},
        {"name": "Recommendation Letters", "required": False, "submitted": False},
    ]
    
    return success_response({
        "documents": required_documents,
        "all_submitted": False,
        "submission_deadline": "2025-09-01"
    })




@finalist_bp.route("/profile", methods=["PUT"])
@jwt_required()
def update_finalist_profile():
    """Update finalist profile"""
    result = check_finalist_access()
    if len(result) == 2:
        return result
    user, error, approved_app = result
    
    data = request.get_json()
    
    # Update user information
    if "first_name" in data:
        user.first_name = data["first_name"]
    if "last_name" in data:
        user.last_name = data["last_name"]
    if "phone" in data:
        user.phone = data["phone"]
    
    # Update student profile if exists
    profile = FinalistProfile.query.filter_by(user_id=user.id).first()
    if not profile:
        profile = FinalistProfile(user_id=user.id, application_id=approved_app.id if approved_app else None, is_finalist=True)
        db.session.add(profile)
    
    # Update profile fields
    profile_fields = [
        "student_number", "year_of_study", "graduation_year", "gpa",
        "skills", "bio", "cv_url", "is_finalist"
    ]
    
    for field in profile_fields:
        if field in data:
            setattr(profile, field, data[field])
    
    db.session.commit()
    
    return success_response(
        profile.to_dict() if hasattr(profile, 'to_dict') else vars(profile),
        message="Profile updated successfully"
    )


# Admin endpoints for finalist management
@finalist_bp.route("/admin/list", methods=["GET"])
@jwt_required()
def list_finalists():
    """Admin: List all finalists with filters"""
    # Check admin access
    admin_check = get_current_user()
    if len(admin_check) == 2:
        return admin_check
    user, error = admin_check
    if error or user.role not in ["admin", "staff"]:
        return forbidden("Admin access required")
    
    # Query parameters
    program = request.args.get("program")
    faculty = request.args.get("faculty")
    year_of_study = request.args.get("year_of_study", type=int)
    status = request.args.get("status")
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)
    
    # Build query
    query = AdmissionApplication.query.filter(
        AdmissionApplication.enrollment_status.in_(["enrolled", "final_year"])
    )
    
    if program:
        query = query.filter(AdmissionApplication.program_name.ilike(f"%{program}%"))
    if year_of_study:
        query = query.filter(AdmissionApplication.current_year_of_study == year_of_study)
    
    # Get paginated results
    pagination = query.order_by(AdmissionApplication.updated_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    finalists = []
    for app in pagination.items:
        user = User.query.get(app.user_id)
        finalists.append({
            "id": app.id,
            "user_id": app.user_id,
            "student_name": f"{user.first_name} {user.last_name}" if user else "Unknown",
            "email": user.email if user else None,
            "program": app.program_name,
            "student_number": app.student_number,
            "current_year": app.current_year_of_study,
            "expected_graduation": app.expected_graduation_year,
            "enrollment_status": app.enrollment_status,
            "cgpa": app.cgpa if hasattr(app, 'cgpa') else None,
            "updated_at": app.updated_at.isoformat() if app.updated_at else None
        })
    
    return paginated_response(
        items=finalists,
        total=pagination.total,
        page=page,
        per_page=per_page,
        data_key="finalists"
    )


@finalist_bp.route("/admin/statistics", methods=["GET"])
@jwt_required()
def get_finalist_statistics():
    """Admin: Get finalist statistics"""
    admin_check = get_current_user()
    if len(admin_check) == 2:
        return admin_check
    user, error = admin_check
    if error or user.role not in ["admin", "staff"]:
        return forbidden("Admin access required")
    
    # Total finalists
    total_finalists = AdmissionApplication.query.filter(
        AdmissionApplication.enrollment_status.in_(["enrolled", "final_year"])
    ).count()
    
    # By program
    program_counts = db.session.query(
        AdmissionApplication.program_name,
        db.func.count(AdmissionApplication.id)
    ).filter(
        AdmissionApplication.enrollment_status.in_(["enrolled", "final_year"])
    ).group_by(AdmissionApplication.program_name).all()
    
    # By year of study
    year_counts = db.session.query(
        AdmissionApplication.current_year_of_study,
        db.func.count(AdmissionApplication.id)
    ).filter(
        AdmissionApplication.enrollment_status.in_(["enrolled", "final_year"])
    ).group_by(AdmissionApplication.current_year_of_study).all()
    
    # Expected graduation years
    graduation_counts = db.session.query(
        AdmissionApplication.expected_graduation_year,
        db.func.count(AdmissionApplication.id)
    ).filter(
        AdmissionApplication.enrollment_status.in_(["enrolled", "final_year"]),
        AdmissionApplication.expected_graduation_year.isnot(None)
    ).group_by(AdmissionApplication.expected_graduation_year).all()
    
    return success_response({
        "total_finalists": total_finalists,
        "by_program": {prog: count for prog, count in program_counts},
        "by_year": {str(year): count for year, count in year_counts if year},
        "by_graduation_year": {str(year): count for year, count in graduation_counts},
        "generated_at": datetime.utcnow().isoformat()
    })


@finalist_bp.route("/admin/graduate", methods=["POST"])
@jwt_required()
def mark_as_graduated():
    """Admin: Mark finalist as graduated"""
    admin_check = get_current_user()
    if len(admin_check) == 2:
        return admin_check
    user, error = admin_check
    if error or user.role not in ["admin", "staff"]:
        return forbidden("Admin access required")
    
    data = request.get_json()
    application_id = data.get("application_id")
    
    if not application_id:
        return bad_request("Application ID required", errors={"application_id": "Required"})
    
    app = AdmissionApplication.query.get(application_id)
    if not app:
        return not_found("Application not found")
    
    # Update status
    app.enrollment_status = "graduated"
    app.graduation_date = datetime.utcnow()
    app.current_year_of_study = app.program_duration_years if hasattr(app, 'program_duration_years') else 4
    
    db.session.commit()
    
    return success_response({
        "application_id": application_id,
        "graduation_date": app.graduation_date.isoformat() if app.graduation_date else None
    }, message="Student marked as graduated")


@finalist_bp.route("/clearance", methods=["GET"])
@jwt_required()
def get_clearance_status():
    """Get student clearance status"""
    result = check_finalist_access()
    if len(result) == 2:
        return result
    user, error, approved_app = result
    
    # Mock clearance data - in production, this would come from various departments
    clearance_items = [
        {"department": "Library", "status": "cleared", "notes": "No outstanding books"},
        {"department": "Finance", "status": approved_app.fees_balance == 0 if hasattr(approved_app, 'fees_balance') else True, "notes": "All fees paid"},
        {"department": "Academic", "status": "cleared", "notes": "All courses completed"},
        {"department": "Hostel", "status": "cleared", "notes": "Room checked out"},
        {"department": "Student Affairs", "status": "pending", "notes": "Student ID card not returned"},
    ]
    
    all_cleared = all(item["status"] == "cleared" or item["status"] == True for item in clearance_items)
    
    return success_response({
        "clearance_items": clearance_items,
        "all_cleared": all_cleared,
        "can_graduate": all_cleared
    }, message="All clearance items completed! You can proceed to graduation." if all_cleared else "Please complete all clearance items.")


@finalist_bp.route("/career-prep", methods=["GET"])
@jwt_required()
def get_career_preparation():
    """Get career preparation resources for finalists"""
    result = check_finalist_access()
    if len(result) == 2:
        return result
    user, error, approved_app = result
    
    # Get program-specific career paths
    program = Program.query.filter_by(name=approved_app.program_name).first()
    career_paths = program.career_paths if program and hasattr(program, 'career_paths') else []
    
    # Mock career prep resources
    resources = {
        "resume_workshop": {
            "available": True,
            "dates": ["2025-06-15", "2025-07-20"],
            "registration_open": True
        },
        "interview_prep": {
            "available": True,
            "dates": ["2025-06-20", "2025-07-25"],
            "registration_open": True
        },
        "job_fair": {
            "available": True,
            "date": "2025-08-10",
            "employers_registered": 45
        },
        "career_counseling": {
            "available": True,
            "bookings_open": True
        },
        "alumni_mentorship": {
            "available": True,
            "mentors_available": 120
        }
    }
    
    return success_response({
        "career_paths": career_paths,
        "resources": resources,
        "recommended_actions": [
            "Join the KIU alumni network",
            "Attend career fairs and networking events",
            "Consider postgraduate studies if interested"
        ]
    })
