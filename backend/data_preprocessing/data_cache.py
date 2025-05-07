# In-memory cache for storing datasets
_cache = {}

def get_cache():
    """Get the global cache instance."""
    return _cache

def set_cache(key, value):
    """Set a value in the cache."""
    _cache[key] = value

def clear_cache():
    """Clear the entire cache."""
    _cache.clear() 