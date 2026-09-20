"""Tests for the observation-only browser agent.

These exercise the interpretation layer and the safety rails without launching
a browser, so CI stays fast and never touches a real business.
"""
from __future__ import annotations

import pytest

from rra import browser_scan as bs


def _home(**kwargs) -> bs.PageFacts:
    defaults = dict(
        url="https://example-hvac.com/",
        final_url="https://example-hvac.com/",
        title="Example HVAC",
        load_ms=900,
        word_count=800,
        tel_above_fold=True,
        tel_links=["tel:+18325551234"],
        cta_above_fold=["Call now"],
    )
    defaults.update(kwargs)
    return bs.PageFacts(**defaults)


# --------------------------------------------------------------------------
# The central guarantee: this agent never contacts the business.
# --------------------------------------------------------------------------

def test_payload_always_reports_no_contact_channels_used():
    payload = bs.build_observations([_home()], "https://example-hvac.com/")
    assert payload["contactChannelsUsed"] == []


def test_draft_tests_are_never_determinate():
    pages = [_home(forms=[{"fields": 9, "required": 7, "action": "/contact"}],
                   conversion_links=[{"href": "https://example-hvac.com/x",
                                      "status": "broken", "detail": "HTTP 404"}])]
    drafts = bs.build_draft_tests(pages)
    assert drafts
    for draft in drafts:
        assert draft["status"] == "PLANNED"
        assert draft["status"] not in ("VERIFIED_FAILURE", "VERIFIED_PASS")


def test_contact_channel_checks_are_never_auto_completed():
    """EXT-005/006/007/015 require contacting the business — the agent must not claim them."""
    pages = [_home(forms=[{"fields": 6, "required": 4, "action": "/contact"}],
                   booking_links=["https://example-hvac.com/book"])]
    ids = {d["checkId"] for d in bs.build_draft_tests(pages)}
    assert not ids & {"EXT-001", "EXT-002", "EXT-003", "EXT-004",
                      "EXT-005", "EXT-006", "EXT-007", "EXT-015"}


def test_form_draft_says_it_did_not_submit():
    pages = [_home(forms=[{"fields": 9, "required": 7, "action": "/contact"}])]
    form_draft = next(d for d in bs.build_draft_tests(pages) if d["checkId"] == "EXT-014")
    assert "did not submit" in form_draft["agentObservation"]


# --------------------------------------------------------------------------
# Signal classification
# --------------------------------------------------------------------------

def test_missing_booking_and_chat_are_flagged_present():
    signals = {s["signalType"]: s for s in bs.classify_signals([_home()])}
    assert signals["NO_ONLINE_BOOKING"]["status"] == "PRESENT"
    assert signals["NO_CHAT_WIDGET"]["status"] == "PRESENT"


def test_found_booking_marks_the_concern_absent():
    pages = [_home(booking_links=["https://example-hvac.com/schedule"])]
    signals = {s["signalType"]: s for s in bs.classify_signals(pages)}
    assert signals["NO_ONLINE_BOOKING"]["status"] == "ABSENT"


def test_review_and_search_signals_stay_not_reviewed():
    """Unknown is not the same as not-applicable — never guess these."""
    signals = {s["signalType"]: s for s in bs.classify_signals([_home()])}
    for unknown in ("LOW_REVIEW_RESPONSE", "OLD_LATEST_REVIEW",
                    "LOW_REVIEW_COUNT", "WEAK_SEARCH_VISIBILITY"):
        assert signals[unknown]["status"] == "NOT_REVIEWED"


def test_slow_page_flagged_only_past_threshold():
    fast = {s["signalType"]: s for s in bs.classify_signals([_home(load_ms=800)])}
    slow = {s["signalType"]: s for s in bs.classify_signals([_home(load_ms=9000)])}
    assert fast["SLOW_PERFORMANCE"]["status"] == "ABSENT"
    assert slow["SLOW_PERFORMANCE"]["status"] == "PRESENT"


def test_all_signal_types_are_known_to_the_tool():
    """Signal IDs must match the catalog in docs/index.html or the import silently drops them."""
    known = {
        "NO_CHAT_WIDGET", "NO_ONLINE_BOOKING", "NO_FINANCING", "SLOW_PERFORMANCE",
        "LOW_REVIEW_RESPONSE", "OLD_LATEST_REVIEW", "LOW_REVIEW_COUNT",
        "WEAK_SEARCH_VISIBILITY", "THIN_SERVICE_PAGES", "NO_SMS_OPTION",
        "NO_PRICING_GUIDANCE", "PHONE_NOT_PROMINENT", "WEAK_CTA",
    }
    pages = [_home(), bs.PageFacts(url="https://example-hvac.com/ac", word_count=100)]
    for signal in bs.classify_signals(pages):
        assert signal["signalType"] in known


def test_empty_or_failed_scan_produces_nothing_rather_than_guesses():
    failed = [bs.PageFacts(url="https://example-hvac.com/", error="timeout")]
    assert bs.classify_signals(failed) == []
    assert bs.build_draft_tests(failed) == []
    payload = bs.build_observations(failed, "https://example-hvac.com/")
    assert payload["errors"] and not payload["signals"]


# --------------------------------------------------------------------------
# Never claim a link is dead when we simply could not check it
# --------------------------------------------------------------------------

def test_unreachable_links_are_not_reported_as_broken():
    pages = [_home(conversion_links=[
        {"href": "https://example-hvac.com/a", "status": "ok", "detail": ""},
        {"href": "https://example-hvac.com/b", "status": "unverified", "detail": "timeout"},
    ])]
    draft = next(d for d in bs.build_draft_tests(pages) if d["checkId"] == "EXT-011")
    assert "none returned an error" in draft["agentObservation"]
    assert "could not be checked" in draft["agentObservation"]


def test_genuinely_broken_links_are_reported_with_the_unverified_caveat():
    pages = [_home(conversion_links=[
        {"href": "https://example-hvac.com/dead", "status": "broken", "detail": "HTTP 404"},
        {"href": "https://example-hvac.com/b", "status": "unverified", "detail": "timeout"},
    ])]
    obs = next(d for d in bs.build_draft_tests(pages)
               if d["checkId"] == "EXT-011")["agentObservation"]
    assert "1 of 2 conversion links returned an error" in obs
    assert "NOT counted as broken" in obs


def test_booking_needs_a_real_destination_not_just_cta_text():
    links = [{"href": "https://example-hvac.com/dead-link.html", "text": "Request Service"}]
    facts = bs._extract_facts(
        {"links": links, "bodyLower": "", "htmlLower": "<html></html>"},
        "https://example-hvac.com/", 500)
    assert facts.booking_links == []

    real = bs._extract_facts(
        {"links": [{"href": "https://example-hvac.com/schedule/", "text": "Book"}],
         "bodyLower": "", "htmlLower": "<html></html>"},
        "https://example-hvac.com/", 500)
    assert real.booking_links


def test_booking_widget_marker_counts_as_a_booking_path():
    facts = bs._extract_facts(
        {"links": [], "bodyLower": "", "htmlLower": "<script src='housecallpro.js'>"},
        "https://example-hvac.com/", 500)
    assert facts.booking_links == ["widget:housecallpro"]


# --------------------------------------------------------------------------
# Click-to-call correctness
# --------------------------------------------------------------------------

def test_mismatched_click_to_call_is_called_out():
    pages = [_home(tel_links=["tel:+18889999999"])]
    draft = next(d for d in bs.build_draft_tests(pages, published_phone="832-555-1234")
                 if d["checkId"] == "EXT-008")
    assert "does not match" in draft["agentObservation"]


def test_matching_click_to_call_is_not_called_a_mismatch():
    pages = [_home(tel_links=["tel:+18325551234"])]
    draft = next(d for d in bs.build_draft_tests(pages, published_phone="(832) 555-1234")
                 if d["checkId"] == "EXT-008")
    assert "does not match" not in draft["agentObservation"]


def test_missing_tel_link_is_reported():
    pages = [_home(tel_links=[], tel_above_fold=False)]
    draft = next(d for d in bs.build_draft_tests(pages) if d["checkId"] == "EXT-008")
    assert "No tel: link" in draft["agentObservation"]


# --------------------------------------------------------------------------
# Job summary
# --------------------------------------------------------------------------

def test_summary_repeats_the_scope_caveat():
    payload = bs.build_observations([_home()], "https://example-hvac.com/")
    md = bs.format_summary(payload)
    assert "never called, texted, submitted a form, or booked" in md
    assert "all PLANNED, none verified" in md
    assert "EXT-001..007 and EXT-015 remain manual" in md


def test_summary_escapes_pipes_so_tables_survive():
    pages = [_home(tel_links=["tel:+1888|999"])]
    payload = bs.build_observations(pages, "https://example-hvac.com/",
                                    published_phone="832-555-1234")
    md = bs.format_summary(payload)
    for line in md.splitlines():
        if line.startswith("| `EXT-008`"):
            assert "\\|" in line  # the pipe inside the content was escaped
            unescaped = sum(1 for i, ch in enumerate(line)
                            if ch == "|" and (i == 0 or line[i - 1] != "\\"))
            assert unescaped == 4  # 3 cells => 4 delimiters, table stays intact
            break
    else:
        pytest.fail("EXT-008 row missing from summary")


def test_summary_lists_unreadable_pages():
    pages = [_home(), bs.PageFacts(url="https://example-hvac.com/x", error="timeout")]
    md = bs.format_summary(bs.build_observations(pages, "https://example-hvac.com/"))
    assert "could not be read" in md and "timeout" in md


# --------------------------------------------------------------------------
# Safety rails
# --------------------------------------------------------------------------

@pytest.mark.parametrize("url", [
    "http://localhost:8000/",
    "http://127.0.0.1/",
    "http://169.254.169.254/latest/meta-data/",
    "http://10.0.0.5/",
])
def test_private_and_metadata_targets_are_refused(url):
    with pytest.raises(ValueError):
        bs.check_url_safe(url)


@pytest.mark.parametrize("url", ["ftp://example.com/", "file:///etc/passwd", "not-a-url"])
def test_non_http_schemes_are_refused(url):
    with pytest.raises(ValueError):
        bs.check_url_safe(url)


def test_private_hosts_allowed_only_behind_the_explicit_flag():
    with pytest.raises(ValueError):
        bs.check_url_safe("http://127.0.0.1:9999/")
    assert bs.check_url_safe("http://127.0.0.1:9999/", allow_private_hosts=True)


def test_same_site_does_not_leak_to_other_domains():
    assert bs.same_site("https://www.example-hvac.com/ac", "https://example-hvac.com/")
    assert not bs.same_site("https://evil.com/ac", "https://example-hvac.com/")
    assert not bs.same_site("https://example-hvac.com.evil.com/", "https://example-hvac.com/")


def test_observe_site_reports_missing_extra_clearly(monkeypatch):
    """Without the browser extra, fail with a useful message rather than a traceback."""
    import builtins
    real_import = builtins.__import__

    def fake_import(name, *args, **kwargs):
        if name.startswith("playwright"):
            raise ImportError("no playwright")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", fake_import)
    with pytest.raises(RuntimeError, match="browser extra"):
        bs.observe_site("https://example-hvac.com/")
