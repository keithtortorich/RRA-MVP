# NETBUILD.PRO Sizzle MVP

Sizzle is NETBUILD.PRO's lightweight operator cockpit for validating Revenue Recovery with independent residential HVAC contractors. It is not a CRM or backend platform.

**Validation question:** Can RRA acquire an HVAC customer, profitably deliver a $997 Revenue Recovery Sprint, and document recovered revenue?

**Gate:** five real proposals before platform expansion.

Target → Diagnose → Verify → Quantify → Contact → Sell → Baseline → Fix → Measure → Prove → Next Leak.

The entry offer is one leak, one fix, one fixed $997 price, and a 30-day measurement period. Automated scanner findings are `AUTOMATED_SIGNAL` until an operator verifies them. Modeled opportunity is never documented recovered revenue.

The canonical cockpit is `docs/index.html`. It stores data in browser `localStorage`; use JSON export/import to move or back up records.

## Verification

```bash
python -m pip install -e ".[dev]"
python -m pytest -q
python -m mypy src/rra
python -m ruff check --select E9,F63,F7,F82 src tests
npm ci
TZ=UTC npm test
TZ=Pacific/Auckland npm test
```
