# Leak Detector Sales Playbook

Status: launch-stage operating playbook. Adapted from the NetBuild.Pro lead-engine pattern to Leak Detector's existing `docs/LAUNCH_PLAN.md`. This document does not replace the launch plan. It turns it into a repeatable sales pull for the first five HVAC prospects.

## Mission

Get five evidence-backed Leak Detector proposals in front of five real residential HVAC owners, have five real conversations, and use the outcomes to decide what changes next.

The first launch is validation, not scale. Do not automate volume before the first five proposals teach us whether the wedge and offer sell.

## Offer

Leak Detector is not sold as marketing, AI, software, or a generic audit. Leak Detector identifies a specific revenue leak, documents the evidence, sizes the opportunity conservatively, and offers a fixed-fee way to fix the biggest leak first.

Commercial ladder for launch:

- Free scan: evidence and leak, no speculative revenue claim.
- $997 Good: fix the single biggest validated leak.
- Better: $5,000 setup + $2,500/month implementation when broader implementation is justified.
- Best: $7,500/month management/full-stack engagement when the owner explicitly wants the broader engagement.

No revenue share. No performance-only pricing. No attribution-based fee. Human approval remains required before client delivery or operational changes.

## 1. Target Pull

### Launch cohort

Exactly five prospects for the first cycle.

Target filter:

| Factor | Leak Detector launch criteria |
|---|---|
| Industry | Residential HVAC |
| Size | 2-15 technicians |
| Ownership | Owner-operated |
| Exclude | Franchises, agencies, commercial-only firms, firms with a full-time marketing hire |
| Website | Existing site with visible conversion/response weaknesses preferred |
| Reachability | Working phone/contact path and identifiable owner preferred |
| Revenue-leak signal | At least one observable issue worth manually validating |

Priority signals include missed/after-hours calls, no missed-call text-back, weak mobile booking, buried click-to-call, unanswered reviews, weak local visibility, and a mismatch between a stated service promise and observed customer experience.

Record each target in `pipeline.md`: name, URL, phone, owner, why-them, status.

### Sourcing

For the first five, manual Google Maps/search/referral sourcing is sufficient.
The optional local scraper pass in `docs/GOOGLE_MAPS_RESEARCH.md` can speed up
listing research, but every candidate still needs human qualification. Do not
buy a sourcing stack to avoid doing five manual selections. If the first cycle
validates the offer, NetBuild.Pro's vendor pattern can be reconsidered for scale.

## 2. Qualification and Priority

Leak Detector does not import NetBuild.Pro's AOKAI score. Leak Detector already has its own revenue-priority scoring after evidence collection.

Before audit, use a simple launch qualification gate:

1. Fits the HVAC launch cohort.
2. Has a reachable decision maker or credible route to one.
3. Has at least one observable public revenue-leak signal.
4. The signal can be manually verified without private-system access.
5. Leak Detector can plausibly offer a single operational fix if the evidence survives audit.

If any of 1, 3, or 4 fails, replace the prospect rather than forcing an audit.

After audit, rank by Leak Detector Revenue Priority Score and lead with the top evidence-backed opportunity.

## 3. Evidence Pull

For each prospect:

1. Run `leak-detector-audit`.
2. Open the internal output.
3. Spend approximately 20 minutes manually validating the top opportunity.
4. Convert observations into KNOWN metrics where possible.
5. Re-run with real metrics.
6. Run `leak-detector-propose` only after the evidence is credible.

Manual validation checklist:

- Google review count and last review date.
- Whether recent negative reviews are answered.
- Mobile click-to-call visibility.
- Booking/request-service friction.
- After-hours call handling when lawful and reasonable to test.
- Whether a stated 24/7/emergency promise matches observed handling.
- Any other public evidence directly supporting the top leak.

Never manufacture private operational numbers. Benchmarks and estimates must remain labeled as such.

## 4. Outreach Sequence

The first cycle is founder/human-led. The sequence borrows NetBuild.Pro's fail-safe follow-up discipline but is shortened to match Leak Detector's launch plan.

| Touch | Day | Channel | Purpose |
|---|---:|---|---|
| 1 | 0 | Email or direct message | Evidence hook + one quantified opportunity + Good-tier next step |
| 2 | 0-1 | Human call | Ask for a short conversation about the observed leak |
| 3 | 4 | Email | First follow-up; restate the evidence, not generic benefits |
| 4 | 11 | Email/call | Final launch follow-up |
| 5 | 30 | Optional re-engage | Only for prospects that said "not now" or showed real interest |

No automated cold voice/SMS campaign is part of the first-five protocol. Any future automated outbound must be separately approved and compliance-reviewed before use.

### First-touch formula

Subject: one concrete revenue leak or observed contradiction.

Opening structure:

1. State the observation.
2. State when/how it was observed.
3. Connect it to the conservative monthly opportunity estimate.
4. Offer the single biggest fix first.
5. Ask for a short conversation.

Example pattern:

`I noticed your site says 24/7 service, but the after-hours call path I tested did not reach a live response. Based on the assumptions in the attached breakdown, that leak could represent roughly $X/month. Leak Detector's first recommendation is one fix, not a marketing package: [fix]. The fixed-fee Good option is $997. Worth 10 minutes to walk through the evidence?`

Use the actual client-facing proposal output. Do not send internal IDs, confidence floats, raw worker output, or hidden assumptions.

## 5. Conversation Pull

The call is diagnostic, not a feature demo.

Opening questions:

- How are after-hours and missed calls handled today?
- Roughly how many inbound calls do you receive in a normal month?
- Do you know how many fail to become a live conversation?
- What is a normal service ticket worth?
- If this leak is real, is fixing it operationally useful right now?

Then reconcile the owner's numbers with the audit. If their real numbers materially change the opportunity, update the analysis rather than defending the estimate.

Close on the smallest credible next step: the Good tier when the top leak is validated. Move to Better or Best only when the owner asks for broader implementation and the evidence supports it.

## 6. Objection Handling

### "How did you get that number?"

Show the inputs. Separate KNOWN, ESTIMATED, and benchmark assumptions. Invite the owner to replace estimates with actual numbers and recalculate.

### "Is this marketing?"

No. The launch offer is to identify and fix a measurable revenue leak. Some later fixes may touch marketing, but the proposal leads with the operational leak Leak Detector actually found.

### "Is this AI?"

The implementation may use automation where appropriate. The sale is the recovered revenue opportunity and operational fix, not the technology.

### "Send me information."

Send the client-facing proposal or free scan and set a specific follow-up date. Do not send the internal audit.

### "Too expensive."

Return to the evidence and economics. Do not discount reflexively. If the validated opportunity is too small to justify $997, Leak Detector should not force the sale.

### "Not now."

Record the reason and re-engage in 30 days if appropriate.

### "No."

Record it, stop active outreach, and move on.

## 7. Pipeline States

Use only the states needed for the first validation cycle:

`TARGET -> AUDITED -> VERIFIED -> PROPOSAL_READY -> SENT -> CONVERSATION -> WON / LOST / NURTURE`

Minimum fields:

- Business name
- URL
- Owner/contact
- Phone/email
- Why selected
- Top leak
- Evidence status
- Estimated monthly opportunity
- Proposal price/tier
- Current state
- Last contact
- Next follow-up
- Outcome/reason

A spreadsheet or `pipeline.md` is sufficient. Do not build a CRM for five prospects.

## 8. Launch Metrics

These are observations, not promises or historical conversion claims.

Track:

- Targets selected: 5
- Audits completed
- Audits manually verified
- Proposals sent
- Replies
- Owner conversations
- Good/Better/Best offers discussed
- Sales
- Lost reasons
- Time from target selection to proposal

The launch decision is made after the five proposals:

### If 2-3 sell

Move into delivery. Execute the top leak fix for the first client, measure recovered calls/revenue over 30 days, and turn verified results into the first case study.

### If zero sell but there are real conversations

Change one variable only: targeting, evidence quality, wedge, price presentation, or proposal clarity. Run five more.

### If zero replies

Assume the targeting/message/evidence failed to earn attention. Change the targets, message, or numbers and run another five. Do not respond by adding product features.

## 9. Fail-Safe Rules

- Every SENT prospect must have a next-follow-up date.
- Follow up on Day 4 and Day 11 unless the prospect opts out or clearly declines.
- Every revenue claim must trace to evidence plus explicit assumptions.
- Client-facing material must pass Leak Detector guardrails.
- Never send the internal proposal/audit view.
- Do not request private system access during prospecting.
- Do not promise recovered revenue.
- Do not use revenue-share/performance pricing.
- Do not automate cold calling or SMS during the first-five validation cycle.
- Human review is mandatory before anything is sent.

## 10. What Stays Frozen

Until the first five-proposal cycle produces market evidence:

- No dashboard.
- No CRM integration.
- No billing system.
- No second vertical.
- No autonomous execution.
- No orchestrator expansion.
- No architecture refactor.
- No paid lead stack unless manual sourcing proves to be the actual bottleneck.

## Immediate Run Order

1. Verify the production MVP on `main`.
2. Select five HVAC targets and update `pipeline.md`.
3. Audit all five.
4. Manually verify the top leak for each.
5. Re-run with known metrics where available.
6. Generate and human-review five client-facing proposals.
7. Send all five.
8. Follow up Day 4 and Day 11.
9. Record conversations and sales outcomes.
10. Make the next product/sales decision from those five outcomes.
