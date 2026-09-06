# Decision 0032 — video-confirmed promotion and inducement transaction boundaries

Date: 2026-09-06

## Context

Fine inspection of user-supplied V03 around video `00:33:08–00:35:02` resolves two previously open transaction boundaries.

At 1Y Sep day 2:

- direct mail is selected before 10:00 without an immediate debit;
- cash is `7,430,572 yen` at 10:00 and `7,330,572 yen` at 10:02 when the direct-mail event notice appears;
- store popularity changes from `42 → 54` and `37 → 49`, while cleaning, security and service remain unchanged;
- entering company placement subtracts its `5,400,000 yen` aid, and cancellation restores it;
- entering pool placement independently subtracts its `1,800,000 yen` aid, and cancellation restores it;
- the placement UI displays different totals as the target tile changes.

## Decision

1. Mark direct-mail cost, gain, trigger day/hour and payment-at-trigger timing as `CONFIRMED_VISUAL`.
2. Provide a composed direct-mail event path that records the promotion debit and applies popularity to the supplied owned-store set.
3. Continue rejecting composed payment for other promotion methods until their payment timing is directly observed or otherwise upgraded.
4. Model inducement placement entry as an aid debit/reservation and cancellation as an equal refund.
5. Store location-dependent placement totals as supplied observations only.
6. Do not yet calculate land cost, enforce quote affordability, finalize a placement, or schedule construction. Those behaviors were not completed in the inspected sequence.

## Integrity boundary

The composed promotion path validates known payment timing and cost before mutating either popularity or cash. The inducement cancellation is one-shot. These guards prevent callers from converting an observation seam into guessed or repeatable money creation.

## Deferred

- successful inducement confirmation and the remaining debit;
- whether displayed placement total is exactly `aid + land` in every case;
- insufficient-funds behavior and negative-cash consequences;
- construction delay and facility activation;
- payment timing for newspaper, airship, radio and TV.
