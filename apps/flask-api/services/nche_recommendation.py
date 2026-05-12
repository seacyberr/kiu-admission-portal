"""
NCHE Uganda A-Level Weighting System for Programme Recommendations.

Based on the official MoES/NCHE weighting system (2019/2020) which applies
to all Ugandan universities including KIU.

Grading: A=6, B=5, C=4, D=3, E=2, O=1, F=0
Weights: Essential=3, Relevant=2, Desirable=1
"""

from typing import List, Tuple, Dict, Any

GRADE_POINTS = {
    'A': 6, 'B': 5, 'C': 4, 'D': 3, 'E': 2, 'O': 1, 'F': 0,
}

WEIGHTS = {'essential': 3, 'relevant': 2, 'desirable': 1}

O_LEVEL_WEIGHTS = {'distinction': 0.3, 'credit': 0.2, 'pass': 0.1}


def grade_to_points(grade: str) -> float:
    """Convert A-Level grade letter to points."""
    return GRADE_POINTS.get(grade.upper(), 0)


def compute_o_level_weight(distinctions: int, credits: int, passes: int) -> float:
    """Calculate O-Level weight contribution."""
    return (distinctions * O_LEVEL_WEIGHTS['distinction'] +
            credits     * O_LEVEL_WEIGHTS['credit'] +
            passes      * O_LEVEL_WEIGHTS['pass'])


def compute_subsidiary_bonus(gp_grade: str = None, sub_maths: bool = False, 
                             computer_studies: bool = False) -> float:
    """
    Calculate subsidiary subject bonus.
    General Paper pass, Subsidiary Mathematics pass, and Computer Studies pass
    each contribute +1 point to the A-Level score.
    """
    bonus = 0.0
    if gp_grade and gp_grade.upper() in ('D', 'C', 'P', '1', '2', '3'):
        bonus += 1.0
    if sub_maths:
        bonus += 1.0
    if computer_studies:
        bonus += 1.0
    return bonus


def compute_alevel_weight(subjects: List[Tuple[str, str]], programme) -> Tuple[float, List[Dict]]:
    """
    Compute the A-Level weighted score for a candidate for a given programme.

    subjects:   list of (subject_name, grade) tuples
    programme:  Programme model instance

    Returns: (weighted_score, breakdown_list)
    """
    essential_list  = [s.upper() for s in programme.get_essential_list()]
    relevant_list   = [s.upper() for s in programme.get_relevant_list()]
    essential_type  = programme.essential_type  # 'specific' or 'any_two'

    if not essential_list and not relevant_list:
        return 0.0, []

    # Normalise candidate subjects
    candidate = [(s.strip().upper(), g.strip().upper()) for s, g in subjects if s and g]

    assigned = []   # (subject, grade, category)

    if essential_type == 'any_two':
        sorted_cands = sorted(candidate, key=lambda x: grade_to_points(x[1]), reverse=True)
        for i, (subj, grade) in enumerate(sorted_cands):
            if i < 2:
                assigned.append((subj, grade, 'essential'))
            else:
                assigned.append((subj, grade, 'desirable'))
    else:
        essential_matched = []
        relevant_matched  = []
        desirable_matched = []

        for subj, grade in candidate:
            if subj in essential_list:
                essential_matched.append((subj, grade))
            elif subj in relevant_list:
                relevant_matched.append((subj, grade))
            else:
                desirable_matched.append((subj, grade))

        essential_matched.sort(key=lambda x: grade_to_points(x[1]), reverse=True)
        for i, (subj, grade) in enumerate(essential_matched):
            if i < 2:
                assigned.append((subj, grade, 'essential'))
            else:
                relevant_matched.append((subj, grade))

        relevant_matched.sort(key=lambda x: grade_to_points(x[1]), reverse=True)
        for subj, grade in relevant_matched[:1]:
            assigned.append((subj, grade, 'relevant'))

        for subj, grade in relevant_matched[1:]:
            assigned.append((subj, grade, 'desirable'))

        for subj, grade in desirable_matched:
            assigned.append((subj, grade, 'desirable'))

    weighted = assigned[:3]
    total_score = 0.0
    breakdown = []

    for subj, grade, category in weighted:
        pts = grade_to_points(grade)
        weight = WEIGHTS[category]
        contribution = pts * weight
        total_score += contribution
        breakdown.append({
            'subject': subj.title(),
            'grade': grade,
            'points': pts,
            'category': category.capitalize(),
            'weight': weight,
            'contribution': contribution,
        })

    return round(total_score, 2), breakdown


def check_eligibility(subjects: List[Tuple[str, str]], programme) -> Tuple[bool, str]:
    """
    Check if a candidate meets the minimum essential subject requirements.
    """
    if not subjects:
        return False, "No A-Level subjects provided."

    candidate_subjects = {
        s.strip().upper() for s, g in subjects
        if s and g and grade_to_points(g.strip().upper()) > 0
    }
    essential_list = [s.upper() for s in programme.get_essential_list()]
    essential_type = programme.essential_type

    if not essential_list:
        return True, "No specific essential subjects required."

    if essential_type == 'any_two':
        passed = [s for s, g in subjects if grade_to_points(g.strip().upper()) >= 2]
        if len(passed) < 2:
            return False, "Minimum 2 principal passes (grade E or above) required."
        return True, "Meets minimum requirements."

    missing = [s.title() for s in essential_list if s not in candidate_subjects]
    if missing:
        return False, f"Essential subject(s) not passed: {', '.join(missing)}."

    return True, "Meets essential subject requirements."


def recommend_programmes(alevel_subjects: List[Dict], olevel_summary: Dict, 
                         programmes: List, gp_grade: str = None,
                         sub_maths: bool = False, computer_studies: bool = False) -> List[Dict]:
    """
    Generate ranked programme recommendations for a student.
    
    Args:
        alevel_subjects: List of dicts with 'subject', 'grade', 'subjectType' keys
        olevel_summary: Dict with 'distinctions', 'credits', 'passes' keys
        programmes: List of Program model instances
        gp_grade: General Paper grade
        sub_maths: Subsidiary Mathematics pass
        computer_studies: Computer Studies pass
    
    Returns: list of dicts sorted by combined score descending
    """
    subjects = [(s.get('subject', ''), s.get('grade', '')) for s in alevel_subjects 
                if s.get('subjectType', '').lower() == 'principal']
    
    o_bonus = compute_o_level_weight(
        olevel_summary.get('distinctions', 0),
        olevel_summary.get('credits', 0),
        olevel_summary.get('passes', 0),
    )
    sub_bonus = compute_subsidiary_bonus(gp_grade, sub_maths, computer_studies)

    results = []
    for prog in programmes:
        if prog.level != 'degree':
            continue
            
        eligible, reason = check_eligibility(subjects, prog)
        alevel_score, breakdown = compute_alevel_weight(subjects, prog)
        
        combined_score = round(alevel_score + sub_bonus + o_bonus, 2)
        
        meets_minimum = combined_score >= prog.min_weighted_score if prog.min_weighted_score else True
        
        results.append({
            'programme': prog,
            'eligible': eligible and meets_minimum,
            'alevel_score': alevel_score,
            'sub_bonus': sub_bonus,
            'o_level_score': round(o_bonus, 2),
            'combined_score': combined_score,
            'breakdown': breakdown,
            'eligibility_reason': reason,
            'meets_minimum_score': meets_minimum,
        })

    results.sort(key=lambda x: (not x['eligible'], -x['combined_score']))
    return results
