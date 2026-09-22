"""
Leak Detector v1 — Effort Estimation Module
Effort Factor = (6 - Effort) / 5
"""

from __future__ import annotations

from enum import IntEnum
from typing import Dict, Optional, Tuple


class EffortLevel(IntEnum):
    TRIVIAL   = 1
    LOW       = 2
    MEDIUM    = 3
    HIGH      = 4
    VERY_HIGH = 5


EFFORT_ANCHORS: Dict[int, Dict[str, str]] = {
    1: {"label": "Trivial",
        "description": "Config / text / template only. No integration, no process change.",
        "examples": "Change CTA copy, add click-to-call, update GMB hours, simple review reply template",
        "calendar": "Hours", "person_days": "0.1 – 0.5"},
    2: {"label": "Low",
        "description": "Single tool or process, minimal client coordination.",
        "examples": "Missed-call text-back, basic form friction reduction, automated review request setup",
        "calendar": "1–3 days", "person_days": "0.5 – 2"},
    3: {"label": "Medium",
        "description": "Light integration or cross-function coordination required.",
        "examples": "New booking flow + calendar sync, after-hours answering service, structured follow-up sequences",
        "calendar": "1–2 weeks", "person_days": "3 – 8"},
    4: {"label": "High",
        "description": "Multi-system integration or significant process redesign.",
        "examples": "CRM + phone system integration, custom estimate follow-up automation, multi-location reputation system",
        "calendar": "2–6 weeks", "person_days": "10 – 25"},
    5: {"label": "Very High",
        "description": "Major build, organizational change, or new tech stack.",
        "examples": "Custom revenue recovery platform, full sales process redesign + training, platform migration",
        "calendar": "1–3+ months", "person_days": "30+"},
}

T_SHIRT_TO_EFFORT = {"XS": 1, "S": 2, "M": 3, "L": 4, "XL": 5}


def validate_effort(effort: int) -> int:
    if not isinstance(effort, int):
        raise TypeError(f"Effort must be an integer, got {type(effort)}")
    return max(1, min(5, effort))


def effort_factor(effort: int) -> float:
    effort = validate_effort(effort)
    return (6 - effort) / 5.0


def estimate_effort_from_dimensions(
    technical: int, integration: int, coordination: int,
    uncertainty: int = 3,
    weights: Optional[Tuple[float, float, float, float]] = None,
) -> int:
    for val in (technical, integration, coordination, uncertainty):
        if not 1 <= val <= 5:
            raise ValueError(f"Each dimension must be 1–5, got {val}")
    if weights is None:
        weights = (0.30, 0.25, 0.25, 0.20)
    if abs(sum(weights) - 1.0) > 1e-6:
        raise ValueError("Weights must sum to 1.0")
    weighted = (technical * weights[0] + integration * weights[1]
                + coordination * weights[2] + uncertainty * weights[3])
    return validate_effort(round(weighted))


def effort_from_tshirt(size: str) -> int:
    size = size.upper().strip()
    if size not in T_SHIRT_TO_EFFORT:
        raise ValueError(f"Unknown T-shirt size: {size}. Use XS, S, M, L, XL")
    return T_SHIRT_TO_EFFORT[size]


def describe_effort(effort: int) -> Dict[str, str]:
    return EFFORT_ANCHORS[validate_effort(effort)].copy()


def format_effort_rationale(
    effort: int, technical: Optional[int] = None,
    integration: Optional[int] = None, coordination: Optional[int] = None,
    uncertainty: Optional[int] = None, notes: str = "",
) -> str:
    effort = validate_effort(effort)
    anchor = EFFORT_ANCHORS[effort]
    parts = [
        f"Effort {effort} ({anchor['label']}): {anchor['description']}",
        f"Typical calendar: {anchor['calendar']} | Person-days: {anchor['person_days']}",
    ]
    if any(v is not None for v in (technical, integration, coordination, uncertainty)):
        parts.append(f"Dimensions → technical={technical}, integration={integration}, "
                     f"coordination={coordination}, uncertainty={uncertainty}")
    if notes:
        parts.append(f"Notes: {notes}")
    return " | ".join(parts)


def apply_effort_to_opportunity(opportunity: dict) -> dict:
    effort = validate_effort(opportunity.get("effort", 3))
    opportunity["effort"] = effort
    opportunity["effort_factor"] = effort_factor(effort)
    opportunity["effort_label"] = EFFORT_ANCHORS[effort]["label"]
    return opportunity
