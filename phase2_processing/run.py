"""
CLI entry point for Phase 2: Data Processing & Enrichment.
Usage:
  python -m phase2_processing.run
  python -m phase2_processing.run --input scraper/output/icici_prudential_funds.json --output-dir ./output --parquet
"""
import argparse
import logging
import sys
from pathlib import Path

from phase2_processing.config import DEFAULT_INPUT_PATH, DEFAULT_OUTPUT_DIR
from phase2_processing.pipeline import run_pipeline

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Phase 2: Clean, enrich, and chunk fund data for RAG")
    parser.add_argument("--input", type=str, default=str(DEFAULT_INPUT_PATH), help="Path to Phase 1 JSON output")
    parser.add_argument("--output-dir", type=str, default=None, help="Output directory (default: phase2_processing/output)")
    parser.add_argument("--parquet", action="store_true", help="Also write clean dataset as Parquet")
    args = parser.parse_args()
    output_dir = Path(args.output_dir) if args.output_dir else DEFAULT_OUTPUT_DIR
    try:
        result = run_pipeline(
            input_path=args.input,
            output_dir=output_dir,
            save_parquet=args.parquet,
        )
        print("Phase 2 complete.")
        print("Outputs:", result.get("output_paths", {}))
        return 0
    except Exception as e:
        logging.exception("Phase 2 failed: %s", e)
        return 1


if __name__ == "__main__":
    sys.exit(main())
