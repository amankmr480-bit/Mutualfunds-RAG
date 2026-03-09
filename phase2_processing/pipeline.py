"""
Phase 2 pipeline: load Phase 1 output → clean → enrich → chunk → save.
Outputs: clean dataset (CSV, optional Parquet) + RAG-ready chunks (JSON).
"""
import csv
import json
import logging
from pathlib import Path
from typing import Any

from phase2_processing.chunker import build_rag_chunks
from phase2_processing.cleaner import clean_funds
from phase2_processing.config import (
    CLEAN_DATASET_CSV,
    CLEAN_DATASET_PARQUET,
    DEFAULT_INPUT_PATH,
    DEFAULT_OUTPUT_DIR,
    RAG_CHUNKS_JSON,
)
from phase2_processing.enrich import enrich_funds_with_summary

logger = logging.getLogger(__name__)

# CSV columns (aligned to architecture)
CSV_COLUMNS = [
    "fund_name",
    "category",
    "risk",
    "nav",
    "expense_ratio",
    "return_1y",
    "return_5y",
    "return_10y",
    "exit_load",
    "min_investment_amount",
    "aum",
]


def load_phase1_output(input_path: str | Path) -> dict[str, Any]:
    """Load Phase 1 scraper JSON."""
    path = Path(input_path)
    if not path.exists():
        raise FileNotFoundError(f"Phase 1 output not found: {path}")
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _row_for_csv(fund: dict[str, Any]) -> dict[str, str]:
    """Convert cleaned fund to CSV row (all values as string)."""
    row = {}
    for col in CSV_COLUMNS:
        val = fund.get(col)
        if val is None:
            row[col] = ""
        elif isinstance(val, float):
            row[col] = str(val)
        else:
            row[col] = str(val)
    return row


def save_clean_csv(funds: list[dict[str, Any]], output_path: Path) -> None:
    """Write clean dataset to CSV."""
    if not funds:
        logger.warning("No funds to write to CSV")
        return
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_COLUMNS, extrasaction="ignore")
        writer.writeheader()
        for fund in funds:
            writer.writerow(_row_for_csv(fund))
    logger.info("Wrote CSV: %s", output_path)


def save_rag_chunks(chunks: list[dict[str, Any]], output_path: Path) -> None:
    """Write RAG chunks to JSON."""
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(chunks, f, indent=2, ensure_ascii=False)
    logger.info("Wrote RAG chunks: %s (%s chunks)", output_path, len(chunks))


def run_pipeline(
    input_path: str | Path | None = None,
    output_dir: str | Path | None = None,
    save_parquet: bool = False,
) -> dict[str, Any]:
    """
    Run Phase 2: load → clean → enrich → chunk → save.
    Returns summary: { clean_funds, rag_chunks, output_paths }.
    """
    input_path = Path(input_path or DEFAULT_INPUT_PATH)
    output_dir = Path(output_dir or DEFAULT_OUTPUT_DIR)
    output_dir.mkdir(parents=True, exist_ok=True)

    data = load_phase1_output(input_path)
    funds_raw = data.get("funds", [])
    metadata = data.get("metadata", {})
    source_url = metadata.get("source_url")
    scrape_ts = metadata.get("scrape_timestamp", "")
    scrape_date = scrape_ts[:10] if isinstance(scrape_ts, str) and len(scrape_ts) >= 10 else None

    if not funds_raw:
        logger.warning("No funds in Phase 1 output")
        return {"clean_funds": [], "rag_chunks": [], "output_paths": {}}

    # Clean
    clean_funds_list = clean_funds(funds_raw, use_missing_str=True)
    # Enrich (add summary_text)
    enriched = enrich_funds_with_summary(clean_funds_list)
    # Chunk (one per fund)
    chunks = build_rag_chunks(enriched, scrape_date=scrape_date, source_url=source_url)

    # Save clean dataset (CSV)
    csv_path = output_dir / CLEAN_DATASET_CSV
    save_clean_csv(clean_funds_list, csv_path)

    # Save Parquet if requested
    parquet_path = output_dir / CLEAN_DATASET_PARQUET
    if save_parquet:
        try:
            import pandas as pd
            df = pd.DataFrame(clean_funds_list)
            df.to_parquet(parquet_path, index=False)
            logger.info("Wrote Parquet: %s", parquet_path)
        except ImportError:
            logger.warning("pandas/pyarrow not installed; skipping Parquet")

    # Save RAG chunks
    chunks_path = output_dir / RAG_CHUNKS_JSON
    save_rag_chunks(chunks, chunks_path)

    output_paths = {"csv": str(csv_path), "rag_chunks": str(chunks_path)}
    if save_parquet and parquet_path.exists():
        output_paths["parquet"] = str(parquet_path)

    return {
        "clean_funds": clean_funds_list,
        "rag_chunks": chunks,
        "output_paths": output_paths,
    }
