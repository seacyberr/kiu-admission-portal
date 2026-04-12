"""
Flask Middleware - Request/Response Processing
Adds request tracking, security headers, and CORS handling
"""
import uuid
import time
import logging
from flask import request, g, make_response
from functools import wraps

logger = logging.getLogger(__name__)


def init_middleware(app):
    """Initialize all middleware on Flask app"""
    
    @app.before_request
    def before_request():
        """Set up request context"""
        # Generate request ID for tracing
        g.request_id = request.headers.get('X-Request-ID') or str(uuid.uuid4())
        
        # Track request start time for performance monitoring
        g.request_start_time = time.time()
        
        # Log request
        logger.info(
            f"Request started: {request.method} {request.path}",
            extra={
                'request_id': g.request_id,
                'method': request.method,
                'path': request.path,
                'remote_addr': request.remote_addr,
                'user_agent': request.headers.get('User-Agent', 'unknown')
            }
        )
    
    @app.after_request
    def after_request(response):
        """Add standard headers to all responses"""
        # Add request ID header for tracing
        if hasattr(g, 'request_id'):
            response.headers['X-Request-ID'] = g.request_id
        
        # Security headers
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        response.headers['Permissions-Policy'] = 'geolocation=(), microphone=(), camera=()'
        
        # HSTS in production (force HTTPS)
        if app.config.get('ENV') == 'production':
            response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        
        # Log response
        duration = None
        if hasattr(g, 'request_start_time'):
            duration = (time.time() - g.request_start_time) * 1000  # ms
        
        log_level = logging.WARNING if response.status_code >= 400 else logging.INFO
        logger.log(
            log_level,
            f"Request completed: {request.method} {request.path} - {response.status_code}",
            extra={
                'request_id': getattr(g, 'request_id', 'unknown'),
                'method': request.method,
                'path': request.path,
                'status_code': response.status_code,
                'duration_ms': duration
            }
        )
        
        return response
    
    @app.errorhandler(400)
    def bad_request_handler(error):
        """Handle 400 Bad Request"""
        from utils.api_response import bad_request
        return bad_request(str(error.description) if hasattr(error, 'description') else "Bad request")
    
    @app.errorhandler(404)
    def not_found_handler(error):
        """Handle 404 Not Found"""
        from utils.api_response import not_found
        return not_found("The requested resource was not found")
    
    @app.errorhandler(405)
    def method_not_allowed_handler(error):
        """Handle 405 Method Not Allowed"""
        from utils.api_response import error_response
        return error_response(
            f"Method {request.method} not allowed for this endpoint",
            "METHOD_NOT_ALLOWED",
            status_code=405
        )
    
    @app.errorhandler(500)
    def internal_error_handler(error):
        """Handle 500 Internal Server Error"""
        from utils.api_response import internal_error
        error_id = str(uuid.uuid4())
        logger.error(
            f"Internal server error: {error}",
            exc_info=True,
            extra={'error_id': error_id, 'request_id': getattr(g, 'request_id', 'unknown')}
        )
        return internal_error("An unexpected error occurred", error_id=error_id)
    
    # CORS preflight handler
    @app.route('/api/<path:path>', methods=['OPTIONS'])
    def handle_preflight(path):
        """Handle CORS preflight requests"""
        response = make_response()
        response.status_code = 204
        
        # Get allowed origins from config
        origins = app.config.get('CORS_ORIGINS', 'http://localhost:5173')
        if origins == '*':
            response.headers['Access-Control-Allow-Origin'] = '*'
        else:
            origin_list = [o.strip() for o in origins.split(',')]
            request_origin = request.headers.get('Origin')
            if request_origin and request_origin in origin_list:
                response.headers['Access-Control-Allow-Origin'] = request_origin
            else:
                response.headers['Access-Control-Allow-Origin'] = origin_list[0] if origin_list else 'http://localhost:5173'
        
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS, PATCH'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-Request-ID, X-CSRF-Token, Accept'
        response.headers['Access-Control-Allow-Credentials'] = 'true'
        response.headers['Access-Control-Max-Age'] = '86400'
        
        return response


def require_auth(f):
    """Decorator to require authentication"""
    @wraps(f)
    def decorated(*args, **kwargs):
        from routes.auth import get_current_user
        user, error = get_current_user()
        if error:
            from utils.api_response import unauthorized
            return unauthorized(error)
        g.current_user = user
        return f(*args, **kwargs)
    return decorated


def require_role(*roles):
    """Decorator to require specific role(s)"""
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            from routes.auth import get_current_user
            user, error = get_current_user()
            if error:
                from utils.api_response import unauthorized
                return unauthorized(error)
            
            if user.role not in roles:
                from utils.api_response import forbidden
                return forbidden(f"This action requires one of: {', '.join(roles)}")
            
            g.current_user = user
            return f(*args, **kwargs)
        return decorated
    return decorator
