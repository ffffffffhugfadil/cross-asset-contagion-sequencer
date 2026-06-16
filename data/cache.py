"""
data/cache.py
=============
Local caching for API responses to avoid rate limits.

Saves fetched data to JSON files and reuses them
within the same day to reduce API calls.
"""

import os
import json
import time
from typing import Dict, Any, Optional
from datetime import datetime, timedelta


class DataCache:
    """
    Simple file-based cache for API responses.
    
    Usage:
        cache = DataCache(cache_dir='.cache')
        data = cache.get('btc_quotes', max_age_hours=1)
        if data is None:
            data = fetch_from_api()
            cache.set('btc_quotes', data)
    """
    
    def __init__(self, cache_dir: str = '.cache'):
        """
        Initialize cache with directory.
        
        Args:
            cache_dir: Directory to store cache files
        """
        self.cache_dir = cache_dir
        os.makedirs(cache_dir, exist_ok=True)
    
    def _get_cache_path(self, key: str) -> str:
        """Get file path for cache key."""
        # Sanitize key for filename
        safe_key = key.replace('/', '_').replace('\\', '_')
        return os.path.join(self.cache_dir, f"{safe_key}.json")
    
    def get(self, key: str, max_age_hours: int = 1) -> Optional[Any]:
        """
        Retrieve cached data if it exists and is fresh.
        
        Args:
            key: Cache key
            max_age_hours: Maximum age of cached data in hours
        
        Returns:
            Cached data or None if expired/not found
        """
        cache_path = self._get_cache_path(key)
        
        if not os.path.exists(cache_path):
            return None
        
        try:
            with open(cache_path, 'r') as f:
                cached = json.load(f)
            
            # Check age
            cache_time = cached.get('_cache_time', 0)
            if time.time() - cache_time > max_age_hours * 3600:
                return None
            
            return cached.get('data')
        except (json.JSONDecodeError, KeyError):
            return None
    
    def set(self, key: str, data: Any) -> None:
        """
        Store data in cache.
        
        Args:
            key: Cache key
            data: Data to cache (must be JSON-serializable)
        """
        cache_path = self._get_cache_path(key)
        
        cache_data = {
            '_cache_time': time.time(),
            'data': data,
        }
        
        with open(cache_path, 'w') as f:
            json.dump(cache_data, f, indent=2)
    
    def clear(self, key: Optional[str] = None) -> None:
        """
        Clear cache for specific key or all keys.
        
        Args:
            key: Specific key to clear, or None to clear all
        """
        if key is None:
            # Clear all
            for filename in os.listdir(self.cache_dir):
                if filename.endswith('.json'):
                    os.remove(os.path.join(self.cache_dir, filename))
        else:
            cache_path = self._get_cache_path(key)
            if os.path.exists(cache_path):
                os.remove(cache_path)
    
    def is_fresh(self, key: str, max_age_hours: int = 1) -> bool:
        """
        Check if cached data is still fresh.
        
        Returns:
            True if cache exists and is fresh
        """
        cache_path = self._get_cache_path(key)
        
        if not os.path.exists(cache_path):
            return False
        
        try:
            with open(cache_path, 'r') as f:
                cached = json.load(f)
            cache_time = cached.get('_cache_time', 0)
            return time.time() - cache_time <= max_age_hours * 3600
        except (json.JSONDecodeError, KeyError):
            return False


# Singleton instance for convenience
_default_cache = None


def get_cache() -> DataCache:
    """Get default cache instance."""
    global _default_cache
    if _default_cache is None:
        _default_cache = DataCache()
    return _default_cache
