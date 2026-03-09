"""
Configuration for Phase 1 scraper - ICICI Prudential Mutual Fund (Groww).
"""
import os
from pathlib import Path

# Target URL (Groww AMC page)
BASE_URL = "https://groww.in/mutual-funds/amc/icici-prudential-mutual-funds"

# Rate limiting & retries
REQUEST_DELAY_SECONDS = 2.0
MAX_RETRIES = 3
RETRY_DELAY_SECONDS = 5.0

# Timeouts (Playwright)
PAGE_LOAD_TIMEOUT_MS = 30_000
TABLE_WAIT_TIMEOUT_MS = 15_000

# Output
SCHEMA_VERSION = "1.0"
DEFAULT_OUTPUT_DIR = Path(__file__).resolve().parent / "output"
DEFAULT_OUTPUT_FILE = "icici_prudential_funds.json"

def get_output_path(output_dir: str | Path | None = None, filename: str | None = None) -> Path:
    """Return path for scraped JSON output."""
    base = Path(output_dir) if output_dir else DEFAULT_OUTPUT_DIR
    base.mkdir(parents=True, exist_ok=True)
    name = filename or DEFAULT_OUTPUT_FILE
    return base / name
