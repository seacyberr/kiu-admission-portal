"""
CSRF Protection - Double-Submit Cookie Pattern
OWASP recommended approach for SPA with cookie-based auth
"""
import secrets
import hmac
import hashlib
from functools import wraps
from flask import request, jsonify, current_app, g


def generate_csrf_token():
    """Generate new CSRF token"""
    return secrets.token_urlsafe(32)


def set_csrf_cookie(response):
    """Set CSRF token in cookie (not httpOnly - JS needs to read it)"""
    token = generate_csrf_token()
    is_prod = current_app.config.get('ENV') == 'production'
    
    response.set_cookie(
        'csrf_token',
        token,
        secure=is_prod,
        samesite='Strict',
        max_age=86400,  # 24 hours
        path='/'
    )
    
    # Also store in session for validation
    g.csrf_token = token
    return response


def validate_csrf_token():
    """Validate CSRF token from header against cookie"""
    # Skip for safe methods
    if request.method in ('GET', 'HEAD', 'OPTIONS', 'TRACE'):
        return True
    
    # Skip if no cookie set yet (first request)
    cookie_token = request.cookies.get('csrf_token')
    if not cookie_token:
        return True  # Let it through, will set on response
    
    # Check header
    header_token = request.headers.get('X-CSRF-Token')
    if not header_token:
        return False
    
    # Constant-time comparison to prevent timing attacks
    return hmac.compare_digest(cookie_token, header_token)


def csrf_protect(f):
    """Decorator to enforce CSRF protection on state-changing endpoints"""
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not validate_csrf_token():
            return jsonify({
                "status": "error",
                "message": "CSRF token missing or invalid",
                "error": {
                    "code": "CSRF_ERROR",
                    "hint": "Include X-CSRF-Token header matching the csrf_token cookie"
                }
            }), 403
        return f(*args, **kwargs)
    return wrapper


def init_csrf(app):
    """Initialize CSRF protection on app"""
    
    @app.after_request
    def add_csrf_cookie(response):
        # Set CSRF cookie on auth-related responses if not present
        if request.path.startswith('/api/auth') and not request.cookies.get('csrf_token'):
            response = set_csrf_cookie(response)
        return response
