"""
KIU Certificate Programs - 1-2.5 year university programs
These are DIFFERENT from National Certificate (which is a 2-year vocational qualification)
"""

CERTIFICATE_PROGRAMS = [
    # Health Sciences - Certificate Programs (2.5 years)
    {
        "name": "Certificate in General Nursing",
        "duration": "2.5 years",
        "campus": "Main & Western",
        "level": "certificate",
        "requirements": ["uce", "national_certificate"],
        "category": "health_sciences",
        "required_subjects": ["Biology"],
        "code": "CERT-GEN-NURS-001"
    },
    {
        "name": "Certificate in Midwifery",
        "duration": "2.5 years",
        "campus": "Main & Western",
        "level": "certificate",
        "requirements": ["uce", "national_certificate"],
        "category": "health_sciences",
        "required_subjects": ["Biology"],
        "code": "CERT-MIDW-001"
    },
    
    # English Language Certificate (6 months)
    {
        "name": "Certificate in English",
        "duration": "6 months",
        "campus": "Main",
        "level": "certificate",
        "requirements": ["uce", "national_certificate"],
        "category": "language",
        "code": "CERT-ENG-001"
    },
    
    # Other Certificate Programs (if any)
    # Add more certificate programs here as they become available
]

def get_certificate_by_category(category):
    return [p for p in CERTIFICATE_PROGRAMS if p.get("category") == category]

def get_certificate_by_requirement(req):
    return [p for p in CERTIFICATE_PROGRAMS if req in p.get("requirements", [])]
