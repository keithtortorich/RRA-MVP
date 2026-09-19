"""
RRA v1 — HVAC Leak Library
Canonical registry of every revenue leak the HVAC vertical knows about.
"""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Any, Dict, List, Optional

LIBRARY_ID = "HVAC-LEAK-LIBRARY-V1"
LIBRARY_VERSION = "1.0.0"
VERTICAL = "hvac"

class LeakCategory(str, Enum):
    LEAD_CAPTURE="lead_capture"; CONVERSION_FRICTION="conversion_friction"; RESPONSE_SPEED="response_speed"; LOCAL_VISIBILITY="local_visibility"; AI_SEARCH_VISIBILITY="ai_search_visibility"; REPUTATION_TRUST="reputation_trust"; FOLLOW_UP="follow_up"; TECHNICAL_SEO="technical_seo"

class DetectionSignal(str, Enum):
    NO_CTA_ABOVE_FOLD="no_cta_above_fold"; NO_CLICK_TO_CALL="no_click_to_call"; FORM_TOO_LONG="form_too_long"; NO_ONLINE_BOOKING="no_online_booking"; MOBILE_BOOKING_BROKEN="mobile_booking_broken"; SLOW_FORM_RESPONSE="slow_form_response"; MISSED_CALL_RATE_HIGH="missed_call_rate_high"; NO_AFTER_HOURS_CAPTURE="no_after_hours_capture"; NO_SMS_TEXTBACK="no_sms_textback"; SLOW_QUOTE_FOLLOWUP="slow_quote_followup"; NO_REVIEW_RESPONSES="no_review_responses"; LOW_REVIEW_COUNT="low_review_count"; NEGATIVE_REVIEWS_UNANSWERED="negative_reviews_unanswered"; NO_REVIEW_REQUEST_FLOW="no_review_request_flow"; LOW_LOCAL_PACK_PRESENCE="low_local_pack_presence"; NO_GMB_OPTIMIZATION="no_gmb_optimization"; POOR_AI_VISIBILITY="poor_ai_visibility"; NO_SCHEMA_MARKUP="no_schema_markup"; WEAK_SERVICE_PAGES="weak_service_pages"; NO_MAINTENANCE_CONVERSION="no_maintenance_conversion"; NO_REFERRAL_SYSTEM="no_referral_system"

@dataclass(frozen=True)
class DiagnosticSignalSpec:
    signal: DetectionSignal
    weight: float
    description: str = ""

@dataclass(frozen=True)
class LeakDefinition:
    leak_id: str; name: str; category: LeakCategory; description: str; signals: List[DiagnosticSignalSpec]
    min_signals: int=1; benchmark_keys: List[str]=field(default_factory=list); default_effort: int=3; default_time_to_value_days: int=14; playbook_id: Optional[str]=None; playbook_module: Optional[str]=None; recommended_action: str=""; recommendation_notes: str=""; requires_operational_fix: bool=False
    def to_dict(self)->Dict[str,Any]:
        d=asdict(self); d["category"]=self.category.value; d["signals"]=[{"signal":s.signal.value,"weight":s.weight,"description":s.description} for s in self.signals]; return d

def S(signal,weight,description=""): return DiagnosticSignalSpec(signal,weight,description)

def L(i,name,cat,desc,signals,bench=None,effort=3,ttv=14,action="",op=False,playbook=None,module=None,notes=""):
    return LeakDefinition(i,name,cat,desc,signals,benchmark_keys=bench or [],default_effort=effort,default_time_to_value_days=ttv,recommended_action=action,requires_operational_fix=op,playbook_id=playbook,playbook_module=module,recommendation_notes=notes)

HVAC_LEAK_LIBRARY={
"HVAC-LEAK-001":L("HVAC-LEAK-001","Missed calls and slow lead response",LeakCategory.LEAD_CAPTURE,"Inbound calls go unanswered or are never followed up.",[S(DetectionSignal.MISSED_CALL_RATE_HIGH,.40),S(DetectionSignal.NO_AFTER_HOURS_CAPTURE,.30),S(DetectionSignal.NO_SMS_TEXTBACK,.30)],["monthly_inbound_calls","missed_call_rate","after_hours_call_share","call_to_book_rate","average_service_ticket","contribution_margin_per_job"],2,7,"Deploy missed-call text-back + AI receptionist / after-hours routing",True,"HVAC-MISSED-CALL-V1","rra.verticals.hvac.playbooks.missed_call","Operational fix required (§17.2)."),
"HVAC-LEAK-002":L("HVAC-LEAK-002","Booking friction on website and mobile",LeakCategory.CONVERSION_FRICTION,"Visitors face friction booking or requesting service.",[S(DetectionSignal.NO_CTA_ABOVE_FOLD,.30),S(DetectionSignal.NO_CLICK_TO_CALL,.25),S(DetectionSignal.FORM_TOO_LONG,.25),S(DetectionSignal.MOBILE_BOOKING_BROKEN,.30)],["monthly_inbound_calls","web_form_to_conversation_rate","average_service_ticket","contribution_margin_per_job"],2,10,"Simplify booking flow: above-fold CTA, short form, one-tap call"),
"HVAC-LEAK-003":L("HVAC-LEAK-003","Weak estimate / quote follow-up",LeakCategory.FOLLOW_UP,"Estimates sent but not systematically followed up.",[S(DetectionSignal.SLOW_QUOTE_FOLLOWUP,.60),S(DetectionSignal.NO_SMS_TEXTBACK,.20),S(DetectionSignal.SLOW_FORM_RESPONSE,.20)],["estimate_close_rate","average_replacement_ticket","contribution_margin_per_job"],3,14,"Install estimate follow-up sequence (email + SMS + call)"),
"HVAC-LEAK-004":L("HVAC-LEAK-004","Unworked leads and no systematic follow-up",LeakCategory.FOLLOW_UP,"Inbound leads never worked to conclusion.",[S(DetectionSignal.SLOW_FORM_RESPONSE,.50),S(DetectionSignal.NO_SMS_TEXTBACK,.30),S(DetectionSignal.SLOW_QUOTE_FOLLOWUP,.20)],["monthly_inbound_calls","web_form_to_conversation_rate","call_to_book_rate","average_service_ticket","contribution_margin_per_job"],3,14,"Deploy lead qualification + follow-up automation"),
"HVAC-LEAK-005":L("HVAC-LEAK-005","Weak local visibility and Google Business Profile",LeakCategory.LOCAL_VISIBILITY,"Under-represented in local pack for high-intent searches.",[S(DetectionSignal.LOW_LOCAL_PACK_PRESENCE,.50),S(DetectionSignal.NO_GMB_OPTIMIZATION,.50)],["monthly_inbound_calls","average_service_ticket","contribution_margin_per_job"],4,45,"Optimize GMB, service-area pages, local citations"),
"HVAC-LEAK-006":L("HVAC-LEAK-006","Poor AI-search visibility (GEO)",LeakCategory.AI_SEARCH_VISIBILITY,"Not surfaced in AI-generated answers.",[S(DetectionSignal.POOR_AI_VISIBILITY,.60),S(DetectionSignal.NO_SCHEMA_MARKUP,.40)],["average_service_ticket","contribution_margin_per_job"],4,60,"Add schema, structured content, and citation-ready assets"),
"HVAC-LEAK-007":L("HVAC-LEAK-007","Weak reputation and unanswered reviews",LeakCategory.REPUTATION_TRUST,"Low review count, unanswered negatives, no request flow.",[S(DetectionSignal.LOW_REVIEW_COUNT,.40),S(DetectionSignal.NO_REVIEW_RESPONSES,.30),S(DetectionSignal.NEGATIVE_REVIEWS_UNANSWERED,.20),S(DetectionSignal.NO_REVIEW_REQUEST_FLOW,.30)],["average_service_ticket","contribution_margin_per_job"],3,30,"Deploy review monitoring, responses, and post-job review requests",False,"HVAC-REPUTATION-V1","rra.verticals.hvac.playbooks.reputation"),
"HVAC-LEAK-008":L("HVAC-LEAK-008","Weak service pages",LeakCategory.CONVERSION_FRICTION,"Service pages are thin or lack clear CTAs.",[S(DetectionSignal.WEAK_SERVICE_PAGES,.60),S(DetectionSignal.NO_CTA_ABOVE_FOLD,.40)],["average_replacement_ticket","contribution_margin_per_job"],3,30,"Rewrite high-value service pages"),
"HVAC-LEAK-009":L("HVAC-LEAK-009","Weak maintenance-plan conversion",LeakCategory.CONVERSION_FRICTION,"Service visits not converted to maintenance plans.",[S(DetectionSignal.NO_MAINTENANCE_CONVERSION,.70),S(DetectionSignal.SLOW_QUOTE_FOLLOWUP,.30)],["average_service_ticket","contribution_margin_per_job"],3,45,"Install maintenance-agreement conversion sequence"),
"HVAC-LEAK-010":L("HVAC-LEAK-010","No systematic referral system",LeakCategory.FOLLOW_UP,"Customers not systematically asked for referrals.",[S(DetectionSignal.NO_REFERRAL_SYSTEM,.70),S(DetectionSignal.NO_REVIEW_REQUEST_FLOW,.30)],["average_service_ticket","contribution_margin_per_job"],2,30,"Install referral + review request sequence")}

def list_leaks(): return list(HVAC_LEAK_LIBRARY.values())
def get_leak(leak_id):
    if leak_id not in HVAC_LEAK_LIBRARY: raise KeyError(f"No HVAC leak defined for '{leak_id}'")
    return HVAC_LEAK_LIBRARY[leak_id]
def leaks_by_category(category): return [l for l in HVAC_LEAK_LIBRARY.values() if l.category==category]
def leaks_requiring_operational_fix(): return [l for l in HVAC_LEAK_LIBRARY.values() if l.requires_operational_fix]

@dataclass
class LeakCandidate:
    leak_id:str; name:str; category:str; matched_signals:List[str]; confidence:float; requires_operational_fix:bool; playbook_id:Optional[str]; default_effort:int; default_time_to_value_days:int; benchmark_keys:List[str]; recommended_action:str

def match_signals(detected_signals:List[str])->List[LeakCandidate]:
    detected={str(s) for s in detected_signals}; candidates=[]
    for leak in HVAC_LEAK_LIBRARY.values():
        matched=[]; matched_weight=0.; total_weight=sum(sig.weight for sig in leak.signals) or 1.
        for sig in leak.signals:
            if sig.signal.value in detected: matched.append(sig.signal.value); matched_weight+=sig.weight
        if len(matched)>=leak.min_signals:
            candidates.append(LeakCandidate(leak.leak_id,leak.name,leak.category.value,matched,round(matched_weight/total_weight,3),leak.requires_operational_fix,leak.playbook_id,leak.default_effort,leak.default_time_to_value_days,list(leak.benchmark_keys),leak.recommended_action))
    return sorted(candidates,key=lambda c:c.confidence,reverse=True)
