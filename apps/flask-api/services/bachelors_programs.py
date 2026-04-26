"""KIU Bachelor's Programs - Requires UACE, HEC, or Diploma"""

BACHELORS_PROGRAMS = [
    # Law
    {"name": "Bachelor of Laws (LL.B)", "duration": "4 years", "campus": "Main & Western", "level": "degree", "requirements": ["uace", "hec", "diploma"], "category": "law", "min_principals": 2},
    {"name": "LL.B (Weekend)", "duration": "4.5 years", "campus": "Main", "level": "degree", "requirements": ["uace", "hec", "diploma"], "category": "law", "min_principals": 2},
    
    # Business & Management
    {"name": "Bachelor of Business Administration", "duration": "3 years", "campus": "Main & Western", "level": "degree", "requirements": ["uace", "hec", "diploma"], "category": "business", "min_principals": 2},
    {"name": "BBA (Finance & Banking)", "duration": "3 years", "campus": "Main", "level": "degree", "requirements": ["uace", "hec", "diploma"], "category": "business", "min_principals": 2},
    {"name": "BBA (Marketing)", "duration": "3 years", "campus": "Main", "level": "degree", "requirements": ["uace", "hec", "diploma"], "category": "business", "min_principals": 2},
    {"name": "Bachelor of Entrepreneurship", "duration": "3 years", "campus": "Main", "level": "degree", "requirements": ["uace", "hec", "diploma"], "category": "business", "min_principals": 2},
    {"name": "Bachelor of Human Resource Management", "duration": "3 years", "campus": "Main", "level": "degree", "requirements": ["uace", "hec", "diploma"], "category": "business", "min_principals": 2},
    
    # Economics
    {"name": "Bachelor of Arts in Economics", "duration": "3 years", "campus": "Main", "level": "degree", "requirements": ["uace", "hec", "diploma"], "category": "economics", "min_principals": 2},
    {"name": "Bachelor of Economics and Applied Statistics", "duration": "3 years", "campus": "Main", "level": "degree", "requirements": ["uace", "hec", "diploma"], "category": "economics", "min_principals": 2},
    
    # Tourism & Hospitality
    {"name": "Bachelor of Tourism and Hotel Management", "duration": "3 years", "campus": "Main", "level": "degree", "requirements": ["uace", "hec", "diploma"], "category": "tourism", "min_principals": 2},
    
    # Communication
    {"name": "Bachelor of Arts in Mass Communication", "duration": "3 years", "campus": "Main", "level": "degree", "requirements": ["uace", "hec", "diploma"], "category": "communication", "min_principals": 2},
    
    # Social Sciences
    {"name": "Bachelor of Development Studies", "duration": "3 years", "campus": "Main & Western", "level": "degree", "requirements": ["uace", "hec", "diploma"], "category": "social_sciences", "min_principals": 2},
    {"name": "Bachelor of Public Administration", "duration": "3 years", "campus": "Main & Western", "level": "degree", "requirements": ["uace", "hec", "diploma"], "category": "administration", "min_principals": 2},
    {"name": "Bachelor of International Relations", "duration": "3 years", "campus": "Main", "level": "degree", "requirements": ["uace", "hec", "diploma"], "category": "international", "min_principals": 2},
    {"name": "Bachelor of Guidance and Counseling", "duration": "3 years", "campus": "Main", "level": "degree", "requirements": ["uace", "hec", "diploma"], "category": "psychology", "min_principals": 2},
    {"name": "Bachelor of Social Work", "duration": "3 years", "campus": "Main", "level": "degree", "requirements": ["uace", "hec", "diploma"], "category": "social_work", "min_principals": 2},
    {"name": "Bachelor of Social and Community Development", "duration": "3 years", "campus": "Main", "level": "degree", "requirements": ["uace", "hec", "diploma"], "category": "social_work", "min_principals": 2},
    
    # Engineering (4 years, requires science subjects)
    {"name": "Bachelor of Science in Civil Engineering", "duration": "4 years", "campus": "Main", "level": "degree", "requirements": ["uace", "hec", "diploma"], "category": "engineering", "min_principals": 2, "required_subjects": ["Mathematics", "Physics"]},
    {"name": "Bachelor of Science in Electrical Engineering", "duration": "4 years", "campus": "Main", "level": "degree", "requirements": ["uace", "hec", "diploma"], "category": "engineering", "min_principals": 2, "required_subjects": ["Mathematics", "Physics"]},
    {"name": "Bachelor of Science in Mechanical Engineering", "duration": "4 years", "campus": "Main", "level": "degree", "requirements": ["uace", "hec", "diploma"], "category": "engineering", "min_principals": 2, "required_subjects": ["Mathematics", "Physics"]},
    {"name": "Bachelor of Science in Telecommunication Engineering", "duration": "4 years", "campus": "Main", "level": "degree", "requirements": ["uace", "hec", "diploma"], "category": "engineering", "min_principals": 2, "required_subjects": ["Mathematics", "Physics"]},
    {"name": "Bachelor of Science in Computer Engineering", "duration": "4 years", "campus": "Main", "level": "degree", "requirements": ["uace", "hec", "diploma"], "category": "engineering", "min_principals": 2, "required_subjects": ["Mathematics", "Physics"]},
    {"name": "Bachelor of Science in Biomedical Engineering", "duration": "4 years", "campus": "Main", "level": "degree", "requirements": ["uace", "hec", "diploma"], "category": "engineering", "min_principals": 2, "required_subjects": ["Mathematics", "Physics", "Chemistry"]},
    {"name": "Bachelor of Architecture", "duration": "5 years", "campus": "Main", "level": "degree", "requirements": ["uace", "hec", "diploma"], "category": "engineering", "min_principals": 2, "required_subjects": ["Mathematics", "Physics"]},
    {"name": "Bachelor of Science in Petroleum Engineering", "duration": "4 years", "campus": "Main", "level": "degree", "requirements": ["uace", "hec", "diploma"], "category": "engineering", "min_principals": 2, "required_subjects": ["Mathematics", "Physics", "Chemistry"]},
    {"name": "Bachelor of Science in Surveying", "duration": "4 years", "campus": "Main", "level": "degree", "requirements": ["uace", "hec", "diploma"], "category": "engineering", "min_principals": 2, "required_subjects": ["Mathematics", "Physics"]},
    {"name": "Bachelor of Science in Agricultural Engineering", "duration": "4 years", "campus": "Main", "level": "degree", "requirements": ["uace", "hec", "diploma"], "category": "engineering", "min_principals": 2, "required_subjects": ["Mathematics", "Physics"]},
    
    # Agriculture
    {"name": "Bachelor of Agribusiness", "duration": "3 years", "campus": "Main", "level": "degree", "requirements": ["uace", "hec", "diploma"], "category": "agriculture", "min_principals": 2},
    {"name": "Bachelor of Agricultural Economics", "duration": "3 years", "campus": "Main", "level": "degree", "requirements": ["uace", "hec", "diploma"], "category": "agriculture", "min_principals": 2},
    {"name": "Bachelor of Agricultural Extension", "duration": "3 years", "campus": "Main", "level": "degree", "requirements": ["uace", "hec", "diploma"], "category": "agriculture", "min_principals": 2},
    
    # Health Sciences (Western Campus) - High requirements
    {"name": "Bachelor of Medicine and Surgery (MBChB)", "duration": "5.5 years", "campus": "Western", "level": "degree", "requirements": ["uace", "hec"], "category": "medicine", "min_principals": 3, "min_points": 9, "required_subjects": ["Biology", "Chemistry", "Physics/Mathematics"]},
    {"name": "Bachelor of Dental Surgery", "duration": "5.5 years", "campus": "Western", "level": "degree", "requirements": ["uace", "hec"], "category": "medicine", "min_principals": 3, "min_points": 9, "required_subjects": ["Biology", "Chemistry", "Physics/Mathematics"]},
    {"name": "Bachelor of Pharmacy", "duration": "4.5 years", "campus": "Western", "level": "degree", "requirements": ["uace", "hec"], "category": "medicine", "min_principals": 3, "min_points": 8, "required_subjects": ["Chemistry", "Biology", "Mathematics/Physics"]},
    {"name": "Bachelor of Medical Laboratory Science (Direct)", "duration": "4.5 years", "campus": "Western", "level": "degree", "requirements": ["uace", "hec"], "category": "health_sciences", "min_principals": 2, "required_subjects": ["Biology", "Chemistry"]},
    {"name": "Bachelor of Clinical Medicine (Direct)", "duration": "4.5 years", "campus": "Western", "level": "degree", "requirements": ["uace", "hec"], "category": "medicine", "min_principals": 3, "required_subjects": ["Biology", "Chemistry", "Physics/Mathematics"]},
    {"name": "Bachelor of Nursing Sciences (Direct)", "duration": "4 years", "campus": "Western", "level": "degree", "requirements": ["uace", "hec"], "category": "health_sciences", "min_principals": 2, "required_subjects": ["Biology"]},
    {"name": "Bachelor of Nursing Sciences (Extension)", "duration": "3 years", "campus": "Western", "level": "degree", "requirements": ["diploma"], "category": "health_sciences"},
    {"name": "Bachelor of Science in Anatomy", "duration": "3.5 years", "campus": "Western", "level": "degree", "requirements": ["uace", "hec"], "category": "health_sciences", "min_principals": 2, "required_subjects": ["Biology", "Chemistry"]},
    {"name": "Bachelor of Science in Biochemistry", "duration": "3 years", "campus": "Western", "level": "degree", "requirements": ["uace", "hec"], "category": "health_sciences", "min_principals": 2, "required_subjects": ["Chemistry", "Biology"]},
    {"name": "Bachelor of Science in Microbiology", "duration": "3.5 years", "campus": "Western", "level": "degree", "requirements": ["uace", "hec"], "category": "health_sciences", "min_principals": 2, "required_subjects": ["Biology", "Chemistry"]},
    {"name": "Bachelor of Science in Physiology", "duration": "3.5 years", "campus": "Western", "level": "degree", "requirements": ["uace", "hec"], "category": "health_sciences", "min_principals": 2, "required_subjects": ["Biology", "Chemistry"]},
    
    # Technology & Computing
    {"name": "Bachelor of Computer Science", "duration": "3 years", "campus": "Main", "level": "degree", "requirements": ["uace", "hec", "diploma"], "category": "technology", "min_principals": 2},
    {"name": "Bachelor of Information Technology", "duration": "3 years", "campus": "Main", "level": "degree", "requirements": ["uace", "hec", "diploma"], "category": "technology", "min_principals": 2},
    {"name": "Bachelor of Science in Data Management", "duration": "3 years", "campus": "Main", "level": "degree", "requirements": ["uace", "hec", "diploma"], "category": "technology", "min_principals": 2},
    {"name": "Bachelor of Science in Cybersecurity", "duration": "3 years", "campus": "Main", "level": "degree", "requirements": ["uace", "hec", "diploma"], "category": "technology", "min_principals": 2},
    {"name": "Bachelor of Science in AI", "duration": "3 years", "campus": "Main", "level": "degree", "requirements": ["uace", "hec", "diploma"], "category": "technology", "min_principals": 2},
    {"name": "Bachelor of Science in Software Development", "duration": "3 years", "campus": "Main", "level": "degree", "requirements": ["uace", "hec", "diploma"], "category": "technology", "min_principals": 2},
    
    # Education
    {"name": "Bachelor of Arts with Education", "duration": "3 years", "campus": "Main & Western", "level": "degree", "requirements": ["uace", "hec", "diploma"], "category": "education", "min_principals": 2},
    {"name": "Bachelor of Science with Education", "duration": "3 years", "campus": "Main", "level": "degree", "requirements": ["uace", "hec", "diploma"], "category": "education", "min_principals": 2, "required_subjects": ["Mathematics", "Physics", "Chemistry", "Biology"]},
    {"name": "Bachelor of Education (Primary/Secondary/Special Needs)", "duration": "2 years", "campus": "Main & Western", "level": "degree", "requirements": ["diploma"], "category": "education", "note": "Inservice program"},
]

def get_bachelors_by_category(category):
    return [p for p in BACHELORS_PROGRAMS if p.get("category") == category]

def get_bachelors_by_requirement(req):
    return [p for p in BACHELORS_PROGRAMS if req in p.get("requirements", [])]
