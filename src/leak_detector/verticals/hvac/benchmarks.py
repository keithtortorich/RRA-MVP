"""
Leak Detector v1 — HVAC Industry Benchmarks (Conservative)
Used only when the client cannot supply the metric.
"""

from __future__ import annotations

from enum import Enum
from typing import Any, Dict, Optional


class Label(str, Enum):
    KNOWN     = "KNOWN"
    ASSUMED   = "ASSUMED"
    ESTIMATED = "ESTIMATED"
    UNKNOWN   = "UNKNOWN"


HVAC_BENCHMARKS: Dict[str, Dict[str, Any]] = {
    "monthly_inbound_calls": {
        "value": 120, "label": Label.ESTIMATED,
        "notes": "Conservative mid-range for 2–8 tech residential HVAC.",
        "source": "Industry ranges 2025-2026 (ServiceTitan / CallJolt aggregated)"},
    "missed_call_rate": {
        "value": 0.45, "label": Label.ESTIMATED,
        "notes": "Industry reports 25-62%. We use 45% as realistic average.",
        "source": "CallJolt / ServiceTitan 2025-2026"},
    "after_hours_call_share": {
        "value": 0.35, "label": Label.ESTIMATED,
        "notes": "Common observed range.",
        "source": "Multiple 2025-2026 home-service studies"},
    "call_to_book_rate": {
        "value": 0.40, "label": Label.ESTIMATED,
        "notes": "ServiceTitan average ~38%. Top performers 65-85%.",
        "source": "ServiceTitan / industry aggregates"},
    "estimate_close_rate": {
        "value": 0.38, "label": Label.ESTIMATED,
        "notes": "Residential HVAC replacement/service close rates 35-45%.",
        "source": "ACHR News / Service Roundtable ranges"},
    "web_form_to_conversation_rate": {
        "value": 0.45, "label": Label.ESTIMATED,
        "notes": "Many form leads never become a real conversation.",
        "source": "CallRail / home-service studies"},
    "average_service_ticket": {
        "value": 550, "label": Label.ESTIMATED,
        "notes": "Repair tickets often $300-600; blended service average.",
        "source": "MarginPlug / ACHR / 2026 reports"},
    "average_replacement_ticket": {
        "value": 7500, "label": Label.ESTIMATED,
        "notes": "Typical residential replacement range.",
        "source": "Industry financial benchmarks 2026"},
    "contribution_margin_per_job": {
        "value": 0.40, "label": Label.ASSUMED,
        "notes": "Conservative contribution margin assumption.",
        "source": "Internal modeling assumption"},
    "response_under_5min_booking_lift": {
        "value": 0.25, "label": Label.ESTIMATED,
        "notes": "Modest recoverable portion of documented lifts.",
        "source": "MIT / Harvard lead response studies"},
}


def get_benchmark(key: str) -> Dict[str, Any]:
    if key not in HVAC_BENCHMARKS:
        raise KeyError(f"No HVAC benchmark defined for '{key}'")
    return HVAC_BENCHMARKS[key].copy()


def resolve_metric(client_value: Optional[float], benchmark_key: str,
                    client_label: Label = Label.KNOWN) -> Dict[str, Any]:
    if client_value is not None:
        return {
            "value": client_value,
            "label": client_label.value if isinstance(client_label, Label) else str(client_label),
            "source": "client_provided",
            "notes": "Supplied by client",
        }
    bench = get_benchmark(benchmark_key)
    label = bench["label"]
    return {
        "value": bench["value"],
        "label": label.value if isinstance(label, Label) else str(label),
        "source": bench.get("source", "industry_benchmark"),
        "notes": bench.get("notes", ""),
    }
