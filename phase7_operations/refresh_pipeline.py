"""
Phase 7.1: Full data refresh — Phase 1 → Phase 2 → Phase 3.
Run weekly or manually to update fund data and re-index.
"""
import json
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path

# Add project root
_root = Path(__file__).resolve().parent.parent
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

from phase7_operations.config import (
    LAST_RUN_FILE,
    MONITORING_DIR,
    PHASE2_CHUNKS,
    PHASE2_OUTPUT_DIR,
    PHASE3_PERSIST_DIR,
    SCRAPER_OUTPUT,
    STATUS_FILE,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


def run_phase1() -> bool:
    """Run scraper; return True if success."""
    try:
        from scraper.scraper import scrape_and_save
        scrape_and_save(output_path=SCRAPER_OUTPUT, use_playwright=True)
        return SCRAPER_OUTPUT.exists()
    except Exception as e:
        logger.exception("Phase 1 failed: %s", e)
        return False


def run_phase2() -> bool:
    """Run processing; return True if success."""
    try:
        from phase2_processing.pipeline import run_pipeline
        run_pipeline(input_path=SCRAPER_OUTPUT, output_dir=PHASE2_OUTPUT_DIR, save_parquet=False)
        return PHASE2_CHUNKS.exists()
    except Exception as e:
        logger.exception("Phase 2 failed: %s", e)
        return False


def run_phase3() -> bool:
    """Run embedding and vector store; return True if success."""
    try:
        from phase3_vectorstore.pipeline import run_pipeline
        result = run_pipeline(
            chunks_path=PHASE2_CHUNKS,
            persist_dir=PHASE3_PERSIST_DIR,
            replace_collection=True,
        )
        return result.get("chunk_count", 0) >= 1
    except Exception as e:
        logger.exception("Phase 3 failed: %s", e)
        return False


def write_status(success: bool, step: str, error: str | None = None) -> None:
    """Write simple status for monitoring."""
    MONITORING_DIR.mkdir(parents=True, exist_ok=True)
    now = datetime.now(timezone.utc).isoformat()
    with open(LAST_RUN_FILE, "w") as f:
        f.write(now)
    status = {"last_run": now, "success": success, "last_step": step}
    if error:
        status["error"] = error
    with open(STATUS_FILE, "w") as f:
        json.dump(status, f, indent=2)


def run_full_refresh() -> bool:
    """Run Phase 1 → 2 → 3. Return True if all success."""
    logger.info("Starting full refresh (Phase 1 → 2 → 3)")
    if not run_phase1():
        write_status(False, "phase1", "Scraper failed")
        return False
    if not run_phase2():
        write_status(False, "phase2", "Processing failed")
        return False
    if not run_phase3():
        write_status(False, "phase3", "Vector store failed")
        return False
    write_status(True, "complete")
    logger.info("Full refresh completed successfully")
    return True


if __name__ == "__main__":
    ok = run_full_refresh()
    sys.exit(0 if ok else 1)
