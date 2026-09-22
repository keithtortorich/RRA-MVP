"""Deterministic HVAC evidence scoring for the Leak Detector MVP."""
from __future__ import annotations
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional
from leak_detector.core.effort import apply_effort_to_opportunity
from leak_detector.core.scoring import calculate_scores_for_opportunities
from leak_detector.verticals.hvac.benchmarks import Label, resolve_metric
from leak_detector.verticals.hvac.leak_library import DetectionSignal, LeakCategory, get_leak, match_signals

MIN_EVIDENCE_CONFIDENCE = 0.50
CATEGORY_TO_DEFAULT_SIGNAL = {
    LeakCategory.LEAD_CAPTURE.value: DetectionSignal.MISSED_CALL_RATE_HIGH.value,
    LeakCategory.RESPONSE_SPEED.value: DetectionSignal.MISSED_CALL_RATE_HIGH.value,
    LeakCategory.CONVERSION_FRICTION.value: DetectionSignal.NO_CTA_ABOVE_FOLD.value,
    LeakCategory.FOLLOW_UP.value: DetectionSignal.SLOW_FORM_RESPONSE.value,
    LeakCategory.LOCAL_VISIBILITY.value: DetectionSignal.LOW_LOCAL_PACK_PRESENCE.value,
    LeakCategory.AI_SEARCH_VISIBILITY.value: DetectionSignal.POOR_AI_VISIBILITY.value,
    LeakCategory.REPUTATION_TRUST.value: DetectionSignal.NO_REVIEW_RESPONSES.value,
    LeakCategory.TECHNICAL_SEO.value: DetectionSignal.NO_SCHEMA_MARKUP.value,
}
OBSERVATION_HINTS = [
    ("missed call", DetectionSignal.MISSED_CALL_RATE_HIGH.value),
    ("click-to-call", DetectionSignal.NO_CLICK_TO_CALL.value),
    ("after hours", DetectionSignal.NO_AFTER_HOURS_CAPTURE.value),
    ("text-back", DetectionSignal.NO_SMS_TEXTBACK.value),
    ("cta above", DetectionSignal.NO_CTA_ABOVE_FOLD.value),
    ("form too long", DetectionSignal.FORM_TOO_LONG.value),
    ("online booking", DetectionSignal.NO_ONLINE_BOOKING.value),
    ("mobile booking", DetectionSignal.MOBILE_BOOKING_BROKEN.value),
    ("slow form", DetectionSignal.SLOW_FORM_RESPONSE.value),
    ("quote follow", DetectionSignal.SLOW_QUOTE_FOLLOWUP.value),
    ("review response", DetectionSignal.NO_REVIEW_RESPONSES.value),
    ("low review", DetectionSignal.LOW_REVIEW_COUNT.value),
    ("local pack", DetectionSignal.LOW_LOCAL_PACK_PRESENCE.value),
    ("ai visibility", DetectionSignal.POOR_AI_VISIBILITY.value),
    ("schema", DetectionSignal.NO_SCHEMA_MARKUP.value),
    ("service pages", DetectionSignal.WEAK_SERVICE_PAGES.value),
    ("maintenance", DetectionSignal.NO_MAINTENANCE_CONVERSION.value),
    ("referral", DetectionSignal.NO_REFERRAL_SYSTEM.value),
]

def _dedupe(xs):
    return list(dict.fromkeys(xs))

def _extract_signals_from_evidence(ev: Dict[str, Any]) -> List[str]:
    signals=[]
    if ev.get("signal"): signals.append(str(ev["signal"]))
    if isinstance(ev.get("signals"),(list,tuple)): signals += [str(x) for x in ev["signals"]]
    if signals: return _dedupe(signals)
    obs=str(ev.get("observation","")).lower()
    signals += [sig for key,sig in OBSERVATION_HINTS if key in obs]
    if not signals and ev.get("category") in CATEGORY_TO_DEFAULT_SIGNAL:
        signals.append(CATEGORY_TO_DEFAULT_SIGNAL[ev["category"]])
    return _dedupe(signals)

def extract_signals_from_markdown(markdown: str) -> List[str]:
    if not markdown: return []
    lower=markdown.lower(); signals=[sig for key,sig in OBSERVATION_HINTS if key in lower]
    for s in DetectionSignal:
        if s.value in lower or s.value.replace("_"," ") in lower: signals.append(s.value)
    return _dedupe(signals)

def _metric(client: Dict[str,float], key: str):
    return resolve_metric(client.get(key), key)

def _sizing(leak_id: str, client: Dict[str,float]):
    calls=_metric(client,"monthly_inbound_calls"); service=_metric(client,"average_service_ticket"); repl=_metric(client,"average_replacement_ticket"); margin=_metric(client,"contribution_margin_per_job")
    roi={"monthly_inbound_calls":calls,"average_service_ticket":service,"average_replacement_ticket":repl,"contribution_margin_per_job":margin}
    if leak_id=="HVAC-LEAK-001":
        missed=_metric(client,"missed_call_rate"); roi["missed_call_rate"]=missed; monthly=calls["value"]*missed["value"]*.5*service["value"]*margin["value"]
    elif leak_id in {"HVAC-LEAK-002","HVAC-LEAK-004"}:
        conv=_metric(client,"web_form_to_conversation_rate"); roi["web_form_to_conversation_rate"]=conv; monthly=calls["value"]*.30*(1-conv["value"])*.5*service["value"]*margin["value"]
    elif leak_id=="HVAC-LEAK-003": monthly=10*.08*repl["value"]*margin["value"]
    elif leak_id=="HVAC-LEAK-005": monthly=calls["value"]*.10*.5*service["value"]*margin["value"]
    elif leak_id=="HVAC-LEAK-006": monthly=3*service["value"]*margin["value"]
    elif leak_id=="HVAC-LEAK-007": monthly=2*service["value"]*margin["value"]
    elif leak_id=="HVAC-LEAK-008": monthly=repl["value"]*margin["value"]
    elif leak_id=="HVAC-LEAK-009": monthly=4*service["value"]*margin["value"]
    elif leak_id=="HVAC-LEAK-010": monthly=3*service["value"]*margin["value"]
    else: return 0, roi
    return round(float(monthly),2), roi

def _confidence(roi):
    mult={Label.KNOWN.value:1.0,Label.ESTIMATED.value:.9,Label.ASSUMED.value:.8,Label.UNKNOWN.value:.7}
    vals=[mult.get(str(v.get("label")),.85) for v in roi.values() if isinstance(v,dict) and "label" in v]
    return min(vals) if vals else 1.0

@dataclass
class ScoringResult:
    business_id: str
    opportunities: List[Dict[str,Any]]
    warnings: List[str]=field(default_factory=list)
    signals_seen: List[str]=field(default_factory=list)
    def to_dict(self): return asdict(self)

def score_evidence(business_id: str, evidence: List[Dict[str,Any]], client_metrics: Optional[Dict[str,float]]=None) -> ScoringResult:
    if not business_id: raise ValueError("business_id is required")
    client_metrics=client_metrics or {}; warnings=[]; signal_to_evidence: Dict[str, List[str]] = {}
    for ev in evidence or []:
        try: conf=float(ev.get("confidence",0) or 0)
        except (TypeError,ValueError):
            warnings.append(f"{ev.get('id','<unknown>')}: invalid confidence — dropped"); continue
        if conf < MIN_EVIDENCE_CONFIDENCE:
            warnings.append(f"{ev.get('id','<unknown>')}: confidence {conf:.2f} below {MIN_EVIDENCE_CONFIDENCE} — dropped"); continue
        for sig in _extract_signals_from_evidence(ev): signal_to_evidence.setdefault(sig,[]).append(ev.get("id",""))
    signals=sorted(signal_to_evidence)
    if not signals: return ScoringResult(business_id,[],warnings+["no signals extracted"],[])
    candidates=match_signals(signals)
    if not candidates: return ScoringResult(business_id,[],warnings+["no leak matched the signals"],signals)
    opps=[]
    for candidate in candidates:
        monthly,roi=_sizing(candidate.leak_id,client_metrics)
        if monthly<=0: continue
        leak=get_leak(candidate.leak_id); ev_ids=_dedupe([eid for s in candidate.matched_signals for eid in signal_to_evidence.get(s,[]) if eid])
        opp={"id":"","business_id":business_id,"evidence_ids":ev_ids,"leak_id":candidate.leak_id,"category":candidate.category,"finding":candidate.name,"estimated_monthly_opportunity":monthly,"confidence":round(max(0,min(1,candidate.confidence*_confidence(roi))),3),"effort":leak.default_effort,"time_to_value_days":leak.default_time_to_value_days,"requires_operational_fix":leak.requires_operational_fix,"playbook_id":leak.playbook_id,"roi_assumptions":roi,"recommendation":{"action":leak.recommended_action}}
        opps.append(apply_effort_to_opportunity(opp))
    ranked=calculate_scores_for_opportunities(opps)
    for i,o in enumerate(ranked,1): o["id"]=f"OPP-{i:04d}"
    return ScoringResult(business_id,ranked,warnings,signals)
