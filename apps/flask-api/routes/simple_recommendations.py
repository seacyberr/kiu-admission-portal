"""
apps/flask-api/routes/simple_recommendations.py

Simple programme recommendation engine for KIU Uganda.

Direct application flow:
- Browse programmes by interest/qualification
- Get personalized recommendations
- Apply directly to any programme
"""

from flask import Blueprint, request, jsonify
import logging

simple_recommendations_bp = Blueprint("simple_recommendations", __name__)
log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Simple programme catalogue
# ---------------------------------------------------------------------------
KIU_PROGRAMMES = [
    {
        "id": "mbchb",
        "code": "MBChB",
        "name": "Bachelor of Medicine and Bachelor of Surgery",
        "faculty": "College of Health Sciences",
        "duration_years": 5,
        "intake_months": [8, 1],
        "campus": ["Main Campus (Kansanga)", "Western Campus (Ishaka)"],
        "tuition_ugx_per_semester": 6500000,
        "tuition_usd_per_semester": 1800,
        "category": "Health Sciences",
        "requirements": {
            "subjects": ["Biology", "Chemistry", "Physics/Mathematics"],
            "minimum_education": "A-Level with 2 principal passes",
            "alternative": "Diploma in relevant health field"
        },
        "career_prospects": ["Medical Officer", "Surgeon", "Specialist Physician"],
        "accreditation": "NCHE, Uganda Medical and Dental Practitioners Council",
    },
    {
        "id": "bnsc",
        "code": "BNSc",
        "name": "Bachelor of Nursing Science",
        "faculty": "College of Health Sciences",
        "duration_years": 4,
        "intake_months": [8, 1, 3],
        "campus": ["Main Campus (Kansanga)", "Western Campus (Ishaka)"],
        "tuition_ugx_per_semester": 3800000,
        "tuition_usd_per_semester": 1100,
        "category": "Health Sciences",
        "requirements": {
            "subjects": ["Biology", "Chemistry"],
            "minimum_education": "A-Level with 1 principal pass",
            "alternative": "Diploma in Nursing/Midwifery"
        },
        "career_prospects": ["Nurse", "Midwife", "Nursing Manager", "Public Health Nurse"],
        "accreditation": "NCHE, Uganda Nurses and Midwives Council",
    },
    {
        "id": "bpharm",
        "code": "BPharm",
        "name": "Bachelor of Pharmacy",
        "faculty": "College of Health Sciences",
        "duration_years": 4,
        "intake_months": [8, 1],
        "campus": ["Main Campus (Kansanga)"],
        "tuition_ugx_per_semester": 4200000,
        "tuition_usd_per_semester": 1200,
        "category": "Health Sciences",
        "requirements": {
            "subjects": ["Biology", "Chemistry", "Physics/Mathematics"],
            "minimum_education": "A-Level with 2 principal passes",
            "alternative": "Diploma in Pharmacy"
        },
        "career_prospects": ["Pharmacist", "Drug Inspector", "Clinical Pharmacist"],
        "accreditation": "NCHE, Pharmaceutical Society of Uganda",
    },
    {
        "id": "llb",
        "code": "LLB",
        "name": "Bachelor of Laws",
        "faculty": "Faculty of Law",
        "duration_years": 4,
        "intake_months": [8, 1, 3],
        "campus": ["Main Campus (Kansanga)", "Western Campus (Ishaka)"],
        "tuition_ugx_per_semester": 2800000,
        "tuition_usd_per_semester": 900,
        "category": "Law",
        "requirements": {
            "subjects": ["Any combination", "Good English skills"],
            "minimum_education": "A-Level with 2 principal passes",
            "alternative": "Diploma in Law"
        },
        "career_prospects": ["Lawyer", "Judge", "Legal Advisor", "Prosecutor"],
        "accreditation": "NCHE, Law Development Centre",
    },
    {
        "id": "bsc_ce",
        "code": "BSc CE",
        "name": "Bachelor of Science in Civil Engineering",
        "faculty": "Faculty of Engineering and Applied Sciences",
        "duration_years": 4,
        "intake_months": [8, 1],
        "campus": ["Main Campus (Kansanga)"],
        "tuition_ugx_per_semester": 3500000,
        "tuition_usd_per_semester": 1050,
        "category": "Engineering",
        "requirements": {
            "subjects": ["Mathematics", "Physics", "Chemistry"],
            "minimum_education": "A-Level with 2 principal passes",
            "alternative": "Diploma in Civil Engineering"
        },
        "career_prospects": ["Civil Engineer", "Structural Engineer", "Project Manager"],
        "accreditation": "NCHE, Engineers Registration Board",
    },
    {
        "id": "bsc_ee",
        "code": "BSc EE",
        "name": "Bachelor of Science in Electrical Engineering",
        "faculty": "Faculty of Engineering and Applied Sciences",
        "duration_years": 4,
        "intake_months": [8, 1],
        "campus": ["Main Campus (Kansanga)"],
        "tuition_ugx_per_semester": 3500000,
        "tuition_usd_per_semester": 1050,
        "category": "Engineering",
        "requirements": {
            "subjects": ["Mathematics", "Physics", "Chemistry"],
            "minimum_education": "A-Level with 2 principal passes",
            "alternative": "Diploma in Electrical Engineering"
        },
        "career_prospects": ["Electrical Engineer", "Power Systems Engineer", "Telecom Engineer"],
        "accreditation": "NCHE, Engineers Registration Board",
    },
    {
        "id": "bsc_cs",
        "code": "BSc CS",
        "name": "Bachelor of Science in Computer Science",
        "faculty": "Faculty of Information and Communication Technology",
        "duration_years": 3,
        "intake_months": [8, 1, 3],
        "campus": ["Main Campus (Kansanga)", "Western Campus (Ishaka)"],
        "tuition_ugx_per_semester": 2600000,
        "tuition_usd_per_semester": 800,
        "category": "Information Technology",
        "requirements": {
            "subjects": ["Mathematics", "Physics", "Computer Studies"],
            "minimum_education": "A-Level with 2 principal passes",
            "alternative": "Diploma in Computer Science/IT"
        },
        "career_prospects": ["Software Developer", "Systems Analyst", "Network Engineer"],
        "accreditation": "NCHE",
    },
    {
        "id": "bsc_it",
        "code": "BSc IT",
        "name": "Bachelor of Science in Information Technology",
        "faculty": "Faculty of Information and Communication Technology",
        "duration_years": 3,
        "intake_months": [8, 1, 3],
        "campus": ["Main Campus (Kansanga)", "Western Campus (Ishaka)"],
        "tuition_ugx_per_semester": 2400000,
        "tuition_usd_per_semester": 750,
        "category": "Information Technology",
        "requirements": {
            "subjects": ["Mathematics", "Computer Studies"],
            "minimum_education": "A-Level with 1 principal pass",
            "alternative": "Diploma in IT/Computer Science"
        },
        "career_prospects": ["IT Manager", "Network Administrator", "Database Administrator"],
        "accreditation": "NCHE",
    },
    {
        "id": "bba",
        "code": "BBA",
        "name": "Bachelor of Business Administration",
        "faculty": "Faculty of Business and Management",
        "duration_years": 3,
        "intake_months": [8, 1, 3],
        "campus": ["Main Campus (Kansanga)", "Western Campus (Ishaka)"],
        "tuition_ugx_per_semester": 2200000,
        "tuition_usd_per_semester": 700,
        "category": "Business",
        "requirements": {
            "subjects": ["Any combination", "Good Mathematics"],
            "minimum_education": "A-Level with 2 principal passes",
            "alternative": "Diploma in Business/Administration"
        },
        "career_prospects": ["Business Manager", "Marketing Manager", "HR Manager"],
        "accreditation": "NCHE",
    },
    {
        "id": "bcom",
        "code": "BCom",
        "name": "Bachelor of Commerce",
        "faculty": "Faculty of Business and Management",
        "duration_years": 3,
        "intake_months": [8, 1, 3],
        "campus": ["Main Campus (Kansanga)", "Western Campus (Ishaka)"],
        "tuition_ugx_per_semester": 2200000,
        "tuition_usd_per_semester": 700,
        "category": "Business",
        "requirements": {
            "subjects": ["Mathematics", "Economics", "Accounting"],
            "minimum_education": "A-Level with 2 principal passes",
            "alternative": "Diploma in Commerce/Accounting"
        },
        "career_prospects": ["Accountant", "Financial Analyst", "Auditor"],
        "accreditation": "NCHE",
    },
    {
        "id": "bed_arts",
        "code": "BEd Arts",
        "name": "Bachelor of Education (Arts)",
        "faculty": "Faculty of Education",
        "duration_years": 3,
        "intake_months": [8, 1, 3],
        "campus": ["Main Campus (Kansanga)", "Western Campus (Ishaka)"],
        "tuition_ugx_per_semester": 2000000,
        "tuition_usd_per_semester": 650,
        "category": "Education",
        "requirements": {
            "subjects": ["Any teaching subjects", "Good English"],
            "minimum_education": "A-Level with 2 principal passes",
            "alternative": "Diploma in Education"
        },
        "career_prospects": ["Teacher", "Education Administrator", "Curriculum Developer"],
        "accreditation": "NCHE, Ministry of Education",
    },
    {
        "id": "bed_science",
        "code": "BEd Science",
        "name": "Bachelor of Education (Science)",
        "faculty": "Faculty of Education",
        "duration_years": 3,
        "intake_months": [8, 1, 3],
        "campus": ["Main Campus (Kansanga)", "Western Campus (Ishaka)"],
        "tuition_ugx_per_semester": 2000000,
        "tuition_usd_per_semester": 650,
        "category": "Education",
        "requirements": {
            "subjects": ["Mathematics", "Physics", "Chemistry", "Biology"],
            "minimum_education": "A-Level with 2 principal passes",
            "alternative": "Diploma in Science Education"
        },
        "career_prospects": ["Science Teacher", "Lab Technician", "Education Officer"],
        "accreditation": "NCHE, Ministry of Education",
    },
    {
        "id": "bsocsc",
        "code": "BSocSc",
        "name": "Bachelor of Social Sciences",
        "faculty": "Faculty of Humanities and Social Sciences",
        "duration_years": 3,
        "intake_months": [8, 1, 3],
        "campus": ["Main Campus (Kansanga)", "Western Campus (Ishaka)"],
        "tuition_ugx_per_semester": 2000000,
        "tuition_usd_per_semester": 650,
        "category": "Social Sciences",
        "requirements": {
            "subjects": ["Any combination", "Good English"],
            "minimum_education": "A-Level with 2 principal passes",
            "alternative": "Diploma in Social Sciences"
        },
        "career_prospects": ["Social Worker", "Community Development Officer", "NGO Manager"],
        "accreditation": "NCHE",
    },
    {
        "id": "mba",
        "code": "MBA",
        "name": "Master of Business Administration",
        "faculty": "Faculty of Business and Management",
        "duration_years": 2,
        "intake_months": [8, 1],
        "campus": ["Main Campus (Kansanga)", "Western Campus (Ishaka)"],
        "tuition_ugx_per_semester": 3500000,
        "tuition_usd_per_semester": 1100,
        "category": "Business",
        "requirements": {
            "subjects": ["Bachelor's degree in any field"],
            "minimum_education": "Bachelor's degree with Second Class Lower",
            "alternative": "Relevant work experience"
        },
        "career_prospects": ["CEO", "Operations Manager", "Management Consultant"],
        "accreditation": "NCHE",
    },
    {
        "id": "mphil",
        "code": "MPhil",
        "name": "Master of Philosophy (Research)",
        "faculty": "School of Postgraduate Studies",
        "duration_years": 2,
        "intake_months": [8, 1],
        "campus": ["Main Campus (Kansanga)"],
        "tuition_ugx_per_semester": 3500000,
        "tuition_usd_per_semester": 1100,
        "category": "Research",
        "requirements": {
            "subjects": ["Bachelor's degree in relevant field"],
            "minimum_education": "Bachelor's degree with Second Class Lower",
            "alternative": "Research experience"
        },
        "career_prospects": ["Researcher", "Academic", "Policy Analyst"],
        "accreditation": "NCHE",
    },
]

# ---------------------------------------------------------------------------
# Simple recommendation logic
# ---------------------------------------------------------------------------
def _get_simple_recommendations(user_profile: dict) -> list:
    """Get simple recommendations based on user interests and qualifications"""
    recommendations = []
    
    # Get user preferences
    interests = user_profile.get("interests", [])
    education_level = user_profile.get("education_level", "")
    subjects = user_profile.get("subjects", [])
    
    for programme in KIU_PROGRAMMES:
        score = 0
        reasons = []
        
        # Check category match
        if interests:
            for interest in interests:
                if interest.lower() in programme["category"].lower():
                    score += 30
                    reasons.append(f"Matches your interest in {interest}")
        
        # Check subject match
        if subjects:
            programme_subjects = programme["requirements"]["subjects"]
            matching_subjects = [s for s in subjects if any(p.lower() in s.lower() for p in programme_subjects)]
            if matching_subjects:
                score += 20
                reasons.append(f"Subject match: {', '.join(matching_subjects)}")
        
        # Check education level
        if education_level:
            if "A-Level" in education_level and "principal passes" in programme["requirements"]["minimum_education"]:
                score += 25
                reasons.append("Education level matches requirements")
            elif "Diploma" in education_level and "Diploma" in programme["requirements"]["alternative"]:
                score += 20
                reasons.append("Diploma pathway available")
            elif "Bachelor" in education_level and "Bachelor's degree" in programme["requirements"]["minimum_education"]:
                score += 25
                reasons.append("Bachelor's degree qualifies")
        
        # Add to recommendations if score is significant
        if score >= 20:
            recommendations.append({
                **programme,
                "match_score": score,
                "match_reasons": reasons,
                "apply_url": f"/apply/{programme['id']}"
            })
    
    # Sort by match score
    recommendations.sort(key=lambda x: x["match_score"], reverse=True)
    return recommendations[:10]  # Return top 10

# ---------------------------------------------------------------------------
# Simple routes
# ---------------------------------------------------------------------------
@recommendations_bp.route("/v1/programmes", methods=["GET"])
def list_programmes():
    """List all available programmes"""
    category = request.args.get("category", "").lower()
    
    programmes = KIU_PROGRAMMES
    if category:
        programmes = [p for p in programmes if category in p["category"].lower()]
    
    return jsonify({
        "programmes": programmes,
        "categories": list(set(p["category"] for p in KIU_PROGRAMMES)),
        "total": len(programmes)
    })

@recommendations_bp.route("/v1/recommend", methods=["POST"])
def get_recommendations():
    """Get personalized programme recommendations"""
    try:
        user_profile = request.get_json() or {}
        
        if not user_profile:
            return jsonify({"error": "Please provide your preferences"}), 400
        
        recommendations = _get_simple_recommendations(user_profile)
        
        return jsonify({
            "recommendations": recommendations,
            "total": len(recommendations),
            "message": "Based on your interests and qualifications"
        })
        
    except Exception as e:
        log.error(f"Error getting recommendations: {e}")
        return jsonify({"error": "Unable to get recommendations"}), 500

@recommendations_bp.route("/v1/programme/<programme_id>", methods=["GET"])
def get_programme_details(programme_id):
    """Get details for a specific programme"""
    programme = next((p for p in KIU_PROGRAMMES if p["id"] == programme_id), None)
    
    if not programme:
        return jsonify({"error": "Programme not found"}), 404
    
    # Add apply URL
    programme["apply_url"] = f"/apply/{programme_id}"
    
    return jsonify(programme)
