# Decision 0052 — Validate clustered checkout load with explicit scenario parameters

## Decision

The parameter-driven minimal representative-day scenario may optionally receive a `CheckoutAngerTriggerPolicy`. When supplied, the scenario creates and exposes the checkout-pressure timing and anger-penalty runtimes and runs them through the same `StoreStepOrchestrator` as demand, traffic, purchases, staff work, checkout timing, rest and telemetry.

Scenario-only anger policies may use explicit test thresholds such as active-service elapsed time or total checkout elapsed time. These values are validation inputs only and are not promoted to first-title rules.

Representative-day metrics now include `checkout_anger_events`, counted only from anger evaluations that actually triggered a staff-specific penalty event. The metric can be supplied sparsely on the observation side like the other day metrics.

## Why

A single-customer happy path does not exercise the original game's important competition for checkout capacity. Clustered arrivals are needed to validate queue growth, one-register throughput, ordering, checkout pressure and eventual anger hooks under a repeatable load.

## Evidence boundary

First-title/Saturn research supports that keeping customers waiting can provoke anger, while separate first-title dedicated research supports a -2 employee work-skill consequence. The exact patience threshold and the exact contribution of queue wait versus active register processing remain unresolved.

## Not decided here

This decision does **not** define:

- an original arrival burst distribution;
- an original FIFO queue rule;
- an original checkout duration;
- an original patience threshold;
- whether waiting and service elapsed time are weighted differently;
- abandonment after anger;
- queue geometry;
- a production tuning target for maximum queue length.
