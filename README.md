# Leak Detector MVP

Revenue Recovery for independent residential HVAC contractors.

Leak Detector finds a specific, evidence-backed revenue leak on an HVAC
contractor's website or phone-handling process (a missed-call gap, a broken
"24/7" claim, booking friction, etc.), then sells a $997 fixed-scope
**Revenue Recovery Sprint** to fix it. Sizzle's static operator cockpit reads
the local prospect record; it does not add a backend, subscription, or
autonomous execution before the offer is proven to sell and deliver.

**Validation question:** Can Leak Detector acquire an HVAC customer,
profitably deliver a $997 Revenue Recovery Sprint, and document recovered
revenue?

**Hard gate:** five real, client-facing proposals sent before any platform
expansion. See `docs/VALIDATION_SCOREBOARD.md` for the three gates (Sell →
Prove → Repeat) and the current read.

Target → Diagnose → Verify → Quantify → Sell → Baseline → Fix → Measure → Prove.

## Status

Launch-stage MVP. Code and operating docs are ahead of sales progress —
Batch 1 (5 prospects) is sourced in `pipeline.md` but not yet verified,
audited, or proposed. Nothing beyond the four CLI commands below and the
fallback (non-browser) scan path is load-bearing; see `OPERATOR.md` for
what's intentionally frozen until Gate 1 clears.

## Quick start

```bash
pip install -e .
```

Requires Python 3.10+. No external services or API keys are needed for the
default (fallback) path — everything is standard library. The optional
`leak-detector-observe` browser-based checks need the `browser` extra
(`pip install -e ".[browser]"`, which pulls in Playwright).

Core commands, run in this order per prospect:

```bash
leak-detector-scan "https://example-hvac.com"
leak-detector-audit "ACME HVAC" "https://example-hvac.com" --metrics metrics.json
leak-detector-propose "ACME HVAC" path/to/opportunities.json
```

`leak-detector-audit` and `leak-detector-propose` both take the client name
as the first argument, before the URL or file path. `metrics.json` is the
manually captured evidence from the 20-minute verification pass (see
`docs/SALES_PLAYBOOK.md` §3) — the scan alone is not enough to sell on.

## Docs

- **`OPERATOR.md`** — how to run the system end to end, and what's
  intentionally not built yet.
- **`docs/LAUNCH_PLAN.md`** — the step-by-step launch sequence.
- **`docs/GOOGLE_MAPS_RESEARCH.md`** — optional local listing research for the first five prospects.
- **`docs/SALES_PLAYBOOK.md`** — how to qualify, verify, and sell a prospect.
- **`docs/MEASUREMENT_PROTOCOL.md`** — how documented recovered revenue gets
  measured after delivery.
- **`docs/VALIDATION_SCOREBOARD.md`** — the three gates, KPI hierarchy, and
  the current Batch 1 read.
- **`pipeline.md`** — the live prospect pipeline (Batch 1 + bench).

## Rule

Do not expand the platform, add a second vertical, or build any of the
post-validation architecture in `docs/MVP.md` until five real proposals have
gone out and been read honestly against the gates above. The dashboard in
`docs/index.html` is a view of the existing local operator records, not a
change to that gate.

## Privacy note

`docs/observations/` and any scan/audit reports contain real business names,
phone numbers, and site content pulled from public sources for prospecting
purposes. Treat that directory (and anything under the gitignored `reports/`
folder) as containing real third-party business data, not sample data —
don't publish it anywhere beyond what the launch plan explicitly calls for
(e.g. GitHub Pages for the Sizzle observation tool, if you choose to enable
it).
