from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from datetime import datetime, date
from models import db, Opportunity, OpportunityApplication
from routes.auth import get_current_user
from sqlalchemy import func
from utils.api_response import success_response, paginated_response, bad_request, unauthorized, forbidden, not_found, conflict, created, no_content

opportunities_bp = Blueprint("opportunities", __name__)


@opportunities_bp.route("", methods=["GET"])
def list_opportunities():
    opp_type = request.args.get("type")
    field = request.args.get("field")
    page = int(request.args.get("page", 1))
    limit = int(request.args.get("limit", 20))

    query = Opportunity.query.filter_by(is_active=True)
    if opp_type:
        query = query.filter_by(type=opp_type)
    if field:
        # Cross-compatible JSON array search (works on both MySQL and PostgreSQL)
        query = query.filter(Opportunity.required_programs.like(f'%"{field}"%'))

    total = query.count()
    opps = query.order_by(Opportunity.posted_at.desc()).offset((page - 1) * limit).limit(limit).all()
    opp_ids = [o.id for o in opps]
    counts_by_id = {}
    if opp_ids:
        count_rows = (
            db.session.query(
                OpportunityApplication.opportunity_id,
                func.count(OpportunityApplication.id),
            )
            .filter(OpportunityApplication.opportunity_id.in_(opp_ids))
            .group_by(OpportunityApplication.opportunity_id)
            .all()
        )
        counts_by_id = {opp_id: count for opp_id, count in count_rows}

    return paginated_response(
        items=[o.to_dict(applicant_count=counts_by_id.get(o.id, 0)) for o in opps],
        total=total,
        page=page,
        per_page=limit,
        data_key="opportunities"
    )


@opportunities_bp.route("", methods=["POST"])
@jwt_required()
def create_opportunity():
    user, error = get_current_user()
    if error:
        return unauthorized(error)
    if user.role != "admin":
        return forbidden("Admin access required")

    data = request.get_json()
    if not data:
        return bad_request("No JSON body provided")
    
    required = ["title", "organization", "type", "description", "requirements", "applicationDeadline"]
    missing = [field for field in required if field not in data]
    if missing:
        return bad_request(f"Missing required fields: {', '.join(missing)}", errors={field: "Required" for field in missing})

    try:
        deadline = date.fromisoformat(data["applicationDeadline"])
    except ValueError:
        return bad_request("Invalid applicationDeadline format", errors={"applicationDeadline": "Must be ISO date format (YYYY-MM-DD)"})

    opp = Opportunity(
        title=data["title"],
        organization=data["organization"],
        type=data["type"],
        description=data["description"],
        requirements=data["requirements"],
        required_programs=data.get("requiredPrograms", []),
        required_skills=data.get("requiredSkills", []),
        location=data.get("location"),
        salary_range=data.get("salaryRange"),
        application_deadline=deadline,
        contact_email=data.get("contactEmail"),
        is_active=data.get("isActive", True),
    )
    db.session.add(opp)
    db.session.commit()
    return success_response(opp.to_dict(), message="Opportunity created successfully", status_code=201)


@opportunities_bp.route("/<int:opp_id>", methods=["GET"])
def get_opportunity(opp_id):
    opp = Opportunity.query.get(opp_id)
    if not opp:
        return not_found("Opportunity not found")
    return success_response(opp.to_dict())


@opportunities_bp.route("/<int:opp_id>", methods=["PATCH"])
def update_opportunity(opp_id):
    user, error = get_current_user()
    if error:
        return unauthorized(error)
    if user.role != "admin":
        return forbidden("Admin access required")

    opp = Opportunity.query.get(opp_id)
    if not opp:
        return not_found("Opportunity not found")

    data = request.get_json()
    if not data:
        return bad_request("No JSON body provided")
    
    for field, attr in [
        ("title", "title"), ("organization", "organization"), ("type", "type"),
        ("description", "description"), ("requirements", "requirements"),
        ("location", "location"), ("salaryRange", "salary_range"),
        ("contactEmail", "contact_email"), ("isActive", "is_active"),
        ("requiredPrograms", "required_programs"), ("requiredSkills", "required_skills"),
    ]:
        if field in data:
            setattr(opp, attr, data[field])

    if "applicationDeadline" in data:
        try:
            opp.application_deadline = date.fromisoformat(data["applicationDeadline"])
        except ValueError:
            return bad_request("Invalid applicationDeadline format", errors={"applicationDeadline": "Must be ISO date format"})

    opp.updated_at = datetime.utcnow()
    db.session.commit()
    return success_response(opp.to_dict(), message="Opportunity updated successfully")


@opportunities_bp.route("/<int:opp_id>", methods=["DELETE"])
def delete_opportunity(opp_id):
    user, error = get_current_user()
    if error:
        return unauthorized(error)
    if user.role != "admin":
        return forbidden("Admin access required")

    opp = Opportunity.query.get(opp_id)
    if not opp:
        return not_found("Opportunity not found")

    db.session.delete(opp)
    db.session.commit()
    return no_content()


@opportunities_bp.route("/<int:opp_id>/apply", methods=["POST"])
def apply_for_opportunity(opp_id):
    user, error = get_current_user()
    if error:
        return unauthorized(error)

    opp = Opportunity.query.get(opp_id)
    if not opp or not opp.is_active:
        return not_found("Opportunity not found or no longer active")

    existing = OpportunityApplication.query.filter_by(opportunity_id=opp_id, user_id=user.id).first()
    if existing:
        return conflict("You have already applied for this opportunity")

    data = request.get_json()
    if not data or not data.get("coverLetter"):
        return bad_request("coverLetter is required", errors={"coverLetter": "Required"})

    application = OpportunityApplication(
        opportunity_id=opp_id,
        user_id=user.id,
        cover_letter=data["coverLetter"],
        cv_url=data.get("cvUrl"),
        additional_info=data.get("additionalInfo"),
    )
    db.session.add(application)
    db.session.commit()
    return created(application.to_dict(), message="Application submitted successfully")


@opportunities_bp.route("/applications/my", methods=["GET"])
def my_applications():
    user, error = get_current_user()
    if error:
        return unauthorized(error)

    apps = OpportunityApplication.query.filter_by(user_id=user.id).order_by(
        OpportunityApplication.applied_at.desc()
    ).all()

    return success_response({"applications": [a.to_dict() for a in apps], "total": len(apps)})


@opportunities_bp.route("/applications/<int:app_id>", methods=["PATCH"])
def update_application_status(app_id):
    user, error = get_current_user()
    if error:
        return unauthorized(error)
    if user.role != "admin":
        return forbidden("Admin access required")

    application = OpportunityApplication.query.get(app_id)
    if not application:
        return not_found("Application not found")

    data = request.get_json()
    if not data:
        return bad_request("No JSON body provided")
    
    valid_statuses = ["applied", "shortlisted", "interview_scheduled", "accepted", "rejected"]
    new_status = data.get("status")
    if new_status not in valid_statuses:
        return bad_request(f"Status must be one of {valid_statuses}", errors={"status": f"Must be one of: {', '.join(valid_statuses)}"})

    application.status = new_status
    if "adminNotes" in data:
        application.admin_notes = data["adminNotes"]
    application.updated_at = datetime.utcnow()
    db.session.commit()
    return success_response(application.to_dict(), message="Application status updated")


@opportunities_bp.route("/advanced-search", methods=["GET"])
def advanced_job_search():
    """Advanced job search with multiple filters"""
    keywords = request.args.get("keywords")
    location = request.args.get("location")
    opp_type = request.args.get("type")
    field = request.args.get("field")
    min_salary = request.args.get("min_salary", type=int)
    date_posted = request.args.get("date_posted")
    sort_by = request.args.get("sort_by", "relevance")
    page = request.args.get("page", 1, type=int)
    limit = request.args.get("limit", 20, type=int)
    
    query = Opportunity.query.filter_by(is_active=True)
    
    if keywords:
        search = f"%{keywords}%"
        query = query.filter(
            db.or_(
                Opportunity.title.ilike(search),
                Opportunity.description.ilike(search),
                Opportunity.organization.ilike(search)
            )
        )
    
    if location:
        query = query.filter(Opportunity.location.ilike(f"%{location}%"))
    
    if opp_type:
        query = query.filter_by(type=opp_type)
    
    if field:
        query = query.filter(Opportunity.required_programs.like(f'%"{field}"%'))
    
    if min_salary:
        query = query.filter(Opportunity.salary_range >= min_salary)
    
    if date_posted == "24h":
        from datetime import timedelta
        cutoff = datetime.utcnow() - timedelta(days=1)
        query = query.filter(Opportunity.posted_at >= cutoff)
    elif date_posted == "7d":
        from datetime import timedelta
        cutoff = datetime.utcnow() - timedelta(days=7)
        query = query.filter(Opportunity.posted_at >= cutoff)
    
    # Sorting
    if sort_by == "date":
        query = query.order_by(Opportunity.posted_at.desc())
    elif sort_by == "salary":
        query = query.order_by(Opportunity.salary_range.desc())
    else:
        query = query.order_by(Opportunity.posted_at.desc())
    
    total = query.count()
    opps = query.offset((page - 1) * limit).limit(limit).all()
    
    return paginated_response(
        items=[o.to_dict() for o in opps],
        total=total,
        page=page,
        per_page=limit,
        data_key="opportunities"
    )


@opportunities_bp.route("/trending", methods=["GET"])
def get_trending_jobs():
    """Get trending/popular job opportunities"""
    from datetime import timedelta
    
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    
    # Get jobs with most applications in last 30 days
    trending = db.session.query(
        Opportunity,
        db.func.count(OpportunityApplication.id).label('app_count')
    ).join(
        OpportunityApplication, Opportunity.id == OpportunityApplication.opportunity_id
    ).filter(
        Opportunity.is_active == True,
        Opportunity.posted_at >= thirty_days_ago
    ).group_by(
        Opportunity.id
    ).order_by(
        db.desc('app_count')
    ).limit(10).all()
    
    return success_response({
        "trending": [
            {
                "opportunity": opp.to_dict(),
                "applications_count": count
            }
            for opp, count in trending
        ],
        "period": "last_30_days"
    })


@opportunities_bp.route("/salary-insights", methods=["GET"])
def get_salary_insights():
    """Get salary insights for different job types"""
    opp_type = request.args.get("type")
    field = request.args.get("field")
    
    query = Opportunity.query.filter(Opportunity.salary_range.isnot(None))
    
    if opp_type:
        query = query.filter_by(type=opp_type)
    
    if field:
        query = query.filter(Opportunity.required_programs.like(f'%"{field}"%'))
    
    opportunities = query.all()
    
    if not opportunities:
        return not_found("No salary data available")
    
    salaries = [opp.salary_range for opp in opportunities if opp.salary_range]
    
    if salaries:
        import statistics
        avg_salary = statistics.mean(salaries)
        median_salary = statistics.median(salaries)
        
        return success_response({
            "type": opp_type or "all",
            "field": field or "all",
            "count": len(salaries),
            "average": int(avg_salary),
            "median": int(median_salary),
            "min": min(salaries),
            "max": max(salaries)
        })
    
    return not_found("Insufficient data")


@opportunities_bp.route("/statistics", methods=["GET"])
def get_opportunity_statistics():
    """Admin: Get job market statistics"""
    user, error = get_current_user()
    if error or user.role != "admin":
        return forbidden("Admin access required")
    
    # Total statistics
    total_active = Opportunity.query.filter_by(is_active=True).count()
    total_applications = OpportunityApplication.query.count()
    
    # By type
    type_counts = db.session.query(
        Opportunity.type,
        db.func.count(Opportunity.id)
    ).filter_by(is_active=True).group_by(Opportunity.type).all()
    
    # By field/program
    # This requires parsing JSON array, simplified here
    all_programs = db.session.query(Opportunity.required_programs).filter_by(is_active=True).all()
    field_counts = {}
    for programs, in all_programs:
        if programs:
            for prog in programs:
                field_counts[prog] = field_counts.get(prog, 0) + 1
    
    # Application status breakdown
    status_counts = db.session.query(
        OpportunityApplication.status,
        db.func.count(OpportunityApplication.id)
    ).group_by(OpportunityApplication.status).all()
    
    return success_response({
        "total_active_opportunities": total_active,
        "total_applications": total_applications,
        "by_type": {t: c for t, c in type_counts},
        "top_fields": dict(sorted(field_counts.items(), key=lambda x: x[1], reverse=True)[:10]),
        "application_status": {s: c for s, c in status_counts},
        "generated_at": datetime.utcnow().isoformat()
    })
