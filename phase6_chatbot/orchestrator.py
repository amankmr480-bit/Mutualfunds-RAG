"""
Phase 6: Orchestration — personal check → RAG (Phase 4 + Phase 5).
No cache; no personal data stored.
"""
import logging
from typing import Any

from phase5_llm.guardrails import get_refusal_message, is_personal_query
from phase5_llm.pipeline import answer_query

logger = logging.getLogger(__name__)


def chat_turn(user_query: str, top_k: int = 7, **kwargs: Any) -> dict[str, Any]:
    """
    One chat turn: personal check → RAG (Phase 4 + Phase 5).
    Returns { "answer", "sources", "refused_personal" }.
    """
    if not (user_query or "").strip():
        return {"answer": "Please ask a question about ICICI Prudential mutual funds.", "sources": [], "refused_personal": False}
    if is_personal_query(user_query):
        return {"answer": get_refusal_message(), "sources": [], "refused_personal": True}
    result = answer_query(user_query, top_k=top_k, **kwargs)
    return result
