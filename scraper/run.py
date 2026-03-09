"""
CLI entry point for Phase 1 scraper.
Usage:
  python -m scraper.run
  python -m scraper.run --output-dir ./output --file funds.json
"""
import argparse
import logging
import sys
from pathlib import Path

from scraper.config import get_output_path
from scraper.scraper import scrape_and_save

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Scrape ICICI Prudential MF list from Groww (Phase 1)")
    parser.add_argument("--output-dir", type=str, default=None, help="Output directory for JSON")
    parser.add_argument("--file", type=str, default=None, help="Output filename")
    parser.add_argument("--no-playwright", action="store_true", help="Use requests instead of Playwright (may miss JS content)")
    args = parser.parse_args()
    out_path = get_output_path(output_dir=args.output_dir, filename=args.file)
    try:
        scrape_and_save(output_path=out_path, use_playwright=not args.no_playwright)
        return 0
    except Exception as e:
        logging.exception("Scrape failed: %s", e)
        return 1


if __name__ == "__main__":
    sys.exit(main())
