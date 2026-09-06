# Decision 0049: require coverage and semantic assertions before observations become full-day targets

## Status
Accepted for the evidence-safe reference runtime.

## Context

`GameplayObservationTimeline` stores direct annotated sightings from gameplay/video sources, while `ObservedRepresentativeDayMetrics` is designed for comparing a complete autonomous representative day against sparse observed targets.

A timeline may cover only a short video segment. It is also not always valid to equate a generic `CUSTOMER_ARRIVAL` annotation with successful engine admission or a `CHECKOUT_SERVICE_END` annotation with a proven completed sale. Promoting those counts automatically would create false full-day targets.

## Decision

Add `ObservationDayMetricAdapter` with two explicit gates:

1. `ObservationDayCoverage` declares the representative year/month/day and observed minute window.
2. `ObservationDayMetricMapping` declares whether the researcher's annotation convention supports mapping:
   - `CUSTOMER_ARRIVAL` -> admitted arrival;
   - `CHECKOUT_SERVICE_END` -> completed checkout sale.

The adapter always returns factual window summaries:
- arrival count;
- checkout-service-end count;
- per-staff minimum observed stamina in the window.

Only when coverage is exactly 00:00–24:00 are values promoted to full-day comparison targets. Semantic event counts are promoted only when their mapping assertion is explicitly enabled. Full-day stamina minima are promoted because complete-day coverage makes the observed minimum directly comparable to the simulated full-day minimum.

Partial windows never populate full-day targets, even when semantic mapping flags are enabled.

Non-integral stamina observations are rejected instead of silently rounded.

## Evidence-safe boundary

This change does not infer:
- unobserved arrivals outside a captured window;
- checkout sales from queue/service annotations without an explicit mapping assertion;
- attempted demand from visible arrivals;
- revenue from checkout completion;
- queue peaks from incomplete queue events;
- full-day stamina minima from partial footage.

## Consequence

The separate video-analysis workflow can now annotate observations independently, then pass them into the codebase with explicit coverage metadata. Only observation sets that genuinely support a full-day comparison can influence the representative-day validation surface.
