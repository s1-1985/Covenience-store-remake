# Decision 0029: checkout duration policy seam

## Context

The first-title evidence supports a strong dependence of checkout speed on staff register ability and also confirms at least one two-staff register variant. Exact duration, scaling, rounding, interruption behavior and two-person cooperation are still unresolved.

The runtime already separates customer selection/service start from explicit service completion, so measured video timings need a place to enter without collapsing that boundary.

## Decision

1. Add `CheckoutServiceTimingCoordinator` as a separate timing layer.
2. Register an already-started checkout service with its explicit game-minute start time.
3. Expose timing context containing elapsed game minutes, staff register skill and checkout simultaneous-staff capacity.
4. Delegate required duration to a replaceable `CheckoutServiceDurationPolicy`.
5. `None` means duration remains unknown; service stays active.
6. Complete and settle the sale only when an explicit recovered/measured duration is reached.
7. Reject negative duration values, future start times and stale/non-active service registrations.

## Not decided

- register skill -> duration formula
- duration rounding/granularity
- two-person cooperation formula
- stamina interruption or abandonment interaction
- whether service time depends on basket size/product types
- platform/revision differences

These remain future video/guidebook-derived policy inputs.
