"""
Leak Detector v1 — Revenue Priority Score
Revenue Priority Score = Impact × Confidence × Effort Factor × Time-to-Value Factor
Normalized to 0–100 relative to the highest raw score in the batch.
"""

from __future__ import annotations

from typing import List, Optional


def calculate_revenue_priority_score(
    impact: float, confidence: float, effort: int,
    time_to_value_days: int, max_raw_score: Optional[float] = None,
) -> float:
    if impact < 0:
        raise ValueError("Impact ($) cannot be negative")
    if not 0.0 <= confidence <= 1.0:
        raise ValueError("Confidence must be between 0.0 and 1.0")

    effort = max(1, min(5, effort))
    time_to_value_days = max(1, time_to_value_days)

    effort_factor = (6 - effort) / 5
    time_to_value_factor = 30 / time_to_value_days

    raw_score = impact * confidence * effort_factor * time_to_value_factor

    if max_raw_score is not None and max_raw_score > 0:
        normalized = (raw_score / max_raw_score) * 100
    else:
        normalized = min(100.0, raw_score / 500)

    return round(normalized, 1)


def calculate_scores_for_opportunities(opportunities: List[dict]) -> List[dict]:
    if not opportunities:
        return []

    raw_scores = []
    for opp in opportunities:
        raw = (opp["estimated_monthly_opportunity"] * opp["confidence"]
               * ((6 - max(1, min(5, opp["effort"]))) / 5)
               * (30 / max(1, opp["time_to_value_days"])))
        raw_scores.append(raw)

    max_raw = max(raw_scores) if raw_scores else 1.0

    for opp in opportunities:
        opp["priority_score"] = calculate_revenue_priority_score(
            impact=opp["estimated_monthly_opportunity"],
            confidence=opp["confidence"],
            effort=opp["effort"],
            time_to_value_days=opp["time_to_value_days"],
            max_raw_score=max_raw,
        )

    return sorted(opportunities, key=lambda x: x["priority_score"], reverse=True)
