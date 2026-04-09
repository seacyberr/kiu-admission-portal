"""
Unit tests for recommendations.py validation logic
"""

import pytest
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from routes.recommendations import (
    _score_uace_programme, _score_diploma_programme, 
    _score_bachelors_programme, _score_masters_programme,
    _score_phd_programme, _score_hec_programme,
    _score_uce_programme, _score_national_cert_programme
)

# Sample programme data for testing
SAMPLE_PROGRAMME = {
    "id": "test_program",
    "code": "TEST",
    "name": "Test Programme",
    "faculty": "Test Faculty",
    "level": "undergraduate",
    "duration_years": 3,
    "intake_months": [8, 1, 3],
    "campus": ["Test Campus"],
    "tuition_ugx_per_semester": 2000000,
    "tuition_usd_per_semester": 500,
    "nche_entry": {
        "uace_direct": {
            "min_principal_passes": 2,
            "required_subjects": ["Mathematics", "Physics"],
            "one_of_subjects": ["Chemistry", "Biology"],
            "min_points": 10,
        },
        "diploma_entry": {
            "eligible": True,
            "min_class": "Credit",
            "relevant_fields": ["Computer Science", "ICT"],
        }
    },
    "career_prospects": ["Test Professional"],
    "accreditation": "Test Council",
}

# Sample programme data for bachelors tests
SAMPLE_BACHELORS = {
    "id": "test_bachelors",
    "code": "BTEST",
    "name": "Test Bachelors Programme",
    "faculty": "Test Faculty",
    "level": "postgraduate",
    "duration_years": 2,
    "intake_months": [8, 1],
    "campus": ["Test Campus"],
    "tuition_ugx_per_semester": 3000000,
    "tuition_usd_per_semester": 800,
    "nche_entry": {
        "bachelors_required": True,
        "min_class": "Second Class Lower",
    }
}

# Sample programme data for masters tests
SAMPLE_MASTERS = {
    "id": "test_masters",
    "code": "MTEST",
    "name": "Test Masters Programme",
    "faculty": "Test Faculty",
    "level": "masters",
    "duration_years": 2,
    "intake_months": [8, 1],
    "campus": ["Test Campus"],
    "tuition_ugx_per_semester": 3500000,
    "tuition_usd_per_semester": 1000,
    "nche_entry": {
        "bachelors_required": True,
        "min_class": "Pass",
    }
}

class TestRecommendationsValidation:
    """Test suite for recommendations validation logic"""
    
    def test_uace_scoring_valid_data(self):
        """Test UACE scoring with valid data"""
        applicant = {
            "uace_subjects": ["Mathematics", "Physics", "Chemistry"],
            "uace_principal_passes": 2,
            "uace_points": 12,
            "uce_passes": 6
        }
        result = _score_uace_programme(SAMPLE_PROGRAMME, applicant)
        
        assert result["eligible"] is True
        assert result["route"] == "uace_direct"
        assert len(result["reasons_pass"]) > 0
        assert len(result["reasons_fail"]) == 0
    
    def test_uace_scoring_insufficient_principal_passes(self):
        """Test UACE scoring with insufficient principal passes"""
        applicant = {
            "uace_subjects": ["Mathematics", "Physics"],
            "uace_principal_passes": 1,  # Below required
            "uace_points": 12,
            "uce_passes": 6
        }
        result = _score_uace_programme(SAMPLE_PROGRAMME, applicant)
        
        assert result["eligible"] is False
        assert "Requires 2 principal pass(es)" in result["reasons_fail"][0]
    
    def test_uace_scoring_missing_required_subjects(self):
        """Test UACE scoring with missing required subjects"""
        applicant = {
            "uace_subjects": ["Mathematics", "Biology"],  # Missing Physics
            "uace_principal_passes": 2,
            "uace_points": 12,
            "uce_passes": 6
        }
        result = _score_uace_programme(SAMPLE_PROGRAMME, applicant)
        
        assert result["eligible"] is False
        assert "Missing mandatory subject(s): Physics" in result["reasons_fail"][0]
    
    def test_diploma_scoring_valid_credit(self):
        """Test diploma scoring with valid Credit class"""
        applicant = {
            "diploma_class": "Credit",
            "diploma_field": "Computer Science"
        }
        result = _score_diploma_programme(SAMPLE_PROGRAMME, applicant)
        
        assert result["eligible"] is True
        assert result["route"] == "diploma"
        assert len(result["reasons_pass"]) > 0
    
    def test_diploma_scoring_invalid_class(self):
        """Test diploma scoring with invalid class"""
        applicant = {
            "diploma_class": "Fail",  # Below Credit requirement
            "diploma_field": "Computer Science"
        }
        result = _score_diploma_programme(SAMPLE_PROGRAMME, applicant)
        
        assert result["eligible"] is False
        assert "Invalid diploma class: Fail" in result["reasons_fail"][0]
    
    def test_bachelors_scoring_valid_second_class_upper(self):
        """Test bachelors scoring with valid class"""
        applicant = {
            "bachelors_class": "Second Class Upper",
            "bachelors_field": "Business Administration",
            "work_experience_years": 2
        }
        result = _score_bachelors_programme(SAMPLE_BACHELORS, applicant)
        
        assert result["eligible"] is True
        assert result["route"] == "bachelors"
    
    def test_masters_scoring_valid_merit(self):
        """Test masters scoring with valid Merit class"""
        applicant = {
            "masters_class": "Merit",
            "masters_field": "Business Administration",
            "work_experience_years": 3
        }
        result = _score_masters_programme(SAMPLE_MASTERS, applicant)
        
        assert result["eligible"] is True
        assert result["route"] == "masters"
    
    def test_input_validation_invalid_integer(self):
        """Test input validation with invalid integer data"""
        applicant = {
            "uace_principal_passes": "invalid_number",  # Should be handled gracefully
            "uace_points": 12,
            "uce_passes": 6
        }
        
        # This should not crash, but handle gracefully
        try:
            result = _score_uace_programme(SAMPLE_PROGRAMME, applicant)
            # Should default to 0 for invalid input
            assert result["eligible"] is False
        except Exception as e:
            # If it crashes, that's a problem
            pytest.fail(f"Function crashed with invalid input: {e}")
    
    def test_edge_case_empty_applicant_data(self):
        """Test with empty applicant data"""
        applicant = {}
        result = _score_uace_programme(SAMPLE_PROGRAMME, applicant)
        
        # Should handle empty data gracefully
        assert "eligible" in result
        assert "route" in result
        assert isinstance(result["reasons_fail"], list)

if __name__ == "__main__":
    pytest.main([__file__])
