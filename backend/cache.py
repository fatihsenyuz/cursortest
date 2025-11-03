"""
Redis Cache Helper Module
"""
import json
import os
from typing import Optional, Any
from functools import wraps
import logging

logger = logging.getLogger(__name__)

# Try to import redis, but make it optional
try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    logger.warning("Redis module not found. Cache functionality will be disabled.")

# Redis connection
redis_client = None

def init_redis():
    """Initialize Redis connection"""
    global redis_client
    
    if not REDIS_AVAILABLE:
        logger.info("Redis module not available. Cache functionality disabled.")
        redis_client = None
        return
    
    try:
        redis_url = os.environ.get('REDIS_URL', 'redis://localhost:6379')
        redis_client = redis.from_url(redis_url, decode_responses=True)
        # Test connection
        redis_client.ping()
        logger.info("Redis connection established")
    except Exception as e:
        logger.warning(f"Redis connection failed: {e}. Cache will be disabled.")
        redis_client = None

def get_cache_key(prefix: str, key: str) -> str:
    """Generate cache key"""
    return f"royal:{prefix}:{key}"

def cache_result(prefix: str, ttl: int = 300):
    """
    Decorator to cache function results
    
    Args:
        prefix: Cache key prefix
        ttl: Time to live in seconds (default 5 minutes)
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Skip caching if Redis is not available
            if redis_client is None:
                return await func(*args, **kwargs)
            
            # Generate cache key from function arguments
            cache_key = get_cache_key(prefix, f"{func.__name__}:{str(args)}:{str(kwargs)}")
            
            try:
                # Try to get from cache
                cached_result = redis_client.get(cache_key)
                if cached_result is not None:
                    logger.debug(f"Cache hit: {cache_key}")
                    return json.loads(cached_result)
                
                # Execute function
                result = await func(*args, **kwargs)
                
                # Store in cache
                redis_client.setex(cache_key, ttl, json.dumps(result, default=str))
                logger.debug(f"Cache miss, stored: {cache_key}")
                
                return result
            except Exception as e:
                logger.error(f"Cache error: {e}")
                # Fallback to function execution
                return await func(*args, **kwargs)
        
        return wrapper
    return decorator

def invalidate_cache(prefix: str, pattern: str = None):
    """
    Invalidate cache entries
    
    Args:
        prefix: Cache key prefix
        pattern: Optional pattern to match specific keys
    """
    if redis_client is None:
        return
    
    try:
        if pattern:
            cache_key = get_cache_key(prefix, pattern)
            deleted = redis_client.delete(cache_key)
        else:
            # Delete all keys with this prefix
            pattern_key = f"royal:{prefix}:*"
            keys = redis_client.keys(pattern_key)
            if keys:
                deleted = redis_client.delete(*keys)
            else:
                deleted = 0
        
        logger.info(f"Invalidated {deleted} cache entries for prefix: {prefix}")
    except Exception as e:
        logger.error(f"Cache invalidation error: {e}")

