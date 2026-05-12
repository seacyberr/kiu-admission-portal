"""KIU Higher Education Certificate (HEC) Programs - For UCE Holders"""

HEC_PROGRAMS = [
    # Biological Sciences Track
    {"name": "Higher Education Certificate in Biology and Chemistry", "duration": "1 year", "campus": "Main", "level": "hec", "hec_track": "biological", "requirements": ["uce"], "required_subjects": ["Biology", "Chemistry"]},
    {"name": "Higher Education Certificate in Biology and Physics", "duration": "1 year", "campus": "Main", "level": "hec", "hec_track": "biological", "requirements": ["uce"], "required_subjects": ["Biology", "Physics"]},
    
    # Physical Sciences Track
    {"name": "Higher Education Certificate in Chemistry and Mathematics", "duration": "1 year", "campus": "Main", "level": "hec", "hec_track": "physical", "requirements": ["uce"], "required_subjects": ["Chemistry", "Mathematics"]},
    {"name": "Higher Education Certificate in Physics and Mathematics", "duration": "1 year", "campus": "Main", "level": "hec", "hec_track": "physical", "requirements": ["uce"], "required_subjects": ["Physics", "Mathematics"]},
    
    # Arts Track
    {"name": "Higher Education Certificate in Economics and Mathematics", "duration": "1 year", "campus": "Main", "level": "hec", "hec_track": "arts", "requirements": ["uce"]},
    {"name": "Higher Education Certificate in Geography and Economics", "duration": "1 year", "campus": "Main", "level": "hec", "hec_track": "arts", "requirements": ["uce"]},
    {"name": "Higher Education Certificate in Geography and Entrepreneurship", "duration": "1 year", "campus": "Main", "level": "hec", "hec_track": "arts", "requirements": ["uce"]},
    {"name": "Higher Education Certificate in Geography and History", "duration": "1 year", "campus": "Main", "level": "hec", "hec_track": "arts", "requirements": ["uce"]},
    {"name": "Higher Education Certificate in Geography and Mathematics", "duration": "1 year", "campus": "Main", "level": "hec", "hec_track": "arts", "requirements": ["uce"]},
    {"name": "Higher Education Certificate in History and Economics", "duration": "1 year", "campus": "Main", "level": "hec", "hec_track": "arts", "requirements": ["uce"]},
    {"name": "Higher Education Certificate in History and Entrepreneurship", "duration": "1 year", "campus": "Main", "level": "hec", "hec_track": "arts", "requirements": ["uce"]},
    {"name": "Higher Education Certificate in History and Religious Education", "duration": "1 year", "campus": "Main", "level": "hec", "hec_track": "arts", "requirements": ["uce"]},
    {"name": "Higher Education Certificate in Literature and Geography", "duration": "1 year", "campus": "Main", "level": "hec", "hec_track": "arts", "requirements": ["uce"]},
    {"name": "Higher Education Certificate in Literature and History", "duration": "1 year", "campus": "Main", "level": "hec", "hec_track": "arts", "requirements": ["uce"]},
    {"name": "Higher Education Certificate in Literature and Religious Education", "duration": "1 year", "campus": "Main", "level": "hec", "hec_track": "arts", "requirements": ["uce"]},
    {"name": "Higher Education Certificate in Mathematics and Entrepreneurship", "duration": "1 year", "campus": "Main", "level": "hec", "hec_track": "arts", "requirements": ["uce"]},
    {"name": "Higher Education Certificate in Religious Education and Economics", "duration": "1 year", "campus": "Main", "level": "hec", "hec_track": "arts", "requirements": ["uce"]},
    {"name": "Higher Education Certificate in Religious Education and Entrepreneurship", "duration": "1 year", "campus": "Main", "level": "hec", "hec_track": "arts", "requirements": ["uce"]},
]

def get_hec_by_track(track):
    """Get HEC programs by track: biological, physical, arts"""
    return [p for p in HEC_PROGRAMS if p.get("hec_track") == track]

def get_all_hec_tracks():
    """Get list of all HEC tracks"""
    return list(set(p.get("hec_track") for p in HEC_PROGRAMS if p.get("hec_track")))
