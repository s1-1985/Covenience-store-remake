# Decision 0060: compose observation-backed runtime inputs without promoting them to defaults

## Context

Three independent evidence-safe replay seams now exist for representative-day validation:

- explicit observed customer arrival minutes;
- explicit observed checkout service durations;
- explicit observed first-anger timing using a caller-selected elapsed-time basis.

Using these independently is useful, but downstream validation often needs several upstream timings held fixed at once. For example, queue behavior can only be isolated cleanly if both observed arrival cadence and observed checkout duration are replayed. Anger behavior can additionally hold the observed trigger threshold fixed.

These replay values are experimental inputs from one observation timeline. They must not silently become general first-title defaults or overwrite the scenario config's provenance values.

## Decision

Add a composed observation replay layer with these rules:

1. `ComposedObservationReplaySelection` explicitly chooses which replay seams are active.
2. At least one seam must be selected.
3. Arrival, checkout-duration and anger replay remain independently optional.
4. Anger replay mapping and `ObservedAngerBasis` must be supplied together.
5. Each selected seam delegates to its existing strict adapter and preserves that adapter's evidence rules.
6. Arrival replay may replace the scenario arrival tuple, but the original scenario object is not mutated.
7. Checkout-duration replay is passed as an explicit validation policy override; the config's synthetic `checkout_game_minutes` value remains unchanged.
8. Anger replay is passed as an explicit trigger policy; it is not stored as a recovered global threshold.
9. The same caller-supplied `ObservationIdentityMapping` is reused for checkout-duration, anger and final event comparison.
10. When arrival replay is active, customer-id mapping is rejected because arrival replay deliberately makes the observed customer id the runtime customer id. Staff and fixture mappings remain allowed.
11. The composed run still goes through the ordinary autonomous scenario, metric reduction, simulation observation export and event-level comparison.
12. `representative_day_validation` accepts an optional caller-supplied checkout-duration policy so observation replay can be injected before the run without changing the core scenario builder's default policy.

## Why

This creates a controlled validation mode where selected source-observed timings are held fixed and the remaining mechanics can be evaluated independently. Because every replay seam is explicit and optional, the system can progressively substitute recovered evidence without treating one video's timings as universal original-game constants.

## Non-decisions

This does not define:

- a production/original demand formula;
- default checkout duration;
- default patience or anger threshold;
- which anger timing basis is original;
- missing-observation imputation;
- customer identity inference;
- queue ordering;
- congestion reroute timing;
- purchase probabilities;
- staff task priorities;
- sub-minute timing or video/game-time conversion.
