"""
Phase 3.2: Vector store (Chroma).
- Create/load collection with metadata support.
- Add documents (text + embedding + metadata).
- Persist to disk; optional versioning by scrape_date.
"""
import logging
from pathlib import Path
from typing import Any

from phase3_vectorstore.config import COLLECTION_NAME, DEFAULT_PERSIST_DIR, METADATA_KEYS

logger = logging.getLogger(__name__)


def _sanitize_metadata(meta: dict[str, Any]) -> dict[str, str | int | float | bool]:
    """Chroma accepts only str, int, float, bool. Convert others to str."""
    out = {}
    for k in METADATA_KEYS:
        if k not in meta:
            continue
        v = meta[k]
        if v is None:
            continue
        if isinstance(v, (str, int, float, bool)):
            out[k] = v
        else:
            out[k] = str(v)
    return out


def get_chroma_client(persist_directory: str | Path | None = None):
    """Return Chroma client with persistence."""
    try:
        import chromadb
        from chromadb.config import Settings
    except ImportError:
        raise ImportError("Install chromadb: pip install chromadb")
    path = str(Path(persist_directory or DEFAULT_PERSIST_DIR).resolve())
    Path(path).mkdir(parents=True, exist_ok=True)
    client = chromadb.PersistentClient(
        path=path,
        settings=Settings(anonymized_telemetry=False),
    )
    return client


def create_or_get_collection(
    client: Any,
    collection_name: str = COLLECTION_NAME,
    replace: bool = False,
):
    """
    Create or get collection. If replace=True, delete existing and create new.
    """
    if replace and collection_name in [c.name for c in client.list_collections()]:
        client.delete_collection(collection_name)
        logger.info("Deleted existing collection: %s", collection_name)
    return client.get_or_create_collection(
        name=collection_name,
        metadata={"description": "ICICI Prudential MF RAG chunks"},
    )


def add_chunks_to_collection(
    collection: Any,
    chunks: list[dict[str, Any]],
    embeddings: list[list[float]],
    ids: list[str] | None = None,
) -> None:
    """
    Add chunks to Chroma. Each chunk has 'text' and 'metadata'.
    embeddings[i] is the vector for chunks[i].
    """
    if len(chunks) != len(embeddings):
        raise ValueError("chunks and embeddings length mismatch")
    documents = [c["text"] for c in chunks]
    metadatas = [_sanitize_metadata(c.get("metadata") or {}) for c in chunks]
    if ids is None:
        ids = [f"fund_{i}" for i in range(len(chunks))]
    collection.add(
        ids=ids,
        embeddings=embeddings,
        documents=documents,
        metadatas=metadatas,
    )
    logger.info("Added %s documents to collection", len(chunks))


def load_collection(
    persist_directory: str | Path | None = None,
    collection_name: str = COLLECTION_NAME,
):
    """Load existing Chroma collection (read-only usage)."""
    client = get_chroma_client(persist_directory)
    return client.get_collection(name=collection_name)
