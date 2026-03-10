"""
Simple file-based cache with TTL support.

Provides caching functionality to reduce redundant API calls during development.
"""

import json
import logging
import os
import time
from pathlib import Path
from typing import Any, Optional, Callable
from functools import wraps


logger = logging.getLogger(__name__)


class FileCache:
    """Simple file-based cache with TTL support."""
    
    def __init__(self, cache_dir: Optional[Path] = None, default_ttl: int = 300):
        """
        Initialize file cache.
        
        Args:
            cache_dir: Directory for cache files. Defaults to ~/.cache/work_summary
            default_ttl: Default TTL in seconds (5 minutes)
        """
        if cache_dir is None:
            cache_dir = Path.home() / '.cache' / 'work_summary'
        
        self.cache_dir = Path(cache_dir)
        self.default_ttl = default_ttl
        
        # Create cache directory if it doesn't exist
        self.cache_dir.mkdir(parents=True, exist_ok=True)
    
    def _get_cache_path(self, key: str) -> Path:
        """
        Get cache file path for a key.
        
        Args:
            key: Cache key
            
        Returns:
            Path to cache file
        """
        # Sanitize key for filename
        safe_key = "".join(c if c.isalnum() or c in ('-', '_') else '_' for c in key)
        return self.cache_dir / f"{safe_key}.json"
    
    def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache.
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None if not found or expired
        """
        cache_path = self._get_cache_path(key)
        
        if not cache_path.exists():
            logger.debug(f"Cache miss: {key}")
            return None
        
        try:
            with open(cache_path, 'r') as f:
                cache_data = json.load(f)
            
            # Check TTL
            cached_at = cache_data.get('cached_at', 0)
            ttl = cache_data.get('ttl', self.default_ttl)
            
            if time.time() - cached_at > ttl:
                logger.debug(f"Cache expired: {key}")
                cache_path.unlink()
                return None
            
            logger.debug(f"Cache hit: {key}")
            return cache_data.get('value')
            
        except (json.JSONDecodeError, KeyError) as e:
            logger.warning(f"Invalid cache file for {key}: {e}")
            cache_path.unlink()
            return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """
        Set value in cache.
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: TTL in seconds. Uses default if not specified.
        """
        cache_path = self._get_cache_path(key)
        
        cache_data = {
            'value': value,
            'cached_at': time.time(),
            'ttl': ttl if ttl is not None else self.default_ttl
        }
        
        try:
            with open(cache_path, 'w') as f:
                json.dump(cache_data, f)
            logger.debug(f"Cached: {key}")
        except Exception as e:
            logger.warning(f"Failed to cache {key}: {e}")
    
    def delete(self, key: str) -> None:
        """
        Delete value from cache.
        
        Args:
            key: Cache key
        """
        cache_path = self._get_cache_path(key)
        if cache_path.exists():
            cache_path.unlink()
            logger.debug(f"Deleted cache: {key}")
    
    def clear(self) -> None:
        """Clear all cache files."""
        for cache_file in self.cache_dir.glob('*.json'):
            cache_file.unlink()
        logger.info("Cache cleared")
    
    def invalidate_expired(self) -> int:
        """
        Remove all expired cache files.
        
        Returns:
            Number of files removed
        """
        removed = 0
        for cache_file in self.cache_dir.glob('*.json'):
            try:
                with open(cache_file, 'r') as f:
                    cache_data = json.load(f)
                
                cached_at = cache_data.get('cached_at', 0)
                ttl = cache_data.get('ttl', self.default_ttl)
                
                if time.time() - cached_at > ttl:
                    cache_file.unlink()
                    removed += 1
            except Exception:
                # Remove invalid cache files
                cache_file.unlink()
                removed += 1
        
        if removed > 0:
            logger.info(f"Removed {removed} expired cache files")
        
        return removed


def cached(ttl: Optional[int] = None, key_func: Optional[Callable] = None):
    """
    Decorator for caching function results.
    
    Args:
        ttl: TTL in seconds
        key_func: Function to generate cache key from args/kwargs
        
    Returns:
        Decorated function
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Get cache instance
            cache = kwargs.pop('_cache', None)
            if cache is None or not isinstance(cache, FileCache):
                # No cache provided, just call function
                return await func(*args, **kwargs)
            
            # Generate cache key
            if key_func is not None:
                cache_key = key_func(*args, **kwargs)
            else:
                # Default key from function name and args
                cache_key = f"{func.__name__}_{hash(str(args) + str(kwargs))}"
            
            # Try to get from cache
            cached_value = cache.get(cache_key)
            if cached_value is not None:
                return cached_value
            
            # Call function and cache result
            result = await func(*args, **kwargs)
            cache.set(cache_key, result, ttl=ttl)
            
            return result
        
        return wrapper
    return decorator


# Global cache instance
_global_cache: Optional[FileCache] = None


def get_cache() -> FileCache:
    """Get the global cache instance."""
    global _global_cache
    if _global_cache is None:
        _global_cache = FileCache()
    return _global_cache


def set_cache(cache: FileCache) -> None:
    """Set the global cache instance."""
    global _global_cache
    _global_cache = cache
