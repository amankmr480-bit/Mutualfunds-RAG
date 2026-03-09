# Phase 1: Data Acquisition & Scraping

Scraper for **ICICI Prudential Mutual Fund** list from [Groww AMC page](https://groww.in/mutual-funds/amc/icici-prudential-mutual-funds).

## Data captured

- **Fund Name**, **Category**, **Risk**, **NAV**, **Expense Ratio**
- **1Y / 5Y / 10Y Returns**
- **Exit Load**, **Min Investment Amount**, **AUM**

Output: JSON with `metadata` (source_url, scrape_timestamp, schema_version, fund_count) and `funds` array.

## Setup

```bash
# From project root (Mutual Funds-RAG)
pip install -r scraper/requirements.txt

# For live scraping (JS-rendered page)
playwright install chromium
```

## Run scraper

```bash
# From project root
python -m scraper.run

# Custom output path
python -m scraper.run --output-dir ./output --file icici_funds.json

# Use requests instead of Playwright (may miss table if page is JS-only)
python -m scraper.run --no-playwright
```

Output is written to `scraper/output/icici_prudential_funds.json` by default.

## Run tests

Verifies parsing and output schema using fixture HTML (no network required):

```bash
# From project root
python -m pytest scraper/tests/test_scraper.py -v
```

## Folder structure

```
scraper/
├── __init__.py
├── config.py           # URL, timeouts, output paths
├── parser.py           # HTML parsing (table + detail sections)
├── scraper.py          # Fetch + scrape + save
├── run.py              # CLI entry point
├── requirements.txt
├── README.md
├── output/             # Created on first run
│   └── icici_prudential_funds.json
└── tests/
    ├── __init__.py
    ├── test_scraper.py
    └── fixtures/
        └── sample_amc_page.html
```

## Schedule (Phase 1)

Scraper is intended to run **weekly** (e.g. cron or task scheduler). See main `RAG_ARCHITECTURE_MUTUAL_FUNDS.md`.
