# Decision 0037 — Compose optional checkout timing into store steps

Date: 2026-09-06

## Context

The reference simulator already had two separate pieces:

- `StoreStepOrchestrator`, which can advance game time, evaluate replaceable demand and purchase policies, move customers, select staff work, and start checkout service for a selected waiting customer;
- `CheckoutServiceTimingCoordinator`, which can track an already-started checkout service and complete it after a caller-supplied duration policy says enough in-game minutes have elapsed.

Because those pieces were not connected, a policy-driven store loop still needed an external caller to register every newly started checkout service and later call the timing coordinator. That manual seam prevented the composed loop from progressing through checkout settlement on its own even when an explicit duration policy was available.

The original register-skill-to-service-duration equation is still unresolved. This change must therefore compose the existing policy boundary without introducing a guessed duration.

## Decision

`StoreStepOrchestrator` may now receive both:

- a `CheckoutServiceTimingCoordinator` using the same `StoreRuntimeHarness`;
- a `CheckoutServiceDurationPolicy`.

They are an optional pair. Supplying only one is rejected.

When the pair is supplied, each store step now:

1. advances the explicit in-game clock;
2. evaluates checkout services already registered on earlier steps;
3. settles any service whose supplied duration policy is satisfied;
4. continues demand, traffic, purchase and staff-policy processing;
5. starts checkout service through the existing replaceable customer-selection policy;
6. automatically registers each newly started service at the current absolute game minute for evaluation on later steps.

If the timing pair is omitted, checkout completion remains explicit exactly as before.

## Evidence-safe boundary

This is orchestration only. It does **not** define:

- a register-skill duration formula;
- a default checkout duration;
- queue patience or abandonment timing;
- stamina loss during checkout;
- interruption or cancellation semantics;
- a wall-clock/video-time to game-time ratio.

A duration policy may return `None`; in that case the service remains active and no settlement is invented.

The timing evaluation result also uses the actual `CheckoutSaleCompletion` type returned by `StoreRuntimeHarness.finish_checkout_sale`, correcting the previous annotation mismatch without changing runtime behavior.

## Consequence

The headless compatibility core can now progress from an automatically selected waiting customer through elapsed-time checkout settlement without a manual finish call, provided the caller supplies an explicit duration policy. This moves the current milestone closer to a small store running a representative day autonomously while keeping the unresolved original timing formula outside the engine.
