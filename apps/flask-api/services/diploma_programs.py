"""KIU Diploma Programs - Requires UCE or National Certificate"""

DIPLOMA_PROGRAMS = [
    # Business & Management (2 years)
    {"name": "Diploma in Business Administration", "duration": "2 years", "campus": "Main & Western", "level": "diploma", "requirements": ["uce", "national_certificate"], "category": "business"},
    {"name": "Diploma in Tourism and Hotel Management", "duration": "2 years", "campus": "Main", "level": "diploma", "requirements": ["uce", "national_certificate"], "category": "tourism"},
    {"name": "Diploma in Human Resource Management", "duration": "2 years", "campus": "Main", "level": "diploma", "requirements": ["uce", "national_certificate"], "category": "business"},
    {"name": "Diploma in Supplies and Procurement Management", "duration": "2 years", "campus": "Main", "level": "diploma", "requirements": ["uce", "national_certificate"], "category": "business"},
    {"name": "Diploma in Secretarial Studies", "duration": "2 years", "campus": "Main", "level": "diploma", "requirements": ["uce", "national_certificate"], "category": "business"},
    {"name": "Diploma in Commerce", "duration": "2 years", "campus": "Main", "level": "diploma", "requirements": ["uce", "national_certificate"], "category": "business", "note": "Distance learning"},
    
    # Social Sciences (2 years)
    {"name": "Diploma in Public Administration", "duration": "2 years", "campus": "Main & Western", "level": "diploma", "requirements": ["uce", "national_certificate"], "category": "administration"},
    {"name": "Diploma in Development Studies", "duration": "2 years", "campus": "Main", "level": "diploma", "requirements": ["uce", "national_certificate"], "category": "social_sciences"},
    {"name": "Diploma in International Relations", "duration": "2 years", "campus": "Main", "level": "diploma", "requirements": ["uce", "national_certificate"], "category": "international"},
    {"name": "Diploma in Social and Community Development", "duration": "2 years", "campus": "Main", "level": "diploma", "requirements": ["uce", "national_certificate"], "category": "social_work"},
    {"name": "Diploma in Social Work", "duration": "2 years", "campus": "Main", "level": "diploma", "requirements": ["uce", "national_certificate"], "category": "social_work"},
    
    # Engineering (2 years)
    {"name": "Diploma in Civil Engineering", "duration": "2 years", "campus": "Main", "level": "diploma", "requirements": ["uce", "national_certificate"], "category": "engineering"},
    {"name": "Diploma in Electrical Engineering", "duration": "2 years", "campus": "Main", "level": "diploma", "requirements": ["uce", "national_certificate"], "category": "engineering"},
    {"name": "Diploma in Mechanical Engineering", "duration": "2 years", "campus": "Main", "level": "diploma", "requirements": ["uce", "national_certificate"], "category": "engineering"},
    {"name": "Diploma in Automotive Engineering", "duration": "2 years", "campus": "Main", "level": "diploma", "requirements": ["uce", "national_certificate"], "category": "engineering"},
    {"name": "Diploma in Telecommunication Engineering", "duration": "2 years", "campus": "Main", "level": "diploma", "requirements": ["uce", "national_certificate"], "category": "engineering"},
    
    # Agriculture (2 years)
    {"name": "Diploma in Agribusiness", "duration": "2 years", "campus": "Main", "level": "diploma", "requirements": ["uce", "national_certificate"], "category": "agriculture"},
    {"name": "Diploma in Agricultural Extension", "duration": "2 years", "campus": "Main", "level": "diploma", "requirements": ["uce", "national_certificate"], "category": "agriculture"},
    {"name": "Diploma in Agricultural Economics", "duration": "2 years", "campus": "Main", "level": "diploma", "requirements": ["uce", "national_certificate"], "category": "agriculture"},
    
    # Health Sciences (Western - 3 years or 1.5 extension)
    {"name": "Diploma in Clinical Medicine", "duration": "3 years", "campus": "Western", "level": "diploma", "requirements": ["uce"], "category": "medicine", "required_subjects": ["Biology", "Chemistry"]},
    {"name": "Diploma in Medical Laboratory Technology", "duration": "3 years", "campus": "Western", "level": "diploma", "requirements": ["uce"], "category": "health_sciences", "required_subjects": ["Chemistry", "Biology"]},
    {"name": "Diploma in Pharmacy", "duration": "3 years", "campus": "Western", "level": "diploma", "requirements": ["uce"], "category": "medicine", "required_subjects": ["Chemistry", "Biology"]},
    {"name": "Diploma in Nursing Sciences (Direct)", "duration": "3 years", "campus": "Western", "level": "diploma", "requirements": ["uce"], "category": "health_sciences", "required_subjects": ["Biology"]},
    {"name": "Diploma in Nursing Sciences (Extension)", "duration": "1.5 years", "campus": "Western", "level": "diploma", "requirements": ["national_certificate"], "category": "health_sciences"},
]

def get_diploma_by_category(category):
    return [p for p in DIPLOMA_PROGRAMS if p.get("category") == category]

def get_diploma_by_requirement(req):
    return [p for p in DIPLOMA_PROGRAMS if req in p.get("requirements", [])]
