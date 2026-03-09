"""
Configuration for Phase 2: Data Processing & Enrichment.
Input: Phase 1 scraper output JSON.
Output: Clean dataset (CSV/Parquet) + RAG-ready chunks (JSON).
"""
from pathlib import Path

# Default paths (relative to project root)
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_INPUT_PATH = PROJECT_ROOT / "scraper" / "output" / "icici_prudential_funds.json"
DEFAULT_OUTPUT_DIR = Path(__file__).resolve().parent / "output"

# Output filenames
CLEAN_DATASET_CSV = "funds_clean.csv"
CLEAN_DATASET_PARQUET = "funds_clean.parquet"
RAG_CHUNKS_JSON = "rag_chunks.json"

# Missing-value standard
MISSING_STR = "Not available"

# Normalized category/risk labels (for consistency)
CATEGORY_ALIASES = {
    "equity": "Equity",
    "hybrid": "Hybrid",
    "debt": "Debt",
}

RISK_ALIASES = {
    "very high": "Very High",
    "moderately high": "Moderately High",
    "high": "High",
    "moderate": "Moderate",
    "low": "Low",
}
