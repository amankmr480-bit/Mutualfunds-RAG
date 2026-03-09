"""
Phase 4: Retrieval — embed query, vector search, optional metadata filter, return top-K chunks.
Includes in-memory fallback (JSON + embeddings) when ChromaDB fails (e.g. on Streamlit Cloud).
"""
import json
import logging
import os
from pathlib import Path
from typing import Any

import numpy as np

from phase3_vectorstore.embeddings import embed_query, embed_texts
from phase4_retrieval.config import (
    COLLECTION_NAME,
    DEFAULT_CHUNKS_PATH,
    DEFAULT_PERSIST_DIR,
    DEFAULT_TOP_K,
)
from phase4_retrieval.preprocess import preprocess_query

logger = logging.getLogger(__name__)

# Cache for in-memory fallback: (chunks, embeddings)
_chunks_cache: tuple[list[dict], list[list[float]]] | None = None

# Skip ChromaDB on Streamlit Cloud (SQLite incompatible) - use JSON retrieval only
_USE_JSON_ONLY = os.environ.get("STREAMLIT_SERVER_HEADLESS", "").lower() in ("true", "1")


def _find_chunks_path() -> Path | None:
    """Find rag_chunks.json using multiple path strategies for Streamlit Cloud."""
    root_env = os.environ.get("RAG_PROJECT_ROOT")
    candidates = [
        DEFAULT_CHUNKS_PATH,
        Path(root_env) / "phase2_processing" / "output" / "rag_chunks.json" if root_env else None,
        Path(__file__).resolve().parent.parent / "phase2_processing" / "output" / "rag_chunks.json",
        Path.cwd() / "phase2_processing" / "output" / "rag_chunks.json",
    ]
    for p in candidates:
        if p and p.exists():
            return p
    return None


def _load_chunks_and_embeddings(chunks_path: str | Path | None = None) -> tuple[list[dict], list[list[float]]]:
    """Load RAG chunks from JSON and compute embeddings. Cached for reuse."""
    global _chunks_cache
    if _chunks_cache is not None:
        return _chunks_cache
    path = Path(chunks_path) if chunks_path else _find_chunks_path()
    if not path or not path.exists():
        raise FileNotFoundError(f"Chunks file not found. Tried: {DEFAULT_CHUNKS_PATH}")
    with open(path, encoding="utf-8") as f:
        chunks = json.load(f)
    if not chunks:
        _chunks_cache = ([], [])
        return _chunks_cache
    texts = [c.get("text", "") for c in chunks]
    embeddings = embed_texts(texts, show_progress=False)
    _chunks_cache = (chunks, embeddings)
    return _chunks_cache


def retrieve_from_json(
    query: str,
    top_k: int = DEFAULT_TOP_K,
    chunks_path: str | Path | None = None,
    preprocess: bool = True,
) -> tuple[list[dict[str, Any]], list[float]]:
    """
    In-memory retrieval: load chunks from JSON, embed query, cosine similarity, return top-K.
    Fallback when ChromaDB fails (e.g. Streamlit Cloud SQLite issues).
    """
    q = preprocess_query(query) if preprocess else (query or "").strip()
    if not q:
        q = query or ""
    if not q.strip():
        return [], []
    chunks, chunk_embeddings = _load_chunks_and_embeddings(chunks_path)
    if not chunks:
        return [], []
    query_embedding = embed_query(q)
    qv = np.array(query_embedding, dtype=np.float32)
    cv = np.array(chunk_embeddings, dtype=np.float32)
    scores = np.dot(cv, qv)
    top_indices = np.argsort(scores)[::-1][:top_k]
    result_chunks = [
        {"text": chunks[i].get("text", ""), "metadata": chunks[i].get("metadata") or {}}
        for i in top_indices
    ]
    distances = [float(-scores[i]) for i in top_indices]
    return result_chunks, distances


def _build_where_filter(category: str | None = None, risk: str | None = None) -> dict[str, Any] | None:
    """
    Build Chroma where clause for optional filtering (exact match on category/risk).
    fund_name_contains is applied as post-filter in Python.
    """
    clauses = []
    if category:
        clauses.append({"category": {"$eq": category}})
    if risk:
        clauses.append({"risk": {"$eq": risk}})
    if not clauses:
        return None
    if len(clauses) == 1:
        return clauses[0]
    return {"$and": clauses}


def retrieve(
    query: str,
    top_k: int = DEFAULT_TOP_K,
    persist_dir: str | Path | None = None,
    collection_name: str = COLLECTION_NAME,
    category: str | None = None,
    risk: str | None = None,
    fund_name_contains: str | None = None,
    preprocess: bool = True,
) -> tuple[list[dict[str, Any]], list[float]]:
    """
    Run retrieval: preprocess query → embed → vector search → return top-K chunks.
    On Streamlit Cloud, uses JSON retrieval only (ChromaDB/SQLite incompatible).
    Falls back to in-memory JSON retrieval if ChromaDB fails locally.
    Returns (chunks, distances) where each chunk is { "text": str, "metadata": dict }.
    """
    q = preprocess_query(query) if preprocess else (query or "").strip()
    if not q:
        q = query or ""
    if not q.strip():
        return [], []

    # Streamlit Cloud: skip ChromaDB entirely, use JSON retrieval
    if _USE_JSON_ONLY:
        return retrieve_from_json(query, top_k=top_k, preprocess=False)

    try:
        from phase3_vectorstore.store import load_collection

        query_embedding = embed_query(q)
        persist_dir = Path(persist_dir or DEFAULT_PERSIST_DIR)
        collection = load_collection(persist_directory=persist_dir, collection_name=collection_name)

        where_filter = _build_where_filter(category=category, risk=risk)

        try:
            if where_filter is not None:
                result = collection.query(
                    query_embeddings=[query_embedding],
                    n_results=top_k,
                    where=where_filter,
                    include=["documents", "metadatas", "distances"],
                )
            else:
                result = collection.query(
                    query_embeddings=[query_embedding],
                    n_results=top_k,
                    include=["documents", "metadatas", "distances"],
                )
        except Exception as e:
            logger.warning("Chroma query with filter failed, retrying without filter: %s", e)
            result = collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k,
                include=["documents", "metadatas", "distances"],
            )

        documents = result["documents"][0] if result["documents"] else []
        metadatas = result["metadatas"][0] if result["metadatas"] else []
        distances = result["distances"][0] if result.get("distances") else []

        chunks = [
            {"text": doc, "metadata": meta or {}}
            for doc, meta in zip(documents, metadatas)
        ]
        if fund_name_contains and fund_name_contains.strip():
            sub = fund_name_contains.strip().lower()
            filtered = []
            filtered_dists = []
            for c, d in zip(chunks, distances):
                fn = (c.get("metadata") or {}).get("fund_name") or ""
                if sub in fn.lower():
                    filtered.append(c)
                    filtered_dists.append(d)
            chunks = filtered
            distances = filtered_dists
        return chunks, distances

    except Exception as e:
        logger.warning("ChromaDB retrieval failed, falling back to in-memory: %s", e)
        return retrieve_from_json(query, top_k=top_k, preprocess=False)
