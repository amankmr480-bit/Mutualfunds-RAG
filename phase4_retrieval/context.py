"""
Phase 4.3: Context assembly.
Concatenate top-K chunk texts into a single context string with max length for LLM.
"""
from typing import Any

from phase4_retrieval.config import MAX_CONTEXT_CHARS


def assemble_context(
    chunks: list[dict[str, Any]],
    max_chars: int = MAX_CONTEXT_CHARS,
    separator: str = "\n\n",
) -> str:
    """
    Build a single context string from retrieved chunks for the LLM.
    Stops adding chunks when adding the next would exceed max_chars.
    """
    if not chunks:
        return ""
    parts = []
    total = 0
    for c in chunks:
        text = (c.get("text") or "").strip()
        if not text:
            continue
        need = len(text) + (len(separator) if parts else 0)
        if total + need > max_chars and parts:
            break
        parts.append(text)
        total += need
    return separator.join(parts)
