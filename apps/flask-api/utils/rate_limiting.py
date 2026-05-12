"""
Enhanced Rate Limiting System for KIU Admission Portal

Provides intelligent rate limiting with different tiers for different endpoints
and user types, with Redis backend for distributed systems.
"""

import time
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple
from functools import wraps
from flask import request, jsonify, g
from flask_limiter import Limiter
from redis import Redis, ConnectionPool
import hashlib

logger = logging.getLogger(__name__)

class AdvancedRateLimiter:
    """
    Advanced rate limiting with Redis backend and intelligent limits
    """
    
    def __init__(self, redis_url: str = None):
        self.redis_client = None
        if redis_url:
            try:
                self.redis_client = Redis.from_url(redis_url, decode_responses=True)
                logger.info("Connected to Redis for rate limiting")
            except Exception as e:
                logger.warning(f"Redis connection failed, falling back to memory: {e}")
                self.redis_client = None
    
    def get_client_ip(self) -> str:
        """Get client IP with proxy support"""
        # Check for forwarded headers
        if request.headers.getlist("X-Forwarded-For"):
            return request.headers.get("X-Forwarded-For").split(",")[0].strip()
        elif request.headers.get("X-Real-IP"):
            return request.headers.get("X-Real-IP")
        else:
            return request.remote_addr or "127.0.0.1"
    
    def get_user_identifier(self) -> str:
        """Get unique identifier for rate limiting using Flask g object"""
        # Use Flask g object to avoid circular import from routes.auth
        user = getattr(g, 'current_user', None)
        if user and hasattr(user, 'id'):
            return f"user:{user.id}"
        else:
            return f"ip:{self.get_client_ip()}"
    
    def get_rate_limits(self, endpoint: str, user_role: str = None) -> Dict[str, int]:
        """
        Get rate limits based on endpoint and user role
        
        Args:
            endpoint: API endpoint path
            user_role: User role (applicant, admin, etc.)
            
        Returns:
            Dictionary of rate limits (requests per time window)
        """
        # Base limits for all users
        base_limits = {
            "window": 300,      # 5 minutes
            "requests": 50,     # 50 requests per 5 minutes
        }
        
        # Endpoint-specific limits
        endpoint_limits = {
            # Authentication endpoints - stricter limits
            "/api/auth/login": {"window": 300, "requests": 5},
            "/api/auth/register": {"window": 300, "requests": 3},
            "/api/auth/forgot-password": {"window": 900, "requests": 3},
            
            # Application endpoints - moderate limits
            "/api/admission/applications": {"window": 3600, "requests": 3},
            "/api/admission/applications/*/certificate": {"window": 300, "requests": 10},
            
            # Recommendation endpoints - higher limits for better UX
            "/api/recommendations": {"window": 300, "requests": 20},
            "/api/recommend": {"window": 300, "requests": 15},
            
            # Certificate verification - moderate limits
            "/api/certificate-verification/verify": {"window": 300, "requests": 5},
            "/api/certificate-verification/verify-with-data": {"window": 300, "requests": 10},
        }
        
        # Role-based adjustments
        role_multipliers = {
            "admin": 2.0,      # Admins get 2x limit
            "staff": 1.5,      # Staff get 1.5x limit
            "applicant": 1.0,   # Applicants get standard limit
            "anonymous": 0.5,   # Anonymous users get 0.5x limit
        }
        
        # Get the most specific limit
        limit_key = None
        for endpoint_pattern in endpoint_limits:
            if endpoint.startswith(endpoint_pattern):
                limit_key = endpoint_pattern
                break
        
        if limit_key:
            limits = endpoint_limits[limit_key].copy()
        else:
            limits = base_limits.copy()
        
        # Apply role-based multiplier
        multiplier = role_multipliers.get(user_role, 1.0)
        limits["requests"] = int(limits["requests"] * multiplier)
        
        return limits
    
    def check_rate_limit_redis(self, key: str, limits: Dict[str, int]) -> Tuple[bool, Dict]:
        """
        Check rate limit using Redis
        
        Args:
            key: Rate limit key
            limits: Rate limit configuration
            
        Returns:
            Tuple of (allowed, info_dict)
        """
        if not self.redis_client:
            return True, {"message": "Rate limiting disabled (no Redis)"}
        
        try:
            current_time = int(time.time())
            window_start = current_time - limits["window"]
            
            # Clean old entries
            self.redis_client.zremrangebyscore(key, 0, window_start)
            
            # Count current requests
            current_requests = self.redis_client.zcard(key)
            
            # Calculate remaining requests and reset time
            remaining = max(0, limits["requests"] - current_requests)
            reset_time = current_time + limits["window"]
            
            # Add current request to counter
            self.redis_client.zadd(key, {str(current_time): current_time})
            self.redis_client.expire(key, limits["window"])
            
            allowed = current_requests < limits["requests"]
            
            info = {
                "limit": limits["requests"],
                "remaining": remaining,
                "reset": reset_time,
                "retry_after": limits["window"] if not allowed else 0,
                "current": current_requests
            }
            
            return allowed, info
            
        except Exception as e:
            logger.error(f"Rate limit check failed: {e}")
            return True, {"message": "Rate limit check failed"}
    
    def get_rate_limit_headers(self, info: Dict) -> Dict[str, str]:
        """
        Generate rate limit headers for response
        
        Args:
            info: Rate limit information
            
        Returns:
            Dictionary of headers
        """
        headers = {}
        
        if "limit" in info:
            headers["X-RateLimit-Limit"] = str(info["limit"])
        if "remaining" in info:
            headers["X-RateLimit-Remaining"] = str(info["remaining"])
        if "reset" in info:
            headers["X-RateLimit-Reset"] = str(info["reset"])
        if "retry_after" in info:
            headers["Retry-After"] = str(info["retry_after"])
        
        return headers

# Global rate limiter instance
rate_limiter = AdvancedRateLimiter()

def rate_limit(
    endpoint_limits: Dict[str, Dict[str, int]] = None,
    key_func: callable = None,
    error_message: str = "Rate limit exceeded"
):
    """
    Decorator for applying rate limits to endpoints
    
    Args:
        endpoint_limits: Custom limits for specific endpoints
        key_func: Function to generate rate limit key
        error_message: Custom error message
        
    Returns:
        Decorated function
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            from flask import g
            
            # Get user info for rate limiting
            user_identifier = rate_limiter.get_user_identifier()
            
            # Determine user role
            user_role = "anonymous"
            if hasattr(g, 'current_user') and g.current_user:
                if hasattr(g.current_user, 'role'):
                    user_role = g.current_user.role
                elif not g.current_user.is_anonymous:
                    user_role = "applicant"
            
            # Get limits for this endpoint
            endpoint = request.endpoint or request.path
            limits = endpoint_limits.get(endpoint, None)
            if limits is None:
                limits = rate_limiter.get_rate_limits(endpoint, user_role)
            
            # Generate rate limit key
            if key_func:
                rate_key = key_func(*args, **kwargs)
            else:
                key_parts = [user_identifier, endpoint]
                rate_key = ":".join(key_parts)
                rate_key = hashlib.md5(rate_key.encode()).hexdigest()
            
            # Check rate limit
            allowed, info = rate_limiter.check_rate_limit_redis(rate_key, limits)
            
            if not allowed:
                # Add rate limit headers
                headers = rate_limiter.get_rate_limit_headers(info)
                
                return jsonify({
                    "error": "RATE_LIMIT_EXCEEDED",
                    "message": error_message,
                    "details": info,
                    "timestamp": datetime.utcnow().isoformat()
                }), 429, headers
            
            # Store rate limit info in context for potential use
            g.rate_limit_info = info
            
            return func(*args, **kwargs)
        
        return wrapper
    
    return decorator

def apply_rate_limits(app):
    """
    Apply rate limits to Flask application
    
    Args:
        app: Flask application instance
    """
    # Configure Flask-Limiter with Redis
    if rate_limiter.redis_client:
        try:
            limiter = Limiter(
                app,
                key_func=rate_limiter.get_user_identifier,
                storage_uri="redis://localhost:6379",
                default_limits=["1000 per hour", "10000 per day"]
            )
            logger.info("Advanced rate limiting initialized with Redis")
        except Exception as e:
            logger.warning(f"Failed to initialize Redis rate limiting: {e}")
    
    # Apply custom rate limits to specific endpoints
    @app.before_request
    def check_rate_limits():
        # Skip rate limiting for health checks and static files
        if request.path.startswith('/api/health') or request.path.startswith('/static'):
            return
        
        # Get user for role-based limits
        user_role = "anonymous"
        if hasattr(g, 'current_user') and g.current_user:
            if hasattr(g.current_user, 'role'):
                user_role = g.current_user.role
            elif not g.current_user.is_anonymous:
                user_role = "applicant"
        
        # Check if this endpoint has custom limits
        endpoint = request.endpoint or request.path
        custom_limits = rate_limiter.get_rate_limits(endpoint, user_role)
        
        # Store in context for middleware
        g.rate_limits = custom_limits

def create_rate_limit_response(info: Dict[str, int]) -> Tuple[dict, int]:
    """
    Create standardized rate limit response
    
    Args:
        info: Rate limit information
        
    Returns:
        Tuple of (response_dict, status_code)
    """
    response_data = {
        "error": "RATE_LIMIT_EXCEEDED",
        "message": "Rate limit exceeded. Please try again later.",
        "details": {
            "limit": info.get("limit", 0),
            "remaining": info.get("remaining", 0),
            "reset": info.get("reset", 0),
            "retry_after": info.get("retry_after", 60),
            "current": info.get("current", 0)
        },
        "timestamp": datetime.utcnow().isoformat()
    }
    
    headers = rate_limiter.get_rate_limit_headers(info)
    
    return response_data, 429, headers

def log_rate_limit_violation(endpoint: str, user_id: str, info: Dict):
    """
    Log rate limit violations for monitoring
    
    Args:
        endpoint: API endpoint that was rate limited
        user_id: User identifier
        info: Rate limit information
    """
    log_data = {
        "endpoint": endpoint,
        "user_id": user_id,
        "limit": info.get("limit", 0),
        "current": info.get("current", 0),
        "timestamp": datetime.utcnow().isoformat(),
        "ip_address": rate_limiter.get_client_ip()
    }
    
    logger.warning(f"Rate limit violation: {json.dumps(log_data)}")

# Predefined rate limit decorators for common use cases
auth_rate_limit = rate_limit(
    endpoint_limits={
        "auth.login": {"window": 300, "requests": 5},
        "auth.register": {"window": 300, "requests": 3},
    },
    error_message="Too many authentication attempts. Please try again later."
)

application_rate_limit = rate_limit(
    endpoint_limits={
        "admission.create_application": {"window": 3600, "requests": 3},
        "admission.upload_certificate": {"window": 300, "requests": 10},
    },
    error_message="Application rate limit exceeded. Please wait before trying again."
)

recommendation_rate_limit = rate_limit(
    endpoint_limits={
        "recommendations.get_recommendations": {"window": 300, "requests": 20},
        "recommendations.recommend_programs": {"window": 300, "requests": 15},
    },
    error_message="Recommendation rate limit exceeded. Please wait before trying again."
)

certificate_verification_rate_limit = rate_limit(
    endpoint_limits={
        "certificate_verification.verify_certificate": {"window": 300, "requests": 5},
        "certificate_verification.verify_with_data": {"window": 300, "requests": 10},
    },
    error_message="Certificate verification rate limit exceeded. Please wait before trying again."
)

admin_rate_limit = rate_limit(
    endpoint_limits={
        # Admin endpoints get higher limits
            "default": {"window": 300, "requests": 100},
        },
    error_message="Admin rate limit exceeded. Please wait before trying again."
)
