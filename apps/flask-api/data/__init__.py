"""KIU Program Data Package
All programs organized by level with NCHE entry requirements

IMPORTANT DISTINCTION:
- National Certificate = 2-year vocational QUALIFICATION (what you have)
- Certificate Programs = 1-2.5 year university PROGRAMS (what you enter)
"""

from .kiu_programs import PHD_PROGRAMS, MASTERS_PROGRAMS, PGD_PROGRAMS
from .bachelors_programs import BACHELORS_PROGRAMS
from .diploma_programs import DIPLOMA_PROGRAMS
from .certificate_programs import CERTIFICATE_PROGRAMS
from .hec_programs import HEC_PROGRAMS

# Combined list of all programs
ALL_PROGRAMS = (
    PHD_PROGRAMS + 
    MASTERS_PROGRAMS + 
    PGD_PROGRAMS + 
    BACHELORS_PROGRAMS + 
    DIPLOMA_PROGRAMS + 
    CERTIFICATE_PROGRAMS + 
    HEC_PROGRAMS
)

# Programs by entry qualification
PROGRAMS_BY_ENTRY = {
    "phd": PHD_PROGRAMS,
    "masters": MASTERS_PROGRAMS,
    "pgd": PGD_PROGRAMS,
    "bachelors": BACHELORS_PROGRAMS,
    "diploma": DIPLOMA_PROGRAMS,
    "certificate": CERTIFICATE_PROGRAMS,  # University certificate programs (1-2.5 years)
    "hec": HEC_PROGRAMS,
}

# Entry requirements mapping
ENTRY_REQUIREMENTS = {
    "phd": ["masters"],
    "masters": ["bachelors"],
    "pgd": ["bachelors"],
    "bachelors": ["uace", "hec", "diploma"],
    "diploma": ["uce", "national_certificate"],
    "certificate": ["uce", "national_certificate"],  # Certificate programs accept UCE or National Certificate
    "hec": ["uce"],
}

def get_programs_by_level(level):
    """Get all programs for a specific level"""
    return PROGRAMS_BY_ENTRY.get(level, [])

def get_programs_by_requirement(qualification):
    """Get programs available to holders of a specific qualification"""
    result = []
    for level, programs in PROGRAMS_BY_ENTRY.items():
        if qualification in ENTRY_REQUIREMENTS.get(level, []):
            result.extend(programs)
    return result

def get_program_by_name(name):
    """Find a program by name"""
    for program in ALL_PROGRAMS:
        if program["name"] == name:
            return program
    return None

def search_programs(query):
    """Search programs by name or category"""
    query = query.lower()
    results = []
    for program in ALL_PROGRAMS:
        if query in program["name"].lower() or query in program.get("category", "").lower():
            results.append(program)
    return results

__all__ = [
    "PHD_PROGRAMS",
    "MASTERS_PROGRAMS", 
    "PGD_PROGRAMS",
    "BACHELORS_PROGRAMS",
    "DIPLOMA_PROGRAMS",
    "HEC_PROGRAMS",
    "ALL_PROGRAMS",
    "PROGRAMS_BY_ENTRY",
    "ENTRY_REQUIREMENTS",
    "get_programs_by_level",
    "get_programs_by_requirement",
    "get_program_by_name",
    "search_programs",
]
