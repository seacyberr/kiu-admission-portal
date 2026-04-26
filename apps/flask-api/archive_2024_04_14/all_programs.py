"""
KIU UNIFIED PROGRAMS DATABASE
=============================

Single source of truth for ALL KIU programs.
Loads from seed-programs.json (official KIU data with default codes).

This file provides a unified interface to access all programs without duplication.
Other program files should import from here or be deprecated.
"""

import json
import os
from typing import List, Dict, Optional, Any

# Load official programs from seed-programs.json
_DATA_FILE = os.path.join(os.path.dirname(__file__), 'seed-programs.json')

def _load_programs() -> List[Dict]:
    """Load programs from seed-programs.json (official KIU source)"""
    try:
        with open(_DATA_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get('programs', [])
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Warning: Could not load seed-programs.json: {e}")
        return []

# Load all programs from official source
_ALL_PROGRAMS = _load_programs()

# Validate and normalize campus field
def _normalize_campus(campus: str) -> str:
    """Normalize campus to: main, western, or both"""
    if not campus:
        return "main"
    camp = str(campus).lower()
    if camp in ["kampala", "main campus", "kiu main", "kiu-main"]:
        return "main"
    elif camp in ["western", "western campus", "ishaka", "bushenyi", "kiu western", "kiu-western"]:
        return "western"
    elif camp in ["both", "all", "main/western", "western/main"]:
        return "both"
    return camp

# Process and normalize all programs
for p in _ALL_PROGRAMS:
    p['campus'] = _normalize_campus(p.get('campus', 'main'))

# =============================================================================
# UNIFIED PROGRAM LISTS - No Duplication
# =============================================================================

# All programs
ALL_PROGRAMS = _ALL_PROGRAMS

# Programs by level (using official KIU level names from seed-programs.json)
PROGRAMS_BY_LEVEL = {
    "certificate": [p for p in ALL_PROGRAMS if p.get("level") == "certificate"],
    "diploma": [p for p in ALL_PROGRAMS if p.get("level") == "diploma"],
    "hec": [p for p in ALL_PROGRAMS if p.get("level") == "hec"],
    "bachelors": [p for p in ALL_PROGRAMS if p.get("level") in ["bachelors", "degree"]],
    "degree": [p for p in ALL_PROGRAMS if p.get("level") == "degree"],  # alias
    "pgd": [p for p in ALL_PROGRAMS if p.get("level") == "pgd"],
    "masters": [p for p in ALL_PROGRAMS if p.get("level") == "masters"],
    "phd": [p for p in ALL_PROGRAMS if p.get("level") == "phd"],
}

# Programs by campus
PROGRAMS_BY_CAMPUS = {
    "main": [p for p in ALL_PROGRAMS if p.get("campus") in ["main", "both"]],
    "western": [p for p in ALL_PROGRAMS if p.get("campus") in ["western", "both"]],
    "both": [p for p in ALL_PROGRAMS if p.get("campus") == "both"],
}

# Programs by faculty
FACULTIES = sorted(set(p.get("faculty", "Unknown") for p in ALL_PROGRAMS))
PROGRAMS_BY_FACULTY = {
    faculty: [p for p in ALL_PROGRAMS if p.get("faculty") == faculty]
    for faculty in FACULTIES
}

# =============================================================================
# BACKWARD COMPATIBILITY - For existing code that imports from scattered files
# =============================================================================

# Map to old variable names for backward compatibility
CERTIFICATE_PROGRAMS = PROGRAMS_BY_LEVEL["certificate"]
DIPLOMA_PROGRAMS = PROGRAMS_BY_LEVEL["diploma"]
HEC_PROGRAMS = PROGRAMS_BY_LEVEL["hec"]
BACHELORS_PROGRAMS = PROGRAMS_BY_LEVEL["bachelors"]
PGD_PROGRAMS = PROGRAMS_BY_LEVEL["pgd"]
MASTERS_PROGRAMS = PROGRAMS_BY_LEVEL["masters"]
PHD_PROGRAMS = PROGRAMS_BY_LEVEL["phd"]

# Old entry requirements mapping (backward compatibility)
ENTRY_REQUIREMENTS = {
    "phd": ["masters"],
    "masters": ["bachelors"],
    "pgd": ["bachelors"],
    "bachelors": ["uace", "hec", "diploma"],
    "diploma": ["uce", "national_certificate"],
    "certificate": ["uce", "national_certificate"],
    "hec": ["uce"],
}

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def get_programs_by_level(level: str) -> List[Dict]:
    """Get all programs for a specific academic level"""
    return PROGRAMS_BY_LEVEL.get(level.lower(), [])

def get_programs_by_campus(campus: str) -> List[Dict]:
    """Get all programs available at a specific campus"""
    campus = _normalize_campus(campus)
    if campus in ["main", "western", "both"]:
        return PROGRAMS_BY_CAMPUS.get(campus, [])
    return []

def get_programs_by_faculty(faculty: str) -> List[Dict]:
    """Get all programs for a specific faculty"""
    return PROGRAMS_BY_FACULTY.get(faculty, [])

def get_program_by_code(code: str) -> Optional[Dict]:
    """Get a specific program by its official KIU code"""
    code_upper = code.upper()
    for p in ALL_PROGRAMS:
        if p.get("code", "").upper() == code_upper:
            return p
    return None

def get_program_by_name(name: str) -> Optional[Dict]:
    """Get a program by name (exact match)"""
    for p in ALL_PROGRAMS:
        if p.get("name") == name:
            return p
    return None

def search_programs(query: str, level: Optional[str] = None, campus: Optional[str] = None) -> List[Dict]:
    """Search programs by name, code, or faculty"""
    query_lower = query.lower()
    results = []
    
    for p in ALL_PROGRAMS:
        # Check if query matches any field
        searchable = [
            p.get("name", ""),
            p.get("code", ""),
            p.get("faculty", ""),
            p.get("description", ""),
        ]
        if any(query_lower in str(field).lower() for field in searchable):
            # Apply filters
            if level and p.get("level") != level.lower():
                continue
            if campus and p.get("campus") != _normalize_campus(campus):
                continue
            results.append(p)
    
    return results

def get_program_count() -> Dict[str, int]:
    """Get count of programs by level and total"""
    counts = {level: len(progs) for level, progs in PROGRAMS_BY_LEVEL.items()}
    counts["total"] = len(ALL_PROGRAMS)
    counts["main_campus"] = len(PROGRAMS_BY_CAMPUS["main"])
    counts["western_campus"] = len(PROGRAMS_BY_CAMPUS["western"])
    counts["both_campuses"] = len(PROGRAMS_BY_CAMPUS["both"])
    return counts

# =============================================================================
# NCHE FORMAT CONVERSION
# =============================================================================

def to_nche_format(program: Dict) -> Dict:
    """Convert program to NCHE recommendation engine format"""
    campus = program.get("campus", "main")
    campus_list = ["Main", "Western"] if campus == "both" else [campus.capitalize()]
    
    return {
        "id": program.get("id"),
        "name": program.get("name"),
        "code": program.get("code"),
        "institution": "Kampala International University",
        "faculty": program.get("faculty", ""),
        "programme_level": program.get("level", "").capitalize(),
        "duration_years": program.get("duration", 3),
        "intake_months": program.get("intake_months", [8, 1]),
        "campus": campus_list,
        "tuition_ugx_per_semester": program.get("tuition_ugx", 0),
        "tuition_usd_per_semester": program.get("tuition_usd", 0),
        "nche_accreditation": {
            "status": program.get("nche_status", "Fully Accredited"),
            "accreditation_number": program.get("nche_accreditation_number", ""),
            "programme_level": program.get("level", "").capitalize(),
        },
        "nche_requirements": {
            "essential": program.get("required_subjects", []),
            "minimum_points": program.get("min_points", 4),
            "minimum_principal_passes": program.get("min_principals", 2),
        },
        "nche_compliant": program.get("nche_accredited", True),
    }

def get_all_nche_programs() -> List[Dict]:
    """Get ALL programs in NCHE format for the recommendation engine"""
    return [to_nche_format(p) for p in ALL_PROGRAMS]

def get_nche_programs_by_level(level: str) -> List[Dict]:
    """Get programs for a specific level in NCHE format"""
    programs = get_programs_by_level(level)
    return [to_nche_format(p) for p in programs]

# =============================================================================
# DEPRECATED - Old function names for backward compatibility
# =============================================================================

def get_programs_by_requirement(qualification: str) -> List[Dict]:
    """Get programs available to holders of a specific qualification (deprecated)"""
    result = []
    for level, programs in PROGRAMS_BY_LEVEL.items():
        if qualification in ENTRY_REQUIREMENTS.get(level, []):
            result.extend(programs)
    return result

# =============================================================================
# STATISTICS
# =============================================================================

if __name__ == "__main__":
    stats = get_program_count()
    print("\n" + "=" * 70)
    print("KIU UNIFIED PROGRAMS DATABASE (Official KIU Codes)")
    print("=" * 70)
    print(f"\nTotal programs: {stats['total']}")
    print(f"\nBy level:")
    for level in ["certificate", "hec", "diploma", "pgd", "bachelors", "masters", "phd"]:
        if stats[level] > 0:
            print(f"  - {level.capitalize():12}: {stats[level]:3d} programs")
    print(f"\nBy campus:")
    print(f"  - Main Campus:     {stats['main_campus']:3d} programs")
    print(f"  - Western Campus:  {stats['western_campus']:3d} programs")
    print(f"  - Both Campuses:   {stats['both_campuses']:3d} programs")
    print(f"\nFaculties: {len(FACULTIES)}")
    print("\n" + "=" * 70)
