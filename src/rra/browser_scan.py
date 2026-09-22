"""Observation-only browser agent for external leak verification.

Renders a prospect's PUBLIC pages in a headless browser and records what it
can see. It is structurally incapable of contacting the business: it never
submits a form, never completes a booking, never dials, never texts. Those
checks stay with a human operator — both because the guardrails in the Sizzle
tool require it, and because "I called at 8:43pm and got voicemail" is only
defensible on a sales call if a person actually did.

Everything this produces is a SIGNAL or a PLANNED draft test. It never emits a
determinate result (VERIFIED_FAILURE / VERIFIED_PASS); an operator confirms
each observation before it can carry Minimum Truth Pass weight.

Playwright is an optional extra: `pip install -e ".[browser]"`.
"""
from __future__ import annotations

import json
import re
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
from urllib import robotparser
from urllib.parse import urljoin, urlparse

from rra.fallback_scan import _fetch_once, _resolve_safe_ip

USER_AGENT = "RRA-MVP/1.0 public-audit (observation-only; contact via the site owner)"
MAX_PAGES = 12
REQUEST_DELAY_SECONDS = 1.0
MOBILE_VIEWPORT = {"width": 375, "height": 812}
SLOW_LOAD_MS = 4000
THIN_PAGE_WORDS = 250

# The agent may look. It may not talk. Enforced at the call sites that would
# otherwise reach the business, and asserted in the test suite.
CONTACT_ACTIONS_FORBIDDEN = ("submit_form", "complete_booking", "place_call", "send_sms")

CHAT_WIDGET_MARKERS = (
    "intercom", "drift.com", "tawk.to", "livechatinc", "tidio", "podium.com",
    "js.hs-scripts.com", "crisp.chat", "zendesk", "olark", "birdeye",
)
BOOKING_MARKERS = (
    "housecallpro", "servicetitan", "getjobber", "jobber.com", "calendly",
    "schedulericons", "acuityscheduling", "setmore", "servicefusion",
)
# Path fragments that name an actual booking destination (used for booking detection).
BOOKING_PATH_WORDS = ("book", "schedule", "appointment")
# Hosts that are never a booking destination, however their name reads.
SOCIAL_HOSTS = ("facebook.com", "instagram.com", "twitter.com", "x.com", "linkedin.com",
                "yelp.com", "nextdoor.com", "youtube.com", "tiktok.com", "pinterest.com")
# A scheduling subdomain is a booking destination; a host that merely contains a
# booking word is not.
BOOKING_SUBDOMAINS = frozenset({
    "book", "booking", "bookings", "schedule", "schedules", "scheduling",
    "scheduler", "appointment", "appointments",
})
# Third-party scheduler domains. A booking flow hosted at acme.bookingkoala.com
# carries no booking word in its path and no booking word in its leftmost label,
# so it is only recognisable by the provider's own domain.
BOOKING_HOST_SUFFIXES = (
    "housecallpro.com", "servicetitan.com", "getjobber.com", "jobber.com",
    "calendly.com", "acuityscheduling.com", "setmore.com", "servicefusion.com",
    "bookingkoala.com", "schedulicity.com", "booksy.com", "simplybook.me",
    "youcanbook.me", "appointlet.com", "squarespacescheduling.com",
    "mindbodyonline.com", "vagaro.com", "fieldedge.com", "scheduleengine.com",
)
# Broader set used only to recognise conversion CTAs worth link-checking.
BOOKING_LINK_WORDS = ("book", "schedule", "appointment", "request service")
FINANCING_WORDS = ("financing", "finance", "payment plan", "wells fargo", "synchrony",
                   "greensky", "monthly payments", "0% apr")
PRICING_WORDS = ("pricing", "price", "$", "flat rate", "estimate cost", "how much")
CTA_WORDS = ("call", "book", "schedule", "get a quote", "request", "contact",
             "free estimate", "emergency")
EMERGENCY_WORDS = ("emergency", "24/7", "24-7", "after hours", "same day", "urgent")


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class PageFacts:
    """Raw, un-interpreted observations from one rendered page."""

    url: str
    final_url: str = ""
    title: str = ""
    load_ms: int = 0
    word_count: int = 0
    tel_links: List[str] = field(default_factory=list)
    sms_links: List[str] = field(default_factory=list)
    booking_links: List[str] = field(default_factory=list)
    service_area_links: List[str] = field(default_factory=list)
    conversion_links: List[Dict[str, Any]] = field(default_factory=list)
    forms: List[Dict[str, Any]] = field(default_factory=list)
    chat_widget: Optional[str] = None
    financing_mentioned: bool = False
    pricing_mentioned: bool = False
    tel_above_fold: bool = False
    cta_above_fold: List[str] = field(default_factory=list)
    emergency_path_clicks: Optional[int] = None
    jsonld_hours: List[str] = field(default_factory=list)
    visible_hours: List[str] = field(default_factory=list)
    public_claims: List[str] = field(default_factory=list)
    screenshot: Optional[str] = None
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {k: v for k, v in self.__dict__.items()}


# --------------------------------------------------------------------------
# Safety / politeness
# --------------------------------------------------------------------------

def check_url_safe(url: str, allow_private_hosts: bool = False) -> str:
    """Reject non-public targets before a browser ever opens them.

    Mirrors the SSRF posture of fallback_scan. This is a pre-flight check:
    the browser performs its own DNS resolution, so this catches an operator
    pointing the agent at an internal host, not a determined rebinding
    attacker. Navigation is additionally confined to the target host by
    _install_request_guard().
    """
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"} or not parsed.hostname:
        raise ValueError("url must be an absolute http(s) URL")
    if allow_private_hosts:
        return url
    port = parsed.port or (443 if parsed.scheme == "https" else 80)
    _resolve_safe_ip(parsed.hostname, port)  # raises on private/reserved space
    return url


def robots_checker(base_url: str, allow_private_hosts: bool = False):
    """Return a callable(url) -> bool honoring the site's robots.txt.

    A tool whose entire pitch is evidentiary honesty should not be sneaking
    past robots.txt. On any fetch problem we fail open (same as a missing
    robots.txt), which is the conventional reading.
    """
    parser = robotparser.RobotFileParser()
    robots_url = urljoin(base_url, "/robots.txt")
    try:
        check_url_safe(robots_url, allow_private_hosts)
        status, _headers, body = _fetch_once(robots_url, timeout=8.0)
        if status == 200:
            parser.parse(body.decode("utf-8", errors="replace").splitlines())
        else:
            return lambda _url: True
    except Exception:
        return lambda _url: True

    def allowed(url: str) -> bool:
        try:
            return parser.can_fetch(USER_AGENT, url)
        except Exception:
            return True

    return allowed


def same_site(candidate: str, base: str) -> bool:
    try:
        c, b = urlparse(candidate).hostname, urlparse(base).hostname
    except ValueError:
        return False
    if not c or not b:
        return False
    c, b = c.lower().lstrip("www."), b.lower().lstrip("www.")
    return c == b


# --------------------------------------------------------------------------
# Interpretation (pure — unit tested without a browser)
# --------------------------------------------------------------------------

def _digits(value: str) -> str:
    return re.sub(r"\D", "", value or "")


def is_booking_link(href: str) -> bool:
    """True when a URL names an actual booking destination.

    Matches on the host and the path, not the whole URL. "facebook.com" contains
    "book", so testing the raw href counted every prospect's Facebook link as an
    online booking path — which wrongly cleared the NO_ONLINE_BOOKING signal on
    two of the first four real prospects scanned.

    The fragment counts as part of the destination: plenty of sites open booking
    through an in-page anchor or a hash route (#book, #/schedule).
    """
    try:
        parsed = urlparse(href or "")
    except ValueError:
        return False
    host = (parsed.hostname or "").lower()
    if any(host == s or host.endswith("." + s) for s in SOCIAL_HOSTS):
        return False
    if any(host == s or host.endswith("." + s) for s in BOOKING_HOST_SUFFIXES):
        return True
    target = f"{parsed.path} {parsed.query} {parsed.fragment}".lower()
    if any(w in target for w in BOOKING_PATH_WORDS):
        return True
    return host.split(".")[0] in BOOKING_SUBDOMAINS


def classify_signals(pages: List[PageFacts]) -> List[Dict[str, Any]]:
    """Turn raw page facts into investigation signals.

    Signal semantics match the Sizzle tool: the signal *type* names a concern,
    so status PRESENT means "we observed this concern" (e.g. NO_ONLINE_BOOKING
    PRESENT == no booking path was found). ABSENT means the concern does not
    apply because we found the thing.

    Anything that genuinely needs Google Business Profile or search-rank data
    is left NOT_REVIEWED rather than guessed — unknown is not the same as
    not-applicable.
    """
    ok = [p for p in pages if not p.error]
    if not ok:
        return []
    home = ok[0]
    signals: List[Dict[str, Any]] = []

    def add(signal_type: str, present: bool, note: str, source: str = "") -> None:
        signals.append({
            "signalType": signal_type,
            "status": "PRESENT" if present else "ABSENT",
            "evidenceType": "AUTOMATED_SIGNAL",
            "requiresOperatorVerification": True,
            "sourceUrl": source or home.final_url or home.url,
            "notes": note,
            "observedAt": now_iso(),
        })

    chat = next((p.chat_widget for p in ok if p.chat_widget), None)
    add("NO_CHAT_WIDGET", chat is None,
        "No chat widget detected in rendered page." if chat is None
        else f"Chat widget detected: {chat}.")

    has_booking = any(p.booking_links for p in ok)
    add("NO_ONLINE_BOOKING", not has_booking,
        "No booking or scheduling path found in rendered pages." if not has_booking
        else "Booking path found: " + ", ".join(ok[0].booking_links[:2]))

    has_financing = any(p.financing_mentioned for p in ok)
    add("NO_FINANCING", not has_financing,
        "No financing or payment-plan option visible." if not has_financing
        else "Financing mentioned on the public site.")

    slow = home.load_ms >= SLOW_LOAD_MS
    add("SLOW_PERFORMANCE", slow,
        f"Homepage rendered in {home.load_ms}ms (threshold {SLOW_LOAD_MS}ms).")

    has_sms = any(p.sms_links for p in ok) or any(
        "text us" in (p.title or "").lower() for p in ok)
    add("NO_SMS_OPTION", not has_sms,
        "No sms: link or visible text-us option." if not has_sms
        else "SMS contact option found.")

    has_pricing = any(p.pricing_mentioned for p in ok)
    add("NO_PRICING_GUIDANCE", not has_pricing,
        "No pricing guidance found on public pages." if not has_pricing
        else "Some pricing guidance present.")

    add("PHONE_NOT_PROMINENT", not home.tel_above_fold,
        "No tappable phone number above the fold at 375px."
        if not home.tel_above_fold else "Phone number present above the fold on mobile.")

    add("WEAK_CTA", not home.cta_above_fold,
        "No clear call to action above the fold at 375px."
        if not home.cta_above_fold
        else "Above-fold CTA(s): " + "; ".join(home.cta_above_fold[:3]))

    service_pages = [p for p in ok[1:] if p.word_count]
    thin = [p for p in service_pages if p.word_count < THIN_PAGE_WORDS]
    if service_pages:
        add("THIN_SERVICE_PAGES", bool(thin),
            f"{len(thin)} of {len(service_pages)} inner pages under {THIN_PAGE_WORDS} words."
            if thin else "Inner pages carry reasonable content depth.")

    # Needs review/search data this agent deliberately does not collect.
    for unknown in ("LOW_REVIEW_RESPONSE", "OLD_LATEST_REVIEW", "LOW_REVIEW_COUNT",
                    "WEAK_SEARCH_VISIBILITY"):
        signals.append({
            "signalType": unknown,
            "status": "NOT_REVIEWED",
            "evidenceType": "AUTOMATED_SIGNAL",
            "requiresOperatorVerification": True,
            "sourceUrl": "",
            "notes": "Requires Google Business Profile / search data — not collected by the "
                     "observation agent. Review manually.",
            "observedAt": now_iso(),
        })
    return signals


def build_draft_tests(pages: List[PageFacts], published_phone: str = "") -> List[Dict[str, Any]]:
    """Pre-fill PLANNED draft tests for the browser-observable checks.

    Never returns a determinate status. The agent finds the thing; the operator
    confirms it. That keeps every test that carries Truth Pass weight something
    a human can stand behind.
    """
    ok = [p for p in pages if not p.error]
    if not ok:
        return []
    home = ok[0]
    drafts: List[Dict[str, Any]] = []

    def draft(check_id: str, channel: str, observed: str, claim: str = "",
              source: str = "", reference: str = "") -> None:
        drafts.append({
            "checkId": check_id,
            "status": "PLANNED",
            "channel": channel,
            "publicClaim": claim,
            "sourceUrl": source or home.final_url or home.url,
            "expectedResult": "",
            "agentObservation": observed,
            "evidenceReference": reference or (home.screenshot or ""),
            "observedAt": now_iso(),
        })

    # EXT-008 — mobile click to call
    if home.tel_links:
        tel = home.tel_links[0]
        if published_phone and _digits(published_phone) not in _digits(tel):
            draft("EXT-008", "PHONE",
                  f"Click-to-call link resolves to {tel}, which does not match the "
                  f"published number {published_phone}. Confirm by tapping it on a phone.")
        else:
            draft("EXT-008", "PHONE",
                  f"Click-to-call link present ({tel}) and tappable at 375px. "
                  "Confirm it actually dials.")
    else:
        draft("EXT-008", "PHONE",
              "No tel: link found on the homepage at 375px — nothing to tap on mobile.")

    # EXT-010 — emergency contact friction
    if home.emergency_path_clicks is not None:
        draft("EXT-010", "WEBSITE",
              f"Emergency/after-hours contact path reachable in "
              f"{home.emergency_path_clicks} click(s) from the homepage on mobile.")
    else:
        draft("EXT-010", "WEBSITE",
              "No emergency or after-hours contact path found from the homepage on mobile.")

    # EXT-011 — conversion link integrity
    all_links = [c for p in ok for c in p.conversion_links]
    broken = [c for c in all_links if c.get("status") == "broken"]
    unverified = [c for c in all_links if c.get("status") == "unverified"]
    if all_links:
        caveat = (f" {len(unverified)} link(s) could not be checked and are NOT counted as "
                  "broken — verify those by hand.") if unverified else ""
        if broken:
            detail = "; ".join(f"{c['href']} ({c.get('detail', 'unreachable')})" for c in broken[:4])
            draft("EXT-011", "WEBSITE",
                  f"{len(broken)} of {len(all_links)} conversion links returned an error: "
                  f"{detail}.{caveat}")
        else:
            draft("EXT-011", "WEBSITE",
                  f"{len(all_links) - len(unverified)} conversion link(s) resolved successfully, "
                  f"none returned an error.{caveat}")

    # EXT-012 — hours consistency
    if home.jsonld_hours or home.visible_hours:
        draft("EXT-012", "DIRECTORY_COMPARISON",
              f"Structured-data hours: {home.jsonld_hours or 'none'}. "
              f"Visible hours: {home.visible_hours or 'none'}. "
              "Compare against Google Business Profile and directories.")

    # EXT-013 — service-area conversion path
    area_pages = [p for p in ok if p.url in home.service_area_links]
    if home.service_area_links:
        without_cta = [p.url for p in area_pages if not p.cta_above_fold and not p.tel_links]
        if without_cta:
            draft("EXT-013", "WEBSITE",
                  f"{len(without_cta)} service-area page(s) carry no conversion element: "
                  + ", ".join(without_cta[:3]),
                  source=without_cta[0])
        else:
            draft("EXT-013", "WEBSITE",
                  f"{len(home.service_area_links)} service-area page(s) found, each with a "
                  "conversion element.")

    # EXT-014 — form friction (counted only; the agent never submits)
    form_page = next((p for p in ok if p.forms), None)
    if form_page:
        form = max(form_page.forms, key=lambda f: f.get("fields", 0))
        draft("EXT-014", "WEB_FORM",
              f"Public form has {form.get('fields', 0)} field(s), "
              f"{form.get('required', 0)} required. Agent did not submit it — "
              "complete EXT-005/EXT-006 manually.",
              source=form_page.final_url or form_page.url)

    for claim in home.public_claims[:1]:
        for d in drafts:
            if not d["publicClaim"]:
                d["publicClaim"] = claim
    return drafts


def build_observations(pages: List[PageFacts], url: str, published_phone: str = "",
                       company: str = "") -> Dict[str, Any]:
    """Assemble the import payload consumed by the Sizzle tool.

    runId lets the tool import the same published file repeatedly without
    stacking duplicate drafts — it skips runs it has already applied.
    """
    return {
        "rraObservations": 1,
        "runId": uuid.uuid4().hex,
        "generatedAt": now_iso(),
        "target": url,
        "company": company,
        "host": (urlparse(url).hostname or "").lower().lstrip("www."),
        "agent": "observation-only browser agent",
        "classification": "AUTOMATED_SIGNAL",
        "requiresOperatorVerification": True,
        "contactChannelsUsed": [],  # always empty: this agent never contacts the business
        "pagesObserved": [p.final_url or p.url for p in pages if not p.error],
        "errors": [{"url": p.url, "error": p.error} for p in pages if p.error],
        "signals": classify_signals(pages),
        "draftTests": build_draft_tests(pages, published_phone),
    }


def load_targets(path: str) -> tuple:
    """Read the target list. Returns (runnable, skipped).

    A target without a url is skipped and reported — never guessed at. The
    Reed Heating entry is exactly this case: several unrelated Texas HVAC
    companies share the name, so pipeline.md warns against assuming a domain.
    """
    with open(path, "r", encoding="utf-8") as fh:
        data = json.load(fh)
    runnable, skipped = [], []
    for entry in data.get("targets", []):
        if not isinstance(entry, dict):
            continue
        url = entry.get("url")
        if not url or not str(url).strip():
            skipped.append({"company": entry.get("company", "(unnamed)"),
                            "reason": entry.get("note", "No URL on file.")})
            continue
        runnable.append({
            "company": entry.get("company", ""),
            "url": str(url).strip(),
            "phone": str(entry.get("phone") or "").strip(),
        })
    return runnable, skipped


def build_index(payloads: List[Dict[str, Any]], skipped: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Index the published observation files so the tool can find them by host."""
    return {
        "rraObservationsIndex": 1,
        "generatedAt": now_iso(),
        "runs": [{
            "runId": p.get("runId"),
            "company": p.get("company", ""),
            "host": p.get("host", ""),
            "target": p.get("target", ""),
            "generatedAt": p.get("generatedAt"),
            "file": p.get("file") or f"{slug_for(p.get('target', ''))}.json",
            "signalCount": len([s for s in p.get("signals", [])
                                if s.get("status") in ("PRESENT", "ABSENT")]),
            "draftCount": len(p.get("draftTests", [])),
        } for p in payloads],
        "skipped": skipped,
    }


def slug_for(url: str) -> str:
    """Filename stem for a target.

    Includes port and path, not just the hostname: two targets sharing a host
    would otherwise write to the same file, and the second would silently
    overwrite the first — publishing one prospect's findings under another
    prospect's name.
    """
    parsed = urlparse(url)
    parts = [(parsed.hostname or "target").lower()]
    if parsed.port:
        parts.append(str(parsed.port))
    path = (parsed.path or "").strip("/")
    if path:
        parts.append(path)
    return re.sub(r"[^a-z0-9]+", "-", "-".join(parts).lower()).strip("-") or "target"


def unique_slugs(urls: List[str]) -> Dict[str, str]:
    """Map each url to a filename stem that is unique within the batch."""
    used: Dict[str, int] = {}
    out: Dict[str, str] = {}
    for url in urls:
        base = slug_for(url)
        if base in used:
            used[base] += 1
            out[url] = f"{base}-{used[base]}"
        else:
            used[base] = 1
            out[url] = base
    return out


# --------------------------------------------------------------------------
# Browser collection (requires the optional `browser` extra)
# --------------------------------------------------------------------------

_PAGE_EXTRACTOR = """
() => {
  const abs = (h) => { try { return new URL(h, location.href).href; } catch (e) { return null; } };
  const anchors = Array.from(document.querySelectorAll('a[href]'));
  const foldHeight = window.innerHeight;
  const aboveFold = (el) => {
    const r = el.getBoundingClientRect();
    return r.top < foldHeight && r.bottom > 0 && r.width > 0 && r.height > 0;
  };
  const text = (document.body ? document.body.innerText : '') || '';
  const lower = text.toLowerCase();
  const html = document.documentElement.outerHTML.toLowerCase();

  const tel = anchors.filter(a => (a.getAttribute('href') || '').startsWith('tel:'))
                     .map(a => a.getAttribute('href'));
  const sms = anchors.filter(a => (a.getAttribute('href') || '').startsWith('sms:'))
                     .map(a => a.getAttribute('href'));

  const jsonldHours = [];
  Array.from(document.querySelectorAll('script[type="application/ld+json"]')).forEach(s => {
    try {
      const data = JSON.parse(s.textContent);
      const nodes = Array.isArray(data) ? data : [data];
      nodes.forEach(n => {
        const h = n && (n.openingHours || n.openingHoursSpecification);
        if (!h) return;
        (Array.isArray(h) ? h : [h]).forEach(v => jsonldHours.push(typeof v === 'string' ? v : JSON.stringify(v)));
      });
    } catch (e) { /* malformed JSON-LD is itself just noise, not a finding */ }
  });

  const hourLines = text.split('\\n')
    .map(l => l.trim())
    .filter(l => /(mon|tue|wed|thu|fri|sat|sun)/i.test(l) && /\\d/.test(l))
    .slice(0, 8);

  const claimLines = text.split('\\n').map(l => l.trim()).filter(l =>
    l.length > 8 && l.length < 140 &&
    /(24\\/7|24-7|24 hours|emergency|same.day|always open|any ?time)/i.test(l)).slice(0, 5);

  const forms = Array.from(document.querySelectorAll('form')).map(f => {
    const fields = Array.from(f.querySelectorAll('input, select, textarea'))
      .filter(i => !['hidden', 'submit', 'button'].includes((i.getAttribute('type') || '').toLowerCase()));
    return {
      fields: fields.length,
      required: fields.filter(i => i.hasAttribute('required')).length,
      action: f.getAttribute('action') || ''
    };
  });

  const ctaAboveFold = anchors.concat(Array.from(document.querySelectorAll('button')))
    .filter(aboveFold)
    .map(el => (el.innerText || '').trim())
    .filter(t => t && t.length < 60)
    .slice(0, 12);

  return {
    finalUrl: location.href,
    title: document.title || '',
    wordCount: text.split(/\\s+/).filter(Boolean).length,
    telLinks: tel,
    smsLinks: sms,
    telAboveFold: anchors.some(a => (a.getAttribute('href') || '').startsWith('tel:') && aboveFold(a)),
    ctaAboveFold: ctaAboveFold,
    links: anchors.map(a => ({ href: abs(a.getAttribute('href')), text: (a.innerText || '').trim().slice(0, 80) }))
                  .filter(l => l.href),
    forms: forms,
    jsonldHours: jsonldHours,
    visibleHours: hourLines,
    publicClaims: claimLines,
    bodyLower: lower.slice(0, 200000),
    htmlLower: html.slice(0, 400000)
  };
}
"""


def _extract_facts(raw: Dict[str, Any], url: str, load_ms: int) -> PageFacts:
    body = raw.get("bodyLower", "")
    html = raw.get("htmlLower", "")
    links = raw.get("links", [])
    facts = PageFacts(
        url=url,
        final_url=raw.get("finalUrl", url),
        title=raw.get("title", ""),
        load_ms=load_ms,
        word_count=raw.get("wordCount", 0),
        tel_links=raw.get("telLinks", []),
        sms_links=raw.get("smsLinks", []),
        forms=raw.get("forms", []),
        jsonld_hours=raw.get("jsonldHours", []),
        visible_hours=raw.get("visibleHours", []),
        public_claims=raw.get("publicClaims", []),
        tel_above_fold=bool(raw.get("telAboveFold")),
    )
    facts.cta_above_fold = [t for t in raw.get("ctaAboveFold", [])
                            if any(w in t.lower() for w in CTA_WORDS)]
    facts.chat_widget = next((m for m in CHAT_WIDGET_MARKERS if m in html), None)
    facts.financing_mentioned = any(w in body for w in FINANCING_WORDS)
    facts.pricing_mentioned = any(w in body for w in PRICING_WORDS)
    # Booking requires a real booking destination — a known scheduler widget, or a URL
    # path that names one. Link *text* alone is too weak: "Request Service" is usually a
    # contact CTA, and treating it as a booking path would wrongly clear the signal.
    facts.booking_links = [f"widget:{m}" for m in BOOKING_MARKERS if m in html]
    facts.booking_links += [l["href"] for l in links if is_booking_link(l["href"])]
    facts.service_area_links = [
        l["href"] for l in links
        if re.search(r"/(service-area|areas?-we-serve|locations?|cities)/", (l["href"] or "").lower())
    ]
    return facts


def _check_conversion_links(facts: PageFacts, links: List[Dict[str, Any]],
                            allow_private_hosts: bool, limit: int = 8) -> None:
    """GET-check conversion destinations. Never POSTs, never submits.

    Three outcomes, deliberately: ok, broken, and unverified. Only a definite
    error response counts as broken. A link we merely could not reach — TLS
    quirk, timeout, bot-block — is "unverified", because telling an owner
    their links are dead when we never actually checked is the exact kind of
    fabricated certainty this tool exists to avoid.
    """
    seen = set()
    for link in links:
        href = link.get("href") or ""
        text = (link.get("text") or "").lower()
        is_conversion = (
            href.startswith("tel:") or href.startswith("sms:") or href.startswith("mailto:")
            or any(w in href.lower() for w in BOOKING_LINK_WORDS + ("contact",))
            or any(w in text for w in CTA_WORDS)
        )
        if not is_conversion or href in seen:
            continue
        seen.add(href)
        if len(facts.conversion_links) >= limit:
            return
        if href.startswith(("tel:", "sms:", "mailto:")):
            target = href.split(":", 1)[1]
            valid = bool(_digits(target)) if href.startswith(("tel:", "sms:")) else "@" in target
            facts.conversion_links.append({
                "href": href, "text": link.get("text", ""),
                "status": "ok" if valid else "broken",
                "detail": "" if valid else "malformed link target",
            })
            continue
        try:
            check_url_safe(href, allow_private_hosts)
            status, _h, _b = _fetch_once(href, timeout=10.0)
            # Auth and method gates are not dead links — a 403 on a contact page
            # usually means a bot filter, not a broken conversion path.
            if status < 400 or status in (401, 403, 405):
                result = {"status": "ok", "detail": ""}
            else:
                result = {"status": "broken", "detail": f"HTTP {status}"}
        except Exception as exc:
            result = {"status": "unverified", "detail": str(exc)[:120]}
        facts.conversion_links.append(
            {"href": href, "text": link.get("text", ""), **result})
        time.sleep(REQUEST_DELAY_SECONDS)


def observe_site(url: str, published_phone: str = "", max_pages: int = MAX_PAGES,
                 screenshot_dir: Optional[str] = None,
                 allow_private_hosts: bool = False,
                 executable_path: Optional[str] = None,
                 company: str = "") -> Dict[str, Any]:
    """Render the public site and return signals + PLANNED draft tests.

    Contacts nobody. Submits nothing. Books nothing.
    """
    try:
        from playwright.sync_api import sync_playwright  # type: ignore[import-not-found]
    except ImportError as exc:  # pragma: no cover - exercised only without the extra
        raise RuntimeError(
            "The observation agent needs the browser extra: pip install -e \".[browser]\""
        ) from exc

    check_url_safe(url, allow_private_hosts)
    allowed = robots_checker(url, allow_private_hosts)
    shots = Path(screenshot_dir) if screenshot_dir else None
    if shots:
        shots.mkdir(parents=True, exist_ok=True)

    pages: List[PageFacts] = []
    queue: List[str] = [url]
    visited: set = set()

    with sync_playwright() as pw:
        launch_kwargs: Dict[str, Any] = {}
        if executable_path:
            launch_kwargs["executable_path"] = executable_path
        browser = pw.chromium.launch(**launch_kwargs)
        context = browser.new_context(viewport=MOBILE_VIEWPORT, user_agent=USER_AGENT,
                                      is_mobile=True, has_touch=True)
        try:
            while queue and len(visited) < max_pages:
                target = queue.pop(0)
                if target in visited:
                    continue
                visited.add(target)
                if not allowed(target):
                    pages.append(PageFacts(url=target, error="disallowed by robots.txt"))
                    continue

                page = context.new_page()
                try:
                    started = time.time()
                    page.goto(target, wait_until="domcontentloaded", timeout=30000)
                    page.wait_for_timeout(600)  # let client-rendered widgets mount
                    load_ms = int((time.time() - started) * 1000)
                    raw = page.evaluate(_PAGE_EXTRACTOR)
                    facts = _extract_facts(raw, target, load_ms)

                    if shots:
                        name = re.sub(r"[^a-z0-9]+", "-", urlparse(target).path.lower()).strip("-") or "home"
                        shot = shots / f"{name}.png"
                        page.screenshot(path=str(shot), full_page=False)
                        facts.screenshot = str(shot)

                    if len(pages) == 0:  # homepage only: the expensive checks
                        _check_conversion_links(facts, raw.get("links", []), allow_private_hosts)
                        facts.emergency_path_clicks = _emergency_clicks(raw.get("links", []),
                                                                        raw.get("bodyLower", ""))
                        for link in facts.service_area_links[:3]:
                            if same_site(link, url):
                                queue.append(link)
                        for link in (l["href"] for l in raw.get("links", [])):
                            if len(queue) >= max_pages:
                                break
                            if link and same_site(link, url) and re.search(
                                    r"/(contact|service|ac|heating|repair)", link.lower()):
                                queue.append(link)
                    pages.append(facts)
                except Exception as exc:
                    pages.append(PageFacts(url=target, error=str(exc)[:200]))
                finally:
                    page.close()
                    time.sleep(REQUEST_DELAY_SECONDS)
        finally:
            context.close()
            browser.close()

    return build_observations(pages, url, published_phone, company)


def _emergency_clicks(links: List[Dict[str, Any]], body_lower: str) -> Optional[int]:
    """0 = emergency contact is on the homepage; 1 = one link away; None = not found."""
    if any(w in body_lower for w in EMERGENCY_WORDS):
        for link in links:
            if link.get("href", "").startswith("tel:"):
                return 0
    for link in links:
        haystack = f"{link.get('href', '')} {link.get('text', '')}".lower()
        if any(w in haystack for w in EMERGENCY_WORDS):
            return 1
    return None


def format_summary(payload: Dict[str, Any]) -> str:
    """Render the payload as Markdown for a CI job summary or a terminal read.

    Deliberately repeats the scope caveat: nothing here is a verified finding,
    and the checks that carry Truth Pass weight are not in this file.
    """
    signals = payload.get("signals", [])
    drafts = payload.get("draftTests", [])
    errors = payload.get("errors", [])
    observed = [s for s in signals if s.get("status") in ("PRESENT", "ABSENT")]
    unreviewed = [s for s in signals if s.get("status") == "NOT_REVIEWED"]

    lines: List[str] = []
    lines.append(f"## Observation run — {payload.get('target', 'unknown target')}")
    lines.append("")
    lines.append(f"- Pages rendered: **{len(payload.get('pagesObserved', []))}**")
    lines.append(f"- Signals recorded: **{len(observed)}** "
                 f"({len(unreviewed)} left NOT_REVIEWED)")
    lines.append(f"- Draft tests: **{len(drafts)}** — all PLANNED, none verified")
    lines.append(f"- Contact channels used: **{len(payload.get('contactChannelsUsed', [])) or 'none'}**")
    lines.append("")
    lines.append("> The agent never called, texted, submitted a form, or booked. "
                 "EXT-001..007 and EXT-015 remain manual, and nothing below counts "
                 "toward a Minimum Truth Pass until you confirm it yourself.")
    lines.append("")

    if drafts:
        lines.append("### Draft tests (confirm each before it counts)")
        lines.append("")
        lines.append("| Check | Status | What the agent saw |")
        lines.append("|---|---|---|")
        for d in drafts:
            note = str(d.get("agentObservation", "")).replace("|", "\\|")
            lines.append(f"| `{d.get('checkId', '?')}` | {d.get('status', '?')} | {note} |")
        lines.append("")

    if observed:
        lines.append("### Signals")
        lines.append("")
        lines.append("| Signal | Status | Note |")
        lines.append("|---|---|---|")
        for s in observed:
            note = str(s.get("notes", "")).replace("|", "\\|")
            lines.append(f"| `{s.get('signalType')}` | {s.get('status')} | {note} |")
        lines.append("")

    if unreviewed:
        lines.append("### Not reviewed")
        lines.append("")
        lines.append("Needs Google Business Profile or search data the agent does not "
                     "collect — check these by hand: "
                     + ", ".join(f"`{s.get('signalType')}`" for s in unreviewed))
        lines.append("")

    if errors:
        lines.append("### Pages that could not be read")
        lines.append("")
        for e in errors:
            lines.append(f"- `{e.get('url')}` — {e.get('error')}")
        lines.append("")

    lines.append("Import the JSON in the Sizzle tool: prospect → Evidence → "
                 "**Import agent observations**.")
    return "\n".join(lines)


def write_observations(payload: Dict[str, Any], output_dir: str, url: str,
                       stem: Optional[str] = None) -> str:
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    path = out / f"{stem or slug_for(url)}.json"
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return str(path)
