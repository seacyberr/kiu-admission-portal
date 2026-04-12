"""
Error Handlers - Global exception handling
"""
import logging
from flask import jsonify, request

logger = logging.getLogger(__name__)


def handle_validation_error(error):
    """Handle 400 Bad Request errors"""
    logger.warning(f"Validation error: {str(error)}")
    return jsonify({
        "error": "Bad Request",
        "message": str(error.description) if hasattr(error, 'description') else str(error),
        "code": 400
    }), 400


def handle_not_found(error):
    """Handle 404 Not Found errors"""
    logger.info(f"Not found: {request.path}")
    return jsonify({
        "error": "Not Found",
        "message": f"The requested resource '{request.path}' was not found.",
        "code": 404
    }), 404


def handle_server_error(error):
    """Handle 500 Internal Server Error"""
    logger.exception(f"Server error: {str(error)}")
    return jsonify({
        "error": "Internal Server Error",
        "message": "An unexpected error occurred. Please try again later.",
        "code": 500
    }), 500


class APIError(Exception):
    """Custom API error with status code"""
    def __init__(self, message, status_code=400, payload=None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.payload = payload
    
    def to_dict(self):
        rv = dict(self.payload or ())
        rv['error'] = self.message
        rv['code'] = self.status_code
        return rv
