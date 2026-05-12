"""KIU Program Catalog - PhD, Masters, PGD, Bachelor's, Diploma, HEC Programs"""

PHD_PROGRAMS = [
    {"name": "PhD in Counseling Psychology", "duration": "3 years", "campus": "Main", "level": "phd", "requirements": ["masters"]},
    {"name": "PhD in Conflict Resolution", "duration": "3 years", "campus": "Main", "level": "phd", "requirements": ["masters"]},
    {"name": "PhD in Development Studies", "duration": "3 years", "campus": "Main", "level": "phd", "requirements": ["masters"]},
    {"name": "PhD in Public Management", "duration": "3 years", "campus": "Main", "level": "phd", "requirements": ["masters"]},
    {"name": "PhD in Telecommunications Engineering", "duration": "3 years", "campus": "Main", "level": "phd", "requirements": ["masters"]},
    {"name": "PhD in Agriculture", "duration": "3 years", "campus": "Main", "level": "phd", "requirements": ["masters"]},
    {"name": "PhD in Anatomy", "duration": "3 years", "campus": "Western", "level": "phd", "requirements": ["masters"]},
    {"name": "PhD in Physiology", "duration": "3 years", "campus": "Western", "level": "phd", "requirements": ["masters"]},
    {"name": "PhD in Biochemistry", "duration": "3 years", "campus": "Western", "level": "phd", "requirements": ["masters"]},
    {"name": "PhD in Microbiology", "duration": "3 years", "campus": "Western", "level": "phd", "requirements": ["masters"]},
    {"name": "PhD in Environmental Science", "duration": "3 years", "campus": "Main", "level": "phd", "requirements": ["masters"]},
]

MASTERS_PROGRAMS = [
    {"name": "Master of Business Administration (MBA)", "duration": "2 years", "campus": "Main & Western", "level": "masters", "requirements": ["bachelors"], "category": "business"},
    {"name": "Master of Arts in Economic Policy", "duration": "2 years", "campus": "Main", "level": "masters", "requirements": ["bachelors"], "category": "economics"},
    {"name": "Master of Arts in Conflict Resolution", "duration": "2 years", "campus": "Main", "level": "masters", "requirements": ["bachelors"], "category": "social_sciences"},
    {"name": "Master of Arts in Counseling Psychology", "duration": "2 years", "campus": "Main", "level": "masters", "requirements": ["bachelors"], "category": "psychology"},
    {"name": "Master of Arts in Development Studies", "duration": "2 years", "campus": "Main", "level": "masters", "requirements": ["bachelors"], "category": "development"},
    {"name": "Master of Arts in Public Administration", "duration": "2 years", "campus": "Main", "level": "masters", "requirements": ["bachelors"], "category": "administration"},
    {"name": "Master of Arts in Social Work", "duration": "2 years", "campus": "Main", "level": "masters", "requirements": ["bachelors"], "category": "social_work"},
    {"name": "Master of Arts in International Relations", "duration": "2 years", "campus": "Main", "level": "masters", "requirements": ["bachelors"], "category": "international"},
    {"name": "Master of Science in Mass Communication", "duration": "2 years", "campus": "Main", "level": "masters", "requirements": ["bachelors"], "category": "communication"},
    {"name": "Master of Science in IT", "duration": "2 years", "campus": "Main", "level": "masters", "requirements": ["bachelors"], "category": "technology"},
    {"name": "Master of Science in Renewable Energy", "duration": "2 years", "campus": "Main", "level": "masters", "requirements": ["bachelors"], "category": "engineering"},
    {"name": "Master of Science in Microbiology", "duration": "2 years", "campus": "Western", "level": "masters", "requirements": ["bachelors"], "category": "health_sciences"},
    {"name": "Master of Science in Anatomy", "duration": "2 years", "campus": "Western", "level": "masters", "requirements": ["bachelors"], "category": "health_sciences"},
    {"name": "Master of Science in Physiology", "duration": "2 years", "campus": "Western", "level": "masters", "requirements": ["bachelors"], "category": "health_sciences"},
    {"name": "Master of Science in Biochemistry", "duration": "2 years", "campus": "Western", "level": "masters", "requirements": ["bachelors"], "category": "health_sciences"},
    {"name": "Master of Science in Pharmacology", "duration": "2 years", "campus": "Western", "level": "masters", "requirements": ["bachelors"], "category": "health_sciences"},
    {"name": "Master of Science in Public Health", "duration": "2 years", "campus": "Western", "level": "masters", "requirements": ["bachelors"], "category": "health_sciences"},
    {"name": "Master of Science in Medical Lab Tech", "duration": "2 years", "campus": "Western", "level": "masters", "requirements": ["bachelors"], "category": "health_sciences"},
    {"name": "Master of Medicine in Internal Medicine", "duration": "3 years", "campus": "Western", "level": "masters", "requirements": ["bachelors"], "category": "medicine"},
    {"name": "Master of Medicine in Surgery", "duration": "3 years", "campus": "Western", "level": "masters", "requirements": ["bachelors"], "category": "medicine"},
    {"name": "Master of Agribusiness", "duration": "2 years", "campus": "Main", "level": "masters", "requirements": ["bachelors"], "category": "agriculture"},
    {"name": "Master of Agricultural Extension", "duration": "2 years", "campus": "Main", "level": "masters", "requirements": ["bachelors"], "category": "agriculture"},
    {"name": "Master of Agricultural Economics", "duration": "2 years", "campus": "Main", "level": "masters", "requirements": ["bachelors"], "category": "agriculture"},
]

PGD_PROGRAMS = [
    {"name": "Postgraduate Diploma in Business Administration", "duration": "1 year", "campus": "Main", "level": "pgd", "requirements": ["bachelors"], "category": "business"},
    {"name": "PGD in Human Resource Management", "duration": "1 year", "campus": "Main", "level": "pgd", "requirements": ["bachelors"], "category": "business"},
    {"name": "PGD in Public Administration", "duration": "1 year", "campus": "Main", "level": "pgd", "requirements": ["bachelors"], "category": "administration"},
    {"name": "PGD in Development Studies", "duration": "1 year", "campus": "Main", "level": "pgd", "requirements": ["bachelors"], "category": "development"},
    {"name": "PGD in Civil Engineering", "duration": "1 year", "campus": "Main", "level": "pgd", "requirements": ["bachelors"], "category": "engineering"},
    {"name": "PGD in Electrical Engineering", "duration": "1 year", "campus": "Main", "level": "pgd", "requirements": ["bachelors"], "category": "engineering"},
    {"name": "PGD in Mechanical Engineering", "duration": "1 year", "campus": "Main", "level": "pgd", "requirements": ["bachelors"], "category": "engineering"},
    {"name": "PGD in Education", "duration": "1 year", "campus": "Main & Western", "level": "pgd", "requirements": ["bachelors"], "category": "education"},
]

# Get all programs combined
def get_all_programs():
    return PHD_PROGRAMS + MASTERS_PROGRAMS + PGD_PROGRAMS

def get_programs_by_level(level):
    """Get programs by level: phd, masters, pgd"""
    all_programs = get_all_programs()
    return [p for p in all_programs if p["level"] == level]

def get_programs_by_category(category):
    """Get programs by category"""
    all_programs = get_all_programs()
    return [p for p in all_programs if p.get("category") == category]
