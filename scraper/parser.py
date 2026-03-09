"""
Parse Groww AMC page HTML to extract fund table and detail sections.
Uses BeautifulSoup; expects HTML from Playwright or similar.
"""
import re
from typing import Any

from bs4 import BeautifulSoup


# Required fields per architecture
REQUIRED_FIELDS = [
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


def _normalize_percent(s: str) -> str | None:
    """Return percentage string or None for N/A/--."""
    if not s or not s.strip():
        return None
    s = s.strip().replace(",", "")
    if s in ("--", "N/A", "NA", "-", ""):
        return None
    return s


def _normalize_number(s: str) -> str | None:
    """Strip ₹, commas, 'Cr'; return cleaned string or None."""
    if not s or not s.strip():
        return None
    s = s.strip().replace("₹", "").replace(",", "").replace(" ", "").replace("Cr", "").strip()
    if s in ("--", "N/A", "-", ""):
        return None
    return s


def _parse_nav(s: str) -> str | None:
    """NAV is a number, may have commas."""
    return _normalize_number(s) if s else None


def _parse_aum(s: str) -> str | None:
    """AUM often like ₹6,658 or ₹6,658Cr."""
    return _normalize_number(s) if s else None


def _parse_min_investment(s: str) -> str | None:
    """Min investment like ₹5,000 or ₹100."""
    return _normalize_number(s) if s else None


def parse_fund_table(html: str) -> list[dict[str, Any]]:
    """
    Parse the main 'List of ICICI Prudential Mutual Fund in India' table.
    Returns list of dicts with keys: fund_name, category, risk, nav, expense_ratio,
    return_1y, return_3y, return_5y, return_7y, return_10y, rating, aum, exit_load.
    """
    soup = BeautifulSoup(html, "html.parser")
    rows: list[dict[str, Any]] = []

    # Try common table selectors
    tables = soup.find_all("table")
    target_table = None
    for t in tables:
        headers = [th.get_text(strip=True).lower() for th in t.find_all("th")]
        if "fund name" in " ".join(headers) and "nav" in " ".join(headers):
            target_table = t
            break

    if not target_table:
        return rows

    thead = target_table.find("thead")
    header_cells = thead.find_all("th") if thead else target_table.find("tr").find_all("th") if target_table.find("tr") else []
    if not header_cells:
        header_cells = target_table.find("tr").find_all("th") if target_table.find("tr") else []
    col_names = [c.get_text(strip=True).lower() for c in header_cells]

    tbody = target_table.find("tbody") or target_table
    trs = tbody.find_all("tr") if tbody else []

    for tr in trs:
        cells = tr.find_all(["td", "th"])
        if len(cells) < 5:
            continue
        row_text = [c.get_text(separator=" ", strip=True) for c in cells]
        # Build dict by position; map common column names
        row_dict: dict[str, Any] = {}
        for i, name in enumerate(col_names):
            if i >= len(row_text):
                break
            val = row_text[i]
            if "fund name" in name or "fund name" in name.replace("name", " name"):
                row_dict["fund_name"] = val
            elif "category" in name:
                row_dict["category"] = val or None
            elif "risk" in name:
                row_dict["risk"] = val or None
            elif "nav" in name and "expense" not in name:
                row_dict["nav"] = _parse_nav(val)
            elif "expense" in name:
                row_dict["expense_ratio"] = _normalize_percent(val)
            elif "1y" in name or "1 y" in name:
                row_dict["return_1y"] = _normalize_percent(val)
            elif "3y" in name or "3 y" in name:
                row_dict["return_3y"] = _normalize_percent(val)
            elif "5y" in name or "5 y" in name:
                row_dict["return_5y"] = _normalize_percent(val)
            elif "7y" in name or "7 y" in name:
                row_dict["return_7y"] = _normalize_percent(val)
            elif "10y" in name or "10 y" in name:
                row_dict["return_10y"] = _normalize_percent(val)
            elif "rating" in name:
                row_dict["rating"] = val or None
            elif "fund size" in name or "aum" in name:
                row_dict["aum"] = _parse_aum(val)
            elif "exit" in name:
                row_dict["exit_load"] = val or None

        # Skip "View All", header row, or non-fund rows
        fn = row_dict.get("fund_name") or ""
        fn_lower = fn.lower()
        if not fn or "view all" in fn_lower:
            continue
        if fn_lower in ("fund name", "category", "nav", "risk", "expense ratio", "rating"):
            continue
        rows.append(row_dict)

    return rows


def parse_detail_sections_min_investment(html: str) -> dict[str, dict[str, Any]]:
    """
    Parse 'Let's have a closer look' sections to extract min_investment_amount and aum per fund.
    Returns dict keyed by normalized fund name (for matching) with { min_investment_amount, aum }.
    """
    soup = BeautifulSoup(html, "html.parser")
    result: dict[str, dict[str, Any]] = {}

    # Look for headings (h2, h3) that are fund names, then next table or paragraph with Min Investment / AUM
    for tag in soup.find_all(["h2", "h3"]):
        fund_heading = tag.get_text(strip=True)
        if "view mutual funds" in fund_heading.lower() or "let's have" in fund_heading.lower():
            continue
        if "ICICI Prudential" not in fund_heading:
            continue
        # Normalize key: lowercase, collapse spaces
        key = re.sub(r"\s+", " ", fund_heading).strip().lower()
        entry: dict[str, Any] = {"min_investment_amount": None, "aum": None}
        # Next siblings: look for "Minimum Investment Amount: ... ₹X" or table with Min Investment Amt
        next_el = tag.find_next_sibling()
        for _ in range(15):
            if next_el is None:
                break
            text = next_el.get_text() if next_el else ""
            # Lump sum minimum amount ... is ₹X
            match = re.search(r"is\s*₹\s*([\d,]+)", text, re.IGNORECASE)
            if match:
                entry["min_investment_amount"] = _parse_min_investment("₹" + match.group(1))
            if next_el.name == "table":
                for r in next_el.find_all("tr"):
                    tds = r.find_all("td")
                    if len(tds) >= 2:
                        label = (tds[0].get_text(strip=True) or "").lower()
                        value = tds[1].get_text(strip=True) if len(tds) > 1 else ""
                        if "min investment" in label:
                            entry["min_investment_amount"] = _parse_min_investment(value)
                        if "aum" in label or "fund size" in label:
                            entry["aum"] = _parse_aum(value)
            next_el = next_el.find_next_sibling()
        result[key] = entry

    return result


def merge_min_investment_into_funds(
    table_funds: list[dict[str, Any]],
    detail_map: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    """
    Match table rows with detail sections by fund name and set min_investment_amount (and aum if missing).
    """
    for fund in table_funds:
        name = (fund.get("fund_name") or "").strip()
        key = re.sub(r"\s+", " ", name).strip().lower()
        if key in detail_map:
            fund["min_investment_amount"] = detail_map[key].get("min_investment_amount")
            if not fund.get("aum"):
                fund["aum"] = detail_map[key].get("aum")
        if "min_investment_amount" not in fund:
            fund["min_investment_amount"] = None
    return table_funds


def ensure_required_fields(funds: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Ensure each fund has all REQUIRED_FIELDS; use None for missing."""
    out = []
    for f in funds:
        row = {k: f.get(k) for k in REQUIRED_FIELDS}
        # Map return_1y/5y/10y if we stored under different keys
        if "return_1y" not in row and "return_1y" in f:
            row["return_1y"] = f["return_1y"]
        if "return_5y" not in row and "return_5y" in f:
            row["return_5y"] = f["return_5y"]
        if "return_10y" not in row and "return_10y" in f:
            row["return_10y"] = f["return_10y"]
        out.append(row)
    return out
