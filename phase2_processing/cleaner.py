"""
Phase 2.1: Cleaning & Normalization.
- Standardize missing values (--, N/A, empty) to None or 'Not available'.
- Parse numbers: NAV, returns, expense ratio, AUM (commas, Cr suffix).
- Normalize text: category, risk; trim whitespace.
- Exit load: keep as text.
"""
from typing import Any

from phase2_processing.config import CATEGORY_ALIASES, MISSING_STR, RISK_ALIASES

# Values treated as missing
MISSING_VALUES = ("--", "-", "n/a", "na", "null", "")


def _is_missing(val: Any) -> bool:
    if val is None:
        return True
    if isinstance(val, str):
        return val.strip().lower() in MISSING_VALUES
    return False


def _normalize_missing(val: Any) -> str | None:
    """Return None for missing; optionally use MISSING_STR for display."""
    if _is_missing(val):
        return None
    return val if isinstance(val, str) else str(val)


def _normalize_number_raw(s: Any) -> float | None:
    """Parse number: strip ₹, commas, Cr; return float or None."""
    if s is None or (isinstance(s, str) and s.strip().lower() in MISSING_VALUES):
        return None
    if isinstance(s, (int, float)):
        return float(s)
    s = str(s).strip().replace("₹", "").replace(",", "").replace(" ", "").replace("Cr", "").replace("%", "").strip()
    if not s:
        return None
    try:
        return float(s)
    except ValueError:
        return None


def _normalize_percent_display(s: Any) -> str | None:
    """Return percentage string for display (e.g. '8.9%') or None."""
    n = _normalize_number_raw(s)
    if n is None:
        return None
    return f"{n}%"


def _normalize_text(s: Any) -> str | None:
    """Trim whitespace; return None if missing."""
    if _is_missing(s):
        return None
    t = (s or "").strip()
    return t if t else None


def _normalize_category(s: Any) -> str | None:
    """Normalize category label."""
    t = _normalize_text(s)
    if not t:
        return None
    key = t.lower().strip()
    return CATEGORY_ALIASES.get(key, t)


def _normalize_risk(s: Any) -> str | None:
    """Normalize risk label."""
    t = _normalize_text(s)
    if not t:
        return None
    key = t.lower().strip()
    return RISK_ALIASES.get(key, t)


def clean_fund(fund: dict[str, Any], use_missing_str: bool = False) -> dict[str, Any]:
    """
    Clean and normalize a single fund record.
    Numbers are kept as typed (float where applicable) for CSV/Parquet; string forms for display in chunks.
    use_missing_str: if True, replace None with MISSING_STR for string fields in output.
    """
    out: dict[str, Any] = {}
    # fund_name: text
    out["fund_name"] = _normalize_text(fund.get("fund_name")) or (MISSING_STR if use_missing_str else None)
    # category, risk: normalized labels
    out["category"] = _normalize_category(fund.get("category")) or (MISSING_STR if use_missing_str else None)
    out["risk"] = _normalize_risk(fund.get("risk")) or (MISSING_STR if use_missing_str else None)
    # NAV: float for dataset, keep string for display in chunks
    nav_raw = _normalize_number_raw(fund.get("nav"))
    out["nav"] = nav_raw
    out["nav_display"] = f"{nav_raw}" if nav_raw is not None else (MISSING_STR if use_missing_str else None)
    # expense_ratio: float
    out["expense_ratio"] = _normalize_number_raw(fund.get("expense_ratio"))
    out["expense_ratio_display"] = _normalize_percent_display(fund.get("expense_ratio")) or (MISSING_STR if use_missing_str else None)
    # returns: percent display
    out["return_1y"] = _normalize_percent_display(fund.get("return_1y")) or (MISSING_STR if use_missing_str else None)
    out["return_5y"] = _normalize_percent_display(fund.get("return_5y")) or (MISSING_STR if use_missing_str else None)
    out["return_10y"] = _normalize_percent_display(fund.get("return_10y")) or (MISSING_STR if use_missing_str else None)
    # exit_load: keep as text, normalize missing
    out["exit_load"] = _normalize_text(fund.get("exit_load")) or (MISSING_STR if use_missing_str else None)
    # min_investment_amount: number (display as string with ₹ for chunks)
    min_inv = _normalize_number_raw(fund.get("min_investment_amount"))
    out["min_investment_amount"] = min_inv
    out["min_investment_display"] = f"₹{int(min_inv)}" if min_inv is not None else (MISSING_STR if use_missing_str else None)
    # AUM: number (in Cr)
    aum = _normalize_number_raw(fund.get("aum"))
    out["aum"] = aum
    out["aum_display"] = f"₹{int(aum)} Cr" if aum is not None else (MISSING_STR if use_missing_str else None)
    return out


def clean_funds(funds: list[dict[str, Any]], use_missing_str: bool = True) -> list[dict[str, Any]]:
    """Clean and normalize a list of fund records. Default: use 'Not available' for missing strings."""
    return [clean_fund(f, use_missing_str=use_missing_str) for f in funds]
