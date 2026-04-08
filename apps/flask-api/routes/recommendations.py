"""
apps/flask-api/routes/recommendations.py

NCHE-compliant programme recommendation engine for KIU Uganda.

Entry routes supported (per NCHE Uganda / KIU Senate regulations):
  1. UACE Direct Entry  – UCE ≥5 passes + UACE ≥2 principal passes (same sitting)
  2. Diploma Entry      – Credit/Second-Class Diploma from NCHE-recognised institution
  3. Mature Age Entry   – Age ≥25, Mature Age Entry Exam ≥50%, approved by NCHE
  4. International      – Foreign qualifications equated by UNEB/NCHE

KIU admits 3 intakes per year: August/September · December/January · March/April
"""

from flask import Blueprint, request, jsonify
from functools import wraps
import jwt, os
from datetime import datetime

recommendations_bp = Blueprint("recommendations", __name__)

# ---------------------------------------------------------------------------
# Auth helper (re-use your existing decorator if available; this is a fallback)
# ---------------------------------------------------------------------------
def _get_user_from_cookie():
    token = request.cookies.get("auth_token")
    if not token:
        return None
    try:
        secret = os.environ.get("JWT_SECRET") or os.environ.get("SECRET_KEY", "")
        return jwt.decode(token, secret, algorithms=["HS256"])
    except jwt.PyJWTError:
        return None


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        user = _get_user_from_cookie()
        if not user:
            return jsonify({"error": "Authentication required"}), 401
        return f(*args, user=user, **kwargs)
    return decorated


# ---------------------------------------------------------------------------
# KIU Programme catalogue with NCHE entry requirements
# Source: kiu.ac.ug · NCHE Uganda minimum standards
# ---------------------------------------------------------------------------
KIU_PROGRAMMES = [
    # ── COLLEGE OF HEALTH SCIENCES ─────────────────────────────────────────
    {
        "id": "mbchb",
        "code": "MBChB",
        "name": "Bachelor of Medicine and Bachelor of Surgery",
        "faculty": "College of Health Sciences",
        "level": "undergraduate",
        "duration_years": 5,
        "intake_months": [8, 1],  # Aug and Jan
        "campus": ["Main Campus (Kansanga)", "Western Campus (Ishaka)"],
        "tuition_ugx_per_year": 6500000,
        "tuition_usd_per_year": 1800,
        "nche_entry": {
            "uace_direct": {
                "min_principal_passes": 2,
                "required_subjects": ["Biology", "Chemistry"],
                "one_of_subjects": ["Physics", "Mathematics"],
                "min_points": 15,  # UACE points (A=6, B=5, C=4, D=3, E=2, O=1, F=0)
            },
            "diploma_entry": {
                "eligible": True,
                "min_class": "Credit",
                "relevant_fields": ["Clinical Medicine", "Nursing", "Medical Laboratory", "Pharmacy Technology", "Radiography"],
                "extra": "Must be registered with relevant professional council",
            },
            "mature_age": False,  # Not eligible for MBChB
            "uace_subjects_note": "Biology and Chemistry are mandatory. Physics or Mathematics as third subject.",
        },
        "career_prospects": ["Medical Officer", "Surgeon", "Specialist Physician", "Public Health Officer"],
        "accreditation": "NCHE, Uganda Medical and Dental Practitioners Council",
    },
    {
        "id": "bns",
        "code": "BNSc",
        "name": "Bachelor of Nursing Science",
        "faculty": "College of Health Sciences",
        "level": "undergraduate",
        "duration_years": 4,
        "intake_months": [8, 1, 3],
        "campus": ["Main Campus (Kansanga)", "Western Campus (Ishaka)"],
        "tuition_ugx_per_year": 3800000,
        "tuition_usd_per_year": 1100,
        "nche_entry": {
            "uace_direct": {
                "min_principal_passes": 2,
                "required_subjects": ["Biology"],
                "one_of_subjects": ["Chemistry", "Physics", "Mathematics"],
                "min_points": 10,
            },
            "diploma_entry": {
                "eligible": True,
                "min_class": "Credit",
                "relevant_fields": ["Nursing", "Midwifery", "Clinical Medicine"],
                "extra": "Must have ≥2 years post-registration work experience",
            },
            "mature_age": True,
        },
        "career_prospects": ["Registered Nurse", "Nurse Manager", "Community Health Nurse", "Nurse Educator"],
        "accreditation": "NCHE, Uganda Nurses and Midwives Council",
    },
    {
        "id": "bpharm",
        "code": "BPharm",
        "name": "Bachelor of Pharmacy",
        "faculty": "College of Health Sciences",
        "level": "undergraduate",
        "duration_years": 4,
        "intake_months": [8, 1],
        "campus": ["Main Campus (Kansanga)"],
        "tuition_ugx_per_year": 4200000,
        "tuition_usd_per_year": 1200,
        "nche_entry": {
            "uace_direct": {
                "min_principal_passes": 2,
                "required_subjects": ["Chemistry"],
                "one_of_subjects": ["Biology", "Physics", "Mathematics"],
                "min_points": 12,
            },
            "diploma_entry": {
                "eligible": True,
                "min_class": "Credit",
                "relevant_fields": ["Pharmacy Technology", "Laboratory"],
            },
            "mature_age": True,
        },
        "career_prospects": ["Pharmacist", "Drug Inspector", "Pharmaceutical Sales", "Clinical Pharmacist"],
        "accreditation": "NCHE, Pharmacy Council of Uganda",
    },
    # ── FACULTY OF LAW ─────────────────────────────────────────────────────
    {
        "id": "llb",
        "code": "LLB",
        "name": "Bachelor of Laws",
        "faculty": "Faculty of Law",
        "level": "undergraduate",
        "duration_years": 4,
        "intake_months": [8, 1, 3],
        "campus": ["Main Campus (Kansanga)", "Western Campus (Ishaka)"],
        "tuition_ugx_per_year": 2800000,
        "tuition_usd_per_year": 900,
        "nche_entry": {
            "uace_direct": {
                "min_principal_passes": 2,
                "required_subjects": [],
                "one_of_subjects": ["History", "Economics", "Divinity", "Literature", "Government"],
                "min_points": 10,
                "arts_preferred": True,
            },
            "diploma_entry": {
                "eligible": True,
                "min_class": "Credit",
                "relevant_fields": ["Law", "Business Administration", "Public Administration", "Social Sciences"],
            },
            "mature_age": True,
        },
        "career_prospects": ["Advocate", "State Attorney", "Legal Counsel", "Magistrate", "Corporate Lawyer"],
        "accreditation": "NCHE, Law Council of Uganda",
    },
    # ── FACULTY OF ENGINEERING ─────────────────────────────────────────────
    {
        "id": "bscce",
        "code": "BSc CE",
        "name": "Bachelor of Science in Civil Engineering",
        "faculty": "Faculty of Engineering and Applied Sciences",
        "level": "undergraduate",
        "duration_years": 4,
        "intake_months": [8, 1],
        "campus": ["Main Campus (Kansanga)"],
        "tuition_ugx_per_year": 3500000,
        "tuition_usd_per_year": 1050,
        "nche_entry": {
            "uace_direct": {
                "min_principal_passes": 2,
                "required_subjects": ["Mathematics", "Physics"],
                "one_of_subjects": ["Chemistry", "Technical Drawing", "Biology"],
                "min_points": 13,
            },
            "diploma_entry": {
                "eligible": True,
                "min_class": "Credit",
                "relevant_fields": ["Civil Engineering", "Construction", "Building Technology"],
            },
            "mature_age": True,
        },
        "career_prospects": ["Civil Engineer", "Structural Engineer", "Project Manager", "Site Engineer"],
        "accreditation": "NCHE, Uganda Institution of Professional Engineers",
    },
    {
        "id": "bscee",
        "code": "BSc EE",
        "name": "Bachelor of Science in Electrical Engineering",
        "faculty": "Faculty of Engineering and Applied Sciences",
        "level": "undergraduate",
        "duration_years": 4,
        "intake_months": [8, 1],
        "campus": ["Main Campus (Kansanga)"],
        "tuition_ugx_per_year": 3500000,
        "tuition_usd_per_year": 1050,
        "nche_entry": {
            "uace_direct": {
                "min_principal_passes": 2,
                "required_subjects": ["Mathematics", "Physics"],
                "one_of_subjects": ["Chemistry", "Computer Studies"],
                "min_points": 13,
            },
            "diploma_entry": {
                "eligible": True,
                "min_class": "Credit",
                "relevant_fields": ["Electrical Engineering", "Electronics", "Telecommunications"],
            },
            "mature_age": True,
        },
        "career_prospects": ["Electrical Engineer", "Power Systems Engineer", "Telecommunications Engineer"],
        "accreditation": "NCHE, Uganda Institution of Professional Engineers",
    },
    # ── FACULTY OF ICT ──────────────────────────────────────────────────────
    {
        "id": "bsccs",
        "code": "BSc CS",
        "name": "Bachelor of Science in Computer Science",
        "faculty": "Faculty of Information and Communication Technology",
        "level": "undergraduate",
        "duration_years": 3,
        "intake_months": [8, 1, 3],
        "campus": ["Main Campus (Kansanga)", "Western Campus (Ishaka)"],
        "tuition_ugx_per_year": 2600000,
        "tuition_usd_per_year": 800,
        "nche_entry": {
            "uace_direct": {
                "min_principal_passes": 2,
                "required_subjects": ["Mathematics"],
                "one_of_subjects": ["Physics", "Computer Studies", "Chemistry"],
                "min_points": 10,
            },
            "diploma_entry": {
                "eligible": True,
                "min_class": "Pass",
                "relevant_fields": ["Computer Science", "ICT", "Information Technology", "Engineering"],
            },
            "mature_age": True,
        },
        "career_prospects": ["Software Developer", "Systems Analyst", "Database Administrator", "Network Engineer"],
        "accreditation": "NCHE",
    },
    {
        "id": "bscit",
        "code": "BSc IT",
        "name": "Bachelor of Science in Information Technology",
        "faculty": "Faculty of Information and Communication Technology",
        "level": "undergraduate",
        "duration_years": 3,
        "intake_months": [8, 1, 3],
        "campus": ["Main Campus (Kansanga)", "Western Campus (Ishaka)"],
        "tuition_ugx_per_year": 2400000,
        "tuition_usd_per_year": 750,
        "nche_entry": {
            "uace_direct": {
                "min_principal_passes": 2,
                "required_subjects": [],
                "one_of_subjects": ["Mathematics", "Physics", "Computer Studies"],
                "min_points": 8,
            },
            "diploma_entry": {
                "eligible": True,
                "min_class": "Pass",
                "relevant_fields": ["ICT", "Computer Science", "Business", "Engineering"],
            },
            "mature_age": True,
        },
        "career_prospects": ["IT Manager", "Web Developer", "IT Support Specialist", "Systems Administrator"],
        "accreditation": "NCHE",
    },
    # ── FACULTY OF BUSINESS ────────────────────────────────────────────────
    {
        "id": "bba",
        "code": "BBA",
        "name": "Bachelor of Business Administration",
        "faculty": "Faculty of Business and Management",
        "level": "undergraduate",
        "duration_years": 3,
        "intake_months": [8, 1, 3],
        "campus": ["Main Campus (Kansanga)", "Western Campus (Ishaka)"],
        "tuition_ugx_per_year": 2200000,
        "tuition_usd_per_year": 700,
        "nche_entry": {
            "uace_direct": {
                "min_principal_passes": 2,
                "required_subjects": [],
                "one_of_subjects": ["Economics", "Mathematics", "Entrepreneurship", "Commerce", "Accounting"],
                "min_points": 8,
            },
            "diploma_entry": {
                "eligible": True,
                "min_class": "Pass",
                "relevant_fields": ["Business", "Commerce", "Accounting", "Finance", "Management"],
            },
            "mature_age": True,
        },
        "career_prospects": ["Business Manager", "Entrepreneur", "Marketing Manager", "HR Manager"],
        "accreditation": "NCHE",
    },
    {
        "id": "bcom",
        "code": "BCom",
        "name": "Bachelor of Commerce",
        "faculty": "Faculty of Business and Management",
        "level": "undergraduate",
        "duration_years": 3,
        "intake_months": [8, 1, 3],
        "campus": ["Main Campus (Kansanga)", "Western Campus (Ishaka)"],
        "tuition_ugx_per_year": 2200000,
        "tuition_usd_per_year": 700,
        "nche_entry": {
            "uace_direct": {
                "min_principal_passes": 2,
                "required_subjects": [],
                "one_of_subjects": ["Economics", "Mathematics", "Commerce", "Accounting"],
                "min_points": 8,
            },
            "diploma_entry": {
                "eligible": True,
                "min_class": "Pass",
                "relevant_fields": ["Commerce", "Business", "Accounting", "Finance"],
            },
            "mature_age": True,
        },
        "career_prospects": ["Accountant", "Banker", "Financial Analyst", "Auditor", "Tax Consultant"],
        "accreditation": "NCHE",
    },
    # ── FACULTY OF EDUCATION ───────────────────────────────────────────────
    {
        "id": "bedu",
        "code": "BEd",
        "name": "Bachelor of Education (Arts)",
        "faculty": "Faculty of Education",
        "level": "undergraduate",
        "duration_years": 3,
        "intake_months": [8, 1, 3],
        "campus": ["Main Campus (Kansanga)", "Western Campus (Ishaka)"],
        "tuition_ugx_per_year": 2000000,
        "tuition_usd_per_year": 650,
        "nche_entry": {
            "uace_direct": {
                "min_principal_passes": 2,
                "required_subjects": [],
                "one_of_subjects": ["History", "Literature", "French", "Divinity", "Geography", "Economics"],
                "min_points": 8,
                "arts_preferred": True,
            },
            "diploma_entry": {
                "eligible": True,
                "min_class": "Pass",
                "relevant_fields": ["Education", "Teaching", "Social Sciences"],
            },
            "mature_age": True,
        },
        "career_prospects": ["Secondary School Teacher", "Education Officer", "Curriculum Developer"],
        "accreditation": "NCHE, National Curriculum Development Centre",
    },
    {
        "id": "bedsci",
        "code": "BEd Sci",
        "name": "Bachelor of Education (Science)",
        "faculty": "Faculty of Education",
        "level": "undergraduate",
        "duration_years": 3,
        "intake_months": [8, 1, 3],
        "campus": ["Main Campus (Kansanga)", "Western Campus (Ishaka)"],
        "tuition_ugx_per_year": 2200000,
        "tuition_usd_per_year": 680,
        "nche_entry": {
            "uace_direct": {
                "min_principal_passes": 2,
                "required_subjects": [],
                "one_of_subjects": ["Mathematics", "Physics", "Chemistry", "Biology"],
                "min_points": 8,
            },
            "diploma_entry": {
                "eligible": True,
                "min_class": "Pass",
                "relevant_fields": ["Education", "Science", "Teaching"],
            },
            "mature_age": True,
        },
        "career_prospects": ["Science Teacher", "Education Officer", "Curriculum Specialist"],
        "accreditation": "NCHE",
    },
    # ── FACULTY OF SOCIAL SCIENCES ─────────────────────────────────────────
    {
        "id": "bsocsc",
        "code": "BSocSc",
        "name": "Bachelor of Social Sciences",
        "faculty": "Faculty of Humanities and Social Sciences",
        "level": "undergraduate",
        "duration_years": 3,
        "intake_months": [8, 1, 3],
        "campus": ["Main Campus (Kansanga)", "Western Campus (Ishaka)"],
        "tuition_ugx_per_year": 2000000,
        "tuition_usd_per_year": 650,
        "nche_entry": {
            "uace_direct": {
                "min_principal_passes": 2,
                "required_subjects": [],
                "one_of_subjects": ["History", "Economics", "Sociology", "Geography", "Divinity"],
                "min_points": 8,
                "arts_preferred": True,
            },
            "diploma_entry": {
                "eligible": True,
                "min_class": "Pass",
                "relevant_fields": ["Social Sciences", "Public Administration", "Sociology"],
            },
            "mature_age": True,
        },
        "career_prospects": ["Social Worker", "Community Development Officer", "NGO Manager", "Civil Servant"],
        "accreditation": "NCHE",
    },
    # ── POSTGRADUATE ───────────────────────────────────────────────────────
    {
        "id": "mba",
        "code": "MBA",
        "name": "Master of Business Administration",
        "faculty": "Faculty of Business and Management",
        "level": "postgraduate",
        "duration_years": 2,
        "intake_months": [8, 1],
        "campus": ["Main Campus (Kansanga)", "Western Campus (Ishaka)"],
        "tuition_ugx_per_year": 3500000,
        "tuition_usd_per_year": 1100,
        "nche_entry": {
            "bachelors_required": True,
            "min_class": "Second Class Lower",
            "relevant_fields": ["Business", "Management", "Engineering", "Sciences", "Any discipline"],
            "work_experience_years": 2,
        },
        "career_prospects": ["CEO", "Operations Manager", "Management Consultant", "Finance Director"],
        "accreditation": "NCHE",
    },
    {
        "id": "mphil",
        "code": "MPhil",
        "name": "Master of Philosophy (Research)",
        "faculty": "School of Postgraduate Studies",
        "level": "postgraduate",
        "duration_years": 2,
        "intake_months": [8, 1],
        "campus": ["Main Campus (Kansanga)"],
        "tuition_ugx_per_year": 3000000,
        "tuition_usd_per_year": 950,
        "nche_entry": {
            "bachelors_required": True,
            "min_class": "Second Class Lower",
            "relevant_fields": ["Any discipline relevant to research area"],
            "work_experience_years": 0,
        },
        "career_prospects": ["Researcher", "Academic", "Policy Analyst"],
        "accreditation": "NCHE",
    },
]

INTAKE_SCHEDULE = {
    1: {"name": "January/February Intake", "application_deadline": "December 31"},
    3: {"name": "March/April Intake", "application_deadline": "February 28"},
    8: {"name": "August/September Intake", "application_deadline": "July 31"},
}

UACE_SUBJECT_CATEGORIES = {
    "sciences": ["Mathematics", "Physics", "Chemistry", "Biology", "Computer Studies", "Agriculture"],
    "arts": ["History", "Literature", "French", "Divinity", "Religious Education", "Music"],
    "social_sciences": ["Economics", "Geography", "Government", "Sociology", "Entrepreneurship"],
    "technical": ["Technical Drawing", "Fine Art", "Physical Education"],
}


# ---------------------------------------------------------------------------
# Recommendation engine
# ---------------------------------------------------------------------------
def _score_uace_programme(programme: dict, applicant: dict) -> dict:
    """
    Returns eligibility dict for a single programme based on applicant UACE data.
    NCHE Uganda rules:
      - Minimum 2 principal passes at UACE (same sitting)
      - Specific subject requirements per programme
      - UCE minimum 5 passes (validated separately)
    """
    uace = programme["nche_entry"].get("uace_direct", {})
    if not uace:
        return {"eligible": False, "route": "uace_direct", "reasons": ["Programme does not accept UACE direct entry"]}

    applicant_subjects = {s.strip() for s in applicant.get("uace_subjects", [])}
    applicant_principal_count = int(applicant.get("uace_principal_passes", 0))
    applicant_points = int(applicant.get("uace_points", 0))
    applicant_uace_year = applicant.get("uace_year")

    reasons_fail = []
    reasons_warn = []
    reasons_pass = []

    # Check 1: NCHE minimum principal passes
    min_pp = uace.get("min_principal_passes", 2)
    if applicant_principal_count < min_pp:
        reasons_fail.append(
            f"Requires {min_pp} principal pass(es) at UACE; you have {applicant_principal_count}"
        )
    else:
        reasons_pass.append(f"UACE principal passes: {applicant_principal_count} ✓")

    # Check 2: Mandatory subjects
    required = uace.get("required_subjects", [])
    missing_required = [s for s in required if s not in applicant_subjects]
    if missing_required:
        reasons_fail.append(f"Missing mandatory subject(s): {', '.join(missing_required)}")
    elif required:
        reasons_pass.append(f"Mandatory subjects met ({', '.join(required)}) ✓")

    # Check 3: At least one from recommended subjects
    one_of = uace.get("one_of_subjects", [])
    if one_of and not any(s in applicant_subjects for s in one_of):
        reasons_warn.append(
            f"Recommended to have at least one of: {', '.join(one_of)}"
        )
    elif one_of:
        matched = [s for s in one_of if s in applicant_subjects]
        reasons_pass.append(f"Subject match: {', '.join(matched)} ✓")

    # Check 4: Points
    min_pts = uace.get("min_points", 0)
    if applicant_points and applicant_points < min_pts:
        reasons_fail.append(f"Minimum {min_pts} UACE points required; you have {applicant_points}")
    elif applicant_points:
        reasons_pass.append(f"UACE points: {applicant_points} ✓")

    eligible = len(reasons_fail) == 0
    return {
        "eligible": eligible,
        "route": "uace_direct",
        "strong_match": eligible and len(reasons_warn) == 0,
        "reasons_pass": reasons_pass,
        "reasons_fail": reasons_fail,
        "reasons_warn": reasons_warn,
    }


def _score_diploma_programme(programme: dict, applicant: dict) -> dict:
    """Evaluate diploma entry route."""
    diploma_entry = programme["nche_entry"].get("diploma_entry", {})
    if not diploma_entry or not diploma_entry.get("eligible"):
        return {"eligible": False, "route": "diploma", "reasons_fail": ["Programme does not accept diploma entry"]}

    applicant_diploma_class = applicant.get("diploma_class", "")
    applicant_diploma_field = applicant.get("diploma_field", "")

    reasons_fail = []
    reasons_pass = []
    reasons_warn = []

    required_class = diploma_entry.get("min_class", "Pass")
    class_hierarchy = ["Pass", "Credit", "Distinction", "Second Class Lower", "Second Class Upper", "First Class"]

    if applicant_diploma_class:
        try:
            applicant_level = class_hierarchy.index(applicant_diploma_class)
            required_level = class_hierarchy.index(required_class) if required_class in class_hierarchy else 0
            if applicant_level < required_level:
                reasons_fail.append(f"Minimum {required_class} Diploma required; you have {applicant_diploma_class}")
            else:
                reasons_pass.append(f"Diploma class: {applicant_diploma_class} ✓")
        except ValueError:
            reasons_pass.append(f"Diploma class submitted ({applicant_diploma_class})")

    relevant_fields = diploma_entry.get("relevant_fields", [])
    if applicant_diploma_field and relevant_fields:
        field_match = any(
            field.lower() in applicant_diploma_field.lower() or applicant_diploma_field.lower() in field.lower()
            for field in relevant_fields
        )
        if field_match:
            reasons_pass.append(f"Diploma field ({applicant_diploma_field}) is relevant ✓")
        else:
            reasons_warn.append(
                f"Your diploma field ({applicant_diploma_field}) may not be directly relevant. "
                f"Relevant fields: {', '.join(relevant_fields[:3])}"
            )

    extra = diploma_entry.get("extra")
    if extra:
        reasons_warn.append(f"Additional requirement: {extra}")

    return {
        "eligible": len(reasons_fail) == 0,
        "route": "diploma",
        "strong_match": len(reasons_fail) == 0 and len(reasons_warn) == 0,
        "reasons_pass": reasons_pass,
        "reasons_fail": reasons_fail,
        "reasons_warn": reasons_warn,
    }


def _score_bachelors_programme(programme: dict, applicant: dict) -> dict:
    """Evaluate postgraduate entry (bachelors required)."""
    pg_entry = programme["nche_entry"]
    if not pg_entry.get("bachelors_required"):
        return {"eligible": False, "route": "bachelors", "reasons_fail": ["Not a postgraduate programme"]}

    reasons_fail = []
    reasons_pass = []
    reasons_warn = []

    applicant_degree_class = applicant.get("bachelors_class", "")
    class_hierarchy = ["Third Class", "Second Class Lower", "Second Class Upper", "First Class"]
    required_class = pg_entry.get("min_class", "Second Class Lower")

    if applicant_degree_class:
        try:
            applicant_level = class_hierarchy.index(applicant_degree_class)
            required_level = class_hierarchy.index(required_class)
            if applicant_level < required_level:
                reasons_fail.append(f"Minimum {required_class} degree required; you have {applicant_degree_class}")
            else:
                reasons_pass.append(f"Degree class: {applicant_degree_class} ✓")
        except ValueError:
            reasons_pass.append(f"Degree class submitted ({applicant_degree_class})")

    work_exp = pg_entry.get("work_experience_years", 0)
    applicant_work_years = int(applicant.get("work_experience_years", 0))
    if work_exp > 0:
        if applicant_work_years < work_exp:
            reasons_warn.append(f"Recommended {work_exp}+ years work experience; you have {applicant_work_years}")
        else:
            reasons_pass.append(f"Work experience: {applicant_work_years} years ✓")

    return {
        "eligible": len(reasons_fail) == 0,
        "route": "bachelors",
        "strong_match": len(reasons_fail) == 0 and len(reasons_warn) == 0,
        "reasons_pass": reasons_pass,
        "reasons_fail": reasons_fail,
        "reasons_warn": reasons_warn,
    }


def _next_intakes(intake_months: list) -> list:
    now = datetime.utcnow()
    result = []
    for month in intake_months:
        year = now.year if month >= now.month else now.year + 1
        schedule = INTAKE_SCHEDULE.get(month, {})
        result.append({
            "month": month,
            "year": year,
            "name": schedule.get("name", f"Intake {month}/{year}"),
            "application_deadline": f"{schedule.get('application_deadline', '')} {year}",
        })
    result.sort(key=lambda x: (x["year"], x["month"]))
    return result[:2]  # Show next 2 upcoming intakes


def _recommend(applicant: dict) -> dict:
    entry_route = applicant.get("entry_route", "uace_direct")
    recommended = []
    partially_eligible = []
    not_eligible = []

    for prog in KIU_PROGRAMMES:
        # Skip postgraduate if not using bachelors route
        if prog["level"] == "postgraduate" and entry_route != "bachelors":
            continue
        if prog["level"] == "undergraduate" and entry_route == "bachelors":
            continue

        if entry_route == "uace_direct":
            result = _score_uace_programme(prog, applicant)
        elif entry_route == "diploma":
            result = _score_diploma_programme(prog, applicant)
        elif entry_route == "bachelors":
            result = _score_bachelors_programme(prog, applicant)
        elif entry_route == "mature_age":
            mature_eligible = prog["nche_entry"].get("mature_age", False)
            result = {
                "eligible": mature_eligible,
                "route": "mature_age",
                "strong_match": mature_eligible,
                "reasons_pass": ["Mature age entry accepted ✓"] if mature_eligible else [],
                "reasons_fail": [] if mature_eligible else ["Programme does not accept mature age entry"],
                "reasons_warn": ["Must have passed NCHE Mature Age Entry Exam with ≥50%"] if mature_eligible else [],
            }
        else:
            continue

        entry = {
            **{k: prog[k] for k in ["id", "code", "name", "faculty", "level", "duration_years",
                                     "campus", "tuition_ugx_per_year", "tuition_usd_per_year",
                                     "career_prospects", "accreditation"]},
            "next_intakes": _next_intakes(prog["intake_months"]),
            "eligibility": result,
            "match_score": (
                100 if result.get("strong_match") else
                70 if result.get("eligible") and result.get("reasons_warn") else
                30 if not result.get("eligible") and result.get("reasons_fail") and len(result["reasons_fail"]) == 1 else
                0
            ),
        }

        if result.get("eligible") and result.get("strong_match"):
            recommended.append(entry)
        elif result.get("eligible"):
            partially_eligible.append(entry)
        else:
            not_eligible.append(entry)

    recommended.sort(key=lambda x: -x["match_score"])
    partially_eligible.sort(key=lambda x: -x["match_score"])

    return {
        "recommended": recommended,
        "partially_eligible": partially_eligible,
        "not_eligible": not_eligible,
        "total_programmes": len(KIU_PROGRAMMES),
        "entry_route": entry_route,
        "nche_note": (
            "Recommendations are based on NCHE Uganda minimum entry requirements. "
            "Final admission decisions are made by KIU's Admission Committee. "
            "Contact admissions@kiu.ac.ug for clarification."
        ),
        "kiu_intakes": [
            "August/September Intake (applications close July 31)",
            "January/February Intake (applications close December 31)",
            "March/April Intake (applications close February 28)",
        ],
    }


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------
@recommendations_bp.route("/v1/recommendations", methods=["POST"])
@login_required
def get_recommendations(user):
    """
    Get programme recommendations for the authenticated applicant.

    Body (JSON):
      entry_route: "uace_direct" | "diploma" | "mature_age" | "bachelors"

      For uace_direct:
        uace_subjects: ["Mathematics", "Physics", "Chemistry"]
        uace_principal_passes: 2
        uace_points: 15
        uace_year: 2024
        uce_passes: 7

      For diploma:
        diploma_class: "Credit" | "Distinction" | "Pass"
        diploma_field: "Computer Science"
        diploma_institution: "Uganda Polytechnic Kyambogo"

      For bachelors (postgraduate):
        bachelors_class: "Second Class Upper"
        bachelors_field: "Business Administration"
        work_experience_years: 3

      For mature_age:
        age: 27
        mature_age_score: 65  # percentage in NCHE exam
    """
    data = request.get_json(silent=True) or {}

    # Validate entry route
    valid_routes = ["uace_direct", "diploma", "mature_age", "bachelors", "international"]
    entry_route = data.get("entry_route", "uace_direct")
    if entry_route not in valid_routes:
        return jsonify({"error": f"Invalid entry_route. Must be one of: {', '.join(valid_routes)}"}), 400

    # Validate UACE route basics
    if entry_route == "uace_direct":
        uce_passes = int(data.get("uce_passes", 0))
        if uce_passes < 5:
            return jsonify({
                "error": "NCHE minimum requirement: UCE with at least 5 passes at the same sitting.",
                "code": "UCE_INSUFFICIENT",
                "uce_passes_provided": uce_passes,
                "uce_passes_required": 5,
                "alternative": "Consider Mature Age Entry, Diploma Entry, or upgrade your qualifications.",
            }), 422

        principal_passes = int(data.get("uace_principal_passes", 0))
        if principal_passes < 2:
            return jsonify({
                "error": "NCHE minimum: at least 2 principal passes at UACE for undergraduate degree entry.",
                "code": "UACE_INSUFFICIENT",
                "principal_passes_provided": principal_passes,
                "principal_passes_required": 2,
                "alternative": "Consider Diploma Entry or Mature Age Entry if you have 1 principal pass.",
                "available_programmes": [
                    "Diploma programmes (1 principal pass + 2 subsidiaries)",
                    "Higher Education Certificate (HEC) bridging programme",
                ],
            }), 422

    # Mature age validation
    if entry_route == "mature_age":
        age = int(data.get("age", 0))
        if age < 25:
            return jsonify({
                "error": "Mature Age Entry requires applicants to be at least 25 years old (NCHE regulation).",
                "code": "AGE_INSUFFICIENT",
            }), 422

    result = _recommend(data)
    return jsonify(result), 200


@recommendations_bp.route("/v1/recommendations/programmes", methods=["GET"])
def list_programmes():
    """Public endpoint — list all KIU programmes with entry requirements."""
    faculty_filter = request.args.get("faculty", "").lower()
    level_filter = request.args.get("level", "").lower()

    progs = KIU_PROGRAMMES
    if faculty_filter:
        progs = [p for p in progs if faculty_filter in p["faculty"].lower()]
    if level_filter:
        progs = [p for p in progs if p["level"] == level_filter]

    return jsonify({
        "programmes": [
            {**p, "next_intakes": _next_intakes(p["intake_months"])}
            for p in progs
        ],
        "total": len(progs),
        "intakes_per_year": 3,
        "intake_schedule": list(INTAKE_SCHEDULE.values()),
    }), 200


@recommendations_bp.route("/v1/recommendations/check-eligibility", methods=["POST"])
def check_eligibility():
    """
    Quick NCHE eligibility check — no auth required.
    Used on the public-facing 'Am I eligible?' tool.
    """
    data = request.get_json(silent=True) or {}
    programme_id = data.get("programme_id")
    entry_route = data.get("entry_route", "uace_direct")

    programme = next((p for p in KIU_PROGRAMMES if p["id"] == programme_id), None)
    if not programme:
        return jsonify({"error": "Programme not found"}), 404

    if entry_route == "uace_direct":
        result = _score_uace_programme(programme, data)
    elif entry_route == "diploma":
        result = _score_diploma_programme(programme, data)
    elif entry_route == "bachelors":
        result = _score_bachelors_programme(programme, data)
    else:
        return jsonify({"error": "Invalid entry_route"}), 400

    return jsonify({
        "programme": programme["name"],
        "faculty": programme["faculty"],
        "eligibility": result,
        "next_intakes": _next_intakes(programme["intake_months"]),
        "nche_note": "Eligibility check is indicative. Final decisions are made by KIU Admissions Committee.",
    }), 200