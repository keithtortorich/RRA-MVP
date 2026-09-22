"""
Leak Detector v1 — Client-Facing Summary Filter
Hard boundary between internal data and anything a client sees.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


FORBIDDEN_KEYS = {
    "id", "evidence_ids", "worker_source", "confidence", "observed_at",
    "priority_score", "effort_factor", "roi_assumptions", "business_id",
    "category", "raw_evidence", "agent", "schema_version", "internal_notes",
    "internal_opportunities", "evidence_sources", "recommendation_raw",
    "pricing_model", "access_boundary",
}


def _sanitize(obj: Any) -> Any:
    if isinstance(obj, dict):
        return {k: _sanitize(v) for k, v in obj.items()
                if k not in FORBIDDEN_KEYS and not str(k).startswith("_")}
    if isinstance(obj, list):
        return [_sanitize(item) for item in obj]
    if isinstance(obj, tuple):
        return tuple(_sanitize(item) for item in obj)
    return obj


def _money(value: float) -> int:
    try:
        return int(round(float(value)))
    except (TypeError, ValueError):
        return 0


def _safe_label(opp: Dict[str, Any]) -> str:
    label = opp.get("effort_label")
    if label:
        return str(label)
    mapping = {1: "Trivial", 2: "Low", 3: "Medium", 4: "High", 5: "Very High"}
    raw_effort = opp.get("effort")
    if raw_effort is None:
        return "Medium"
    try:
        effort = int(raw_effort)
    except (TypeError, ValueError):
        return "Medium"
    return mapping.get(effort, "Medium")


def _to_client_opp(opp: Dict[str, Any]) -> Dict[str, Any]:
    recommendation = opp.get("recommendation") or {}
    action = recommendation.get("action") if isinstance(recommendation, dict) else None
    return {
        "finding": opp.get("finding", "Revenue leak identified"),
        "estimated_monthly_impact": _money(opp.get("estimated_monthly_opportunity", 0)),
        "recommended_action": action or "Review and fix",
        "time_to_value": f"{int(opp.get('time_to_value_days', 14))} days",
        "effort": _safe_label(opp),
    }


def client_facing_summary(
    opportunities: List[Dict[str, Any]],
    proposal: Optional[Dict[str, Any]] = None,
    recovered_to_date: float = 0.0,
    client_name: str = "your business",
) -> Dict[str, Any]:
    generated_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    if not opportunities:
        return _sanitize({
            "headline": f"No significant revenue leaks identified for {client_name} at this time.",
            "primary_opportunity": None,
            "additional_opportunities": [],
            "total_monthly_opportunity": 0,
            "recovered_to_date": _money(recovered_to_date),
            "next_step": "No action required at this time.",
            "generated_at": generated_at,
        })

    ranked = sorted(opportunities, key=lambda o: o.get("priority_score", 0), reverse=True)
    primary = ranked[0]
    additional = ranked[1:4]

    primary_client = _to_client_opp(primary)
    additional_client = [_to_client_opp(o) for o in additional]

    total = sum(o.get("estimated_monthly_opportunity", 0) for o in ranked)
    primary_impact = _money(primary.get("estimated_monthly_opportunity", 0))

    summary = {
        "headline": (f"Estimated recovery opportunity for {client_name}: "
                     f"${primary_impact:,} per month from the top identified issue."),
        "primary_opportunity": primary_client,
        "additional_opportunities": additional_client,
        "total_monthly_opportunity": _money(total),
        "recovered_to_date": _money(recovered_to_date),
        "next_step": (f"Fix the primary issue first. "
                      f"Expected time to value: {primary_client['time_to_value']}."),
        "generated_at": generated_at,
    }
    return _sanitize(summary)
