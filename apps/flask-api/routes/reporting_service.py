"""
Reporting Service
Generates comprehensive reports for admissions and career offices.
Uses existing models only - no external dependencies.
"""
from datetime import datetime, timedelta
from typing import Dict, List, Any
from sqlalchemy import func, extract
from models import db, AdmissionApplication, OpportunityApplication, Opportunity
from models import User, Program, FinalistProfile, Notification


class ReportingService:
    """
    Generate institutional reports using database queries.
    No external APIs, exports to CSV/JSON using Python standard library.
    """
    
    @classmethod
    def get_admissions_dashboard(cls) -> Dict[str, Any]:
        """
        Comprehensive admissions statistics for admin dashboard.
        """
        # Overall statistics
        total_applications = AdmissionApplication.query.count()
        total_pending = AdmissionApplication.query.filter_by(status='pending').count()
        total_accepted = AdmissionApplication.query.filter_by(status='accepted').count()
        total_rejected = AdmissionApplication.query.filter_by(status='rejected').count()
        total_enrolled = AdmissionApplication.query.filter_by(status='enrolled').count()
        
        # By program
        program_stats = db.session.query(
            Program.name,
            func.count(AdmissionApplication.id).label('applications'),
            func.sum(func.case([(AdmissionApplication.status == 'accepted', 1)], else_=0)).label('accepted'),
            func.sum(func.case([(AdmissionApplication.status == 'enrolled', 1)], else_=0)).label('enrolled')
        ).join(AdmissionApplication).group_by(Program.id).all()
        
        # Monthly trend (last 6 months)
        six_months_ago = datetime.utcnow() - timedelta(days=180)
        monthly_trend = db.session.query(
            extract('month', AdmissionApplication.submitted_at).label('month'),
            extract('year', AdmissionApplication.submitted_at).label('year'),
            func.count(AdmissionApplication.id).label('count')
        ).filter(AdmissionApplication.submitted_at >= six_months_ago).group_by('year', 'month').all()
        
        # By entry qualification
        qualification_stats = db.session.query(
            AdmissionApplication.exam_level,
            func.count(AdmissionApplication.id).label('count')
        ).group_by(AdmissionApplication.exam_level).all()
        
        return {
            "summary": {
                "totalApplications": total_applications,
                "pending": total_pending,
                "accepted": total_accepted,
                "rejected": total_rejected,
                "enrolled": total_enrolled,
                "conversionRate": round((total_enrolled / total_applications * 100), 2) if total_applications > 0 else 0
            },
            "byProgram": [
                {"program": name, "applications": apps, "accepted": acc, "enrolled": enrolled}
                for name, apps, acc, enrolled in program_stats
            ],
            "monthlyTrend": [
                {"month": int(month), "year": int(year), "count": count}
                for month, year, count in monthly_trend
            ],
            "byQualification": [
                {"level": level, "count": count}
                for level, count in qualification_stats
            ]
        }
    
    @classmethod
    def get_career_services_dashboard(cls) -> Dict[str, Any]:
        """
        Career services statistics for admin dashboard.
        """
        # Opportunity statistics
        total_opportunities = Opportunity.query.count()
        active_opportunities = Opportunity.query.filter_by(is_active=True).count()
        
        # Application statistics
        total_opportunity_apps = OpportunityApplication.query.count()
        pending_apps = OpportunityApplication.query.filter_by(status='applied').count()
        shortlisted_apps = OpportunityApplication.query.filter_by(status='shortlisted').count()
        offered_apps = OpportunityApplication.query.filter_by(status='offered').count()
        accepted_offers = OpportunityApplication.query.filter_by(status='accepted').count()
        
        # By organization
        org_stats = db.session.query(
            Opportunity.organization,
            func.count(OpportunityApplication.id).label('applications')
        ).join(OpportunityApplication).group_by(Opportunity.organization).all()
        
        # Top opportunities by applications
        top_opportunities = db.session.query(
            Opportunity.title,
            Opportunity.organization,
            func.count(OpportunityApplication.id).label('applications')
        ).join(OpportunityApplication).group_by(Opportunity.id).order_by(func.count(OpportunityApplication.id).desc()).limit(10).all()
        
        # Finalist statistics
        total_finalists = FinalistProfile.query.count()
        finalists_with_cv = FinalistProfile.query.filter(FinalistProfile.cv_url.isnot(None)).count()
        finalists_with_skills = FinalistProfile.query.filter(FinalistProfile.skills != []).count()
        
        return {
            "summary": {
                "totalOpportunities": total_opportunities,
                "activeOpportunities": active_opportunities,
                "totalApplications": total_opportunity_apps,
                "pending": pending_apps,
                "shortlisted": shortlisted_apps,
                "offered": offered_apps,
                "accepted": accepted_offers,
                "placementRate": round((accepted_offers / total_opportunity_apps * 100), 2) if total_opportunity_apps > 0 else 0
            },
            "byOrganization": [
                {"organization": org, "applications": count}
                for org, count in org_stats
            ],
            "topOpportunities": [
                {"title": title, "organization": org, "applications": count}
                for title, org, count in top_opportunities
            ],
            "finalistStats": {
                "totalFinalists": total_finalists,
                "withCV": finalists_with_cv,
                "withSkills": finalists_with_skills,
                "profileCompletion": round(((finalists_with_cv + finalists_with_skills) / (total_finalists * 2) * 100), 2) if total_finalists > 0 else 0
            }
        }
    
    @classmethod
    def export_applications_csv(cls, start_date: datetime = None, end_date: datetime = None) -> str:
        """
        Generate CSV export of applications for reporting.
        Returns CSV content as string.
        """
        import csv
        import io
        
        query = AdmissionApplication.query
        if start_date:
            query = query.filter(AdmissionApplication.submitted_at >= start_date)
        if end_date:
            query = query.filter(AdmissionApplication.submitted_at <= end_date)
        
        applications = query.all()
        
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Header
        writer.writerow([
            'Application Number', 'Student Name', 'Email', 'Program', 'Status',
            'Exam Level', 'Exam Year', 'Submitted Date', 'Campus'
        ])
        
        # Data
        for app in applications:
            writer.writerow([
                app.application_number,
                f"{app.user.first_name} {app.user.last_name}" if app.user else '',
                app.user.email if app.user else '',
                app.program.name if app.program else '',
                app.status,
                app.exam_level,
                app.exam_year,
                app.submitted_at.strftime('%Y-%m-%d') if app.submitted_at else '',
                app.program.campus if app.program else ''
            ])
        
        return output.getvalue()
    
    @classmethod
    def generate_institutional_report(cls) -> Dict[str, Any]:
        """
        Comprehensive report for institutional planning and accreditation.
        """
        admissions = cls.get_admissions_dashboard()
        career = cls.get_career_services_dashboard()
        
        # Calculate key metrics
        total_users = User.query.count()
        total_programs = Program.query.count()
        
        # User role distribution
        role_dist = db.session.query(
            User.role,
            func.count(User.id).label('count')
        ).group_by(User.role).all()
        
        return {
            "generatedAt": datetime.utcnow().isoformat(),
            "systemOverview": {
                "totalUsers": total_users,
                "totalPrograms": total_programs,
                "userRoles": {role: count for role, count in role_dist}
            },
            "admissions": admissions,
            "careerServices": career,
            "recommendations": [
                "Focus marketing on programs with low application numbers",
                "Improve finalist profile completion rate",
                "Engage more employers for opportunities"
            ]
        }
