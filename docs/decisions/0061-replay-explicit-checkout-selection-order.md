# Decision 0061: replay explicit checkout service-start order and earliest start time

## Context

The minimal autonomous scenario currently uses `FirstWaitingScenarioCheckoutPolicy`, a deterministic FIFO-like test policy. That policy is intentionally not an original-game claim: first-title evidence already shows that a later-arriving customer can be served before an earlier waiter.

`GameplayObservationTimeline` now records explicit `CHECKOUT_SERVICE_START` events with customer, staff, fixture and game time. Those events can therefore constrain which customer a cashier selects and when service may begin, without fitting a general checkout-order formula.

## Decision

Add an observation-backed checkout selection replay layer with these rules:

1. Using `CHECKOUT_SERVICE_START` observations as selection rules requires explicit `checkout_service_start_means_selection=True`.
2. Only service-start events inside caller-supplied `ObservationDayCoverage` become rules.
3. Each rule requires explicit customer, staff and fixture ids.
4. Different observed/runtime ids may be normalized only through the existing one-to-one `ObservationIdentityMapping`.
5. `CheckoutSelectionContext` exposes the current factual `minute_of_day` from the existing game clock; no wall-clock conversion is introduced.
6. Rules are replayed per staff/fixture in observed game-time and observation-sequence order.
7. The next observed customer is the only customer that may be selected for that staff/fixture.
8. A service may not start before its observed game minute.
9. If the expected observed customer is not waiting when the observed minute is reached, the rule remains pending. The policy does not skip to another waiter or infer a substitute.
10. Later observed rules are not consumed until earlier rules for that staff/fixture are fulfilled.
11. Once a rule selects its expected waiting customer, the normal checkout runtime starts service and existing timing/effects/anger layers continue unchanged.
12. Representative-day validation accepts an optional caller-supplied checkout-selection policy, and the composed observation replay can opt into this seam alongside arrivals, duration and anger.

## Why

This allows non-FIFO behavior seen in source footage to be reproduced directly as evidence while preserving any mismatch in customer arrival/pathing/staff readiness as a visible timing difference instead of hiding it behind a fallback selection.

## Non-decisions

This does not define:

- the original general checkout-order algorithm;
- FIFO or LIFO as a default;
- how a customer is chosen when no observed rule exists;
- a tolerance around observed start time;
- staff dispatch priority;
- queue patience/abandonment;
- checkout duration;
- sub-minute timing or video/game-time conversion.
