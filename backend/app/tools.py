from typing import Any, Dict, Optional

# Verified financial figures (in USD billions) from the indexed FY2024 10-K filings (Item 7, Page 2)
VERIFIED_FINANCIALS: Dict[str, Dict[str, Any]] = {
    "AAPL": {
        "company": "Apple Inc.",
        "document_name": "AAPL_10K_2024.pdf",
        "section": "Item 7. MD&A",
        "page_number": 2,
        "metrics": {
            "revenue": {2023: 383.29, 2024: 391.04, "label": "Total Net Sales (Revenue)"},
            "operating_income": {2023: 114.30, 2024: 123.22, "label": "Operating Income"},
            "net_income": {2024: 93.74, "label": "Net Income"},
            "services_revenue": {2023: 85.20, 2024: 96.17, "label": "Services Revenue"},
        },
    },
    "MSFT": {
        "company": "Microsoft Corporation",
        "document_name": "MSFT_10K_2024.pdf",
        "section": "Item 7. MD&A",
        "page_number": 2,
        "metrics": {
            "revenue": {2023: 211.92, 2024: 245.12, "label": "Total Revenue"},
            "operating_income": {2023: 88.52, 2024: 109.43, "label": "Operating Income"},
            "net_income": {2024: 88.14, "label": "Net Income"},
        },
    },
}


def detect_ticker(question: str, explicit_ticker: Optional[str] = None) -> Optional[str]:
    if explicit_ticker and explicit_ticker.upper() in VERIFIED_FINANCIALS:
        return explicit_ticker.upper()
    q_low = question.lower()
    if "apple" in q_low or "aapl" in q_low or "iphone" in q_low:
        return "AAPL"
    if "microsoft" in q_low or "msft" in q_low or "azure" in q_low:
        return "MSFT"
    return None


def detect_metric(question: str) -> str:
    q_low = question.lower()
    if "services" in q_low:
        return "services_revenue"
    if "operating margin" in q_low:
        return "operating_margin"
    if "operating income" in q_low or "operating profit" in q_low:
        return "operating_income"
    if "net margin" in q_low or "profit margin" in q_low:
        return "net_margin"
    if "net income" in q_low:
        return "net_income"
    return "revenue"


def run_financial_calculation(
    question: str, explicit_ticker: Optional[str] = None
) -> Dict[str, Any]:
    """Run a deterministic Python calculation on verified 10-K figures."""
    ticker = detect_ticker(question, explicit_ticker)
    if not ticker:
        return {
            "supported": False,
            "reason": "Could not identify a supported company (AAPL or MSFT) for calculation.",
        }

    company_data = VERIFIED_FINANCIALS[ticker]
    metrics = company_data["metrics"]
    metric_key = detect_metric(question)

    # Case 1: Operating Margin calculation (Operating Income / Revenue * 100)
    if metric_key == "operating_margin":
        rev_24 = metrics["revenue"][2024]
        op_24 = metrics["operating_income"][2024]
        rev_23 = metrics["revenue"][2023]
        op_23 = metrics["operating_income"][2023]
        margin_24 = round((op_24 / rev_24) * 100, 2)
        margin_23 = round((op_23 / rev_23) * 100, 2)
        delta_bps = round((margin_24 - margin_23) * 100, 0)
        summary = (
            f"Deterministic Calculation ({company_data['company']} - Operating Margin): "
            f"FY2024 Operating Margin was {margin_24}% (${op_24:.2f}B Operating Income / ${rev_24:.2f}B Revenue), "
            f"compared to {margin_23}% in FY2023 (${op_23:.2f}B / ${rev_23:.2f}B), "
            f"representing a change of {margin_24 - margin_23:+.2f} percentage points ({delta_bps:+.0f} bps) [1]."
        )
        return {"supported": True, "ticker": ticker, "summary": summary}

    # Case 2: Net Margin calculation (Net Income / Revenue * 100)
    if metric_key == "net_margin":
        rev_24 = metrics["revenue"][2024]
        ni_24 = metrics["net_income"][2024]
        margin_24 = round((ni_24 / rev_24) * 100, 2)
        summary = (
            f"Deterministic Calculation ({company_data['company']} - FY2024 Net Profit Margin): "
            f"{margin_24}% (${ni_24:.2f}B Net Income / ${rev_24:.2f}B Revenue) [1]."
        )
        return {"supported": True, "ticker": ticker, "summary": summary}

    # Case 3: Year-over-Year change (2023 -> 2024) for Revenue, Operating Income, or Services Revenue
    metric_info = metrics.get(metric_key)
    if not metric_info or 2023 not in metric_info or 2024 not in metric_info:
        return {
            "supported": False,
            "reason": f"Metric '{metric_key}' does not have 2023 and 2024 comparative values in the indexed 10-K.",
        }

    v23 = metric_info[2023]
    v24 = metric_info[2024]
    abs_change = round(v24 - v23, 2)
    pct_change = round(((v24 - v23) / v23) * 100, 2)
    label = metric_info["label"]

    summary = (
        f"Deterministic Calculation ({company_data['company']} - {label}, FY2023 to FY2024): "
        f"{label} changed from ${v23:.2f} billion in FY2023 to ${v24:.2f} billion in FY2024, "
        f"an absolute change of ${abs_change:+.2f} billion ({pct_change:+.2f}%) [1]."
    )
    return {"supported": True, "ticker": ticker, "summary": summary}
