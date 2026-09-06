# Decision 0057: replay explicit observed arrivals without fitting demand

## Context

The reference simulator can now export runtime events into `GameplayObservationTimeline` and compare them event-by-event with source-video annotations. A remaining validation problem is demand: if the simulator uses a synthetic or future recovered demand formula while checkout, congestion or anger behavior is being evaluated, upstream arrival differences can obscure whether the downstream model is correct.

The repository already supports deterministic scenario arrivals and a lower-level observed/manual arrival replayer, but the autonomous representative-day validation path did not yet accept a video observation timeline as the source of its arrival schedule.

A raw `CUSTOMER_ARRIVAL` annotation is not automatically equivalent to an engine demand event. Some annotations may describe a sighting or another researcher convention. Missing customers in a partial clip also cannot be reconstructed safely.

## Decision

Add an observation-arrival replay adapter with these boundaries:

1. Replaying `CUSTOMER_ARRIVAL` events as scenario demand intents requires explicit `customer_arrival_means_demand_intent=True`.
2. Only events inside caller-supplied `ObservationDayCoverage` are replayed.
3. Every replayed arrival must have an explicit customer id.
4. Customer ids must be unique inside the replay window; duplicate/missing ids are rejected rather than synthesized.
5. Observed game minute is copied exactly into `ScheduledScenarioCustomer`.
6. Applying a replay plan replaces the scenario's existing synthetic arrival tuple; it does not append to it.
7. Replay coverage must target the same representative year/month/day as the scenario config.
8. If an observed arrival precedes the configured simulation start, validation rejects the plan instead of silently dropping that arrival.
9. The resulting scenario still routes replayed arrivals through the normal store admission gate.
10. Purchase choice, checkout selection/timing, congestion, stamina, staff priorities, rest and anger remain caller-supplied scenario/policy behavior.

`validate_minimal_day_replaying_observed_arrivals()` composes arrival extraction, config replacement, the autonomous day run, simulation observation export, aggregate metric comparison and event-level comparison.

## Why

This allows downstream mechanics to be tested against the exact observed arrival cadence without inventing a demand distribution or fitting a spawn formula first. It also keeps partial-video limitations explicit: only annotated arrivals in the selected window are replayed.

## Non-decisions

This does not define:

- the original customer spawn/demand formula;
- missing arrivals outside or inside a partial clip;
- an arrival-rate extrapolation;
- customer archetype selection;
- purchase choice probabilities;
- checkout queue order;
- checkout duration;
- congestion reroute timing;
- patience/anger thresholds;
- video-time to game-time conversion.
