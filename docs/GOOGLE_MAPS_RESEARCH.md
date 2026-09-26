# Google Maps Research for Leak Detector

Use this optional research pass to find and check **five** residential HVAC
prospects. It supplies public listing evidence to `pipeline.md`; it does not
run the audit, prove a missed call, or create a client-facing revenue claim.
The [gosom/google-maps-scraper](https://github.com/gosom/google-maps-scraper)
agent skill is a convenient way to run the pass locally. Keep the scraper and
its dependencies outside this MVP repository.

## Run a small local pass

On a machine with Node.js and Docker installed, install the upstream agent
skill in your agent environment (the skill is not a Leak Detector dependency):

```bash
npx skills add gosom/google-maps-scraper
```

Ask the agent:

> Find independent residential HVAC companies in Fulshear, Celina, and
> Melissa, Texas for a five-prospect Leak Detector validation batch. Run a
> small test first. Export local CSV with business name, category, address,
> public phone, website, Google Maps listing URL, rating, review count, and
> listed hours. Do not extract emails, use paid proxies, contact businesses,
> or send data to a lead service. Stop at enough candidates to select five.

The upstream skill guides the local Docker run and offers a no-proxy option.
If the skill is unavailable, use the upstream CLI directly. Put one search per
line in a local `queries.txt` and run from a working directory outside the
repository:

```text
residential HVAC in Fulshear TX
residential HVAC in Celina TX
residential HVAC in Melissa TX
```

```bash
mkdir -p gmaps-output
docker run --rm \
  -v gmaps-playwright-cache:/opt \
  -v "$PWD/queries.txt:/queries.txt:ro" \
  -v "$PWD/gmaps-output:/out" \
  gosom/google-maps-scraper \
  -input /queries.txt -results /out/results.csv \
  -depth 1 -exit-on-inactivity 3m
```

Keep the raw CSV local. Record the scraper/image version, query, and run date
with it so a changing review count can be traced to a specific observation.
The source project documents the Docker command and exported fields in its
[README](https://github.com/gosom/google-maps-scraper#quick-start).

## Turn results into candidates

1. Deduplicate by Maps listing URL, then by matching phone and website. A
   search result is a candidate, not a qualified prospect.
2. Check name, city, category, website, and public phone against the listing
   and the company's own site. Reject unrelated same-name businesses and
   franchises. Leave owner and technician count blank until independently
   established; Google Maps does not prove either.
3. Record listing URL, observation date, rating, review count, listed hours,
   and any website/Maps discrepancy in the `pipeline.md` research notes. Mark
   these **public listing observations**, not verified operating facts. A
   missing search result does not prove a business has no Google profile.
4. Select exactly five qualified targets. For each, run the existing site
   scan and browser observation. Compare Maps hours with the site and check
   review recency/owner response manually. Keep contradictory claims open
   until a human checks the actual customer path.
5. Complete the 20-minute manual pass in `LAUNCH_PLAN.md` Step 3. A real
   after-hours call, form, booking, or SMS test is performed by the operator,
   never by this scraper. No response rate, missed-call rate, monthly calls,
   average ticket, or recovered revenue comes from Maps data.

Only enter **KNOWN** values in `metrics.json` when their source actually
measures that field. Listing rating, review count, hours, and phone are useful
for qualification and contradiction checks; they cannot turn benchmark
revenue estimates into observed revenue. Re-run the audit with measured inputs
when available, and label all remaining assumptions ESTIMATED.

## Boundaries

- No bulk lead import, CRM, scheduled crawling, automatic outreach, or paid
  sourcing stack during the first-five validation cycle.
- Keep raw exports and internal notes local; put only reviewed evidence needed
  for a specific prospect in the pipeline or observation record. Review any
  public repository or Pages publication separately.
- Do not equate a scraper result with a Google endorsement, a live-business
  verification, or proof that a business answers its phone.
