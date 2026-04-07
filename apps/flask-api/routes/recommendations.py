"""Programme recommendations with proper education hierarchy validation."""

from flask import Blueprint, jsonify, g
from typing import Dict, List, Any, Optional

recommendations_bp = Blueprint("recommendations", __name__, url_prefix="/api/v1/recommendations")


# Canonical education level ranking. Higher integer = higher qualification.
# All aliases map to the same rank for consistent comparison.
LEVEL_RANK: Dict[str, int] = {
    # Lower secondary
    "o-level": 10,
    "o level": 10,
    "ordinary level": 10,
    "uganda certificate of education": 10,
    "uce": 10,

    # Upper secondary
    "a-level": 20,
    "a level": 20,
    "advanced level": 20,
    "uganda advanced certificate of education": 20,
    "uace": 20,

    # Post-secondary certificate
    "certificate": 30,
    "certificate level": 30,
    "national certificate": 30,

    # Diploma
    "diploma": 40,
    "national diploma": 40,
    "higher diploma": 40,

    # Undergraduate
    "bachelors": 50,
    "bachelor": 50,
    "bachelor's": 50,
    "bachelor's degree": 50,
    "undergraduate": 50,
    "first degree": 50,

    # Postgraduate
    "postgraduate certificate": 60,
    "postgraduate diploma": 70,
    "masters": 80,
    "master": 80,
    "master's": 80,
    "master's degree": 80,
    "graduate degree": 80,

    # Doctorate
    "phd": 90,
    "doctorate": 90,
    "doctor of philosophy": 90,
    "doctoral degree": 90,
}

# Clean normalized name to display name mapping
LEVEL_DISPLAY: Dict[str, str] = {
    "o-level": "O-Level / UCE",
    "a-level": "A-Level / UACE",
    "certificate": "Certificate",
    "diploma": "Diploma",
    "bachelors": "Bachelor's Degree",
    "postgraduate-certificate": "Postgraduate Certificate",
    "postgraduate-diploma": "Postgraduate Diploma",
    "masters": "Master's Degree",
    "phd": "Doctorate (PhD)",
}


def _get_level_rank(level_name: Optional[str]) -> int:
    """Get canonical rank for any education level string. Returns 0 if unknown."""
    if not level_name:
        return 0
    normalised = level_name.strip().lower()
    return LEVEL_RANK.get(normalised, 0)


def _applicant_qualifies(applicant_level: str, programme_min_level: str) -> bool:
    """
    Return True if applicant holds sufficient qualification for the programme.
    
    Correctly handles all cases:
    ✅ PhD holder can apply for Bachelor's, Diploma, etc.
    ✅ Masters holder can apply for Bachelors
    ✅ Bachelors holder cannot apply for Masters
    ✅ Only applicants >= programme minimum level are accepted
    """
    applicant_rank = _get_level_rank(applicant_level)
    programme_rank = _get_level_rank(programme_min_level)
    
    return applicant_rank >= programme_rank


def _sort_programmes(programmes: List[Dict[str, Any]], applicant_level: str) -> List[Dict[str, Any]]:
    """
    Sort programmes with optimal priority order:
    1. Programmes requiring ONE level above applicant (best upward mobility)
    2. Programmes requiring SAME level as applicant
    3. Programmes requiring LOWER levels (descending order)
    """
    applicant_rank = _get_level_rank(applicant_level)
    
    def sort_key(programme: Dict[str, Any]) -> tuple:
        prog_rank = _get_level_rank(programme.get("minimum_level", ""))
        delta = prog_rank - applicant_rank
        
        if delta == 10:
            # Exactly one level up: highest priority
            return (0, -prog_rank)
        elif delta == 0:
            # Same level
            return (1, -prog_rank)
        elif delta < 0:
            # Lower level programmes
            return (2, -prog_rank)
        else:
            # Not eligible - lowest priority
            return (99, -prog_rank)
    
    return sorted(programmes, key=sort_key)


@recommendations_bp.route("", methods=["GET"])
def get_recommendations():
    """Get sorted list of programmes the current user is eligible for."""
    user = g.current_user
    applicant_level = user.highest_education_level
    
    # TODO: Fetch actual programmes from database
    all_programmes: List[Dict[str, Any]] = []
    
    eligible = [p for p in all_programmes if _applicant_qualifies(applicant_level, p.get("minimum_level", ""))]
    sorted_programmes = _sort_programmes(eligible, applicant_level)
    
    return jsonify({
        "applicant_level": applicant_level,
        "applicant_rank": _get_level_rank(applicant_level),
        "count": len(sorted_programmes),
        "programmes": sorted_programmes
    })


@recommendations_bp.route("/eligible-levels", methods=["GET"])
def get_eligible_levels():
    """Get list of education levels the current user is qualified to apply for."""
    user = g.current_user
    applicant_rank = _get_level_rank(user.highest_education_level)
    
    eligible = []
    for level, rank in sorted(LEVEL_RANK.items(), key=lambda x: x[1]):
        if rank <= applicant_rank:
            eligible.append({
                "level": level,
                "rank": rank,
                "display_name": LEVEL_DISPLAY.get(level, level.title())
            })
    
    # Remove duplicates, keep highest rank per level group
    seen = set()
    unique_levels = []
    for item in reversed(eligible):
        if item["rank"] not in seen:
            seen.add(item["rank"])
            unique_levels.insert(0, item)
    
    return jsonify({
        "applicant_level": user.highest_education_level,
        "applicant_rank": applicant_rank,
        "eligible_levels": unique_levels
    })


@recommendations_bp.route("/summary", methods=["GET"])
def get_recommendation_summary():
    """Get summary statistics for recommendation eligibility."""
    user = g.current_user
    applicant_level = user.highest_education_level
    applicant_rank = _get_level_rank(applicant_level)
    
    return jsonify({
        "highest_education_level": applicant_level,
        "education_rank": applicant_rank,
        "can_apply_above": applicant_rank < max(LEVEL_RANK.values()),
        "maximum_eligible_level": max(r for r in LEVEL_RANK.values() if r <= applicant_rank),
        "next_level_up": min(r for r in LEVEL_RANK.values() if r > applicant_rank) if applicant_rank < max(LEVEL_RANK.values()) else None
    })