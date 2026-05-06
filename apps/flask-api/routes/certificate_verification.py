"""Certificate Verification Routes for KIU Admission Portal

Provides endpoints for automated and manual certificate verification
"""

import os
import logging
from flask import Blueprint, request, jsonify, current_app
from routes.auth import get_current_user
# from services.certificate_verification import certificate_verifier
from models import db, AdmissionApplication
from utils.api_response import success_response, bad_request, unauthorized, forbidden, not_found
from utils.external_api_validation import (
    safe_external_api_call,
    validate_certificate_service_response,
    validate_external_api_response
)

log = logging.getLogger(__name__)

certificate_verification_bp = Blueprint("certificate_verification", __name__)

@certificate_verification_bp.route("/verify/<int:application_id>", methods=["POST"])
def verify_certificate(application_id):
    """
    Verify uploaded certificate for an application
    
    Args:
        application_id: ID of the application to verify certificate for
        
    Returns:
        Verification result with status and details
    """
    user, error = get_current_user()
    if error:
        return unauthorized(error)
    
    application = db.session.get(AdmissionApplication, application_id)
    if not application:
        return not_found("Application not found")
    
    if application.user_id != user.id and user.role != "admin":
        return forbidden("Access denied")
    
    data = request.get_json()
    if not data:
        return bad_request("No JSON body provided")
    
    certificate_type = data.get("certificate_type", "")
    if certificate_type not in ["uce", "uace", "diploma", "hec"]:
        return bad_request(
            "certificate_type must be one of: uce, uace, diploma, hec",
            errors={"certificate_type": "Invalid value"}
        )
    
    # Determine which certificate file to verify
    certificate_path = None
    if certificate_type == "uce" and application.olevel_certificate_path:
        certificate_path = os.path.join(
            current_app.config["UPLOAD_FOLDER"], 
            "certificates", 
            os.path.basename(application.olevel_certificate_path)
        )
    elif certificate_type == "uace" and application.alevel_certificate_path:
        certificate_path = os.path.join(
            current_app.config["UPLOAD_FOLDER"], 
            "certificates", 
            os.path.basename(application.alevel_certificate_path)
        )
    elif certificate_type == "diploma" and application.diploma_certificate_path:
        certificate_path = os.path.join(
            current_app.config["UPLOAD_FOLDER"], 
            "certificates", 
            os.path.basename(application.diploma_certificate_path)
        )
    elif certificate_type == "hec" and application.hec_certificate_path:
        certificate_path = os.path.join(
            current_app.config["UPLOAD_FOLDER"], 
            "certificates", 
            os.path.basename(application.hec_certificate_path)
        )
    
    if not certificate_path or not os.path.exists(certificate_path):
        return not_found(f"No {certificate_type.upper()} certificate found for this application")
    
    try:
        # Perform verification
        verification_result = certificate_verifier.verify_certificate_file(
            certificate_path, 
            certificate_type.upper()
        )
        
        # Store verification result in application (if you have verification fields in your model)
        # For now, return the result
        
        return success_response({
            "application_id": application_id,
            "certificate_type": certificate_type,
            "verification_result": verification_result,
        }, message=f"Certificate verification completed: {verification_result['verification_status']}")
        
    except Exception as e:
        log.error(f"Certificate verification failed: {str(e)}")
        return bad_request(f"Certificate verification encountered an error: {str(e)}")


@certificate_verification_bp.route("/verify-with-data", methods=["POST"])
def verify_certificate_with_data():
    """
    Verify certificate using manually entered data
    
    This endpoint allows verification when OCR data is available
    or when certificates are verified manually
    """
    user, error = get_current_user()
    if error:
        return unauthorized(error)
    
    data = request.get_json()
    if not data:
        return bad_request("No JSON body provided")
    
    certificate_type = data.get("certificate_type", "")
    certificate_data = data.get("certificate_data", {})
    
    if certificate_type not in ["uce", "uace", "diploma", "hec"]:
        return bad_request(
            "certificate_type must be one of: uce, uace, diploma, hec",
            errors={"certificate_type": "Invalid value"}
        )
    
    try:
        # Perform verification based on certificate type
        if certificate_type == "uce":
            verification_result = certificate_verifier.verify_uce_certificate(certificate_data)
        elif certificate_type == "uace":
            verification_result = certificate_verifier.verify_uace_certificate(certificate_data)
        elif certificate_type in ["diploma", "hec"]:
            verification_result = certificate_verifier.verify_diploma_certificate(certificate_data)
        else:
            return bad_request(
                f"Unsupported certificate type: {certificate_type}",
                errors={"certificate_type": "Unsupported"}
            )
        
        return success_response({
            "certificate_type": certificate_type,
            "verification_result": verification_result,
        }, message=f"Certificate verification completed: {verification_result['verification_status']}")
        
    except Exception as e:
        log.error(f"Certificate verification with data failed: {str(e)}")
        return bad_request(f"Certificate verification encountered an error: {str(e)}")


@certificate_verification_bp.route("/extract-data", methods=["POST"])
def extract_certificate_data():
    """
    Extract structured data from certificate text using OCR patterns
    
    This endpoint processes OCR text and structures it
    """
    user, error = get_current_user()
    if error:
        return unauthorized(error)
    
    data = request.get_json()
    if not data:
        return bad_request("No JSON body provided")
    
    ocr_text = data.get("ocr_text", "")
    certificate_type = data.get("certificate_type", "")
    
    if not ocr_text.strip():
        return bad_request("ocr_text is required", errors={"ocr_text": "Required"})
    
    if certificate_type not in ["uce", "uace"]:
        return bad_request(
            "certificate_type must be uce or uace",
            errors={"certificate_type": "Invalid value"}
        )
    
    try:
        extracted_data = certificate_verifier.extract_certificate_data_from_text(
            ocr_text, 
            certificate_type.upper()
        )
        
        return success_response({
            "certificate_type": certificate_type,
            "extracted_data": extracted_data,
        }, message=f"Data extraction completed with confidence score: {extracted_data['confidence_score']}%")
        
    except Exception as e:
        log.error(f"Certificate data extraction failed: {str(e)}")
        return bad_request(f"Data extraction encountered an error: {str(e)}")


@certificate_verification_bp.route("/verification-status/<int:application_id>", methods=["GET"])
def get_verification_status(application_id):
    """
    Get verification status for all certificates of an application
    
    Args:
        application_id: ID of the application
        
    Returns:
        Verification status for all certificate types
    """
    user, error = get_current_user()
    if error:
        return unauthorized(error)
    
    application = db.session.get(AdmissionApplication, application_id)
    if not application:
        return not_found("Application not found")
    
    if application.user_id != user.id and user.role != "admin":
        return forbidden("Access denied")
    
    try:
        # Check which certificates are uploaded
        certificates_status = {}
        
        if application.olevel_certificate_path:
            cert_path = os.path.join(
                current_app.config["UPLOAD_FOLDER"], 
                "certificates", 
                os.path.basename(application.olevel_certificate_path)
            )
            if os.path.exists(cert_path):
                verification = certificate_verifier.verify_certificate_file(cert_path, "UCE")
                certificates_status["uce"] = verification
        
        if application.alevel_certificate_path:
            cert_path = os.path.join(
                current_app.config["UPLOAD_FOLDER"], 
                "certificates", 
                os.path.basename(application.alevel_certificate_path)
            )
            if os.path.exists(cert_path):
                verification = certificate_verifier.verify_certificate_file(cert_path, "UACE")
                certificates_status["uace"] = verification
        
        if application.diploma_certificate_path:
            cert_path = os.path.join(
                current_app.config["UPLOAD_FOLDER"], 
                "certificates", 
                os.path.basename(application.diploma_certificate_path)
            )
            if os.path.exists(cert_path):
                verification = certificate_verifier.verify_certificate_file(cert_path, "DIPLOMA")
                certificates_status["diploma"] = verification
        
        if application.hec_certificate_path:
            cert_path = os.path.join(
                current_app.config["UPLOAD_FOLDER"], 
                "certificates", 
                os.path.basename(application.hec_certificate_path)
            )
            if os.path.exists(cert_path):
                verification = certificate_verifier.verify_certificate_file(cert_path, "HEC")
                certificates_status["hec"] = verification
        
        return success_response({
            "application_id": application_id,
            "certificates_status": certificates_status,
            "overall_status": _calculate_overall_status(certificates_status),
            "verified_count": len([c for c in certificates_status.values() if c.get("verification_status") == "verified"]),
            "total_certificates": len(certificates_status)
        })
        
    except Exception as e:
        log.error(f"Get verification status failed: {str(e)}")
        return bad_request(f"Status check encountered an error: {str(e)}")


def _calculate_overall_status(certificates_status):
    """
    Calculate overall verification status from individual certificate statuses
    """
    if not certificates_status:
        return "no_certificates"
    
    statuses = [cert.get("verification_status", "pending") for cert in certificates_status.values()]
    
    if all(status == "verified" for status in statuses):
        return "all_verified"
    elif any(status == "failed" for status in statuses):
        return "some_failed"
    elif any(status in ["needs_review", "provisionally_verified"] for status in statuses):
        return "needs_review"
    elif any(status == "verified" for status in statuses):
        return "partially_verified"
    else:
        return "pending"


@certificate_verification_bp.route("/verification-standards", methods=["GET"])
def get_verification_standards():
    """
    Get verification standards and criteria used for certificate verification
    
    Returns:
        Verification standards for different certificate types
    """
    try:
        standards = {
            "uce": {
                "required_subjects": certificate_verifier.valid_uce_subjects,
                "valid_grades_old": certificate_verifier.uce_old_grades,
                "valid_grades_new": certificate_verifier.uce_new_grades,
                "minimum_subjects": 5,
                "index_number_pattern": certificate_verifier.uce_certificate_patterns['index_number'],
                "verification_criteria": {
                    "index_number_format": "Must follow UNEB format (U####/###)",
                    "examination_year": "Must be valid year within last 30 years",
                    "school_name": "Must be recognized institution",
                    "subjects_count": "Minimum 5 subjects required",
                    "grade_validity": "Grades must be valid for curriculum type"
                }
            },
            "uace": {
                "required_principal_subjects": certificate_verifier.valid_uace_principal_subjects,
                "required_subsidiary_subjects": certificate_verifier.valid_uace_subsidiary_subjects,
                "valid_grades": certificate_verifier.uace_grades,
                "minimum_principal_subjects": 2,
                "minimum_subsidiary_subjects": 1,
                "index_number_pattern": certificate_verifier.uace_certificate_patterns['index_number'],
                "grade_points": {"A": 6, "B": 5, "C": 4, "D": 3, "E": 2, "O": 1, "F": 0},
                "verification_criteria": {
                    "index_number_format": "Must follow UNEB format (A####/###)",
                    "examination_year": "Must be valid year within last 30 years",
                    "principal_subjects": "Minimum 2 principal subjects required",
                    "subsidiary_subjects": "General Paper mandatory, plus Subsidiary Math or ICT",
                    "grade_calculation": "Points calculated from principal subjects only",
                    "minimum_points": "Minimum 6 points required for university entry"
                }
            },
            "diploma": {
                "verification_criteria": {
                    "institution_accreditation": "Must be NCHE accredited institution",
                    "award_date": "Must be valid date within reasonable timeframe",
                    "classification": "Must show class/division awarded",
                    "program_relevance": "Program should be relevant to field of study"
                }
            },
            "hec": {
                "verification_criteria": {
                    "institution_accreditation": "Must be NCHE accredited institution",
                    "award_date": "Must be valid date within reasonable timeframe",
                    "classification": "Must show class/division awarded",
                    "program_relevance": "Program should be relevant to intended degree program"
                }
            }
        }
        
        # Add o_level and a_level as aliases for uce and uace
        standards["o_level"] = standards["uce"]
        standards["a_level"] = standards["uace"]
        
        return success_response({
            "standards": standards,
            "o_level": standards["uce"],
            "a_level": standards["uace"],
        }, message="Verification standards retrieved successfully")
        
    except Exception as e:
        log.error(f"Get verification standards failed: {str(e)}")
        return bad_request(f"Failed to retrieve verification standards: {str(e)}")
