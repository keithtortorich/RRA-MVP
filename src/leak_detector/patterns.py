"""Leak Detector — cross-company pattern aggregation.

Reads the per-company observation files a `leak-detector-observe` run
publishes (docs/observations/*.json) and turns them into a pattern read
across the batch: prevalence per signal, which signals co-occur more than
chance (lift), a per-company leak score, and a worst-first ranking.

This module detects nothing new. It only summarizes what the observation
agent already recorded, so every caveat that applies to those signals still
applies here: NOT_REVIEWED signals are excluded from denominators rather
than counted as absent, and nothing here is a dollar claim or a verified
finding — see docs/MEASUREMENT_PROTOCOL.md for what turns an observation
into one of those.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from itertools import combinations
from pathlib import Path
from typing import Any, Dict, List

from leak_detector.browser_scan import observation_key
from leak_detector.verticals.hvac.leak_library import DetectionSignal, get_leak, match_signals

# Maps a browser-observed signal (browser_scan.classify_signals(), the
# vocabulary every published observation file actually uses) to the canonical
# HVAC leak library's DetectionSignal vocabulary (verticals/hvac/leak_library.py),
# so match_signals() can score real HVAC-LEAK-XXX candidates from what the
# observation agent already recorded. Before this bridge existed, the two
# vocabularies shared no names in common (the one literal overlap,
# NO_ONLINE_BOOKING, wasn't referenced by any leak definition), so nothing the
# browser agent found could ever produce a scored leak.
#
# Each mapping is a considered judgment call, not a mechanical rename — kept
# 1:1 and only where the two concepts are close enough to defend out loud:
#   WEAK_CTA            -> no clear above-fold call to action
#   PHONE_NOT_PROMINENT -> no tappable click-to-call on mobile
#   NO_ONLINE_BOOKING   -> no online booking path (exact match)
#   THIN_SERVICE_PAGES  -> weak/thin service pages
#   NO_SMS_OPTION       -> no sms: link or "text us" option
#   NO_FINANCING        -> no financing/payment-plan option (HVAC-LEAK-011)
#   NO_CHAT_WIDGET       -> no instant-contact channel (HVAC-LEAK-012)
# NO_PRICING_GUIDANCE and SLOW_PERFORMANCE are left unmapped: neither has a
# leak in the library that honestly fits it yet, and forcing one in just to
# use the signal would be exactly the kind of overclaiming this project
# guards against everywhere else.
OBSERVATION_SIGNAL_BRIDGE: Dict[str, DetectionSignal] = {
    "WEAK_CTA": DetectionSignal.NO_CTA_ABOVE_FOLD,
    "PHONE_NOT_PROMINENT": DetectionSignal.NO_CLICK_TO_CALL,
    "NO_ONLINE_BOOKING": DetectionSignal.NO_ONLINE_BOOKING,
    "THIN_SERVICE_PAGES": DetectionSignal.WEAK_SERVICE_PAGES,
    "NO_SMS_OPTION": DetectionSignal.NO_SMS_TEXTBACK,
    "NO_FINANCING": DetectionSignal.NO_FINANCING_OPTIONS,
    "NO_CHAT_WIDGET": DetectionSignal.NO_INSTANT_CONTACT_CHANNEL,
}


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class CompanyObservation:
    company: str
    host: str
    target: str
    file: str
    present: List[str] = field(default_factory=list)
    absent: List[str] = field(default_factory=list)
    not_reviewed: List[str] = field(default_factory=list)


def load_observations(observations_dir: str) -> List[CompanyObservation]:
    """Load the currently-active published observation files in a directory.

    Prefers index.json's `runs` list as the active file set: a target that
    was removed from targets.json, or that a later run records as failed,
    drops out of the index and must drop out of the pattern read too —
    otherwise its old file (which still exists on disk) would keep
    inflating companyCount and feeding stale signals into every aggregate
    forever. Falls back to a full directory glob only when no index.json
    exists (e.g. a directory of hand-assembled observation files).

    Either way, files are deduplicated by observation_key() (host, port,
    path — the same identity browser_scan.slug_for() uses for filenames),
    keeping the one with the latest `generatedAt`, since a target whose URL
    changed (e.g. www -> bare domain) can still leave an old slug-named
    file behind without index.json listing it twice.
    """
    index_path = Path(observations_dir) / "index.json"
    index = None
    if index_path.exists():
        try:
            index = json.loads(index_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            index = None

    if index and isinstance(index.get("runs"), list):
        candidate_paths = []
        for run in index["runs"]:
            file_name = run.get("file")
            if not file_name:
                continue
            candidate_path = Path(observations_dir) / file_name
            if candidate_path.exists():
                candidate_paths.append(candidate_path)
    else:
        candidate_paths = [p for p in sorted(Path(observations_dir).glob("*.json"))
                            if p.name != "index.json"]

    latest_by_key: Dict[str, tuple] = {}
    for path in candidate_paths:
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            continue
        if "signals" not in payload:
            continue
        host = payload.get("host") or ""
        key = observation_key(host, payload.get("target") or "") if host else (
            payload.get("company") or path.stem)
        generated_at = str(payload.get("generatedAt", ""))
        existing = latest_by_key.get(key)
        if existing is None or generated_at >= existing[0]:
            latest_by_key[key] = (generated_at, payload, path)

    out: List[CompanyObservation] = []
    for generated_at, payload, path in latest_by_key.values():
        present, absent, not_reviewed = [], [], []
        for sig in payload.get("signals", []):
            sig_type = sig.get("signalType")
            status = sig.get("status")
            if not sig_type:
                continue
            if status == "PRESENT":
                present.append(sig_type)
            elif status == "ABSENT":
                absent.append(sig_type)
            elif status == "NOT_REVIEWED":
                not_reviewed.append(sig_type)
        out.append(CompanyObservation(
            company=payload.get("company") or payload.get("host") or path.stem,
            host=payload.get("host", ""),
            target=payload.get("target", ""),
            file=path.name,
            present=present,
            absent=absent,
            not_reviewed=not_reviewed,
        ))
    out.sort(key=lambda c: c.company)
    return out


def compute_prevalence(companies: List[CompanyObservation]) -> List[Dict[str, Any]]:
    """Share of companies with each signal PRESENT, among those where it was reviewed."""
    signal_types = sorted({s for c in companies for s in (c.present + c.absent)})
    rows = []
    for sig in signal_types:
        reviewed = [c for c in companies if sig in c.present or sig in c.absent]
        present = [c for c in reviewed if sig in c.present]
        rows.append({
            "signalType": sig,
            "presentCount": len(present),
            "reviewedCount": len(reviewed),
            "prevalence": round(len(present) / len(reviewed), 3) if reviewed else 0.0,
            "companies": [c.company for c in present],
        })
    rows.sort(key=lambda r: (-r["prevalence"], -r["presentCount"], r["signalType"]))
    return rows


def compute_cooccurrence(companies: List[CompanyObservation],
                          min_companies: int = 2) -> List[Dict[str, Any]]:
    """Which PRESENT signal pairs travel together more often than chance (lift).

    Lift is p(both) / (p(a) * p(b)) over companies where both signals were
    reviewed. A pair where fewer than `min_companies` share both signals is
    left out — lift on a single data point is noise, not a pattern. A pair
    whose lift doesn't exceed 1 is left out too: this section claims signals
    that travel together more than chance, and reporting an independent or
    negatively-associated pair here would misrepresent it as one.
    """
    if min_companies < 1:
        raise ValueError(f"min_companies must be >= 1, got {min_companies}")
    signal_types = sorted({s for c in companies for s in (c.present + c.absent)})
    rows = []
    for a, b in combinations(signal_types, 2):
        reviewed_both = [c for c in companies
                          if (a in c.present or a in c.absent)
                          and (b in c.present or b in c.absent)]
        if not reviewed_both:
            continue
        both = [c for c in reviewed_both if a in c.present and b in c.present]
        if len(both) < min_companies:
            continue
        p_a = len([c for c in reviewed_both if a in c.present]) / len(reviewed_both)
        p_b = len([c for c in reviewed_both if b in c.present]) / len(reviewed_both)
        p_ab = len(both) / len(reviewed_both)
        if not (p_a and p_b):
            continue
        raw_lift = p_ab / (p_a * p_b)
        if raw_lift <= 1:
            continue
        lift = round(raw_lift, 3)
        rows.append({
            "signalA": a,
            "signalB": b,
            "companiesWithBoth": len(both),
            "companiesReviewed": len(reviewed_both),
            "lift": lift,
            "companies": [c.company for c in both],
        })
    rows.sort(key=lambda r: (-r["lift"], -r["companiesWithBoth"]))
    return rows


def compute_company_scores(companies: List[CompanyObservation]) -> List[Dict[str, Any]]:
    """Per-company leak score: share of reviewed signals found PRESENT.

    Unweighted by design — the leak library's per-signal weights are defined
    against a different signal vocabulary (verticals/hvac/leak_library.py)
    than the observation agent emits, so every reviewed signal here counts
    equally rather than pretending a weight that doesn't exist yet.

    A company with zero reviewed signals (every page failed to render, so
    classify_signals() had nothing to classify) gets `score: None` and
    `unscored: True` rather than a 0.0 — a real error is not the same as a
    company that cleared every check, and worst-first must not put them in
    the same place.
    """
    rows = []
    for c in companies:
        reviewed = len(c.present) + len(c.absent)
        unscored = reviewed == 0
        score = None if unscored else round(len(c.present) / reviewed, 3)
        rows.append({
            "company": c.company,
            "host": c.host,
            "target": c.target,
            "presentCount": len(c.present),
            "reviewedCount": reviewed,
            "notReviewedCount": len(c.not_reviewed),
            "score": score,
            "unscored": unscored,
            "presentSignals": sorted(c.present),
        })
    # Unscored companies sort after every scored one, regardless of score.
    rows.sort(key=lambda r: (r["unscored"], -(r["score"] or 0), -r["presentCount"], r["company"]))
    return rows


def compute_leak_candidates(companies: List[CompanyObservation]) -> List[Dict[str, Any]]:
    """Score canonical HVAC-LEAK-XXX candidates from each company's observed signals.

    Bridges browser_scan's PRESENT signals through OBSERVATION_SIGNAL_BRIDGE and
    runs them against the leak library's match_signals(). Confidence reflects
    only the observation-agent evidence available (min_signals=1 for most
    library leaks, so one bridged signal is enough to surface a candidate) —
    it is not the Minimum Truth Pass, and nothing here is a dollar claim. See
    docs/MEASUREMENT_PROTOCOL.md for what actually turns a candidate into one.
    """
    rows = []
    for c in companies:
        bridged = sorted({OBSERVATION_SIGNAL_BRIDGE[sig].value
                          for sig in c.present if sig in OBSERVATION_SIGNAL_BRIDGE})
        if not bridged:
            continue
        candidates = match_signals(bridged)
        if not candidates:
            continue
        rows.append({
            "company": c.company,
            "host": c.host,
            "target": c.target,
            "bridgedSignals": bridged,
            "candidates": [{
                "leakId": cand.leak_id,
                "name": cand.name,
                "category": cand.category,
                "confidence": cand.confidence,
                "matchedSignals": cand.matched_signals,
            } for cand in candidates],
        })
    rows.sort(key=lambda r: (-r["candidates"][0]["confidence"], r["company"]))
    return rows


def build_patterns_report(companies: List[CompanyObservation],
                           min_companies: int = 2) -> Dict[str, Any]:
    warnings = []
    if len(companies) < 5:
        warnings.append(
            f"Only {len(companies)} company observation(s) loaded — prevalence and "
            "co-occurrence read as noise below ~3-5 companies. Treat this as a "
            "preliminary shape, not a pattern.")
    return {
        "leakDetectorPatterns": 1,
        "generatedAt": now_iso(),
        "companyCount": len(companies),
        "minCompaniesForCooccurrence": min_companies,
        "warnings": warnings,
        "prevalence": compute_prevalence(companies),
        "cooccurrence": compute_cooccurrence(companies, min_companies=min_companies),
        "companyScores": compute_company_scores(companies),
        "leakCandidates": compute_leak_candidates(companies),
    }


def format_summary(report: Dict[str, Any]) -> str:
    """Render the report as Markdown for a CI job summary or a terminal read."""
    lines: List[str] = []
    lines.append(f"## Pattern read — {report.get('companyCount', 0)} companies")
    lines.append("")
    for w in report.get("warnings", []):
        lines.append(f"> {w}")
    lines.append("")

    lines.append("### Worst-first")
    lines.append("| Company | Score | Present / Reviewed | Not reviewed |")
    lines.append("|---|---|---|---|")
    for row in report.get("companyScores", []):
        score_cell = "unscored (0 reviewed)" if row["unscored"] else f"{row['score']:.0%}"
        lines.append(f"| {row['company']} | {score_cell} "
                      f"| {row['presentCount']}/{row['reviewedCount']} "
                      f"| {row['notReviewedCount']} |")
    lines.append("")

    lines.append("### Prevalence by signal")
    lines.append("| Signal | Present | Reviewed | Prevalence |")
    lines.append("|---|---|---|---|")
    for row in report.get("prevalence", []):
        lines.append(f"| `{row['signalType']}` | {row['presentCount']} "
                      f"| {row['reviewedCount']} | {row['prevalence']:.0%} |")
    lines.append("")

    cooc = report.get("cooccurrence", [])
    lines.append("### Co-occurrence (lift > 1 means they travel together)")
    if cooc:
        lines.append("| Signal A | Signal B | Both | Lift |")
        lines.append("|---|---|---|---|")
        for row in cooc:
            lines.append(f"| `{row['signalA']}` | `{row['signalB']}` "
                          f"| {row['companiesWithBoth']} | {row['lift']} |")
    else:
        lines.append("_No pair reached the minimum company count yet._")
    lines.append("")

    candidates = report.get("leakCandidates", [])
    lines.append("### Likely leak, by company (canonical library match, top candidate only)")
    if candidates:
        lines.append("| Company | Leak | Confidence | Matched on |")
        lines.append("|---|---|---|---|")
        for row in candidates:
            top = row["candidates"][0]
            lines.append(f"| {row['company']} | {top['leakId']} — {top['name']} "
                          f"| {top['confidence']:.0%} "
                          f"| {', '.join(f'`{s}`' for s in top['matchedSignals'])} |")
    else:
        lines.append("_No observed signal bridges to a library leak yet._")
    lines.append("")
    return "\n".join(lines)


def write_patterns(report: Dict[str, Any], output_dir: str,
                    filename: str = "patterns.json") -> str:
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    path = out / filename
    path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    return str(path)
