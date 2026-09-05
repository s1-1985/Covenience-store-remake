# Decision 0024 — caller-driven store step orchestrator

Date: 2026-09-06

## Decision

Add a thin `StoreStepOrchestrator` that composes already-recovered runtime layers without introducing new first-title formulas.

One explicit step performs:

1. caller-supplied in-game minute advancement,
2. optional customer-demand policy evaluation through the existing admission gate,
3. one customer traffic tick,
4. optional purchase-policy evaluation for customers that are physically at merchandise.

Checkout service, staff task selection/execution, queue patience, autonomous restocking and day-close/month-close remain outside this layer.

## Why

The reference core now contains independent evidence-safe seams for opening state, customer demand, movement, purchase choice, checkout, inventory, staff tasks, cash and representative-day/month boundaries. A composition seam is needed to exercise these together while preserving every unresolved timing and priority rule.

## Evidence boundary

This decision does **not** claim that the original 1997 PS/SS executable internally used this exact update order. It is an integration boundary for the remake/reference simulator.

The following remain unresolved and must not be inferred from this orchestrator:

- real-time seconds to in-game minutes,
- demand evaluation frequency,
- staff AI reconsideration frequency,
- checkout duration and queue ordering,
- purchase probabilities and quantities,
- autonomous replenishment thresholds,
- exact day-end event ordering.

Any recovered rule can later replace or wrap the corresponding seam without changing inventory, basket, cash or customer-state bookkeeping.
