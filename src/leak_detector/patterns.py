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
    """Load every published per-company observation file in a directory.

    Skips index.json and anything without a `signals` key rather than
    guessing what it is. A target whose URL changed (e.g. www -> bare
    domain) leaves its old slug-named file behind rather than replacing it,
    so files are deduplicated by host, keeping the one with the latest
    `generatedAt` — otherwise the same company would be counted twice and
    skew prevalence, scores, and co-occurrence.
    """
    latest_by_key: Dict[str, tuple] = {}
    for path in sorted(Path(observations_dir).glob("*.json")):
        if path.name == "index.json":
            continue
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            continue
        if "signals" not in payload:
            continue
        key = payload.get("host") or payload.get("company") or path.stem
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
    left out — lift on a single data point is noise, not a pattern.
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
        lift = round(p_ab / (p_a * p_b), 3) if p_a and p_b else 0.0
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
    """
    rows = []
    for c in companies:
        reviewed = len(c.present) + len(c.absent)
        score = round(len(c.present) / reviewed, 3) if reviewed else 0.0
        rows.append({
            "company": c.company,
            "host": c.host,
            "target": c.target,
            "presentCount": len(c.present),
            "reviewedCount": reviewed,
            "notReviewedCount": len(c.not_reviewed),
            "score": score,
            "presentSignals": sorted(c.present),
        })
    rows.sort(key=lambda r: (-r["score"], -r["presentCount"], r["company"]))
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
        lines.append(f"| {row['company']} | {row['score']:.0%} "
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
    return "\n".join(lines)


def write_patterns(report: Dict[str, Any], output_dir: str,
                    filename: str = "patterns.json") -> str:
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    path = out / filename
    path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    return str(path)
