"""
Configuration for Phase 4: Retrieval Layer.
Uses Phase 3 Chroma DB and same embedding model.
"""
from pathlib import Path

# Chroma (same as Phase 3)
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_PERSIST_DIR = PROJECT_ROOT / "phase3_vectorstore" / "chroma_db"
DEFAULT_CHUNKS_PATH = PROJECT_ROOT / "phase2_processing" / "output" / "rag_chunks.json"
COLLECTION_NAME = "icici_prudential_funds"

# Retrieval
DEFAULT_TOP_K = 7
MAX_CONTEXT_CHARS = 6000  # Keep context + query + system prompt within GROQ window

# Abbreviation expansions for query preprocessing
QUERY_ABBREVIATIONS = {
    "1y": "1 year return",
    "5y": "5 year return",
    "10y": "10 year return",
    "1yr": "1 year return",
    "5yr": "5 year return",
    "10yr": "10 year return",
    "nav": "net asset value",
    "aum": "assets under management",
    "er": "expense ratio",
    "exit load": "exit load redemption",
}
