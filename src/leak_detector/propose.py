"""
Leak Detector MVP — Proposal Stage
Opportunities JSON → Good / Better / Best proposal.

Every proposal is:
  1. Guardrail-checked (raises ValueError if non-compliant)
  2. Client-facing-filtered via leak_detector.core.client_facing.client_facing_summary
  3. Wedge-first (Good tier == #1 opportunity, matched by leak_id)
  4. Rendered as two files: internal (operator) and external (client)
"""

from __future__ import annotations

import json
import os
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from leak_detector.core.client_facing import client_facing_summary
from leak_detector.core.guardrails import (
    build_decision_checklist, render_decision_checklist, validate_proposal,
)

DEFAULT_OUTPUT_DIR = "reports/proposals"


def _good_tier(top: Dict[str, Any]) -> Dict[str, Any]:
    finding = top.get("finding", "the top revenue leak")
    recommended = (top.get("recommendation") or {}).get("action", "Fix the #1 leak")
    category = str(top.get("category", "")).lower()
    leak_id = top.get("leak_id")
    includes = [f"Deep diagnosis of: {finding}"]
    if category in {"lead_capture", "response_speed"}:
        includes.append("AI receptionist / SMS catcher setup (immediate operational fix)")
    elif category == "paid_traffic":
        includes.append("Call tracking + paid-traffic leak fix")
    else:
        includes.append("Implementation of the #1 opportunity")
    includes.append("30-day measurement of recovered revenue")
    return {"name":"Good — Fix the Biggest Leak","focus":finding,"leak_id":leak_id,"focus_leak_id":leak_id,"description":"Single-fix entry designed to prove value fast.","recommended_action":recommended,"monthly_impact":int(round(top.get("estimated_monthly_opportunity",0))),"price":997,"monthly":0,"includes":includes}


def _better_tier(ranked: List[Dict[str, Any]]) -> Dict[str, Any]:
    total = sum(o.get("estimated_monthly_opportunity", 0) for o in ranked[:3])
    return {"name":"Better — Revenue Recovery Systems","focus":"Primary leak + next two highest opportunities","leak_id":ranked[0].get("leak_id") if ranked else None,"description":"Install and manage the top three fixes.","monthly_impact":int(round(total)),"price":5000,"monthly":2500,"includes":["Everything in Good","Implementation of top 3 opportunities","90-day roadmap and baseline tracking","Monthly optimization review"]}


def _best_tier(ranked: List[Dict[str, Any]]) -> Dict[str, Any]:
    total = sum(o.get("estimated_monthly_opportunity", 0) for o in ranked)
    return {"name":"Best — Full Revenue Recovery Management","focus":"Continuous recovery and continuous improvement","leak_id":ranked[0].get("leak_id") if ranked else None,"description":"Ongoing management of the full Revenue Recovery System.","monthly_impact":int(round(total)),"price":0,"monthly":7500,"includes":["Everything in Better","Monthly re-scan and priority refresh","Dedicated recovery management","Quarterly business review"]}


def build_proposal(ctx: Dict[str, Any], opportunities: List[Dict[str, Any]]) -> Dict[str, Any]:
    if not opportunities:
        raise ValueError("propose: no opportunities — nothing to propose")
    ranked = sorted(opportunities, key=lambda o: o.get("priority_score", 0), reverse=True)
    top = ranked[0]
    generated_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    client_summary = client_facing_summary(opportunities=ranked, client_name=ctx.get("name", "your business"))
    proposal = {
        "business_id":ctx.get("business_id"),"client_name":ctx.get("name","your business"),"generated_at":generated_at,"pricing_model":"fixed_fee","access_boundary":"public_only",
        "primary_recommendation":{"leak_id":top.get("leak_id"),"finding":top.get("finding"),"estimated_monthly_impact":int(round(top.get("estimated_monthly_opportunity",0))),"recommended_action":(top.get("recommendation") or {}).get("action"),"time_to_value_days":int(top.get("time_to_value_days",14))},
        "tiers":{"good":_good_tier(top),"better":_better_tier(ranked),"best":_best_tier(ranked)},"client_summary":client_summary,"internal_opportunities":ranked,
    }
    ok, violations = validate_proposal(proposal)
    if not ok:
        raise ValueError("Non-compliant proposal blocked by guardrails: " + ", ".join(violations))
    return proposal


def render_operator_view(proposal: Dict[str, Any]) -> str:
    lines=[f"# Proposal (Internal) — {proposal.get('client_name')}",f"_Generated: {proposal.get('generated_at')}_","",f"**Pricing model:** {proposal.get('pricing_model')}  ",f"**Access boundary:** {proposal.get('access_boundary')}",""]
    primary=proposal.get("primary_recommendation",{})
    lines += ["## Primary Recommendation",f"- **Leak:** {primary.get('finding')} (`{primary.get('leak_id')}`)",f"- **Monthly impact:** ${int(primary.get('estimated_monthly_impact',0)):,}",f"- **Action:** {primary.get('recommended_action')}",f"- **Time-to-value:** {primary.get('time_to_value_days')} days",""]
    lines.append("## Tiers")
    for label in ("good","better","best"):
        tier=proposal["tiers"][label]
        lines += [f"### {tier.get('name')}",f"- **Focus:** {tier.get('focus')}",f"- **Leak ID:** `{tier.get('leak_id')}`",f"- **Monthly impact:** ${int(tier.get('monthly_impact',0)):,}"]
        price_bits=[]
        if tier.get("price"): price_bits.append(f"${int(tier['price']):,} setup")
        if tier.get("monthly"): price_bits.append(f"${int(tier['monthly']):,}/mo")
        lines.append(f"- **Price:** {' + '.join(price_bits) or '—'}")
        for item in tier.get("includes",[]): lines.append(f"  - {item}")
        lines.append("")
    lines += ["## Ranked Opportunities (Internal)","| # | Leak ID | Finding | $/mo | Conf | Effort | TTV (d) | Score |","|---|---------|---------|------|------|--------|---------|-------|"]
    for i,opp in enumerate(proposal.get("internal_opportunities",[]),1):
        lines.append(f"| {i} | {opp.get('leak_id')} | {opp.get('finding')} | ${int(opp.get('estimated_monthly_opportunity',0)):,} | {opp.get('confidence')} | {opp.get('effort_label')} | {opp.get('time_to_value_days')} | {opp.get('priority_score')} |")
    lines += ["","## Commercial Decision Checklist","```",render_decision_checklist(build_decision_checklist(proposal)),"```"]
    return "\n".join(lines)


def render_client_view(proposal: Dict[str, Any]) -> str:
    summary=proposal.get("client_summary") or {}; tiers=proposal.get("tiers",{})
    lines=[f"# Revenue Recovery Proposal — {proposal.get('client_name')}",f"_Prepared {date.today().isoformat()}_","","## The Situation","",summary.get("headline",""),"","## What We Propose",""]
    for label in ("good","better","best"):
        tier=tiers.get(label,{})
        if not tier: continue
        lines += [f"### {tier.get('name')}",f"_{tier.get('description','')}_","",f"**Estimated monthly impact:** ${int(tier.get('monthly_impact',0)):,}"]
        price_bits=[]
        if tier.get("price"): price_bits.append(f"${int(tier['price']):,} setup")
        if tier.get("monthly"): price_bits.append(f"${int(tier['monthly']):,}/month")
        lines += [f"**Investment:** {' + '.join(price_bits) or '—'}","","Includes:"]
        for item in tier.get("includes",[]): lines.append(f"- {item}")
        lines.append("")
    lines += ["## Next Step","",summary.get("next_step","Reply with the option you'd like to start with.")]
    return "\n".join(lines)


def propose(client_name: str, opportunities_path: str, output_dir: Optional[str] = None) -> Dict[str, str]:
    output_dir=output_dir or DEFAULT_OUTPUT_DIR; os.makedirs(output_dir,exist_ok=True)
    with open(opportunities_path,"r",encoding="utf-8") as fh: payload=json.load(fh)
    ctx=payload.get("ctx") or {"business_id":"BUS-UNKNOWN","name":client_name}; ctx.setdefault("name",client_name)
    proposal=build_proposal(ctx,payload.get("opportunities") or [])
    slug=_slugify(client_name); today=date.today().isoformat(); operator_path=Path(output_dir)/f"{slug}-proposal-{today}.internal.md"; client_path=Path(output_dir)/f"{slug}-proposal-{today}.md"
    operator_path.write_text(render_operator_view(proposal),encoding="utf-8"); client_path.write_text(render_client_view(proposal),encoding="utf-8")
    print(f"[propose] internal → {operator_path}"); print(f"[propose] client   → {client_path}")
    return {"operator_path":str(operator_path),"client_path":str(client_path)}


def _slugify(name: str) -> str:
    return name.lower().replace(" ","-").replace("/","-") or "client"
