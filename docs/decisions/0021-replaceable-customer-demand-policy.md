# Decision 0021 — customer demand uses a replaceable policy boundary

Date: 2026-09-06

## Context

The reference runtime now has an evidence-backed gameplay admission gate:

- open store -> customer may be created;
- ordinary closed hours / temporary closure -> reject;
- unknown opening schedule -> preserve unknown and reject;
- observation replay may still inject a customer directly when the source itself proves the customer was present.

What remains unresolved is the first-title demand equation itself: customer share, time of day, weather, nearby population, popularity, assortment, price, competition and other factors are known to matter, but their exact conversion into customer arrivals is not recovered.

Hard-coding a temporary spawn-rate formula here would contaminate later measurement from V01/V02/V03 and the guidebooks.

## Decision

1. Add a `CustomerDemandPolicy` protocol that receives an explicit runtime context and returns zero or more `CustomerArrivalIntent` values.
2. The context exposes only already-known state:
   - absolute game minute / minute of day / elapsed representative days;
   - effective open state;
   - currently known customer-share result;
   - the existing evidence-safe customer-share input snapshot.
3. Add `CustomerDemandCoordinator` to route every policy-generated intent through `StoreRuntimeHarness.admit_customer(...)`.
4. Do not let a demand policy bypass ordinary hours or temporary closure.
5. Do not automatically retry or queue a rejected demand intent. Retry semantics are themselves unresolved and belong to a future recovered policy.
6. Do not add a default first-title demand implementation until the original behavior is sufficiently measured.
7. Keep `ExplicitArrivalSchedule` / `ObservedArrivalReplayer` as the separate observation-replay path. Those components reproduce measured arrivals and are not gameplay demand AI.

## Consequence

The compatibility core can now run with a caller-supplied or future reconstructed demand policy without changing customer creation, opening-hours checks, baskets or downstream transaction bookkeeping.

This moves the project toward the milestone of one small store running a representative day autonomously while keeping the main unresolved equation outside the stable runtime core.

## Deferred

Still unresolved:

- share-percent -> arrival-rate conversion;
- time-of-day demand curve;
- weather multipliers;
- weekday vs holiday demand difference;
- popularity / service / cleaning contribution beyond the existing share-input model;
- customer demographic/type distribution;
- entrance retry/queue behavior while closed or blocked;
- exact policy evaluation cadence.

No coefficients or fallback rates are introduced by this decision.
