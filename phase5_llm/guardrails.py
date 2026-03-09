"""
Guardrails: detect personal questions — do not answer, do not store personal data.
"""
import re
from typing import Any

# Patterns and keywords that suggest personal / off-topic questions
PERSONAL_KEYWORDS = [
    "my name", "my email", "my phone", "my number", "my address",
    "my income", "my salary", "how much i earn", "how much do i earn", "my investment", "my portfolio",
    "store my", "save my", "remember my", "my account", "my bank",
    "who am i", "what am i", "identify me", "my details", "personal information",
    "my aadhaar", "my pan", "my kyc", "my dob", "my date of birth",
    "call me", "email me", "contact me", "reach me",
]

# Mutual-fund / on-topic keywords (if query has only these, less likely personal)
TOPIC_KEYWORDS = [
    "fund", "nav", "return", "aum", "expense", "exit load", "icici", "prudential",
    "scheme", "sip", "lump sum", "category", "risk", "equity", "debt", "hybrid",
    "minimum", "investment", "growth", "direct",
]


def _normalize_for_check(q: str) -> str:
    return " " + (q or "").lower().strip() + " "


def is_personal_query(query: str) -> bool:
    """
    Return True if the query appears to ask for personal data, personal advice,
    or to store/use personal information. No personal data is logged or stored.
    """
    if not query or not query.strip():
        return False
    n = _normalize_for_check(query)
    for k in PERSONAL_KEYWORDS:
        if k in n:
            return True
    # Short generic questions that are likely "who am i" style
    if re.match(r"^\s*(who\s+am\s+i|what\s+am\s+i|where\s+am\s+i)\s*[?.]?\s*$", query, re.IGNORECASE):
        return True
    return False


def get_refusal_message() -> str:
    """Standard refusal for personal questions (no personal data stored)."""
    from phase5_llm.config import PERSONAL_QUERY_REFUSAL
    return PERSONAL_QUERY_REFUSAL
