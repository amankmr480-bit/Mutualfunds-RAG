"""
Phase 4: Retrieval — embed query, vector search, optional metadata filter, return top-K chunks.
"""
import logging
from pathlib import Path
from typing import Any

from phase3_vectorstore.embeddings import embed_query
from phase3_vectorstore.store import get_chroma_client, load_collection
from phase4_retrieval.config import COLLECTION_NAME, DEFAULT_PERSIST_DIR, DEFAULT_TOP_K
from phase4_retrieval.preprocess import preprocess_query

logger = logging.getLogger(__name__)


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
    Returns (chunks, distances) where each chunk is { "text": str, "metadata": dict }.
    """
    q = preprocess_query(query) if preprocess else (query or "").strip()
    if not q:
        q = query or ""
    if not q.strip():
        return [], []

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
    # Optional post-filter by fund name substring
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
