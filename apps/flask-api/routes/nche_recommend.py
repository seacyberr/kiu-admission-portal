"""
NCHE Programme Recommendation API

Provides A-Level based programme recommendations using the official
NCHE Uganda weighted scoring system (Essential×3, Relevant×2, Desirable×1)
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Program, User
from services.nche_recommendation import recommend_programmes
from utils.api_response import success_response, bad_request, unauthorized

nche_recommend_bp = Blueprint("nche_recommend", __name__)


@nche_recommend_bp.route("/recommend", methods=["POST"])
def recommend_programs():
    """
    Recommend programs based on A-Level subject combination with NCHE compliance.
    
    Request body:
    {
        "alevelSubjects": [
            {"subject": "Mathematics", "grade": "A", "subjectType": "principal"},
            {"subject": "Physics", "grade": "B", "subjectType": "principal"},
            {"subject": "Chemistry", "grade": "C", "subjectType": "principal"},
            {"subject": "General Paper", "grade": "D", "subjectType": "subsidiary"}
        ],
        "olevelSummary": {
            "distinctions": 2,
            "credits": 4,
            "passes": 2
        },
        "subsidiaryMaths": true,
        "computerStudies": false
    }
    """
    data = request.get_json()
    if not data:
        return bad_request("No JSON body provided")
    
    alevel_subjects = data.get("alevelSubjects", [])
    if not alevel_subjects:
        return bad_request("alevelSubjects is required")
    
    principal_subjects = [s for s in alevel_subjects 
                          if s.get("subjectType", "").lower() == "principal"]
    if len(principal_subjects) < 2:
        return bad_request("At least 2 principal subjects required")
    
    olevel_summary = data.get("olevelSummary", {})
    gp_grade = None
    for s in alevel_subjects:
        if s.get("subject", "").lower() in ["general paper", "gp"]:
            gp_grade = s.get("grade")
            break
    
    programmes = Program.query.filter_by(level="degree").all()
    
    recommendations = recommend_programmes(
        alevel_subjects=alevel_subjects,
        olevel_summary=olevel_summary,
        programmes=programmes,
        gp_grade=gp_grade,
        sub_maths=data.get("subsidiaryMaths", False),
        computer_studies=data.get("computerStudies", False)
    )
    
    return success_response({
        "recommendations": [
            {
                "id": r["programme"].id,
                "name": r["programme"].name,
                "code": r["programme"].code,
                "faculty": r["programme"].faculty,
                "duration": r["programme"].duration,
                "feesPerYear": r["programme"].fees_per_year,
                "careerProspects": r["programme"].career_prospects,
                "eligible": r["eligible"],
                "alevelScore": r["alevel_score"],
                "subBonus": r["sub_bonus"],
                "oLevelScore": r["o_level_score"],
                "combinedScore": r["combined_score"],
                "breakdown": r["breakdown"],
                "eligibilityReason": r["eligibility_reason"],
            }
            for r in recommendations[:20]
        ],
        "total": len(recommendations),
        "eligibleCount": sum(1 for r in recommendations if r["eligible"]),
    })


@nche_recommend_bp.route("/programs", methods=["GET"])
def list_programs_with_requirements():
    """List all degree programs with their NCHE subject requirements."""
    campus = request.args.get("campus")
    faculty = request.args.get("faculty")
    
    query = Program.query.filter_by(level="degree")
    if campus:
        query = query.filter_by(campus=campus)
    if faculty:
        query = query.filter(Program.faculty.ilike(f"%{faculty}%"))
    
    programmes = query.order_by(Program.faculty, Program.name).all()
    
    return success_response({
        "programs": [
            {
                "id": p.id,
                "name": p.name,
                "code": p.code,
                "faculty": p.faculty,
                "duration": p.duration,
                "feesPerYear": p.fees_per_year,
                "essentialSubjects": p.get_essential_list(),
                "relevantSubjects": p.get_relevant_list(),
                "desirableSubjects": p.get_desirable_list(),
                "essentialType": p.essential_type,
                "minWeightedScore": p.min_weighted_score,
                "careerProspects": p.career_prospects,
            }
            for p in programmes
        ],
        "total": len(programmes),
    })


@nche_recommend_bp.route("/programs/<int:program_id>", methods=["GET"])
def get_program_requirements(program_id):
    """Get detailed NCHE requirements for a specific program."""
    prog = db.session.get(Program, program_id)
    if not prog:
        return bad_request("Program not found")
    
    return success_response({
        "id": prog.id,
        "name": prog.name,
        "code": prog.code,
        "faculty": prog.faculty,
        "department": prog.department,
        "duration": prog.duration,
        "description": prog.description,
        "entryRequirements": prog.entry_requirements,
        "feesPerYear": prog.fees_per_year,
        "careerProspects": prog.career_prospects,
        "ncheRequirements": {
            "essentialSubjects": prog.get_essential_list(),
            "relevantSubjects": prog.get_relevant_list(),
            "desirableSubjects": prog.get_desirable_list(),
            "essentialType": prog.essential_type,
            "minWeightedScore": prog.min_weighted_score,
        },
    })
