"""
Phase 4 pipeline: retrieve(query) → chunks + assembled context for LLM.
"""
import logging
from pathlib import Path
from typing import Any

from phase4_retrieval.config import MAX_CONTEXT_CHARS
from phase4_retrieval.context import assemble_context
from phase4_retrieval.retriever import retrieve

logger = logging.getLogger(__name__)


def retrieve_context(
    query: str,
    top_k: int = 7,
    max_context_chars: int | None = None,
    category: str | None = None,
    risk: str | None = None,
    fund_name_contains: str | None = None,
    persist_dir: str | Path | None = None,
    **kwargs: Any,
) -> dict[str, Any]:
    """
    Full retrieval pipeline: preprocess → embed → search → assemble context.
    Returns dict with:
      - chunks: list of { text, metadata }
      - context: single string for LLM
      - distances: list of similarity distances (if any)
    """
    chunks, distances = retrieve(
        query,
        top_k=top_k,
        persist_dir=persist_dir,
        category=category,
        risk=risk,
        fund_name_contains=fund_name_contains,
        **kwargs,
    )
    max_chars = max_context_chars if max_context_chars is not None else MAX_CONTEXT_CHARS
    context = assemble_context(chunks, max_chars=max_chars)
    return {
        "chunks": chunks,
        "context": context,
        "distances": distances,
    }
