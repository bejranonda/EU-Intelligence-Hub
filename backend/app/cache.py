"""Caching utilities and strategies."""
import json
import logging
from typing import Any, Optional, Callable
from datetime import timedelta
from functools import wraps
import hashlib
from app.config import get_settings
import redis

logger = logging.getLogger(__name__)

settings = get_settings()


class CacheManager:
    """Redis-based cache manager."""

    def __init__(self, redis_url: str = None, default_ttl: int = 3600):
        """
        Initialize cache manager.
        
        Args:
            redis_url: Redis connection URL
            default_ttl: Default time-to-live in seconds
        """
        self.redis_url = redis_url or settings.redis_url
        try:
            self.redis_client = redis.from_url(self.redis_url)
            self.redis_client.ping()
            self.available = True
            logger.info("Cache manager initialized successfully")
        except Exception as e:
            logger.warning(f"Cache manager initialization failed: {e}. Using no-op cache.")
            self.available = False
            self.redis_client = None
        
        self.default_ttl = default_ttl

    def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        if not self.available:
            return None
        
        try:
            value = self.redis_client.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            logger.error(f"Cache get error: {e}")
            return None

    def set(self, key: str, value: Any, ttl: int = None) -> bool:
        """Set value in cache."""
        if not self.available:
            return False
        
        try:
            ttl = ttl or self.default_ttl
            self.redis_client.setex(
                key,
                ttl,
                json.dumps(value, default=str)
            )
            return True
        except Exception as e:
            logger.error(f"Cache set error: {e}")
            return False

    def delete(self, key: str) -> bool:
        """Delete value from cache."""
        if not self.available:
            return False
        
        try:
            self.redis_client.delete(key)
            return True
        except Exception as e:
            logger.error(f"Cache delete error: {e}")
            return False

    def clear_pattern(self, pattern: str) -> int:
        """Clear all keys matching pattern."""
        if not self.available:
            return 0
        
        try:
            keys = self.redis_client.keys(pattern)
            if keys:
                return self.redis_client.delete(*keys)
            return 0
        except Exception as e:
            logger.error(f"Cache clear error: {e}")
            return 0

    def get_stats(self) -> dict:
        """Get cache statistics."""
        if not self.available:
            return {"status": "unavailable"}
        
        try:
            info = self.redis_client.info()
            return {
                "status": "available",
                "used_memory_mb": info.get("used_memory", 0) / (1024 * 1024),
                "connected_clients": info.get("connected_clients", 0),
                "total_commands": info.get("total_commands_processed", 0),
                "expired_keys": info.get("expired_keys", 0),
            }
        except Exception as e:
            logger.error(f"Cache stats error: {e}")
            return {"status": "error"}


# Global cache instance
_cache_manager: Optional[CacheManager] = None


def get_cache() -> CacheManager:
    """Get or create cache manager instance."""
    global _cache_manager
    if _cache_manager is None:
        _cache_manager = CacheManager()
    return _cache_manager


def cache_key(*args, **kwargs) -> str:
    """Generate cache key from function arguments."""
    key_data = str(args) + str(sorted(kwargs.items()))
    return hashlib.md5(key_data.encode()).hexdigest()


def cached(ttl: int = 3600, key_prefix: str = ""):
    """
    Decorator to cache function results.
    
    Args:
        ttl: Time-to-live in seconds
        key_prefix: Prefix for cache key
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            cache = get_cache()
            
            # Generate cache key
            func_name = func.__module__ + "." + func.__name__
            key = f"{key_prefix}:{func_name}:{cache_key(*args, **kwargs)}"
            
            # Try to get from cache
            cached_value = cache.get(key)
            if cached_value is not None:
                logger.debug(f"Cache hit: {key}")
                return cached_value
            
            # Call function and cache result
            result = await func(*args, **kwargs)
            cache.set(key, result, ttl)
            logger.debug(f"Cache miss and set: {key}")
            
            return result
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            cache = get_cache()
            
            # Generate cache key
            func_name = func.__module__ + "." + func.__name__
            key = f"{key_prefix}:{func_name}:{cache_key(*args, **kwargs)}"
            
            # Try to get from cache
            cached_value = cache.get(key)
            if cached_value is not None:
                logger.debug(f"Cache hit: {key}")
                return cached_value
            
            # Call function and cache result
            result = func(*args, **kwargs)
            cache.set(key, result, ttl)
            logger.debug(f"Cache miss and set: {key}")
            
            return result
        
        # Return async or sync wrapper based on function
        if hasattr(func, '__code__') and 'async' in func.__code__.co_names:
            return async_wrapper
        return sync_wrapper
    
    return decorator


class CacheInvalidationManager:
    """Manages cache invalidation strategies."""

    @staticmethod
    def invalidate_related_caches(entity_type: str, entity_id: int = None) -> int:
        """
        Invalidate all caches related to an entity.
        
        Args:
            entity_type: Type of entity (e.g., 'keyword', 'sentiment')
            entity_id: Optional entity ID for specific invalidation
            
        Returns:
            Number of cache keys invalidated
        """
        cache = get_cache()
        
        patterns = {
            'keyword': [
                f"*:*get_keyword*",
                f"*:*list_keywords*",
                f"*:*search_keywords*",
            ],
            'sentiment': [
                f"*:*get_sentiment*",
                f"*:*sentiment_trend*",
                f"*:*sentiment_stats*",
            ],
            'search': [
                f"*:*semantic_search*",
                f"*:*keyword_search*",
            ],
        }
        
        invalidated = 0
        
        if entity_type in patterns:
            for pattern in patterns[entity_type]:
                invalidated += cache.clear_pattern(pattern)
        
        if entity_id:
            # Invalidate specific entity cache
            specific_pattern = f"*:*{entity_type}*{entity_id}*"
            invalidated += cache.clear_pattern(specific_pattern)
        
        logger.info(f"Invalidated {invalidated} cache keys for {entity_type}")
        return invalidated
