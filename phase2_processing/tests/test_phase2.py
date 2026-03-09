"""
Tests for Phase 2: cleaning, enrichment, chunking, pipeline.
"""
import json
from pathlib import Path

import pytest

from phase2_processing.cleaner import clean_fund, clean_funds
from phase2_processing.enrich import build_fund_summary_text, enrich_funds_with_summary
from phase2_processing.chunker import build_rag_chunks, fund_to_chunk
from phase2_processing.pipeline import run_pipeline, load_phase1_output, CSV_COLUMNS

# Sample raw fund (Phase 1 style)
SAMPLE_FUND = {
    "fund_name": "ICICI Prudential Value Direct Growth",
    "category": "Equity",
    "risk": "Very High",
    "nav": "520.49",
    "expense_ratio": "0.96",
    "return_1y": "12.7%",
    "return_5y": "20.0%",
    "return_10y": "17.1%",
    "exit_load": "Exit load of 1% if redeemed within 12 months",
    "min_investment_amount": None,
    "aum": "60352",
}


# --- Cleaner ---


def test_clean_fund_returns_dict():
    out = clean_fund(SAMPLE_FUND, use_missing_str=True)
    assert isinstance(out, dict)


def test_clean_fund_normalizes_missing():
    fund = {"fund_name": "X", "return_10y": "--", "nav": None}
    out = clean_fund(fund, use_missing_str=True)
    assert out["return_10y"] == "Not available" or out["return_10y"] is None
    assert out.get("nav") is None


def test_clean_fund_normalizes_numbers():
    out = clean_fund(SAMPLE_FUND, use_missing_str=False)
    assert isinstance(out["nav"], (int, float))
    assert out["nav"] == 520.49
    assert out["aum"] == 60352.0 or out["aum"] == 60352


def test_clean_funds_returns_list():
    out = clean_funds([SAMPLE_FUND])
    assert isinstance(out, list)
    assert len(out) == 1


def test_clean_fund_category_risk_normalized():
    out = clean_fund({"fund_name": "F", "category": "equity", "risk": "very high"})
    assert out["category"] == "Equity"
    assert out["risk"] == "Very High"


# --- Enrich ---


def test_build_fund_summary_text_includes_key_fields():
    cleaned = clean_fund(SAMPLE_FUND, use_missing_str=True)
    text = build_fund_summary_text(cleaned)
    assert "ICICI Prudential Value" in text
    assert "Equity" in text
    assert "Very High" in text or "risk" in text.lower()
    assert "520" in text or "NAV" in text
    assert "12.7" in text or "1Y" in text or "return" in text.lower()


def test_enrich_funds_with_summary_adds_summary_text():
    cleaned = [clean_fund(SAMPLE_FUND)]
    enriched = enrich_funds_with_summary(cleaned)
    assert len(enriched) == 1
    assert "summary_text" in enriched[0]
    assert len(enriched[0]["summary_text"]) > 50


# --- Chunker ---


def test_fund_to_chunk_has_text_and_metadata():
    cleaned = clean_fund(SAMPLE_FUND)
    cleaned["summary_text"] = build_fund_summary_text(cleaned)
    chunk = fund_to_chunk(cleaned)
    assert "text" in chunk
    assert "metadata" in chunk
    assert isinstance(chunk["metadata"], dict)


def test_build_rag_chunks_one_per_fund():
    funds = [clean_fund(SAMPLE_FUND), clean_fund({**SAMPLE_FUND, "fund_name": "Other Fund"})]
    for f in funds:
        f["summary_text"] = build_fund_summary_text(f)
    chunks = build_rag_chunks(funds)
    assert len(chunks) == 2
    assert all("text" in c and "metadata" in c for c in chunks)


def test_chunk_metadata_has_fund_name_and_category():
    cleaned = clean_fund(SAMPLE_FUND)
    cleaned["summary_text"] = "dummy"
    chunk = fund_to_chunk(cleaned)
    assert chunk["metadata"].get("fund_name") == "ICICI Prudential Value Direct Growth"
    assert "category" in chunk["metadata"] or "risk" in chunk["metadata"]


# --- Pipeline ---


def test_load_phase1_output_raises_if_missing():
    with pytest.raises(FileNotFoundError):
        load_phase1_output(Path("/nonexistent/file.json"))


def test_run_pipeline_with_real_input(tmp_path):
    """Run pipeline using scraper output if present; else skip."""
    phase1_path = Path(__file__).resolve().parent.parent.parent / "scraper" / "output" / "icici_prudential_funds.json"
    if not phase1_path.exists():
        pytest.skip("Phase 1 output not found; run scraper first")
    result = run_pipeline(input_path=phase1_path, output_dir=tmp_path, save_parquet=False)
    assert "clean_funds" in result
    assert "rag_chunks" in result
    assert "output_paths" in result
    assert result["output_paths"].get("csv")
    assert result["output_paths"].get("rag_chunks")
    assert len(result["clean_funds"]) >= 1
    assert len(result["rag_chunks"]) == len(result["clean_funds"])
    assert (tmp_path / "funds_clean.csv").exists()
    assert (tmp_path / "rag_chunks.json").exists()


def test_rag_chunks_json_structure(tmp_path):
    """RAG chunks file is valid JSON with text and metadata per item."""
    phase1_path = Path(__file__).resolve().parent.parent.parent / "scraper" / "output" / "icici_prudential_funds.json"
    if not phase1_path.exists():
        pytest.skip("Phase 1 output not found")
    run_pipeline(input_path=phase1_path, output_dir=tmp_path)
    with open(tmp_path / "rag_chunks.json", encoding="utf-8") as f:
        chunks = json.load(f)
    assert isinstance(chunks, list)
    for c in chunks:
        assert "text" in c and "metadata" in c
        assert isinstance(c["metadata"], dict)
        assert "fund_name" in c["metadata"]


def test_csv_has_required_columns(tmp_path):
    """Clean CSV contains all architecture columns."""
    phase1_path = Path(__file__).resolve().parent.parent.parent / "scraper" / "output" / "icici_prudential_funds.json"
    if not phase1_path.exists():
        pytest.skip("Phase 1 output not found")
    run_pipeline(input_path=phase1_path, output_dir=tmp_path)
    with open(tmp_path / "funds_clean.csv", encoding="utf-8") as f:
        line = f.readline()
    headers = [h.strip() for h in line.split(",")]
    for col in CSV_COLUMNS:
        assert col in headers, f"Missing column: {col}"
