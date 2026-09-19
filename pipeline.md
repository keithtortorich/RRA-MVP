# MVP Prospect Pipeline

Use exactly five qualified HVAC prospects for the first validation cycle.

Sourced from public business listings (BBB, LinkedIn, company sites) across
Fulshear, Celina, and Melissa, TX. Phone numbers recorded are ones each
business publicly advertises for contact — no private cell numbers.
See "Batch 1 research notes" below for what's confirmed vs. still needs the
20-minute manual pass (Step 3, `docs/LAUNCH_PLAN.md`).

| Business | URL | Phone | Owner | Why this prospect | Status | Last action | Next action | Follow-up date |
|---|---|---|---|---|---|---|---|---|
| Exodus Mechanical | exodusmechanical.com | 469-500-7977 (call/text) | Brian & Kristi | Owners explicitly advertise "call or text" on a mobile number — a direct SMS outreach route most of this list doesn't have. Site/reviews claim no after-hours charge + same-day guarantee, so the leak here is probably *not* missed-call capture — confirm which leak actually applies in the manual pass. | Researching | | Verify evidence | |
| Ample Services | amplehouston.com | 832-794-4878 | Robert Coufal (BBB-confirmed) | Claims 24/7 emergency service on-site — the classic "claims 24/7, does it hold up at 7pm" wedge is directly testable here. | Researching | | Verify evidence | |
| Bill Anderson Air | billandersonair.com | 281-769-9999 | Bill Anderson | Family-owned since 1998, posted hours Mon-Fri 8-4 only (no stated weekend/after-hours coverage) — after-hours/weekend capture is a plausible wedge, worth the 7pm test call. | Researching | | Verify evidence | |
| Castle Air Conditioning & Heating | castleacandheating.com | 713-667-7606 | Josh Cartwright (owner since 2014, per company site/LinkedIn) | Small, owner-operated, clearly a real local shop (not a franchise). Specific leak not yet identified — needs the manual pass same as any TARGET. | Researching | | Verify evidence | |
| Reed Heating and Air | **TBD — do not use any of the several similarly-named reed*.com domains found in search; confirm directly (call or Google Maps) before scanning** | 469-831-9842 | Eric Reed (BBB + LinkedIn confirmed) | Owner-operated, ~20+ years in business per BBB. Website search returned multiple unrelated "Reed" HVAC companies elsewhere in TX — do not guess which domain is theirs. | Researching | | Confirm website, then verify evidence | |

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

This research was done from an environment whose network egress is
allowlisted (it could not directly load any of these companies' sites to
quote exact on-page text or check for booking/chat/SMS widgets — only
search-engine-indexed summaries were reachable). Run `revenue-scan` /
`revenue-audit` against each confirmed URL from a normal internet
connection to get the actual site-signal scan, and do the phone-call and
on-page checks in Step 3 yourself — that's where ESTIMATED becomes KNOWN.

## Extended research record (fill in during Step 3, one per Batch 1 prospect)

The columns below are the fuller sales-ready record worth capturing per
prospect — beyond what fits in the pipeline table above. Leave a field
blank rather than guessing; blank means "not yet KNOWN," which is itself
useful information. `RRA score`/`Outreach priority` are your call once the
row is otherwise filled in — this repo doesn't compute them for you.

| Field | Exodus Mechanical | Ample Services | Bill Anderson Air | Castle A/C & Heating | Reed Heating and Air |
|---|---|---|---|---|---|
| City | Melissa | Fulshear | Fulshear/Katy | Fulshear | Melissa |
| Owner | Brian & Kristi | Robert Coufal | Bill Anderson | Josh Cartwright | Eric Reed |
| Public textable number | 469-500-7977 (explicit call/text) | not confirmed | not confirmed | not confirmed | not confirmed |
| Main business phone | 469-500-7977 | 832-794-4878 | 281-769-9999 | 713-667-7606 | 469-831-9842 |
| Website | exodusmechanical.com | amplehouston.com | billandersonair.com | castleacandheating.com | TBD — confirm before use |
| Google rating / review count | | | | | |
| 24/7 claim (exact wording, on-site) | reported: "never charges for after-hours" + "emergency service" (unverified on-site) | reported: "24/7 emergency HVAC service" (unverified on-site) | none found — hours posted Mon-Fri 8-4 | | |
| After-hours/emergency claim vs. 7pm test call | | | | | |
| Online booking | | | | | |
| Web chat | | | | | |
| SMS/text capability | yes — advertised directly | | | | |
| Apparent AI receptionist | | | | | |
| Company size (techs) | | | | | |
| Top observable leak | | | | | |
| Evidence | | | | | |
| RRA score | | | | | |
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
