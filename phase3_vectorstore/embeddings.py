"""
Phase 3.1: Embedding model.
Uses sentence-transformers for local embeddings (no API key).
"""
import logging
from typing import Any

from phase3_vectorstore.config import DEFAULT_EMBEDDING_MODEL, EMBED_BATCH_SIZE

logger = logging.getLogger(__name__)

_model = None


def get_embedding_model(model_name: str | None = None):
    """Lazy-load the sentence-transformers model."""
    global _model
    if _model is None:
        try:
            from sentence_transformers import SentenceTransformer
        except ImportError:
            raise ImportError(
                "Install sentence-transformers: pip install sentence-transformers"
            )
        name = model_name or DEFAULT_EMBEDDING_MODEL
        logger.info("Loading embedding model: %s", name)
        _model = SentenceTransformer(name)
    return _model


def embed_texts(
    texts: list[str],
    model_name: str | None = None,
    batch_size: int = EMBED_BATCH_SIZE,
    show_progress: bool = True,
) -> list[list[float]]:
    """
    Embed a list of texts. Returns list of vectors (each vector is list of floats).
    """
    model = get_embedding_model(model_name)
    embeddings = model.encode(
        texts,
        batch_size=batch_size,
        show_progress_bar=show_progress,
        convert_to_numpy=True,
    )
    return embeddings.tolist()


def embed_query(query: str, model_name: str | None = None) -> list[float]:
    """Embed a single query string (for retrieval in Phase 4)."""
    model = get_embedding_model(model_name)
    vec = model.encode([query], convert_to_numpy=True)
    return vec[0].tolist()
