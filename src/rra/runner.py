"""Runs Zubair's worker suites as black boxes."""

from __future__ import annotations
import os
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional


WORKER_PATHS: Dict[str, str] = {
    "sales":      os.environ.get("RRA_SALES_REPO",      "../ai-sales-team-claude"),
    "marketing":  os.environ.get("RRA_MARKETING_REPO",  "../ai-marketing-claude"),
    "geo":        os.environ.get("RRA_GEO_REPO",        "../geo-seo-claude"),
    "reputation": os.environ.get("RRA_REPUTATION_REPO", "../ai-reputation-claude"),
    "proposal":   os.environ.get("RRA_PROPOSAL_REPO",   "../ai-proposal-claude"),
}

WORKER_COMMANDS: Dict[str, List[str]] = {
    "sales":      ["claude", "run", "audit", "--target", "{target}"],
    "marketing":  ["claude", "run", "audit", "--url",    "{target}"],
    "geo":        ["claude", "run", "audit", "--url",    "{target}"],
    "reputation": ["claude", "run", "audit", "--url",    "{target}"],
    "proposal":   ["claude", "run", "propose", "--input", "{input}"],
}


@dataclass
class WorkerResult:
    worker: str
    status: str
    stdout: str = ""
    stderr: str = ""
    output_path: Optional[str] = None


def run_worker(worker: str, target: str, timeout_seconds: int = 900,
                extra_args: Optional[List[str]] = None) -> WorkerResult:
    if worker not in WORKER_PATHS:
        return WorkerResult(worker=worker, status="failed",
                            stderr=f"unknown worker '{worker}'")

    repo = Path(WORKER_PATHS[worker]).expanduser().resolve()
    if not repo.is_dir():
        return WorkerResult(worker=worker, status="missing",
                            stderr=f"repo not found at {repo}.")

    command_template = WORKER_COMMANDS.get(worker)
    if not command_template:
        return WorkerResult(worker=worker, status="failed",
                            stderr=f"no command template for '{worker}'")

    command = [part.format(target=target, input=target) for part in command_template]
    if extra_args:
        command.extend(extra_args)

    try:
        proc = subprocess.run(command, cwd=str(repo), capture_output=True,
                               text=True, timeout=timeout_seconds)
    except subprocess.TimeoutExpired:
        return WorkerResult(worker=worker, status="failed",
                            stderr=f"timeout after {timeout_seconds}s")
    except FileNotFoundError as exc:
        return WorkerResult(worker=worker, status="failed",
                            stderr=f"command not found: {exc}")

    status = "ok" if proc.returncode == 0 else "failed"
    return WorkerResult(worker=worker, status=status,
                        stdout=proc.stdout, stderr=proc.stderr)


def run_workers_parallel(workers: List[str], target: str,
                          timeout_seconds: int = 900) -> Dict[str, WorkerResult]:
    from concurrent.futures import ThreadPoolExecutor
    results: Dict[str, WorkerResult] = {}
    with ThreadPoolExecutor(max_workers=len(workers)) as pool:
        futures = {pool.submit(run_worker, w, target, timeout_seconds): w
                   for w in workers}
        for future, worker in futures.items():
            try:
                results[worker] = future.result()
            except Exception as exc:
                results[worker] = WorkerResult(worker=worker, status="failed",
                                                stderr=str(exc))
    return results
