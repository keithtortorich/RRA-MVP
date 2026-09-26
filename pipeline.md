# MVP Prospect Pipeline

Use exactly five qualified HVAC prospects for the first validation cycle.

Sourced from public business listings (BBB, LinkedIn, company sites) across
Fulshear, Celina, and Melissa, TX. Phone numbers recorded are ones each
business publicly advertises for contact — no private cell numbers.
See "Batch 1 research notes" below for what's confirmed vs. still needs the
20-minute manual pass (Step 3, `docs/LAUNCH_PLAN.md`). Scan and audit
`reports/` paths mentioned below are local, gitignored outputs from the session
package; the committed browser observations are in `docs/observations/`.

| Business | URL | Phone | Owner | Why this prospect | Status | Last action | Next action | Follow-up date |
|---|---|---|---|---|---|---|---|---|
| Exodus Mechanical | exodusmechanical.com | 469-500-7977 (call/text) | Brian & Kristi | Owners explicitly advertise "call or text" on a mobile number — a direct SMS outreach route most of this list doesn't have. Site/reviews claim no after-hours charge + same-day guarantee, so the leak here is probably *not* missed-call capture — confirm which leak actually applies in the manual pass. | Researching | Scan + browser observation done 2026-09-26 (see `reports/`, `docs/observations/exodusmechanical-com.json`): site has financing + pricing info and a call/text CTA, but no online booking, no chat, no SMS link, weak above-fold CTA on 4/6 inner pages under 250 words. **GBP-verified 2026-09-26 via Google Maps scrape: 5.0★, 406 reviews** (own-site widget only shows 42 — likely a curated subset, not the real count). **Google Business Profile also lists hours as "Open 24 hours" every day** — if accurate, this likely rules out missed-call as the leak here; needs a direct check since GBP hours fields are often stale/default. | Cap'n: 20-min manual pass — verify the 24-hour claim with a real off-peak test call (this is now the key open question, not review count), then re-run `leak-detector-audit` with metrics.json | |
| Ample Services | amplehouston.com | 832-794-4878 | Robert Coufal (BBB-confirmed) | Claims 24/7 emergency service on-site — the classic "claims 24/7, does it hold up at 7pm" wedge is directly testable here. | Researching | Scan + browser observation done 2026-09-26 (see `docs/observations/amplehouston-com.json`): no online booking, no chat widget, no SMS option, no financing/pricing shown; phone is prominent and above-fold CTA is present. **GBP-verified 2026-09-26 via Google Maps scrape: 5.0★, 107 reviews** (listed as "Ample Services AC and Heating LLC"). | Cap'n: 20-min manual pass — the 24/7 claim is the wedge here; test a real after-hours call, then re-run audit with metrics.json | |
| Bill Anderson Air | billandersonair.com | 281-769-9999 | Bill Anderson | Family-owned since 1998, posted hours Mon-Fri 8-4 only (no stated weekend/after-hours coverage) — after-hours/weekend capture is a plausible wedge, worth the 7pm test call. | Researching | Scan + browser observation done 2026-09-26 (see `docs/observations/billandersonair-com.json`): confirmed on-site hours are Mon-Fri 8-4, closed Sat/Sun, no 24/7 claim anywhere. Also no chat, no online booking, no SMS, no financing/pricing guidance, phone NOT tappable above the fold on mobile, no clear CTA above the fold — the most signal-dense site of the four scanned. **GBP-verified 2026-09-26 via Google Maps scrape: 4.9★, 199 reviews.** Also found a real discrepancy: **their Google Business Profile lists Saturday hours as 8am-1pm (Sunday closed)**, contradicting the website's "Mon-Fri only, closed Sat/Sun." One of the two is wrong or stale — worth nailing down, and if the website is the stale one, that's a small conversion-friction finding on its own. | Cap'n: strongest automated-signal prospect of the four — 20-min manual pass to test what actually happens on a Sunday/evening call (voicemail? nothing? a competitor picks it up?) and resolve the Saturday-hours discrepancy, then re-run audit with metrics.json | |
| Castle Air Conditioning & Heating | castleacandheating.com | 713-667-7606 | Josh Cartwright (owner since 2014, per company site/LinkedIn) | Small, owner-operated, clearly a real local shop (not a franchise). Specific leak not yet identified — needs the manual pass same as any TARGET. | Researching | Scan + browser observation done 2026-09-26 (see `docs/observations/castleacandheating-com.json`): well-built site — has chat (Podium), online booking (HouseCallPro), financing, pricing guidance, prominent phone, clear CTA, no thin pages. **GBP-verified 2026-09-26 via Google Maps scrape: 4.9★, 201 reviews** (matches their own site's claimed 4.9★/200 almost exactly — this one's numbers check out). No 24/7 claim found; "Emergency AC Repair" offered as a category only. Automated scan found no clear opportunity — if this one holds a leak, it's likely something only the manual pass surfaces (response speed, review-response gaps, or a claim/reality mismatch), not a site-structure gap. | Cap'n: weakest automated signal of the four — decide after the manual pass whether this stays in Batch 1 or gets swapped for a bench candidate | |
| Reed Heating and Air | **Still unconfirmed after a second, deeper search pass 2026-09-26 — see note below. Recommend confirming by phone or Google Maps, or swapping in a bench candidate.** | 469-831-9842 | Eric Reed (BBB + LinkedIn confirmed) | Owner-operated, ~20+ years in business per BBB. Website search returned multiple unrelated "Reed" HVAC companies elsewhere in TX — do not guess which domain is theirs. | Researching | Re-searched 2026-09-26: BBB profile (Melissa, TX; phone and owner match) lists no working company site — only a dead third-party directory listing (Kompass, now 410). No Facebook/Instagram found under this business's own name in Melissa, TX (the "Reed Heating and Air" social profiles that do exist belong to unrelated companies in Moody, AL and elsewhere). Buzzfile lists the same phone number under a Garland, TX address instead of Melissa. **Third check, 2026-09-26: a direct Google Maps search for "Reed Heating and Air, Melissa, TX" returns no matching listing at all** — Google falls back to unrelated nearby HVAC businesses, and the one exact-name match it does surface ("Reed Heating & Air") is a different company entirely, in Oklahoma City with a 405 area code. Three independent checks now agree: this business has no public website and no discoverable Google Business Profile under its own name. That itself could be a strong lead (zero digital presence = high floor for missed calls) but can't be scanned/audited the normal way. | Cap'n: confirm by phone whether they have a site at all (unlikely at this point) or an unlisted GBP; if not, either audit them phone/manual-only or swap in a bench candidate (KMI A/C and Heating already has a confirmed website) | |

## Bench (Batch 2 candidates if a Batch 1 slot needs replacing)

Per the launch protocol: replace a LOST slot rather than forcing a weak
audit. These were sourced in the same pass but held back from Batch 1
because a field (owner name, phone, or website) wasn't yet confirmed, or to
avoid over-concentrating Batch 1 in one market.

| Business | Market | Phone | Owner | Website | Note |
|---|---|---|---|---|---|
| Chillzone Refrigeration & Air Conditioning | Fulshear | 832-599-0677 | Not yet identified | Not found yet | |
| Aba One Plumbing | Fulshear | 346-509-2900 | Not yet identified | Not confirmed | Plumbing-primary — confirm they also do residential HVAC before qualifying |
| KMI A/C and Heating | Celina | 972-382-1110 | Not yet identified | Confirmed | Website confirmed but owner not yet identified |
| T L Central Heating & Air | Celina | 972-382-2663 | Tim Looper (BBB-confirmed) | Not confirmed | |
| Blessed Air & Refrigeration Service | Celina | 972-382-2479 | Terry Dorris (owner) | Not found yet | |
| Air Rescue Heating & Cooling | Celina | 469-294-2616 | Not yet identified | Not confirmed | |
| Dyno Heating & Cooling | Melissa | 972-838-7075 | Marcus Stevenson (BBB-confirmed) | Not found yet | |
| Arrowhead Air Solutions | Melissa | 469-993-8283 | Randy S. Landers (owner/license holder) | Not found yet | |
| H2 Mechanical Services | Melissa | Still needed | Ryan (owner) | Not confirmed | Phone not yet identified — lowest-priority bench entry until found |

## Batch 1 research notes

Confirmed via public sources (BBB, LinkedIn, company websites) as of this
pass — treat as **ESTIMATED/reported, not KNOWN**, until verified directly
per the manual pass in `docs/LAUNCH_PLAN.md` Step 3:

- **Exodus Mechanical**: company site and aggregator reviews (Yelp, Houzz)
  state "never charges for after-hours service," offers "emergency service,"
  and a "guaranteed same-day service" option, and has been voted a
  "Neighborhood Favorite" 2021-2023. If accurate, the after-hours/missed-call
  wedge may not apply — the 7pm test call and a review-response check are
  the first things to verify here, not assume the standard playbook fits.
- **Ample Services**: claims "24/7 emergency HVAC service" and "15+ years"
  in business (amplehouston.com).
- **Bill Anderson Air**: posted business hours Mon-Fri 8am-4pm, closed
  weekends (per BBB/Yelp listings) — no after-hours claim found, which
  itself is a possible booking/contact-path signal to check on mobile.
- **Castle Air Conditioning & Heating**: owner-operated since 2014, no
  specific claims found yet to test against — needs the standard manual
  pass with no shortcuts.
- **Reed Heating and Air**: owner and ~20+ years in business confirmed via
  BBB and LinkedIn; website not confirmed — multiple unrelated Texas HVAC
  companies also use "Reed" in their name and domain, so do not assume any
  of them belong to Eric Reed's Melissa, TX business.

This initial pass was done from an environment whose network egress was
allowlisted (it could not directly load any of these companies' sites to
quote exact on-page text or check for booking/chat/SMS widgets — only
search-engine-indexed summaries were reachable).

**Update 2026-09-26:** `leak-detector-scan`, `leak-detector-audit`, and
`leak-detector-observe` (Playwright/Chromium) were all run from an
environment with full network access against the four confirmed URLs
(Exodus, Ample, Bill Anderson, Castle). Their on-site content, booking/chat/
SMS presence, and stated hours/claims are now directly observed — see the
per-prospect "Last action" notes above and `docs/observations/*.json` — not
just search-indexed summaries.

**Update 2026-09-26 (2):** Google Business Profile ratings/review counts for
all five prospects were pulled directly (`gosom/google-maps-scraper`, run
locally) rather than estimated from each business's own site or a
third-party aggregator — see the per-prospect rows above, all marked
"GBP-verified." This also gave a clean, independent confirmation that Reed
Heating and Air has no discoverable Google Business Profile under its own
name, and surfaced two things worth a direct call: Exodus's GBP lists
"Open 24 hours" every day, and Bill Anderson Air's GBP shows Saturday hours
its own website doesn't mention. What's still outstanding, and genuinely
needs a human: every live-call/form-submission check (after-hours handling,
7pm test call, missed-call behavior, and resolving the two hours
discrepancies above) — the tooling deliberately never contacts a business
itself. That's the actual remaining work in Step 3, and it's what turns
ESTIMATED into KNOWN.

## Extended research record (fill in during Step 3, one per Batch 1 prospect)

The columns below are the fuller sales-ready record worth capturing per
prospect — beyond what fits in the pipeline table above. Leave a field
blank rather than guessing; blank means "not yet KNOWN," which is itself
useful information. `Leak Detector score`/`Outreach priority` are your call once the
row is otherwise filled in — this repo doesn't compute them for you.

| Field | Exodus Mechanical | Ample Services | Bill Anderson Air | Castle A/C & Heating | Reed Heating and Air |
|---|---|---|---|---|---|
| City | Melissa | Fulshear | Fulshear/Katy | Fulshear | Melissa |
| Owner | Brian & Kristi | Robert Coufal | Bill Anderson | Josh Cartwright | Eric Reed |
| Public textable number | 469-500-7977 (explicit call/text) | not confirmed | not confirmed | not confirmed | not confirmed |
| Main business phone | 469-500-7977 | 832-794-4878 | 281-769-9999 | 713-667-7606 | 469-831-9842 |
| Website | exodusmechanical.com | amplehouston.com | billandersonair.com | castleacandheating.com | not found — see pipeline note above |
| Google rating / review count | **GBP-verified 2026-09-26 (Google Maps scrape, phone+website match confirmed): 5.0★, 406 reviews** — note this is far higher than the "42 rated reviews" shown on their own site widget; own-site widget likely only shows a curated subset | **GBP-verified 2026-09-26: 5.0★, 107 reviews** (listed as "Ample Services AC and Heating LLC") | **GBP-verified 2026-09-26: 4.9★, 199 reviews** | **GBP-verified 2026-09-26: 4.9★, 201 reviews** (matches their own site's claimed 4.9★/200 almost exactly) | **No Google Business Profile found under this name in Melissa, TX** (Google Maps scrape 2026-09-26) — search returned only unrelated fallback businesses; the one "Reed Heating & Air" match found is a different company in Oklahoma City (405 area code, unrelated phone/site). Third confirmation (after BBB/Kompass and Facebook/Buzzfile checks) that this business has no discoverable public web or GBP presence under its own name. |
| 24/7 claim (exact wording, on-site) | reported: "never charges for after-hours" + "emergency service" (unverified on-site). **Google Business Profile hours show "Open 24 hours" every day of the week** (GBP-verified 2026-09-26) — worth confirming this is accurate and not a default/misconfigured GBP field, since if true it likely rules out missed-call as the leak here | reported: "24/7 emergency HVAC service" (unverified on-site) | none found — hours posted Mon-Fri 8-4, closed Sat/Sun (confirmed on-site 2026-09-26). **Google Business Profile hours instead show Sat 8am-1pm open, Sun closed** (GBP-verified 2026-09-26) — a real discrepancy between the website and the Google listing; needs a direct call to find out which one is true, and if the website is stale that's itself a small conversion-friction finding | none found — "Emergency AC Repair" offered as a category, no 24/7 wording | unknown |
| After-hours/emergency claim vs. 7pm test call | not yet tested | not yet tested | not yet tested | not yet tested | unknown |
| Online booking | absent (browser-observed 2026-09-26) | absent (browser-observed 2026-09-26) | absent (browser-observed 2026-09-26) | present — HouseCallPro widget (browser-observed 2026-09-26) | unknown |
| Web chat | absent (browser-observed 2026-09-26) | absent (browser-observed 2026-09-26) | absent (browser-observed 2026-09-26) | present — Podium (browser-observed 2026-09-26) | unknown |
| SMS/text capability | yes — advertised directly | no sms: link found (browser-observed 2026-09-26) | no sms: link found (browser-observed 2026-09-26) | no sms: link found (browser-observed 2026-09-26) | unknown |
| Apparent AI receptionist | not observed | not observed | not observed | not observed | unknown |
| Company size (techs) | | | | | |
| Top observable leak (automated, pre-manual-pass) | none sized — fallback scan found no signals; browser observation shows weak above-fold CTA + 4/6 thin inner pages | HVAC-LEAK-002 booking friction, $2,178/mo est. (low confidence 0.22 — ESTIMATED benchmarks, no client metrics) | HVAC-LEAK-002 booking friction $2,178/mo + HVAC-LEAK-006 weak AI-search visibility $660/mo (low confidence — ESTIMATED benchmarks); most signal-dense site of the four, phone not tappable above fold on mobile | none sized — fallback scan found no signals; site is well-built (chat, booking, financing, pricing all present) | not yet scanned — no confirmed URL |
| Evidence | `reports/scans/exodusmechanical-com-2026-09-26.md`, `reports/audits/exodus-mechanical-*-2026-09-26.*`, `docs/observations/exodusmechanical-com.json` | `reports/scans/amplehouston-com-2026-09-26.md`, `reports/audits/ample-services-*-2026-09-26.*`, `docs/observations/amplehouston-com.json` | `reports/scans/billandersonair-com-2026-09-26.md`, `reports/audits/bill-anderson-air-*-2026-09-26.*`, `docs/observations/billandersonair-com.json` | `reports/scans/castleacandheating-com-2026-09-26.md`, `reports/audits/castle-air-conditioning-heating-*-2026-09-26.*`, `docs/observations/castleacandheating-com.json` | — |
| Leak Detector score | pending manual pass | pending manual pass | pending manual pass | pending manual pass | pending website confirmation |
| Outreach priority | | | | | |

## Allowed statuses

- Researching
- Evidence verified
- Audit complete
- Proposal sent
- Follow-up 1
- Follow-up 2
- Conversation
- Won
- Lost

## Qualification

- Residential HVAC
- 2–15 technicians
- Owner-operated
- Reachable owner or decision-maker
- Website or call handling shows a credible revenue leak
- No franchise
- No full-time internal marketing lead
- No commercial-only operator

## Follow-up rule

Follow up once on day 4 and once on day 11. Then close the prospect as lost unless the owner re-engages.
