# Decision 0050: one-call representative-day validation loop

## Status
Accepted for the evidence-safe reference runtime.

## Context

The reference runtime now has all individual pieces needed for a closed validation loop:

- parameter-driven minimal store/day composition;
- autonomous representative-day execution;
- time-aligned store telemetry;
- factual day-metric reduction;
- sparse observed targets;
- coverage-aware adaptation from `GameplayObservationTimeline`.

Without a composition helper, callers still have to manually perform build -> run -> reduce -> compare and separately wire observation adaptation. That creates unnecessary opportunities to use mismatched runs/targets or bypass coverage semantics.

## Decision

Add `representative_day_validation.py` with:

- `validate_minimal_representative_day(config, observed)`:
  - build the configured minimal scenario;
  - run the representative day;
  - derive factual simulation metrics;
  - compare only supplied observation targets;
  - return the scenario, run, metrics and comparison together.

- `validate_minimal_day_from_observation_timeline(...)`:
  - reduce an annotated timeline using explicit day coverage and semantic mapping;
  - pass only the resulting safe full-day targets into the same validation path;
  - retain the observation-window reduction alongside the validation result.

## Evidence-safe boundary

This helper adds no simulation rule and no calibration algorithm. It does not:

- extrapolate partial footage;
- tune parameters automatically;
- choose arrival rates, purchase probabilities, staff priorities or timings;
- reinterpret ambiguous observation kinds;
- treat missing targets as zero.

## Consequence

The codebase now has one executable feedback-loop entry point from annotated first-title observations to autonomous-day differences. Future calibration can replace scenario parameters or add explicit fitting logic without duplicating runtime orchestration or weakening the observation-safety gates.
