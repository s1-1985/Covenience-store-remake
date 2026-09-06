# Decision 0054 — Record checkout anger as an explicit observation event

## Decision

Add `CHECKOUT_ANGER` to the gameplay observation timeline. The event means the researcher explicitly identified a visible checkout-anger occurrence in the source; it is not inferred from elapsed time, queue length or register skill.

Two reducers may measure time to the first explicitly annotated anger event in a checkout lifecycle:

- queue entry → first anger, keyed by customer and checkout fixture;
- active service start → first anger, keyed by customer, serving staff and checkout fixture.

If the relevant start event or identity is absent, no measurement is produced.

The coverage-aware day adapter counts explicit checkout-anger observations inside every selected window. The count is promoted to the full-day `checkout_anger_events` comparison target only for exact 00:00–24:00 representative-day coverage. Partial clips retain only their window count.

## Why

The simulator can now emit checkout anger through a replaceable policy, but the observation schema previously had no direct way to record visible anger. Adding an explicit event lets future video analysis constrain the trigger using measured queue/service elapsed times without reverse-engineering anger from a guessed threshold.

## Not decided here

This decision does **not** define:

- what visual cue qualifies as anger for every source;
- a patience threshold;
- whether queue time, service time or total checkout time causes anger;
- whether one customer can become angry more than once during a checkout lifecycle;
- abandonment behavior;
- any employee penalty when the serving staff cannot be identified.
