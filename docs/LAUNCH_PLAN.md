# Launch
Go Sell.

You now have the smallest system that can produce and deliver a paid audit. The next move is not more code. Your own spec says it in §23:

If yes → we have a business. If no → everything else is theater.

You cannot answer yes or no until you've sent proposals to real HVAC owners and watched what happens. Everything below is sequenced toward that answer.

---

## Step 1 — Pre-flight (30 minutes)

Before touching a real prospect, verify the MVP actually runs end-to-end.

```bash
# Claude Code CLI present?
which claude


# Worker repos cloned somewhere?
ls ../ai-marketing-claude ../geo-seo-claude ../ai-reputation-claude ../ai-sales-team-claude


# Env wired
export RRA_MARKETING_REPO=$(pwd)/../ai-marketing-claude
export RRA_GEO_REPO=$(pwd)/../geo-seo-claude
export RRA_REPUTATION_REPO=$(pwd)/../ai-reputation-claude
export RRA_SALES_REPO=$(pwd)/../ai-sales-team-claude


# Install + smoke
pip install -e .
leak-detector-scan https://example-hvac.com
```

If claude run audit --url ... isn't the correct invocation for your worker repos, fix src/leak_detector/runner.py now. Two hours of debugging against a fake target saves two weeks of confusion against real ones.

Write a one-page operator README (OPERATOR.md) covering the three commands, the env vars, and where the outputs land. Future-you will thank past-you.

---

## Step 2 — Pick 5 targets (this week)

Not 50. Five. Local HVAC shops you can name, describe, and drive to if needed.

Selection criteria:

· Residential HVAC, 2–15 techs (small enough to move, big enough to lose real money)
· Owner-operated
· Has a website that clearly hasn't been touched in a while
· Answers less than 100% of calls — call them at 6pm and see
· Reachable — a phone number, a contact form, a real owner name

No agencies. No franchises. No commercial-only. No shops with a full-time marketing hire.

Write the list down in a file called pipeline.md. Columns: name, URL, phone, owner, why-them, status.

For public listing research, optionally run the small local Google Maps pass
in `docs/GOOGLE_MAPS_RESEARCH.md`. Check each candidate before adding it to
the five. Listed hours and reviews are research evidence, not proof of call
handling or revenue loss.

Also open `docs/VALIDATION_SCOREBOARD.md` and add these five as Batch 1, row
1-5. `pipeline.md` tracks each prospect's day-to-day state; the scoreboard
tracks the batch-level read (sold / conversations / replies) you'll need at
Step 6 to decide what Batch 2 changes, if anything.

---

## Step 3 — Run the audit, then do 20 minutes of manual work (this week)

Run leak-detector-audit on each of the 5.

Then — and this is the part most operators skip — open the output and do a real-world pass on the top opportunity. The audit gives you benchmark-driven dollar figures. Benchmarks are fine for a first pass, but sending an owner a proposal where 5 of 7 assumptions are labeled ASSUMED and ESTIMATED looks like a guess. It is a guess. Owners smell it.

20 minutes per prospect:

· Count their reviews on Google. Actual number.
· Record the Maps listing URL and observation date; resolve same-name matches
  by phone, website, and location. Check discrepancies with the company's site.
· Check the last review date. If the owner hasn't responded in 6 months, that's a KNOWN datapoint.
· Call them at 7pm. Does it ring out? Voicemail? Answering service? That's a KNOWN datapoint on after-hours capture.
· Look at their site on your phone. Does the phone number appear without scrolling? Does a booking button exist? KNOWN.
· Read their top-of-page. Do they say "24/7 service" and then not answer at 7pm? That's the wedge.

Then rebuild the metrics file with the real numbers you just observed:

```json
{
  "monthly_inbound_calls": 143,
  "missed_call_rate": 0.52,
  "average_service_ticket": 720
}
```

Re-run the audit with --metrics metrics.json. The top opportunity is now built from KNOWN data, not benchmarks. That proposal is credible.

This is the actual work. The pipeline produces a skeleton. You fill in the truth. That 20 minutes is what separates Leak Detector from every AI-audit tool that's ever been ignored by an HVAC owner.

---

## Step 4 — Send 5 proposals (this week)

Run leak-detector-propose on each of the 5 opportunities JSON files.

The client-facing file is what you send. Not the internal one. It has no IDs, no confidence floats, no schema keys. Just the headline, the three tiers, and one next step.

Delivery format: PDF if you can, email body if you can't. Owners don't open attachments from strangers. Paste the client view into the email body, with Good — Fix the Biggest Leak at the top, one number, one price.

Example subject: "You're losing about $9,400/mo on missed calls"

Example first line: "I noticed you say 24/7 service on your site. I called last Tuesday at 6:45pm and it rang out. Here's what that's costing you."

Then attach or link the proposal. Then stop typing and hit send.

---

## Step 5 — Have 5 conversations (next 2 weeks)

Expect replies. Expect "how did you find that" and "who are you" and "how much again."

You are not selling marketing. You are not selling AI. You are reading back a number the owner already suspected and never had written down.

Some will ask for the free scan first. Send it — the free scan is the audit minus the dollars. Then, after they see the leaks, the paid audit is a formality.

Some will sign the $997 Good tier immediately. Take it. That is Business Milestone #1.

Some will ask "can you just do the whole thing?" Send them Better. That is the retainer track.

Some will ghost. Follow up once at 4 days, once at 11 days, then move on.

---

## Step 6 — Measure (end of week 3)

After 5 proposals, you know one of three things:

A. Two or three sold. You have a business. Move to delivery. Fix the #1 leak for the first client using the missed-call playbook. Bill the $997. Run `docs/MEASUREMENT_PROTOCOL.md` — baseline, intervention, 30-day after, documented result. That measured number, not the pre-fix estimate, is your first case study.

B. Zero sold, but real conversations. The offer is close. Diagnose: was the number too small? The price too high? The proposal confusing? Adjust one variable. Run Batch 2 (see `docs/VALIDATION_SCOREBOARD.md`).

C. Zero replies. The targets were wrong, or the emails read like a robot wrote them, or the numbers didn't ring true. Diagnose. Pick 5 different targets. Do the 20-minute manual pass harder.

Either way — you will know something you do not know today. Write the read in `docs/VALIDATION_SCOREBOARD.md` before running the next batch.

---

## What You Do Not Do

· Do not touch leak_detector/orchestrator/, leak_detector/stages/, or the playbook boilerplate. That's v2 blueprint. It stays cold until delivery pain forces it hot.
· Do not add a dashboard, a CRM integration, a second vertical, or a billing system.
· Do not rewrite the worker adapters to use a different LLM.
· Do not refactor for elegance. The code is done. The math is testable. That is enough.
· Do not send the internal proposal view to a client. Ever. The guardrails will not save you from yourself if you paste the wrong file into an email.

---

## The Only Question That Matters Right Now

Can Leak Detector reliably identify a credible, evidence-backed revenue opportunity that a business owner would pay us to fix?

You cannot answer that by writing more code. You answer it by sending 5 proposals, watching what comes back, and reading the answer in the replies.

Next action, in order:

## 1. Pre-flight the MVP (30 min)
## 2. Write OPERATOR.md and pipeline.md (30 min)
## 3. Pick 5 targets (30 min)
## 4. Run audits, do the manual pass, re-run with real metrics (2 hours)
## 5. Send 5 proposals (1 hour)
## 6. Wait, follow up, close.

That's the plan. Everything after Step 6 depends on what those 5 conversations teach you.

When you get to delivery on the first paid client — the moment you need missed_call.py for real — that is when Track B thaws. Not before.
