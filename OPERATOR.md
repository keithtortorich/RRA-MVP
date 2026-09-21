# Leak Detector MVP Operator Guide

## Purpose

Run the smallest end-to-end system that can produce a credible paid revenue-recovery audit and a client-safe proposal.

## Prerequisites

- Python environment suitable for the repository.
- Python 3.10+.
- No external worker repositories are required for the default fallback path.

Optional full-fidelity worker mode can use:
  - `ai-marketing-claude`
  - `geo-seo-claude`
  - `ai-reputation-claude`
  - `ai-sales-team-claude`

`src/leak_detector/runner.py` also defines a fifth worker slot, `proposal`
(`RRA_PROPOSAL_REPO` / `ai-proposal-claude`), but nothing in the current
`leak-detector-scan` / `leak-detector-audit` / `leak-detector-propose` commands calls it —
`leak-detector-propose` builds the proposal directly from the opportunities JSON,
no worker subprocess involved. You do not need this fifth repo to run the
live path; it's unused configuration, not a missing prerequisite. If a
worker actually calls it in the future, add it here as a real prerequisite.

## Optional worker configuration

From the Leak Detector repository root:

```bash
export RRA_MARKETING_REPO="$(pwd)/../ai-marketing-claude"
export RRA_GEO_REPO="$(pwd)/../geo-seo-claude"
export RRA_REPUTATION_REPO="$(pwd)/../ai-reputation-claude"
export RRA_SALES_REPO="$(pwd)/../ai-sales-team-claude"
```

## Install

```bash
pip install -e .
```

## Commands

`leak-detector-audit` and `leak-detector-propose` both require the client name as the
first argument, before the URL or file path:

```bash
leak-detector-scan https://example-hvac.com
leak-detector-audit "ACME HVAC" https://example-hvac.com
leak-detector-propose "ACME HVAC" path/to/opportunities.json
```

### Observation agent (optional)

> **Scope decision — read before changing or removing this.**
> The Sizzle External Leak Verification plan states "do not create a scanner"
> and rules out a crawler or monitoring. `leak-detector-observe` and the weekly
> `observe` workflow are a scanner and scheduled monitoring, and they are an
> **authorised exception to that constraint**, decided by the repository owner
> after the agent was built. Do not delete them as a plan violation.
>
> The exception has a boundary, and the boundary is the part that still binds:
> the agent observes public pages and nothing else. It never contacts a
> business — no form submission, no booking, no call, no text — and it never
> produces a determinate result. EXT-001 through EXT-007 and EXT-015 stay
> manual. Do not extend the agent past that line without asking the owner; the
> plan's other guardrails (§13, and "the application records tests; operators
> execute them") are unaffected by this exception.

`leak-detector-observe` renders a prospect's public pages in a headless browser and
writes signals plus pre-filled **draft** tests for the checks a browser can see
on its own. Install the extra first:

```bash
pip install -e ".[browser]"
python -m playwright install chromium
leak-detector-observe https://example-hvac.com --phone "832-555-1234" --screenshots shots/
```

Import the resulting JSON in the Sizzle tool: prospect → Evidence → **Import
agent observations** — or let the tool pull runs on its own, which needs Pages
(below).

### Serving the tool (one-time setup)

Auto-sync only works when the tool is served over HTTP: a page opened as a local
file cannot fetch `observations/index.json`. Enable GitHub Pages once, at
Settings → Pages:

- **Source:** Deploy from a branch
- **Branch:** `main`, folder `/docs`

The site is then at `https://<owner>.github.io/RRA-MVP/`, and every push to
`docs/` — including the observe workflow's commits — republishes it.

This was tried as an Actions workflow with `actions/configure-pages`
(`enablement: true`) so no setting needed touching. It does not work: the
default `GITHUB_TOKEN` may deploy to an existing Pages site but is not
permitted to create one, and the run fails with *"Create Pages site failed:
Resource not accessible by integration."* Creating the site needs the settings
UI or a PAT with admin scope. Branch source is also the better fit regardless —
`docs/` is static and committed, so there is no build step worth a workflow run
on every observation commit.

Pages is public. That includes `docs/observations/`, which names prospects and
describes their sites. The tool page carries `noindex` so it stays out of search
results, but that is de-indexing, not access control, and the JSON files cannot
carry a meta tag at all. If the research needs to stay private, leave Pages off
and use **Import from file**.

What it covers: click-to-call correctness, emergency-contact friction,
conversion link integrity, hours consistency, service-area conversion paths,
form friction, and most investigation signals.

What it will not do, by design: it never submits a form, books an appointment,
calls, or sends a text. Those checks — EXT-001 through EXT-007 and EXT-015,
which carry most of the Minimum Truth Pass weight — stay manual. Everything it
produces imports as `PLANNED` and needs your confirmation before it counts
toward a Truth Pass, because an evidence-backed sales claim should be one a
person can defend on the call.

Review-count, review-recency, review-response and search-visibility signals are
left `NOT_REVIEWED` rather than guessed; they need Google Business Profile data
the agent does not collect. A conversion link the agent could not reach is
reported as unverified, never as broken.

For a stronger audit, replace benchmark assumptions with observed metrics:

```bash
leak-detector-audit "ACME HVAC" https://example-hvac.com --metrics metrics.json
```

Example `metrics.json`:

```json
{
  "monthly_inbound_calls": 143,
  "missed_call_rate": 0.52,
  "average_service_ticket": 720
}
```

## Operating sequence

1. Run `leak-detector-scan`.
2. Review evidence and identify assumptions.
3. Manually verify Google reviews, after-hours call handling, mobile site conversion, booking access, and 24/7 claims. Optionally run `leak-detector-observe` first to pre-fill the site-observation half — the call, text, form, and booking checks are still yours.
4. Record observed metrics in `metrics.json`.
5. Run `leak-detector-audit` again with the metrics file.
6. Run `leak-detector-propose` on the resulting opportunities JSON.
7. Send only the client-facing proposal.
8. Record outreach and follow-up in `pipeline.md`.

## Output handling

The proposal command produces two views:

- Internal: evidence, IDs, confidence, assumptions, and operator detail.
- Client-facing: headline, quantified leak, three tiers, and one next step.

Never send the internal view to a prospect.

## Pre-flight acceptance

Before using a real prospect, confirm:

- Installation completes.
- The default fallback scan works without sibling repositories.
- If using optional worker mode, `which claude` succeeds and configured worker paths resolve.
- Installation completes.
- A scan against a harmless test URL completes.
- Audit output is created.
- Proposal output contains separate internal and client-safe views.
- The Good tier matches the top-ranked leak.
- Client output contains no forbidden internal keys.

If the worker invocation in `src/leak_detector/runner.py` does not match the installed Claude CLI, fix and retest it before prospecting.
