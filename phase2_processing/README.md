# Phase 2: Data Processing & Enrichment

Takes **Phase 1** scraper output (JSON) and produces:
- **Structured dataset:** clean table (CSV, optional Parquet) with normalized fields.
- **RAG-ready documents:** one chunk per fund with `text` (readable summary) and `metadata` for retrieval.

Per [RAG_ARCHITECTURE_MUTUAL_FUNDS.md](../RAG_ARCHITECTURE_MUTUAL_FUNDS.md).

## Steps

1. **Cleaning & normalization**  
   Missing values → `"Not available"`; numbers parsed (NAV, returns, AUM, etc.); category/risk labels normalized; exit load kept as text.

2. **Enrichment for RAG**  
   One unified paragraph per fund: Fund Name, Category, Risk, NAV, Expense Ratio, 1Y/5Y/10Y returns, Exit Load, Min Investment, AUM.

3. **Chunking**  
   One chunk per fund: `{ "text": "<summary paragraph>", "metadata": { fund_name, category, risk, nav, aum, ... } }`.

## Input

- Phase 1 JSON: `scraper/output/icici_prudential_funds.json` (default).

## Output (in `phase2_processing/output/`)

| File | Description |
|------|-------------|
| `funds_clean.csv` | Clean table: fund_name, category, risk, nav, expense_ratio, return_1y/5y/10y, exit_load, min_investment_amount, aum. |
| `rag_chunks.json` | List of `{ "text": "...", "metadata": { ... } }` for Phase 3 embedding/indexing. |
| `funds_clean.parquet` | Optional; written if `--parquet` is used (requires pandas + pyarrow). |

## Setup

No extra dependencies for CSV + JSON. For Parquet:

```bash
pip install pandas pyarrow
```

## Run

From project root (`Mutual Funds-RAG`):

```bash
# Default: read scraper/output/icici_prudential_funds.json, write to phase2_processing/output/
python -m phase2_processing.run

# Custom input/output
python -m phase2_processing.run --input scraper/output/icici_prudential_funds.json --output-dir ./my_output

# Also write Parquet
python -m phase2_processing.run --parquet
```

## Tests

```bash
# From project root
python -m pytest phase2_processing/tests/test_phase2.py -v
```

Tests that use Phase 1 output are skipped if `scraper/output/icici_prudential_funds.json` is missing (run Phase 1 first).

## Folder structure

```
phase2_processing/
├── __init__.py
├── config.py       # Paths, missing-str, category/risk aliases
├── cleaner.py      # clean_fund, clean_funds
├── enrich.py       # build_fund_summary_text, enrich_funds_with_summary
├── chunker.py      # fund_to_chunk, build_rag_chunks
├── pipeline.py     # load_phase1_output, run_pipeline
├── run.py          # CLI
├── requirements.txt
├── README.md
├── output/         # Created on first run
│   ├── funds_clean.csv
│   ├── rag_chunks.json
│   └── (funds_clean.parquet if --parquet)
└── tests/
    ├── __init__.py
    └── test_phase2.py
```
