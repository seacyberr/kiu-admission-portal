"""
KIU Actual Programs Database - 2025/2026 Tuition Fees
===============================================

SOURCES (Official KIU Documents):
1. "Local Main Campus Brochure August 2025" - UGX fees for local students
2. "International Main Campus Brochure January 2025" - USD fees for international students  
3. KIU Internal Database (seed-programs.json) - Program codes and structure

FEE STRUCTURE:
- All fees are PER SEMESTER unless noted "PAID ONCE"
- Functional fees are ADDITIONAL to tuition fees
- Application Fee (PAID ONCE): 50,000 UGX / 25 USD

FUNCTIONAL FEES (Per Semester):
- Health Science Degree Programs: 700,000 UGX / 425 USD
- Health Sciences Diploma Programs: 550,000 UGX / 350 USD
- Health Science Certificate Programs: 217,000 UGX / 217 USD
- Arts, Science & Technology Programs: 353,000 UGX / 353 USD
- Higher Education Certificate (HEC): 0 UGX / 200 USD
- Masters Programs: 500,000 UGX / 150 USD
- Postgraduate Diplomas: 500,000 UGX / 150 USD

RESEARCH FEES (PAID ONCE):
- Masters Research Fee: 500 USD
- PhD Research Fee: 650 USD

CAMPUSES:
- Main Campus (Kampala): Kansanga, Kampala
- Western Campus (Ishaka): Bushenyi District (Health Sciences)

LAST UPDATED: April 2026
VERIFIED: Yes - Against official KIU fee brochures
"""

# PROGRAM LISTS BY LEVEL
# ======================

# CERTIFICATE PROGRAMS (Entry level for O-Level holders)
CERTIFICATE_PROGRAMS = [
    "Certificate in Nursing",
    "Certificate in Midwifery",
    "Certificate in Medical Laboratory",
    "Certificate in Pharmacy",
    "Certificate in Clinical Medicine",
    "Certificate in Public Health",
    "Certificate in Business Administration",
    "Certificate in Information Technology",
    "Certificate in Education",
    "Certificate in Agriculture",
    "Certificate in Hotel Management",
    "Certificate in Tourism",
]

# DIPLOMA PROGRAMS (For O-Level + 2 passes or Certificate holders)
DIPLOMA_PROGRAMS = [
    # Health Sciences
    "Diploma in Nursing",
    "Diploma in Midwifery",
    "Diploma in Medical Laboratory",
    "Diploma in Pharmacy",
    "Diploma in Clinical Medicine",
    "Diploma in Public Health",
    "Diploma in Environmental Health",
    "Diploma in Dental Surgery",
    "Diploma in Orthopedics",
    "Diploma in Optometry",
    # Business & Management
    "Diploma in Business Administration",
    "Diploma in Accounting",
    "Diploma in Finance",
    "Diploma in Marketing",
    "Diploma in Human Resource Management",
    "Diploma in Procurement",
    "Diploma in Logistics",
    # ICT & Computing
    "Diploma in Computer Science",
    "Diploma in Information Technology",
    "Diploma in Software Engineering",
    "Diploma in Networking",
    "Diploma in Cyber Security",
    # Education
    "Diploma in Education (Primary)",
    "Diploma in Education (Secondary)",
    "Diploma in Early Childhood Education",
    "Diploma in Special Needs Education",
    # Law & Social Sciences
    "Diploma in Law",
    "Diploma in Social Work",
    "Diploma in Counseling",
    # Engineering & Technical
    "Diploma in Civil Engineering",
    "Diploma in Electrical Engineering",
    "Diploma in Mechanical Engineering",
    "Diploma in Automotive Engineering",
    # Agriculture & Environment
    "Diploma in Agriculture",
    "Diploma in Forestry",
    "Diploma in Fisheries",
    "Diploma in Animal Production",
    # Journalism & Media
    "Diploma in Journalism",
    "Diploma in Mass Communication",
    "Diploma in Public Relations",
    # Hospitality & Tourism
    "Diploma in Hotel Management",
    "Diploma in Tourism",
    "Diploma in Catering",
]

# HEC (Higher Education Certificate) PROGRAMS
# Foundation year for A-Level holders who don't qualify for direct degree
HEC_PROGRAMS = [
    "HEC - Sciences Track (Biological Sciences)",
    "HEC - Sciences Track (Physical Sciences)",
    "HEC - Arts Track (Humanities)",
    "HEC - Arts Track (Social Sciences)",
    "HEC - Business Track",
    "HEC - Education Track",
    "HEC - Engineering Track",
    "HEC - Health Sciences Track",
]

# BACHELOR'S DEGREE PROGRAMS
BACHELOR_PROGRAMS = [
    # Medicine & Health Sciences (Western Campus)
    "Bachelor of Medicine and Bachelor of Surgery (MBChB)",
    "Bachelor of Dental Surgery (BDS)",
    "Bachelor of Pharmacy (BPharm)",
    "Bachelor of Nursing Sciences",
    "Bachelor of Medical Laboratory Sciences",
    "Bachelor of Public Health",
    "Bachelor of Environmental Health",
    "Bachelor of Clinical Medicine",
    "Bachelor of Optometry",
    "Bachelor of Physiotherapy",
    "Bachelor of Radiology",
    "Bachelor of Anesthesia",
    # Business & Management
    "Bachelor of Business Administration (BBA)",
    "Bachelor of Commerce (B.Com)",
    "Bachelor of Accounting and Finance",
    "Bachelor of Procurement and Logistics",
    "Bachelor of Human Resource Management",
    "Bachelor of Marketing",
    "Bachelor of Entrepreneurship",
    "Bachelor of International Business",
    # Computing & ICT
    "Bachelor of Computer Science",
    "Bachelor of Information Technology",
    "Bachelor of Software Engineering",
    "Bachelor of Computer Engineering",
    "Bachelor of Data Science",
    "Bachelor of Artificial Intelligence",
    "Bachelor of Cyber Security",
    # Education
    "Bachelor of Education (Arts)",
    "Bachelor of Education (Science)",
    "Bachelor of Education (Primary)",
    "Bachelor of Education (Early Childhood)",
    "Bachelor of Education (Special Needs)",
    "Bachelor of Education (Business)",
    # Law & Social Sciences
    "Bachelor of Laws (LLB)",
    "Bachelor of Social Work",
    "Bachelor of Counseling",
    "Bachelor of Public Administration",
    "Bachelor of Governance and Ethics",
    "Bachelor of International Relations",
    # Engineering
    "Bachelor of Civil Engineering",
    "Bachelor of Electrical Engineering",
    "Bachelor of Mechanical Engineering",
    "Bachelor of Telecommunications Engineering",
    "Bachelor of Biomedical Engineering",
    # Agriculture & Environment
    "Bachelor of Agriculture",
    "Bachelor of Agricultural Economics",
    "Bachelor of Animal Production",
    "Bachelor of Crop Science",
    "Bachelor of Forestry",
    "Bachelor of Fisheries",
    "Bachelor of Environmental Science",
    "Bachelor of Natural Resources Management",
    # Arts & Humanities
    "Bachelor of Arts in Economics",
    "Bachelor of Arts in Geography",
    "Bachelor of Arts in History",
    "Bachelor of Arts in Political Science",
    "Bachelor of Arts in Sociology",
    "Bachelor of Arts in Psychology",
    "Bachelor of Arts in Philosophy",
    "Bachelor of Arts in Literature",
    "Bachelor of Arts in Languages",
    # Journalism & Media
    "Bachelor of Journalism and Media",
    "Bachelor of Mass Communication",
    "Bachelor of Public Relations",
    # Hospitality & Tourism
    "Bachelor of Hotel Management",
    "Bachelor of Tourism",
    "Bachelor of Catering",
    # Sciences
    "Bachelor of Science in Biology",
    "Bachelor of Science in Chemistry",
    "Bachelor of Science in Physics",
    "Bachelor of Science in Mathematics",
    "Bachelor of Science in Statistics",
    # Development Studies
    "Bachelor of Development Studies",
    "Bachelor of Community Development",
]

# MASTERS DEGREE PROGRAMS
MASTERS_PROGRAMS = [
    # Business & Management
    "Master of Business Administration (MBA)",
    "Master of Commerce (M.Com)",
    "Master of Accounting",
    "Master of Finance",
    "Master of Marketing",
    "Master of Human Resource Management",
    "Master of Procurement",
    # Education
    "Master of Education (M.Ed)",
    "Master of Arts in Education",
    "Master of Science in Education",
    # Public Health
    "Master of Public Health (MPH)",
    "Master of Health Administration",
    "Master of Epidemiology",
    "Master of Biostatistics",
    # Health Sciences
    "Master of Nursing",
    "Master of Midwifery",
    "Master of Medical Laboratory Sciences",
    "Master of Clinical Medicine",
    # Computing
    "Master of Computer Science",
    "Master of Information Technology",
    "Master of Data Science",
    "Master of Software Engineering",
    # Social Sciences
    "Master of Social Work",
    "Master of Public Administration",
    "Master of Development Studies",
    "Master of International Relations",
    # Agriculture
    "Master of Agriculture",
    "Master of Agricultural Economics",
    "Master of Animal Science",
    "Master of Crop Science",
    # Law
    "Master of Laws (LLM)",
    # Engineering
    "Master of Engineering",
    # General
    "Master of Arts (MA)",
    "Master of Science (MSc)",
]

# PhD / DOCTORATE PROGRAMS
PHD_PROGRAMS = [
    # Business
    "Doctor of Philosophy (PhD) in Business Administration",
    "PhD in Management",
    "PhD in Finance",
    "PhD in Marketing",
    # Education
    "PhD in Education",
    "PhD in Educational Administration",
    "PhD in Curriculum Studies",
    # Health
    "PhD in Public Health",
    "PhD in Health Sciences",
    "PhD in Nursing",
    # Social Sciences
    "PhD in Development Studies",
    "PhD in Social Work",
    "PhD in International Relations",
    # Agriculture
    "PhD in Agriculture",
    "PhD in Agricultural Economics",
    # Computing
    "PhD in Computer Science",
    "PhD in Information Technology",
    # General
    "PhD in Arts",
    "PhD in Science",
]

# FEE CALCULATION HELPERS
def get_functional_fee(program_level: str, program_category: str, is_international: bool = False) -> int:
    """
    Get functional fee based on program level and category
    
    Args:
        program_level: "certificate", "diploma", "bachelor", "masters", "phd", "hec"
        program_category: "health", "business", "computing", "education", "law", "engineering"
        is_international: True for USD fees, False for UGX
    
    Returns:
        Functional fee amount in UGX or USD
    """
    if is_international:
        # USD functional fees
        fees = {
            "health": {"bachelor": 425, "diploma": 350, "certificate": 217, "masters": 150, "phd": 150},
            "other": {"bachelor": 353, "diploma": 353, "certificate": 217, "masters": 150, "phd": 150, "hec": 200}
        }
    else:
        # UGX functional fees
        fees = {
            "health": {"bachelor": 700_000, "diploma": 550_000, "certificate": 217_000, "masters": 500_000, "phd": 500_000},
            "other": {"bachelor": 353_000, "diploma": 353_000, "certificate": 217_000, "masters": 500_000, "phd": 500_000, "hec": 0}
        }
    
    category = "health" if program_category == "health" else "other"
    return fees[category].get(program_level, fees["other"].get(program_level, 0))


# KIU Programs with verified 2025/2026 tuition fees from official brochures

KIU_PROGRAMS_DB = {
    # HEALTH SCIENCES - Western Campus (Ishaka)
    # Source: Local Main Campus Brochure August 2025, International Brochure Jan 2025
    # Note: Health Sciences have higher functional fees (700k UGX / 425 USD per sem)
    
    "MBChB": {
        "name": "Bachelor of Medicine and Bachelor of Surgery",
        "faculty": "Faculty of Health Sciences",
        "campus": ["western"],
        "duration": 5,
        "duration_note": "5.5 years (11 semesters)",
        "tuition_ugx": 7_085_000,
        "tuition_usd": 3_445,
        "functional_fee_ugx": 700_000,
        "functional_fee_usd": 425,
        "total_per_sem_ugx": 7_785_000,
        "total_per_sem_usd": 3_870,
        "level": "bachelor",
        "program_category": "health",
        "requirements": {
            "essential": ["Biology", "Chemistry"],
            "relevant": ["Physics", "Mathematics"],
            "minimum_points": 15,
            "min_principal_passes": 2
        },
        "career_paths": ["Medical Officer", "Surgeon", "Specialist"],
        "source": "KIU Fee Brochure Aug 2025"
    },
    "BPharm": {
        "name": "Bachelor of Pharmacy",
        "faculty": "Faculty of Health Sciences",
        "campus": ["western"],
        "duration": 5,
        "tuition_ugx": 4_160_000,
        "tuition_usd": 2_535,
        "functional_fee_ugx": 700_000,
        "functional_fee_usd": 425,
        "total_per_sem_ugx": 4_860_000,
        "total_per_sem_usd": 2_960,
        "level": "bachelor",
        "program_category": "health",
        "requirements": {
            "essential": ["Chemistry", "Biology"],
            "relevant": ["Physics", "Mathematics"],
            "minimum_points": 12,
            "min_principal_passes": 2
        },
        "career_paths": ["Pharmacist", "Clinical Pharmacist", "Drug Inspector"],
        "source": "KIU Fee Brochure Aug 2025"
    },
    "BDS-DENT": {
        "name": "Bachelor of Dental Surgery",
        "faculty": "Faculty of Health Sciences",
        "campus": ["western"],
        "duration": 5,
        "duration_note": "5.5 years (11 semesters)",
        "tuition_ugx": 7_085_000,
        "tuition_usd": 3_445,
        "functional_fee_ugx": 700_000,
        "functional_fee_usd": 425,
        "total_per_sem_ugx": 7_785_000,
        "total_per_sem_usd": 3_870,
        "level": "bachelor",
        "program_category": "health",
        "requirements": {
            "essential": ["Chemistry", "Biology"],
            "relevant": ["Physics"],
            "minimum_points": 13,
            "min_principal_passes": 2
        },
        "career_paths": ["Dentist", "Oral Surgeon", "Dental Specialist"],
        "source": "KIU Fee Brochure Aug 2025"
    },
    "BNS-DIRECT": {
        "name": "Bachelor of Nursing Sciences (Direct Entry)",
        "faculty": "Faculty of Health Sciences",
        "campus": ["western"],
        "duration": 4,
        "tuition_ugx": 2_000_000,
        "level": "bachelor",
        "requirements": {
            "essential": ["Biology"],
            "relevant": ["Chemistry", "Physics"],
            "minimum_points": 10,
            "min_principal_passes": 2
        },
        "career_paths": ["Registered Nurse", "Nurse Practitioner", "Nursing Manager"]
    },
    "BNS-EXT": {
        "name": "Bachelor of Nursing Sciences (Extension)",
        "faculty": "Faculty of Health Sciences",
        "campus": ["western"],
        "duration": 2,
        "tuition_ugx": 1_500_000,
        "level": "bachelor",
        "entry_type": "diploma_entry",
        "requirements": {
            "diploma_required": True,
            "diploma_field": "Nursing"
        },
        "career_paths": ["Registered Nurse", "Nursing Manager"]
    },
    "BCMCH-DIRECT": {
        "name": "Bachelor of Clinical Medicine and Community Health (Direct)",
        "faculty": "Faculty of Health Sciences",
        "campus": ["western"],
        "duration": 4,
        "tuition_ugx": 2_200_000,
        "level": "bachelor",
        "requirements": {
            "essential": ["Biology", "Chemistry"],
            "minimum_points": 12,
            "min_principal_passes": 2
        },
        "career_paths": ["Clinical Officer", "Medical Officer"]
    },
    "BCMCH-EXT": {
        "name": "Bachelor of Clinical Medicine and Community Health (Extension)",
        "faculty": "Faculty of Health Sciences",
        "campus": ["western"],
        "duration": 3,
        "tuition_ugx": 1_800_000,
        "level": "bachelor",
        "entry_type": "diploma_entry",
        "requirements": {
            "diploma_required": True,
            "diploma_field": "Clinical Medicine"
        },
        "career_paths": ["Clinical Officer"]
    },
    "BMLS-DIRECT": {
        "name": "Bachelor of Medical Laboratory Science (Direct)",
        "faculty": "Faculty of Health Sciences",
        "campus": ["western"],
        "duration": 4,
        "tuition_ugx": 2_000_000,
        "level": "bachelor",
        "requirements": {
            "essential": ["Biology", "Chemistry"],
            "minimum_points": 12,
            "min_principal_passes": 2
        },
        "career_paths": ["Medical Lab Scientist", "Lab Manager"]
    },
    "BMLS-EXT": {
        "name": "Bachelor of Medical Laboratory Science (Extension)",
        "faculty": "Faculty of Health Sciences",
        "campus": ["western"],
        "duration": 3,
        "tuition_ugx": 1_600_000,
        "level": "bachelor",
        "entry_type": "diploma_entry",
        "requirements": {
            "diploma_required": True,
            "diploma_field": "Medical Laboratory Science"
        },
        "career_paths": ["Medical Lab Scientist"]
    },
    "BPH": {
        "name": "Bachelor of Public Health",
        "faculty": "Faculty of Health Sciences",
        "campus": ["western"],
        "duration": 3,
        "tuition_ugx": 1_800_000,
        "level": "bachelor",
        "requirements": {
            "essential": ["Biology"],
            "relevant": ["Chemistry", "Physics", "Mathematics", "Geography"],
            "minimum_points": 8,
            "min_principal_passes": 2
        },
        "career_paths": ["Public Health Officer", "Epidemiologist", "Health Educator"]
    },

    # BASIC SCIENCES - Western Campus
    "BSc-ANAT": {
        "name": "Bachelor of Science in Anatomy",
        "faculty": "Faculty of Health Sciences",
        "campus": ["western"],
        "duration": 3,
        "tuition_ugx": 1_500_000,
        "level": "bachelor",
        "requirements": {
            "essential": ["Biology", "Chemistry"],
            "minimum_points": 10,
            "min_principal_passes": 2
        },
        "career_paths": ["Anatomist", "Researcher", "Medical Educator"]
    },
    "BSc-BIOCHEM": {
        "name": "Bachelor of Science in Biochemistry",
        "faculty": "Faculty of Health Sciences",
        "campus": ["western"],
        "duration": 3,
        "tuition_ugx": 1_500_000,
        "level": "bachelor",
        "requirements": {
            "essential": ["Chemistry", "Biology"],
            "minimum_points": 10,
            "min_principal_passes": 2
        },
        "career_paths": ["Biochemist", "Research Scientist", "Lab Manager"]
    },
    "BSc-PHYSIO": {
        "name": "Bachelor of Science in Physiology",
        "faculty": "Faculty of Health Sciences",
        "campus": ["western"],
        "duration": 3,
        "tuition_ugx": 1_500_000,
        "level": "bachelor",
        "requirements": {
            "essential": ["Biology", "Chemistry"],
            "minimum_points": 10,
            "min_principal_passes": 2
        },
        "career_paths": ["Physiologist", "Researcher", "Medical Educator"]
    },
    "BSc-MICRO": {
        "name": "Bachelor of Science in Microbiology",
        "faculty": "Faculty of Health Sciences",
        "campus": ["western"],
        "duration": 3,
        "tuition_ugx": 1_500_000,
        "level": "bachelor",
        "requirements": {
            "essential": ["Biology", "Chemistry"],
            "minimum_points": 10,
            "min_principal_passes": 2
        },
        "career_paths": ["Microbiologist", "Lab Scientist", "Researcher"]
    },
    "BSc-PHARM": {
        "name": "Bachelor of Science in Pharmacology",
        "faculty": "Faculty of Health Sciences",
        "campus": ["western"],
        "duration": 3,
        "tuition_ugx": 1_500_000,
        "level": "bachelor",
        "requirements": {
            "essential": ["Chemistry", "Biology"],
            "minimum_points": 10,
            "min_principal_passes": 2
        },
        "career_paths": ["Pharmacologist", "Researcher", "Drug Developer"]
    },
    "BSc-MRIT": {
        "name": "Bachelor of Science in Medical Radiography and Imaging Technology",
        "faculty": "Faculty of Health Sciences",
        "campus": ["western"],
        "duration": 4,
        "tuition_ugx": 2_000_000,
        "level": "bachelor",
        "requirements": {
            "essential": ["Physics", "Biology"],
            "relevant": ["Chemistry"],
            "minimum_points": 12,
            "min_principal_passes": 2
        },
        "career_paths": ["Radiographer", "Medical Imaging Specialist", "MRI Technician"]
    },
    "BSc-PHT": {
        "name": "Bachelor of Science in Physiotherapy",
        "faculty": "Faculty of Health Sciences",
        "campus": ["western"],
        "duration": 4,
        "tuition_ugx": 2_000_000,
        "level": "bachelor",
        "requirements": {
            "essential": ["Biology"],
            "relevant": ["Physics", "Chemistry"],
            "minimum_points": 12,
            "min_principal_passes": 2
        },
        "career_paths": ["Physiotherapist", "Sports Therapist", "Rehabilitation Specialist"]
    },

    # SCIENCE AND TECHNOLOGY - Main Campus (Kampala)
    "BSc-MATH": {
        "name": "Bachelor of Science in Mathematics",
        "faculty": "Faculty of Science and Technology",
        "campus": ["kampala"],
        "duration": 3,
        "tuition_ugx": 1_300_000,
        "level": "bachelor",
        "requirements": {
            "essential": ["Mathematics"],
            "minimum_points": 8,
            "min_principal_passes": 2
        },
        "career_paths": ["Mathematician", "Data Analyst", "Actuary", "Teacher"]
    },
    "BSc-STAT": {
        "name": "Bachelor of Science in Statistics",
        "faculty": "Faculty of Science and Technology",
        "campus": ["kampala"],
        "duration": 3,
        "tuition_ugx": 1_300_000,
        "level": "bachelor",
        "requirements": {
            "essential": ["Mathematics"],
            "minimum_points": 8,
            "min_principal_passes": 2
        },
        "career_paths": ["Statistician", "Data Scientist", "Research Analyst"]
    },
    "BSc-ENVM": {
        "name": "Bachelor of Science in Environmental Management",
        "faculty": "Faculty of Science and Technology",
        "campus": ["kampala"],
        "duration": 3,
        "tuition_ugx": 1_300_000,
        "level": "bachelor",
        "requirements": {
            "essential": ["Biology", "Chemistry"],
            "minimum_points": 10,
            "min_principal_passes": 2
        },
        "career_paths": ["Environmental Officer", "Conservationist", "Environmental Consultant"]
    },
    "BSc-WMCM": {
        "name": "Bachelor of Science in Wildlife Management and Conservation",
        "faculty": "Faculty of Science and Technology",
        "campus": ["kampala"],
        "duration": 3,
        "tuition_ugx": 1_300_000,
        "level": "bachelor",
        "requirements": {
            "essential": ["Biology"],
            "relevant": ["Chemistry", "Geography"],
            "minimum_points": 10,
            "min_principal_passes": 2
        },
        "career_paths": ["Wildlife Manager", "Conservation Officer", "Park Warden"]
    },
    "BSc-IC": {
        "name": "Bachelor of Science in Industrial Chemistry",
        "faculty": "Faculty of Science and Technology",
        "campus": ["kampala"],
        "duration": 3,
        "tuition_ugx": 1_300_000,
        "level": "bachelor",
        "requirements": {
            "essential": ["Chemistry", "Mathematics"],
            "minimum_points": 10,
            "min_principal_passes": 2
        },
        "career_paths": ["Industrial Chemist", "Quality Control Officer", "Chemical Engineer"]
    },

    # EDUCATION - Main Campus
    "BAED": {
        "name": "Bachelor of Arts with Education",
        "faculty": "Faculty of Education",
        "campus": ["kampala"],
        "duration": 3,
        "tuition_ugx": 1_100_000,
        "level": "bachelor",
        "requirements": {
            "relevant": ["Any two teaching subjects"],
            "minimum_points": 8,
            "min_principal_passes": 2
        },
        "career_paths": ["Secondary Teacher", "Education Administrator"]
    },
    "BSED": {
        "name": "Bachelor of Science with Education",
        "faculty": "Faculty of Education",
        "campus": ["kampala"],
        "duration": 3,
        "tuition_ugx": 1_200_000,
        "level": "bachelor",
        "requirements": {
            "relevant": ["Any two science teaching subjects"],
            "minimum_points": 8,
            "min_principal_passes": 2
        },
        "career_paths": ["Science Teacher", "Education Administrator"]
    },
    "BEd-SNE": {
        "name": "Bachelor of Education in Special Needs Education",
        "faculty": "Faculty of Education",
        "campus": ["kampala"],
        "duration": 3,
        "tuition_ugx": 1_100_000,
        "level": "bachelor",
        "requirements": {
            "minimum_points": 8,
            "min_principal_passes": 2
        },
        "career_paths": ["Special Needs Teacher", "Inclusive Education Specialist"]
    },

    # BUSINESS AND MANAGEMENT - Main Campus
    "BBA": {
        "name": "Bachelor of Business Administration",
        "faculty": "School of Business and Management",
        "campus": ["kampala"],
        "duration": 3,
        "tuition_ugx": 1_435_830,
        "level": "bachelor",
        "requirements": {
            "relevant": ["Economics", "Mathematics", "Business Studies"],
            "minimum_points": 8,
            "min_principal_passes": 2
        },
        "specializations": ["Finance & Banking", "Accounting & Finance", "Marketing"],
        "career_paths": ["Business Manager", "Marketing Manager", "Operations Manager"]
    },
    "BBA-EVENING": {
        "name": "Bachelor of Business Administration (Evening)",
        "faculty": "School of Business and Management",
        "campus": ["kampala"],
        "duration": 4,
        "tuition_ugx": 1_236_867,
        "level": "bachelor",
        "study_mode": "evening",
        "requirements": {
            "minimum_points": 8,
            "min_principal_passes": 2
        },
        "career_paths": ["Business Manager"]
    },
    "BEM": {
        "name": "Bachelor of Entrepreneurship & Business Management",
        "faculty": "School of Business and Management",
        "campus": ["kampala"],
        "duration": 3,
        "tuition_ugx": 1_435_830,
        "level": "bachelor",
        "requirements": {
            "minimum_points": 8,
            "min_principal_passes": 2
        },
        "career_paths": ["Entrepreneur", "Business Owner", "Startup Founder"]
    },
    "BSc-FIN": {
        "name": "Bachelor of Science in Finance",
        "faculty": "School of Business and Management",
        "campus": ["kampala"],
        "duration": 3,
        "tuition_ugx": 1_435_830,
        "level": "bachelor",
        "requirements": {
            "essential": ["Mathematics"],
            "minimum_points": 8,
            "min_principal_passes": 2
        },
        "career_paths": ["Financial Analyst", "Investment Banker", "Financial Manager"]
    },
    "BSc-BANK": {
        "name": "Bachelor of Science in Banking",
        "faculty": "School of Business and Management",
        "campus": ["kampala"],
        "duration": 3,
        "tuition_ugx": 1_718_200,
        "level": "bachelor",
        "requirements": {
            "minimum_points": 8,
            "min_principal_passes": 2
        },
        "career_paths": ["Banker", "Loan Officer", "Bank Manager"]
    },
    "BBC": {
        "name": "Bachelor of Business Computing",
        "faculty": "School of Business and Management",
        "campus": ["kampala"],
        "duration": 3,
        "tuition_ugx": 1_718_200,
        "level": "bachelor",
        "requirements": {
            "minimum_points": 8,
            "min_principal_passes": 2
        },
        "career_paths": ["IT Business Analyst", "Systems Analyst"]
    },
    "BEAS": {
        "name": "Bachelor of Economics and Applied Statistics",
        "faculty": "School of Business and Management",
        "campus": ["kampala"],
        "duration": 3,
        "tuition_ugx": 1_718_200,
        "level": "bachelor",
        "requirements": {
            "essential": ["Mathematics", "Economics"],
            "minimum_points": 10,
            "min_principal_passes": 2
        },
        "career_paths": ["Economist", "Statistician", "Policy Analyst"]
    },
    "BA-ECON": {
        "name": "Bachelor of Arts in Economics",
        "faculty": "School of Business and Management",
        "campus": ["kampala"],
        "duration": 3,
        "tuition_ugx": 1_435_830,
        "level": "bachelor",
        "requirements": {
            "relevant": ["Economics", "Mathematics"],
            "minimum_points": 8,
            "min_principal_passes": 2
        },
        "career_paths": ["Economist", "Policy Analyst"]
    },
    "BSc-TOUR": {
        "name": "Bachelor of Science in Tourism Management",
        "faculty": "School of Business and Management",
        "campus": ["kampala"],
        "duration": 3,
        "tuition_ugx": 1_435_830,
        "level": "bachelor",
        "requirements": {
            "minimum_points": 8,
            "min_principal_passes": 2
        },
        "career_paths": ["Tourism Manager", "Hotel Manager", "Tour Operator"]
    },
    "BHRM": {
        "name": "Bachelor of Human Resource Management",
        "faculty": "School of Business and Management",
        "campus": ["kampala"],
        "duration": 3,
        "tuition_ugx": 1_435_830,
        "level": "bachelor",
        "requirements": {
            "minimum_points": 8,
            "min_principal_passes": 2
        },
        "career_paths": ["HR Manager", "Recruitment Specialist", "Training Coordinator"]
    },
    "BHRM-EVENING": {
        "name": "Bachelor of Human Resource Management (Evening)",
        "faculty": "School of Business and Management",
        "campus": ["kampala"],
        "duration": 4,
        "tuition_ugx": 1_236_867,
        "level": "bachelor",
        "study_mode": "evening",
        "requirements": {
            "minimum_points": 8,
            "min_principal_passes": 2
        },
        "career_paths": ["HR Manager"]
    },
    "BPLM": {
        "name": "Bachelor of Procurement and Logistics Management",
        "faculty": "School of Business and Management",
        "campus": ["kampala"],
        "duration": 3,
        "tuition_ugx": 1_435_830,
        "level": "bachelor",
        "requirements": {
            "minimum_points": 8,
            "min_principal_passes": 2
        },
        "career_paths": ["Procurement Officer", "Supply Chain Manager", "Logistics Coordinator"]
    },
    "BPLM-EVENING": {
        "name": "Bachelor of Procurement and Logistics Management (Evening)",
        "faculty": "School of Business and Management",
        "campus": ["kampala"],
        "duration": 4,
        "tuition_ugx": 1_236_867,
        "level": "bachelor",
        "study_mode": "evening",
        "requirements": {
            "minimum_points": 8,
            "min_principal_passes": 2
        },
        "career_paths": ["Procurement Manager"]
    },
    "BIB": {
        "name": "Bachelor of International Business",
        "faculty": "School of Business and Management",
        "campus": ["kampala"],
        "duration": 3,
        "tuition_ugx": 1_435_830,
        "level": "bachelor",
        "requirements": {
            "minimum_points": 8,
            "min_principal_passes": 2
        },
        "career_paths": ["International Business Manager", "Export Manager", "Trade Consultant"]
    },
    "BCOM-BA-EVENING": {
        "name": "Bachelor of Commerce, Business Administration (Evening)",
        "faculty": "School of Business and Management",
        "campus": ["kampala"],
        "duration": 4,
        "tuition_ugx": 1_236_867,
        "level": "bachelor",
        "study_mode": "evening",
        "requirements": {
            "minimum_points": 8,
            "min_principal_passes": 2
        },
        "career_paths": ["Business Administrator"]
    },

    # COMPUTING AND IT - Main Campus
    "BCS": {
        "name": "Bachelor of Computer Science",
        "faculty": "School of Computing and Information Technology",
        "campus": ["kampala"],
        "duration": 3,
        "tuition_ugx": 2_048_000,
        "level": "bachelor",
        "requirements": {
            "essential": ["Mathematics"],
            "relevant": ["Physics", "Computer Studies"],
            "minimum_points": 10,
            "min_principal_passes": 2
        },
        "career_paths": ["Software Developer", "Systems Analyst", "Computer Scientist"]
    },
    "BIT": {
        "name": "Bachelor of Information Technology",
        "faculty": "School of Computing and Information Technology",
        "campus": ["kampala"],
        "duration": 3,
        "tuition_ugx": 2_048_000,
        "level": "bachelor",
        "requirements": {
            "essential": ["Mathematics"],
            "relevant": ["Computer Studies", "Physics"],
            "minimum_points": 8,
            "min_principal_passes": 1
        },
        "career_paths": ["IT Manager", "Network Administrator", "Database Administrator"]
    },
    "BLIS": {
        "name": "Bachelor of Library and Information Science",
        "faculty": "School of Computing and Information Technology",
        "campus": ["kampala"],
        "duration": 3,
        "tuition_ugx": 2_048_000,
        "level": "bachelor",
        "requirements": {
            "minimum_points": 8,
            "min_principal_passes": 2
        },
        "career_paths": ["Librarian", "Information Manager", "Knowledge Manager"]
    },
    "BSc-CDAG": {
        "name": "Bachelor of Science in Computer Design Art and Graphics",
        "faculty": "School of Computing and Information Technology",
        "campus": ["kampala"],
        "duration": 3,
        "tuition_ugx": 2_048_000,
        "level": "bachelor",
        "requirements": {
            "minimum_points": 8,
            "min_principal_passes": 2
        },
        "career_paths": ["Graphic Designer", "UI/UX Designer", "Creative Director"]
    },
    "BSc-DMA": {
        "name": "Bachelor of Science in Digital Media and Animation",
        "faculty": "School of Computing and Information Technology",
        "campus": ["kampala"],
        "duration": 3,
        "tuition_ugx": 2_048_000,
        "level": "bachelor",
        "requirements": {
            "minimum_points": 8,
            "min_principal_passes": 2
        },
        "career_paths": ["Animator", "Digital Media Producer", "Game Developer"]
    },
    "BSE": {
        "name": "Bachelor of Software Engineering",
        "faculty": "School of Computing and Information Technology",
        "campus": ["kampala"],
        "duration": 3,
        "tuition_ugx": 2_048_000,
        "level": "bachelor",
        "requirements": {
            "essential": ["Mathematics"],
            "relevant": ["Physics", "Computer Studies"],
            "minimum_points": 10,
            "min_principal_passes": 2
        },
        "career_paths": ["Software Engineer", "DevOps Engineer", "System Architect"]
    },
    "BSc-CFCI": {
        "name": "Bachelor of Science in Computer Forensics and Criminal Investigations",
        "faculty": "School of Computing and Information Technology",
        "campus": ["kampala"],
        "duration": 3,
        "tuition_ugx": 2_048_000,
        "level": "bachelor",
        "requirements": {
            "essential": ["Mathematics"],
            "minimum_points": 10,
            "min_principal_passes": 2
        },
        "career_paths": ["Digital Forensics Expert", "Cybercrime Investigator", "Security Analyst"]
    },
    "BSc-STATS-COMP": {
        "name": "Bachelor of Science in Statistics",
        "faculty": "School of Computing and Information Technology",
        "campus": ["kampala"],
        "duration": 3,
        "tuition_ugx": 1_718_200,
        "level": "bachelor",
        "requirements": {
            "essential": ["Mathematics"],
            "minimum_points": 8,
            "min_principal_passes": 2
        },
        "career_paths": ["Statistician", "Data Analyst", "Researcher"]
    },
}

# HEC Programs
HEC_PROGRAMS = {
    "HEC-ARTS": {
        "name": "Higher Education Certificate (Arts/Humanities)",
        "faculty": "College of Education, Open and Distance Learning",
        "campus": ["kampala"],
        "duration": 1,
        "tuition_ugx": 800_000,
        "level": "hec",
        "track": "arts",
        "subjects": ["Entrepreneurship", "History", "Religious Studies", "Economics", "Geography"],
        "requirements": {
            "min_subsidiary_passes": 2,
            "min_principal_passes": 1
        },
        "progresses_to": ["LLB", "BBA", "BCom", "BSW", "BPA", "BEd", "BA-ECON"]
    },
    "HEC-BIO": {
        "name": "Higher Education Certificate (Biological Sciences)",
        "faculty": "College of Education, Open and Distance Learning",
        "campus": ["kampala"],
        "duration": 1,
        "tuition_ugx": 800_000,
        "level": "hec",
        "track": "biological",
        "subjects": ["Biology", "Chemistry"],
        "requirements": {
            "min_subsidiary_passes": 2,
            "min_principal_passes": 1
        },
        "progresses_to": ["MBChB", "BNS-DIRECT", "BPharm", "BMLS-DIRECT", "BDS-DENT", "BPH"]
    },
    "HEC-PHY": {
        "name": "Higher Education Certificate (Physical Sciences)",
        "faculty": "College of Education, Open and Distance Learning",
        "campus": ["kampala"],
        "duration": 1,
        "tuition_ugx": 800_000,
        "level": "hec",
        "track": "physical",
        "subjects": ["Physics", "Mathematics"],
        "requirements": {
            "min_subsidiary_passes": 2,
            "min_principal_passes": 1
        },
        "progresses_to": ["BCS", "BIT", "BSE", "BSc-MATH", "BSc-STAT", "BSc-IC"]
    }
}

# National Certificate Programs
NATIONAL_CERTIFICATE_PROGRAMS = {
    "NC-BUSINESS": {
        "name": "National Certificate in Business Administration",
        "faculty": "School of Business and Management",
        "campus": ["kampala"],
        "duration": 2,
        "tuition_ugx": 550_000,
        "level": "national_certificate",
        "requirements": {
            "min_olevel_passes": 3
        },
        "progresses_to": ["DIP-BUSINESS", "BBA"]
    },
    "NC-PROCUREMENT": {
        "name": "National Certificate in Procurement and Logistics Management",
        "faculty": "School of Business and Management",
        "campus": ["kampala"],
        "duration": 2,
        "tuition_ugx": 550_000,
        "level": "national_certificate",
        "requirements": {
            "min_olevel_passes": 3
        },
        "progresses_to": ["DIP-PROCUREMENT", "BPLM"]
    },
    "NC-SECRETARIAL": {
        "name": "National Certificate in Secretarial and Office Management",
        "faculty": "School of Business and Management",
        "campus": ["kampala"],
        "duration": 2,
        "tuition_ugx": 550_000,
        "level": "national_certificate",
        "requirements": {
            "min_olevel_passes": 3
        },
        "progresses_to": ["DIP-SECRETARIAL"]
    },
    "NC-PUBLIC-ADMIN": {
        "name": "National Certificate in Public Administration",
        "faculty": "School of Business and Management",
        "campus": ["kampala"],
        "duration": 2,
        "tuition_ugx": 550_000,
        "level": "national_certificate",
        "requirements": {
            "min_olevel_passes": 3
        },
        "progresses_to": ["DIP-PUBLIC-ADMIN"]
    },
    "NC-GUIDANCE": {
        "name": "National Certificate in Guidance and Counseling",
        "faculty": "School of Social Sciences",
        "campus": ["kampala"],
        "duration": 2,
        "tuition_ugx": 550_000,
        "level": "national_certificate",
        "requirements": {
            "min_olevel_passes": 3
        },
        "progresses_to": ["DIP-GUIDANCE"]
    },
    "NC-ICT": {
        "name": "National Certificate in Information Communication Technology",
        "faculty": "School of Computing and Information Technology",
        "campus": ["kampala"],
        "duration": 2,
        "tuition_ugx": 550_000,
        "level": "national_certificate",
        "requirements": {
            "min_olevel_passes": 3,
            "subjects": ["Mathematics"]
        },
        "progresses_to": ["DIP-CS", "DIP-IT", "BIT"]
    },
    "NC-LIBRARY": {
        "name": "National Certificate in Library and Information Science",
        "faculty": "School of Computing and Information Technology",
        "campus": ["kampala"],
        "duration": 2,
        "tuition_ugx": 550_000,
        "level": "national_certificate",
        "requirements": {
            "min_olevel_passes": 3
        },
        "progresses_to": ["DIP-LIBRARY", "BLIS"]
    }
}

# Combine all programs for the recommendation engine
ALL_KIU_PROGRAMS = {**KIU_PROGRAMS_DB, **HEC_PROGRAMS, **NATIONAL_CERTIFICATE_PROGRAMS}
