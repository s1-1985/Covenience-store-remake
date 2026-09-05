# Decision 0016 — gameplay customer creation uses an explicit entry gate

Date: 2026-09-06

## Context

The reference simulation already distinguishes ordinary opening hours from explicit temporary closure. `StoreRuntimeHarness.store_open` therefore resolves to:

- `True` while effectively open,
- `False` while outside the ordinary schedule or temporarily closed,
- `None` when the ordinary opening schedule is unknown and no temporary closure overrides it.

The recovered first-title behavior requires opening/closing state to gate customer traffic, while the video-observation replay layer still needs a lower-level way to inject a customer when the observation itself proves that the customer was present.

## Decision

1. Add `StoreRuntimeHarness.admit_customer(...)` as the gameplay-facing customer-entry gate.
2. Admission succeeds only when effective `store_open is True`.
3. Effective closed state returns `STORE_CLOSED` and creates no customer or basket.
4. Unknown opening state returns `OPEN_STATE_UNKNOWN`; unknown is never silently treated as open.
5. Keep `add_customer(...)` as a lower-level observation/replay hook that bypasses the gate deliberately.
6. Do not add a demand formula, queue-spawn probability, weather multiplier, or customer-share conversion here.

## Consequence

Future autonomous demand/customer-spawn logic must call `admit_customer`, so ordinary closed hours and temporary closure share one explicit admission boundary. Observation replay remains able to inject directly from measured evidence without requiring an inferred opening schedule.

## Evidence boundary

This decision implements only the structural fact that a closed store does not accept gameplay-generated entrants. It does not infer:

- exact customer generation rate,
- customer-share-to-arrival conversion,
- whether customers already inside are forced out at closing time,
- door animation timing,
- entrance queue behavior at the exact opening instant.

Those remain separate research/implementation items.
