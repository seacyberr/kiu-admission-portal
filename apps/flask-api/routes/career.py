from flask import Blueprint, request, jsonify, current_app
from datetime import datetime
import os
import uuid
from werkzeug.utils import secure_filename
from models import db, CareerPath, FinalistProfile, Program
from routes.auth import get_current_user
from utils.api_response import success_response, paginated_response, bad_request, unauthorized, not_found, created

career_bp = Blueprint("career", __name__)


@career_bp.route("/paths", methods=["GET"])
def list_career_paths():
    program_name = request.args.get("program")
    faculty = request.args.get("faculty")
    page = int(request.args.get("page", 1))
    limit = int(request.args.get("limit", 20))

    query = CareerPath.query
    if program_name:
        # Cross-compatible JSON array search (works on both MySQL and PostgreSQL)
        # Uses LIKE with JSON substring pattern instead of PostgreSQL-specific @>
        query = query.filter(CareerPath.related_programs.like(f'%"{program_name}"%'))
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
def get_my_profile():
    user, error = get_current_user()
    if error:
        return unauthorized(error)

    profile = FinalistProfile.query.filter_by(user_id=user.id).first()
    if not profile:
        return not_found("Finalist profile not found")

    return success_response(profile.to_dict())


@career_bp.route("/my-profile", methods=["PUT"])
def upsert_my_profile():
    user, error = get_current_user()
    if error:
        return unauthorized(error)

    data = request.get_json()
    if not data:
        return bad_request("No JSON body provided")

    required = ["programId", "studentNumber", "yearOfStudy"]
    missing = [field for field in required if field not in data]
    if missing:
        return bad_request(f"Missing required fields: {', '.join(missing)}", errors={field: "Required" for field in missing})

    program = db.session.get(Program, data["programId"])
    if not program:
        return not_found("Program not found")

    profile = FinalistProfile.query.filter_by(user_id=user.id).first()
    if not profile:
        profile = FinalistProfile(user_id=user.id)
        db.session.add(profile)

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

    db.session.commit()
    return success_response(profile.to_dict(), message="Profile updated successfully")


@career_bp.route("/profile/upload-cv", methods=["POST"])
def upload_cv():
    user, error = get_current_user()
    if error:
        return unauthorized(error)

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
    profile = FinalistProfile.query.filter_by(user_id=user.id).first()
    if not profile:
        profile = FinalistProfile(user_id=user.id)
        db.session.add(profile)

    profile.cv_url = cv_url
    profile.updated_at = datetime.utcnow()
    db.session.commit()

    return success_response({
        "cvUrl": cv_url,
        "filename": file.filename
    }, message="CV uploaded successfully")


@career_bp.route("/match-jobs", methods=["GET"])
def match_jobs_to_profile():
    """
    Match student profile with available job opportunities
    Uses skills, program, and interests to find best matches
    """
    user, error = get_current_user()
    if error:
        return unauthorized(error)
    
    # Get student's profile
    profile = FinalistProfile.query.filter_by(user_id=user.id).first()
    if not profile:
        return not_found("Profile not found")
    
    # Get student's program for career paths
    program = db.session.get(Program, profile.program_id) if profile.program_id else None
    
    # Get query parameters for filtering
    location = request.args.get("location")
    job_type = request.args.get("job_type")  # full_time, part_time, internship
    min_salary = request.args.get("min_salary", type=int)
    
    # Build query for opportunities
    from models import Opportunity
    query = Opportunity.query.filter_by(status="active")
    
    if location:
        query = query.filter(Opportunity.location.ilike(f"%{location}%"))
    if job_type:
        query = query.filter_by(job_type=job_type)
    if min_salary:
        query = query.filter(Opportunity.salary_min >= min_salary)
    
    # Get all active opportunities
    opportunities = query.all()
    
    # Score each opportunity based on profile match
    scored_opportunities = []
    for opp in opportunities:
        score = 0
        reasons = []
        
        # Check if opportunity is related to student's program
        if program and program.name in (opp.required_programs or []):
            score += 30
            reasons.append(f"Matches your program ({program.name})")
        
        # Check skill overlap
        if profile.skills and opp.required_skills:
            profile_skills = set(s.lower() for s in profile.skills)
            opp_skills = set(s.lower() for s in opp.required_skills)
            overlap = profile_skills & opp_skills
            if overlap:
                skill_score = len(overlap) * 10
                score += min(skill_score, 40)  # Max 40 points for skills
                reasons.append(f"Matches {len(overlap)} of your skills")
        
        # GPA bonus if specified
        if opp.min_gpa and profile.gpa and profile.gpa >= opp.min_gpa:
            score += 10
            reasons.append("Your GPA meets requirements")
        
        # Recent posting bonus
        if opp.created_at:
            days_old = (datetime.utcnow() - opp.created_at).days
            if days_old <= 7:
                score += 5
                reasons.append("Posted recently")
        
        if score > 0:  # Only include if there's some match
            scored_opportunities.append({
                "opportunity": opp.to_dict(),
                "match_score": min(score, 100),
                "match_reasons": reasons,
                "is_recommended": score >= 50
            })
    
    # Sort by match score
    scored_opportunities.sort(key=lambda x: x["match_score"], reverse=True)
    
    return success_response({
        "total_matches": len(scored_opportunities),
        "recommended": [o for o in scored_opportunities if o["is_recommended"]],
        "other_matches": [o for o in scored_opportunities if not o["is_recommended"]],
        "profile_summary": {
            "program": program.name if program else None,
            "skills": profile.skills,
            "gpa": profile.gpa
        }
    })


@career_bp.route("/recommendations", methods=["GET"])
def get_career_recommendations():
    """
    Get personalized career path recommendations based on:
    - Academic performance
    - Skills
    - Program of study
    - Industry trends
    """
    user, error = get_current_user()
    if error:
        return unauthorized(error)
    
    profile = FinalistProfile.query.filter_by(user_id=user.id).first()
    if not profile:
        return not_found("Profile not found")
    
    program = db.session.get(Program, profile.program_id) if profile.program_id else None
    
    recommendations = []
    
    # Get career paths related to the student's program
    if program:
        career_paths = CareerPath.query.filter(
            CareerPath.related_programs.like(f'%"{program.name}"%')
        ).all()
        
        for path in career_paths:
            # Calculate fit score
            fit_score = 50  # Base score
            fit_reasons = [f"Common path for {program.name} graduates"]
            
            # GPA consideration
            if profile.gpa:
                if profile.gpa >= 4.5:
                    fit_score += 20
                    fit_reasons.append("Your excellent GPA opens leadership opportunities")
                elif profile.gpa >= 3.5:
                    fit_score += 10
                    fit_reasons.append("Your strong GPA meets most entry requirements")
            
            # Skills match
            if profile.skills and path.required_skills:
                matches = set(s.lower() for s in profile.skills) & set(s.lower() for s in path.required_skills)
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
                    "Network with professionals in the field"
                ]
            })
    
    # Sort by fit score
    recommendations.sort(key=lambda x: x["fit_score"], reverse=True)
    
    return success_response({
        "recommendations": recommendations[:5],  # Top 5
        "total_available": len(recommendations),
        "student_profile": {
            "program": program.name if program else None,
            "gpa": profile.gpa,
            "skills": profile.skills
        }
    })


@career_bp.route("/skills-gap", methods=["GET"])
def analyze_skills_gap():
    """
    Analyze skills gap between current profile and target career path
    """
    user, error = get_current_user()
    if error:
        return unauthorized(error)
    
    profile = FinalistProfile.query.filter_by(user_id=user.id).first()
    if not profile:
        return not_found("Profile not found")
    
    target_career = request.args.get("target_career")
    
    if not target_career:
        return bad_request("target_career parameter required", errors={"target_career": "Required"})
    
    # Find the career path
    career_path = CareerPath.query.filter(
        CareerPath.title.ilike(f"%{target_career}%")
    ).first()
    
    if not career_path:
        return not_found("Career path not found")
    
    # Compare skills
    current_skills = set(s.lower() for s in (profile.skills or []))
    required_skills = set(s.lower() for s in (career_path.required_skills or []))
    
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
    page = int(request.args.get("page", 1))
    limit = int(request.args.get("limit", 20))
    industry = request.args.get("industry")
    
    # This would typically query an Employer model
    # For now, return mock data representing typical KIU partners
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
    
    return success_response({
        "employers": employers,
        "total": len(employers),
        "partners_only": request.args.get("partners_only") == "true",
        "page": page
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
