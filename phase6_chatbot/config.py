"""
Configuration for Phase 6: Chatbot UI and cache.
No personal data is stored; cache keys are normalized queries only.
"""
import re
from pathlib import Path

# Cache: in-memory, key = normalized query (no user id, no PII)
CACHE_TTL_SECONDS = None  # None = no expiry (invalidate on weekly re-index)
MAX_CACHE_ENTRIES = 500   # Cap size

# Phase 4 / 5
DEFAULT_TOP_K = 7
PROJECT_ROOT = Path(__file__).resolve().parent.parent


def normalize_query_for_cache(q: str) -> str:
    """Normalize for cache key: lowercase, strip, collapse spaces. No personal data."""
    if not q or not isinstance(q, str):
        return ""
    return re.sub(r"\s+", " ", q.strip().lower())
