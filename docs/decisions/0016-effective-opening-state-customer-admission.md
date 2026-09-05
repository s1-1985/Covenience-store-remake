# Decision 0016 — effective opening state gates autonomous customer admission

Date: 2026-09-06

## Context

The reference runtime already distinguishes ordinary opening hours from explicit temporary
closure. Its earlier `add_customer` API, however, could create a customer regardless of that
effective state. This is useful for replaying a directly observed video event, but it is unsafe as
the future demand generator's public entry point because a closed store could receive customers
or an unknown schedule could be treated as open by accident.

## Decision

`StoreRuntimeHarness.admit_customer` is the entry point for generated customer demand.

- Effective open state: create the customer and basket, returning `ADMITTED`.
- Effective closed state: return `STORE_CLOSED` without mutating customer or basket state.
- Unknown ordinary schedule: return `OPEN_STATE_UNKNOWN` without guessing open or closed.
- Explicit temporary closure overrides both 24-hour operation and an unknown ordinary schedule.

`StoreRuntimeHarness.add_customer` remains a deliberately lower-level injection hook. Observation
replay and controlled tests may use it when their source already establishes that the customer
was present. Its bypass behavior is documented rather than hidden.

## Evidence boundary

This gate composes already represented opening hours and temporary closure. It does not decide
customer arrival rates, customer-share coefficients, purchase intent or whether an original-game
edge case allowed entry at a particular animation frame. Those remain policy/evidence tasks.

## Consequences

- A future autonomous arrival policy has one mutation-safe admission boundary.
- Unknown opening hours cannot silently become an open store.
- Video replay remains possible without falsifying the source event.
- Opening/closing boundary behavior can be regression-tested independently of demand formulas.
