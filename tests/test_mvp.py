import json
from pathlib import Path
import pytest
from rra.core.guardrails import validate_proposal
from rra.verticals.hvac.leak_library import match_signals
from rra import audit as audit_mod
from rra import propose as propose_mod
from rra import runner
from rra.scoring import score_evidence
from rra.fallback_scan import scan_public_url

def evidence(signal="missed_call_rate_high",confidence=0.9): return [{"id":"EVD-1","signal":signal,"confidence":confidence,"observation":signal}]

def test_signal_matches_expected_hvac_leak():
    matches=match_signals(["missed_call_rate_high"]); assert matches; assert matches[0].leak_id=="HVAC-LEAK-001"

def test_low_confidence_evidence_is_dropped():
    result=score_evidence("biz",evidence(confidence=0.49)); assert result.opportunities==[]; assert "no signals extracted" in result.warnings

def test_scoring_to_proposal_happy_path():
    result=score_evidence("biz",evidence()); assert result.opportunities; top=result.opportunities[0]; assert top["leak_id"]=="HVAC-LEAK-001"; assert top["estimated_monthly_opportunity"]>0
    proposal=propose_mod.build_proposal({"business_id":"biz","name":"ACME HVAC"},result.opportunities); assert proposal["tiers"]["good"]["price"]==997; assert proposal["tiers"]["good"]["leak_id"]==top["leak_id"]
    ok,violations=validate_proposal(proposal); assert ok,violations

def test_proposal_requires_opportunity():
    with pytest.raises(ValueError,match="no opportunities"): propose_mod.build_proposal({"business_id":"biz","name":"ACME"},[])

def test_guardrail_blocks_revenue_share():
    result=score_evidence("biz",evidence()); proposal=propose_mod.build_proposal({"business_id":"biz","name":"ACME"},result.opportunities); proposal["tiers"]["good"]["description"] += " revenue share"; ok,violations=validate_proposal(proposal); assert not ok; assert "REVENUE_SHARE" in violations

def test_guardrail_blocks_premature_access():
    result=score_evidence("biz",evidence()); proposal=propose_mod.build_proposal({"business_id":"biz","name":"ACME"},result.opportunities); proposal["access_boundary"]="admin_credentials"; ok,violations=validate_proposal(proposal); assert not ok; assert "PREMATURE_ACCESS_REQUEST" in violations

def test_missing_worker_repo_returns_missing(monkeypatch,tmp_path):
    monkeypatch.setitem(runner.WORKER_PATHS,"sales",str(tmp_path/"does-not-exist")); assert runner.run_worker("sales","https://example.com").status=="missing"

def test_unknown_worker_fails():
    result=runner.run_worker("nope","https://example.com"); assert result.status=="failed"; assert "unknown worker" in result.stderr

def test_audit_writes_artifacts_with_mock_workers(monkeypatch,tmp_path):
    fake={"marketing":runner.WorkerResult("marketing","ok",stdout="missed call rate high"),"geo":runner.WorkerResult("geo","ok",stdout=""),"reputation":runner.WorkerResult("reputation","ok",stdout=""),"sales":runner.WorkerResult("sales","ok",stdout="")}
    monkeypatch.setattr(audit_mod,"run_workers_parallel",lambda workers,url:fake); out=audit_mod.audit("ACME HVAC","https://example.com",output_dir=str(tmp_path),workers=["marketing","geo","reputation","sales"]); report=Path(out["report_path"]); opps=Path(out["opportunities_path"]); assert report.exists() and opps.exists(); payload=json.loads(opps.read_text()); assert payload["ctx"]["name"]=="ACME HVAC"; assert payload["opportunities"]

def test_automated_findings_are_signals_not_verified_evidence(monkeypatch,tmp_path):
    monkeypatch.setattr(audit_mod,"scan_public_url",lambda url:"- no_click_to_call")
    out=audit_mod.audit("ACME HVAC","https://example.com",output_dir=str(tmp_path))
    payload=json.loads(Path(out["opportunities_path"]).read_text())
    assert payload["opportunities"][0]["modeled_not_recovered"] is True
    assert payload["opportunities"][0]["financial_classification"]=="BENCHMARK"

def test_audit_workers_are_opt_in(monkeypatch,tmp_path):
    monkeypatch.setattr(audit_mod,"run_workers_parallel",lambda workers,url:pytest.fail("workers must be opt-in"))
    monkeypatch.setattr(audit_mod,"scan_public_url",lambda url:"- no_click_to_call")
    audit_mod.audit("ACME HVAC","https://example.com",output_dir=str(tmp_path))

def test_browser_signals_are_labeled_automated_signal():
    from rra.browser_scan import PageFacts, build_observations
    payload=build_observations([PageFacts(url="https://example.com",final_url="https://example.com")],"https://example.com")
    assert payload["classification"]=="AUTOMATED_SIGNAL"
    assert all(s["requiresOperatorVerification"] for s in payload["signals"])

def test_propose_writes_internal_and_client_artifacts(tmp_path):
    result=score_evidence("biz",evidence()); payload={"ctx":{"business_id":"biz","name":"ACME HVAC"},"opportunities":result.opportunities}; src=tmp_path/"opps.json"; src.write_text(json.dumps(payload),encoding="utf-8"); out=propose_mod.propose("ACME HVAC",str(src),output_dir=str(tmp_path)); assert Path(out["operator_path"]).exists(); assert Path(out["client_path"]).exists(); assert "$997" in Path(out["client_path"]).read_text(encoding="utf-8")

def test_fallback_scan_rejects_non_http_url():
    with pytest.raises(ValueError,match="absolute http"): scan_public_url("file:///etc/passwd")

@pytest.mark.parametrize("url", [
    "http://127.0.0.1/",
    "http://localhost/",
    "http://169.254.169.254/latest/meta-data/",
    "http://10.0.0.5/",
    "http://172.16.0.1/",
    "http://192.168.1.1/",
    "http://[::1]/",
    "http://0.0.0.0/",
    "http://0x7f000001/",
    "http://2130706433/",
    "http://[::ffff:127.0.0.1]/",
])
def test_fallback_scan_blocks_ssrf_targets(url):
    with pytest.raises(ValueError, match="non-public address|could not resolve"):
        scan_public_url(url, timeout=2)

def test_fallback_scan_redirect_to_private_ip_is_blocked(monkeypatch):
    import rra.fallback_scan as fs
    real_fetch_once = fs._fetch_once

    def fake_fetch_once(url, timeout):
        if url == "https://example-hvac.com/":
            return 302, {"Location": "http://169.254.169.254/latest/meta-data/"}, b""
        return real_fetch_once(url, timeout)

    monkeypatch.setattr(fs, "_fetch_once", fake_fetch_once)
    with pytest.raises(ValueError, match="non-public address"):
        fs.scan_public_url("https://example-hvac.com/", timeout=2)
