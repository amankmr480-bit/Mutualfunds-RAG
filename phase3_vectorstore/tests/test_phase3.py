"""
Tests for Phase 3: embeddings, store, pipeline.
"""
import json
from pathlib import Path

import pytest

from phase3_vectorstore.embeddings import embed_texts, embed_query
from phase3_vectorstore.store import (
    _sanitize_metadata,
    add_chunks_to_collection,
    create_or_get_collection,
    get_chroma_client,
)
from phase3_vectorstore.pipeline import load_chunks, run_pipeline

# Minimal chunk for tests
SAMPLE_CHUNKS = [
    {
        "text": "ICICI Prudential Value Fund is an Equity fund with Very High risk. NAV: 520.49.",
        "metadata": {
            "fund_name": "ICICI Prudential Value Fund",
            "category": "Equity",
            "risk": "Very High",
            "nav": 520.49,
            "aum": 60352.0,
            "scrape_date": "2026-03-08",
            "source_url": "https://groww.in/mutual-funds/amc/icici-prudential-mutual-funds",
        },
    },
    {
        "text": "ICICI Prudential Large Cap Fund is an Equity fund. NAV: 119.96.",
        "metadata": {
            "fund_name": "ICICI Prudential Large Cap Fund",
            "category": "Equity",
            "risk": "Very High",
            "nav": 119.96,
            "aum": 76645.0,
        },
    },
]


# --- Store: metadata sanitization ---


def test_sanitize_metadata_keeps_primitives():
    meta = {"fund_name": "X", "category": "Equity", "nav": 10.5, "aum": 1000}
    out = _sanitize_metadata(meta)
    assert out["fund_name"] == "X"
    assert out["nav"] == 10.5
    assert out["aum"] == 1000


def test_sanitize_metadata_converts_non_primitive_to_str():
    meta = {"fund_name": "X", "extra": {"nested": 1}}
    out = _sanitize_metadata(meta)
    assert out["fund_name"] == "X"
    assert "fund_name" in out


# --- Embeddings ---


def test_embed_texts_returns_list_of_vectors():
    try:
        vecs = embed_texts(["Hello world"], show_progress=False)
    except ImportError as e:
        pytest.skip(f"sentence-transformers not installed: {e}")
    assert isinstance(vecs, list)
    assert len(vecs) == 1
    assert isinstance(vecs[0], list)
    assert len(vecs[0]) > 0
    assert all(isinstance(x, float) for x in vecs[0])


def test_embed_query_returns_single_vector():
    try:
        vec = embed_query("What is the NAV of ICICI Value Fund?")
    except ImportError as e:
        pytest.skip(f"sentence-transformers not installed: {e}")
    assert isinstance(vec, list)
    assert len(vec) > 0
    assert all(isinstance(x, float) for x in vec)


# --- Pipeline ---


def test_load_chunks_raises_if_missing():
    with pytest.raises(FileNotFoundError):
        load_chunks(Path("/nonexistent/rag_chunks.json"))


def test_load_chunks_from_json_array(tmp_path):
    path = tmp_path / "chunks.json"
    path.write_text(json.dumps(SAMPLE_CHUNKS), encoding="utf-8")
    loaded = load_chunks(path)
    assert len(loaded) == 2
    assert loaded[0]["text"] == SAMPLE_CHUNKS[0]["text"]


def test_run_pipeline_with_real_chunks(tmp_path):
    """Run full pipeline if Phase 2 chunks exist; use tmp_path for Chroma."""
    chunks_path = Path(__file__).resolve().parent.parent.parent / "phase2_processing" / "output" / "rag_chunks.json"
    if not chunks_path.exists():
        pytest.skip("Phase 2 rag_chunks.json not found; run Phase 2 first")
    try:
        from sentence_transformers import SentenceTransformer  # noqa: F401
    except ImportError:
        pytest.skip("sentence-transformers not installed")
    result = run_pipeline(
        chunks_path=chunks_path,
        persist_dir=tmp_path,
        replace_collection=True,
        embed_batch_size=8,
    )
    assert result["chunk_count"] >= 1
    assert result["persist_dir"] == str(tmp_path)
    assert (tmp_path / "chroma.sqlite3").exists() or any(tmp_path.iterdir())