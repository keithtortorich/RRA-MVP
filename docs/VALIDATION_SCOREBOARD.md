# RRA Validation Scoreboard

Status: launch-stage tracking doc, not software. A spreadsheet works just
as well — this file is the template and the record of what the numbers
mean, kept next to `pipeline.md` (which tracks pipeline *state* per
prospect) and `docs/MEASUREMENT_PROTOCOL.md` (which defines how the
recovered-revenue and delivery-hours columns get filled in).

## The three gates

Do not let version numbers or architecture drive what gets built next.
Let evidence drive it. Three gates, in order:

**Gate 1 — SELL.** Can RRA consistently get an HVAC owner to pay ~$1,000
to fix an evidence-backed leak? Until yes: no more platform development.

**Gate 2 — PROVE.** Can RRA deliver that fix profitably and document
recovered revenue within ~30 days, using `docs/MEASUREMENT_PROTOCOL.md`?
Until yes: no scaling infrastructure.

**Gate 3 — REPEAT.** Can RRA repeat the process across multiple shops
without reinventing delivery each time? Only then does the
POST-VALIDATION ARCHITECTURE in `docs/MVP.md` (benchmark promotion,
associates, work queues, retention engines, a second vertical, portals,
autonomous playbooks) get activated. It stays quarantined — read as
options, not a roadmap — until this gate is actually cleared.

## Batch ladder

Five is still the right first batch — small enough to hand-hold, large
enough to learn from. The mistake is treating 0/5 or 2/5 as a final verdict
on the business. Read it as a staged experiment instead:

| Batch | Size | Cumulative | Purpose |
|---|---:|---:|---|
| 1 | 5 | 5 | Maximum personalization. Learn whether owners understand and believe the offer at all. |
| 2 | 10 | 15 | Change only the one variable that looked broken in Batch 1 (targeting, evidence quality, wedge, price presentation, or proposal clarity — see `docs/SALES_PLAYBOOK.md` §8). |
| 3 | 20 | 35 | Test repeatability of whatever worked in Batch 2. |

Do not jump to 100 generic audits. Thirty-five carefully selected prospects,
read honestly batch over batch, teach more than a hundred rushed ones.

## KPI hierarchy

Track these in order — each one only matters once the one above it is
moving:

| # | KPI | What it tells you |
|---|---|---|
| 0 | Proposals sent | Is outreach happening at all |
| 1 | Conversations started | Is the wedge earning attention |
| 2 | Paid recoveries sold | Gate 1 (SELL) |
| 3 | Documented revenue recovered | Gate 2 (PROVE) — from the measurement protocol, never the pre-fix estimate |
| 4 | Gross margin per recovery | Is this profitable to deliver, not just sellable |
| 5 | Expansion / retention | Did Good lead to Better/Best, or a referral |
| 6 | Operator hours per client | Gate 3 (REPEAT) — the real long-run number is **documented recovered revenue ÷ RRA delivery hour**. That ratio is what tells you whether RRA is an AI-leveraged business or a sophisticated consulting job wearing a dashboard. |

## Scoreboard

One row per prospect. `Recovered Revenue` and `Delivery Hours` only get
filled in after `docs/MEASUREMENT_PROTOCOL.md` has run for that engagement.

| # | Batch | Business | Sent | Replied | Conversation | Proposal | Paid (tier / $) | Recovered Revenue (documented) | Delivery Hours | Notes |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 1 | | | | | | | | | |
| 2 | 1 | | | | | | | | | |
| 3 | 1 | | | | | | | | | |
| 4 | 1 | | | | | | | | | |
| 5 | 1 | | | | | | | | | |

Add rows for Batch 2 / Batch 3 only after the Batch 1 read below has been
done honestly.

## Reading a batch (do this before adding the next one)

After every prospect in a batch has been contacted and given time to
respond (Day 11 follow-up has passed or they've converted/declined):

- **2-3+ sold** → Gate 1 cleared for this batch. Move to Gate 2: deliver,
  run the measurement protocol, and turn the result into a case study.
- **0 sold, but real conversations happened** → the offer is close. Change
  exactly one variable and run the next batch. Do not change the product.
- **0 replies** → targeting, message, or evidence quality failed to earn
  attention. Change targets or numbers, not architecture.

Whatever the batch says, write the read here before starting the next one
— that record is what keeps this an experiment instead of a vibe.

### Batch 1 read

- Result:
- Variable changed for Batch 2 (if any):
- Date:
