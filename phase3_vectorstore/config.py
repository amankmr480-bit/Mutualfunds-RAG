"""
Configuration for Phase 3: Embedding & Vector Store.
Input: Phase 2 RAG chunks JSON.
Output: Persisted Chroma collection with embeddings and metadata.
"""
from pathlib import Path

# Paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_CHUNKS_PATH = PROJECT_ROOT / "phase2_processing" / "output" / "rag_chunks.json"
DEFAULT_PERSIST_DIR = Path(__file__).resolve().parent / "chroma_db"

# Chroma collection name
COLLECTION_NAME = "icici_prudential_funds"

# Embedding model (sentence-transformers, local)
# Small and fast: all-MiniLM-L6-v2 (384 dims)
DEFAULT_EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

# Batch size for embedding (avoid OOM on large corpora)
EMBED_BATCH_SIZE = 32

# Metadata keys to store in vector DB (must be Chroma-compatible: str, int, float, bool)
METADATA_KEYS = [
    "fund_name",
    "category",
    "risk",
    "nav",
    "aum",
    "min_investment_amount",
    "return_1y",
    "return_5y",
    "return_10y",
    "scrape_date",
    "source_url",
]
