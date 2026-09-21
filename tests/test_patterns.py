import json
from pathlib import Path

from leak_detector import patterns as patterns_mod
from leak_detector.cli import patterns_cmd


def _write_observation(dir_path, filename, company, host, signals):
    payload = {
        "leakDetectorObservations": 1,
        "company": company,
        "host": host,
        "target": f"https://{host}",
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
    assert rows[-1]["company"] == "Charlie HVAC"
    assert rows[-1]["score"] == 0.0


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
