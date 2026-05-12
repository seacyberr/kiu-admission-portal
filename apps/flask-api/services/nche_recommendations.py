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
import sys
import os
from utils.api_response import success_response, bad_request, not_found

# Add parent directory to path to import data
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'data'))
from data import (
    BACHELORS_PROGRAMS,
    DIPLOMA_PROGRAMS,
    CERTIFICATE_PROGRAMS,
    HEC_PROGRAMS,
    get_programs_by_requirement,
    search_programs
)

# Import consolidated program database
try:
    from data.all_programs import get_all_nche_programs, get_nche_programs_by_level
    KIU_NCHE_PROGRAMMES = get_all_nche_programs()
except ImportError:
    # Fallback to legacy hardcoded programs if consolidation fails
    KIU_NCHE_PROGRAMMES = []

recommendations_bp = Blueprint("recommendations", __name__)
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
    "engineering": {
        "essential": ["Mathematics", "Physics"],
        "relevant": ["Chemistry", "Technical Drawing", "Economics", "Computer Studies"],
        "desirable": ["Biology", "Agriculture", "Further Mathematics"],
        "minimum_points": 8,
        "minimum_principal_passes": 2,
        "uce_requirement": "UCE with 5 passes including English, Mathematics and Physics at Credit level"
    },
    "engineering_technology": {
        "essential": ["Mathematics", "Physics"],
        "relevant": ["Chemistry", "Technical Drawing", "Economics", "Computer Studies"],
        "desirable": ["Biology", "Agriculture", "Further Mathematics"],
        "minimum_points": 8,
        "minimum_principal_passes": 2,
        "uce_requirement": "UCE with 5 passes including English, Mathematics and Physics at Credit level"
    },
    "health_sciences_veterinary": {
        "essential": ["Biology", "Chemistry"],
        "relevant": ["Agriculture", "Mathematics", "Physics"],
        "desirable": ["Human Biology", "Geography"],
        "minimum_points": 6,
        "minimum_principal_passes": 2,
        "uce_requirement": "UCE with 5 passes including English, Mathematics, Biology and Chemistry at Credit level"
    },
    "business_management": {
        "essential": [],
        "relevant": ["Economics", "Mathematics", "Accounting", "Business Studies", "Entrepreneurship"],
        "desirable": ["English", "Geography", "History", "Government"],
        "minimum_points": 4,
        "minimum_principal_passes": 1,
        "uce_requirement": "UCE with 5 passes including English and Mathematics (Credit level preferred)"
    },
    "social_sciences_humanities": {
        "essential": [],
        "relevant": ["History", "Geography", "Economics", "Literature", "Divinity", "Luganda", "Kiswahili", "French"],
        "desirable": ["English", "Mathematics", "Government", "Christian Religious Education"],
        "minimum_points": 4,
        "minimum_principal_passes": 1,
        "uce_requirement": "UCE with 5 passes including English Language at Credit level"
    },
    "education": {
        "essential": [],
        "relevant": ["Mathematics", "Biology", "Chemistry", "Physics", "History", "Geography", "Literature", "Economics"],
        "desirable": ["English", "Kiswahili", "Luganda", "Christian Religious Education", "Islamic Religious Education"],
        "minimum_points": 4,
        "minimum_principal_passes": 1,
        "uce_requirement": "UCE with 5 passes including English Language; preference for candidates with teaching subjects"
    },
    "law": {
        "essential": [],
        "relevant": ["History", "Literature", "Divinity", "Christian Religious Education", "Economics", "Government"],
        "desirable": ["English", "Kiswahili", "French", "Luganda"],
        "minimum_points": 6,
        "minimum_principal_passes": 2,
        "uce_requirement": "UCE with 5 passes including English Language at Credit level; strong Arts background preferred"
    },
    "computer_science": {
        "essential": ["Mathematics"],
        "relevant": ["Physics", "Computer Studies", "Economics", "Chemistry"],
        "desirable": ["Further Mathematics", "Technical Drawing", "Biology"],
        "minimum_points": 6,
        "minimum_principal_passes": 2,
        "uce_requirement": "UCE with 5 passes including English and Mathematics at Credit level"
    },
    "information_technology": {
        "essential": ["Mathematics"],
        "relevant": ["Physics", "Computer Studies", "Economics", "Chemistry", "Geography"],
        "desirable": ["Further Mathematics", "Technical Drawing", "Biology"],
        "minimum_points": 4,
        "minimum_principal_passes": 1,
        "uce_requirement": "UCE with 5 passes including English and Mathematics at Credit level"
    },
    "cyber_security": {
        "essential": ["Mathematics"],
        "relevant": ["Physics", "Computer Studies", "Economics", "Chemistry"],
        "desirable": ["Further Mathematics", "Technical Drawing", "Biology"],
        "minimum_points": 6,
        "minimum_principal_passes": 2,
        "uce_requirement": "UCE with 5 passes including English and Mathematics at Credit level"
    },
    "pharmacy": {
        "essential": ["Chemistry"],
        "relevant": ["Biology", "Mathematics", "Physics"],
        "desirable": ["Human Biology", "Agriculture", "Food and Nutrition"],
        "minimum_points": 10,
        "minimum_principal_passes": 2,
        "uce_requirement": "UCE with 5 passes including English, Mathematics, Biology and Chemistry at Credit level"
    },
    "dentistry": {
        "essential": ["Biology", "Chemistry"],
        "relevant": ["Mathematics", "Physics"],
        "desirable": ["Human Biology", "Agriculture", "Food and Nutrition"],
        "minimum_points": 10,
        "minimum_principal_passes": 2,
        "uce_requirement": "UCE with 5 passes including English, Mathematics, Biology and Chemistry at Credit level"
    },
    "optometry": {
        "essential": ["Biology", "Physics"],
        "relevant": ["Chemistry", "Mathematics"],
        "desirable": ["Human Biology", "Agriculture", "Food and Nutrition"],
        "minimum_points": 8,
        "minimum_principal_passes": 2,
        "uce_requirement": "UCE with 5 passes including English, Mathematics, Biology and Physics at Credit level"
    }
}

# NCHE Diploma Equivalence Standards (KIU Direct Entry Policy)
# Source: KIU Admission Brochure 2025/2026
NCHE_DIPLOMA_EQUIVALENCE = {
    # HEALTH SCIENCES DIPLOMAS
    "diploma_in_nursing": {
        "equivalent_to": "UACE with 1 Principal Pass in Biology + 2 Subsidiary",
        "points_awarded": 4,  # 1 principal pass
        "principal_passes": 1,
        "entry_requirements": "Certificate in Nursing (Direct Entry) with minimum 50% aggregate",
        "progression": "Diploma in Nursing Year 2 / Bachelor of Nursing Year 2",
        "duration": "2 years after Certificate (3 semesters total)"
    },
    "diploma_in_midwifery": {
        "equivalent_to": "UACE with 1 Principal Pass in Biology + 2 Subsidiary",
        "points_awarded": 4,
        "principal_passes": 1,
        "entry_requirements": "Certificate in Midwifery (Direct Entry) with minimum 50% aggregate",
        "progression": "Diploma in Midwifery Year 2 / Bachelor of Midwifery Year 2",
        "duration": "2 years after Certificate (4 semesters total)"
    },
    "diploma_in_medical_laboratory": {
        "equivalent_to": "UACE with 1 Principal Pass in Biology/Chemistry + 2 Subsidiary",
        "points_awarded": 4,
        "principal_passes": 1,
        "entry_requirements": "Certificate in Medical Laboratory Techniques with minimum 50% aggregate",
        "progression": "Bachelor of Medical Laboratory Sciences Year 3",
        "duration": "2 years after Certificate (4 semesters total)"
    },
    "diploma_in_pharmacy": {
        "equivalent_to": "UACE with 1 Principal Pass in Chemistry + 2 Subsidiary (Biology required)",
        "points_awarded": 5,  # Chemistry principal + Biology subsidiary
        "principal_passes": 1,
        "entry_requirements": "Certificate in Pharmacy with minimum 50% aggregate",
        "progression": "Bachelor of Pharmacy Year 3",
        "duration": "2 years after Certificate (4 semesters total)"
    },
    "diploma_in_clinical_medicine": {
        "equivalent_to": "UACE with 1 Principal Pass in Biology + 2 Subsidiary",
        "points_awarded": 4,
        "principal_passes": 1,
        "entry_requirements": "Certificate in Clinical Medicine with minimum 50% aggregate",
        "progression": "Bachelor of Clinical Medicine and Community Health Year 3",
        "duration": "3 years after Certificate (6 semesters total)"
    },
    "diploma_in_public_health": {
        "equivalent_to": "UACE with 1 Principal Pass in Biology + 2 Subsidiary",
        "points_awarded": 4,
        "principal_passes": 1,
        "entry_requirements": "Certificate in Public Health with minimum 50% aggregate",
        "progression": "Bachelor of Public Health Year 2",
        "duration": "2 years after Certificate (4 semesters total)"
    },
    
    # TECHNICAL & ENGINEERING DIPLOMAS
    "diploma_in_civil_engineering": {
        "equivalent_to": "UACE with 1 Principal in Mathematics/Physics + 2 Subsidiary",
        "points_awarded": 4,
        "principal_passes": 1,
        "entry_requirements": "UCE with 5 credits including Mathematics and Physics",
        "progression": "Bachelor of Civil Engineering Year 2",
        "duration": "2 years after relevant qualification (4 semesters total)"
    },
    "diploma_in_electrical_engineering": {
        "equivalent_to": "UACE with 1 Principal in Mathematics/Physics + 2 Subsidiary",
        "points_awarded": 4,
        "principal_passes": 1,
        "entry_requirements": "UCE with 5 credits including Mathematics and Physics",
        "progression": "Bachelor of Electrical Engineering Year 2",
        "duration": "2 years (4 semesters)"
    },
    "diploma_in_mechanical_engineering": {
        "equivalent_to": "UACE with 1 Principal in Mathematics/Physics + 2 Subsidiary",
        "points_awarded": 4,
        "principal_passes": 1,
        "entry_requirements": "UCE with 5 credits including Mathematics and Physics",
        "progression": "Bachelor of Mechanical Engineering Year 2",
        "duration": "2 years (4 semesters)"
    },
    
    # COMPUTING & IT DIPLOMAS
    "diploma_in_computer_science": {
        "equivalent_to": "UACE with 1 Principal in Mathematics/Physics + 2 Subsidiary",
        "points_awarded": 4,
        "principal_passes": 1,
        "entry_requirements": "UCE with 5 credits including Mathematics and English",
        "progression": "Bachelor of Computer Science Year 2",
        "duration": "2 years (4 semesters)"
    },
    "diploma_in_information_technology": {
        "equivalent_to": "UACE with 1 Principal in Mathematics/Physics + 2 Subsidiary",
        "points_awarded": 4,
        "principal_passes": 1,
        "entry_requirements": "UCE with 5 credits including Mathematics and English",
        "progression": "Bachelor of Information Technology Year 2",
        "duration": "2 years (4 semesters)"
    },
    
    # BUSINESS & MANAGEMENT DIPLOMAS
    "diploma_in_business_administration": {
        "equivalent_to": "UACE with 1 Principal + 2 Subsidiary passes",
        "points_awarded": 4,
        "principal_passes": 1,
        "entry_requirements": "UCE with 5 credits including English and Mathematics",
        "progression": "Bachelor of Business Administration Year 2",
        "duration": "2 years (4 semesters)"
    },
    "diploma_in_accounting_and_finance": {
        "equivalent_to": "UACE with 1 Principal in Economics/Mathematics + 2 Subsidiary",
        "points_awarded": 4,
        "principal_passes": 1,
        "entry_requirements": "UCE with 5 credits including Mathematics and English",
        "progression": "Bachelor of Commerce Year 2",
        "duration": "2 years (4 semesters)"
    },
    "diploma_in_human_resource_management": {
        "equivalent_to": "UACE with 1 Principal + 2 Subsidiary passes",
        "points_awarded": 4,
        "principal_passes": 1,
        "entry_requirements": "UCE with 5 credits including English",
        "progression": "Bachelor of Human Resource Management Year 2",
        "duration": "2 years (4 semesters)"
    }
}

# NCHE Higher Education Certificate (HEC) Equivalence Standards
# HEC is the 4th avenue of admission approved by NCHE
NCHE_HEC_EQUIVALENCE = {
    "hec_arts": {
        "track": "Arts/Humanities",
        "equivalent_to": "UACE with 1 Principal Pass + 2 Subsidiary",
        "points_awarded": 4,
        "principal_passes": 1,
        "recommended_programs": [
            "Law", "Social Work", "Public Administration", "Business Administration",
            "Arts with Education", "Development Studies", "International Relations"
        ],
        "entry_requirements": "UCE with 3 passes, no specific subject requirements",
        "progression": "Direct entry to Year 1 of Arts/Humanities programs",
        "duration": "1 year HEC program, then 3-4 year Bachelor's"
    },
    "hec_physical": {
        "track": "Physical Sciences",
        "equivalent_to": "UACE with 1 Principal in Mathematics/Physics + 2 Subsidiary",
        "points_awarded": 4,
        "principal_passes": 1,
        "recommended_programs": [
            "Computer Science", "Information Technology", "Engineering programs",
            "Mathematics", "Physics", "Chemistry"
        ],
        "entry_requirements": "UCE with passes in Mathematics and any science subject",
        "progression": "Direct entry to Year 1 of Science/Technical programs",
        "duration": "1 year HEC program, then 3-4 year Bachelor's"
    },
    "hec_biological": {
        "track": "Biological Sciences",
        "equivalent_to": "UACE with 1 Principal in Biology + 2 Subsidiary",
        "points_awarded": 4,
        "principal_passes": 1,
        "recommended_programs": [
            "Nursing", "Public Health", "Environmental Health", "Agriculture",
            "Biology", "Medicine", "Pharmacy", "Laboratory Sciences"
        ],
        "entry_requirements": "UCE with passes in Biology and any other science",
        "progression": "Direct entry to Year 1 of Health/Agriculture programs",
        "duration": "1 year HEC program, then 3-5 year Bachelor's"
    }
}

# NCHE National Certificate (Vocational) Equivalence Standards
NCHE_NATIONAL_CERTIFICATE_EQUIVALENCE = {
    "national_certificate_nursing": {
        "field": "Health Sciences",
        "equivalent_to": "UCE with 5 passes including Biology",
        "recommended_programs": ["Diploma in Nursing", "Certificate in Midwifery"],
        "entry_level": "Certificate/Diploma",
        "progression": "Direct entry to Certificate or Diploma programs"
    },
    "national_certificate_medical_lab": {
        "field": "Health Sciences",
        "equivalent_to": "UCE with 5 passes including Biology and Chemistry",
        "recommended_programs": ["Diploma in Medical Laboratory Sciences", "Certificate in Laboratory Techniques"],
        "entry_level": "Certificate/Diploma",
        "progression": "Direct entry to Certificate or Diploma programs"
    },
    "national_certificate_pharmacy": {
        "field": "Health Sciences",
        "equivalent_to": "UCE with 5 passes including Chemistry and Biology",
        "recommended_programs": ["Diploma in Pharmacy", "Certificate in Pharmacy"],
        "entry_level": "Certificate/Diploma",
        "progression": "Direct entry to Certificate or Diploma programs"
    },
    "national_certificate_business": {
        "field": "Business & Management",
        "equivalent_to": "UCE with 5 passes including English and Mathematics",
        "recommended_programs": ["Diploma in Business Administration", "Diploma in Accounting", "Certificate in Business"],
        "entry_level": "Certificate/Diploma",
        "progression": "Direct entry to Certificate or Diploma programs"
    },
    "national_certificate_ict": {
        "field": "Computing & IT",
        "equivalent_to": "UCE with 5 passes including Mathematics",
        "recommended_programs": ["Diploma in Computer Science", "Diploma in IT", "Certificate in IT"],
        "entry_level": "Certificate/Diploma",
        "progression": "Direct entry to Certificate or Diploma programs"
    },
    "national_certificate_education": {
        "field": "Education",
        "equivalent_to": "UCE with 5 passes",
        "recommended_programs": ["Diploma in Education", "Certificate in Education"],
        "entry_level": "Certificate/Diploma",
        "progression": "Direct entry to Certificate or Diploma programs"
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
# NCHE Assessment Functions for Alternative Qualifications
# ---------------------------------------------------------------------------

def assess_hec_eligibility(heq_type: str, programme: Dict) -> Dict:
    """Assess eligibility for HEC (Higher Education Certificate) holders
    
    HEC is NCHE's 4th avenue of admission for applicants who don't meet
    standard UACE requirements but have UCE passes.
    """
    assessment = {
        "eligible": False,
        "reasons": [],
        "hec_track": heq_type,
        "entry_level": "Year 1",
        "meets_nche_minimum": False,
        "points_calculation": {
            "equivalent_to": "UACE with 1 Principal + 2 Subsidiary",
            "points_awarded": 4,
            "principal_passes": 1
        }
    }
    
    if heq_type in NCHE_HEC_EQUIVALENCE:
        hec_data = NCHE_HEC_EQUIVALENCE[heq_type]
        programme_name = programme.get("name", "").lower()
        
        # Check if programme matches HEC track recommendations
        recommended_programs = hec_data.get("recommended_programs", [])
        programme_matches = any(
            prog.lower() in programme_name or programme_name in prog.lower()
            for prog in recommended_programs
        )
        
        if programme_matches:
            assessment["eligible"] = True
            assessment["meets_nche_minimum"] = True
            assessment["reasons"].append(f"HEC {hec_data['track']} qualifies for this programme")
            assessment["entry_level"] = "Year 1 (Direct Entry)"
        elif programme.get("nche_category") in ["arts_humanities", "social_sciences", "business_management"] and heq_type == "hec_arts":
            assessment["eligible"] = True
            assessment["meets_nche_minimum"] = True
            assessment["reasons"].append("HEC Arts track qualifies for Arts/Humanities/Business programmes")
        elif programme.get("nche_category") in ["science_technology", "engineering"] and heq_type == "hec_physical":
            assessment["eligible"] = True
            assessment["meets_nche_minimum"] = True
            assessment["reasons"].append("HEC Physical Sciences track qualifies for Science/Engineering programmes")
        elif programme.get("nche_category") in ["medicine_health_sciences", "agriculture"] and heq_type == "hec_biological":
            assessment["eligible"] = True
            assessment["meets_nche_minimum"] = True
            assessment["reasons"].append("HEC Biological Sciences track qualifies for Health/Agriculture programmes")
        else:
            assessment["reasons"].append(f"HEC {hec_data['track']} may not be ideal for this programme. Consider related programmes.")
            
    return assessment


def assess_national_certificate_eligibility(certificate_type: str, programme: Dict) -> Dict:
    """Assess eligibility for National Certificate (Vocational) holders
    
    National Certificates are 2-year vocational qualifications that
    can lead to Diploma or Certificate programs.
    """
    assessment = {
        "eligible": False,
        "reasons": [],
        "entry_level": None,
        "meets_nche_minimum": False,
        "recommended_entry": None
    }
    
    if certificate_type in NCHE_NATIONAL_CERTIFICATE_EQUIVALENCE:
        cert_data = NCHE_NATIONAL_CERTIFICATE_EQUIVALENCE[certificate_type]
        programme_level = programme.get("nche_accreditation", {}).get("programme_level", "")
        programme_category = programme.get("nche_category", "")
        
        # National Certificates typically qualify for Certificate or Diploma programs
        if programme_level == "Certificate" or programme_level == "Diploma":
            # Check field alignment
            cert_field = cert_data.get("field", "").lower()
            prog_category = programme_category.lower()
            
            if ("health" in cert_field and "health" in prog_category) or \
               ("business" in cert_field and ("business" in prog_category or "commerce" in prog_category)) or \
               ("computing" in cert_field and ("computing" in prog_category or "technology" in prog_category)) or \
               ("education" in cert_field and "education" in prog_category):
                assessment["eligible"] = True
                assessment["meets_nche_minimum"] = True
                assessment["entry_level"] = "Direct Entry"
                assessment["reasons"].append(f"National Certificate in {cert_field} qualifies for this {programme_level} programme")
            else:
                assessment["reasons"].append(f"Consider programmes in {cert_field} for better alignment with your National Certificate")
        elif programme_level == "Undergraduate":
            assessment["reasons"].append("National Certificate holders should apply for Diploma or Certificate programmes first, then progress to Bachelor's")
            assessment["recommended_entry"] = "Diploma (then progress to Bachelor's)"
        else:
            assessment["reasons"].append(f"Entry level {programme_level} may require additional qualifications")
            
    return assessment


def assess_diploma_eligibility(diploma_type: str, diploma_class: str, programme: Dict) -> Dict:
    """Assess eligibility for Diploma holders (Direct Entry to Year 2/3)
    
    Diploma holders with Credit/Distinction can enter Bachelor's programs
    at Year 2 or Year 3 depending on diploma relevance.
    """
    assessment = {
        "eligible": False,
        "reasons": [],
        "entry_level": None,
        "meets_nche_minimum": False,
        "points_calculation": None,
        "progression_year": None
    }
    
    # Check diploma class - minimum Pass (50%) required for direct entry
    if diploma_class.lower() not in ["credit", "distinction", "second class", "2nd class"]:
        assessment["reasons"].append("Diploma class below Credit. Minimum Credit/Distinction required for direct entry to Bachelor's")
        assessment["recommended_entry"] = "Certificate program or repeat Diploma"
        return assessment
    
    if diploma_type in NCHE_DIPLOMA_EQUIVALENCE:
        dip_data = NCHE_DIPLOMA_EQUIVALENCE[diploma_type]
        programme_name = programme.get("name", "").lower()
        
        # Calculate equivalent UACE points
        points_awarded = dip_data.get("points_awarded", 4)
        principal_passes = dip_data.get("principal_passes", 1)
        
        assessment["points_calculation"] = {
            "total_points": points_awarded,
            "principal_passes": principal_passes,
            "equivalent_to": dip_data.get("equivalent_to", "UACE with 1 Principal + 2 Subsidiary"),
            "source": "Diploma equivalence"
        }
        
        # Check if diploma progression matches programme
        progression = dip_data.get("progression", "").lower()
        
        if programme_name in progression or any(word in programme_name for word in progression.split() if len(word) > 3):
            assessment["eligible"] = True
            assessment["meets_nche_minimum"] = True
            assessment["entry_level"] = "Direct Entry"
            
            # Determine entry year based on diploma duration
            duration = dip_data.get("duration", "")
            if "year 3" in progression:
                assessment["progression_year"] = 3
                assessment["reasons"].append(f"Diploma qualifies for Year 3 entry (advanced standing)")
            elif "year 2" in progression:
                assessment["progression_year"] = 2
                assessment["reasons"].append(f"Diploma qualifies for Year 2 entry")
            else:
                assessment["progression_year"] = 1
                assessment["reasons"].append(f"Diploma qualifies for Year 1 entry")
        else:
            assessment["reasons"].append(f"Diploma may not be directly relevant. Consider: {dip_data.get('progression', 'related programmes')}")
            
    return assessment


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
    """NCHE-compliant eligibility assessment with full transparency"""
    assessment = {
        "eligible": False,
        "reasons": [],
        "missing_requirements": [],
        "recommendations": [],
        "meets_nche_minimum": False,
        "transparency": {
            "checked_criteria": [],
            "failed_criteria": [],
            "passed_criteria": [],
            "actionable_steps": [],
            "alternative_pathways": [],
            "meets_minimum_standards": False,
            "meets_programme_requirements": False,
            "meets_quota_requirements": False
        },
        "points_calculation": None,
        "qualification_summary": {}
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
        
        # Populate transparency
        assessment["transparency"]["checked_criteria"].append("essential_subjects")
        if missing_essential:
            assessment["reasons_fail"].append(f"Missing essential NCHE subjects: {', '.join(missing_essential)}")
            assessment["transparency"]["failed_criteria"].append({
                "criterion": "essential_subjects",
                "reason": f"Missing: {', '.join(missing_essential)}"
            })
        else:
            assessment["reasons_pass"].append(f"Meets NCHE essential subjects requirement")
            assessment["transparency"]["passed_criteria"].append({
                "criterion": "essential_subjects",
                "detail": "All essential subjects present"
            })
        
        # Points and principal passes check
        assessment["transparency"]["checked_criteria"].append("minimum_points_requirement")
        if total_points >= nche_req["minimum_points"] and principal_passes >= nche_req["minimum_principal_passes"]:
            assessment["meets_nche_minimum"] = True
            assessment["reasons_pass"].append(f"Meets NCHE minimum: {total_points} points, {principal_passes} principal passes")
            assessment["transparency"]["passed_criteria"].append({
                "criterion": "minimum_points_requirement",
                "detail": f"Points: {total_points}, Principal passes: {principal_passes}"
            })
            assessment["transparency"]["meets_minimum_standards"] = True
        else:
            assessment["reasons_fail"].append(f"Below NCHE minimum: {total_points} < {nche_req['minimum_points']} points or {principal_passes} < {nche_req['minimum_principal_passes']} principal passes")
            assessment["transparency"]["failed_criteria"].append({
                "criterion": "minimum_points_requirement",
                "reason": f"Insufficient points ({total_points}/{nche_req['minimum_points']}) or principal passes ({principal_passes}/{nche_req['minimum_principal_passes']})"
            })
            # Add actionable steps based on UACE performance
            if principal_passes >= 1 and principal_passes < nche_req["minimum_principal_passes"]:
                # Has at least 1 principal but not enough - HEC is a good option
                assessment["transparency"]["actionable_steps"].append("Consider HEC (Higher Education Certificate) program - 1 year pathway to Bachelor's")
            elif principal_passes >= 2 and total_points < nche_req["minimum_points"]:
                # Has 2 principals but low grades - HEC could help upgrade
                assessment["transparency"]["actionable_steps"].append("HEC program may strengthen your profile for competitive programs")
            
            assessment["transparency"]["actionable_steps"].append("Consider upgrading grades in weaker subjects through retakes")
            assessment["transparency"]["actionable_steps"].append("Explore Diploma or National Certificate programs as alternative pathways")
        
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
    
    # HEC Assessment
    if "hec_type" in applicant:
        hec_type = applicant["hec_type"]
        hec_assessment = assess_hec_eligibility(hec_type, programme)
        if hec_assessment["meets_nche_minimum"]:
            assessment["meets_nche_minimum"] = True
            assessment["entry_recommendation"] = hec_assessment["entry_level"]
            assessment["reasons_pass"].extend(hec_assessment["reasons"])
        else:
            assessment["reasons_fail"].extend(hec_assessment["reasons"])
        assessment["hec_assessment"] = hec_assessment
    
    # National Certificate Assessment
    if "national_certificate_type" in applicant:
        cert_type = applicant["national_certificate_type"]
        cert_assessment = assess_national_certificate_eligibility(cert_type, programme)
        if cert_assessment["meets_nche_minimum"]:
            assessment["meets_nche_minimum"] = True
            assessment["entry_recommendation"] = cert_assessment["entry_level"]
            assessment["reasons_pass"].extend(cert_assessment["reasons"])
        else:
            assessment["reasons_fail"].extend(cert_assessment["reasons"])
        assessment["national_certificate_assessment"] = cert_assessment
    
    # Diploma Assessment (enhanced)
    if "diploma_type" in applicant:
        diploma_type = applicant["diploma_type"]
        diploma_class = applicant.get("diploma_class", "")
        diploma_assessment = assess_diploma_eligibility(diploma_type, diploma_class, programme)
        if diploma_assessment["meets_nche_minimum"]:
            assessment["meets_nche_minimum"] = True
            assessment["entry_recommendation"] = diploma_assessment["entry_level"]
            if diploma_assessment["progression_year"]:
                assessment["direct_entry_year"] = diploma_assessment["progression_year"]
            assessment["reasons_pass"].extend(diploma_assessment["reasons"])
        else:
            assessment["reasons_fail"].extend(diploma_assessment["reasons"])
        if diploma_assessment["points_calculation"]:
            assessment["points_calculation"]["diploma_equivalent"] = diploma_assessment["points_calculation"]
            assessment["diploma_assessment"] = diploma_assessment
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
            # Determine qualification type for application link
            qualification = "a_level"
            if applicant.get("diploma_type"):
                qualification = "diploma"
            elif applicant.get("bachelor_gpa"):
                qualification = "degree" if programme.get("nche_category") == "business_management" else "masters"

            recommendation = {
                **programme,
                "nche_assessment": assessment,
                "apply_url": f"/apply/degree?program={programme['id']}&qualification={qualification}&auto=true",
                "direct_application": assessment["eligible"],
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
    
    return success_response({
        "programmes": programmes,
        "nche_categories": list(set(p["nche_category"] for p in KIU_NCHE_PROGRAMMES)),
        "total": len(programmes),
        "filters": {"search": "", "level": "", "category": category}
    })

@recommendations_bp.route("/v1/nche/assess", methods=["POST"])
def nche_admission_assessment():
    """NCHE-compliant admission assessment"""
    try:
        applicant = request.get_json()
        if not applicant:
            return bad_request("Please provide your academic details")
        
        recommendations = get_nche_recommendations(applicant)
        
        return success_response({
            "recommendations": recommendations,
            "total": len(recommendations),
            "nche_assessment_summary": {
                "assessed_at": datetime.now().isoformat(),
                "nche_compliant": True,
                "uganda_curriculum": "Both Old and New (2024+) supported"
            }
        })
        
    except Exception as e:
        log.error(f"Error in NCHE assessment: {e}")
        return bad_request(f"Unable to complete NCHE assessment: {str(e)}")

@recommendations_bp.route("/v1/nche/programme/<programme_id>", methods=["GET"])
def get_nche_programme_details(programme_id):
    """Get detailed NCHE programme information"""
    programme = next((p for p in KIU_NCHE_PROGRAMMES if p["id"] == programme_id), None)
    
    if not programme:
        return not_found("NCHE programme not found")
    
    programme["apply_url"] = f"/apply/{programme_id}"
    
    return success_response(programme)

@recommendations_bp.route("/v1/nche/eligibility-check", methods=["POST"])
def nche_eligibility_check():
    """Quick NCHE eligibility check for a specific programme"""
    try:
        data = request.get_json()
        programme_id = data.get("programme_id")
        applicant = data.get("applicant", {})
        
        if not programme_id:
            return bad_request("Programme ID required", errors={"programme_id": "Required"})
        
        programme = next((p for p in KIU_NCHE_PROGRAMMES if p["id"] == programme_id), None)
        if not programme:
            return not_found("NCHE programme not found")
        
        assessment = assess_nche_eligibility(programme, applicant)
        
        return success_response({
            "programme": {
                "id": programme["id"],
                "name": programme["name"],
                "nche_accredited": programme["nche_accredited"],
                "nche_category": programme["nche_category"]
            },
            "assessment": assessment,
            "eligible": assessment["eligible"],
            "next_steps": assessment.get("next_steps", [])
        })
        
    except Exception as e:
        log.error(f"Error in NCHE eligibility check: {e}")
        return bad_request(f"Unable to check NCHE eligibility: {str(e)}")

@recommendations_bp.route("/v1/nche/standards", methods=["GET"])
def get_nche_standards():
    """Get NCHE Uganda admission standards"""
    return success_response({
        "nche_uace_grading": NCHE_UACE_GRADE_POINTS,
        "nche_uce_grading": NCHE_UCE_DIVISION_POINTS,
        "nche_subject_combinations": NCHE_SUBJECT_COMBINATIONS,
        "nche_diploma_equivalence": NCHE_DIPLOMA_EQUIVALENCE,
        "nche_minimum_standards": "All programmes meet NCHE Uganda minimum requirements"
    })
