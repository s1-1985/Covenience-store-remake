# Decision 0059: replay only explicit first-anger timing with caller-selected basis

## Context

The reference simulator now supports explicit checkout-pressure timing, a policy-driven anger trigger, source-video `CHECKOUT_ANGER` annotations, event-level comparison, observed arrival replay and observed checkout-duration replay. This makes it possible to hold observed upstream timing fixed while testing downstream queue and anger behavior.

The unresolved question is what elapsed-time dimension the original first title actually uses for anger. Current evidence can measure at least two factual candidates:

- checkout queue entry -> first anger;
- checkout service start -> first anger.

Choosing one automatically from sparse footage would prematurely assert the original patience rule. Partial clips can also show anger while the relevant timing anchor is outside the clip.

## Decision

Add an observation-backed anger replay layer with these rules:

1. Using an observed anchor->anger pair as a runtime trigger requires explicit `anger_pair_means_runtime_trigger=True`.
2. The caller must explicitly select `ObservedAngerBasis.QUEUE_ELAPSED` or `ObservedAngerBasis.SERVICE_ELAPSED`; the adapter never chooses the basis.
3. Pair only events inside one caller-supplied `ObservationDayCoverage`.
4. Queue-basis rules require explicit customer and fixture ids and use `CHECKOUT_QUEUE_ENTER -> first CHECKOUT_ANGER` elapsed game minutes.
5. Service-basis rules require explicit customer, staff and fixture ids and use `CHECKOUT_SERVICE_START -> first CHECKOUT_ANGER` elapsed game minutes.
6. Different observation/simulation ids may be normalized only through the existing one-to-one `ObservationIdentityMapping`.
7. The first matched anger event creates one trigger rule. Later anger events without a new explicit anchor remain unpaired and do not create repeated-trigger behavior.
8. Anchors without an in-window anger and anger events without an in-window anchor remain explicitly unpaired; no threshold is inferred.
9. `ObservedCheckoutAngerPolicy` returns `None` for customers/services with no explicit rule.
10. Queue-basis policy compares the recovered threshold with total checkout elapsed time. Service-basis policy compares it with current contiguous service elapsed time for the explicitly identified active staff member.
11. Existing `CheckoutAngerTimingCoordinator` semantics remain unchanged: a trigger request is consumed only when an active checkout staff member exists, because the recovered penalty consequence is staff-specific. A queue threshold reached before service therefore remains pending rather than assigning a guessed employee.

## Why

This lets an observed first-anger timing be replayed exactly as an experimental input while keeping the central model question — whether anger is driven by total checkout time or active service time — explicit and testable. Any mismatch caused by the existing staff-specific trigger boundary remains visible through event-level comparison instead of being hidden by a special case in the replay layer.

## Non-decisions

This does not define:

- which anger timing basis the original game uses;
- a global patience threshold;
- averaging or interpolation across customers;
- repeated anger behavior;
- anger while no staff member is active;
- abandonment/ejection rules;
- queue selection order;
- checkout duration formula;
- sub-minute timing;
- video-time to game-time conversion.
