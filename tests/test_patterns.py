import json
from pathlib import Path

import pytest

from leak_detector import patterns as patterns_mod
from leak_detector.cli import patterns_cmd


def _write_observation(dir_path, filename, company, host, signals, generated_at=""):
    payload = {
        "leakDetectorObservations": 1,
        "company": company,
        "host": host,
        "target": f"https://{host}",
        "generatedAt": generated_at,
        "signals": [{"signalType": t, "status": s} for t, s in signals.items()],
    }
    (Path(dir_path) / filename).write_text(json.dumps(payload), encoding="utf-8")
    return payload


def _seed(dir_path):
    _write_observation(dir_path, "a.json", "Alpha HVAC", "alpha.com", {
        "NO_ONLINE_BOOKING": "PRESENT",
        "WEAK_CTA": "PRESENT",
        "NO_SMS_OPTION": "ABSENT",
        "LOW_REVIEW_COUNT": "NOT_REVIEWED",
    })
    _write_observation(dir_path, "b.json", "Bravo HVAC", "bravo.com", {
        "NO_ONLINE_BOOKING": "PRESENT",
        "WEAK_CTA": "PRESENT",
        "NO_SMS_OPTION": "PRESENT",
        "LOW_REVIEW_COUNT": "NOT_REVIEWED",
    })
    _write_observation(dir_path, "c.json", "Charlie HVAC", "charlie.com", {
        "NO_ONLINE_BOOKING": "ABSENT",
        "WEAK_CTA": "ABSENT",
        "NO_SMS_OPTION": "ABSENT",
        "LOW_REVIEW_COUNT": "NOT_REVIEWED",
    })
    (Path(dir_path) / "index.json").write_text(json.dumps({"runs": []}), encoding="utf-8")


def test_load_observations_skips_index_and_reads_signals(tmp_path):
    _seed(tmp_path)
    companies = patterns_mod.load_observations(str(tmp_path))
    assert len(companies) == 3
    alpha = next(c for c in companies if c.company == "Alpha HVAC")
    assert "NO_ONLINE_BOOKING" in alpha.present
    assert "NO_SMS_OPTION" in alpha.absent
    assert "LOW_REVIEW_COUNT" in alpha.not_reviewed


def test_load_observations_dedupes_stale_file_for_same_host(tmp_path):
    # Simulates a target whose URL changed (www -> bare domain): the old
    # slug-named file is left behind by leak-detector-observe rather than
    # replaced, so both files share the same normalized host.
    _write_observation(tmp_path, "www-delta-com.json", "Delta HVAC", "delta.com", {
        "NO_ONLINE_BOOKING": "PRESENT",
    }, generated_at="2026-01-01T00:00:00+00:00")
    _write_observation(tmp_path, "delta-com.json", "Delta HVAC", "delta.com", {
        "NO_ONLINE_BOOKING": "ABSENT",
    }, generated_at="2026-02-01T00:00:00+00:00")

    companies = patterns_mod.load_observations(str(tmp_path))
    assert len(companies) == 1
    assert companies[0].present == []
    assert companies[0].absent == ["NO_ONLINE_BOOKING"]


def test_load_observations_keeps_distinct_paths_on_same_host(tmp_path):
    # Two different location/franchise pages on the same domain are
    # distinct targets (browser_scan.slug_for() keeps them distinct too) —
    # deduping by host alone would wrongly collapse them into one company.
    payload_a = {
        "leakDetectorObservations": 1,
        "company": "Echo HVAC — North",
        "host": "echo.com",
        "target": "https://echo.com/locations/north",
        "generatedAt": "2026-01-01T00:00:00+00:00",
        "signals": [{"signalType": "NO_ONLINE_BOOKING", "status": "PRESENT"}],
    }
    payload_b = {
        "leakDetectorObservations": 1,
        "company": "Echo HVAC — South",
        "host": "echo.com",
        "target": "https://echo.com/locations/south",
        "generatedAt": "2026-01-01T00:00:00+00:00",
        "signals": [{"signalType": "NO_ONLINE_BOOKING", "status": "ABSENT"}],
    }
    (tmp_path / "echo-com-north.json").write_text(json.dumps(payload_a), encoding="utf-8")
    (tmp_path / "echo-com-south.json").write_text(json.dumps(payload_b), encoding="utf-8")

    companies = patterns_mod.load_observations(str(tmp_path))
    assert len(companies) == 2
    assert {c.company for c in companies} == {"Echo HVAC — North", "Echo HVAC — South"}


def test_load_observations_keeps_distinct_ports_on_same_host(tmp_path):
    # A site reachable on a non-default port is a distinct target from the
    # same path on the default port (slug_for() includes the port too).
    payload_default = {
        "leakDetectorObservations": 1,
        "company": "Foxglove HVAC",
        "host": "foxglove.com",
        "target": "https://foxglove.com/office",
        "generatedAt": "2026-01-01T00:00:00+00:00",
        "signals": [{"signalType": "NO_ONLINE_BOOKING", "status": "PRESENT"}],
    }
    payload_alt_port = {
        "leakDetectorObservations": 1,
        "company": "Foxglove HVAC (staging)",
        "host": "foxglove.com",
        "target": "https://foxglove.com:8443/office",
        "generatedAt": "2026-01-01T00:00:00+00:00",
        "signals": [{"signalType": "NO_ONLINE_BOOKING", "status": "ABSENT"}],
    }
    (tmp_path / "foxglove-com-office.json").write_text(
        json.dumps(payload_default), encoding="utf-8")
    (tmp_path / "foxglove-com-8443-office.json").write_text(
        json.dumps(payload_alt_port), encoding="utf-8")

    companies = patterns_mod.load_observations(str(tmp_path))
    assert len(companies) == 2


def test_prevalence_excludes_not_reviewed_from_denominator(tmp_path):
    _seed(tmp_path)
    companies = patterns_mod.load_observations(str(tmp_path))
    rows = {r["signalType"]: r for r in patterns_mod.compute_prevalence(companies)}
    assert "LOW_REVIEW_COUNT" not in rows
    assert rows["NO_ONLINE_BOOKING"]["reviewedCount"] == 3
    assert rows["NO_ONLINE_BOOKING"]["presentCount"] == 2
    assert rows["NO_ONLINE_BOOKING"]["prevalence"] == round(2 / 3, 3)


def test_cooccurrence_finds_pair_travelling_together(tmp_path):
    _seed(tmp_path)
    companies = patterns_mod.load_observations(str(tmp_path))
    rows = patterns_mod.compute_cooccurrence(companies, min_companies=2)
    pair = next(r for r in rows
                if {r["signalA"], r["signalB"]} == {"NO_ONLINE_BOOKING", "WEAK_CTA"})
    assert pair["companiesWithBoth"] == 2
    assert pair["lift"] > 1


def test_cooccurrence_drops_pairs_below_min_companies(tmp_path):
    _seed(tmp_path)
    companies = patterns_mod.load_observations(str(tmp_path))
    rows = patterns_mod.compute_cooccurrence(companies, min_companies=3)
    assert rows == []


def test_company_scores_rank_worst_first(tmp_path):
    _seed(tmp_path)
    companies = patterns_mod.load_observations(str(tmp_path))
    rows = patterns_mod.compute_company_scores(companies)
    assert rows[0]["company"] == "Bravo HVAC"
    assert rows[0]["score"] == 1.0
    assert rows[0]["unscored"] is False
    assert rows[-1]["company"] == "Charlie HVAC"
    assert rows[-1]["score"] == 0.0
    assert rows[-1]["unscored"] is False


def test_company_with_zero_reviewed_signals_is_unscored_not_zero(tmp_path):
    # Every page failed to render, so classify_signals() had nothing to
    # classify — this must not look identical to a company that passed
    # every check (score 0.0).
    _write_observation(tmp_path, "foxtrot.json", "Foxtrot HVAC", "foxtrot.com", {
        "NO_ONLINE_BOOKING": "NOT_REVIEWED",
    })
    _write_observation(tmp_path, "golf.json", "Golf HVAC", "golf.com", {
        "NO_ONLINE_BOOKING": "ABSENT",
    })

    companies = patterns_mod.load_observations(str(tmp_path))
    rows = {r["company"]: r for r in patterns_mod.compute_company_scores(companies)}

    assert rows["Foxtrot HVAC"]["unscored"] is True
    assert rows["Foxtrot HVAC"]["score"] is None
    assert rows["Golf HVAC"]["unscored"] is False
    assert rows["Golf HVAC"]["score"] == 0.0

    ranked = patterns_mod.compute_company_scores(companies)
    # A real 0.0 (checks passed) must sort before an unscored row (unknown).
    assert ranked[-1]["company"] == "Foxtrot HVAC"


def test_report_warns_on_small_sample(tmp_path):
    _seed(tmp_path)
    companies = patterns_mod.load_observations(str(tmp_path))
    report = patterns_mod.build_patterns_report(companies)
    assert report["companyCount"] == 3
    assert any("preliminary" in w for w in report["warnings"])


def test_format_summary_renders_markdown(tmp_path):
    _seed(tmp_path)
    companies = patterns_mod.load_observations(str(tmp_path))
    report = patterns_mod.build_patterns_report(companies)
    md = patterns_mod.format_summary(report)
    assert "Worst-first" in md
    assert "Bravo HVAC" in md


def test_patterns_cmd_writes_report(tmp_path, capsys):
    obs_dir = tmp_path / "observations"
    obs_dir.mkdir()
    _seed(obs_dir)
    out_dir = tmp_path / "out"
    summary_path = tmp_path / "summary.md"

    rc = patterns_cmd([
        "--dir", str(obs_dir),
        "--out", str(out_dir),
        "--summary-md", str(summary_path),
    ])
    assert rc == 0

    report = json.loads((out_dir / "patterns.json").read_text(encoding="utf-8"))
    assert report["companyCount"] == 3
    assert summary_path.exists()
    assert "Worst-first" in summary_path.read_text(encoding="utf-8")


def test_patterns_cmd_reports_failure_on_empty_dir(tmp_path):
    empty_dir = tmp_path / "empty"
    empty_dir.mkdir()
    rc = patterns_cmd(["--dir", str(empty_dir), "--out", str(tmp_path / "out")])
    assert rc == 1


def test_compute_cooccurrence_rejects_nonpositive_min_companies(tmp_path):
    _seed(tmp_path)
    companies = patterns_mod.load_observations(str(tmp_path))
    with pytest.raises(ValueError):
        patterns_mod.compute_cooccurrence(companies, min_companies=0)
    with pytest.raises(ValueError):
        patterns_mod.compute_cooccurrence(companies, min_companies=-1)


def test_patterns_cmd_rejects_nonpositive_min_companies(tmp_path, capsys):
    obs_dir = tmp_path / "observations"
    obs_dir.mkdir()
    _seed(obs_dir)

    try:
        patterns_cmd(["--dir", str(obs_dir), "--out", str(tmp_path / "out"),
                      "--min-companies", "0"])
        assert False, "expected SystemExit from argparse.error"
    except SystemExit as exc:
        assert exc.code == 2
    assert "must be >= 1" in capsys.readouterr().err
