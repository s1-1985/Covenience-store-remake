# Decision 0022 — store sales permits use an explicit remodel-bound runtime

Date: 2026-09-06

## Context

First-title research consistently identifies three independent regulated merchandise permits:

- tobacco;
- alcohol;
- medicine.

PS evidence shows the categories can differ in eligibility at the same site. SS direct-play evidence additionally states that changing/acquiring permits for an existing store is tied to the remodel flow rather than a standalone permit-only action.

The exact fees, exclusion distances and precise eligibility rules remain unresolved. The newly recovered SS note also does not prove whether the new-store flow can acquire the same permits, so the new-store trigger must not be silently enabled yet.

## Decision

1. Add `StorePermitRuntime` as per-store ownership state.
2. Keep permit categories independent; acquiring one never implies another.
3. Represent eligibility explicitly as `ELIGIBLE`, `INELIGIBLE` or `UNKNOWN`.
4. Allow acquisition through the currently evidenced `REMODEL` trigger.
5. Represent `NEW_STORE` as a known possible lifecycle location but return `TRIGGER_UNCONFIRMED` until first-title evidence confirms it.
6. Do not compute eligibility from distance, nearby competitors or permit type yet. A caller/replay/future policy supplies the eligibility result.
7. Add `FinancialEventKind.PERMIT` so permit spending is distinct in the cash ledger.
8. If the fee is known from the permit master or an explicit observation, debit that value.
9. If an observed acquisition is known to have happened while the fee remains unknown, record an unknown permit debit rather than zero; cash exactness therefore becomes false.
10. Do not implement permit cancellation until first-title evidence supports it.

## Consequence

Guidebook or video values for fees and eligibility can be inserted later without changing the store permit lifecycle. The runtime can already represent the observed PS case where tobacco/alcohol are available while medicine is blocked, and the SS remodel-only constraint, without importing sequel numeric data.

## Deferred

- exact tobacco/alcohol/medicine fees;
- exclusion distances and geometry;
- whether competitor stores or town facilities act as blockers;
- new-store acquisition path;
- cancellation/removal behavior;
- affordability behavior when a fee is unknown;
- platform/revision differences between PS and SS.

Later-series permit fees, distances and cancellation rules remain explicitly out of scope for the first-title baseline.
