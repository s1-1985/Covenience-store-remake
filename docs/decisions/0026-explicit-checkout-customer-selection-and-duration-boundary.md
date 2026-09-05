# Decision 0026 — Separate checkout customer selection from service duration

Date: 2026-09-06

## Decision

Do not keep staffed checkout as an indivisible immediate transaction in the autonomous path.

The reference simulation now separates:

1. selecting a currently waiting customer,
2. beginning service,
3. the unresolved passage of service time,
4. explicitly finishing service and settling the basket.

The existing immediate `complete_checkout_sale(...)` helper remains for deterministic observation/replay tests, but future autonomous behavior should use the split start/finish path.

## Customer selection

A checkout-assigned staff member receives a context containing:

- checkout fixture ID,
- current waiting customer IDs,
- active service count,
- simultaneous staff capacity.

A replaceable policy may choose any currently waiting customer or no customer.

The coordinator intentionally does **not** force FIFO. First-title FAQ evidence reports that checkout order is not strictly FIFO and later-arriving customers may sometimes be served first.

## Capacity

Physical simultaneous-staff capacity remains an enforced runtime constraint. If no service slot is free, no new service begins.

This is not a queue-priority decision.

## Service duration

Beginning service does not settle the basket or complete the customer lifecycle. Sale settlement happens only when `finish_checkout_sale(...)` is called explicitly.

This keeps the following unresolved rather than invented:

- checkout duration by staff register skill,
- effect of two-person registers,
- interruption by stamina depletion,
- task switches while serving,
- queue patience / abandonment during service,
- original update/tick cadence.

## Why this matters

Video analysis is expected to provide direct timing samples for checkout service. The split boundary allows those measured durations to be replayed or later turned into a recovered timing policy without rewriting cash settlement or customer lifecycle code.

## Still unresolved

- exact customer selection rule,
- whether any additional queue grouping exists,
- service time formula,
- two-person register algorithm,
- service interruption semantics,
- abandonment consequences,
- timing relationship between checkout completion and game clock ticks.
