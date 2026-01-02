"""
Semantic Cache Configuration

Configuration settings for semantic caching system.
"""

# Semantic cache settings
SEMANTIC_CACHE_CONFIG = {
    # Enable/disable semantic caching
    "enabled": True,
    
    # Similarity threshold (0-1)
    # Higher = stricter matching, fewer cache hits but more accurate
    # Lower = more cache hits but might return less relevant results
    "similarity_threshold": 0.80,
    
    # Sentence transformer model
    # Options:
    # - "sentence-transformers/all-MiniLM-L6-v2" (80MB, fast, recommended)
    # - "sentence-transformers/all-mpnet-base-v2" (420MB, more accurate)
    "model_name": "sentence-transformers/all-MiniLM-L6-v2",
    
    # Maximum cached queries per schema hash
    "max_cache_size_per_schema": 1000,
    
    # Cache TTL (time to live) in days
    # Entries older than this will be auto-deleted
    "cache_ttl_days": 30,
    
    # Minimum question length to cache
    # Very short questions won't be cached
    "min_question_length": 5,
    
    # Enable cache statistics tracking
    "track_statistics": True,
    
    # Prefer recent cache entries when multiple matches have similar scores
    "prefer_recent": True,
    
    # Maximum age difference (in days) for "recent" preference
    "recent_threshold_days": 7,
}


def get_cache_config(key: str = None):
    """
    Get cache configuration value.
    
    Args:
        key: Configuration key. If None, returns entire config.
        
    Returns:
        Configuration value or entire config dict
    """
    if key is None:
        return SEMANTIC_CACHE_CONFIG
    return SEMANTIC_CACHE_CONFIG.get(key)


def is_cache_enabled() -> bool:
    """Check if semantic caching is enabled."""
    return SEMANTIC_CACHE_CONFIG.get("enabled", True)


def get_similarity_threshold() -> float:
    """Get configured similarity threshold."""
    return SEMANTIC_CACHE_CONFIG.get("similarity_threshold", 0.85)
