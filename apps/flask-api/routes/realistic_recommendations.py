"""
apps/flask-api/routes/realistic_recommendations.py

Realistic programme recommendation engine for KIU Uganda.

Based on actual university admission standards:
- NCHE Uganda minimum requirements
- Real subject combinations and grade thresholds
- Competition levels and admission quotas
- Authentic eligibility assessment
"""

from flask import Blueprint, request, jsonify
import logging
from datetime import datetime

realistic_recommendations_bp = Blueprint("realistic_recommendations", __name__)
log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Realistic programme catalogue with actual admission standards
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
        "competition_level": "Very High",
        "annual_quota": 80,
        "nche_requirements": {
            "minimum_subjects": ["Biology", "Chemistry"],
            "essential_subjects": ["Biology", "Chemistry"],
            "relevant_subjects": ["Physics", "Mathematics"],
            "minimum_uace_points": 15,
            "minimum_principal_passes": 2,
            "minimum_uce_passes": 5,
            "mandatory_credits": ["Biology", "Chemistry", "English", "Mathematics"],
            "diploma_alternative": {
                "eligible": True,
                "diplomas": ["Diploma in Clinical Medicine", "Diploma in Nursing", "Diploma in Medical Laboratory"],
                "minimum_class": "Credit",
                "work_experience": 2,
                "professional_registration": True
            }
        },
        "admission_statistics": {
            "applications_2024": 1200,
            "admitted_2024": 75,
            "average_uace_points_admitted": 18,
            "cut_off_points": 16
        },
        "career_prospects": ["Medical Officer", "Surgeon", "Specialist Physician", "Public Health Officer"],
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
        "competition_level": "High",
        "annual_quota": 150,
        "nche_requirements": {
            "minimum_subjects": ["Biology", "Chemistry"],
            "essential_subjects": ["Biology"],
            "relevant_subjects": ["Chemistry", "Physics", "Mathematics"],
            "minimum_uace_points": 12,
            "minimum_principal_passes": 1,
            "minimum_uce_passes": 5,
            "mandatory_credits": ["Biology", "Chemistry", "English", "Mathematics"],
            "diploma_alternative": {
                "eligible": True,
                "diplomas": ["Diploma in Nursing", "Diploma in Midwifery"],
                "minimum_class": "Credit",
                "work_experience": 1,
                "professional_registration": True
            }
        },
        "admission_statistics": {
            "applications_2024": 800,
            "admitted_2024": 145,
            "average_uace_points_admitted": 14,
            "cut_off_points": 12
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
        "competition_level": "Very High",
        "annual_quota": 60,
        "nche_requirements": {
            "minimum_subjects": ["Biology", "Chemistry"],
            "essential_subjects": ["Biology", "Chemistry"],
            "relevant_subjects": ["Physics", "Mathematics"],
            "minimum_uace_points": 14,
            "minimum_principal_passes": 2,
            "minimum_uce_passes": 5,
            "mandatory_credits": ["Biology", "Chemistry", "Physics", "Mathematics", "English"],
            "diploma_alternative": {
                "eligible": True,
                "diplomas": ["Diploma in Pharmacy", "Diploma in Pharmaceutical Sciences"],
                "minimum_class": "Credit",
                "work_experience": 2,
                "professional_registration": True
            }
        },
        "admission_statistics": {
            "applications_2024": 600,
            "admitted_2024": 58,
            "average_uace_points_admitted": 16,
            "cut_off_points": 14
        },
        "career_prospects": ["Pharmacist", "Drug Inspector", "Clinical Pharmacist", "Hospital Pharmacist"],
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
        "competition_level": "High",
        "annual_quota": 120,
        "nche_requirements": {
            "minimum_subjects": ["Any two principal subjects"],
            "essential_subjects": [],
            "relevant_subjects": ["Literature", "History", "Geography", "Economics", "Divinity"],
            "minimum_uace_points": 10,
            "minimum_principal_passes": 2,
            "minimum_uce_passes": 5,
            "mandatory_credits": ["English", "Mathematics"],
            "diploma_alternative": {
                "eligible": True,
                "diplomas": ["Diploma in Law", "Diploma in Legal Studies"],
                "minimum_class": "Credit",
                "work_experience": 1,
                "professional_registration": False
            }
        },
        "admission_statistics": {
            "applications_2024": 900,
            "admitted_2024": 115,
            "average_uace_points_admitted": 13,
            "cut_off_points": 11
        },
        "career_prospects": ["Lawyer", "Judge", "Legal Advisor", "Prosecutor", "Company Secretary"],
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
        "competition_level": "High",
        "annual_quota": 80,
        "nche_requirements": {
            "minimum_subjects": ["Mathematics", "Physics"],
            "essential_subjects": ["Mathematics", "Physics"],
            "relevant_subjects": ["Chemistry", "Economics", "Technical Drawing"],
            "minimum_uace_points": 12,
            "minimum_principal_passes": 2,
            "minimum_uce_passes": 5,
            "mandatory_credits": ["Mathematics", "Physics", "Chemistry", "English"],
            "diploma_alternative": {
                "eligible": True,
                "diplomas": ["Diploma in Civil Engineering", "Diploma in Building Construction"],
                "minimum_class": "Credit",
                "work_experience": 2,
                "professional_registration": False
            }
        },
        "admission_statistics": {
            "applications_2024": 450,
            "admitted_2024": 75,
            "average_uace_points_admitted": 14,
            "cut_off_points": 12
        },
        "career_prospects": ["Civil Engineer", "Structural Engineer", "Project Manager", "Site Engineer"],
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
        "competition_level": "High",
        "annual_quota": 70,
        "nche_requirements": {
            "minimum_subjects": ["Mathematics", "Physics"],
            "essential_subjects": ["Mathematics", "Physics"],
            "relevant_subjects": ["Chemistry", "Economics", "Technical Drawing"],
            "minimum_uace_points": 12,
            "minimum_principal_passes": 2,
            "minimum_uce_passes": 5,
            "mandatory_credits": ["Mathematics", "Physics", "Chemistry", "English"],
            "diploma_alternative": {
                "eligible": True,
                "diplomas": ["Diploma in Electrical Engineering", "Diploma in Telecommunications"],
                "minimum_class": "Credit",
                "work_experience": 2,
                "professional_registration": False
            }
        },
        "admission_statistics": {
            "applications_2024": 400,
            "admitted_2024": 68,
            "average_uace_points_admitted": 13,
            "cut_off_points": 11
        },
        "career_prospects": ["Electrical Engineer", "Power Systems Engineer", "Telecom Engineer", "Control Engineer"],
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
        "competition_level": "Medium",
        "annual_quota": 120,
        "nche_requirements": {
            "minimum_subjects": ["Mathematics", "Physics"],
            "essential_subjects": ["Mathematics"],
            "relevant_subjects": ["Physics", "Computer Studies", "Economics"],
            "minimum_uace_points": 10,
            "minimum_principal_passes": 2,
            "minimum_uce_passes": 5,
            "mandatory_credits": ["Mathematics", "Physics", "English"],
            "diploma_alternative": {
                "eligible": True,
                "diplomas": ["Diploma in Computer Science", "Diploma in Information Technology"],
                "minimum_class": "Credit",
                "work_experience": 1,
                "professional_registration": False
            }
        },
        "admission_statistics": {
            "applications_2024": 350,
            "admitted_2024": 110,
            "average_uace_points_admitted": 11,
            "cut_off_points": 9
        },
        "career_prospects": ["Software Developer", "Systems Analyst", "Network Engineer", "Data Scientist"],
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
        "competition_level": "Low",
        "annual_quota": 150,
        "nche_requirements": {
            "minimum_subjects": ["Mathematics", "Computer Studies"],
            "essential_subjects": ["Mathematics"],
            "relevant_subjects": ["Computer Studies", "Physics", "Economics"],
            "minimum_uace_points": 8,
            "minimum_principal_passes": 1,
            "minimum_uce_passes": 5,
            "mandatory_credits": ["Mathematics", "English"],
            "diploma_alternative": {
                "eligible": True,
                "diplomas": ["Diploma in IT", "Diploma in Computer Science"],
                "minimum_class": "Pass",
                "work_experience": 1,
                "professional_registration": False
            }
        },
        "admission_statistics": {
            "applications_2024": 200,
            "admitted_2024": 145,
            "average_uace_points_admitted": 9,
            "cut_off_points": 7
        },
        "career_prospects": ["IT Manager", "Network Administrator", "Database Administrator", "Systems Analyst"],
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
        "competition_level": "Low",
        "annual_quota": 200,
        "nche_requirements": {
            "minimum_subjects": ["Any two principal subjects"],
            "essential_subjects": [],
            "relevant_subjects": ["Economics", "Mathematics", "Accounting", "Business Studies"],
            "minimum_uace_points": 6,
            "minimum_principal_passes": 2,
            "minimum_uce_passes": 5,
            "mandatory_credits": ["English", "Mathematics"],
            "diploma_alternative": {
                "eligible": True,
                "diplomas": ["Diploma in Business Administration", "Diploma in Accounting"],
                "minimum_class": "Pass",
                "work_experience": 1,
                "professional_registration": False
            }
        },
        "admission_statistics": {
            "applications_2024": 300,
            "admitted_2024": 190,
            "average_uace_points_admitted": 8,
            "cut_off_points": 6
        },
        "career_prospects": ["Business Manager", "Marketing Manager", "HR Manager", "Operations Manager"],
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
        "competition_level": "Medium",
        "annual_quota": 120,
        "nche_requirements": {
            "minimum_subjects": ["Mathematics", "Economics"],
            "essential_subjects": ["Mathematics"],
            "relevant_subjects": ["Economics", "Accounting", "Business Studies"],
            "minimum_uace_points": 8,
            "minimum_principal_passes": 2,
            "minimum_uce_passes": 5,
            "mandatory_credits": ["Mathematics", "English", "Accounting"],
            "diploma_alternative": {
                "eligible": True,
                "diplomas": ["Diploma in Commerce", "Diploma in Accounting"],
                "minimum_class": "Credit",
                "work_experience": 1,
                "professional_registration": False
            }
        },
        "admission_statistics": {
            "applications_2024": 280,
            "admitted_2024": 115,
            "average_uace_points_admitted": 10,
            "cut_off_points": 8
        },
        "career_prospects": ["Accountant", "Financial Analyst", "Auditor", "Tax Consultant"],
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
        "competition_level": "Medium",
        "annual_quota": 60,
        "nche_requirements": {
            "minimum_qualification": "Bachelor's degree",
            "minimum_class": "Second Class Lower",
            "relevant_fields": ["Business", "Management", "Economics", "Accounting", "Finance"],
            "work_experience_required": 2,
            "gmat_required": False,
            "interview_required": True
        },
        "admission_statistics": {
            "applications_2024": 150,
            "admitted_2024": 55,
            "average_gpa_admitted": 3.2,
            "average_work_experience": 3.5
        },
        "career_prospects": ["CEO", "Operations Manager", "Management Consultant", "Business Analyst"],
        "accreditation": "NCHE",
    }
]

# ---------------------------------------------------------------------------
# Realistic admission assessment logic
# ---------------------------------------------------------------------------
def _calculate_uace_points(subjects_grades: dict) -> int:
    """Calculate UACE points based on grade system: A=6, B=5, C=4, D=3, E=2, O=1, F=0"""
    grade_points = {"A": 6, "B": 5, "C": 4, "D": 3, "E": 2, "O": 1, "F": 0}
    total_points = 0
    
    for subject, grade in subjects_grades.items():
        if grade.upper() in grade_points:
            total_points += grade_points[grade.upper()]
    
    return total_points

def _assess_eligibility(programme: dict, applicant: dict) -> dict:
    """Realistic eligibility assessment based on NCHE standards"""
    nche_req = programme["nche_requirements"]
    assessment = {
        "eligible": False,
        "strong_candidate": False,
        "admission_chance": "Low",
        "reasons_pass": [],
        "reasons_fail": [],
        "warnings": [],
        "meets_minimum": False,
        "points_calculation": {}
    }
    
    # Check UACE qualifications
    if "uace_subjects" in applicant:
        uace_subjects = applicant["uace_subjects"]
        uace_points = _calculate_uace_points(applicant.get("uace_grades", {}))
        principal_passes = applicant.get("principal_passes", 0)
        
        assessment["points_calculation"] = {
            "total_points": uace_points,
            "principal_passes": principal_passes,
            "required_points": nche_req["minimum_uace_points"],
            "required_principal_passes": nche_req["minimum_principal_passes"]
        }
        
        # Check essential subjects
        essential_met = True
        for essential in nche_req["essential_subjects"]:
            if essential not in uace_subjects:
                essential_met = False
                assessment["reasons_fail"].append(f"Missing essential subject: {essential}")
            else:
                assessment["reasons_pass"].append(f"Has essential subject: {essential}")
        
        # Check minimum requirements
        if (uace_points >= nche_req["minimum_uace_points"] and 
            principal_passes >= nche_req["minimum_principal_passes"] and
            essential_met):
            assessment["meets_minimum"] = True
            assessment["reasons_pass"].append(f"Meets minimum UACE requirements")
        
        # Check against competition
        if "cut_off_points" in programme["admission_statistics"]:
            cut_off = programme["admission_statistics"]["cut_off_points"]
            if uace_points >= cut_off:
                assessment["strong_candidate"] = True
                assessment["reasons_pass"].append(f"Above cut-off points ({cut_off})")
            else:
                assessment["warnings"].append(f"Below cut-off points ({cut_off})")
    
    # Check UCE requirements
    if "uce_passes" in applicant:
        uce_passes = applicant["uce_passes"]
        if uce_passes >= nche_req["minimum_uce_passes"]:
            assessment["reasons_pass"].append(f"Meets UCE requirement ({uce_passes} passes)")
        else:
            assessment["reasons_fail"].append(f"Insufficient UCE passes ({uce_passes} < {nche_req['minimum_uce_passes']})")
    
    # Check diploma alternative
    if "diploma_type" in applicant:
        diploma_alt = nche_req["diploma_alternative"]
        if applicant["diploma_type"] in diploma_alt["diplomas"]:
            if applicant.get("diploma_class") in ["Credit", "Distinction", "First Class", "Second Class Upper"]:
                assessment["reasons_pass"].append(f"Diploma pathway: {applicant['diploma_type']}")
                assessment["meets_minimum"] = True
            else:
                assessment["reasons_fail"].append(f"Diploma class too low: {applicant.get('diploma_class')}")
        else:
            assessment["reasons_fail"].append(f"Diploma not relevant: {applicant.get('diploma_type')}")
    
    # Check postgraduate requirements
    if "bachelor_gpa" in applicant and programme["category"] == "Business":
        if applicant["bachelor_gpa"] >= 3.0:
            assessment["reasons_pass"].append(f"Good GPA: {applicant['bachelor_gpa']}")
            assessment["meets_minimum"] = True
        else:
            assessment["reasons_fail"].append(f"GPA too low: {applicant['bachelor_gpa']}")
    
    # Determine admission chance
    if assessment["strong_candidate"]:
        assessment["admission_chance"] = "High"
        assessment["eligible"] = True
    elif assessment["meets_minimum"]:
        assessment["admission_chance"] = "Medium"
        assessment["eligible"] = True
    else:
        assessment["admission_chance"] = "Low"
        assessment["eligible"] = False
    
    return assessment

def _get_realistic_recommendations(applicant: dict) -> list:
    """Get realistic recommendations based on actual admission standards"""
    recommendations = []
    
    for programme in KIU_PROGRAMMES:
        assessment = _assess_eligibility(programme, applicant)
        
        if assessment["eligible"] or assessment["meets_minimum"]:
            recommendation = {
                **programme,
                "assessment": assessment,
                "apply_url": f"/apply/{programme['id']}",
                "recommendation_reason": f"Based on your qualifications and {programme['competition_level'].lower()} competition"
            }
            recommendations.append(recommendation)
    
    # Sort by admission chance and competition level
    chance_priority = {"High": 3, "Medium": 2, "Low": 1}
    competition_priority = {"Low": 3, "Medium": 2, "High": 1, "Very High": 0}
    
    recommendations.sort(key=lambda x: (
        chance_priority.get(x["assessment"]["admission_chance"], 0),
        competition_priority.get(x["competition_level"], 0),
        x["assessment"]["points_calculation"].get("total_points", 0)
    ), reverse=True)
    
    return recommendations

# ---------------------------------------------------------------------------
# API Routes
# ---------------------------------------------------------------------------
@recommendations_bp.route("/v1/programmes", methods=["GET"])
def list_programmes():
    """List all available programmes with admission statistics"""
    category = request.args.get("category", "").lower()
    
    programmes = KIU_PROGRAMMES
    if category:
        programmes = [p for p in programmes if category in p["category"].lower()]
    
    return jsonify({
        "programmes": programmes,
        "categories": list(set(p["category"] for p in KIU_PROGRAMMES)),
        "total": len(programmes)
    })

@recommendations_bp.route("/v1/assess", methods=["POST"])
def assess_admission():
    """Realistic admission assessment"""
    try:
        applicant = request.get_json()
        if not applicant:
            return jsonify({"error": "Please provide your academic details"}), 400
        
        recommendations = _get_realistic_recommendations(applicant)
        
        return jsonify({
            "recommendations": recommendations,
            "total": len(recommendations),
            "assessment_summary": {
                "eligible_programs": len([r for r in recommendations if r["assessment"]["eligible"]]),
                "strong_candidates": len([r for r in recommendations if r["assessment"]["strong_candidate"]]),
                "message": "Based on NCHE standards and actual admission statistics"
            }
        })
        
    except Exception as e:
        log.error(f"Error in admission assessment: {e}")
        return jsonify({"error": "Unable to complete assessment"}), 500

@recommendations_bp.route("/v1/programme/<programme_id>", methods=["GET"])
def get_programme_details(programme_id):
    """Get detailed programme information with admission requirements"""
    programme = next((p for p in KIU_PROGRAMMES if p["id"] == programme_id), None)
    
    if not programme:
        return jsonify({"error": "Programme not found"}), 404
    
    programme["apply_url"] = f"/apply/{programme_id}"
    
    return jsonify(programme)

@recommendations_bp.route("/v1/eligibility-check", methods=["POST"])
def check_eligibility():
    """Quick eligibility check for a specific programme"""
    try:
        data = request.get_json()
        programme_id = data.get("programme_id")
        applicant = data.get("applicant", {})
        
        if not programme_id:
            return jsonify({"error": "Programme ID required"}), 400
        
        programme = next((p for p in KIU_PROGRAMMES if p["id"] == programme_id), None)
        if not programme:
            return jsonify({"error": "Programme not found"}), 404
        
        assessment = _assess_eligibility(programme, applicant)
        
        return jsonify({
            "programme": {
                "id": programme["id"],
                "name": programme["name"],
                "category": programme["category"],
                "competition_level": programme["competition_level"]
            },
            "assessment": assessment
        })
        
    except Exception as e:
        log.error(f"Error in eligibility check: {e}")
        return jsonify({"error": "Unable to check eligibility"}), 500
