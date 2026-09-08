# Decision 0032 — video-confirmed promotion and inducement transaction boundaries

Date: 2026-09-06

Amended: 2026-09-08 after V01 comparison and V03 pool reinspection.
The original pool-refund claim was incorrect; see
[the correction](../research/video-v01-opening-parameters-2026-09-08.md).

## Context

Fine inspection of user-supplied V03 around video `00:33:08–00:35:02` resolves two previously open transaction boundaries.

At 1Y Sep day 2:

- direct mail is selected before 10:00 without an immediate debit;
- cash is `7,430,572 yen` at 10:00 and `7,330,572 yen` at 10:02 when the direct-mail event notice appears;
- store popularity changes from `42 → 54` and `37 → 49`, while cleaning, security and service remain unchanged;
- entering company placement subtracts its `5,400,000 yen` aid, and cancellation restores it;
- entering pool placement subtracts its `1,800,000 yen` aid, then confirmation subtracts the `3,800,000 yen` site quote;
- V01 police-box placement independently shows `400,000 yen` aid followed by a `2,000,000 yen` site payment;
- the placement UI displays different site quotes as the target tile changes.

## Decision

1. Mark direct-mail cost, gain, trigger day/hour and payment-at-trigger timing as `CONFIRMED_VISUAL`.
2. Provide a composed direct-mail event path that records the promotion debit and applies popularity to the supplied owned-store set.
3. Continue rejecting composed payment for other promotion methods until their payment timing is directly observed or otherwise upgraded.
4. Model inducement placement entry as an aid debit/reservation and cancellation as an equal refund.
5. Store location-dependent site quotes as supplied observations only. Rename the misleading `displayed_total_yen` field to `displayed_site_cost_yen`.
6. Confirm the latest valid known quote with an additional debit and a terminal `CONFIRMED` state. Do not calculate site cost, decide affordability or schedule construction. A confirmed cash transaction does not mean construction is complete.

## Integrity boundary

The composed promotion path validates known payment timing and cost before mutating either popularity or cash. Inducement confirmation and cancellation are mutually exclusive and one-shot. Missing, unknown or unplaceable current quotes cannot debit cash, and an older valid quote cannot override a newer invalid one.

## Deferred

- site-price computation and generalization beyond observed facilities;
- insufficient-funds behavior and negative-cash consequences;
- construction delay and facility activation;
- payment timing for newspaper, airship, radio and TV.
