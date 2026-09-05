# Decision 0031 — guard explicit runtime transitions from silent overwrite and partial application

Date: 2026-09-06

## Context

Claude Code's reproduced known-issue sweep against main identified three state-integrity failures that do not require guessing any first-title formula, timing, price, or AI priority:

1. Starting checkout service could silently overwrite a staff member already assigned to replenishment or cleaning.
2. The same fired promotion event could be applied repeatedly.
3. A promotion targeting an unknown store could mutate earlier stores before raising, leaving a partial application.

These are runtime consistency defects rather than unresolved game-design questions. Existing policy seams already separate task selection from execution and promotion scheduling from event application, so silent reassignment or repeated/partial application violates those explicit boundaries.

## Decision

### Checkout service start

`CheckoutStationRuntime.begin_service(...)` may start service only when the staff member is idle, or already assigned to checkout with no conflicting checkout target.

If the staff member is replenishing, cleaning, resting, returning to the break room, or otherwise assigned, checkout start raises instead of reassigning them. Any future evidence-backed interruption/reprioritization behavior must occur through an explicit policy/transition before service start.

This does **not** assert that the original game never interrupts work for checkout. It only prevents the low-level checkout primitive from inventing that decision.

### Promotion application

A fired `ScheduledPromotion` is a one-shot event. Application records `applied=True`; a second application raises.

Before popularity is mutated, the complete deduplicated target-store list is validated. If any target is unknown, the operation raises with no popularity changes and the event remains unapplied.

This preserves the existing first-title evidence boundary: scheduling time, trigger time, popularity gain, and cap remain data-driven; payment timing and other unresolved semantics remain unchanged.

## Verification

Existing `reference_sim/tests/test_known_issues.py` already contains reproduced expected-failure tests for all three defects. This implementation is intended to flip those cases to unexpected-success/XPASS without modifying Claude-owned tests. Full repository CI remains the merge gate.

## Still unresolved

- whether and when original staff AI interrupts replenishment/cleaning for checkout;
- task reconsideration frequency and priority;
- promotion payment timing;
- exact eligibility/ownership snapshot timing for stores opened or closed around a promotion event;
- late scheduling behavior after a promotion trigger;
- notification/modal time-freeze behavior, which varies by observed event type.
