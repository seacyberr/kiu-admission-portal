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
