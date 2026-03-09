"""
Phase 7: Operations & Maintenance — paths and schedule.
"""
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Phase outputs (inputs for next phase)
SCRAPER_OUTPUT = PROJECT_ROOT / "scraper" / "output" / "icici_prudential_funds.json"
PHASE2_CHUNKS = PROJECT_ROOT / "phase2_processing" / "output" / "rag_chunks.json"
PHASE2_OUTPUT_DIR = PROJECT_ROOT / "phase2_processing" / "output"
PHASE3_PERSIST_DIR = PROJECT_ROOT / "phase3_vectorstore" / "chroma_db"

# Monitoring: simple log file for last run and status
MONITORING_DIR = Path(__file__).resolve().parent / "logs"
LAST_RUN_FILE = MONITORING_DIR / "last_refresh.txt"
STATUS_FILE = MONITORING_DIR / "status.json"
