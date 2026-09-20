"""RRA MVP — CLI entry points."""

from __future__ import annotations

import argparse
import json
import os
import sys

from rra import audit as audit_mod
from rra import browser_scan as browser_scan_mod
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


def observe_cmd(argv=None) -> int:
    parser = argparse.ArgumentParser(
        prog="revenue-observe",
        description="Observation-only browser agent. Renders a prospect's public pages and "
                    "records signals plus PLANNED draft tests. It never submits a form, "
                    "books an appointment, calls, or texts — those checks stay manual.")
    parser.add_argument("url", nargs="?", default=None,
                        help="Single site to observe. Omit when using --targets.")
    parser.add_argument("--targets", default=None,
                        help="JSON file of targets to run in one pass (see targets.json)")
    parser.add_argument("--phone", default="",
                        help="Published phone number, to check the click-to-call link against")
    parser.add_argument("--out", default="reports/observations")
    parser.add_argument("--pages", type=int, default=None,
                        help=f"Max pages to render (default {browser_scan_mod.MAX_PAGES})")
    parser.add_argument("--screenshots", default=None,
                        help="Directory for screenshots used as evidence references")
    parser.add_argument("--browser-path", default=None,
                        help="Chromium executable path, if not the Playwright default")
    parser.add_argument("--allow-private-hosts", action="store_true",
                        help="Permit non-public targets. Off by default; for local test "
                             "fixtures only, so the suite never touches a real business.")
    parser.add_argument("--summary-md", default=None,
                        help="Append a Markdown summary here (e.g. $GITHUB_STEP_SUMMARY)")
    args = parser.parse_args(argv)

    if not args.url and not args.targets:
        parser.error("give a url, or --targets pointing at a target list")

    if args.targets:
        runnable, skipped = browser_scan_mod.load_targets(args.targets)
    else:
        runnable = [{"company": "", "url": args.url, "phone": args.phone}]
        skipped = []

    stems = browser_scan_mod.unique_slugs([t["url"] for t in runnable])
    payloads, failures = [], []
    for target in runnable:
        stem = stems[target["url"]]
        label = target["company"] or target["url"]
        print(f"[observe] {label} — {target['url']}")
        try:
            payload = browser_scan_mod.observe_site(
                target["url"],
                published_phone=target["phone"] or args.phone,
                max_pages=args.pages or browser_scan_mod.MAX_PAGES,
                screenshot_dir=(os.path.join(args.screenshots, stem)
                                if args.screenshots else None),
                allow_private_hosts=args.allow_private_hosts,
                executable_path=args.browser_path,
                company=target["company"],
            )
        except Exception as exc:
            # One unreachable prospect must not sink the rest of the batch.
            print(f"[observe] FAILED {label}: {exc}")
            failures.append({"company": target["company"], "url": target["url"],
                             "error": str(exc)[:200]})
            continue
        payload["file"] = f"{stem}.json"
        path = browser_scan_mod.write_observations(payload, args.out, target["url"], stem)
        payloads.append(payload)
        print(f"[observe]   -> {path} "
              f"({len(payload['draftTests'])} draft test(s), all PLANNED)")

    index = browser_scan_mod.build_index(payloads, skipped + failures)
    index_path = os.path.join(args.out, "index.json")
    os.makedirs(args.out, exist_ok=True)
    with open(index_path, "w", encoding="utf-8") as fh:
        json.dump(index, fh, indent=2)
    print(index_path)

    if args.summary_md:
        with open(args.summary_md, "a", encoding="utf-8") as fh:
            for payload in payloads:
                fh.write(browser_scan_mod.format_summary(payload) + "\n")
            for entry in skipped + failures:
                fh.write(f"\n> Skipped **{entry.get('company') or entry.get('url')}** — "
                         f"{entry.get('reason') or entry.get('error')}\n")

    print(f"[observe] {len(payloads)} site(s) observed, {len(skipped)} skipped, "
          f"{len(failures)} failed. Everything is PLANNED — nothing is verified.")
    return 0 if payloads or not runnable else 1


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
