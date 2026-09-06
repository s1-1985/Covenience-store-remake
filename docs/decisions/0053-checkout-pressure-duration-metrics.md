# Decision 0053 — Compare explicit checkout pressure durations without inferring patience

## Decision

Expose three factual checkout-pressure duration maxima from autonomous representative-day runs when checkout anger timing is present:

- maximum pre-service checkout wait in game minutes;
- maximum active checkout-service elapsed time in game minutes;
- maximum total checkout elapsed time in game minutes.

If checkout timing observations are unavailable, these metrics remain `None` rather than becoming zero.

On the observation side, `GameplayObservationTimeline` reduces only explicit event pairs:

- `CHECKOUT_QUEUE_ENTER -> CHECKOUT_SERVICE_START` for pre-service wait;
- `CHECKOUT_SERVICE_START -> CHECKOUT_SERVICE_END` for active service duration;
- `CHECKOUT_QUEUE_ENTER -> CHECKOUT_SERVICE_END` for total checkout duration.

The day adapter pairs only events contained inside the selected coverage window. An event outside a video/observation window is never used to complete a duration whose other endpoint is inside the window.

Partial-window maxima are retained as factual window measurements but are promoted to `ObservedRepresentativeDayMetrics` only when coverage is exactly 00:00–24:00 for one representative day.

## Why

The reference runtime now exposes separate queue-wait and active-service timing, while the video-analysis schema already supports queue-enter, service-start and service-end annotations. These measurements can constrain future patience/anger hypotheses without choosing a trigger formula in advance.

## Not decided here

This decision does **not** define:

- a customer patience threshold;
- whether queue waiting contributes to anger;
- whether active checkout service alone contributes;
- any weighting between wait and service time;
- a conversion between video seconds and game minutes;
- behavior when an annotation endpoint is missing;
- an abandonment threshold or anger duration.
