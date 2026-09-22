---
name: rra-phone-sales-launch
description: Run RRA's phone-sales-to-launch motion for HVAC prospects — verify leaks in Sizzle, cold call, close, and launch delivery. Use whenever Cap'n says "call my list," "who do I call today," "run phone sales," or is working the RRA Track 1 MVP sales motion (scan → verify → call → close → launch).
---

# RRA Phone Sales & Launch

> Imported from a claude.ai iPad session (2026-09-21 handoff) where it lived at
> `/mnt/skills/user/rra-phone-sales-launch/SKILL.md`, built with `playbook-builder`
> (see `playbook-builder.md` in this folder) from the real call script and the
> real repo. Two placeholders below are still open — flagged where they are,
> not blocking.

## Purpose
Convert Leak Detector output into paying, launched RRA clients over the phone, the same way every time, without re-explaining the process.

## When to use this
- Fresh Leak Detector / scan batch ready to work
- Time to call HVAC prospects from the pipeline
- A prospect said yes and needs to move into delivery ("launch")

## Inputs
- Leak Detector / `leak-detector-scan` output — HVAC companies with demonstrable revenue leaks. Repo: https://github.com/keithtortorich/rra-mvp
- `pipeline.md` — name, URL, phone, owner, why-them, status
- Sizzle tool (`docs/index.html` in rra-mvp) — per-prospect verification log: EXT-001 through EXT-015 checks, evidence, Minimum Truth Pass status

## Steps
1. **Scan.** Run Leak Detector (`leak-detector-scan` / `leak-detector-observe`) against target HVAC companies. Log to `pipeline.md`.
2. **Verify before calling — do not skip this.** In Sizzle, run checks against the prospect until the Minimum Truth Pass gate is satisfied (see Definition of done). Start with EXT-001/EXT-002 (after-hours call test, 24/7 claim test) — missed calls (HVAC-LEAK-001) is almost always the #1 leak. Call on a VERIFIED_FAILURE, never on an ASSUMED/ESTIMATED number alone.
3. **Open the call.** "Hey is this [boss]... you guys do ACs, yeah? ... After-hours emergencies? Replacements too?"
4. **State the specific verified leak.** "Well [boss], I was looking at your info and actually called last night and {nobody answered / got voicemail}." Or: "checked your site, didn't see financing." Or the specific leak Sizzle verified. Pivot: "Now the good news is I'm here to see if we can help you with that."
5. **Offer the free list first — don't lead with the card.** "So if it's ok I'll go ahead and send what I found poking around online... but if you want to get serious about plugging any gaps in the way you're doing it now, we could run through some quick questions and figure out how to make sure you're holding on to all that hard-earned money."
6. **If they opt into "get serious," walk the verified findings — don't run a fresh discovery script.** The "quick questions" are you presenting what Sizzle already confirmed (which EXT-checks came back VERIFIED_FAILURE), not open-ended needs-assessment.
7. **Justify the cost, then ask for the card.** "I'm sure you're already way busy, otherwise you would have fixed it. It's gotta be costing you [leak cost] a month — that's [leak cost × 12] a year. I'll take care of it for ya for a whole lot less than that." This line needs the leak's dollar figure already in hand from step 2/6, so run the numbers before you get here. Then: "Alright, if you'll tell me the card you want to use, I'll get started on that right away."
8. **Close outcome.** Good ($997) signs → delivery. "Do the whole thing" → pitch Better (retainer). No response → follow up once day 4, once day 11, then drop.
9. **Launch (post-sale).** Payment clears first, always. Then deliver per the matching appendix from the RRA build doc: A (missed calls / lead capture), B (booking friction), C (reputation). Configure → test → activate → measure 14–30 days → report recovered revenue.

## Decisions
- Verified high-value phone-check failure → HVAC-LEAK-001, use Appendix A.
- Verified top leak is booking/conversion → Appendix B. Reputation → Appendix C.
- Default is send-the-list-first, not card-first. Card only after they ask to "get serious."
- Never configure or activate anything before payment clears — non-negotiable (RRA guardrail §17.1/§17.3, invariant #2: no execution side-effect without approval).

## Definition of done

**Pre-call — Sizzle's own Minimum Truth Pass gate:**
1. ≥3 qualifying tests logged (determinate result + high-value check) — evidence: Sizzle's "Qualifying tests" counter shows 3/3 or higher.
2. Coverage across ≥2 channel families (e.g. PHONE + FORM) — evidence: Sizzle's "Channel families" counter shows 2/2 or higher.
3. Phone requirement satisfied (qualifying phone test run) if a public number is on file, or logged NOT_APPLICABLE with a reason.
4. Digital requirement satisfied (qualifying digital test run) if a public website is on file, or logged NOT_APPLICABLE with a reason.
5. No unresolved INCONCLUSIVE qualifying tests.
6. At least one VERIFIED_FAILURE exists. A clean pass-everything result means no wedge yet — don't call, find another prospect.

**Post-call:**
7. `pipeline.md` status updated same-day, not batched.
8. Payment confirmed received, evidenced by receipt/invoice, before any config or activation work starts.
9. [PLACEHOLDER: your own bar for what makes a call good vs. bad — not yet captured.]

## Edge cases
- [PLACEHOLDER: gatekeeper/receptionist answers instead of the owner]
- [PLACEHOLDER: no answer at all on the sales call itself]
- [PLACEHOLDER: owner pushes back or says no on the call]
- Documented: prospect ghosts after the list is sent → follow up day 4, day 11, then drop (RRA build doc).
