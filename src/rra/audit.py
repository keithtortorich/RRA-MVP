"""RRA MVP audit: public scan -> evidence -> ranked opportunities -> artifacts."""
from __future__ import annotations
import hashlib, json, os
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Dict, Optional
from rra.runner import run_workers_parallel
from rra.scan import SCAN_WORKERS
from rra.scoring import extract_signals_from_markdown, score_evidence
from rra.fallback_scan import scan_public_url

DEFAULT_OUTPUT_DIR="reports/audits"
_SIGNAL_TO_CATEGORY={"no_click_to_call":"lead_capture","missed_call_rate_high":"lead_capture","no_after_hours_capture":"lead_capture","no_sms_textback":"lead_capture","no_cta_above_fold":"conversion_friction","form_too_long":"conversion_friction","no_online_booking":"conversion_friction","mobile_booking_broken":"conversion_friction","slow_form_response":"follow_up","slow_quote_followup":"follow_up","no_review_responses":"reputation_trust","low_review_count":"reputation_trust","negative_reviews_unanswered":"reputation_trust","no_review_request_flow":"reputation_trust","low_local_pack_presence":"local_visibility","no_gmb_optimization":"local_visibility","poor_ai_visibility":"ai_search_visibility","no_schema_markup":"technical_seo","weak_service_pages":"conversion_friction","no_maintenance_conversion":"conversion_friction","no_referral_system":"follow_up"}

def _ev(business_id, source, sig, confidence):
    return {"id":f"EVD-{source}-{sig}","business_id":business_id,"category":_SIGNAL_TO_CATEGORY.get(sig,"unknown"),"observation":f"{source} detected {sig}","signal":sig,"worker_source":source,"confidence":confidence,"observed_at":datetime.now(timezone.utc).isoformat().replace("+00:00","Z")}

def audit(client_name:str,url:str,output_dir:Optional[str]=None,client_metrics:Optional[Dict[str,float]]=None)->Dict[str,str]:
    if not str(client_name).strip(): raise ValueError("client_name is required")
    output_dir=output_dir or DEFAULT_OUTPUT_DIR; os.makedirs(output_dir,exist_ok=True)
    worker_results={}; business_id=_business_id(client_name,url); evidence=[]
    for worker,result in worker_results.items():
        if result.status!="ok": continue
        evidence += [_ev(business_id,worker,sig,.85) for sig in extract_signals_from_markdown(result.stdout)]
    if not evidence:
        try:
            evidence += [_ev(business_id,"fallback",sig,.70) for sig in extract_signals_from_markdown(scan_public_url(url))]
        except Exception as exc:
            print(f"[audit] fallback scan failed — {exc}")
    scoring_result=score_evidence(business_id,evidence,client_metrics or {})
    slug=_slugify(client_name); today=date.today().isoformat(); report_path=Path(output_dir)/f"{slug}-audit-{today}.md"; opportunities_path=Path(output_dir)/f"{slug}-opportunities-{today}.json"
    report_path.write_text(_render_audit(client_name,url,business_id,worker_results,scoring_result,client_metrics or {}),encoding="utf-8")
    payload={"ctx":{"business_id":business_id,"name":client_name,"url":url},"client_metrics":client_metrics or {},"signals":scoring_result.signals_seen,"warnings":scoring_result.warnings,"opportunities":scoring_result.opportunities,"generated_at":datetime.now(timezone.utc).isoformat().replace("+00:00","Z")}
    opportunities_path.write_text(json.dumps(payload,indent=2),encoding="utf-8")
    return {"report_path":str(report_path),"opportunities_path":str(opportunities_path)}

def _render_audit(client_name,url,business_id,worker_results,scoring_result,client_metrics):
    lines=[f"# Revenue Recovery Audit — {client_name}",f"**URL:** {url}  ",f"**Business ID:** {business_id}  ",f"**Date:** {date.today().isoformat()}  ","**Status:** INTERNAL — do not send to client","","## Worker Scan Summary","| Worker | Status | Output (chars) |","|--------|--------|----------------|"]
    for worker,result in worker_results.items(): lines.append(f"| {worker} | {result.status} | {len(result.stdout)} |")
    lines += ["","## Signals Detected"] + ([f"- `{s}`" for s in scoring_result.signals_seen] or ["_No signals detected._"])
    lines += ["","## Ranked Opportunities"]
    if scoring_result.opportunities:
        lines += ["| # | Leak ID | Finding | $/mo | Conf | Effort | TTV | Score |","|---|---------|---------|------|------|--------|-----|-------|"]
        for i,o in enumerate(scoring_result.opportunities,1): lines.append(f"| {i} | {o.get('leak_id')} | {o.get('finding')} | ${int(o.get('estimated_monthly_opportunity',0)):,} | {o.get('confidence')} | {o.get('effort_label')} | {o.get('time_to_value_days')}d | {o.get('priority_score')} |")
    else: lines.append("_No opportunities could be sized from detected signals._")
    if scoring_result.warnings: lines += ["","## Warnings"]+[f"- {w}" for w in scoring_result.warnings]
    return "\n".join(lines)+"\n"

def _business_id(client_name:str,url:str)->str:
    key=f"{client_name}|{url}".lower().encode("utf-8"); return f"BUS-{hashlib.sha1(key).hexdigest()[:8].upper()}"

def _slugify(name:str)->str:
    safe="".join(c.lower() if c.isalnum() else "-" for c in name).strip("-")
    while "--" in safe: safe=safe.replace("--","-")
    return safe or "client"
