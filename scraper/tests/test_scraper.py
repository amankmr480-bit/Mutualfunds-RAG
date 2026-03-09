"""
Test cases to verify Phase 1 scraping: parsing logic and output schema.
"""
import json
from pathlib import Path

import pytest

from scraper.parser import (
    REQUIRED_FIELDS,
    ensure_required_fields,
    merge_min_investment_into_funds,
    parse_detail_sections_min_investment,
    parse_fund_table,
)
from scraper.scraper import scrape_funds, scrape_and_save


FIXTURES_DIR = Path(__file__).resolve().parent / "fixtures"


def _load_fixture_html(name: str = "sample_amc_page.html") -> str:
    path = FIXTURES_DIR / name
    if not path.exists():
        pytest.skip(f"Fixture not found: {path}")
    return path.read_text(encoding="utf-8")


# --- Unit tests: table parsing ---


def test_parse_fund_table_returns_list():
    """parse_fund_table returns a list."""
    html = _load_fixture_html()
    result = parse_fund_table(html)
    assert isinstance(result, list)


def test_parse_fund_table_extracts_funds():
    """parse_fund_table extracts at least one fund from fixture."""
    html = _load_fixture_html()
    result = parse_fund_table(html)
    assert len(result) >= 1, "Expected at least one fund row from fixture table"


def test_parse_fund_table_fund_name_present():
    """Each parsed row has fund_name."""
    html = _load_fixture_html()
    result = parse_fund_table(html)
    for row in result:
        assert "fund_name" in row
        assert row["fund_name"], "fund_name should be non-empty"


def test_parse_fund_table_required_columns_mapped():
    """Parsed rows contain category, risk, nav, expense_ratio, returns, exit_load, aum."""
    html = _load_fixture_html()
    result = parse_fund_table(html)
    for row in result:
        assert "category" in row
        assert "risk" in row
        assert "nav" in row
        assert "expense_ratio" in row
        assert "return_1y" in row
        assert "return_5y" in row
        assert "return_10y" in row
        assert "exit_load" in row
        assert "aum" in row


def test_parse_fund_table_nav_normalized():
    """NAV is normalized (no ₹ or commas in value)."""
    html = _load_fixture_html()
    result = parse_fund_table(html)
    for row in result:
        nav = row.get("nav")
        if nav is not None:
            assert "₹" not in nav and "," not in nav, f"NAV should be normalized: {nav}"


def test_parse_fund_table_skips_view_all_row():
    """Rows with 'View All' as fund name are skipped."""
    html = _load_fixture_html()
    result = parse_fund_table(html)
    for row in result:
        assert "view all" not in (row.get("fund_name") or "").lower()


# --- Unit tests: detail sections (min investment, AUM) ---


def test_parse_detail_sections_returns_dict():
    """parse_detail_sections_min_investment returns a dict."""
    html = _load_fixture_html()
    result = parse_detail_sections_min_investment(html)
    assert isinstance(result, dict)


def test_parse_detail_sections_extracts_min_investment():
    """Detail sections contain min_investment_amount for at least one fund."""
    html = _load_fixture_html()
    result = parse_detail_sections_min_investment(html)
    assert len(result) >= 1
    with_min = [v for v in result.values() if v.get("min_investment_amount")]
    assert len(with_min) >= 1, "Expected at least one fund with min_investment_amount"


def test_parse_detail_sections_min_investment_normalized():
    """Min investment value is normalized (no ₹ or commas)."""
    html = _load_fixture_html()
    result = parse_detail_sections_min_investment(html)
    for key, entry in result.items():
        val = entry.get("min_investment_amount")
        if val is not None:
            assert "₹" not in val and "," not in val, f"min_investment_amount should be normalized: {val}"


# --- Unit tests: merge and ensure_required_fields ---


def test_merge_min_investment_into_funds():
    """merge_min_investment_into_funds adds min_investment_amount to table rows."""
    table_funds = [
        {"fund_name": "ICICI Prudential Value Direct Growth", "aum": "60352"},
    ]
    detail_map = {
        "icici prudential value direct growth": {"min_investment_amount": "1000", "aum": "60352"},
    }
    merged = merge_min_investment_into_funds(table_funds, detail_map)
    assert merged[0].get("min_investment_amount") == "1000"


def test_ensure_required_fields_all_present():
    """ensure_required_fields returns rows with exactly REQUIRED_FIELDS keys."""
    funds = [{"fund_name": "Test Fund", "category": "Equity"}]
    out = ensure_required_fields(funds)
    assert len(out) == 1
    for key in REQUIRED_FIELDS:
        assert key in out[0], f"Missing required field: {key}"


def test_ensure_required_fields_missing_filled_with_none():
    """Missing fields are set to None."""
    funds = [{"fund_name": "Test Fund"}]
    out = ensure_required_fields(funds)
    assert out[0]["fund_name"] == "Test Fund"
    assert out[0]["nav"] is None
    assert out[0]["min_investment_amount"] is None


# --- Integration-style tests: full scrape pipeline on fixture HTML ---


def test_scrape_funds_with_fixture_html_returns_list():
    """scrape_funds(html=fixture) returns a list (no network)."""
    html = _load_fixture_html()
    result = scrape_funds(html=html)
    assert isinstance(result, list)


def test_scrape_funds_with_fixture_has_required_fields():
    """Each fund from scrape_funds has all REQUIRED_FIELDS."""
    html = _load_fixture_html()
    result = scrape_funds(html=html)
    assert len(result) >= 1
    for fund in result:
        for key in REQUIRED_FIELDS:
            assert key in fund, f"Missing required field in scraped fund: {key}"


def test_scrape_funds_with_fixture_field_types():
    """Scraped fund values are str or None (no unexpected types)."""
    html = _load_fixture_html()
    result = scrape_funds(html=html)
    for fund in result:
        for k, v in fund.items():
            assert v is None or isinstance(v, str), f"Field {k} should be str or None, got {type(v)}"


def test_scrape_and_save_output_schema(tmp_path):
    """scrape_and_save(html=fixture) produces JSON with metadata and funds array."""
    html = _load_fixture_html()
    out_file = tmp_path / "out.json"
    payload = scrape_and_save(output_path=out_file, html=html)
    assert "metadata" in payload
    assert "funds" in payload
    assert "source_url" in payload["metadata"]
    assert "scrape_timestamp" in payload["metadata"]
    assert "fund_count" in payload["metadata"]
    assert isinstance(payload["funds"], list)
    assert len(payload["funds"]) == payload["metadata"]["fund_count"]


def test_scrape_and_save_writes_valid_json(tmp_path):
    """scrape_and_save writes valid JSON file that can be loaded."""
    html = _load_fixture_html()
    out_file = tmp_path / "out.json"
    scrape_and_save(output_path=out_file, html=html)
    with open(out_file, encoding="utf-8") as f:
        loaded = json.load(f)
    assert "metadata" in loaded and "funds" in loaded
    assert len(loaded["funds"]) >= 1
    for fund in loaded["funds"]:
        for key in REQUIRED_FIELDS:
            assert key in fund


def test_scraping_is_done_properly_final_check():
    """
    Final verification: scraping produces usable data with expected structure.
    At least one fund has non-null fund_name, category, risk, and at least one of nav/returns/aum.
    """
    html = _load_fixture_html()
    funds = scrape_funds(html=html)
    assert len(funds) >= 1
    at_least_one_complete = False
    for f in funds:
        if not f.get("fund_name"):
            continue
        if not f.get("category") and not f.get("risk"):
            continue
        if f.get("nav") or f.get("return_1y") or f.get("return_5y") or f.get("aum"):
            at_least_one_complete = True
            break
    assert at_least_one_complete, "Expected at least one fund with name, category/risk, and numeric data"


# --- Optional: live scrape (run with pytest -m integration) ---


@pytest.mark.integration
def test_live_scrape_returns_funds():
    """
    Integration test: run scraper against live Groww page (requires network + Playwright).
    Run with: pytest scraper/tests/test_scraper.py -m integration -v
    """
    try:
        funds = scrape_funds(html=None)  # fetches via Playwright
    except Exception as e:
        pytest.skip(f"Live scrape not available: {e}")
    assert isinstance(funds, list)
    assert len(funds) >= 1, "Live scrape should return at least one fund"
    for fund in funds:
        for key in REQUIRED_FIELDS:
            assert key in fund
