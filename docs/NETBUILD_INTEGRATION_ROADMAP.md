# NetBuild.Pro Long-Term Integration Roadmap

**Status:** gated options, not authorization to build

**Reviewed:** 2026-09-28

**Owner:** NetBuild.Pro

**Launch system:** RRA MVP (`rra-mvp/`) and its Sizzle Sales Cockpit

## Purpose

This roadmap records which outside tools may become useful around the RRA
launch path, what evidence would justify adopting them, and what must remain
protected. It is not a sprint plan. The RRA commercial test remains the only
active priority until the first five real, client-facing proposals have been
sent and read against the validation gates.

## Locked operating model

NetBuild.Pro is the company and service brand. RRA is the narrow launch MVP;
Sizzle is its operator cockpit. The live path is:

`prospect → public research → human verification → scan → audit → guarded proposal → human sends`

The launch question is whether an owner-operated residential HVAC company will
pay $997 for one credible, evidence-backed fix. RRA's `scan`, `audit`,
`scoring`, `propose`, `client_facing_summary()`, and proposal guardrails are
load-bearing. Keep their behavior stable until the relevant gate below is
passed.

Non-negotiable controls:

- One highest-value leak leads each proposal; evidence and assumptions remain
  traceable.
- Client-facing output continues through `client_facing_summary()` and
  `guardrails.validate_proposal()`.
- Website observation is preparation, not proof. Only a human can promote an
  observation to verified evidence or decide what is safe to say.
- No tool may call, text, email, submit a lead form, book, send a proposal,
  collect payment, or deploy a client change without explicit operator action.
- The Sales Cockpit remains the operator surface. Integrations may sit beside
  it, but do not replace it or add a second CRM.
- Keep real prospect data, screenshots, and internal findings private. Do not
  commit them or publish them through Pages by default.
- Do not add a field, persistence model, backend, worker, or dependency to the
  launch path just to prepare for a possible later phase.

## Decision: integrate by evidence, not by calendar

The earlier day-by-day sequence would put Agency Agents and a new crawler ahead
of the proposal test. That conflicts with the launch gate. Replace it with the
following gate-based order; dates are deliberately omitted.

| Gate | Evidence required | Permitted integration work |
|---|---|---|
| **Now — SELL pending** | Five real proposals sent; outcomes accurately logged | Use existing RRA CLI, Sizzle, and browser observer. No new platform, crawler, persona framework, orchestration layer, or Batch 2 sourcing before the first-five read. Fix only a demonstrated launch blocker. |
| **SELL passed** | At least one paid engagement, or the scoreboard's explicit decision to test one isolated variable with a second five-prospect batch | For the paid engagement, select the actual delivery tool required by its agreed fix. Trial a single Agency Agents persona only if it measurably improves proposal clarity without bypassing guardrails. Compare a crawler only if the existing observer missed material evidence. |
| **PROVE passed** | Fix delivered profitably and recovered activity/revenue documented under `MEASUREMENT_PROTOCOL.md` | Standardize only the repeatable delivery step that caused real effort. Consider site-generation tools for a confirmed site/page fix; consider a PDF library only if the client deliverable actually needs PDF. |
| **REPEAT passed** | The offer, delivery, measurement, and margin repeat across multiple shops without reinvention | Evaluate workflow orchestration (Dify/Langflow) and broader agent patterns against a written cost, reliability, auditability, and human-approval case. No wholesale adoption. |

The five-proposal experiment can lead to one controlled second batch if the
scoreboard calls for it. That is still sales validation, not permission to
build a platform. Batch 2 should change one diagnosed variable only.

## Candidate disposition

### Near-term helpers already in the RRA operating lane

| Candidate | Decision | Boundary / trigger |
|---|---|---|
| **GoogleChrome/Lighthouse** | Use manually when useful; do not add it to RRA. | A performance/accessibility score is context, not proof of a revenue leak. Record the page, device/profile, date, and result. Do not convert a low score directly into lost-revenue dollars. |
| **Microsoft Playwright** | Keep using the existing `leak-detector-observe` implementation. | The repo already has a mobile browser observer that captures public-site findings as drafts and never submits forms or completes bookings. Do not add the pasted `prospect_check.py` as a second observer. Revisit only if the current observer demonstrably misses a required signal. |
| **gosom/google-maps-scraper** | Optional, low-volume sourcing tool outside the application. | Use only when the validation scoreboard authorizes a new batch. Keep raw CSV local; record query, date, and scraper version; verify identity/site/phone manually; do not bulk-import, enrich with private data, or infer owner size/revenue from a listing. Follow current Google terms and upstream project status before use. |

### Conditional delivery tools after a real paid engagement

| Candidate | Decision | Adoption trigger / control |
|---|---|---|
| **twilio/twilio-python** | Candidate for a narrowly scoped missed-call text-back fix. | Adopt only if a client pays for that exact fix. Test on a controlled number first; get client approval for message content, consent, routing, and recurring cost. Do not build a generic communications service. |
| **Cal.com / Cal.diy** | Do not select Cal.diy as a production dependency. | Cal.com announced a move to closed source in April 2026; its public Cal.diy edition is community-maintained and labeled for personal, non-production use. At delivery time, compare the commercial hosted service with other booking options against the client's actual need, support, terms, and total cost. |
| **Kozea/WeasyPrint** | Candidate only for a paid report requirement. | Use only if an actual client deliverable needs rendered PDF and the current Markdown/client-safe output is insufficient. Check deployment dependencies and test rendering with the real template before committing. |

### Post-validation options, not launch dependencies

| Candidate | Decision | Reconsider when |
|---|---|---|
| **msitarzewski/agency-agents** | Borrow narrowly scoped prompt/persona patterns; do not install a framework into RRA now. | A repeatable bottleneck is specifically research depth, copy clarity, or review effort. Any generated client language remains a draft and passes the existing deterministic guardrails plus human review. Store only versioned, NetBuild-specific adaptations if a trial proves useful. |
| **Firecrawl / Crawl4AI** | Do not replace the existing scan or observer now; they are overlapping alternatives, not a combined stack. | A measured sample shows the current observer misses material pages/signals often enough to weaken evidence or consume excessive operator time. Benchmark one candidate against the same pages, record false positives/negatives, privacy, cost, terms, and self-hosting burden; adopt at most one. |
| **Vercel v0 / Bolt.new** | Delivery-stage prototyping only. | A paid, scoped fix actually requires a new page or component. Generated code is a draft; review accessibility, security, responsive behavior, ownership, deployment, and ongoing costs before release. Keep it outside the RRA sales path. |
| **Dify / Langflow** | No orchestration layer before Repeat. | A documented repeated manual handoff creates measurable errors or hours of avoidable work. Trial one tool in a private sandbox; preserve explicit approval gates and RRA's existing CLI/core as the source of truth. Do not introduce shared `localStorage` as an integration contract. |
| **JackInSightsV2/Automated-Agentic-AI-Web-Agency** | Reference material only; no wholesale adoption. | Repeat has passed and a specific discovery, build, or deployment bottleneck is evidenced. Revalidate repository maintenance, security, dependencies, and license before borrowing any component. |
| **AutoGPT-style orchestration** | Deprioritize. | Only revisit if a concrete repeatability failure remains after a simpler, auditable workflow trial. |
| **Webstudio** | Deprioritize. | Only revisit if paid delivery requires a visual site builder and v0/Bolt or the existing NetBuild process is inadequate. |
| **listmonk / Chatwoot** | Keep out of launch. | Consider only after an explicit, consent-based client communications service is sold and supported. Neither is justified for five-prospect outbound or the current $997 validation. |

Repository activity is a point-in-time signal, not a security or quality
endorsement. Recheck latest commit/release, supported versions, open security
issues, license, terms, and maintenance model immediately before adopting any
candidate. In particular, a recent commit does not establish production
readiness.

## Integration contract if a candidate earns a trial

1. **Isolate it.** Start as an operator-run command or local adapter outside
   `scan.py`, `audit.py`, `scoring.py`, and `propose.py`; no shared runtime
   dependency until the trial passes.
2. **Use existing formats.** Read current CLI outputs and the existing
   observation/evidence structures. Do not create a competing prospect record
   or a second truth system.
3. **Label uncertainty.** Tool output is a candidate observation with source,
   URL, timestamp, and method. It cannot set `KNOWN`, complete a Truth Pass,
   or supply measured revenue by itself.
4. **Keep client output guarded.** Any generated proposal content is
   non-authoritative draft text. The canonical proposal builder and guardrails
   remain mandatory.
5. **Require a before/after test.** Use the same prospect/sample and compare
   evidence accuracy, false positives, operator minutes, total cost, and
   failure rate. Keep the dependency only if it improves a gate-relevant
   metric.
6. **Keep a rollback path.** The existing RRA CLI and manual operator path
   must continue to work if the integration is removed or unavailable.

## Decision record and review cadence

For each proposed adoption, append a short record here with: gate passed,
observed problem, candidate/version/license, controlled test, costs, accuracy
change, operator-time change, privacy/security review, owner decision, and
rollback plan. Review the candidate list only when a gate is passed or a paid
client creates a specific delivery need. Until then, the next action remains
the current RRA proposal test, not integration work.

## Sources

- RRA launch state and constraints: `README.md`, `OPERATOR.md`,
  `docs/LAUNCH_PLAN.md`, `docs/SALES_PLAYBOOK.md`,
  `docs/VALIDATION_SCOREBOARD.md`, `docs/MEASUREMENT_PROTOCOL.md`.
- Existing observation boundary: `OPERATOR.md` and
  `src/leak_detector/browser_scan.py`.
- Cal.com source-status announcement (2026-04-14):
  <https://cal.com/blog/cal-com-goes-closed-source-why>.
- Cal.diy production-use warning: <https://www.cal.diy/>.
