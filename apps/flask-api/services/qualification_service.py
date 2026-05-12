"""
Unified Uganda Qualification Service
Handles both Old Curriculum (Pre-2024) and New Curriculum (2024+) for O-Level and A-Level
Implements NCHE Uganda entry requirements for all pathways:
- Direct Bachelor (A-Level with 2 principal passes)
- Diploma Entry (A-Level with 1 principal + 2 subsidiaries)
- HEC Entry (A-Level with 2 subsidiaries OR 1 principal)
- Diploma to Degree progression
- HEC to Degree progression
"""

from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from enum import Enum


class CurriculumVersion(Enum):
    OLD = "old"  # Pre-2024: D1-D2-C3-C4-C5-C6-P7-P8-F9
    NEW = "new"  # 2024+: A-B-C-D-E


class EntryPathway(Enum):
    BACHELOR_DIRECT = "bachelor_direct"
    DIPLOMA = "diploma"
    HEC = "hec"
    CERTIFICATE = "certificate"
    NATIONAL_CERTIFICATE = "national_certificate"
    MASTERS = "masters"
    PHD = "phd"
    NOT_ELIGIBLE = "not_eligible"


class HECTrack(Enum):
    ARTS = "arts"
    BIOLOGICAL = "biological"
    PHYSICAL = "physical"


@dataclass
class GradeResult:
    grade: str
    points: int
    is_pass: bool
    curriculum: str


@dataclass
class OLevelResult:
    subject: str
    grade: str
    points: int
    is_pass: bool


@dataclass
class ALevelResult:
    subject: str
    grade: str
    points: int
    subject_type: str  # "principal" or "subsidiary"
    is_pass: bool


@dataclass
class QualificationAssessment:
    eligible: bool
    pathways: List[EntryPathway]
    olevel_passes: int
    principal_passes: int
    subsidiary_passes: int
    total_principal_points: int
    has_general_paper: bool
    meets_bachelor_requirements: bool
    meets_diploma_requirements: bool
    meets_hec_requirements: bool
    requirements_met: List[str]
    requirements_missing: List[str]
    recommended_hec_track: Optional[HECTrack]
    warnings: List[str]


class UgandaQualificationService:
    """
    Unified service for assessing Uganda education qualifications
    Handles both old and new curriculum transitions
    """

    # OLD CURRICULUM: O-Level (UCE) - Pre-2024
    # D1 (best) to F9 (fail)
    OLEVEL_OLD_GRADES = {
        "D1": {"points": 1, "pass": True},
        "D2": {"points": 2, "pass": True},
        "C3": {"points": 3, "pass": True},
        "C4": {"points": 4, "pass": True},
        "C5": {"points": 5, "pass": True},
        "C6": {"points": 6, "pass": True},
        "P7": {"points": 7, "pass": True},
        "P8": {"points": 8, "pass": True},
        "F9": {"points": 9, "pass": False},
    }

    # NEW CURRICULUM: O-Level (UCE) - 2024+
    # A (best) to E (pass), F (fail)
    OLEVEL_NEW_GRADES = {
        "A": {"points": 1, "pass": True, "equivalent_old": "D1/D2"},
        "B": {"points": 2, "pass": True, "equivalent_old": "C3/C4"},
        "C": {"points": 3, "pass": True, "equivalent_old": "C5/C6"},
        "D": {"points": 4, "pass": True, "equivalent_old": "P7/P8"},
        "E": {"points": 5, "pass": True, "equivalent_old": "F9"},
        "F": {"points": 6, "pass": False, "equivalent_old": "F9"},
    }

    # A-Level (UACE) - Unchanged across curriculums
    # A=6, B=5, C=4, D=3, E=2, O=1, F=0
    ALEVEL_GRADES = {
        "A": {"points": 6, "pass": True},
        "B": {"points": 5, "pass": True},
        "C": {"points": 4, "pass": True},
        "D": {"points": 3, "pass": True},
        "E": {"points": 2, "pass": True},
        "O": {"points": 1, "pass": False},  # Subsidiary pass only
        "F": {"points": 0, "pass": False},
    }

    # HEC Track Subject Mappings (from NCHE guidelines)
    HEC_ARTS_SUBJECTS = [
        "history", "geography", "economics", "literature", "divinity",
        "christian religious education", "islamic religious education",
        "fine art", "music", "languages"
    ]

    HEC_BIOLOGICAL_SUBJECTS = [
        "biology", "agriculture", "chemistry"
    ]

    HEC_PHYSICAL_SUBJECTS = [
        "mathematics", "physics", "technical drawing", "computer studies",
        "information technology"
    ]

    @staticmethod
    def normalize_grade(grade: str, curriculum: str = "old") -> Tuple[str, int, bool]:
        """
        Normalize any grade to standard format
        Returns: (normalized_grade, points, is_pass)
        """
        grade = grade.upper().strip()

        if curriculum == "new":
            # Handle new curriculum O-Level grades (A-E)
            if grade in UgandaQualificationService.OLEVEL_NEW_GRADES:
                info = UgandaQualificationService.OLEVEL_NEW_GRADES[grade]
                return grade, info["points"], info["pass"]
        else:
            # Handle old curriculum grades
            if grade in UgandaQualificationService.OLEVEL_OLD_GRADES:
                info = UgandaQualificationService.OLEVEL_OLD_GRADES[grade]
                return grade, info["points"], info["pass"]

        # A-Level grades (same in both curriculums)
        if grade in UgandaQualificationService.ALEVEL_GRADES:
            info = UgandaQualificationService.ALEVEL_GRADES[grade]
            return grade, info["points"], info["pass"]

        return grade, 0, False

    @staticmethod
    def convert_new_to_old_grade(new_grade: str) -> str:
        """Convert new curriculum grade to equivalent old curriculum grade"""
        conversion = {
            "A": "D1/D2",
            "B": "C3/C4",
            "C": "C5/C6",
            "D": "P7/P8",
            "E": "F9",
            "F": "F9",
        }
        return conversion.get(new_grade.upper(), new_grade)

    @staticmethod
    def assess_olevel(grades: List[Dict], curriculum: str = "old") -> Dict:
        """
        Assess O-Level (UCE) results
        Minimum requirement: 5 passes
        """
        passes = 0
        total_points = 0
        subject_results = []

        for grade_data in grades:
            subject = grade_data.get("subject", "")
            grade = grade_data.get("grade", "")

            normalized, points, is_pass = UgandaQualificationService.normalize_grade(
                grade, curriculum
            )

            subject_results.append({
                "subject": subject,
                "grade": grade,
                "normalized_grade": normalized,
                "points": points,
                "is_pass": is_pass,
                "curriculum": curriculum
            })

            if is_pass:
                passes += 1
            total_points += points

        # New curriculum: grades A, B, C, D, E are passes (5 grades)
        # Old curriculum: D1-C6 are passes (6 grades), P7-P8 are passes (2 grades)
        min_passes = 5

        # Special note: In new curriculum, P7/P8 equivalent is D grade which is still a pass
        # The only fail is F

        return {
            "eligible": passes >= min_passes,
            "total_passes": passes,
            "total_subjects": len(grades),
            "total_points": total_points,
            "subject_results": subject_results,
            "requirements_met": [f"{passes} O-Level passes"] if passes >= min_passes else [],
            "requirements_missing": (
                [f"Need {min_passes} passes, have {passes}"] if passes < min_passes else []
            ),
            "curriculum": curriculum
        }

    @staticmethod
    def assess_alevel(grades: List[Dict], curriculum: str = "old") -> Dict:
        """
        Assess A-Level (UACE) results
        Bachelor: 2 principal passes OR 1 principal + 2 subsidiaries
        Diploma: 1 principal pass + 2 subsidiaries
        HEC: 2 subsidiaries OR 1 principal pass
        """
        principal_passes = 0
        subsidiary_passes = 0
        total_principal_points = 0
        has_general_paper = False
        gp_grade = None

        passed_subjects = []

        for grade_data in grades:
            subject = grade_data.get("subject", "").lower()
            grade = grade_data.get("grade", "").upper()
            subject_type = grade_data.get("subjectType", "").lower()

            # Handle both old and new curriculum grading for A-Level
            # A-Level grading hasn't changed, but ensure compatibility
            if grade in UgandaQualificationService.ALEVEL_GRADES:
                info = UgandaQualificationService.ALEVEL_GRADES[grade]
                points = info["points"]
                is_pass = info["pass"]

                if subject_type == "principal":
                    if is_pass:  # A, B, C, D, E are principal passes
                        principal_passes += 1
                        total_principal_points += points
                        passed_subjects.append(subject)
                elif subject_type == "subsidiary":
                    if is_pass or grade == "O":  # O is subsidiary pass
                        subsidiary_passes += 1
                        passed_subjects.append(subject)

                    # Check for General Paper
                    if "general paper" in subject or subject == "gp":
                        has_general_paper = True
                        gp_grade = grade

        # Determine eligibility pathways
        pathways = []
        requirements_met = []
        requirements_missing = []
        warnings = []

        # NCHE Minimum for Bachelor: 2 principal passes
        # OR 1 principal + 2 subsidiaries
        meets_bachelor_direct = (
            principal_passes >= 2 or
            (principal_passes >= 1 and subsidiary_passes >= 2)
        )

        # NCHE Minimum for Diploma: 1 principal + 2 subsidiaries
        meets_diploma = principal_passes >= 1 and subsidiary_passes >= 2

        # NCHE Minimum for HEC: 2 subsidiaries OR 1 principal
        meets_hec = subsidiary_passes >= 2 or principal_passes >= 1

        if meets_bachelor_direct:
            pathways.append(EntryPathway.BACHELOR_DIRECT)
            requirements_met.append(
                f"Eligible for Bachelor: {principal_passes} principal passes, "
                f"{subsidiary_passes} subsidiary passes"
            )

        if meets_diploma:
            pathways.append(EntryPathway.DIPLOMA)
            requirements_met.append(
                f"Eligible for Diploma: {principal_passes}P + {subsidiary_passes}S"
            )

        if meets_hec:
            pathways.append(EntryPathway.HEC)
            requirements_met.append(
                f"Eligible for HEC: {subsidiary_passes} subsidiary passes"
            )

        # Check for General Paper requirement for Bachelor
        if meets_bachelor_direct and not has_general_paper:
            requirements_missing.append(
                "General Paper strongly recommended for Bachelor programs"
            )
            warnings.append("Some competitive programs may require General Paper")

        # Points requirement check for competitive programs
        if total_principal_points < 6 and principal_passes >= 2:
            warnings.append(
                f"Low principal points ({total_principal_points}). "
                "Competitive programs typically require 6+ points"
            )

        # Determine recommended HEC track based on subjects
        recommended_track = None
        if meets_hec and passed_subjects:
            biological_count = sum(
                1 for s in passed_subjects
                if any(bio in s for bio in UgandaQualificationService.HEC_BIOLOGICAL_SUBJECTS)
            )
            physical_count = sum(
                1 for s in passed_subjects
                if any(phy in s for phy in UgandaQualificationService.HEC_PHYSICAL_SUBJECTS)
            )
            arts_count = sum(
                1 for s in passed_subjects
                if any(art in s for art in UgandaQualificationService.HEC_ARTS_SUBJECTS)
            )

            # Recommend track with most matching subjects
            counts = {
                HECTrack.BIOLOGICAL: biological_count,
                HECTrack.PHYSICAL: physical_count,
                HECTrack.ARTS: arts_count
            }
            recommended_track = max(counts, key=counts.get)

        return {
            "eligible": len(pathways) > 0,
            "pathways": [p.value for p in pathways],
            "principal_passes": principal_passes,
            "subsidiary_passes": subsidiary_passes,
            "total_principal_points": total_principal_points,
            "has_general_paper": has_general_paper,
            "gp_grade": gp_grade,
            "meets_bachelor_requirements": meets_bachelor_direct,
            "meets_diploma_requirements": meets_diploma,
            "meets_hec_requirements": meets_hec,
            "requirements_met": requirements_met,
            "requirements_missing": requirements_missing,
            "recommended_hec_track": recommended_track.value if recommended_track else None,
            "warnings": warnings,
            "curriculum": curriculum
        }

    @staticmethod
    def assess_national_certificate(certificate_type: str, institution: str = None) -> Dict:
        """
        Assess National Certificate (TVET Level 2-3)
        Entry requirement: O-Level with 3-4 passes
        Can lead to: Diploma, HEC (if with experience), Certificate upgrade
        """
        eligible_for_progression = True

        cert_types = {
            "business": "Certificate in Business Administration",
            "it": "Certificate in Information Technology",
            "agriculture": "Certificate in Agriculture",
            "education_primary": "Certificate in Education (Primary)",
            "engineering": "Certificate in Engineering",
            "health": "Certificate in Health Sciences"
        }

        pathways = [EntryPathway.NATIONAL_CERTIFICATE.value]

        # National cert holders can apply for:
        # 1. Higher National Certificate / Diploma
        # 2. HEC (if they have work experience)
        # 3. Another certificate program (upgrade)

        return {
            "eligible": True,
            "certificate_type": certificate_type,
            "certificate_name": cert_types.get(certificate_type, certificate_type),
            "institution": institution,
            "eligible_for_diploma": True,
            "eligible_for_hec_with_experience": True,  # If 2+ years work experience
            "pathways": [p.value for p in pathways] + [EntryPathway.DIPLOMA.value, EntryPathway.HEC.value],
            "requirements_met": [f"Holds {cert_types.get(certificate_type, certificate_type)}"],
            "recommended_next": "Diploma in related field"
        }

    @staticmethod
    def assess_hec(track: str, gpa: float = None, completed: bool = True) -> Dict:
        """
        Assess HEC (Higher Education Certificate) results
        Tracks: arts, biological, physical
        """
        track_names = {
            "arts": "Higher Education Certificate (Arts)",
            "biological": "Higher Education Certificate (Biological)",
            "physical": "Higher Education Certificate (Physical)"
        }

        if not completed:
            return {
                "eligible": True,
                "status": "in_progress",
                "track": track,
                "track_name": track_names.get(track, track),
                "eligible_for_degree": False,
                "requirements_met": [f"Currently enrolled in {track_names.get(track, track)}"],
                "requirements_missing": ["HEC not yet completed"],
                "pathways": []
            }

        # HEC completion allows degree application
        return {
            "eligible": True,
            "status": "completed",
            "track": track,
            "track_name": track_names.get(track, track),
            "gpa": gpa,
            "eligible_for_degree": True,
            "requirements_met": [f"Completed {track_names.get(track, track)}"],
            "pathways": [EntryPathway.BACHELOR_DIRECT.value],
            "recommended_programs": UgandaQualificationService._get_hec_progression(track)
        }

    @staticmethod
    def _get_hec_progression(track: str) -> List[str]:
        """Get list of programs HEC track progresses to"""
        progressions = {
            "arts": ["LLB", "BBA", "BCom", "BSW", "BPA", "BEd"],
            "biological": ["MBChB", "BNSc", "BPharm", "BMLS", "BDS", "BPH"],
            "physical": ["BSE", "BEE", "BME", "BCS", "BIT", "BSc"]
        }
        return progressions.get(track, [])

    @staticmethod
    def assess_diploma(diploma_program: str, diploma_class: str) -> Dict:
        """
        Assess Diploma results for degree entry
        Classes: distinction, credit, pass
        """
        # Most universities accept Credit and above for direct degree entry
        # Pass may require additional requirements
        eligible_classes = ["distinction", "credit", "pass"]

        is_eligible = diploma_class.lower() in eligible_classes

        warnings = []
        if diploma_class.lower() == "pass":
            warnings.append(
                "Pass class diploma holders may need additional requirements "
                "for competitive degree programs"
            )

        return {
            "eligible": is_eligible,
            "diploma_class": diploma_class,
            "eligible_for_degree": is_eligible,
            "pathways": [EntryPathway.BACHELOR_DIRECT.value] if is_eligible else [],
            "requirements_met": [f"Diploma in {diploma_program} ({diploma_class})"],
            "warnings": warnings
        }

    @staticmethod
    def assess_previous_degree(
        degree_type: str,
        degree_class: str,
        gpa: float = None,
        target_program: str = "masters"
    ) -> Dict:
        """
        Assess previous degree for postgraduate entry
        """
        # Masters entry: minimum 2nd Class Lower or equivalent
        # PhD entry: Masters degree

        eligible_classes = ["first", "second_upper", "second_lower", "pass"]
        is_eligible = degree_class.lower() in eligible_classes

        if target_program == "phd":
            is_eligible = degree_type.lower() in ["masters", "mphil", "msc", "ma", "mba"]

        return {
            "eligible": is_eligible,
            "degree_type": degree_type,
            "degree_class": degree_class,
            "gpa": gpa,
            "requirements_met": [f"{degree_type} ({degree_class})"] if is_eligible else [],
            "requirements_missing": (
                [f"{degree_type} does not meet {target_program} requirements"]
                if not is_eligible else []
            )
        }

    @staticmethod
    def full_qualification_assessment(
        highest_education: str = None,
        olevel_grades: List[Dict] = None,
        alevel_grades: List[Dict] = None,
        national_certificate_info: Dict = None,
        hec_info: Dict = None,
        diploma_info: Dict = None,
        degree_info: Dict = None,
        masters_info: Dict = None,
        phd_info: Dict = None,
        olevel_curriculum: str = "old",
        alevel_curriculum: str = "old",
        target_program_level: str = "bachelor"
    ) -> Dict:
        """
        Comprehensive qualification assessment
        Determines all available entry pathways
        """
        result = {
            "highest_education": highest_education,
            "olevel": None,
            "alevel": None,
            "national_certificate": None,
            "hec": None,
            "diploma": None,
            "degree": None,
            "masters": None,
            "phd": None,
            "overall_eligible": False,
            "available_pathways": [],
            "recommended_pathway": None,
            "apply_for_levels": [],  # What they can apply for
            "warnings": [],
            "errors": []
        }

        # Assess based on highest education level

        # 1. O-Level Assessment
        if olevel_grades or highest_education in ["olevel", "o_level", "uce"]:
            if olevel_grades:
                result["olevel"] = UgandaQualificationService.assess_olevel(
                    olevel_grades, olevel_curriculum
                )
                if result["olevel"]["eligible"]:
                    # O-Level only -> Certificate programs
                    result["apply_for_levels"].append("national_certificate")
                    result["apply_for_levels"].append("certificate")

        # 2. National Certificate Assessment
        if national_certificate_info or highest_education == "national_certificate":
            if national_certificate_info:
                result["national_certificate"] = UgandaQualificationService.assess_national_certificate(
                    national_certificate_info.get("type"),
                    national_certificate_info.get("institution")
                )
                # National Cert -> Diploma, HEC (with experience)
                result["apply_for_levels"].extend(["national_certificate", "diploma", "hec"])

        # 3. A-Level Assessment
        if alevel_grades or highest_education in ["alevel", "a_level", "uace"]:
            if alevel_grades:
                result["alevel"] = UgandaQualificationService.assess_alevel(
                    alevel_grades, alevel_curriculum
                )
                alevel_result = result["alevel"]

                # Determine what A-Level qualifies for
                if alevel_result["meets_bachelor_requirements"]:
                    result["apply_for_levels"].extend(["bachelor", "diploma", "hec"])
                elif alevel_result["meets_diploma_requirements"]:
                    result["apply_for_levels"].extend(["diploma", "hec", "certificate"])
                elif alevel_result["meets_hec_requirements"]:
                    result["apply_for_levels"].extend(["hec", "certificate"])

                result["warnings"].extend(alevel_result.get("warnings", []))

        # 4. HEC Assessment
        if hec_info or highest_education == "hec":
            if hec_info:
                result["hec"] = UgandaQualificationService.assess_hec(
                    hec_info.get("track"),
                    hec_info.get("gpa"),
                    hec_info.get("completed", True)
                )
                if result["hec"]["eligible_for_degree"]:
                    result["apply_for_levels"].append("bachelor")
                else:
                    result["apply_for_levels"].append("hec")

        # 5. Diploma Assessment
        if diploma_info or highest_education == "diploma":
            if diploma_info:
                result["diploma"] = UgandaQualificationService.assess_diploma(
                    diploma_info.get("program"),
                    diploma_info.get("class")
                )
                if result["diploma"]["eligible_for_degree"]:
                    result["apply_for_levels"].append("bachelor")
                result["apply_for_levels"].append("diploma")

        # 6. Degree Assessment
        if degree_info or highest_education in ["bachelor", "degree", "bachelors"]:
            if degree_info:
                result["degree"] = UgandaQualificationService.assess_previous_degree(
                    "bachelors",
                    degree_info.get("class"),
                    degree_info.get("gpa"),
                    "masters"
                )
                if result["degree"]["eligible"]:
                    result["apply_for_levels"].extend(["masters", "bachelor_2nd_degree"])
                else:
                    result["apply_for_levels"].append("bachelor_2nd_degree")

        # 7. Masters Assessment
        if masters_info or highest_education in ["masters", "mba", "ma", "msc", "mphil"]:
            if masters_info:
                result["masters"] = UgandaQualificationService.assess_previous_degree(
                    "masters",
                    masters_info.get("class"),
                    masters_info.get("gpa"),
                    "phd"
                )
                if result["masters"]["eligible"]:
                    result["apply_for_levels"].append("phd")
                result["apply_for_levels"].append("masters_2nd")

        # 8. PhD Assessment
        if phd_info or highest_education in ["phd", "doctorate", "dphil"]:
            result["phd"] = {"eligible": True, "status": "completed"}
            result["apply_for_levels"].append("postdoc")

        # Remove duplicates while preserving order
        seen = set()
        result["apply_for_levels"] = [
            level for level in result["apply_for_levels"]
            if not (level in seen or seen.add(level))
        ]

        result["overall_eligible"] = len(result["apply_for_levels"]) > 0

        # Map apply_for_levels to pathways for compatibility
        level_to_pathway = {
            "national_certificate": EntryPathway.NATIONAL_CERTIFICATE.value,
            "certificate": EntryPathway.CERTIFICATE.value,
            "hec": EntryPathway.HEC.value,
            "diploma": EntryPathway.DIPLOMA.value,
            "bachelor": EntryPathway.BACHELOR_DIRECT.value,
            "bachelor_2nd_degree": EntryPathway.BACHELOR_DIRECT.value,
            "masters": EntryPathway.MASTERS.value,
            "phd": EntryPathway.PHD.value,
        }

        result["available_pathways"] = [
            level_to_pathway.get(level, level)
            for level in result["apply_for_levels"]
        ]

        # Recommend best pathway (prioritize higher levels)
        priority = ["phd", "masters", "bachelor", "diploma", "hec", "national_certificate", "certificate"]
        for level in priority:
            if level in result["apply_for_levels"]:
                result["recommended_pathway"] = level_to_pathway.get(level, level)
                result["recommended_apply_level"] = level
                break

        return result


# Legacy compatibility - maintain old class name
class UgandaQualificationChecker(UgandaQualificationService):
    """Backward compatibility alias"""
    pass
