"""
Phase 4.2: Query preprocessing.
Normalize text, expand abbreviations for better retrieval.
"""
import re
from typing import Any

from phase4_retrieval.config import QUERY_ABBREVIATIONS


def preprocess_query(query: str) -> str:
    """
    Normalize and expand user query for embedding and search.
    - Strip and collapse whitespace
    - Expand known abbreviations (1Y, 5Y, NAV, AUM, etc.)
    - Optional: lowercase for expansion then restore (we keep original case for embedding)
    """
    if not query or not isinstance(query, str):
        return ""
    text = query.strip()
    text = re.sub(r"\s+", " ", text)
    if not text:
        return ""

    # Expand abbreviations (case-insensitive match, replace with space-separated expansion)
    words = text.split()
    expanded = []
    for w in words:
        key = w.lower().rstrip(".,?!")
        if key in QUERY_ABBREVIATIONS:
            expanded.append(QUERY_ABBREVIATIONS[key])
        else:
            expanded.append(w)
    return " ".join(expanded)
