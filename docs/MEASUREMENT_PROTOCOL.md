# Leak Detector First-Client Measurement Protocol

Status: launch-stage protocol, not software. Nothing here requires building
v2. It is the smallest manual discipline that lets Leak Detector say "we recovered
$X, documented" instead of "we estimate we recovered $X."

## Why this exists

The audit and calculator size an *opportunity* before the fix. That number
is explicitly KNOWN / ESTIMATED / BENCHMARK and is never sent to a client as
a promise (see `docs/SALES_PLAYBOOK.md` and the guardrails in
`src/leak_detector/core/guardrails.py`). This protocol is the other half: after the fix is
installed, Leak Detector measures what actually happened and turns that into a
documented result. Estimation gets the meeting. Measurement is what makes
the second sale easier than the first, and it is what eventually lets Leak Detector's
own recovery data replace industry benchmarks.

Three documented recoveries become the first case studies. Every measured
engagement is one data point toward Leak Detector no longer needing to guess.

## Scope for the first five (and the next batches)

Manual. A spreadsheet or this doc's tables are sufficient. Do not build a
measurement dashboard, automated attribution system, or analytics platform
for this. That stays frozen with everything else in the launch freeze.

## The protocol

For each paid engagement:

### 1. Baseline (before the fix, trailing 30 days where possible)

Capture using the same KNOWN / ESTIMATED / BENCHMARK labeling as the audit.
Prefer KNOWN — ask the owner directly, or observe directly (call the
business, check public review/booking signals) rather than defaulting to
benchmarks.

For a missed-call / lead-capture fix (the primary launch wedge):

| Metric | Value | Label | Source |
|---|---|---|---|
| Inbound calls | | | |
| Unanswered / missed calls | | | |
| After-hours calls | | | |
| Callbacks completed | | | |
| Booked jobs | | | |
| Completed jobs | | | |
| Revenue from those jobs | | | |

Adapt the row set to whichever leak from `src/leak_detector/verticals/hvac/leak_library.py`
is actually being fixed (booking friction, follow-up, reputation, etc.) —
the shape stays the same: the metrics that feed that leak's sizing formula,
captured before the fix.

### 2. Intervention record

- Fix implemented:
- Date installed:
- Leak ID (`HVAC-LEAK-0xx`):
- Anything else that changed in the same window (season, ad spend, staffing,
  competitor activity) — record it now, not after the numbers come in.

### 3. Post-intervention (same window length, e.g. 30 days after install)

| Metric | Value | Label | Source |
|---|---|---|---|
| Missed calls | | | |
| Text-backs sent | | | |
| Conversations initiated | | | |
| Appointments booked | | | |
| Jobs completed | | | |
| Documented revenue from those jobs | | | |

### 4. The result statement

Write it as an observation, not a claim of causation:

> "In the 30 days after the fix, N previously-missed calls were recovered,
> B were booked, C were completed, producing $R in documented revenue from
> those jobs. Known confounds: [seasonality / lead volume change / none
> observed]."

Never write "Leak Detector increased revenue by $R." Write what was counted and what
might have contaminated it. The confound line is not optional — leaving it
off is how a documented number quietly turns into an unfalsifiable claim.

### 5. What this becomes

- A case study, once the owner agrees to be named or referenced.
- One row in the validation scoreboard (`docs/VALIDATION_SCOREBOARD.md`).
- Eventually, a data point that lets a future opportunity estimate for a
  similar HVAC shop cite Leak Detector's own observed recovery rate instead of an
  industry benchmark. That swap doesn't happen after one measurement — it
  happens somewhere around 50 measured engagements. This protocol is how
  those 50 get collected without building anything.

## What this protocol is not

- Not a guarantee to the client. The Good/Better/Best offers stay fixed-fee,
  never contingent on the measured result (guardrails already block
  revenue-share and performance pricing).
- Not automated. No integration pulls these numbers — they're gathered the
  same manual way the 20-minute evidence pass is done today.
- Not v2. `docs/MVP.md`'s broader benchmark-promotion and retention-engine
  architecture is POST-VALIDATION ARCHITECTURE — do not build toward it
  from this protocol. This is the smallest version of "measure the
  recovery" that a human can run with a spreadsheet.
