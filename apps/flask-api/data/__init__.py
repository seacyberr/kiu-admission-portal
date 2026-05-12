"""KIU Program Data Package - UNIFIED SOURCE
All programs organized by level with NCHE entry requirements

IMPORTANT: This now imports from all_programs.py which is the SINGLE SOURCE OF TRUTH
loading from seed-programs.json (official KIU data with default codes).

IMPORTANT DISTINCTION:
- National Certificate = 2-year vocational QUALIFICATION (what you have)
- Certificate Programs = 1-2.5 year university PROGRAMS (what you enter)
"""

# Import from unified source (all_programs.py loads from seed-programs.json)
from .all_programs import (
    # Program lists by level
    ALL_PROGRAMS,
    CERTIFICATE_PROGRAMS,
    DIPLOMA_PROGRAMS, 
    HEC_PROGRAMS,
    BACHELORS_PROGRAMS,
    PGD_PROGRAMS,
    MASTERS_PROGRAMS,
    PHD_PROGRAMS,
    # Organized indices
    PROGRAMS_BY_LEVEL,
    PROGRAMS_BY_CAMPUS,
    PROGRAMS_BY_FACULTY,
    FACULTIES,
    # Helper functions
    get_programs_by_level,
    get_programs_by_campus,
    get_programs_by_faculty,
    get_program_by_code,
    get_program_by_name,
    search_programs,
    get_program_count,
    # NCHE functions
    to_nche_format,
    get_all_nche_programs,
    get_nche_programs_by_level,
    # Backward compatibility
    ENTRY_REQUIREMENTS,
    get_programs_by_requirement,
)

# Backward compatibility alias
PROGRAMS_BY_ENTRY = PROGRAMS_BY_LEVEL

__all__ = [
    # Program lists
    "ALL_PROGRAMS",
    "CERTIFICATE_PROGRAMS",
    "DIPLOMA_PROGRAMS",
    "HEC_PROGRAMS",
    "BACHELORS_PROGRAMS",
    "PGD_PROGRAMS",
    "MASTERS_PROGRAMS",
    "PHD_PROGRAMS",
    # Indices
    "PROGRAMS_BY_LEVEL",
    "PROGRAMS_BY_CAMPUS",
    "PROGRAMS_BY_FACULTY",
    "PROGRAMS_BY_ENTRY",  # backward compat
    "FACULTIES",
    "ENTRY_REQUIREMENTS",
    # Functions
    "get_programs_by_level",
    "get_programs_by_campus",
    "get_programs_by_faculty",
    "get_program_by_code",
    "get_program_by_name",
    "search_programs",
    "get_program_count",
    "get_programs_by_requirement",
    "to_nche_format",
    "get_all_nche_programs",
    "get_nche_programs_by_level",
]
