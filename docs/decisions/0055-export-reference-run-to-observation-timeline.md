# Decision 0055 — Export reference runs into the observation timeline vocabulary

## Decision

A completed representative-day reference run may be projected into `GameplayObservationTimeline` using only events already present in `StoreStepResult` and its aligned telemetry snapshots.

The exporter can emit:

- admitted customer → `CUSTOMER_ARRIVAL`;
- customer transition to checkout wait → `CHECKOUT_QUEUE_ENTER`;
- checkout service start → `CHECKOUT_SERVICE_START`;
- triggered checkout anger → `CHECKOUT_ANGER`;
- checkout service completion → `CHECKOUT_SERVICE_END`;
- replenish/clean assignment and completion → corresponding work start/end events;
- optional end-of-step stamina snapshots;
- optional end-of-step game-clock samples.

This gives original-game annotations and reference-simulation output a shared event vocabulary and lets the same duration reducers operate on both.

## Timing boundary

Exported timestamps use the store-step's current game minute. Multiple events inside one store step may therefore share a timestamp. The exporter does not invent sub-minute order, wall-clock/video seconds, or a finer original-game clock.

The exporter preserves the known `StoreStepOrchestrator` event order within a shared timestamp where that order is needed to produce a deterministic timeline.

## Data boundary

Customer sessions may be consulted after the run to recover stable checkout fixture identity for a recorded queue-entry transition. This is historical identity metadata only; no missing gameplay event is reconstructed.

## Not decided here

This decision does **not** claim that:

- one reference step equals an original-engine tick;
- exported event timing has sub-minute precision;
- scenario policies reproduce original AI;
- a simulated event is automatically evidence about the original game;
- video seconds can be derived from game minutes.
