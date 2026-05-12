"""
API Response Standardization
RFC 7807 + JSend compliant responses
"""
import uuid
from datetime import datetime
from flask import jsonify, g, request
from typing import Any, Dict, Optional, List


def success_response(
    data: Any,
    message: Optional[str] = None,
    meta: Optional[Dict] = None,
    status_code: int = 200
):
    """
    Standard success response (JSend format)
    
    Args:
        data: Response payload
        message: Optional success message
        meta: Optional metadata (pagination, etc.)
        status_code: HTTP status code
    """
    response = {
        "status": "success",
        "data": data
    }
    
    if message:
        response["message"] = message
    
    if meta:
        response["meta"] = _add_request_meta(meta)
    else:
        response["meta"] = _add_request_meta({})
    
    return jsonify(response), status_code


def fail_response(
    message: str,
    errors: Optional[Dict] = None,
    status_code: int = 400,
    error_code: Optional[str] = None
):
    """
    Standard fail response (validation errors, etc.)
    
    Args:
        message: Human-readable error message
        errors: Detailed field errors
        status_code: HTTP status code
        error_code: Machine-readable error code
    """
    response = {
        "status": "fail",
        "message": message
    }
    
    if errors:
        response["errors"] = errors
    
    if error_code:
        response["error"] = {"code": error_code}
    
    response["meta"] = _add_request_meta({})
    
    return jsonify(response), status_code


def error_response(
    message: str,
    error_type: str = "INTERNAL_ERROR",
    details: Optional[Dict] = None,
    status_code: int = 500,
    error_id: Optional[str] = None
):
    """
    Standard error response (RFC 7807 style)
    
    Args:
        message: Human-readable error message
        error_type: Machine-readable error type
        details: Additional error details (not in production)
        status_code: HTTP status code
        error_id: Unique error identifier for tracking
    """
    error_id = error_id or str(uuid.uuid4())
    
    response = {
        "status": "error",
        "error": {
            "type": error_type,
            "message": message,
            "id": error_id
        }
    }
    
    # Only include details in non-production environments
    from flask import current_app
    if details and not current_app.config.get('ENV') == 'production':
        response["error"]["details"] = details
    
    response["meta"] = _add_request_meta({})
    
    return jsonify(response), status_code


def paginated_response(
    items: List[Any],
    total: int,
    page: int,
    per_page: int,
    data_key: str = "items"
):
    """
    Standard paginated response
    
    Args:
        items: List of items for current page
        total: Total number of items
        page: Current page number
        per_page: Items per page
        data_key: Key name for items in response
    """
    pages = (total + per_page - 1) // per_page if per_page > 0 else 0
    
    data = {
        data_key: items,
        "pagination": {
            "total": total,
            "page": page,
            "perPage": per_page,
            "pages": pages,
            "hasNext": page < pages,
            "hasPrev": page > 1
        }
    }
    
    return success_response(
        data=data,
        meta={"pagination": data["pagination"]}
    )


def _add_request_meta(meta: Dict) -> Dict:
    """Add standard request metadata to response"""
    meta = meta or {}
    
    # Add request ID for tracing
    request_id = getattr(g, 'request_id', None)
    if request_id:
        meta["requestId"] = request_id
    
    # Add timestamp
    meta["timestamp"] = datetime.utcnow().isoformat()
    
    # Add API version
    meta["apiVersion"] = "v1"
    
    return meta


# Shorthand helpers
def ok(data: Any, message: Optional[str] = None):
    """200 OK response"""
    return success_response(data, message, status_code=200)


def created(data: Any, message: Optional[str] = None):
    """201 Created response"""
    return success_response(data, message or "Resource created", status_code=201)


def accepted(data: Any, message: Optional[str] = None):
    """202 Accepted response"""
    return success_response(data, message, status_code=202)


def no_content():
    """204 No Content response"""
    return jsonify({"status": "success"}), 204


def bad_request(message: str, errors: Optional[Dict] = None):
    """400 Bad Request response"""
    return fail_response(message, errors, status_code=400, error_code="BAD_REQUEST")


def unauthorized(message: str = "Unauthorized"):
    """401 Unauthorized response"""
    return error_response(message, "UNAUTHORIZED", status_code=401)


def forbidden(message: str = "Forbidden"):
    """403 Forbidden response"""
    return error_response(message, "FORBIDDEN", status_code=403)


def not_found(message: str = "Resource not found"):
    """404 Not Found response"""
    return error_response(message, "NOT_FOUND", status_code=404)


def conflict(message: str, error_code: Optional[str] = None):
    """409 Conflict response"""
    return fail_response(message, status_code=409, error_code=error_code or "CONFLICT")


def unprocessable(message: str, errors: Optional[Dict] = None):
    """422 Unprocessable Entity response"""
    return fail_response(message, errors, status_code=422, error_code="VALIDATION_ERROR")


def too_many_requests(message: str = "Rate limit exceeded", retry_after: Optional[int] = None):
    """429 Too Many Requests response"""
    response = error_response(message, "RATE_LIMIT_EXCEEDED", status_code=429)
    if retry_after:
        response[0].headers['Retry-After'] = str(retry_after)
    return response


def internal_error(message: str = "Internal server error", error_id: Optional[str] = None):
    """500 Internal Server Error response"""
    return error_response(
        message, 
        "INTERNAL_ERROR", 
        status_code=500,
        error_id=error_id
    )
