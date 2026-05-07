from flask import Blueprint, request, current_app
from datetime import datetime
import os
import uuid
from functools import wraps
from werkzeug.utils import secure_filename
from models import db, CareerPath, FinalistProfile, Program, Opportunity
from routes.auth import get_current_user
from utils.api_response import success_response, paginated_response, bad_request, unauthorized, not_found, created

career_bp = Blueprint("career", __name__)


def require_auth(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        user, error = get_current_user()
        if error:
            return unauthorized(error)
        return func(user, *args, **kwargs)

    return wrapper


def get_or_create_profile(user, create=False):
    profile = FinalistProfile.query.filter_by(user_id=user.id).first()
    if profile or not create:
        return profile

    profile = FinalistProfile(user_id=user.id)
    db.session.add(profile)
    return profile


def json_array_contains(column, value):
    return column.like(f'%"{value}"%')


def parse_int_query(name, default):
    return request.args.get(name, type=int) or default


@career_bp.route("/paths", methods=["GET"])
def list_career_paths():
    program_name = request.args.get("program")
    faculty = request.args.get("faculty")
    page = parse_int_query("page", 1)
    limit = parse_int_query("limit", 20)

    query = CareerPath.query
    if program_name:
        query = query.filter(json_array_contains(CareerPath.related_programs, program_name))
    if faculty:
        query = query.filter_by(industry_field=faculty)

    total = query.count()
    paths = query.offset((page - 1) * limit).limit(limit).all()
    return paginated_response(
        items=[p.to_dict() for p in paths],
        total=total,
        page=page,
        per_page=limit,
        data_key="careerPaths"
    )


@career_bp.route("/my-profile", methods=["GET"])
@require_auth
def get_my_profile(user):
    profile = FinalistProfile.query.filter_by(user_id=user.id).first()
    if not profile:
        return not_found("Finalist profile not found")

    return success_response(profile.to_dict())


@career_bp.route("/my-profile", methods=["PUT"])
@require_auth
def upsert_my_profile(user):
    data = request.get_json()
    if not data:
        return bad_request("No JSON body provided")

    required = ["programId", "studentNumber", "yearOfStudy"]
    missing = [field for field in required if field not in data]
    if missing:
        return bad_request(
            f"Missing required fields: {', '.join(missing)}",
            errors={field: "Required" for field in missing}
        )

    program = db.session.get(Program, data["programId"])
    if not program:
        return not_found("Program not found")

    profile = get_or_create_profile(user, create=True)
    profile.program_id = data["programId"]
    profile.student_number = data["studentNumber"]
    profile.year_of_study = data["yearOfStudy"]
    profile.graduation_year = data.get("graduationYear")
    profile.gpa = data.get("gpa")
    profile.skills = data.get("skills", [])
    profile.bio = data.get("bio")
    profile.linkedin_url = data.get("linkedinUrl")
    profile.cv_url = data.get("cvUrl")
    profile.is_finalist = True
    profile.updated_at = datetime.utcnow()

    try:
        db.session.commit()
        return success_response(profile.to_dict(), message="Profile updated successfully")
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Failed to update profile: {e}")
        return bad_request("Failed to update profile")


@career_bp.route("/profile/upload-cv", methods=["POST"])
@require_auth
def upload_cv(user):
    if 'cv' not in request.files:
        return bad_request("No file part")

    file = request.files['cv']
    if file.filename == '':
        return bad_request("No selected file")

    # Validate file type
    allowed_extensions = {'pdf', 'doc', 'docx'}
    ext = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else ''
    if ext not in allowed_extensions:
        return bad_request("Invalid file type. Allowed: PDF, DOC, DOCX", errors={"file": "Invalid type"})

    # Validate file size (5MB max)
    file.seek(0, os.SEEK_END)
    if file.tell() > 5 * 1024 * 1024:
        return bad_request("File too large. Maximum 5MB", errors={"file": "Too large"})
    file.seek(0)

    # Create upload directory if it doesn't exist
    upload_dir = os.path.join(current_app.root_path, 'uploads', 'cvs')
    os.makedirs(upload_dir, exist_ok=True)

    # Generate unique filename
    filename = f"{uuid.uuid4()}_{secure_filename(file.filename)}"
    file_path = os.path.join(upload_dir, filename)

    # Save file
    file.save(file_path)

    # Generate public URL
    cv_url = f"/uploads/cvs/{filename}"

    # Update user profile
    profile = get_or_create_profile(user, create=True)
    profile.cv_url = cv_url
    profile.updated_at = datetime.utcnow()
    
    try:
        db.session.commit()
        return success_response({
            "cvUrl": cv_url,
            "filename": file.filename
        }, message="CV uploaded successfully")
    except Exception as e:
        db.session.rollback()
        # Remove uploaded file on error
        if os.path.exists(file_path):
            os.remove(file_path)
        current_app.logger.error(f"Failed to update profile with CV: {e}")
        return bad_request("Failed to upload CV")


@career_bp.route("/match-jobs", methods=["GET"])
@require_auth
def match_jobs_to_profile(user):
    """
    Match student profile with available job opportunities
    Uses skills, program, and interests to find best matches
    """
    profile = FinalistProfile.query.filter_by(user_id=user.id).first()
    if not profile:
        return not_found("Profile not found")

    program = db.session.get(Program, profile.program_id) if profile.program_id else None
    location = request.args.get("location")
    job_type = request.args.get("job_type")
    min_salary = request.args.get("min_salary", type=int)

    query = Opportunity.query.filter_by(status="active")
    if location:
        query = query.filter(Opportunity.location.ilike(f"%{location}%"))
    if job_type:
        query = query.filter_by(job_type=job_type)
    if min_salary:
        query = query.filter(Opportunity.salary_min >= min_salary)

    profile_skills = {s.lower() for s in (profile.skills or [])}
    program_name = program.name.lower() if program else None

    scored_opportunities = []
    for opp in query:
        score = 0
        reasons = []

        if program_name and opp.required_programs and program_name in {p.lower() for p in opp.required_programs}:
            score += 30
            reasons.append(f"Matches your program ({program.name})")

        if opp.required_skills:
            opp_skills = {s.lower() for s in opp.required_skills}
            overlap = profile_skills & opp_skills
            if overlap:
                score += min(len(overlap) * 10, 40)
                reasons.append(f"Matches {len(overlap)} of your skills")

        if opp.min_gpa and profile.gpa and profile.gpa >= opp.min_gpa:
            score += 10
            reasons.append("Your GPA meets requirements")

        if opp.created_at and (datetime.utcnow() - opp.created_at).days <= 7:
            score += 5
            reasons.append("Posted recently")

        if score:
            scored_opportunities.append({
                "opportunity": opp.to_dict(),
                "match_score": min(score, 100),
                "match_reasons": reasons,
                "is_recommended": score >= 50,
            })

    scored_opportunities.sort(key=lambda item: item["match_score"], reverse=True)
    recommended = [o for o in scored_opportunities if o["is_recommended"]]

    return success_response({
        "total_matches": len(scored_opportunities),
        "recommended": recommended,
        "other_matches": [o for o in scored_opportunities if not o["is_recommended"]],
        "profile_summary": {
            "program": program.name if program else None,
            "skills": profile.skills,
            "gpa": profile.gpa,
        },
    })


@career_bp.route("/recommendations", methods=["GET"])
@require_auth
def get_career_recommendations(user):
    """
    Get personalized career path recommendations based on:
    - Academic performance
    - Skills
    - Program of study
    - Industry trends
    """
    profile = FinalistProfile.query.filter_by(user_id=user.id).first()
    if not profile:
        return not_found("Profile not found")

    program = db.session.get(Program, profile.program_id) if profile.program_id else None
    recommendations = []

    if program:
        career_paths = CareerPath.query.filter(
            json_array_contains(CareerPath.related_programs, program.name)
        ).all()
        profile_skills = {s.lower() for s in (profile.skills or [])}

        for path in career_paths:
            fit_score = 50
            fit_reasons = [f"Common path for {program.name} graduates"]

            if profile.gpa:
                if profile.gpa >= 4.5:
                    fit_score += 20
                    fit_reasons.append("Your excellent GPA opens leadership opportunities")
                elif profile.gpa >= 3.5:
                    fit_score += 10
                    fit_reasons.append("Your strong GPA meets most entry requirements")

            if path.required_skills:
                path_skills = {s.lower() for s in path.required_skills}
                matches = profile_skills & path_skills
                if matches:
                    fit_score += min(len(matches) * 5, 15)
                    fit_reasons.append(f"You have {len(matches)} relevant skills")

            recommendations.append({
                "career_path": path.to_dict(),
                "fit_score": min(fit_score, 100),
                "fit_reasons": fit_reasons,
                "estimated_entry_salary": path.entry_salary_range,
                "growth_potential": path.growth_potential,
                "recommended_next_steps": [
                    f"Gain experience in {path.industry_field}",
                    "Build portfolio of relevant projects",
                    "Network with professionals in the field",
                ],
            })

    recommendations.sort(key=lambda x: x["fit_score"], reverse=True)
    return success_response({
        "recommendations": recommendations[:5],
        "total_available": len(recommendations),
        "student_profile": {
            "program": program.name if program else None,
            "gpa": profile.gpa,
            "skills": profile.skills,
        },
    })


@career_bp.route("/skills-gap", methods=["GET"])
@require_auth
def analyze_skills_gap(user):
    """
    Analyze skills gap between current profile and target career path
    """
    profile = FinalistProfile.query.filter_by(user_id=user.id).first()
    if not profile:
        return not_found("Profile not found")
    
    target_career = request.args.get("target_career")
    if not target_career:
        return bad_request("target_career parameter required", errors={"target_career": "Required"})

    career_path = CareerPath.query.filter(
        CareerPath.title.ilike(f"%{target_career}%")
    ).first()
    
    if not career_path:
        return not_found("Career path not found")
    
    # Compare skills
    current_skills = {s.lower() for s in (profile.skills or [])}
    required_skills = {s.lower() for s in (career_path.required_skills or [])}

    matched_skills = current_skills & required_skills
    missing_skills = required_skills - current_skills
    extra_skills = current_skills - required_skills
    
    # Calculate readiness score
    if required_skills:
        readiness = len(matched_skills) / len(required_skills) * 100
    else:
        readiness = 100
    
    return success_response({
        "target_career": career_path.title,
        "readiness_score": round(readiness, 1),
        "skills_analysis": {
            "matched": list(matched_skills),
            "missing": list(missing_skills),
            "extra": list(extra_skills)
        },
        "recommendations": [
            f"Learn: {skill}" for skill in list(missing_skills)[:5]
        ] if missing_skills else ["You have all the key skills! Consider gaining practical experience."],
        "learning_resources": {
            "online_courses": career_path.suggested_courses or [],
            "certifications": career_path.suggested_certifications or [],
            "internship_opportunities": True
        }
    })


@career_bp.route("/employers", methods=["GET"])
def list_employer_partners():
    """List employers who partner with KIU for recruitment"""
    page = parse_int_query("page", 1)
    limit = parse_int_query("limit", 20)
    industry = request.args.get("industry")
    partners_only = request.args.get("partners_only") == "true"

    employers = [
        {
            "name": "Mulago National Referral Hospital",
            "industry": "Healthcare",
            "type": "Government",
            "hiring_programs": ["MBChB", "BNS", "BCMCH"],
            "active_listings": 15,
            "is_partner": True
        },
        {
            "name": "Stanbic Bank Uganda",
            "industry": "Banking & Finance",
            "type": "Private",
            "hiring_programs": ["BBA", "BCom", "Economics"],
            "active_listings": 8,
            "is_partner": True
        },
        {
            "name": "Uganda Bureau of Statistics",
            "industry": "Government & Research",
            "type": "Government",
            "hiring_programs": ["Statistics", "BSc-STAT", "Economics"],
            "active_listings": 5,
            "is_partner": True
        },
        {
            "name": "Mukwano Industries",
            "industry": "Manufacturing",
            "type": "Private",
            "hiring_programs": ["BSc-IC", "Engineering", "BBA"],
            "active_listings": 12,
            "is_partner": False
        }
    ]
    
    if industry:
        employers = [e for e in employers if industry.lower() in e["industry"].lower()]
    if partners_only:
        employers = [e for e in employers if e["is_partner"]]

    start = (page - 1) * limit
    paged_employers = employers[start:start + limit]
    return success_response({
        "employers": paged_employers,
        "total": len(employers),
        "partners_only": partners_only,
        "page": page,
    })


@career_bp.route("/events", methods=["GET"])
def list_career_events():
    """List upcoming career events (job fairs, workshops, etc.)"""
    event_type = request.args.get("type")  # job_fair, workshop, networking
    
    # Mock career events
    events = [
        {
            "id": 1,
            "title": "KIU Annual Career Fair 2025",
            "type": "job_fair",
            "date": "2025-08-15",
            "time": "09:00 - 17:00",
            "location": "KIU Main Campus - Sports Grounds",
            "description": "Connect with 50+ employers. Bring your CV!",
            "target_audience": ["final_year", "recent_graduates"],
            "registration_required": True,
            "registered_count": 450
        },
        {
            "id": 2,
            "title": "Resume Writing Workshop",
            "type": "workshop",
            "date": "2025-07-10",
            "time": "14:00 - 16:00",
            "location": "Online (Zoom)",
            "description": "Learn to craft a professional resume",
            "target_audience": ["all_students"],
            "registration_required": True,
            "registered_count": 120
        },
        {
            "id": 3,
            "title": "Healthcare Professionals Networking Night",
            "type": "networking",
            "date": "2025-07-25",
            "time": "18:00 - 21:00",
            "location": "Kampala Serena Hotel",
            "description": "Network with healthcare industry leaders",
            "target_audience": ["MBChB", "BNS", "BCMCH", "BPharm"],
            "registration_required": True,
            "registered_count": 85
        }
    ]
    
    if event_type:
        events = [e for e in events if e["type"] == event_type]
    
    return success_response({
        "events": events,
        "total": len(events),
        "registration_open": True
    })
