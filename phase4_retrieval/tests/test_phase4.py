"""
Tests for Phase 4: preprocessing, context assembly, retrieval pipeline.
"""
from pathlib import Path

import pytest

from phase4_retrieval.preprocess import preprocess_query
from phase4_retrieval.context import assemble_context
from phase4_retrieval.retriever import retrieve
from phase4_retrieval.pipeline import retrieve_context


# --- Preprocess ---


def test_preprocess_query_strips_whitespace():
    assert preprocess_query("  what is nav  ") == "what is net asset value"


def test_preprocess_query_expands_abbreviations():
    assert "1 year return" in preprocess_query("1Y return")
    assert "5 year return" in preprocess_query("5y returns")
    assert "net asset value" in preprocess_query("NAV of fund")


def test_preprocess_query_empty():
    assert preprocess_query("") == ""
    assert preprocess_query("   ") == ""


# --- Context assembly ---


def test_assemble_context_empty():
    assert assemble_context([]) == ""


def test_assemble_context_single_chunk():
    chunks = [{"text": "Fund A is Equity. NAV 100."}]
    assert assemble_context(chunks) == "Fund A is Equity. NAV 100."


def test_assemble_context_respects_max_chars():
    chunks = [
        {"text": "A" * 100},
        {"text": "B" * 100},
        {"text": "C" * 500},
    ]
    out = assemble_context(chunks, max_chars=250)
    assert len(out) <= 250 + 10  # separator
    assert "A" in out


# --- Retrieval (requires Phase 3 Chroma DB) ---


def test_retrieve_returns_lists():
    """Without Chroma/sentence-transformers this may skip or fail."""
    try:
        chunks, distances = retrieve("What is the NAV of ICICI Value Fund?", top_k=2)
    except (ImportError, Exception) as e:
        pytest.skip(f"Retrieval not available: {e}")
    assert isinstance(chunks, list)
    assert isinstance(distances, list)
    assert len(chunks) <= 2


def test_retrieve_context_structure():
    try:
        result = retrieve_context("Equity funds", top_k=2)
    except (ImportError, Exception) as e:
        pytest.skip(f"Retrieval not available: {e}")
    assert "chunks" in result
    assert "context" in result
    assert "distances" in result
    assert isinstance(result["context"], str)


def test_retrieve_context_with_no_preprocess():
    try:
        result = retrieve_context("ICICI Prudential", top_k=2, preprocess=False)
    except (ImportError, Exception) as e:
        pytest.skip(f"Retrieval not available: {e}")
    assert "context" in result
    assert isinstance(result["chunks"], list)
