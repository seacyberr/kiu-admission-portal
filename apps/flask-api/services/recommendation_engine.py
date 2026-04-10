"""
Unified Recommendation Engine for KIU Admission Portal
Handles all Uganda education pathways:
- O-Level only → Certificate → HEC → Degree
- A-Level direct → Bachelor/Diploma/HEC
- Diploma holders → Bachelor
- HEC completers → Bachelor
- Previous degree holders → Masters/PhD

Maps actual KIU program structure with proper NCHE requirements
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from services.qualification_service import (
    UgandaQualificationService,
    EntryPathway,
    HECTrack
)
from services.kiu_programs_database import ALL_KIU_PROGRAMS, KIU_PROGRAMS_DB, HEC_PROGRAMS, NATIONAL_CERTIFICATE_PROGRAMS


@dataclass
class ProgramRecommendation:
    program_id: str
    program_code: str
    program_name: str
    faculty: str
    campus: List[str]
    duration_years: int
    tuition_ugx_per_semester: int
    is_eligible: bool
    is_strong_candidate: bool
    match_score: int  # 0-100
    match_reasons: List[str]
    warnings: List[str]
    required_subjects_met: List[str]
    required_subjects_missing: List[str]
    cutoff_points: int
    applicant_points: int
    apply_url: str


# KIU Actual Program Structure from database
# Uses imported ALL_KIU_PROGRAMS from kiu_programs_database.py
# 2025/2026 Tuition fees per semester

KIU_PROGRAMS = ALL_KIU_PROGRAMS

# Keep for backward compatibility - reference to actual database
KIU_PROGRAMS_LEGACY = {
    # Faculty of Clinical Medicine and Dentistry
    "MBChB": {
        "name": "Bachelor of Medicine and Bachelor of Surgery",
        "faculty": "Faculty of Clinical Medicine and Dentistry",
        "campus": ["Main Campus", "Western Campus"],
        "duration": 5,
        "tuition_ugx": 6_500_000,
        "level": "bachelor",
        "requirements": {
            "essential": ["Biology", "Chemistry"],
            "relevant": ["Physics", "Mathematics"],
            "minimum_points": 15,
            "cutoff_points": 16,
            "min_principal_passes": 2
        },
        "hec_track": HECTrack.BIOLOGICAL,
        "career_paths": ["Medical Officer", "Surgeon", "Specialist"]
    },
    "BDS": {
        "name": "Bachelor of Dental Surgery",
        "faculty": "Faculty of Clinical Medicine and Dentistry",
        "campus": ["Main Campus"],
        "duration": 4,
        "tuition_ugx": 5_500_000,
        "level": "bachelor",
        "requirements": {
            "essential": ["Biology", "Chemistry"],
            "relevant": ["Physics"],
            "minimum_points": 13,
            "cutoff_points": 14,
            "min_principal_passes": 2
        },
        "hec_track": HECTrack.BIOLOGICAL,
        "career_paths": ["Dentist", "Dental Surgeon", "Oral Health Specialist"]
    },

    # Faculty of Biomedical Sciences
    "BPharm": {
        "name": "Bachelor of Pharmacy",
        "faculty": "Faculty of Biomedical Sciences",
        "campus": ["Main Campus"],
        "duration": 4,
        "tuition_ugx": 4_200_000,
        "level": "bachelor",
        "requirements": {
            "essential": ["Chemistry", "Biology"],
            "relevant": ["Physics", "Mathematics"],
            "minimum_points": 12,
            "cutoff_points": 14,
            "min_principal_passes": 2
        },
        "hec_track": HECTrack.BIOLOGICAL,
        "career_paths": ["Pharmacist", "Clinical Pharmacist", "Drug Inspector"]
    },
    "BNSc": {
        "name": "Bachelor of Nursing Science",
        "faculty": "Faculty of Biomedical Sciences",
        "campus": ["Main Campus", "Western Campus"],
        "duration": 4,
        "tuition_ugx": 3_800_000,
        "level": "bachelor",
        "requirements": {
            "essential": ["Biology"],
            "relevant": ["Chemistry", "Physics", "Mathematics"],
            "minimum_points": 10,
            "cutoff_points": 12,
            "min_principal_passes": 1
        },
        "hec_track": HECTrack.BIOLOGICAL,
        "career_paths": ["Registered Nurse", "Nurse Practitioner", "Nursing Manager"]
    },
    "BMLS": {
        "name": "Bachelor of Medical Laboratory Science",
        "faculty": "Faculty of Biomedical Sciences",
        "campus": ["Western Campus"],
        "duration": 4,
        "tuition_ugx": 3_500_000,
        "level": "bachelor",
        "requirements": {
            "essential": ["Biology", "Chemistry"],
            "relevant": ["Physics", "Mathematics"],
            "minimum_points": 10,
            "cutoff_points": 12,
            "min_principal_passes": 2
        },
        "hec_track": HECTrack.BIOLOGICAL,
        "career_paths": ["Medical Lab Scientist", "Lab Manager", "Research Scientist"]
    },

    # School of Public Health
    "BPH": {
        "name": "Bachelor of Public Health",
        "faculty": "School of Public Health",
        "campus": ["Main Campus"],
        "duration": 3,
        "tuition_ugx": 2_800_000,
        "level": "bachelor",
        "requirements": {
            "essential": ["Biology"],
            "relevant": ["Chemistry", "Physics", "Mathematics", "Geography"],
            "minimum_points": 8,
            "cutoff_points": 10,
            "min_principal_passes": 2
        },
        "hec_track": HECTrack.BIOLOGICAL,
        "career_paths": ["Public Health Officer", "Epidemiologist", "Health Educator"]
    },

    # School of Law
    "LLB": {
        "name": "Bachelor of Laws",
        "faculty": "School of Law",
        "campus": ["Main Campus", "Western Campus"],
        "duration": 4,
        "tuition_ugx": 2_800_000,
        "level": "bachelor",
        "requirements": {
            "essential": [],
            "relevant": ["History", "Literature", "Geography", "Economics", "Divinity"],
            "desirable": ["English"],
            "minimum_points": 10,
            "cutoff_points": 11,
            "min_principal_passes": 2,
            "general_paper_required": True
        },
        "hec_track": HECTrack.ARTS,
        "career_paths": ["Lawyer", "Judge", "Legal Advisor", "Company Secretary"]
    },

    # School of Engineering and Applied Sciences
    "BSE": {
        "name": "Bachelor of Science in Civil Engineering",
        "faculty": "School of Engineering and Applied Sciences",
        "campus": ["Main Campus"],
        "duration": 4,
        "tuition_ugx": 3_500_000,
        "level": "bachelor",
        "requirements": {
            "essential": ["Mathematics", "Physics"],
            "relevant": ["Chemistry", "Technical Drawing"],
            "minimum_points": 12,
            "cutoff_points": 13,
            "min_principal_passes": 2
        },
        "hec_track": HECTrack.PHYSICAL,
        "career_paths": ["Civil Engineer", "Structural Engineer", "Project Manager"]
    },
    "BEE": {
        "name": "Bachelor of Science in Electrical Engineering",
        "faculty": "School of Engineering and Applied Sciences",
        "campus": ["Main Campus"],
        "duration": 4,
        "tuition_ugx": 3_500_000,
        "level": "bachelor",
        "requirements": {
            "essential": ["Mathematics", "Physics"],
            "relevant": ["Chemistry"],
            "minimum_points": 12,
            "cutoff_points": 13,
            "min_principal_passes": 2
        },
        "hec_track": HECTrack.PHYSICAL,
        "career_paths": ["Electrical Engineer", "Power Systems Engineer", "Telecom Engineer"]
    },
    "BME": {
        "name": "Bachelor of Science in Mechanical Engineering",
        "faculty": "School of Engineering and Applied Sciences",
        "campus": ["Main Campus"],
        "duration": 4,
        "tuition_ugx": 3_500_000,
        "level": "bachelor",
        "requirements": {
            "essential": ["Mathematics", "Physics"],
            "relevant": ["Chemistry", "Technical Drawing"],
            "minimum_points": 12,
            "cutoff_points": 13,
            "min_principal_passes": 2
        },
        "hec_track": HECTrack.PHYSICAL,
        "career_paths": ["Mechanical Engineer", "Manufacturing Engineer", "Design Engineer"]
    },

    # School of Mathematics and Computing
    "BCS": {
        "name": "Bachelor of Computer Science",
        "faculty": "School of Mathematics and Computing",
        "campus": ["Main Campus", "Western Campus"],
        "duration": 3,
        "tuition_ugx": 2_600_000,
        "level": "bachelor",
        "requirements": {
            "essential": ["Mathematics"],
            "relevant": ["Physics", "Computer Studies", "Economics"],
            "minimum_points": 10,
            "cutoff_points": 10,
            "min_principal_passes": 2
        },
        "hec_track": HECTrack.PHYSICAL,
        "career_paths": ["Software Developer", "Systems Analyst", "Data Scientist"]
    },
    "BIT": {
        "name": "Bachelor of Information Technology",
        "faculty": "School of Mathematics and Computing",
        "campus": ["Main Campus", "Western Campus"],
        "duration": 3,
        "tuition_ugx": 2_400_000,
        "level": "bachelor",
        "requirements": {
            "essential": ["Mathematics"],
            "relevant": ["Computer Studies", "Physics"],
            "minimum_points": 8,
            "cutoff_points": 8,
            "min_principal_passes": 1
        },
        "hec_track": HECTrack.PHYSICAL,
        "career_paths": ["IT Manager", "Network Administrator", "Database Administrator"]
    },

    # College of Economics and Management
    "BBA": {
        "name": "Bachelor of Business Administration",
        "faculty": "College of Economics and Management",
        "campus": ["Main Campus", "Western Campus"],
        "duration": 3,
        "tuition_ugx": 2_200_000,
        "level": "bachelor",
        "requirements": {
            "essential": [],
            "relevant": ["Economics", "Mathematics", "Business Studies"],
            "minimum_points": 8,
            "cutoff_points": 8,
            "min_principal_passes": 2
        },
        "hec_track": HECTrack.ARTS,
        "career_paths": ["Business Manager", "Marketing Manager", "Operations Manager"]
    },
    "BCom": {
        "name": "Bachelor of Commerce",
        "faculty": "College of Economics and Management",
        "campus": ["Main Campus", "Western Campus"],
        "duration": 3,
        "tuition_ugx": 2_200_000,
        "level": "bachelor",
        "requirements": {
            "essential": ["Mathematics"],
            "relevant": ["Economics", "Accounting"],
            "minimum_points": 8,
            "cutoff_points": 9,
            "min_principal_passes": 2
        },
        "hec_track": HECTrack.ARTS,
        "career_paths": ["Accountant", "Financial Analyst", "Auditor"]
    },
    "MBA": {
        "name": "Master of Business Administration",
        "faculty": "College of Economics and Management",
        "campus": ["Main Campus", "Western Campus"],
        "duration": 2,
        "tuition_ugx": 3_500_000,
        "level": "masters",
        "requirements": {
            "degree_required": True,
            "min_degree_class": "second_lower",
            "work_experience_years": 2
        },
        "career_paths": ["CEO", "Management Consultant", "Business Strategist"]
    },

    # Faculty of Education
    "BEd": {
        "name": "Bachelor of Education",
        "faculty": "Faculty of Education",
        "campus": ["Main Campus", "Western Campus"],
        "duration": 3,
        "tuition_ugx": 2_000_000,
        "level": "bachelor",
        "requirements": {
            "essential": [],
            "relevant": ["Any two teaching subjects"],
            "minimum_points": 8,
            "cutoff_points": 8,
            "min_principal_passes": 2
        },
        "hec_track": None,  # Any track can lead to Education
        "career_paths": ["Teacher", "Education Administrator", "Curriculum Developer"]
    },

    # College of Humanities and Social Sciences
    "BSW": {
        "name": "Bachelor of Social Work and Administration",
        "faculty": "College of Humanities and Social Sciences",
        "campus": ["Main Campus"],
        "duration": 3,
        "tuition_ugx": 2_000_000,
        "level": "bachelor",
        "requirements": {
            "essential": [],
            "relevant": ["History", "Geography", "Economics", "Literature"],
            "minimum_points": 8,
            "cutoff_points": 8,
            "min_principal_passes": 2
        },
        "hec_track": HECTrack.ARTS,
        "career_paths": ["Social Worker", "NGO Manager", "Community Development Officer"]
    },
    "BPA": {
        "name": "Bachelor of Public Administration",
        "faculty": "College of Humanities and Social Sciences",
        "campus": ["Main Campus"],
        "duration": 3,
        "tuition_ugx": 2_000_000,
        "level": "bachelor",
        "requirements": {
            "essential": [],
            "relevant": ["History", "Geography", "Economics"],
            "minimum_points": 8,
            "cutoff_points": 8,
            "min_principal_passes": 2
        },
        "hec_track": HECTrack.ARTS,
        "career_paths": ["Public Administrator", "Civil Servant", "Policy Analyst"]
    },

    # HEC Programs
    "HEC_ARTS": {
        "name": "Higher Education Certificate (Arts)",
        "faculty": "College of Education, Open and Distance Learning",
        "campus": ["Main Campus"],
        "duration": 1,  # 9 months
        "tuition_ugx": 1_500_000,
        "level": "hec",
        "hec_track": HECTrack.ARTS,
        "requirements": {
            "min_subsidiary_passes": 2,
            "min_principal_passes": 1,
            "minimum_points": 0  # HEC accepts lower grades
        },
        "progresses_to": ["BBA", "BCom", "LLB", "BEd", "BSW", "BPA"],
        "career_paths": ["Progress to Humanities/Social Science Degrees"]
    },
    "HEC_BIO": {
        "name": "Higher Education Certificate (Biological)",
        "faculty": "College of Education, Open and Distance Learning",
        "campus": ["Main Campus"],
        "duration": 1,
        "tuition_ugx": 1_500_000,
        "level": "hec",
        "hec_track": HECTrack.BIOLOGICAL,
        "requirements": {
            "min_subsidiary_passes": 2,
            "min_principal_passes": 1,
            "minimum_points": 0
        },
        "progresses_to": ["MBChB", "BDS", "BPharm", "BNSc", "BMLS", "BPH"],
        "career_paths": ["Progress to Health Sciences Degrees"]
    },
    "HEC_PHY": {
        "name": "Higher Education Certificate (Physical)",
        "faculty": "College of Education, Open and Distance Learning",
        "campus": ["Main Campus"],
        "duration": 1,
        "tuition_ugx": 1_500_000,
        "level": "hec",
        "hec_track": HECTrack.PHYSICAL,
        "requirements": {
            "min_subsidiary_passes": 2,
            "min_principal_passes": 1,
            "minimum_points": 0
        },
        "progresses_to": ["BSE", "BEE", "BME", "BCS", "BIT"],
        "career_paths": ["Progress to Engineering/Technology Degrees"]
    },

    # Diploma Programs
    "DIP_BUSINESS": {
        "name": "Diploma in Business Administration",
        "faculty": "College of Economics and Management",
        "campus": ["Main Campus", "Western Campus"],
        "duration": 2,
        "tuition_ugx": 1_800_000,
        "level": "diploma",
        "requirements": {
            "min_principal_passes": 1,
            "min_subsidiary_passes": 2,
            "minimum_points": 0
        },
        "progresses_to": ["BBA", "BCom", "MBA"],
        "career_paths": ["Business Officer", "Admin Assistant", "Progress to Degree"]
    },
    "DIP_CS": {
        "name": "Diploma in Computer Science",
        "faculty": "School of Mathematics and Computing",
        "campus": ["Main Campus"],
        "duration": 2,
        "tuition_ugx": 1_800_000,
        "level": "diploma",
        "requirements": {
            "min_principal_passes": 1,
            "min_subsidiary_passes": 2,
            "minimum_points": 0
        },
        "progresses_to": ["BCS", "BIT"],
        "career_paths": ["IT Technician", "Programmer", "Progress to Degree"]
    },

    # National Certificate Programs (TVET Level 2-3)
    "NATCERT_BUSINESS": {
        "name": "National Certificate in Business Administration",
        "faculty": "College of Economics and Management",
        "campus": ["Main Campus", "Western Campus"],
        "duration": 1,
        "tuition_ugx": 900_000,
        "level": "national_certificate",
        "requirements": {
            "min_olevel_passes": 3,
            "subjects": [],
            "minimum_points": 0
        },
        "progresses_to": ["DIP_BUSINESS", "BBA", "BCom"],
        "career_paths": ["Business Assistant", "Office Admin", "Progress to Diploma"]
    },
    "NATCERT_IT": {
        "name": "National Certificate in Information Technology",
        "faculty": "School of Mathematics and Computing",
        "campus": ["Main Campus"],
        "duration": 1,
        "tuition_ugx": 950_000,
        "level": "national_certificate",
        "requirements": {
            "min_olevel_passes": 3,
            "subjects": ["Mathematics"],
            "minimum_points": 0
        },
        "progresses_to": ["DIP_CS", "BIT"],
        "career_paths": ["IT Support", "Computer Operator", "Progress to Diploma"]
    },
    "NATCERT_AGRIC": {
        "name": "National Certificate in Agriculture",
        "faculty": "School of Natural and Applied Sciences",
        "campus": ["Western Campus"],
        "duration": 1,
        "tuition_ugx": 850_000,
        "level": "national_certificate",
        "requirements": {
            "min_olevel_passes": 3,
            "subjects": ["Biology", "Agriculture"],
            "minimum_points": 0
        },
        "progresses_to": ["DIP_AGRIC", "BSc-AGRIC"],
        "career_paths": ["Agricultural Assistant", "Farm Manager", "Progress to Diploma"]
    },
    "NATCERT_EDUC": {
        "name": "National Certificate in Primary Education",
        "faculty": "Faculty of Education",
        "campus": ["Main Campus", "Western Campus"],
        "duration": 2,
        "tuition_ugx": 800_000,
        "level": "national_certificate",
        "requirements": {
            "min_olevel_passes": 4,
            "subjects": ["English", "Mathematics"],
            "minimum_points": 0
        },
        "progresses_to": ["DIP_EDUC", "BEd"],
        "career_paths": ["Primary Teacher", "Teacher Assistant", "Progress to Diploma"]
    },
}


class RecommendationEngine:
    """
    Main recommendation engine that ties qualification assessment to program matching
    """

    def __init__(self):
        self.qualification_service = UgandaQualificationService()

    def get_recommendations(
        self,
        highest_education: str = None,
        olevel_grades: List[Dict] = None,
        alevel_grades: List[Dict] = None,
        national_certificate_info: Dict = None,
        hec_info: Dict = None,
        diploma_info: Dict = None,
        degree_info: Dict = None,
        masters_info: Dict = None,
        olevel_curriculum: str = "old",
        alevel_curriculum: str = "old",
        preferred_campus: str = None,
        target_level: str = None
    ) -> Dict:
        """
        Get personalized program recommendations based on qualifications
        """

        # First, assess qualifications
        qualification_result = self.qualification_service.full_qualification_assessment(
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
            target_program_level=target_level or "bachelor"
        )

        recommendations = []

        # Get what levels the applicant can apply for
        can_apply_for = qualification_result.get("apply_for_levels", [])

        # Determine which programs to recommend based on qualifications

        # 1. O-Level Only or National Certificate - recommend certificate programs
        if "national_certificate" in can_apply_for or "certificate" in can_apply_for:
            if olevel_grades:
                olevel_result = qualification_result.get("olevel", {})
                if olevel_result.get("eligible"):
                    for code, program in KIU_PROGRAMS.items():
                        if program["level"] != "national_certificate":
                            continue

                        if preferred_campus and preferred_campus not in program["campus"]:
                            continue

                        # Check O-Level passes requirement
                        min_passes = program["requirements"].get("min_olevel_passes", 3)
                        if olevel_result.get("total_passes", 0) >= min_passes:
                            recommendation = ProgramRecommendation(
                                program_id=code.lower(),
                                program_code=code,
                                program_name=program["name"],
                                faculty=program["faculty"],
                                campus=program["campus"],
                                duration_years=program["duration"],
                                tuition_ugx_per_semester=program["tuition_ugx"],
                                is_eligible=True,
                                is_strong_candidate=True,
                                match_score=90,
                                match_reasons=[f"Eligible with {olevel_result.get('total_passes')} O-Level passes"],
                                warnings=[],
                                required_subjects_met=[],
                                required_subjects_missing=[],
                                cutoff_points=0,
                                applicant_points=0,
                                apply_url=f"/apply/certificate?program={code.lower()}&qualification=olevel"
                            )
                            recommendations.append(recommendation)

        # 2. A-Level qualifications
        if qualification_result["alevel"]:
            alevel_assessment = qualification_result["alevel"]

            for code, program in KIU_PROGRAMS.items():
                # Skip if campus filter doesn't match
                if preferred_campus and preferred_campus not in program["campus"]:
                    continue

                # Check if program level matches available pathways
                if program["level"] == "hec" and EntryPathway.HEC.value not in alevel_assessment["pathways"]:
                    continue
                if program["level"] == "diploma" and EntryPathway.DIPLOMA.value not in alevel_assessment["pathways"]:
                    continue
                if program["level"] == "bachelor" and EntryPathway.BACHELOR_DIRECT.value not in alevel_assessment["pathways"]:
                    # Check if they can enter via HEC or Diploma
                    if not (hec_info or diploma_info):
                        continue

                # Score the match
                score, reasons, warnings, subjects_met, subjects_missing = self._score_program_match(
                    program, alevel_assessment, olevel_grades or []
                )

                is_eligible = score >= 50
                is_strong = score >= 80

                recommendation = ProgramRecommendation(
                    program_id=code.lower(),
                    program_code=code,
                    program_name=program["name"],
                    faculty=program["faculty"],
                    campus=program["campus"],
                    duration_years=program["duration"],
                    tuition_ugx_per_semester=program["tuition_ugx"],
                    is_eligible=is_eligible,
                    is_strong_candidate=is_strong,
                    match_score=score,
                    match_reasons=reasons,
                    warnings=warnings,
                    required_subjects_met=subjects_met,
                    required_subjects_missing=subjects_missing,
                    cutoff_points=program["requirements"].get("cutoff_points", 0),
                    applicant_points=alevel_assessment["total_principal_points"],
                    apply_url=f"/apply/{program['level']}?program={code.lower()}&qualification=a_level"
                )

                recommendations.append(recommendation)

        elif hec_info:
            # HEC completer - show degree programs they can progress to
            hec_track = hec_info.get("track")

            for code, program in KIU_PROGRAMS.items():
                if program["level"] != "bachelor":
                    continue

                if preferred_campus and preferred_campus not in program["campus"]:
                    continue

                # Check if this program accepts this HEC track
                if program.get("hec_track") and program["hec_track"].value == hec_track:
                    recommendation = ProgramRecommendation(
                        program_id=code.lower(),
                        program_code=code,
                        program_name=program["name"],
                        faculty=program["faculty"],
                        campus=program["campus"],
                        duration_years=program["duration"],
                        tuition_ugx_per_semester=program["tuition_ugx"],
                        is_eligible=True,
                        is_strong_candidate=True,
                        match_score=85,
                        match_reasons=[f"Eligible via HEC {hec_track} completion"],
                        warnings=[],
                        required_subjects_met=[],
                        required_subjects_missing=[],
                        cutoff_points=program["requirements"].get("cutoff_points", 0),
                        applicant_points=0,
                        apply_url=f"/apply/degree?program={code.lower()}&qualification=hec"
                    )
                    recommendations.append(recommendation)

        elif diploma_info:
            # Diploma holder - show degree programs they can enter
            for code, program in KIU_PROGRAMS.items():
                if program["level"] != "bachelor":
                    continue

                if preferred_campus and preferred_campus not in program["campus"]:
                    continue

                # Check if diploma is relevant
                progresses_from = program.get("progresses_from", [])
                diploma_program = diploma_info.get("program", "").lower()

                is_relevant = any(diploma_program in p.lower() for p in progresses_from)

                recommendation = ProgramRecommendation(
                    program_id=code.lower(),
                    program_code=code,
                    program_name=program["name"],
                    faculty=program["faculty"],
                    campus=program["campus"],
                    duration_years=program["duration"],
                    tuition_ugx_per_semester=program["tuition_ugx"],
                    is_eligible=True,
                    is_strong_candidate=is_relevant,
                    match_score=90 if is_relevant else 70,
                    match_reasons=[f"Eligible via Diploma in {diploma_info.get('program')}"],
                    warnings=[] if is_relevant else ["Diploma may not be directly relevant"],
                    required_subjects_met=[],
                    required_subjects_missing=[],
                    cutoff_points=program["requirements"].get("cutoff_points", 0),
                    applicant_points=0,
                    apply_url=f"/apply/degree?program={code.lower()}&qualification=diploma"
                )
                recommendations.append(recommendation)

        # Sort by match score (descending)
        recommendations.sort(key=lambda x: x.match_score, reverse=True)

        return {
            "qualification_assessment": qualification_result,
            "recommendations": [self._recommendation_to_dict(r) for r in recommendations],
            "total_recommendations": len(recommendations),
            "eligible_recommendations": len([r for r in recommendations if r.is_eligible]),
            "strong_recommendations": len([r for r in recommendations if r.is_strong_candidate]),
            "curriculum_info": {
                "olevel_curriculum": olevel_curriculum,
                "alevel_curriculum": alevel_curriculum,
                "note": self._get_curriculum_note(olevel_curriculum, alevel_curriculum)
            }
        }

    def _score_program_match(
        self,
        program: Dict,
        alevel_assessment: Dict,
        olevel_grades: List[Dict]
    ) -> Tuple[int, List[str], List[str], List[str], List[str]]:
        """
        Score how well a student's qualifications match a program
        Returns: (score, reasons, warnings, subjects_met, subjects_missing)
        """
        score = 0
        reasons = []
        warnings = []
        subjects_met = []
        subjects_missing = []

        req = program["requirements"]
        principal_subjects = [s.lower() for s in alevel_assessment.get("passed_subjects", [])]
        points = alevel_assessment["total_principal_points"]

        # Check essential subjects
        essential_met = True
        for essential in req.get("essential", []):
            essential_lower = essential.lower()
            if any(essential_lower in ps for ps in principal_subjects):
                subjects_met.append(essential)
                score += 25
            else:
                subjects_missing.append(essential)
                essential_met = False

        if essential_met and req.get("essential"):
            reasons.append("All essential subjects met")

        # Check relevant subjects
        relevant_count = 0
        for relevant in req.get("relevant", []):
            relevant_lower = relevant.lower()
            if any(relevant_lower in ps for ps in principal_subjects):
                relevant_count += 1
                if relevant not in subjects_met:
                    subjects_met.append(relevant)
                score += 10

        if relevant_count > 0:
            reasons.append(f"{relevant_count} relevant subjects")

        # Check points requirement
        min_points = req.get("minimum_points", 0)
        if points >= min_points:
            score += 20
            reasons.append(f"Points requirement met ({points} >= {min_points})")
        else:
            warnings.append(f"Below minimum points: {points} < {min_points}")

        # Check cutoff (if applicable)
        cutoff = req.get("cutoff_points")
        if cutoff:
            if points >= cutoff:
                score += 15
                reasons.append(f"Above cutoff ({points} >= {cutoff})")
            else:
                warnings.append(f"Below historical cutoff: {points} < {cutoff}")

        # Check General Paper for Law
        if program["program_code"] == "LLB":
            if not alevel_assessment.get("has_general_paper"):
                warnings.append("Law programs strongly prefer General Paper")
                score -= 10
            else:
                reasons.append("General Paper present")
                score += 10

        # Cap score at 100
        score = min(100, max(0, score))

        return score, reasons, warnings, subjects_met, subjects_missing

    def _recommendation_to_dict(self, rec: ProgramRecommendation) -> Dict:
        """Convert recommendation to dictionary"""
        return {
            "programId": rec.program_id,
            "programCode": rec.program_code,
            "programName": rec.program_name,
            "faculty": rec.faculty,
            "campus": rec.campus,
            "durationYears": rec.duration_years,
            "tuitionUGXPerSemester": rec.tuition_ugx_per_semester,
            "isEligible": rec.is_eligible,
            "isStrongCandidate": rec.is_strong_candidate,
            "matchScore": rec.match_score,
            "matchReasons": rec.match_reasons,
            "warnings": rec.warnings,
            "requiredSubjectsMet": rec.required_subjects_met,
            "requiredSubjectsMissing": rec.required_subjects_missing,
            "cutoffPoints": rec.cutoff_points,
            "applicantPoints": rec.applicant_points,
            "applyUrl": rec.apply_url
        }

    def _get_curriculum_note(self, olevel: str, alevel: str) -> str:
        """Get explanatory note about curriculum"""
        if olevel == "new" or alevel == "new":
            return (
                "Using new curriculum grading system. "
                "A=B(6)=B(5)=C(4)=D(3)=E(2)=F(1)=O(1)=F(0)"
            )
        return "Using standard A-Level grading (A=6, B=5, C=4, D=3, E=2, O=1, F=0)"

    def compare_programs(self, program_codes: List[str]) -> Dict:
        """
        Compare multiple programs side by side
        """
        programs = []
        for code in program_codes:
            if code.upper() in KIU_PROGRAMS:
                prog = KIU_PROGRAMS[code.upper()]
                programs.append({
                    "code": code,
                    "name": prog["name"],
                    "faculty": prog["faculty"],
                    "campus": prog["campus"],
                    "duration": prog["duration"],
                    "tuition_ugx": prog["tuition_ugx"],
                    "requirements": prog["requirements"],
                    "career_paths": prog.get("career_paths", [])
                })

        return {
            "programs": programs,
            "comparison_fields": [
                "duration", "tuition", "requirements", "campus", "career_paths"
            ]
        }
