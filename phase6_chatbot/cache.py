"""
Phase 6: Query-answer cache for FAQ. No personal data stored — only normalized query and answer text.
"""
import logging
import time
from collections import OrderedDict
from typing import Any

from phase6_chatbot.config import MAX_CACHE_ENTRIES, normalize_query_for_cache

logger = logging.getLogger(__name__)


class QueryAnswerCache:
    """
    In-memory cache: key = normalized query, value = { "answer", "cached_at" }.
    No user IDs, no personal data. Optional TTL.
    """

    def __init__(self, ttl_seconds: int | None = None, max_entries: int = MAX_CACHE_ENTRIES):
        self._ttl = ttl_seconds
        self._max = max_entries
        self._store: OrderedDict[str, dict[str, Any]] = OrderedDict()

    def get(self, query: str) -> dict[str, Any] | None:
        """Return cached entry or None. Key is normalized query (no PII)."""
        key = normalize_query_for_cache(query)
        if not key:
            return None
        entry = self._store.get(key)
        if not entry:
            return None
        if self._ttl is not None and (time.time() - (entry.get("cached_at") or 0)) > self._ttl:
            del self._store[key]
            return None
        self._store.move_to_end(key)  # LRU
        return entry

    def set(self, query: str, answer: str) -> None:
        """Store answer for normalized query. No personal data."""
        key = normalize_query_for_cache(query)
        if not key:
            return
        while len(self._store) >= self._max and self._store:
            self._store.popitem(last=False)
        self._store[key] = {"answer": answer, "cached_at": time.time()}
        self._store.move_to_end(key)

    def clear(self) -> None:
        """Invalidate entire cache (e.g. after weekly re-index)."""
        self._store.clear()
        logger.info("Cache cleared")
