"""
Enhanced Error Handling and Logging Utilities for KIU Admission Portal

Provides centralized error handling, structured logging, and
consistent error responses across the application.
"""

import logging
import traceback
import json
from datetime import datetime
from typing import Dict, Any, Optional
from flask import jsonify, Response
from functools import wraps

# Configure structured logging
import os
log_dir = os.path.join(os.path.dirname(__file__), '..', 'logs')
os.makedirs(log_dir, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(os.path.join(log_dir, 'kiu-admission-errors.log'))
    ]
)

logger = logging.getLogger(__name__)

class KIUError(Exception):
    """Base exception for KIU application errors"""
    
    def __init__(self, message: str, error_code: str = None, status_code: int = 500, details: Dict = None):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        self.details = details or {}
        self.timestamp = datetime.utcnow().isoformat()

class ValidationError(KIUError):
    """Raised when input validation fails"""
    
    def __init__(self, message: str, field: str = None, value: Any = None):
        super().__init__(message, "VALIDATION_ERROR", 400)
        self.field = field
        self.value = value

class AuthenticationError(KIUError):
    """Raised when authentication fails"""
    
    def __init__(self, message: str = "Authentication failed"):
        super().__init__(message, "AUTH_ERROR", 401)

class AuthorizationError(KIUError):
    """Raised when authorization fails"""
    
    def __init__(self, message: str = "Access denied"):
        super().__init__(message, "AUTHORIZATION_ERROR", 403)

class NotFoundError(KIUError):
    """Raised when a resource is not found"""
    
    def __init__(self, message: str = "Resource not found"):
        super().__init__(message, "NOT_FOUND", 404)

class ConflictError(KIUError):
    """Raised when there's a conflict with existing data"""
    
    def __init__(self, message: str = "Resource conflict"):
        super().__init__(message, "CONFLICT", 409)

class RateLimitError(KIUError):
    """Raised when rate limit is exceeded"""
    
    def __init__(self, message: str = "Rate limit exceeded", retry_after: int = None):
        super().__init__(message, "RATE_LIMIT", 429)
        self.retry_after = retry_after

class CertificateVerificationError(KIUError):
    """Raised when certificate verification fails"""
    
    def __init__(self, message: str, verification_details: Dict = None):
        super().__init__(message, "CERT_VERIFICATION_ERROR", 422)
        self.verification_details = verification_details or {}

class DatabaseError(KIUError):
    """Raised when database operations fail"""
    
    def __init__(self, message: str = "Database operation failed"):
        super().__init__(message, "DATABASE_ERROR", 500)

def handle_kiu_error(func):
    """
    Decorator for handling KIU errors consistently
    
    Args:
        func: Function to wrap
        
    Returns:
        Wrapped function with error handling
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except KIUError as e:
            logger.error(f"KIU Error: {e.error_code} - {e.message}", exc_info=True)
            return jsonify({
                "error": e.error_code,
                "message": e.message,
                "details": e.details,
                "timestamp": e.timestamp,
                "status": "error"
            }), e.status_code
        except ValidationError as e:
            logger.warning(f"Validation Error: {e.field} - {e.message}")
            return jsonify({
                "error": e.error_code,
                "message": e.message,
                "field": e.field,
                "value": e.value,
                "status": "validation_error"
            }), e.status_code
        except Exception as e:
            logger.error(f"Unexpected Error: {str(e)}", exc_info=True)
            return jsonify({
                "error": "INTERNAL_ERROR",
                "message": "An unexpected error occurred",
                "details": {
                    "type": type(e).__name__,
                    "message": str(e)
                },
                "timestamp": datetime.utcnow().isoformat(),
                "status": "error"
            }), 500
    
    return wrapper

def log_request_info(func):
    """
    Decorator for logging request information
    
    Args:
        func: Function to wrap
        
    Returns:
        Wrapped function with request logging
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        from flask import request
        
        # Log request start
        start_time = datetime.utcnow()
        logger.info(f"Request started: {request.method} {request.path}")
        
        try:
            result = func(*args, **kwargs)
            
            # Log successful completion
            end_time = datetime.utcnow()
            duration = (end_time - start_time).total_seconds()
            logger.info(f"Request completed: {request.method} {request.path} - {duration:.2f}s")
            
            return result
            
        except Exception as e:
            # Log error
            end_time = datetime.utcnow()
            duration = (end_time - start_time).total_seconds()
            logger.error(f"Request failed: {request.method} {request.path} - {duration:.2f}s - {str(e)}", exc_info=True)
            raise
    
    return wrapper

def validate_json_payload(required_fields: list = None, optional_fields: list = None):
    """
    Decorator for validating JSON payload
    
    Args:
        required_fields: List of required field names
        optional_fields: List of optional field names
        
    Returns:
        Wrapped function with JSON validation
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            from flask import request
            
            if not request.is_json:
                raise ValidationError("Request must be JSON")
            
            data = request.get_json()
            if not data:
                raise ValidationError("Invalid JSON payload")
            
            # Check required fields
            if required_fields:
                missing_fields = [field for field in required_fields if field not in data]
                if missing_fields:
                    raise ValidationError(f"Missing required fields: {', '.join(missing_fields)}")
            
            # Validate field types
            if optional_fields:
                for field in optional_fields:
                    if field in data and not isinstance(data[field], (str, int, float, bool, list, dict)):
                        raise ValidationError(f"Invalid type for field {field}")
            
            return func(*args, **kwargs)
        
        return wrapper
    return decorator

def sanitize_input(text: str, max_length: int = 1000, remove_html: bool = True) -> str:
    """
    Sanitize user input to prevent XSS and injection attacks
    
    Args:
        text: Input text to sanitize
        max_length: Maximum allowed length
        remove_html: Whether to remove HTML tags
        
    Returns:
        Sanitized text
    """
    if not text or not isinstance(text, str):
        return ""
    
    # Remove HTML tags if requested
    if remove_html:
        import re
        text = re.sub(r'<[^>]*>', '', text)
        text = re.sub(r'javascript:', '', text, flags=re.IGNORECASE)
        text = re.sub(r'on\w+\s*=', '', text, flags=re.IGNORECASE)
    
    # Limit length
    if len(text) > max_length:
        text = text[:max_length]
    
    return text.strip()

def validate_email(email: str) -> bool:
    """
    Validate email format
    
    Args:
        email: Email address to validate
        
    Returns:
        True if valid, False otherwise
    """
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def validate_phone(phone: str) -> bool:
    """
    Validate phone number format (Uganda format)
    
    Args:
        phone: Phone number to validate
        
    Returns:
        True if valid, False otherwise
    """
    import re
    # Remove common separators
    clean_phone = re.sub(r'[\s\-\(\)]', '', phone)
    
    # Uganda phone patterns
    patterns = [
        r'^\+256\d{9}$',  # International format
        r'^0\d{9}$',      # Local format
        r'^07\d{8}$',      # Mobile format
    ]
    
    return any(bool(re.match(pattern, clean_phone)) for pattern in patterns)

def validate_year(year: int, min_year: int = 1990, max_year: int = None) -> bool:
    """
    Validate year range
    
    Args:
        year: Year to validate
        min_year: Minimum allowed year
        max_year: Maximum allowed year (current year if None)
        
    Returns:
        True if valid, False otherwise
    """
    if not isinstance(year, int):
        return False
    
    if max_year is None:
        from datetime import datetime
        max_year = datetime.now().year
    
    return min_year <= year <= max_year

def create_error_response(error_code: str, message: str, status_code: int = 500, details: Dict = None) -> Response:
    """
    Create standardized error response
    
    Args:
        error_code: Machine-readable error code
        message: Human-readable error message
        status_code: HTTP status code
        details: Additional error details
        
    Returns:
        Flask JSON response
    """
    response_data = {
        "error": error_code,
        "message": message,
        "timestamp": datetime.utcnow().isoformat(),
        "status": "error"
    }
    
    if details:
        response_data["details"] = details
    
    response = jsonify(response_data)
    response.status_code = status_code
    
    # Add security headers
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    
    return response

def log_certificate_verification(verification_result: Dict, certificate_type: str, applicant_id: str = None):
    """
    Log certificate verification results
    
    Args:
        verification_result: Result from certificate verification
        certificate_type: Type of certificate verified
        applicant_id: ID of applicant (optional)
    """
    status = verification_result.get('verification_status', 'unknown')
    score = verification_result.get('verification_score', 0)
    
    log_message = f"Certificate Verification - {certificate_type.upper()} - Status: {status} - Score: {score}%"
    if applicant_id:
        log_message += f" - Applicant: {applicant_id}"
    
    if status == 'verified':
        logger.info(log_message)
    elif status == 'failed':
        logger.error(log_message)
    else:
        logger.warning(log_message)
    
    # Log details if available
    if 'errors' in verification_result:
        logger.error(f"Certificate Verification Errors: {verification_result['errors']}")
    
    if 'warnings' in verification_result:
        logger.warning(f"Certificate Verification Warnings: {verification_result['warnings']}")

def log_application_action(action: str, application_id: str, user_id: str = None, details: Dict = None):
    """
    Log application-related actions
    
    Args:
        action: Action performed (created, updated, submitted, etc.)
        application_id: ID of application
        user_id: ID of user performing action (optional)
        details: Additional action details
    """
    log_message = f"Application Action: {action} - Application: {application_id}"
    if user_id:
        log_message += f" - User: {user_id}"
    
    if details:
        log_message += f" - Details: {json.dumps(details)}"
    
    logger.info(log_message)
