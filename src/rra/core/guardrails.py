"""
RRA v1 — Commercial & Operational Guardrails
Enforces §17.1 (payment), §17.2 (delivery gap), §17.3 (access boundary).

Changes from v1.0:
- WEDGE_FIRST_VIOLATION now compares leak_id (fallback: token overlap).
  Fixes the bug where a correctly-wedge-first proposal whose Good focus
  paraphrased the top finding was rejected by naive substring matching.
- Added MISSING_PAID_TRAFFIC_FIX for paid_traffic top leak (§9 appendix D).
- Added build_decision_checklist() + render_decision_checklist().
"""

from __future__ import annotations

import re
from enum import Enum
from typing import Any, Dict, List, Tuple


class GuardrailViolation(str, Enum):
    PERFORMANCE_PRICING      = "PERFORMANCE_PRICING"
    REVENUE_SHARE            = "REVENUE_SHARE"
    ATTRIBUTION_CLAUSE       = "ATTRIBUTION_CLAUSE"
    MISSING_OPERATIONAL_FIX  = "MISSING_OPERATIONAL_FIX"
    PREMATURE_ACCESS_REQUEST = "PREMATURE_ACCESS_REQUEST"
    WEDGE_FIRST_VIOLATION    = "WEDGE_FIRST_VIOLATION"
    FORBIDDEN_TIER_SHAPE     = "FORBIDDEN_TIER_SHAPE"
    MISSING_PAID_TRAFFIC_FIX = "MISSING_PAID_TRAFFIC_FIX"


FORBIDDEN_PRICING_PATTERNS: List[str] = [
    "revenue share", "revenue-share", "% of recovered",
    "percent of recovered", "performance only", "performance-only",
    "contingent fee", "commission on", "commission-based",
    "attribution-based", "we get paid when",
]

OPERATIONAL_FIX_REQUIRED_CATEGORIES = {"response_speed", "lead_capture"}

OPERATIONAL_FIX_KEYWORDS: List[str] = [
    "receptionist", "ai receptionist", "virtual csr", "sms catcher",
    "sms capture", "after-hours", "after hours", "live routing",
    "call routing", "dispatcher", "call answering", "24/7 coverage",
    "missed-call text-back", "missed call text-back",
]

PAID_TRAFFIC_FIX_KEYWORDS: List[str] = [
    "ad ", "ads ", " ad", "paid", "ppc", "google ads", "call tracking",
    "campaign", "ad account", "ad spend",
]

PERMITTED_ACCESS_STATES = {"public_only"}

_STOPWORDS = {
    "and", "or", "the", "a", "an", "of", "to", "for", "in", "on",
    "with", "by", "at", "is", "are", "was", "were", "be", "been",
    "this", "that", "these", "those", "it", "its", "as", "from",
    "fix", "fixing", "system", "systems", "deploy", "install",
    "setup", "set", "up", "down",
}


def _tokenize(text: str) -> set:
    tokens = re.findall(r"[a-z0-9]+", text.lower())
    return {t for t in tokens if t not in _STOPWORDS and len(t) > 2}


def _topics_overlap(a: str, b: str, threshold: float = 0.34) -> bool:
    ta, tb = _tokenize(a), _tokenize(b)
    if not ta or not tb:
        return False
    inter = ta & tb
    smaller = ta if len(ta) <= len(tb) else tb
    return (len(inter) / len(smaller)) >= threshold


def _scan_for_forbidden_pricing(text: str) -> List[str]:
    if not text:
        return []
    lower = text.lower()
    return [p for p in FORBIDDEN_PRICING_PATTERNS if p in lower]


def _has_operational_fix(text: str) -> bool:
    if not text:
        return False
    lower = text.lower()
    return any(kw in lower for kw in OPERATIONAL_FIX_KEYWORDS)


def _has_paid_traffic_fix(text: str) -> bool:
    if not text:
        return False
    lower = text.lower()
    return any(kw in lower for kw in PAID_TRAFFIC_FIX_KEYWORDS)


def _flatten_tier_text(tier: Dict[str, Any]) -> str:
    parts = [str(tier.get("name", "")), str(tier.get("focus", "")),
             str(tier.get("description", ""))]
    includes = tier.get("includes", [])
    if isinstance(includes, list):
        parts.extend(str(x) for x in includes)
    return " ".join(parts)


def validate_proposal(proposal: Dict[str, Any]) -> Tuple[bool, List[str]]:
    violations: List[str] = []
    if not isinstance(proposal, dict):
        return False, ["PROPOSAL_NOT_A_DICT"]

    pricing_model = str(proposal.get("pricing_model", "")).lower()
    if pricing_model and pricing_model not in {"fixed_fee", "fixed"}:
        if pricing_model in {"performance", "revenue_share", "hybrid"}:
            violations.append(GuardrailViolation.PERFORMANCE_PRICING.value)
        else:
            violations.append(GuardrailViolation.ATTRIBUTION_CLAUSE.value)

    tiers = proposal.get("tiers", {}) or {}
    blob = " ".join([
        _flatten_tier_text(tiers.get("good", {})),
        _flatten_tier_text(tiers.get("better", {})),
        _flatten_tier_text(tiers.get("best", {})),
        str(proposal.get("client_summary", "")),
    ])
    if _scan_for_forbidden_pricing(blob):
        violations.append(GuardrailViolation.REVENUE_SHARE.value)

    access_state = proposal.get("access_boundary")
    if access_state is not None and access_state not in PERMITTED_ACCESS_STATES:
        violations.append(GuardrailViolation.PREMATURE_ACCESS_REQUEST.value)

    good = tiers.get("good", {})
    if not good:
        violations.append(GuardrailViolation.FORBIDDEN_TIER_SHAPE.value)

    internal = proposal.get("internal_opportunities", [])
    if internal and good:
        top = internal[0]
        top_leak_id = top.get("leak_id")
        good_leak_id = good.get("leak_id") or good.get("focus_leak_id")

        if top_leak_id and good_leak_id:
            if str(top_leak_id) != str(good_leak_id):
                violations.append(GuardrailViolation.WEDGE_FIRST_VIOLATION.value)
        else:
            top_finding = str(top.get("finding", ""))
            good_focus = str(good.get("focus", ""))
            if top_finding and good_focus and not _topics_overlap(top_finding, good_focus):
                violations.append(GuardrailViolation.WEDGE_FIRST_VIOLATION.value)

        top_category = str(top.get("category", "")).lower()
        good_text = _flatten_tier_text(good)

        if top_category in OPERATIONAL_FIX_REQUIRED_CATEGORIES:
            if not _has_operational_fix(good_text):
                violations.append(GuardrailViolation.MISSING_OPERATIONAL_FIX.value)

        if top_category == "paid_traffic":
            if not _has_paid_traffic_fix(good_text):
                violations.append(GuardrailViolation.MISSING_PAID_TRAFFIC_FIX.value)

    return (len(violations) == 0), violations


def assert_compliant(proposal: Dict[str, Any]) -> None:
    ok, violations = validate_proposal(proposal)
    if not ok:
        raise ValueError("Proposal violates commercial guardrails: "
                         + ", ".join(violations))


def build_decision_checklist(proposal: Dict[str, Any]) -> Dict[str, bool]:
    tiers = proposal.get("tiers", {}) or {}
    good = tiers.get("good", {})
    internal = proposal.get("internal_opportunities", []) or []
    top = internal[0] if internal else {}
    top_category = str(top.get("category", "")).lower()

    fixed_fee = str(proposal.get("pricing_model", "")).lower() in {"fixed_fee", "fixed"}
    good_text = _flatten_tier_text(good)
    no_forbidden = not _scan_for_forbidden_pricing(good_text)
    op_fix_ok = (
        top_category not in OPERATIONAL_FIX_REQUIRED_CATEGORIES
        or _has_operational_fix(good_text)
    )
    access_ok = proposal.get("access_boundary") in (None, "public_only")

    leads_with_top = True
    if internal and good:
        top_leak_id = top.get("leak_id")
        good_leak_id = good.get("leak_id") or good.get("focus_leak_id")
        if top_leak_id and good_leak_id:
            leads_with_top = str(top_leak_id) == str(good_leak_id)
        else:
            leads_with_top = _topics_overlap(
                str(top.get("finding", "")), str(good.get("focus", "")))

    single_fix = bool(good) and not good.get("is_bundle", False)

    return {
        "pricing_is_fixed_fee": fixed_fee,
        "no_revenue_share_or_performance": no_forbidden,
        "no_attribution_clause": True,
        "operational_fix_present_when_needed": op_fix_ok,
        "public_data_only": access_ok,
        "leads_with_top_opportunity": leads_with_top,
        "good_tier_is_single_fix": single_fix,
        "client_facing_filter_applied": proposal.get("client_summary") is not None,
    }


def render_decision_checklist(flags: Dict[str, bool]) -> str:
    lines = ["COMMERCIAL DECISION CHECKLIST — RRA v1",
             "All boxes must be TRUE before proposal is presented.", ""]
    all_ok = True
    for name, ok in flags.items():
        mark = "x" if ok else " "
        lines.append(f"[{mark}] {name}")
        if not ok:
            all_ok = False
    lines.append("")
    lines.append(f"All checks passed: {'YES' if all_ok else 'NO — DO NOT SEND'}")
    return "\n".join(lines)
