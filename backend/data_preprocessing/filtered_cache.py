_filtered_cache = {}

def get_filtered_cache():
    """Get the global filtered cache instance."""
    return _filtered_cache

def set_filtered_cache(key, value):
    """Set a value in the filtered cache."""
    _filtered_cache[key] = value

def clear_filtered_cache():
    """Clear the entire filtered cache."""
    _filtered_cache.clear() 