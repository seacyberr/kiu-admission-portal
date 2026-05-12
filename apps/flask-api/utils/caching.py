"""
Caching System for KIU Admission Portal

Provides intelligent caching with Redis backend for frequently accessed data
and configurable cache invalidation strategies.
"""

import json
import logging
import hashlib
import os
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Union, List
from functools import wraps
from flask import request, g
import redis
import pickle

logger = logging.getLogger(__name__)

class CacheManager:
    """
    Advanced caching system with Redis backend, connection pooling,
    and intelligent invalidation with fallback to in-memory cache.
    """
    
    def __init__(self, redis_url: str = None, default_ttl: int = 300):
        self.redis_client = None
        self.redis_pool = None
        self.memory_cache = {}  # Fallback in-memory cache
        self.default_ttl = default_ttl  # 5 minutes default
        self._redis_available = False
        
        # Get Redis URL from environment if not provided
        if not redis_url:
            redis_url = os.environ.get('REDIS_URL') or os.environ.get('CACHE_REDIS_URL')
        
        if redis_url:
            try:
                # Create connection pool for better performance
                self.redis_pool = redis.ConnectionPool.from_url(
                    redis_url, 
                    decode_responses=True,
                    max_connections=20,
                    socket_connect_timeout=3,
                    socket_timeout=3,
                    retry_on_timeout=True,
                    health_check_interval=30
                )
                self.redis_client = redis.Redis(connection_pool=self.redis_pool)
                # Test the connection
                self.redis_client.ping()
                self._redis_available = True
                logger.info("Connected to Redis for caching (connection pool: 20 max)")
            except Exception as e:
                logger.warning(f"Redis not available, using in-memory cache: {e}")
                self.redis_client = None
                self.redis_pool = None
        else:
            logger.debug("No Redis URL configured, using in-memory cache")
        
        # Log cache backend status
        if self.redis_client:
            logger.info("Cache backend: Redis")
        else:
            logger.info("Cache backend: In-memory (Redis not configured)")
    
    def _generate_key(self, prefix: str, identifier: str, *args) -> str:
        """Generate cache key with prefix and identifier"""
        key_parts = [prefix, identifier]
        key_parts.extend(str(arg) for arg in args)
        return ":".join(key_parts)
    
    def _serialize_value(self, value: Any) -> str:
        """Serialize value for storage"""
        try:
            return pickle.dumps(value)
        except Exception as e:
            logger.error(f"Failed to serialize cache value: {e}")
            return json.dumps(value)  # Fallback to JSON
    
    def _deserialize_value(self, value: bytes) -> Any:
        """Deserialize value from storage"""
        try:
            return pickle.loads(value)
        except Exception as e:
            logger.error(f"Failed to deserialize cache value: {e}")
            try:
                return json.loads(value.decode())  # Fallback to JSON
            except:
                return None
    
    def health_check(self) -> dict:
        """Check cache backend health"""
        if not self._redis_available or not self.redis_client:
            return {
                "status": "fallback",
                "backend": "in-memory",
                "healthy": True,
                "message": "Using in-memory cache (Redis not configured)"
            }
        
        try:
            info = self.redis_client.info()
            return {
                "status": "connected",
                "backend": "redis",
                "healthy": True,
                "version": info.get("redis_version"),
                "used_memory": info.get("used_memory_human"),
                "connected_clients": info.get("connected_clients"),
                "pool_size": self.redis_pool.max_connections if self.redis_pool else 0
            }
        except Exception as e:
            return {
                "status": "error",
                "backend": "redis",
                "healthy": False,
                "error": str(e)
            }
    
    def get_stats(self) -> dict:
        """Get cache statistics"""
        if not self._redis_available or not self.redis_client:
            return {
                "backend": "in-memory",
                "keys_in_memory": len(self.memory_cache)
            }
        
        try:
            info = self.redis_client.info()
            return {
                "backend": "redis",
                "keys_total": self.redis_client.dbsize(),
                "hits": info.get("keyspace_hits", 0),
                "misses": info.get("keyspace_misses", 0),
                "hit_rate": self._calculate_hit_rate(info),
                "memory_used": info.get("used_memory_human"),
                "evicted_keys": info.get("evicted_keys", 0)
            }
        except Exception as e:
            return {"error": str(e)}
    
    def _calculate_hit_rate(self, info: dict) -> float:
        """Calculate cache hit rate percentage"""
        hits = info.get("keyspace_hits", 0)
        misses = info.get("keyspace_misses", 0)
        total = hits + misses
        if total == 0:
            return 0.0
        return round((hits / total) * 100, 2)
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get value from cache
        
        Args:
            key: Cache key
            default: Default value if not found
            
        Returns:
            Cached value or default
        """
        if not self.redis_client:
            return self.memory_cache.get(key, default)
        
        try:
            value = self.redis_client.get(key)
            if value is not None:
                return self._deserialize_value(value)
            return default
        except Exception as e:
            logger.error(f"Cache get failed: {e}")
            return default
    
    def set(self, key: str, value: Any, ttl: int = None) -> bool:
        """
        Set value in cache
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds
            
        Returns:
            True if successful, False otherwise
        """
        if ttl is None:
            ttl = self.default_ttl
        
        if not self.redis_client:
            self.memory_cache[key] = value
            return True
        
        try:
            serialized = self._serialize_value(value)
            result = self.redis_client.setex(key, ttl, serialized)
            return result
        except Exception as e:
            logger.warning(f"Cache set failed (using memory): {e}")
            # Store in memory cache as fallback
            self.memory_cache[key] = value
            return True
    
    def delete(self, key: str) -> bool:
        """
        Delete value from cache
        
        Args:
            key: Cache key to delete
            
        Returns:
            True if successful, False otherwise
        """
        if not self.redis_client:
            self.memory_cache.pop(key, None)
            return True
        
        try:
            result = self.redis_client.delete(key)
            return result
        except Exception as e:
            logger.error(f"Cache delete failed: {e}")
            return False
    
    def delete_pattern(self, pattern: str) -> int:
        """
        Delete multiple keys matching pattern
        
        Args:
            pattern: Pattern to match keys
            
        Returns:
            Number of keys deleted
        """
        if not self.redis_client:
            keys_to_delete = [k for k in self.memory_cache.keys() if pattern in k]
            for key in keys_to_delete:
                self.memory_cache.pop(key, None)
            return len(keys_to_delete)
        
        try:
            keys = self.redis_client.keys(pattern)
            if keys:
                return self.redis_client.delete(*keys)
            return 0
        except Exception as e:
            logger.error(f"Cache pattern delete failed: {e}")
            return 0
    
    def exists(self, key: str) -> bool:
        """
        Check if key exists in cache
        
        Args:
            key: Cache key to check
            
        Returns:
            True if key exists, False otherwise
        """
        if not self.redis_client:
            return key in self.memory_cache
        
        try:
            return bool(self.redis_client.exists(key))
        except Exception as e:
            logger.error(f"Cache exists check failed: {e}")
            return False

# Global cache manager instance
cache_manager = CacheManager()

def cache_key(prefix: str, *args):
    """
    Decorator to generate cache key from function arguments
    
    Args:
        prefix: Cache key prefix
        *args: Arguments to include in key
        
    Returns:
        Decorator function
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*func_args, **func_kwargs):
            # Generate key from function name and arguments
            identifier = f"{func.__name__}:{hash(str(func_args) + str(sorted(func_kwargs.items())))}"
            return cache_manager._generate_key(prefix, identifier, *args)
        return wrapper
    return decorator

def cached_result(ttl: int = 300, key_prefix: str = "result"):
    """
    Decorator for caching function results
    
    Args:
        ttl: Time to live in seconds
        key_prefix: Prefix for cache key
        
    Returns:
        Decorator function
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            cache_key = cache_manager._generate_key(key_prefix, func.__name__, str(args), str(sorted(kwargs.items())))
            
            # Try to get from cache
            cached = cache_manager.get(cache_key)
            if cached is not None:
                logger.debug(f"Cache hit for {func.__name__}")
                return cached
            
            # Execute function and cache result
            logger.debug(f"Cache miss for {func.__name__}, executing function")
            result = func(*args, **kwargs)
            
            # Cache the result
            cache_manager.set(cache_key, result, ttl)
            return result
        
        return wrapper
    return decorator

def invalidate_cache_pattern(pattern: str):
    """
    Invalidate cache entries matching pattern
    
    Args:
        pattern: Pattern to match for invalidation
    """
    deleted_count = cache_manager.delete_pattern(pattern)
    logger.info(f"Invalidated {deleted_count} cache entries matching pattern: {pattern}")

def get_cache_stats() -> Dict[str, Any]:
    """
    Get cache statistics
    
    Returns:
        Dictionary with cache statistics
    """
    if not cache_manager.redis_client:
        return {
            "backend": "memory",
            "keys_count": len(cache_manager.memory_cache),
            "message": "Using in-memory cache"
        }
    
    try:
        info = cache_manager.redis_client.info()
        return {
            "backend": "redis",
            "connected_clients": info.get("connected_clients", 0),
            "used_memory": info.get("used_memory", 0),
            "used_memory_human": f"{info.get('used_memory', 0) / 1024 / 1024:.2f} MB",
            "total_system_memory": info.get("total_system_memory", 0),
            "keys_count": info.get("db0", 0),
            "hits": info.get("keyspace_hits", 0),
            "misses": info.get("keyspace_misses", 0),
            "hit_rate": 0.0,
            "uptime": info.get("uptime_in_seconds", 0)
        }
    except Exception as e:
        logger.error(f"Failed to get cache stats: {e}")
        return {"backend": "error", "message": str(e)}

def cache_program_list(ttl: int = 3600):
    """
    Cache program list for extended period
    
    Args:
        ttl: Time to live in seconds (default 1 hour)
        
    Returns:
        Decorator function
    """
    return cached_result(ttl=ttl, key_prefix="programs")

def cache_user_data(ttl: int = 1800):
    """
    Cache user data for extended period
    
    Args:
        ttl: Time to live in seconds (default 30 minutes)
        
    Returns:
        Decorator function
    """
    return cached_result(ttl=ttl, key_prefix="user")

def cache_recommendations(ttl: int = 600):
    """
    Cache recommendations for moderate period
    
    Args:
        ttl: Time to live in seconds (default 10 minutes)
        
    Returns:
        Decorator function
    """
    return cached_result(ttl=ttl, key_prefix="recommendations")

def cache_application_status(ttl: int = 300):
    """
    Cache application status for moderate period
    
    Args:
        ttl: Time to live in seconds (default 5 minutes)
        
    Returns:
        Decorator function
    """
    return cached_result(ttl=ttl, key_prefix="application_status")

def cache_nche_standards(ttl: int = 7200):
    """
    Cache NCHE standards for extended period
    
    Args:
        ttl: Time to live in seconds (default 2 hours)
        
    Returns:
        Decorator function
    """
    return cached_result(ttl=ttl, key_prefix="nche_standards")

def cache_verification_results(ttl: int = 1800):
    """
    Cache verification results for moderate period
    
    Args:
        ttl: Time to live in seconds (default 30 minutes)
        
    Returns:
        Decorator function
    """
    return cached_result(ttl=ttl, key_prefix="verification_results")

def invalidate_user_cache(user_id: str):
    """
    Invalidate all cache entries for a specific user
    
    Args:
        user_id: User ID to invalidate cache for
    """
    patterns = [
        f"user:*:{user_id}",
        f"application_status:*:{user_id}",
        f"recommendations:*:{user_id}"
    ]
    
    for pattern in patterns:
        invalidate_cache_pattern(pattern)
    
    logger.info(f"Invalidated cache for user {user_id}")

def invalidate_program_cache():
    """
    Invalidate program-related cache entries
    """
    patterns = [
        "programs:*",
        "nche_standards:*"
    ]
    
    for pattern in patterns:
        invalidate_cache_pattern(pattern)
    
    logger.info("Invalidated program cache")

def warm_cache():
    """
    Warm up cache with frequently accessed data
    """
    logger.info("Starting cache warm-up")
    
    # Warm up common cache entries
    warmup_data = {
        "nche_standards": {
            "uce_grades_old": ["D1", "D2", "C3", "C4", "C5", "C6", "P7", "P8", "F9"],
            "uce_grades_new": ["D1", "D2", "D3", "D4", "D5", "D6", "D7", "D8", "F"],
            "uace_grades": ["A", "B", "C", "D", "E", "O", "F"],
            "valid_subjects": {
                "uce": ["English Language", "Mathematics", "Physics", "Chemistry", "Biology"],
                "uace_principal": ["Mathematics", "Physics", "Chemistry", "Biology"]
            }
        }
    }
    
    for key, data in warmup_data.items():
        cache_key = cache_manager._generate_key("warmup", key)
        cache_manager.set(cache_key, data, ttl=3600)  # 1 hour
    
    logger.info("Cache warm-up completed")

class CacheMiddleware:
    """
    Flask middleware for cache management
    """
    
    def __init__(self, app):
        self.app = app
    
    def init_app(self, app):
        """Initialize cache middleware"""
        app.before_request(self.before_request)
        app.after_request(self.after_request)
    
    def before_request(self):
        """Add cache information to request context"""
        g.cache_info = {
            "hit": False,
            "key": None,
            "ttl": None
        }
    
    def after_request(self, response):
        """Add cache headers if response was cached"""
        if hasattr(g, 'cache_info') and g.cache_info.get('hit'):
            response.headers['X-Cache'] = 'HIT'
            response.headers['X-Cache-Key'] = g.cache_info.get('key', '')
            response.headers['X-Cache-TTL'] = str(g.cache_info.get('ttl', ''))
        return response
