"""
Decorators for DRY (Don't Repeat Yourself) code
Common authentication and validation patterns
"""
from functools import wraps
from flask import jsonify, request
from routes.auth import get_current_user


def require_auth(roles=None):
    """
    Decorator to require authentication
    Optionally restrict to specific roles
    
    Usage:
        @require_auth()  # Any authenticated user
        @require_auth(roles=['admin'])  # Admin only
        @require_auth(roles=['admin', 'staff'])  # Admin or staff
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            user, error = get_current_user()
            
            if error:
                return jsonify({"error": "Unauthorized", "message": error}), 401
            
            if roles and user.role not in roles:
                return jsonify({"error": "Forbidden", "message": "Insufficient permissions"}), 403
            
            # Add user to kwargs for the route to use
            kwargs['current_user'] = user
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def require_admin(f):
    """Shortcut decorator for admin-only routes"""
    @wraps(f)
    @require_auth(roles=['admin'])
    def decorated_function(*args, **kwargs):
        return f(*args, **kwargs)
    return decorated_function


def require_finalist(f):
    """Shortcut decorator for finalist-only routes"""
    @wraps(f)
    @require_auth(roles=['finalist', 'admin'])
    def decorated_function(*args, **kwargs):
        return f(*args, **kwargs)
    return decorated_function


def validate_json(required_fields=None, optional_fields=None):
    """
    Decorator to validate JSON payload
    
    Usage:
        @validate_json(required_fields=['name', 'email'])
        @validate_json(required_fields=['title'], optional_fields=['description'])
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            data = request.get_json()
            
            if data is None:
                return jsonify({"error": "Bad Request", "message": "JSON payload required"}), 400
            
            # Check required fields
            if required_fields:
                missing = [field for field in required_fields if field not in data]
                if missing:
                    return jsonify({
                        "error": "Bad Request", 
                        "message": f"Missing required fields: {', '.join(missing)}"
                    }), 400
            
            # Add validated data to kwargs
            kwargs['validated_data'] = data
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def paginate(default_per_page=20, max_per_page=100):
    """
    Decorator to handle pagination parameters
    Adds 'page' and 'per_page' to kwargs
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', default_per_page, type=int)
            
            # Validate pagination params
            if page < 1:
                page = 1
            if per_page < 1:
                per_page = default_per_page
            if per_page > max_per_page:
                per_page = max_per_page
            
            kwargs['page'] = page
            kwargs['per_page'] = per_page
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def handle_exceptions(f):
    """
    Decorator to catch and handle exceptions uniformly
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except ValueError as e:
            return jsonify({"error": "Bad Request", "message": str(e)}), 400
        except PermissionError as e:
            return jsonify({"error": "Forbidden", "message": str(e)}), 403
        except LookupError as e:
            return jsonify({"error": "Not Found", "message": str(e)}), 404
        except Exception as e:
            # Log the full error
            import logging
            logging.error(f"Unhandled exception in {f.__name__}: {str(e)}", exc_info=True)
            return jsonify({"error": "Internal Server Error", "message": "An unexpected error occurred"}), 500
    return decorated_function
