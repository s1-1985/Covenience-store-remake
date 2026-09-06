# Decision 0072: Export checkout-associated break-room returns as a cause-neutral observation

## Status

Accepted.

## Context

First-title research supports at least two checkout-adjacent situations in which a staff member may head back toward the break room:

1. multiple staff react to the same checkout demand, one takes ownership, and another may return toward the break room;
2. a checkout-assigned staff member may return toward the break room before beginning service, with low stamina reported as a possible factor.

The reference runtime now represents both structures separately through checkout ownership conflict resolution and pre-service departure policies. A source-video observer, however, may be able to see only that a checkout-associated staff member returned toward the break room, not the exact internal cause.

Encoding the runtime cause into the observation kind would force video annotation to claim more than was directly observed.

## Decision

Add one observation kind:

`CHECKOUT_STAFF_RETURN_TO_BREAK_ROOM`

The simulation observation exporter emits this same kind when either:

- a resolved checkout ownership conflict explicitly gives a loser the `RETURN_TO_BREAK_ROOM` disposition; or
- a checkout pre-service departure evaluation explicitly reaches `DEPARTED`.

The observation carries the explicit staff id, checkout fixture id, and the current game-minute timestamp. The note may state the runtime source for debugging, but event matching does not use that note as a causal assertion.

Within a store step, checkout-associated return events are exported after staff-task assignment/work-interruption events and before checkout service-start events, matching the structural order already present in `StoreStepOrchestrator`. No sub-minute timestamp is invented.

## Consequences

- Video annotations can record the visible checkout-associated return without choosing an internal cause.
- Runtime runs produced by either supported mechanism compare in the same event vocabulary.
- Future replay adapters must require an explicit caller mapping when interpreting this cause-neutral observation as a particular runtime policy decision.
- Ownership-conflict loser actions other than return-to-break-room are not promoted to new video-observation events by this decision.

## Explicit non-decisions

This does **not** establish:

- the original checkout ownership winner formula;
- that every ownership-conflict loser returns to the break room;
- a stamina threshold for checkout departure;
- whether stamina is always involved;
- break-room travel or recovery duration;
- a customer-wait threshold for the transition;
- PS/SS equivalence;
- sub-minute ordering or video-time/game-time conversion.
