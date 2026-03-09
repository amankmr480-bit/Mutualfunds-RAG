"""
Phase 7.2: Simple monitoring — last run time, status, optional health check.
"""
import json
from pathlib import Path

from phase7_operations.config import LAST_RUN_FILE, STATUS_FILE


def get_last_run() -> str | None:
    """Return last refresh timestamp or None."""
    if not LAST_RUN_FILE.exists():
        return None
    return LAST_RUN_FILE.read_text().strip()


def get_status() -> dict:
    """Return status dict: last_run, success, last_step, error (if any)."""
    if not STATUS_FILE.exists():
        return {}
    try:
        return json.loads(STATUS_FILE.read_text())
    except Exception:
        return {}


def check_pipeline_ready() -> dict:
    """
    Check if pipeline is ready for chat (Phase 1–3 outputs exist).
    Returns dict with ready: bool, checks: {...}.
    """
    from phase7_operations.config import PHASE2_CHUNKS, PHASE3_PERSIST_DIR, SCRAPER_OUTPUT
    checks = {
        "phase1_output": SCRAPER_OUTPUT.exists(),
        "phase2_chunks": PHASE2_CHUNKS.exists(),
        "phase3_chroma": PHASE3_PERSIST_DIR.exists() and any(PHASE3_PERSIST_DIR.iterdir()),
    }
    return {
        "ready": all(checks.values()),
        "checks": checks,
        "status": get_status(),
        "last_refresh": get_last_run(),
    }
