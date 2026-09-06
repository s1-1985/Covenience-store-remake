# Decision 0058: replay only explicitly paired checkout durations

## Context

Observed arrival replay lets downstream store behavior be tested against the exact customer-arrival cadence without fitting a demand formula. Checkout service duration is another unresolved upstream input: using one synthetic fixed duration can distort queue growth and anger even when the observed video already contains explicit service-start and service-end timestamps.

A partial clip can contain only one endpoint of a checkout service. Staff or fixture identity may also be missing. Filling those gaps with averages or treating missing identifiers as wildcards would invent evidence.

## Decision

Add an observation-backed checkout duration replay layer with these rules:

1. Using checkout start/end pairs as runtime duration requires explicit `checkout_service_pair_means_runtime_duration=True`.
2. Pair only `CHECKOUT_SERVICE_START` and `CHECKOUT_SERVICE_END` events inside one caller-supplied `ObservationDayCoverage`.
3. A replayable pair requires explicit customer, staff and fixture ids on both endpoints.
4. Different observation/simulation ids may be normalized only through the existing one-to-one `ObservationIdentityMapping`.
5. Service duration is the exact observed game-minute difference between the paired endpoints.
6. An end whose start lies outside the coverage window remains `unpaired_end`; no duration is inferred.
7. A start whose end lies outside the coverage window remains `unpaired_start`; no duration is inferred.
8. Duplicate starts without an in-window end for the same explicit identity are rejected.
9. Multiple observed pairs that normalize to the same runtime customer/staff/fixture key are rejected rather than averaged.
10. `ObservedCheckoutDurationPolicy` returns `None` for any runtime checkout service with no explicit observed rule.
11. The policy can replace the synthetic checkout-duration policy on the minimal autonomous scenario without changing the scenario config's recorded synthetic input.

## Why

This permits queue and anger validation to hold actual observed service times fixed while leaving unobserved services unresolved. It isolates downstream mechanics without prematurely fitting a register-skill timing formula or an average duration.

## Non-decisions

This does not define:

- a register-skill to duration formula;
- average or median imputation for missing service times;
- wildcard matching for unidentified staff or fixtures;
- sub-minute checkout timing;
- a video-time to game-time ratio;
- checkout queue selection order;
- patience/anger thresholds;
- checkout stamina cost.
