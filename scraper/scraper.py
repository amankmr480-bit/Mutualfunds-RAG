"""
Phase 1 scraper: fetch ICICI Prudential Mutual Fund list from Groww AMC page.
Uses Playwright for JS-rendered content, then parses with BeautifulSoup.
"""
import json
import logging
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from bs4 import BeautifulSoup

from scraper.config import (
    BASE_URL,
    MAX_RETRIES,
    PAGE_LOAD_TIMEOUT_MS,
    REQUEST_DELAY_SECONDS,
    RETRY_DELAY_SECONDS,
    SCHEMA_VERSION,
    TABLE_WAIT_TIMEOUT_MS,
)
from scraper.parser import (
    ensure_required_fields,
    merge_min_investment_into_funds,
    parse_detail_sections_min_investment,
    parse_fund_table,
)

logger = logging.getLogger(__name__)


def _get_html_playwright() -> str:
    """Fetch page HTML using Playwright (handles JS-rendered content)."""
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        raise ImportError("Install playwright: pip install playwright && playwright install chromium")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.set_default_timeout(PAGE_LOAD_TIMEOUT_MS)
        try:
            page.goto(BASE_URL, wait_until="domcontentloaded")
            # Wait for table or a known element to appear
            page.wait_for_selector("table", timeout=TABLE_WAIT_TIMEOUT_MS)
            time.sleep(REQUEST_DELAY_SECONDS)
            html = page.content()
        finally:
            browser.close()
    return html


def _get_html_requests() -> str:
    """Fallback: fetch with requests (may not get table if page is JS-only)."""
    import requests
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
    }
    r = requests.get(BASE_URL, headers=headers, timeout=30)
    r.raise_for_status()
    return r.text


def fetch_html(use_playwright: bool = True) -> str:
    """Fetch AMC page HTML. Prefer Playwright for full content."""
    for attempt in range(MAX_RETRIES):
        try:
            if use_playwright:
                return _get_html_playwright()
            return _get_html_requests()
        except Exception as e:
            logger.warning("Fetch attempt %s failed: %s", attempt + 1, e)
            if attempt < MAX_RETRIES - 1:
                time.sleep(RETRY_DELAY_SECONDS)
            raise
    raise RuntimeError("Fetch failed after retries")


def scrape_funds(html: str | None = None) -> list[dict[str, Any]]:
    """
    Scrape fund list from Groww AMC page.
    If html is provided, use it; otherwise fetch via Playwright.
    Returns list of fund dicts with required fields.
    """
    if html is None:
        html = fetch_html()
    table_funds = parse_fund_table(html)
    detail_map = parse_detail_sections_min_investment(html)
    merged = merge_min_investment_into_funds(table_funds, detail_map)
    return ensure_required_fields(merged)


def scrape_and_save(
    output_path: str | Path,
    html: str | None = None,
    use_playwright: bool = True,
) -> dict[str, Any]:
    """
    Run scraper and save JSON with metadata.
    Returns the full payload (metadata + funds).
    """
    if html is None:
        html = fetch_html(use_playwright=use_playwright)
    funds = scrape_funds(html=html)
    payload = {
        "metadata": {
            "source_url": BASE_URL,
            "scrape_timestamp": datetime.now(timezone.utc).isoformat(),
            "schema_version": SCHEMA_VERSION,
            "fund_count": len(funds),
        },
        "funds": funds,
    }
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)
    logger.info("Saved %s funds to %s", len(funds), path)
    return payload
