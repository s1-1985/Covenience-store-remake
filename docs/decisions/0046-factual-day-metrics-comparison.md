# Decision 0046: derive factual representative-day metrics before fitting rules

## Status
Accepted for the evidence-safe reference runtime.

## Context

The runtime can now execute one fully composed representative day and capture factual telemetry at the start, after each store step, at 23:59, and after the 00:00 boundary. The next validation step is to compare those runs with V01/V02/V03 or guide-derived observations.

A comparison layer must not turn missing observations into zeros, infer hidden arrival rates from one sample, or treat known-only cash as exact when unknown financial events exist.

## Decision

Add a reducer that derives only direct counters/extrema from one `RepresentativeDayRunResult`:

- arrival intents and admission outcomes;
- completed staffed-checkout sales;
- known staffed-checkout revenue and whether those settlements are exact;
- peak waiting customers and peak active checkout services;
- total customer sessions and selected terminal customer states;
- known cash delta plus exactness flag;
- day-ledger known credits/debits;
- per-staff observed minimum/ending stamina;
- ending inventory units/capacity.

Add an observation-side target object whose scalar fields default to `None`. Comparison emits a delta only for targets explicitly supplied by the researcher. Missing staff/slot identifiers produce `simulated_value=None` and `delta=None` rather than a fabricated zero.

## Evidence-safe boundary

This layer does not fit, infer, or tune:

- arrival rates;
- checkout patience or service-time formulas;
- staff stamina costs/recovery formulas;
- purchase probabilities;
- replenishment rules;
- customer-share coefficients;
- hidden financial aggregation.

It is a measurement/comparison surface only.

## Consequence

Video or guide observations can now be entered as sparse targets and compared against the autonomous-day output without changing runtime mechanics. This creates the executable feedback loop needed for later calibration while preserving unknowns.
