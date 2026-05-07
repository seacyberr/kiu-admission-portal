"""
Uganda National Qualification Checker
Compliant with UHEQF Level 2-9 standards and NCHE guidelines
"""
from typing import Dict, List, Tuple, Optional

class QualificationResult:
    def __init__(self, eligible: bool, message: str = "", eligible_programs: List[str] = None):
        self.eligible = eligible
        self.message = message
        self.eligible_programs = eligible_programs or []
        self.requirements_met = []
        self.requirements_missing = []
    
    def to_dict(self):
        return {
            "eligible": self.eligible,
            "message": self.message,
            "eligiblePrograms": self.eligible_programs,
            "requirementsMet": self.requirements_met,
            "requirementsMissing": self.requirements_missing
        }


class UgandaQualificationChecker:
    """
    Validates student qualifications according to official NCHE/UHEQF standards
    """
    
    @staticmethod
    def validate_olevel(olevel_grades: List[Dict]) -> QualificationResult:
        """
        Validate O-Level (UCE) requirements: minimum 5 passes at same sitting
        """
        result = QualificationResult(False)
        
        if not olevel_grades or len(olevel_grades) == 0:
            result.requirements_missing.append("O-Level results not provided")
            result.message = "O-Level results are required"
            return result
        
        # Count valid passes (NCHE defines PASS as grades D1 to P8. F9 / F is FAIL)
        passes = 0
        total_points = 0
        
        for grade in olevel_grades:
            grade_val = grade.get('points', 9)
            total_points += grade_val
            # ONLY grades 1 through 8 are considered PASSES. Grade 9 is FAIL.
            if 1 <= grade_val <= 8:
                passes += 1
        
        result.requirements_met.append(f"Total subjects: {len(olevel_grades)}")
        result.requirements_met.append(f"Valid passes: {passes}")
        
        if passes >= 5:
            result.eligible = True
            result.requirements_met.append(f"Minimum 5 O-Level passes achieved ({passes} passes)")
            result.message = "O-Level requirements satisfied"
        else:
            result.requirements_missing.append(f"Requires minimum 5 O-Level passes, only {passes} passes obtained")
            result.message = "Insufficient O-Level passes"
        
        return result
    
    @staticmethod
    def validate_alevel(alevel_grades: List[Dict], required_subjects: List[str] = None, curriculum_version: str = "old") -> QualificationResult:
        """
        Validate A-Level (UACE) requirements for different pathways
        
        Standard Bachelor's Entry Requirements:
        - 2 Principal Passes OR 1 Principal + 2 Subsidiary Passes
        - In relevant subjects for the program
        
        Curriculum versions:
        - old: 2009-2024 (6 point scale: A=6, B=5, C=4, D=3, E=2, O=1, F=0)
        - new: 2025+ (9 point scale with competency assessment)
        """
        result = QualificationResult(False)
        
        if not alevel_grades or len(alevel_grades) == 0:
            result.requirements_missing.append("A-Level results not provided")
            result.message = "A-Level results are required"
            return result
            
        result.requirements_met.append(f"Curriculum: {curriculum_version.title()} Curriculum")
        
        principal_passes = 0
        subsidiary_passes = 0
        relevant_principal = 0
        relevant_subsidiary = 0
        passed_subjects = []
        
        for grade in alevel_grades:
            subject_type = grade.get('subjectType', '').lower()
            points = grade.get('points', 0)
            subject = grade.get('subject', '').lower()
            
            if subject_type == 'principal' and points >= 1:
                principal_passes += 1
                passed_subjects.append(subject)
                if required_subjects and subject in [s.lower() for s in required_subjects]:
                    relevant_principal += 1
            elif subject_type == 'subsidiary' and points >= 1:
                subsidiary_passes += 1
                passed_subjects.append(subject)
                if required_subjects and subject in [s.lower() for s in required_subjects]:
                    relevant_subsidiary += 1
        
        result.requirements_met.append(f"A-Level Results: {principal_passes} Principal Passes, {subsidiary_passes} Subsidiary Passes")
        
        # Check subject relevance if required subjects are specified
        meets_subject_requirements = True
        if required_subjects and len(required_subjects) > 0:
            if relevant_principal == 0:
                meets_subject_requirements = False
                result.requirements_missing.append(f"ERROR: Requires Principal Pass in at least one relevant subject: {', '.join(required_subjects)}")
            else:
                result.requirements_met.append(f"SUCCESS: Relevant subject requirements satisfied ({relevant_principal} relevant Principal passes)")
        
        # Calculate total principal points
        total_principal_points = sum(g.get('points', 0) for g in alevel_grades if g.get('subjectType', '').lower() == 'principal')
        has_general_paper = any(g.get('subject', '').lower() in ['general paper', 'gp'] for g in alevel_grades if g.get('subjectType', '').lower() == 'subsidiary')
        
        result.requirements_met.append(f"Total Principal Points: {total_principal_points}")
        
        # NCHE Minimum Requirements Validation - STRICTLY ONLY FOR DIRECT BACHELOR ENTRY
        # THESE REQUIREMENTS DO NOT APPLY TO HEC / DIPLOMA PATHWAYS
        has_minimum_bachelor_requirements = True
        
        minimum_points_required = 6 if curriculum_version == "old" else 7
        
        # Only check these requirements for Bachelor direct entry eligibility
        # HEC and Diploma pathways have their own separate requirements
        
        # Check qualification thresholds
        pathways = []
        
        # HEC Entry - 1 Principal OR 2 Subsidiary passes
        if principal_passes >= 1 or subsidiary_passes >= 2:
            result.requirements_met.append("Eligible for Higher Education Certificate (HEC) Program")
            pathways.append("hec")
        
        # Diploma Entry - 1 Principal + 2 Subsidiary passes
        if principal_passes >= 1 and subsidiary_passes >= 2:
            result.requirements_met.append("Eligible for Diploma Programs")
            pathways.append("diploma")
        
        # Direct Bachelor Entry - 2 Principal passes OR 1 Principal + 2 Subsidiaries
        # Must also meet relevant subject requirements, 6+ points AND General Paper
        # NCHE requirements APPLY ONLY HERE - STRICTLY for Direct Bachelor Entry ONLY
        if total_principal_points < minimum_points_required:
            result.requirements_missing.append(f"Minimum {minimum_points_required} Principal points required for Bachelor programs ({curriculum_version} curriculum). You have {total_principal_points} points")
            has_minimum_bachelor_requirements = False
        
        if not has_general_paper:
            result.requirements_missing.append("General Paper (GP) Subsidiary is required for Bachelor programs")
            has_minimum_bachelor_requirements = False

        meets_bachelor_requirements = (
            meets_subject_requirements 
            and has_minimum_bachelor_requirements
        )
        
        if meets_bachelor_requirements and principal_passes >= 2:
            result.requirements_met.append("Eligible for Direct Bachelor Degree Entry (2+ Principal Passes)")
            pathways.append("bachelor_direct")
        elif meets_bachelor_requirements and principal_passes >= 1 and subsidiary_passes >= 2:
            result.requirements_met.append("Eligible for Direct Bachelor Degree Entry (1 Principal + 2 Subsidiaries)")
            pathways.append("bachelor_direct")
        elif principal_passes < 2 and principal_passes >= 1:
            result.requirements_missing.append("With 1 Principal Pass you qualify for HEC / Diploma programs")
        elif principal_passes == 0 and subsidiary_passes >= 2:
            result.requirements_missing.append("With 2 Subsidiary passes you qualify for HEC program")
        
        if len(pathways) > 0:
            result.eligible = True
            result.eligible_programs = pathways
            result.message = f"Eligible for {len(pathways)} higher education pathways"
        else:
            result.requirements_missing.append("Does not meet minimum requirements for any higher education program")
            result.message = "A-Level results do not meet minimum entry requirements"
        
        return result
    
    @staticmethod
    def check_program_eligibility(program_level: str, 
                                   olevel_result: QualificationResult, 
                                   alevel_result: Optional[QualificationResult] = None,
                                   has_diploma: bool = False,
                                   has_hec: bool = False) -> Tuple[bool, str]:
        """
        Check eligibility for a specific program level
        """
        # O-Level is required for ALL programs at Certificate level and above
        if program_level not in ['phd', 'doctorate', 'master', 'masters', 'postgraduate']:
            if not olevel_result.eligible:
                return False, "O-Level requirements not met"
        
        program_level = program_level.lower().strip()
        
        # Diploma / Certificate Programs
        if program_level in ['certificate', 'diploma']:
            # Diplomas have their own independent entry requirements
            # No A-Level requirements are enforced for Diploma applicants
            if has_hec:
                return True, "Eligible via HEC entry route"
            if olevel_result.eligible:
                return True, "Eligible via O-Level entry route"
            
            # Diploma direct entry has separate requirements
            return False, "Does not meet Diploma entry requirements"
        
        # Bachelor Degree
        elif program_level in ['bachelor', 'degree', 'undergraduate']:
            if has_diploma:
                return True, "Eligible via Diploma entry route"
            if has_hec:
                return True, "Eligible via HEC entry route"
            if alevel_result and alevel_result.eligible and 'bachelor_direct' in alevel_result.eligible_programs:
                return True, "Eligible via Direct A-Level entry route"
            return False, "Does not meet Bachelor degree entry requirements"
        
        # Masters
        elif program_level in ['master', 'masters', 'postgraduate']:
            # Bachelor degree required for Masters
            return True, "Bachelor degree required for Masters entry (verified separately)"
        
        # PhD
        elif program_level in ['phd', 'doctorate']:
            # Masters degree required for PhD
            return True, "Masters degree required for PhD entry (verified separately)"
        
        return False, "Unknown program level"
    
    @staticmethod
    def get_recommended_pathways(olevel_grades: List[Dict], alevel_grades: List[Dict] = None, alevel_curriculum: str = "old") -> Dict:
        """
        Get recommended education pathways based on student qualifications
        Automatically determines highest eligible level and provides direct application links
        """
        olevel_result = UgandaQualificationChecker.validate_olevel(olevel_grades)
        
        result = {
            "olevel": olevel_result.to_dict(),
            "alevel": None,
            "curriculum": alevel_curriculum,
            "primaryRecommendation": None,
            "recommendedPathways": [],
            "availableApplicationLinks": [],
            "nextSteps": []
        }
        
        # Always provide minimum entry options
        all_available_paths = []
        
        if olevel_result.eligible:
            all_available_paths.append({
                "level": "certificate",
                "name": "Certificate Programs",
                "eligible": True,
                "applicationLink": "/apply/certificate"
            })
            
            all_available_paths.append({
                "level": "diploma",
                "name": "Diploma Programs",
                "eligible": True,
                "applicationLink": "/apply/diploma"
            })
            
            all_available_paths.append({
                "level": "hec",
                "name": "Higher Education Certificate (HEC)",
                "eligible": True,
                "applicationLink": "/apply/hec"
            })
        
        if not alevel_grades:
            # O-Level only applicant
            result["primaryRecommendation"] = {
                "level": "alevel",
                "name": "Proceed to A-Level Studies",
                "applicationLink": "/new-applicant"
            }
            
            result["recommendedPathways"] = ["A-Level Studies", "HEC Program", "Diploma Programs"]
            result["availableApplicationLinks"] = [p for p in all_available_paths if p["eligible"]]
            
            result["nextSteps"] = [
                "Select your preferred entry pathway",
                "Complete application form for selected program"
            ]
            
            return result
        
        alevel_result = UgandaQualificationChecker.validate_alevel(alevel_grades, curriculum_version=alevel_curriculum)
        result["alevel"] = alevel_result.to_dict()
        
        # Add A-Level pathways
        if alevel_result.eligible:
            if 'bachelor_direct' in alevel_result.eligible_programs:
                all_available_paths.append({
                    "level": "bachelor",
                    "name": "Bachelor Degree Programs",
                    "eligible": True,
                    "applicationLink": "/apply/bachelor"
                })
            
            if 'hec' in alevel_result.eligible_programs:
                all_available_paths.append({
                    "level": "hec",
                    "name": "Higher Education Certificate (HEC)",
                    "eligible": True,
                    "applicationLink": "/apply/hec"
                })
            
            if 'diploma' in alevel_result.eligible_programs:
                all_available_paths.append({
                    "level": "diploma",
                    "name": "Diploma Programs",
                    "eligible": True,
                    "applicationLink": "/apply/diploma"
                })
        
        # Sort paths by hierarchy priority (highest first)
        path_priority = ['bachelor', 'diploma', 'hec', 'certificate']
        all_available_paths.sort(key=lambda x: path_priority.index(x["level"]))
        
        # Set primary recommendation to highest eligible level
        eligible_paths = [p for p in all_available_paths if p["eligible"]]
        
        if eligible_paths:
            result["primaryRecommendation"] = eligible_paths[0]
            result["recommendedPathways"] = [p["name"] for p in eligible_paths]
            result["availableApplicationLinks"] = eligible_paths
            
            result["nextSteps"] = [
                f"You qualify for {eligible_paths[0]['name']}",
                "Click the application link below to proceed directly",
                "Or select an alternative pathway"
            ]
        else:
            result["primaryRecommendation"] = {
                "level": "bridging",
                "name": "Bridging Program",
                "applicationLink": "/apply/hec"
            }
            
            result["recommendedPathways"] = ["HEC Bridging Program", "Diploma Foundation Entry"]
            result["availableApplicationLinks"] = all_available_paths
            
            result["nextSteps"] = [
                "You qualify for bridging programs",
                "Apply for HEC to progress to higher levels later",
                "Contact admissions office for guidance"
            ]
        
        return result
