"""/revenue scan <url> — thin wrapper over the worker runners."""

from __future__ import annotations
import os
from datetime import date
from pathlib import Path
from typing import List, Optional

from rra.runner import run_workers_parallel


SCAN_WORKERS = ["marketing", "geo", "reputation", "sales"]
DEFAULT_OUTPUT_DIR = "reports/scans"


def scan(url: str, output_dir: Optional[str] = None,
         workers: Optional[List[str]] = None) -> str:
    workers = workers or SCAN_WORKERS
    output_dir = output_dir or DEFAULT_OUTPUT_DIR
    os.makedirs(output_dir, exist_ok=True)

    print(f"[scan] running workers: {', '.join(workers)}")
    results = run_workers_parallel(workers, url)

    slug = _slugify(url)
    today = date.today().isoformat()
    report_path = Path(output_dir) / f"{slug}-{today}.md"
    _write_report(report_path, url, results)
    print(f"[scan] report written → {report_path}")
    return str(report_path)


def _slugify(url: str) -> str:
    cleaned = url.replace("https://", "").replace("http://", "").strip("/")
    cleaned = cleaned.replace("/", "-").replace(".", "-")
    return cleaned or "target"


def _write_report(path: Path, url: str, results: dict) -> None:
    parts: List[str] = []
    parts.append("# Revenue Leak Report\n")
    parts.append(f"**Target:** {url}  ")
    parts.append(f"**Date:** {date.today().isoformat()}  ")
    parts.append("**Status:** draft — operator to fill dollar figures\n")
    parts.append("---\n")
    parts.append("## Estimated Monthly Opportunity\n")
    parts.append("> **$______/mo** total estimated recoverable revenue\n")
    parts.append("## Top Leaks\n")
    parts.append("| # | Leak | $/mo | Confidence | Ease | Recommendation |")
    parts.append("|---|------|------|------------|------|----------------|")
    parts.append("| 1 |      |      |            |      |                |")
    parts.append("| 2 |      |      |            |      |                |")
    parts.append("| 3 |      |      |            |      |                |")
    parts.append("\n**Start here:** ______________________________________\n")
    parts.append("---\n")
    parts.append("## Raw Worker Outputs\n")
    for worker, result in results.items():
        parts.append(f"### {worker}  ")
        parts.append(f"Status: `{result.status}`  ")
        if result.status != "ok":
            parts.append(f"> _Worker error:_ `{result.stderr.strip()[:400]}`  \n")
        if result.stdout:
            parts.append("<details><summary>Output</summary>\n")
            parts.append("```")
            parts.append(result.stdout.strip()[:20000])
            parts.append("```")
            parts.append("</details>\n")
    path.write_text("\n".join(parts), encoding="utf-8")
