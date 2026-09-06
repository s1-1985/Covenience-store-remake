# Decision 0044: parameter-driven minimal representative-day scenario

## Status
Accepted for the evidence-safe reference runtime.

## Context

The reference runtime now contains independently testable layers for customer demand, purchase choice, traffic, checkout timing, staff task selection, replenishment/cleaning timing, stamina return/rest, day running, and telemetry. The next milestone requires those layers to be runnable as one store/day without manual event injection.

The first-title formulas that would normally choose arrival rates, purchase preferences, staff priorities, work durations, stamina costs and recovery timing are still unresolved. Wiring the runtime together must not silently promote convenient test constants into original-game rules.

## Decision

Add a parameter-driven minimal scenario composition root with:

- one explicitly configured merchandise fixture;
- one explicitly configured staffed checkout;
- one explicitly configured staff member;
- one product/inventory slot;
- an explicit one-day customer schedule;
- deterministic scenario policies for purchase choice, staff task ordering, checkout selection, checkout/work timing, stamina effects and rest transitions;
- the existing `RepresentativeDayRunner` and factual telemetry recorder.

All gameplay-sensitive numeric values are supplied through scenario configuration. The deterministic policies are integration/test policies only and are named/documented as such.

The scenario schedule emits each configured customer at most once. If store-step cadence is coarser than the configured arrival minute, admission occurs at the first policy evaluation after that minute; no hidden sub-step simulation is invented.

## Evidence-safe boundary

This change does **not** claim that the first title used:

- FIFO checkout service;
- the configured staff task order;
- fixed checkout/work durations;
- fixed stamina costs or recovery intervals;
- the synthetic one-shelf layout used by tests;
- the test product prices, capacities or procurement costs;
- any particular customer arrival interval.

Those values remain replaceable inputs until stronger first-title evidence is recovered.

## Consequence

The compatibility core can now execute a fully composed representative day and produce time-aligned telemetry without a caller manually invoking each customer/staff transaction. This provides the integration surface needed to substitute V01/V02/V03 observations or later guide-derived parameters one field at a time.
