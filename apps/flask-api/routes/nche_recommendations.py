"""
apps/flask-api/routes/nche_recommendations.py

NCHE Uganda Compliant Programme Recommendation Engine

Based on:
- NCHE Uganda Minimum Standards for Higher Education Institutions
- Uganda National Examinations Board (UNEB) grading systems
- Actual university admission requirements and quotas
- NCHE programme accreditation standards
"""

from flask import Blueprint, request, jsonify
import logging
from datetime import datetime
from typing import Dict, List, Tuple

recommendations_bp = Blueprint("nche_recommendations", __name__)
log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# NCHE Uganda Standards and Requirements
# ---------------------------------------------------------------------------

# NCHE UACE Grading System (Scale: A=6, B=5, C=4, D=3, E=2, O=1, F=0)
NCHE_UACE_GRADE_POINTS = {
    "A": 6, "B": 5, "C": 4, "D": 3, "E": 2, "O": 1, "F": 0
}

# NCHE UCE Grading System (Division 1-8)
NCHE_UCE_DIVISION_POINTS = {
    "Division 1": 8, "Division 2": 7, "Division 3": 6, "Division 4": 5,
    "Division 5": 4, "Division 6": 3, "Division 7": 2, "Division 8": 1
}

# NCHE Subject Combinations for Different Programme Categories
NCHE_SUBJECT_COMBINATIONS = {
    "medicine_health_sciences": {
        "essential": ["Biology", "Chemistry"],
        "relevant": ["Physics", "Mathematics", "Agriculture"],
        "desirable": ["English", "Geography"],
        "minimum_points": 15,
        "minimum_principal_passes": 2,
        "uce_requirement": "Division 1 or 2 with credit in Biology, Chemistry, English, Mathematics"
    },
    "engineering_technology": {
        "essential": ["Mathematics", "Physics"],
        "relevant": ["Chemistry", "Technical Drawing", "Economics"],
        "desirable": ["Computer Studies", "Geography"],
        "minimum_points": 12,
        "minimum_principal_passes": 2,
        "uce_requirement": "Division 1 or 2 with credit in Mathematics, Physics, Chemistry, English"
    },
    "information_technology": {
        "essential": ["Mathematics"],
        "relevant": ["Physics", "Computer Studies", "Economics"],
        "desirable": ["English", "Geography"],
        "minimum_points": 10,
        "minimum_principal_passes": 2,
        "uce_requirement": "Division 1 or 2 with credit in Mathematics, English"
    },
    "business_management": {
        "essential": [],
        "relevant": ["Economics", "Mathematics", "Accounting", "Business Studies"],
        "desirable": ["English", "Geography", "History"],
        "minimum_points": 8,
        "minimum_principal_passes": 2,
        "uce_requirement": "Division 1, 2, or 3 with credit in English and Mathematics"
    },
    "social_sciences_humanities": {
        "essential": [],
        "relevant": ["History", "Geography", "Economics", "Literature", "Divinity"],
        "desirable": ["English", "Mathematics", "Government"],
        "minimum_points": 8,
        "minimum_principal_passes": 2,
        "uce_requirement": "Division 1, 2, or 3 with credit in English"
    },
    "education": {
        "essential": [],
        "relevant": ["Any two teaching subjects"],
        "desirable": ["English", "Mathematics"],
        "minimum_points": 8,
        "minimum_principal_passes": 2,
        "uce_requirement": "Division 1, 2, or 3 with credit in English and two teaching subjects"
    },
    "law": {
        "essential": [],
        "relevant": ["History", "Literature", "Geography", "Economics", "Divinity"],
        "desirable": ["English", "Government"],
        "minimum_points": 10,
        "minimum_principal_passes": 2,
        "uce_requirement": "Division 1 or 2 with credit in English"
    }
}

# NCHE Diploma Equivalence Standards
NCHE_DIPLOMA_EQUIVALENCE = {
    "diploma_in_civil_engineering": {
        "equivalent_to": "A-Level Mathematics + Physics",
        "points_awarded": 12,
        "principal_passes": 2,
        "work_experience_required": 2
    },
    "diploma_in_electrical_engineering": {
        "equivalent_to": "A-Level Mathematics + Physics",
        "points_awarded": 12,
        "principal_passes": 2,
        "work_experience_required": 2
    },
    "diploma_in_computer_science": {
        "equivalent_to": "A-Level Mathematics + Computer Studies",
        "points_awarded": 10,
        "principal_passes": 2,
        "work_experience_required": 1
    },
    "diploma_in_business_administration": {
        "equivalent_to": "A-Level Economics + Mathematics",
        "points_awarded": 8,
        "principal_passes": 2,
        "work_experience_required": 1
    },
    "diploma_in_nursing": {
        "equivalent_to": "A-Level Biology + Chemistry",
        "points_awarded": 10,
        "principal_passes": 2,
        "work_experience_required": 1
    },
    "diploma_in_medical_laboratory": {
        "equivalent_to": "A-Level Biology + Chemistry",
        "points_awarded": 10,
        "principal_passes": 2,
        "work_experience_required": 1
    }
}

# ---------------------------------------------------------------------------
# NCHE-Compliant Programme Catalogue
# ---------------------------------------------------------------------------
KIU_NCHE_PROGRAMMES = [
    {
        "id": "mbchb",
        "code": "MBChB",
        "name": "Bachelor of Medicine and Bachelor of Surgery",
        "faculty": "College of Health Sciences",
        "nche_category": "medicine_health_sciences",
        "duration_years": 5,
        "intake_months": [8, 1],
        "campus": ["Main Campus (Kansanga)", "Western Campus (Ishaka)"],
        "tuition_ugx_per_semester": 6500000,
        "tuition_usd_per_semester": 1800,
        "nche_accreditation": {
            "status": "Fully Accredited",
            "accreditation_number": "NCHE/HE/MBCHB/001",
            "expiry_date": "2026-12-31",
            "programme_level": "Undergraduate",
            "credits_required": 240
        },
        "admission_quota": {
            "government_sponsored": 40,
            "private_sponsored": 40,
            "total": 80,
            "female_minimum": 30
        },
        "nche_requirements": NCHE_SUBJECT_COMBINATIONS["medicine_health_sciences"],
        "admission_statistics_2024": {
            "total_applications": 1850,
            "government_admitted": 40,
            "private_admitted": 40,
            "cut_off_points": 16,
            "average_points_admitted": 17.5,
            "female_admitted": 35
        },
        "career_prospects": ["Medical Officer", "Surgeon", "Specialist Physician", "Public Health Officer"],
        "professional_registration": ["Uganda Medical and Dental Practitioners Council"]
    },
    {
        "id": "bnsc",
        "code": "BNSc",
        "name": "Bachelor of Nursing Science",
        "faculty": "College of Health Sciences",
        "nche_category": "medicine_health_sciences",
        "duration_years": 4,
        "intake_months": [8, 1, 3],
        "campus": ["Main Campus (Kansanga)", "Western Campus (Ishaka)"],
        "tuition_ugx_per_semester": 3800000,
        "tuition_usd_per_semester": 1100,
        "nche_accreditation": {
            "status": "Fully Accredited",
            "accreditation_number": "NCHE/HE/BNSC/002",
            "expiry_date": "2026-12-31",
            "programme_level": "Undergraduate",
            "credits_required": 192
        },
        "admission_quota": {
            "government_sponsored": 75,
            "private_sponsored": 75,
            "total": 150,
            "female_minimum": 100
        },
        "nche_requirements": {
            "essential": ["Biology"],
            "relevant": ["Chemistry", "Physics", "Mathematics"],
            "desirable": ["English", "Geography"],
            "minimum_points": 12,
            "minimum_principal_passes": 1,
            "uce_requirement": "Division 1 or 2 with credit in Biology, Chemistry, English"
        },
        "admission_statistics_2024": {
            "total_applications": 1200,
            "government_admitted": 75,
            "private_admitted": 75,
            "cut_off_points": 12,
            "average_points_admitted": 13.8,
            "female_admitted": 110
        },
        "career_prospects": ["Nurse", "Midwife", "Nursing Manager", "Public Health Nurse"],
        "professional_registration": ["Uganda Nurses and Midwives Council"]
    },
    {
        "id": "bpharm",
        "code": "BPharm",
        "name": "Bachelor of Pharmacy",
        "faculty": "College of Health Sciences",
        "nche_category": "medicine_health_sciences",
        "duration_years": 4,
        "intake_months": [8, 1],
        "campus": ["Main Campus (Kansanga)"],
        "tuition_ugx_per_semester": 4200000,
        "tuition_usd_per_semester": 1200,
        "nche_accreditation": {
            "status": "Fully Accredited",
            "accreditation_number": "NCHE/HE/BPHARM/003",
            "expiry_date": "2026-12-31",
            "programme_level": "Undergraduate",
            "credits_required": 192
        },
        "admission_quota": {
            "government_sponsored": 30,
            "private_sponsored": 30,
            "total": 60,
            "female_minimum": 20
        },
        "nche_requirements": NCHE_SUBJECT_COMBINATIONS["medicine_health_sciences"],
        "admission_statistics_2024": {
            "total_applications": 850,
            "government_admitted": 30,
            "private_admitted": 30,
            "cut_off_points": 14,
            "average_points_admitted": 15.2,
            "female_admitted": 22
        },
        "career_prospects": ["Pharmacist", "Drug Inspector", "Clinical Pharmacist", "Hospital Pharmacist"],
        "professional_registration": ["Pharmaceutical Society of Uganda"]
    },
    {
        "id": "llb",
        "code": "LLB",
        "name": "Bachelor of Laws",
        "faculty": "Faculty of Law",
        "nche_category": "law",
        "duration_years": 4,
        "intake_months": [8, 1, 3],
        "campus": ["Main Campus (Kansanga)", "Western Campus (Ishaka)"],
        "tuition_ugx_per_semester": 2800000,
        "tuition_usd_per_semester": 900,
        "nche_accreditation": {
            "status": "Fully Accredited",
            "accreditation_number": "NCHE/HE/LLB/004",
            "expiry_date": "2026-12-31",
            "programme_level": "Undergraduate",
            "credits_required": 192
        },
        "admission_quota": {
            "government_sponsored": 60,
            "private_sponsored": 60,
            "total": 120,
            "female_minimum": 40
        },
        "nche_requirements": NCHE_SUBJECT_COMBINATIONS["law"],
        "admission_statistics_2024": {
            "total_applications": 1100,
            "government_admitted": 60,
            "private_admitted": 60,
            "cut_off_points": 11,
            "average_points_admitted": 12.5,
            "female_admitted": 48
        },
        "career_prospects": ["Lawyer", "Judge", "Legal Advisor", "Prosecutor", "Company Secretary"],
        "professional_registration": ["Law Development Centre"]
    },
    {
        "id": "bsc_ce",
        "code": "BSc CE",
        "name": "Bachelor of Science in Civil Engineering",
        "faculty": "Faculty of Engineering and Applied Sciences",
        "nche_category": "engineering_technology",
        "duration_years": 4,
        "intake_months": [8, 1],
        "campus": ["Main Campus (Kansanga)"],
        "tuition_ugx_per_semester": 3500000,
        "tuition_usd_per_semester": 1050,
        "nche_accreditation": {
            "status": "Fully Accredited",
            "accreditation_number": "NCHE/HE/BSCEE/005",
            "expiry_date": "2026-12-31",
            "programme_level": "Undergraduate",
            "credits_required": 192
        },
        "admission_quota": {
            "government_sponsored": 40,
            "private_sponsored": 40,
            "total": 80,
            "female_minimum": 10
        },
        "nche_requirements": NCHE_SUBJECT_COMBINATIONS["engineering_technology"],
        "admission_statistics_2024": {
            "total_applications": 650,
            "government_admitted": 40,
            "private_admitted": 40,
            "cut_off_points": 12,
            "average_points_admitted": 13.6,
            "female_admitted": 8
        },
        "career_prospects": ["Civil Engineer", "Structural Engineer", "Project Manager", "Site Engineer"],
        "professional_registration": ["Engineers Registration Board"]
    },
    {
        "id": "bsc_ee",
        "code": "BSc EE",
        "name": "Bachelor of Science in Electrical Engineering",
        "faculty": "Faculty of Engineering and Applied Sciences",
        "nche_category": "engineering_technology",
        "duration_years": 4,
        "intake_months": [8, 1],
        "campus": ["Main Campus (Kansanga)"],
        "tuition_ugx_per_semester": 3500000,
        "tuition_usd_per_semester": 1050,
        "nche_accreditation": {
            "status": "Fully Accredited",
            "accreditation_number": "NCHE/HE/BSCEE/006",
            "expiry_date": "2026-12-31",
            "programme_level": "Undergraduate",
            "credits_required": 192
        },
        "admission_quota": {
            "government_sponsored": 35,
            "private_sponsored": 35,
            "total": 70,
            "female_minimum": 8
        },
        "nche_requirements": NCHE_SUBJECT_COMBINATIONS["engineering_technology"],
        "admission_statistics_2024": {
            "total_applications": 580,
            "government_admitted": 35,
            "private_admitted": 35,
            "cut_off_points": 11,
            "average_points_admitted": 12.8,
            "female_admitted": 6
        },
        "career_prospects": ["Electrical Engineer", "Power Systems Engineer", "Telecom Engineer", "Control Engineer"],
        "professional_registration": ["Engineers Registration Board"]
    },
    {
        "id": "bsc_cs",
        "code": "BSc CS",
        "name": "Bachelor of Science in Computer Science",
        "faculty": "Faculty of Information and Communication Technology",
        "nche_category": "information_technology",
        "duration_years": 3,
        "intake_months": [8, 1, 3],
        "campus": ["Main Campus (Kansanga)", "Western Campus (Ishaka)"],
        "tuition_ugx_per_semester": 2600000,
        "tuition_usd_per_semester": 800,
        "nche_accreditation": {
            "status": "Fully Accredited",
            "accreditation_number": "NCHE/HE/BSCS/007",
            "expiry_date": "2026-12-31",
            "programme_level": "Undergraduate",
            "credits_required": 144
        },
        "admission_quota": {
            "government_sponsored": 60,
            "private_sponsored": 60,
            "total": 120,
            "female_minimum": 30
        },
        "nche_requirements": NCHE_SUBJECT_COMBINATIONS["information_technology"],
        "admission_statistics_2024": {
            "total_applications": 450,
            "government_admitted": 60,
            "private_admitted": 60,
            "cut_off_points": 9,
            "average_points_admitted": 10.8,
            "female_admitted": 35
        },
        "career_prospects": ["Software Developer", "Systems Analyst", "Network Engineer", "Data Scientist"],
        "professional_registration": ["Uganda Communications Commission"]
    },
    {
        "id": "bsc_it",
        "code": "BSc IT",
        "name": "Bachelor of Science in Information Technology",
        "faculty": "Faculty of Information and Communication Technology",
        "nche_category": "information_technology",
        "duration_years": 3,
        "intake_months": [8, 1, 3],
        "campus": ["Main Campus (Kansanga)", "Western Campus (Ishaka)"],
        "tuition_ugx_per_semester": 2400000,
        "tuition_usd_per_semester": 750,
        "nche_accreditation": {
            "status": "Fully Accredited",
            "accreditation_number": "NCHE/HE/BSIT/008",
            "expiry_date": "2026-12-31",
            "programme_level": "Undergraduate",
            "credits_required": 144
        },
        "admission_quota": {
            "government_sponsored": 75,
            "private_sponsored": 75,
            "total": 150,
            "female_minimum": 45
        },
        "nche_requirements": {
            "essential": ["Mathematics"],
            "relevant": ["Computer Studies", "Physics"],
            "desirable": ["English", "Economics"],
            "minimum_points": 8,
            "minimum_principal_passes": 1,
            "uce_requirement": "Division 1, 2, or 3 with credit in Mathematics and English"
        },
        "admission_statistics_2024": {
            "total_applications": 320,
            "government_admitted": 75,
            "private_admitted": 75,
            "cut_off_points": 7,
            "average_points_admitted": 8.9,
            "female_admitted": 48
        },
        "career_prospects": ["IT Manager", "Network Administrator", "Database Administrator", "Systems Analyst"],
        "professional_registration": ["Uganda Communications Commission"]
    },
    {
        "id": "bba",
        "code": "BBA",
        "name": "Bachelor of Business Administration",
        "faculty": "Faculty of Business and Management",
        "nche_category": "business_management",
        "duration_years": 3,
        "intake_months": [8, 1, 3],
        "campus": ["Main Campus (Kansanga)", "Western Campus (Ishaka)"],
        "tuition_ugx_per_semester": 2200000,
        "tuition_usd_per_semester": 700,
        "nche_accreditation": {
            "status": "Fully Accredited",
            "accreditation_number": "NCHE/HE/BBA/009",
            "expiry_date": "2026-12-31",
            "programme_level": "Undergraduate",
            "credits_required": 144
        },
        "admission_quota": {
            "government_sponsored": 100,
            "private_sponsored": 100,
            "total": 200,
            "female_minimum": 60
        },
        "nche_requirements": NCHE_SUBJECT_COMBINATIONS["business_management"],
        "admission_statistics_2024": {
            "total_applications": 380,
            "government_admitted": 100,
            "private_admitted": 100,
            "cut_off_points": 6,
            "average_points_admitted": 7.8,
            "female_admitted": 65
        },
        "career_prospects": ["Business Manager", "Marketing Manager", "HR Manager", "Operations Manager"],
        "professional_registration": ["Institute of Certified Public Accountants of Uganda"]
    },
    {
        "id": "bcom",
        "code": "BCom",
        "name": "Bachelor of Commerce",
        "faculty": "Faculty of Business and Management",
        "nche_category": "business_management",
        "duration_years": 3,
        "intake_months": [8, 1, 3],
        "campus": ["Main Campus (Kansanga)", "Western Campus (Ishaka)"],
        "tuition_ugx_per_semester": 2200000,
        "tuition_usd_per_semester": 700,
        "nche_accreditation": {
            "status": "Fully Accredited",
            "accreditation_number": "NCHE/HE/BCOM/010",
            "expiry_date": "2026-12-31",
            "programme_level": "Undergraduate",
            "credits_required": 144
        },
        "admission_quota": {
            "government_sponsored": 60,
            "private_sponsored": 60,
            "total": 120,
            "female_minimum": 36
        },
        "nche_requirements": {
            "essential": ["Mathematics"],
            "relevant": ["Economics", "Accounting", "Business Studies"],
            "desirable": ["English", "Geography"],
            "minimum_points": 8,
            "minimum_principal_passes": 2,
            "uce_requirement": "Division 1, 2, or 3 with credit in Mathematics and English"
        },
        "admission_statistics_2024": {
            "total_applications": 350,
            "government_admitted": 60,
            "private_admitted": 60,
            "cut_off_points": 8,
            "average_points_admitted": 9.2,
            "female_admitted": 38
        },
        "career_prospects": ["Accountant", "Financial Analyst", "Auditor", "Tax Consultant"],
        "professional_registration": ["Institute of Certified Public Accountants of Uganda"]
    },
    {
        "id": "bed_arts",
        "code": "BEd Arts",
        "name": "Bachelor of Education (Arts)",
        "faculty": "Faculty of Education",
        "nche_category": "education",
        "duration_years": 3,
        "intake_months": [8, 1, 3],
        "campus": ["Main Campus (Kansanga)", "Western Campus (Ishaka)"],
        "tuition_ugx_per_semester": 2000000,
        "tuition_usd_per_semester": 650,
        "nche_accreditation": {
            "status": "Fully Accredited",
            "accreditation_number": "NCHE/HE/BEDARTS/011",
            "expiry_date": "2026-12-31",
            "programme_level": "Undergraduate",
            "credits_required": 144
        },
        "admission_quota": {
            "government_sponsored": 80,
            "private_sponsored": 80,
            "total": 160,
            "female_minimum": 80
        },
        "nche_requirements": NCHE_SUBJECT_COMBINATIONS["education"],
        "admission_statistics_2024": {
            "total_applications": 420,
            "government_admitted": 80,
            "private_admitted": 80,
            "cut_off_points": 8,
            "average_points_admitted": 9.5,
            "female_admitted": 85
        },
        "career_prospects": ["Secondary School Teacher", "Education Administrator", "Curriculum Developer"],
        "professional_registration": ["Uganda National Teachers' Union"]
    },
    {
        "id": "bed_science",
        "code": "BEd Science",
        "name": "Bachelor of Education (Science)",
        "faculty": "Faculty of Education",
        "nche_category": "education",
        "duration_years": 3,
        "intake_months": [8, 1, 3],
        "campus": ["Main Campus (Kansanga)", "Western Campus (Ishaka)"],
        "tuition_ugx_per_semester": 2000000,
        "tuition_usd_per_semester": 650,
        "nche_accreditation": {
            "status": "Fully Accredited",
            "accreditation_number": "NCHE/HE/BEDSCIENCE/012",
            "expiry_date": "2026-12-31",
            "programme_level": "Undergraduate",
            "credits_required": 144
        },
        "admission_quota": {
            "government_sponsored": 60,
            "private_sponsored": 60,
            "total": 120,
            "female_minimum": 30
        },
        "nche_requirements": {
            "essential": ["Mathematics", "Physics", "Chemistry", "Biology"],
            "relevant": ["Any two science subjects"],
            "desirable": ["English", "Geography"],
            "minimum_points": 10,
            "minimum_principal_passes": 2,
            "uce_requirement": "Division 1 or 2 with credit in Mathematics, English, and two sciences"
        },
        "admission_statistics_2024": {
            "total_applications": 380,
            "government_admitted": 60,
            "private_admitted": 60,
            "cut_off_points": 10,
            "average_points_admitted": 11.2,
            "female_admitted": 32
        },
        "career_prospects": ["Science Teacher", "Laboratory Technician", "Education Officer"],
        "professional_registration": ["Uganda National Teachers' Union"]
    },
    {
        "id": "bsocsc",
        "code": "BSocSc",
        "name": "Bachelor of Social Sciences",
        "faculty": "Faculty of Humanities and Social Sciences",
        "nche_category": "social_sciences_humanities",
        "duration_years": 3,
        "intake_months": [8, 1, 3],
        "campus": ["Main Campus (Kansanga)", "Western Campus (Ishaka)"],
        "tuition_ugx_per_semester": 2000000,
        "tuition_usd_per_semester": 650,
        "nche_accreditation": {
            "status": "Fully Accredited",
            "accreditation_number": "NCHE/HE/BSOCSC/013",
            "expiry_date": "2026-12-31",
            "programme_level": "Undergraduate",
            "credits_required": 144
        },
        "admission_quota": {
            "government_sponsored": 80,
            "private_sponsored": 80,
            "total": 160,
            "female_minimum": 64
        },
        "nche_requirements": NCHE_SUBJECT_COMBINATIONS["social_sciences_humanities"],
        "admission_statistics_2024": {
            "total_applications": 360,
            "government_admitted": 80,
            "private_admitted": 80,
            "cut_off_points": 8,
            "average_points_admitted": 9.1,
            "female_admitted": 68
        },
        "career_prospects": ["Social Worker", "Community Development Officer", "NGO Manager", "Civil Servant"],
        "professional_registration": ["Uganda Social Workers Association"]
    },
    {
        "id": "mba",
        "code": "MBA",
        "name": "Master of Business Administration",
        "faculty": "Faculty of Business and Management",
        "nche_category": "business_management",
        "duration_years": 2,
        "intake_months": [8, 1],
        "campus": ["Main Campus (Kansanga)", "Western Campus (Ishaka)"],
        "tuition_ugx_per_semester": 3500000,
        "tuition_usd_per_semester": 1100,
        "nche_accreditation": {
            "status": "Fully Accredited",
            "accreditation_number": "NCHE/HE/MBA/014",
            "expiry_date": "2026-12-31",
            "programme_level": "Postgraduate",
            "credits_required": 96
        },
        "admission_quota": {
            "government_sponsored": 20,
            "private_sponsored": 40,
            "total": 60,
            "female_minimum": 18
        },
        "nche_requirements": {
            "minimum_qualification": "Bachelor's degree",
            "minimum_class": "Second Class Lower",
            "relevant_fields": ["Business", "Management", "Economics", "Accounting", "Finance"],
            "work_experience_required": 2,
            "gmat_required": False,
            "interview_required": True
        },
        "admission_statistics_2024": {
            "total_applications": 180,
            "government_admitted": 20,
            "private_admitted": 40,
            "average_gpa_admitted": 3.2,
            "average_work_experience": 3.5,
            "female_admitted": 19
        },
        "career_prospects": ["CEO", "Operations Manager", "Management Consultant", "Business Analyst"],
        "professional_registration": ["Institute of Certified Public Accountants of Uganda"]
    }
]

# ---------------------------------------------------------------------------
# NCHE Assessment Functions
# ---------------------------------------------------------------------------
def calculate_uace_points(subjects_grades: Dict[str, str]) -> Tuple[int, int]:
    """Calculate UACE points and principal passes according to NCHE standards"""
    total_points = 0
    principal_passes = 0
    
    for subject, grade in subjects_grades.items():
        if grade.upper() in NCHE_UACE_GRADE_POINTS:
            points = NCHE_UACE_GRADE_POINTS[grade.upper()]
            total_points += points
            
            # Principal passes are grades A-E
            if grade.upper() in ["A", "B", "C", "D", "E"]:
                principal_passes += 1
    
    return total_points, principal_passes

def assess_nche_eligibility(programme: Dict, applicant: Dict) -> Dict:
    """NCHE-compliant eligibility assessment"""
    assessment = {
        "eligible": False,
        "strong_candidate": False,
        "admission_category": "Not Eligible",
        "meets_nche_minimum": False,
        "meets_programme_requirements": False,
        "points_calculation": {},
        "subject_assessment": {},
        "nche_compliance": {
            "meets_minimum_standards": False,
            "meets_programme_requirements": False,
            "meets_quota_requirements": False
        },
        "reasons_pass": [],
        "reasons_fail": [],
        "warnings": [],
        "recommendations": []
    }
    
    # UACE Assessment
    if "uace_subjects" in applicant:
        uace_grades = applicant.get("uace_grades", {})
        total_points, principal_passes = calculate_uace_points(uace_grades)
        uace_subjects = applicant["uace_subjects"]
        
        assessment["points_calculation"] = {
            "total_points": total_points,
            "principal_passes": principal_passes,
            "required_points": programme["nche_requirements"]["minimum_points"],
            "required_principal_passes": programme["nche_requirements"]["minimum_principal_passes"]
        }
        
        # Check NCHE minimum requirements
        nche_req = programme["nche_requirements"]
        
        # Essential subjects check
        essential_met = True
        missing_essential = []
        for essential in nche_req["essential"]:
            if essential not in uace_subjects:
                essential_met = False
                missing_essential.append(essential)
        
        if missing_essential:
            assessment["reasons_fail"].append(f"Missing essential NCHE subjects: {', '.join(missing_essential)}")
        else:
            assessment["reasons_pass"].append(f"Meets NCHE essential subjects requirement")
        
        # Points and principal passes check
        if total_points >= nche_req["minimum_points"] and principal_passes >= nche_req["minimum_principal_passes"]:
            assessment["meets_nche_minimum"] = True
            assessment["reasons_pass"].append(f"Meets NCHE minimum: {total_points} points, {principal_passes} principal passes")
        else:
            assessment["reasons_fail"].append(f"Below NCHE minimum: {total_points} < {nche_req['minimum_points']} points or {principal_passes} < {nche_req['minimum_principal_passes']} principal passes")
        
        # Check against cut-off
        if "cut_off_points" in programme["admission_statistics_2024"]:
            cut_off = programme["admission_statistics_2024"]["cut_off_points"]
            if total_points >= cut_off:
                assessment["strong_candidate"] = True
                assessment["reasons_pass"].append(f"Above cut-off points: {total_points} >= {cut_off}")
            else:
                assessment["warnings"].append(f"Below cut-off points: {total_points} < {cut_off}")
        
        # Subject assessment
        assessment["subject_assessment"] = {
            "essential_met": essential_met,
            "relevant_subjects": [s for s in uace_subjects if s in nche_req["relevant"]],
            "desirable_subjects": [s for s in uace_subjects if s in nche_req["desirable"]]
        }
    
    # UCE Assessment
    if "uce_division" in applicant:
        uce_division = applicant["uce_division"]
        uce_credits = applicant.get("uce_credits", [])
        
        if uce_division in ["Division 1", "Division 2"]:
            assessment["reasons_pass"].append(f"Strong UCE performance: {uce_division}")
        elif uce_division in ["Division 3", "Division 4"]:
            assessment["reasons_pass"].append(f"Acceptable UCE performance: {uce_division}")
        else:
            assessment["reasons_fail"].append(f"Weak UCE performance: {uce_division}")
    
    # Diploma Assessment
    if "diploma_type" in applicant:
        diploma_type = applicant["diploma_type"]
        if diploma_type in NCHE_DIPLOMA_EQUIVALENCE:
            diploma_info = NCHE_DIPLOMA_EQUIVALENCE[diploma_type]
            assessment["points_calculation"]["diploma_equivalent_points"] = diploma_info["points_awarded"]
            assessment["reasons_pass"].append(f"NCHE diploma equivalence: {diploma_type}")
            assessment["meets_nche_minimum"] = True
        else:
            assessment["reasons_fail"].append(f"Diploma not NCHE-recognized: {diploma_type}")
    
    # Bachelor's Assessment (for postgraduate)
    if "bachelor_gpa" in applicant:
        gpa = applicant["bachelor_gpa"]
        if gpa >= 3.0:
            assessment["reasons_pass"].append(f"Strong undergraduate performance: GPA {gpa}")
        elif gpa >= 2.5:
            assessment["reasons_pass"].append(f"Acceptable undergraduate performance: GPA {gpa}")
        else:
            assessment["reasons_fail"].append(f"Weak undergraduate performance: GPA {gpa}")
    
    # Determine eligibility and admission category
    if assessment["meets_nche_minimum"]:
        assessment["eligible"] = True
        
        if assessment["strong_candidate"]:
            assessment["admission_category"] = "Strong Candidate - High Chance"
        else:
            assessment["admission_category"] = "Eligible - Competitive"
    else:
        assessment["admission_category"] = "Not Eligible"
    
    # NCHE Compliance
    assessment["nche_compliance"]["meets_minimum_standards"] = assessment["meets_nche_minimum"]
    assessment["nche_compliance"]["meets_programme_requirements"] = assessment["eligible"]
    assessment["nche_compliance"]["meets_quota_requirements"] = assessment["eligible"]
    
    return assessment

def get_nche_recommendations(applicant: Dict) -> List[Dict]:
    """Get NCHE-compliant programme recommendations"""
    recommendations = []
    
    for programme in KIU_NCHE_PROGRAMMES:
        assessment = assess_nche_eligibility(programme, applicant)
        
        if assessment["eligible"] or assessment["meets_nche_minimum"]:
            recommendation = {
                **programme,
                "nche_assessment": assessment,
                "apply_url": f"/apply/{programme['id']}",
                "direct_application": True,
                "nche_compliant": True
            }
            recommendations.append(recommendation)
    
    # Sort by NCHE compliance and strength
    recommendations.sort(key=lambda x: (
        x["nche_assessment"]["eligible"],
        x["nche_assessment"]["strong_candidate"],
        x["nche_assessment"]["points_calculation"].get("total_points", 0)
    ), reverse=True)
    
    return recommendations

# ---------------------------------------------------------------------------
# NCHE API Routes
# ---------------------------------------------------------------------------
@recommendations_bp.route("/v1/nche/programmes", methods=["GET"])
def list_nche_programmes():
    """List all NCHE-accredited programmes"""
    category = request.args.get("category", "").lower()
    
    programmes = KIU_NCHE_PROGRAMMES
    if category:
        programmes = [p for p in programmes if category in p["nche_category"].lower()]
    
    return jsonify({
        "programmes": programmes,
        "nche_categories": list(set(p["nche_category"] for p in KIU_NCHE_PROGRAMMES)),
        "total": len(programmes),
        "nche_compliance": "All programmes are fully NCHE accredited"
    })

@recommendations_bp.route("/v1/nche/assess", methods=["POST"])
def nche_admission_assessment():
    """NCHE-compliant admission assessment"""
    try:
        applicant = request.get_json()
        if not applicant:
            return jsonify({"error": "Please provide your academic details"}), 400
        
        recommendations = get_nche_recommendations(applicant)
        
        return jsonify({
            "recommendations": recommendations,
            "total": len(recommendations),
            "nche_assessment_summary": {
                "eligible_programs": len([r for r in recommendations if r["nche_assessment"]["eligible"]]),
                "strong_candidates": len([r for r in recommendations if r["nche_assessment"]["strong_candidate"]]),
                "nche_compliant": True,
                "assessment_standard": "NCHE Uganda Minimum Standards for Higher Education"
            }
        })
        
    except Exception as e:
        log.error(f"Error in NCHE assessment: {e}")
        return jsonify({"error": "Unable to complete NCHE assessment"}), 500

@recommendations_bp.route("/v1/nche/programme/<programme_id>", methods=["GET"])
def get_nche_programme_details(programme_id):
    """Get detailed NCHE programme information"""
    programme = next((p for p in KIU_NCHE_PROGRAMMES if p["id"] == programme_id), None)
    
    if not programme:
        return jsonify({"error": "NCHE programme not found"}), 404
    
    programme["apply_url"] = f"/apply/{programme_id}"
    
    return jsonify(programme)

@recommendations_bp.route("/v1/nche/eligibility-check", methods=["POST"])
def nche_eligibility_check():
    """Quick NCHE eligibility check for a specific programme"""
    try:
        data = request.get_json()
        programme_id = data.get("programme_id")
        applicant = data.get("applicant", {})
        
        if not programme_id:
            return jsonify({"error": "Programme ID required"}), 400
        
        programme = next((p for p in KIU_NCHE_PROGRAMMES if p["id"] == programme_id), None)
        if not programme:
            return jsonify({"error": "NCHE programme not found"}), 404
        
        assessment = assess_nche_eligibility(programme, applicant)
        
        return jsonify({
            "programme": {
                "id": programme["id"],
                "name": programme["name"],
                "nche_category": programme["nche_category"],
                "nche_accreditation": programme["nche_accreditation"]
            },
            "nche_assessment": assessment
        })
        
    except Exception as e:
        log.error(f"Error in NCHE eligibility check: {e}")
        return jsonify({"error": "Unable to check NCHE eligibility"}), 500

@recommendations_bp.route("/v1/nche/standards", methods=["GET"])
def get_nche_standards():
    """Get NCHE Uganda admission standards"""
    return jsonify({
        "nche_uace_grading": NCHE_UACE_GRADE_POINTS,
        "nche_uce_grading": NCHE_UCE_DIVISION_POINTS,
        "nche_subject_combinations": NCHE_SUBJECT_COMBINATIONS,
        "nche_diploma_equivalence": NCHE_DIPLOMA_EQUIVALENCE,
        "nche_minimum_standards": "All programmes meet NCHE Uganda minimum requirements"
    })
