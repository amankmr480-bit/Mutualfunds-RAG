"""
Phase 2.2: Enrichment for RAG.
- Unified text chunks: readable paragraph per fund (Fund Name, Category, Risk, NAV, Expense Ratio,
  1Y/5Y/10Y returns, Exit Load, Min Investment, AUM) for semantic and keyword search.
- Optional: synthetic Q&A pairs per fund for better retrieval.
"""
from typing import Any


def build_fund_summary_text(fund: dict[str, Any]) -> str:
    """
    Build a single readable paragraph per fund for RAG retrieval.
    Uses _display fields when present (cleaner output), else raw keys.
    """
    name = fund.get("fund_name") or "Unknown"
    category = fund.get("category", "")
    risk = fund.get("risk", "")
    nav = fund.get("nav_display") or fund.get("nav") or "Not available"
    expense = fund.get("expense_ratio_display") or fund.get("expense_ratio") or "Not available"
    r1 = fund.get("return_1y") or "Not available"
    r5 = fund.get("return_5y") or "Not available"
    r10 = fund.get("return_10y") or "Not available"
    exit_load = fund.get("exit_load") or "Not available"
    min_inv = fund.get("min_investment_display") or fund.get("min_investment_amount") or "Not available"
    aum = fund.get("aum_display") or fund.get("aum") or "Not available"

    return (
        f"{name} is an {category} fund with {risk} risk. "
        f"NAV: {nav}; Expense ratio: {expense}. "
        f"Returns: 1Y {r1}, 5Y {r5}, 10Y {r10}. "
        f"Exit load: {exit_load}. "
        f"Minimum investment: {min_inv}; AUM: {aum}."
    )


def generate_synthetic_qa_pairs(fund: dict[str, Any], max_pairs: int = 5) -> list[dict[str, str]]:
    """
    Generate likely user Q&A pairs for this fund (optional enrichment).
    Returns list of {"question": str, "answer": str}.
    """
    name = (fund.get("fund_name") or "").strip() or "this fund"
    qa: list[dict[str, str]] = []
    if fund.get("fund_name"):
        qa.append({"question": f"What is {name}?", "answer": build_fund_summary_text(fund)})
    if fund.get("return_1y") or fund.get("return_5y"):
        qa.append({
            "question": f"What are the returns of {name}?",
            "answer": f"1Y: {fund.get('return_1y') or 'N/A'}, 5Y: {fund.get('return_5y') or 'N/A'}, 10Y: {fund.get('return_10y') or 'N/A'}.",
        })
    if fund.get("nav") is not None or fund.get("nav_display"):
        qa.append({
            "question": f"What is the NAV of {name}?",
            "answer": f"NAV: {fund.get('nav_display') or fund.get('nav') or 'Not available'}.",
        })
    if fund.get("min_investment_display") or fund.get("min_investment_amount"):
        qa.append({
            "question": f"What is the minimum investment for {name}?",
            "answer": f"Minimum investment: {fund.get('min_investment_display') or fund.get('min_investment_amount') or 'Not available'}.",
        })
    if fund.get("exit_load"):
        qa.append({
            "question": f"What is the exit load for {name}?",
            "answer": f"Exit load: {fund.get('exit_load') or 'Not available'}.",
        })
    return qa[:max_pairs]


def enrich_funds_with_summary(funds: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Add 'summary_text' key to each fund (unified paragraph)."""
    out = []
    for f in funds:
        rec = dict(f)
        rec["summary_text"] = build_fund_summary_text(rec)
        out.append(rec)
    return out
