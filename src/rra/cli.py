"""RRA MVP — CLI entry points."""

from __future__ import annotations

import argparse
import json
import sys

from rra import audit as audit_mod
from rra import propose as propose_mod
from rra import scan as scan_mod


def scan_cmd(argv=None) -> int:
    parser = argparse.ArgumentParser(prog="revenue-scan")
    parser.add_argument("url")
    parser.add_argument("--out", default=None)
    parser.add_argument("--workers", default=None)
    args = parser.parse_args(argv)
    workers = args.workers.split(",") if args.workers else None
    path = scan_mod.scan(args.url, output_dir=args.out, workers=workers)
    print(path)
    return 0


def audit_cmd(argv=None) -> int:
    parser = argparse.ArgumentParser(prog="revenue-audit")
    parser.add_argument("client_name")
    parser.add_argument("url")
    parser.add_argument("--out", default=None)
    parser.add_argument("--metrics", default=None,
                        help="Path to JSON file with client-supplied metrics")
    args = parser.parse_args(argv)

    metrics = None
    if args.metrics:
        with open(args.metrics, "r", encoding="utf-8") as fh:
            metrics = json.load(fh)

    result = audit_mod.audit(args.client_name, args.url,
                              output_dir=args.out, client_metrics=metrics)
    print(result["report_path"])
    print(result["opportunities_path"])
    return 0


def propose_cmd(argv=None) -> int:
    parser = argparse.ArgumentParser(prog="revenue-propose")
    parser.add_argument("client_name")
    parser.add_argument("opportunities_path",
                        help="Path to opportunities JSON from revenue-audit")
    parser.add_argument("--out", default=None)
    args = parser.parse_args(argv)

    result = propose_mod.propose(
        client_name=args.client_name,
        opportunities_path=args.opportunities_path,
        output_dir=args.out,
    )
    print(result["client_path"])
    return 0


if __name__ == "__main__":
    sys.exit(scan_cmd())
