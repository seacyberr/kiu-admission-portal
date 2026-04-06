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
        for grade in olevel_grades:
            grade_val = grade.get('points', 9)
            # ONLY grades 1 through 8 are considered PASSES. Grade 9 is FAIL.
            if 1 <= grade_val <= 8:
                passes += 1
        
        if passes >= 5:
            result.eligible = True
            result.requirements_met.append(f"✅ Minimum 5 O-Level passes achieved ({passes} passes)")
            result.message = "O-Level requirements satisfied"
        else:
            result.requirements_missing.append(f"❌ Requires minimum 5 O-Level passes, only {passes} passes obtained")
            result.message = "Insufficient O-Level passes"
        
        return result
    
    @staticmethod
    def validate_alevel(alevel_grades: List[Dict]) -> QualificationResult:
        """
        Validate A-Level (UACE) requirements for different pathways
        """
        result = QualificationResult(False)
        
        if not alevel_grades or len(alevel_grades) == 0:
            result.requirements_missing.append("A-Level results not provided")
            result.message = "A-Level results are required"
            return result
        
        principal_passes = 0
        subsidiary_passes = 0
        
        for grade in alevel_grades:
            subject_type = grade.get('subjectType', '').lower()
            points = grade.get('points', 0)
            
            if subject_type == 'principal' and points >= 1:
                principal_passes += 1
            elif subject_type == 'subsidiary' and points >= 1:
                subsidiary_passes += 1
        
        result.requirements_met.append(f"📊 A-Level Results: {principal_passes} Principal Passes, {subsidiary_passes} Subsidiary Passes")
        
        # Check qualification thresholds
        pathways = []
        
        # Direct Bachelor Entry
        if principal_passes >= 2:
            result.requirements_met.append("✅ Eligible for Direct Bachelor Degree Entry (2+ Principal Passes)")
            pathways.append("bachelor_direct")
        elif principal_passes >= 1 and subsidiary_passes >= 2:
            result.requirements_met.append("✅ Eligible for Direct Bachelor Degree Entry (1 Principal + 2 Subsidiaries)")
            pathways.append("bachelor_direct")
        
        # HEC Entry
        if principal_passes >= 1 or subsidiary_passes >= 2:
            result.requirements_met.append("✅ Eligible for Higher Education Certificate (HEC) Program")
            pathways.append("hec")
        
        # Diploma Entry
        if principal_passes >= 1 and subsidiary_passes >= 2:
            result.requirements_met.append("✅ Eligible for Diploma Programs")
            pathways.append("diploma")
        
        if len(pathways) > 0:
            result.eligible = True
            result.eligible_programs = pathways
            result.message = f"Eligible for {len(pathways)} higher education pathways"
        else:
            result.requirements_missing.append("❌ Does not meet minimum requirements for any higher education program")
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
        # O-Level is required for ALL programs
        if not olevel_result.eligible:
            return False, "O-Level requirements not met"
        
        program_level = program_level.lower().strip()
        
        # Certificate / Diploma
        if program_level in ['certificate', 'diploma']:
            if alevel_result and alevel_result.eligible and 'diploma' in alevel_result.eligible_programs:
                return True, "Eligible for Diploma program"
            return False, "Does not meet Diploma entry requirements"
        
        # Bachelor Degree
        elif program_level in ['bachelor', 'degree', 'undergraduate']:
            if has_diploma or has_hec:
                return True, "Eligible via Diploma/HEC entry route"
            if alevel_result and alevel_result.eligible and 'bachelor_direct' in alevel_result.eligible_programs:
                return True, "Eligible via Direct A-Level entry route"
            return False, "Does not meet Bachelor degree entry requirements"
        
        # Masters
        elif program_level in ['master', 'masters', 'postgraduate']:
            return True, "Bachelor degree required for Masters entry (verified separately)"
        
        # PhD
        elif program_level in ['phd', 'doctorate']:
            return True, "Masters degree required for PhD entry (verified separately)"
        
        return False, "Unknown program level"
    
    @staticmethod
    def get_recommended_pathways(olevel_grades: List[Dict], alevel_grades: List[Dict] = None) -> Dict:
        """
        Get recommended education pathways based on student qualifications
        """
        olevel_result = UgandaQualificationChecker.validate_olevel(olevel_grades)
        
        result = {
            "olevel": olevel_result.to_dict(),
            "alevel": None,
            "recommendedPathways": [],
            "nextSteps": []
        }
        
        if not olevel_result.eligible:
            result["nextSteps"] = [
                "Retake O-Level examinations to achieve at least 5 passes",
                "Consider vocational training options"
            ]
            return result
        
        if not alevel_grades:
            result["recommendedPathways"] = ["Proceed to A-Level studies"]
            result["nextSteps"] = [
                "Register for A-Level program",
                "Select appropriate subject combinations for your career interests"
            ]
            return result
        
        alevel_result = UgandaQualificationChecker.validate_alevel(alevel_grades)
        result["alevel"] = alevel_result.to_dict()
        
        if alevel_result.eligible:
            result["recommendedPathways"] = alevel_result.eligible_programs
            result["nextSteps"] = [
                "Review available programs",
                "Check subject requirements for your preferred program",
                "Submit admission application"
            ]
        else:
            result["nextSteps"] = [
                "Consider Higher Education Certificate (HEC) bridging program",
                "Explore vocational training options",
                "Contact admissions office for guidance"
            ]
        
        return result