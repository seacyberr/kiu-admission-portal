"""
Report Generation System for KIU Admission Portal
Provides comprehensive reporting for administrators
"""
import io
import csv
from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify, current_app, Response
from sqlalchemy import func, and_, or_
from models import (
    db, AdmissionApplication, Program, User,
    ApplicationStatusHistory, OpportunityApplication
)
from routes.auth import get_current_user
from utils.api_response import success_response, bad_request, unauthorized, forbidden

reports_bp = Blueprint("reports", __name__)


def check_admin_access():
    """Verify user is admin"""
    user, error = get_current_user()
    if error:
        return None, unauthorized(error)
    if user.role != "admin":
        return None, forbidden("Admin access required")
    return user, None


@reports_bp.route("/dashboard-stats", methods=["GET"])
def get_dashboard_stats():
    """Get dashboard statistics for admin"""
    user, error = check_admin_access()
    if error:
        return error
    
    # Date filters
    days = request.args.get("days", 30, type=int)
    since = datetime.utcnow() - timedelta(days=days)
    
    # Application statistics
    total_applications = AdmissionApplication.query.count()
    recent_applications = AdmissionApplication.query.filter(
        AdmissionApplication.submitted_at >= since
    ).count()
    
    applications_by_status = db.session.query(
        AdmissionApplication.status,
        func.count(AdmissionApplication.id)
    ).group_by(AdmissionApplication.status).all()
    
    # Payment statistics
    total_payments = Payment.query.filter_by(status="successful").count()
    total_revenue = db.session.query(
        func.sum(Payment.amount)
    ).filter(Payment.status == "successful").scalar() or 0
    
    recent_payments = Payment.query.filter(
        Payment.created_at >= since,
        Payment.status == "successful"
    ).count()
    
    # Program statistics
    applications_by_program = db.session.query(
        Program.name,
        func.count(AdmissionApplication.id)
    ).join(AdmissionApplication).group_by(Program.id).order_by(
        func.count(AdmissionApplication.id).desc()
    ).limit(10).all()
    
    # User statistics
    total_users = User.query.count()
    new_users = User.query.filter(User.created_at >= since).count()
    
    return success_response({
        "period": f"Last {days} days",
        "applications": {
            "total": total_applications,
            "recent": recent_applications,
            "by_status": {status: count for status, count in applications_by_status}
        },
        "payments": {
            "total_count": total_payments,
            "recent_count": recent_payments,
            "total_revenue_ugx": total_revenue,
            "total_revenue_formatted": f"UGX {total_revenue:,.0f}"
        },
        "programs": {
            "top_10": [{"program": name, "applications": count} for name, count in applications_by_program]
        },
        "users": {
            "total": total_users,
            "new": new_users
        }
    })


@reports_bp.route("/applications", methods=["GET"])
def get_applications_report():
    """Generate applications report with filters"""
    user, error = check_admin_access()
    if error:
        return error
    
    # Query parameters
    status = request.args.get("status")
    program_id = request.args.get("program_id", type=int)
    exam_level = request.args.get("exam_level")
    campus = request.args.get("campus")
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")
    export_format = request.args.get("format", "json")  # json, csv
    
    # Build query
    query = AdmissionApplication.query.join(User).join(Program)
    
    if status:
        query = query.filter(AdmissionApplication.status == status)
    if program_id:
        query = query.filter(AdmissionApplication.program_id == program_id)
    if exam_level:
        query = query.filter(AdmissionApplication.exam_level == exam_level)
    if campus:
        query = query.filter(Program.campus == campus)
    if start_date:
        query = query.filter(AdmissionApplication.submitted_at >= start_date)
    if end_date:
        query = query.filter(AdmissionApplication.submitted_at <= end_date)
    
    applications = query.order_by(AdmissionApplication.submitted_at.desc()).all()
    
    # Prepare data
    data = []
    for app in applications:
        data.append({
            "id": app.id,
            "application_number": app.application_number,
            "applicant_name": f"{app.user.first_name} {app.user.last_name}",
            "applicant_email": app.user.email,
            "applicant_phone": app.user.phone,
            "program": app.program.name,
            "campus": app.program.campus,
            "faculty": app.program.faculty,
            "exam_level": app.exam_level,
            "index_number": app.index_number,
            "status": app.status,
            "payment_status": app.payment_status,
            "submitted_at": app.submitted_at.isoformat() if app.submitted_at else None,
            "district": app.district,
            "gender": app.gender
        })
    
    if export_format == "csv":
        return export_to_csv(data, "applications_report.csv")
    
    return success_response({
        "count": len(data),
        "applications": data
    })


@reports_bp.route("/payments", methods=["GET"])
def get_payments_report():
    """Generate payments report"""
    user, error = check_admin_access()
    if error:
        return error
    
    # Query parameters
    status = request.args.get("status")
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")
    export_format = request.args.get("format", "json")
    
    query = Payment.query.join(User).join(AdmissionApplication)
    
    if status:
        query = query.filter(Payment.status == status)
    if start_date:
        query = query.filter(Payment.created_at >= start_date)
    if end_date:
        query = query.filter(Payment.created_at <= end_date)
    
    payments = query.order_by(Payment.created_at.desc()).all()
    
    total_amount = sum(p.amount for p in payments if p.status == "successful")
    
    data = []
    for payment in payments:
        data.append({
            "id": payment.id,
            "reference": payment.reference,
            "applicant_name": f"{payment.user.first_name} {payment.user.last_name}",
            "applicant_email": payment.user.email,
            "amount": payment.amount,
            "currency": payment.currency,
            "status": payment.status,
            "phone_number": payment.phone_number,
            "application_number": payment.application.application_number if payment.application else None,
            "created_at": payment.created_at.isoformat() if payment.created_at else None,
            "paid_at": payment.paid_at.isoformat() if payment.paid_at else None
        })
    
    if export_format == "csv":
        return export_to_csv(data, "payments_report.csv")
    
    return success_response({
        "count": len(data),
        "total_amount_ugx": total_amount,
        "total_amount_formatted": f"UGX {total_amount:,.0f}",
        "payments": data
    })


@reports_bp.route("/program-analytics/<int:program_id>", methods=["GET"])
def get_program_analytics(program_id):
    """Get detailed analytics for a specific program"""
    user, error = check_admin_access()
    if error:
        return error
    
    program = Program.query.get_or_404(program_id)
    
    # Application statistics
    total_applications = AdmissionApplication.query.filter_by(program_id=program_id).count()
    
    by_status = db.session.query(
        AdmissionApplication.status,
        func.count(AdmissionApplication.id)
    ).filter_by(program_id=program_id).group_by(AdmissionApplication.status).all()
    
    by_exam_level = db.session.query(
        AdmissionApplication.exam_level,
        func.count(AdmissionApplication.id)
    ).filter_by(program_id=program_id).group_by(AdmissionApplication.exam_level).all()
    
    by_payment_status = db.session.query(
        AdmissionApplication.payment_status,
        func.count(AdmissionApplication.id)
    ).filter_by(program_id=program_id).group_by(AdmissionApplication.payment_status).all()
    
    # Conversion metrics
    paid_count = sum(1 for s, c in by_payment_status if s == "paid" for _ in range(c))
    conversion_rate = (paid_count / total_applications * 100) if total_applications > 0 else 0
    
    # Daily trend (last 30 days)
    days = 30
    daily_stats = []
    for i in range(days):
        date = datetime.utcnow() - timedelta(days=i)
        count = AdmissionApplication.query.filter(
            func.date(AdmissionApplication.submitted_at) == date.date(),
            AdmissionApplication.program_id == program_id
        ).count()
        daily_stats.append({
            "date": date.strftime("%Y-%m-%d"),
            "applications": count
        })
    
    return success_response({
        "program": {
            "id": program.id,
            "name": program.name,
            "code": program.code,
            "faculty": program.faculty,
            "campus": program.campus
        },
        "summary": {
            "total_applications": total_applications,
            "by_status": {status: count for status, count in by_status},
            "by_exam_level": {level: count for level, count in by_exam_level},
            "by_payment_status": {status: count for status, count in by_payment_status},
            "conversion_rate": round(conversion_rate, 2)
        },
        "daily_trend": list(reversed(daily_stats))
    })


@reports_bp.route("/enrollment-forecast", methods=["GET"])
def get_enrollment_forecast():
    """Get enrollment forecast based on current trends"""
    user, error = check_admin_access()
    if error:
        return error
    
    # Current statistics
    current_month_start = datetime.utcnow().replace(day=1)
    
    monthly_applications = db.session.query(
        func.date_trunc('month', AdmissionApplication.submitted_at),
        func.count(AdmissionApplication.id)
    ).group_by(
        func.date_trunc('month', AdmissionApplication.submitted_at)
    ).order_by(
        func.date_trunc('month', AdmissionApplication.submitted_at)
    ).limit(6).all()
    
    # Program capacity analysis
    program_capacity = []
    programs = Program.query.all()
    
    for program in programs:
        applications = AdmissionApplication.query.filter_by(program_id=program.id).count()
        capacity = program.available_slots or 100
        fill_rate = (applications / capacity * 100) if capacity > 0 else 0
        
        program_capacity.append({
            "program_id": program.id,
            "program_name": program.name,
            "capacity": capacity,
            "applications": applications,
            "fill_rate": round(fill_rate, 2),
            "status": "full" if fill_rate >= 100 else "almost_full" if fill_rate >= 80 else "open"
        })
    
    return success_response({
        "monthly_trend": [
            {"month": month.strftime("%Y-%m"), "applications": count}
            for month, count in monthly_applications
        ],
        "program_capacity": sorted(program_capacity, key=lambda x: x["fill_rate"], reverse=True),
        "forecast": {
            "message": "Based on current trends, recommend opening more slots for high-demand programs",
            "high_demand_programs": [p["program_name"] for p in program_capacity if p["fill_rate"] > 80]
        }
    })


def export_to_csv(data, filename):
    """Export data to CSV format"""
    if not data:
        return bad_request("No data to export")
    
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=data[0].keys())
    writer.writeheader()
    writer.writerows(data)
    
    response = Response(output.getvalue(), mimetype="text/csv")
    response.headers["Content-Disposition"] = f"attachment; filename={filename}"
    return response
