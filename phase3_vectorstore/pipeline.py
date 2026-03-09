"""
Phase 3 pipeline: Load Phase 2 chunks → embed → upsert to Chroma → persist.
"""
import json
import logging
from pathlib import Path
from typing import Any

from phase3_vectorstore.config import (
    COLLECTION_NAME,
    DEFAULT_CHUNKS_PATH,
    DEFAULT_PERSIST_DIR,
)
from phase3_vectorstore.embeddings import embed_texts
from phase3_vectorstore.store import (
    add_chunks_to_collection,
    create_or_get_collection,
    get_chroma_client,
)

logger = logging.getLogger(__name__)


def load_chunks(chunks_path: str | Path) -> list[dict[str, Any]]:
    """Load RAG chunks from Phase 2 JSON."""
    path = Path(chunks_path)
    if not path.exists():
        raise FileNotFoundError(f"Chunks file not found: {path}")
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    if isinstance(data, list):
        return data
    if isinstance(data, dict) and "chunks" in data:
        return data["chunks"]
    raise ValueError("Chunks file must be a JSON array or object with 'chunks' key")


def run_pipeline(
    chunks_path: str | Path | None = None,
    persist_dir: str | Path | None = None,
    collection_name: str = COLLECTION_NAME,
    replace_collection: bool = True,
    model_name: str | None = None,
    embed_batch_size: int = 32,
) -> dict[str, Any]:
    """
    Run Phase 3: load chunks → embed → add to Chroma → persist.
    Returns summary: { chunk_count, persist_dir, collection_name }.
    """
    chunks_path = Path(chunks_path or DEFAULT_CHUNKS_PATH)
    persist_dir = Path(persist_dir or DEFAULT_PERSIST_DIR)

    chunks = load_chunks(chunks_path)
    if not chunks:
        logger.warning("No chunks to index")
        return {"chunk_count": 0, "persist_dir": str(persist_dir), "collection_name": collection_name}

    # Embed
    texts = [c["text"] for c in chunks]
    logger.info("Embedding %s chunks...", len(texts))
    embeddings = embed_texts(texts, model_name=model_name, batch_size=embed_batch_size)

    # Chroma: create collection and add
    client = get_chroma_client(persist_dir)
    collection = create_or_get_collection(client, collection_name=collection_name, replace=replace_collection)
    add_chunks_to_collection(collection, chunks, embeddings)

    return {
        "chunk_count": len(chunks),
        "persist_dir": str(persist_dir),
        "collection_name": collection_name,
    }
