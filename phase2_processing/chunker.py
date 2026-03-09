"""
Phase 2.3: Chunking strategy.
- One chunk per fund: each chunk = one fund's full summary + metadata for RAG.
Output: list of {"text": str, "metadata": dict}.
"""
from typing import Any

from phase2_processing.enrich import build_fund_summary_text


# Metadata keys to store with each chunk (for filtering in Phase 3/4)
CHUNK_METADATA_KEYS = [
    "fund_name",
    "category",
    "risk",
    "nav",
    "aum",
    "min_investment_amount",
    "return_1y",
    "return_5y",
    "return_10y",
]


def fund_to_chunk(fund: dict[str, Any], scrape_date: str | None = None, source_url: str | None = None) -> dict[str, Any]:
    """
    Convert one cleaned+enriched fund to a RAG chunk: { "text": str, "metadata": dict }.
    """
    text = fund.get("summary_text") or build_fund_summary_text(fund)
    metadata: dict[str, Any] = {}
    for k in CHUNK_METADATA_KEYS:
        v = fund.get(k)
        if v is not None:
            metadata[k] = v
    if scrape_date:
        metadata["scrape_date"] = scrape_date
    if source_url:
        metadata["source_url"] = source_url
    return {"text": text, "metadata": metadata}


def build_rag_chunks(
    funds: list[dict[str, Any]],
    scrape_date: str | None = None,
    source_url: str | None = None,
) -> list[dict[str, Any]]:
    """
    Build RAG-ready documents: one chunk per fund.
    Returns list of { "text": str, "metadata": dict }.
    """
    return [
        fund_to_chunk(f, scrape_date=scrape_date, source_url=source_url)
        for f in funds
    ]
