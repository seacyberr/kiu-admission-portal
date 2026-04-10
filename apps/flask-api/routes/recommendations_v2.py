"""
Unified Recommendations API v2
Handles both Old and New Uganda Curriculum
Supports all entry pathways: Direct, HEC, Diploma, Previous Degree
"""

from flask import Blueprint, request, jsonify
import logging
from services.recommendation_engine import RecommendationEngine

recommendations_v2_bp = Blueprint("recommendations_v2", __name__)
log = logging.getLogger(__name__)


@recommendations_v2_bp.route("/assess", methods=["POST"])
def assess_qualifications():
    """
    Main qualification assessment endpoint
    Supports all Uganda education levels and both old and new curriculum
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400

        # Extract highest education level (what they have)
        highest_education = data.get("highestEducation", "olevel")

        # Extract qualification data (what they have)
        olevel_grades = data.get("olevelGrades", [])
        alevel_grades = data.get("alevelGrades", [])
        national_certificate_info = data.get("nationalCertificateInfo")
        hec_info = data.get("hecInfo")
        diploma_info = data.get("diplomaInfo")
        degree_info = data.get("degreeInfo")
        masters_info = data.get("mastersInfo")

        # Curriculum versions (critical for 2024-2025 transition)
        olevel_curriculum = data.get("olevelCurriculum", "old")
        alevel_curriculum = data.get("alevelCurriculum", "old")

        # Preferences
        preferred_campus = data.get("preferredCampus")
        target_level = data.get("targetLevel")  # What they want to apply for

        # Validate curriculum values
        if olevel_curriculum not in ["old", "new"]:
            return jsonify({"error": "olevelCurriculum must be 'old' or 'new'"}), 400
        if alevel_curriculum not in ["old", "new"]:
            return jsonify({"error": "alevelCurriculum must be 'old' or 'new'"}), 400

        # Run recommendation engine
        engine = RecommendationEngine()
        result = engine.get_recommendations(
            highest_education=highest_education,
            olevel_grades=olevel_grades,
            alevel_grades=alevel_grades,
            national_certificate_info=national_certificate_info,
            hec_info=hec_info,
            diploma_info=diploma_info,
            degree_info=degree_info,
            masters_info=masters_info,
            olevel_curriculum=olevel_curriculum,
            alevel_curriculum=alevel_curriculum,
            preferred_campus=preferred_campus,
            target_level=target_level
        )

        return jsonify(result), 200

    except Exception as e:
        log.error(f"Error in qualification assessment: {e}")
        return jsonify({"error": "Assessment failed", "details": str(e)}), 500


@recommendations_v2_bp.route("/compare", methods=["POST"])
def compare_programs():
    """
    Compare multiple programs side by side
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400

        program_codes = data.get("programCodes", [])
        if len(program_codes) < 2:
            return jsonify({"error": "Provide at least 2 programs to compare"}), 400

        engine = RecommendationEngine()
        comparison = engine.compare_programs(program_codes)

        return jsonify(comparison), 200

    except Exception as e:
        log.error(f"Error comparing programs: {e}")
        return jsonify({"error": "Comparison failed", "details": str(e)}), 500


@recommendations_v2_bp.route("/curriculum-info", methods=["GET"])
def get_curriculum_info():
    """
    Get information about Uganda curriculum systems and all admission pathways
    """
    return jsonify({
        "uganda_curriculum_systems": {
            "old_olevel": {
                "name": "Old O-Level (UCE) - Pre-2024",
                "grades": ["D1", "D2", "C3", "C4", "C5", "C6", "P7", "P8", "F9"],
                "pass_grades": ["D1", "D2", "C3", "C4", "C5", "C6", "P7", "P8"],
                "minimum_passes": 5,
                "description": "Numerical grading system used before 2024"
            },
            "new_olevel": {
                "name": "New O-Level (UCE) - 2024+",
                "grades": ["A", "B", "C", "D", "E", "F"],
                "pass_grades": ["A", "B", "C", "D", "E"],
                "minimum_passes": 5,
                "description": "Letter grading system introduced 2024",
                "equivalence": {
                    "A": "D1/D2 (Old)",
                    "B": "C3/C4 (Old)",
                    "C": "C5/C6 (Old)",
                    "D": "P7/P8 (Old)",
                    "E": "F9 (Old)",
                    "F": "F9 (Old)"
                }
            },
            "alevel": {
                "name": "A-Level (UACE)",
                "note": "Grading unchanged across curriculums",
                "principal_grades": {
                    "A": 6, "B": 5, "C": 4, "D": 3, "E": 2
                },
                "subsidiary_grades": {
                    "O": 1
                },
                "fail": "F",
                "minimum_for_bachelor": "2 principal passes OR 1 principal + 2 subsidiaries",
                "minimum_for_diploma": "1 principal pass + 2 subsidiaries",
                "minimum_for_hec": "2 subsidiary passes OR 1 principal pass"
            }
        },
        "education_levels": {
            "what_you_have": [
                {"level": "phd", "name": "PhD (Doctorate)", "duration": "3-5 years"},
                {"level": "masters", "name": "Masters Degree", "duration": "1.5-2 years"},
                {"level": "bachelor", "name": "Bachelor Degree", "duration": "3-5 years"},
                {"level": "diploma", "name": "Diploma", "duration": "2 years"},
                {"level": "hec", "name": "Higher Education Certificate", "duration": "9-12 months"},
                {"level": "national_certificate", "name": "National Certificate (TVET)", "duration": "1-2 years"},
                {"level": "alevel", "name": "A-Level (UACE)", "duration": "2 years"},
                {"level": "olevel", "name": "O-Level (UCE)", "duration": "4 years"}
            ],
            "what_you_can_apply_for": [
                {"level": "national_certificate", "entry": "O-Level with 3-4 passes", "leads_to": "Diploma"},
                {"level": "hec", "entry": "A-Level with 2 subsidiaries OR 1 principal", "leads_to": "Bachelor"},
                {"level": "diploma", "entry": "A-Level with 1P+2S OR National Cert", "leads_to": "Bachelor"},
                {"level": "bachelor", "entry": "A-Level with 2 principals OR HEC/Diploma", "leads_to": "Masters"},
                {"level": "masters", "entry": "Bachelor degree (2nd class lower+)", "leads_to": "PhD"},
                {"level": "phd", "entry": "Masters degree", "leads_to": "Postdoc/Academia"}
            ]
        },
        "admission_pathway_matrix": {
            "headers": ["Have → Apply", "National Cert", "HEC", "Diploma", "Bachelor", "Masters", "PhD"],
            "rows": [
                {"have": "O-Level Only", "national_cert": "Yes", "hec": "No", "diploma": "No", "bachelor": "No", "masters": "No", "phd": "No"},
                {"have": "National Cert", "national_cert": "Yes (upgrade)", "hec": "Yes", "diploma": "Yes", "bachelor": "No", "masters": "No", "phd": "No"},
                {"have": "A-Level (2 Subs only)", "national_cert": "Yes", "hec": "Yes", "diploma": "No", "bachelor": "No", "masters": "No", "phd": "No"},
                {"have": "A-Level (1P + 2S)", "national_cert": "Yes", "hec": "Yes", "diploma": "Yes", "bachelor": "No", "masters": "No", "phd": "No"},
                {"have": "A-Level (2 Principal)", "national_cert": "Yes", "hec": "Yes", "diploma": "Yes", "bachelor": "Yes", "masters": "No", "phd": "No"},
                {"have": "HEC Completed", "national_cert": "No", "hec": "No", "diploma": "No", "bachelor": "Yes", "masters": "No", "phd": "No"},
                {"have": "Diploma (Credit/Dist)", "national_cert": "No", "hec": "No", "diploma": "Yes (higher)", "bachelor": "Yes", "masters": "No", "phd": "No"},
                {"have": "Bachelor", "national_cert": "No", "hec": "No", "diploma": "No", "bachelor": "Yes (2nd degree)", "masters": "Yes", "phd": "No"},
                {"have": "Masters", "national_cert": "No", "hec": "No", "diploma": "No", "bachelor": "No", "masters": "No", "phd": "Yes"}
            ]
        },
        "entry_pathways": {
            "national_certificate": {
                "requirements": "O-Level with 3-4 passes",
                "duration": "1-2 years",
                "progression": "National Certificate → Diploma → Bachelor",
                "awarding_bodies": ["DIT", "UBTEB"]
            },
            "hec": {
                "requirements": "A-Level with 2 subsidiaries OR 1 principal pass",
                "tracks": ["Arts", "Biological", "Physical"],
                "duration": "9-12 months",
                "progression": "HEC → Bachelor (direct progression)"
            },
            "diploma": {
                "requirements": "A-Level with 1 principal + 2 subsidiaries OR National Certificate",
                "duration": "2 years",
                "classes": ["Distinction", "Credit", "Pass"],
                "progression": "Diploma → Bachelor (with credit transfer)"
            },
            "bachelor_direct": {
                "requirements": "A-Level with 2 principal passes (minimum 6 points)",
                "duration": "3-5 years",
                "subject_requirements": "Varies by program (Biology/Chemistry for Medicine, Math/Physics for Engineering)"
            },
            "masters": {
                "requirements": "Bachelor Degree (Second Class Lower or above)",
                "duration": "1.5-2 years",
                "types": ["Taught", "Research", "Professional"]
            },
            "phd": {
                "requirements": "Masters Degree",
                "duration": "3-5 years",
                "requirements_extra": ["Research proposal", "Supervisor acceptance", "Publications (for competitive programs)"]
            }
        },
        "hec_tracks": {
            "arts": {
                "name": "Higher Education Certificate (Arts)",
                "prepares_for": ["Humanities", "Social Sciences", "Business", "Law"],
                "progresses_to": ["LLB", "BBA", "BCom", "BSW", "BPA", "BEd"]
            },
            "biological": {
                "name": "Higher Education Certificate (Biological)",
                "prepares_for": ["Health Sciences", "Agriculture", "Environment"],
                "progresses_to": ["MBChB", "BNSc", "BPharm", "BMLS", "BDS", "BPH"]
            },
            "physical": {
                "name": "Higher Education Certificate (Physical)",
                "prepares_for": ["Engineering", "Technology", "Physical Sciences"],
                "progresses_to": ["BSE", "BEE", "BME", "BCS", "BIT", "BSc"]
            }
        }
    }), 200


@recommendations_v2_bp.route("/programs", methods=["GET"])
def list_programs():
    """
    List all KIU programs with requirements
    """
    from services.recommendation_engine import KIU_PROGRAMS

    level_filter = request.args.get("level")
    faculty_filter = request.args.get("faculty")
    campus_filter = request.args.get("campus")

    programs = []
    for code, prog in KIU_PROGRAMS.items():
        # Apply filters
        if level_filter and prog["level"] != level_filter:
            continue
        if faculty_filter and faculty_filter.lower() not in prog["faculty"].lower():
            continue
        if campus_filter and campus_filter not in prog["campus"]:
            continue

        programs.append({
            "code": code,
            "name": prog["name"],
            "faculty": prog["faculty"],
            "campus": prog["campus"],
            "duration_years": prog["duration"],
            "tuition_ugx_per_semester": prog["tuition_ugx"],
            "level": prog["level"],
            "requirements": prog["requirements"],
            "career_paths": prog.get("career_paths", [])
        })

    return jsonify({
        "programs": programs,
        "total": len(programs),
        "filters_applied": {
            "level": level_filter,
            "faculty": faculty_filter,
            "campus": campus_filter
        }
    }), 200


@recommendations_v2_bp.route("/program/<program_code>", methods=["GET"])
def get_program_details(program_code):
    """
    Get detailed information about a specific program
    """
    from services.recommendation_engine import KIU_PROGRAMS

    program_code = program_code.upper()
    if program_code not in KIU_PROGRAMS:
        return jsonify({"error": "Program not found"}), 404

    prog = KIU_PROGRAMS[program_code]

    return jsonify({
        "code": program_code,
        "name": prog["name"],
        "faculty": prog["faculty"],
        "campus": prog["campus"],
        "duration_years": prog["duration"],
        "tuition_ugx_per_semester": prog["tuition_ugx"],
        "level": prog["level"],
        "requirements": prog["requirements"],
        "hec_track": prog.get("hec_track").value if prog.get("hec_track") else None,
        "career_paths": prog.get("career_paths", []),
        "progresses_from": prog.get("progresses_from", []),
        "progresses_to": prog.get("progresses_to", [])
    }), 200
