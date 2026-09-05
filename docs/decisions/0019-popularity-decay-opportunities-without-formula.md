# Decision 0019 — popularity decay is an explicit opportunity until the rating formula is recovered

Date: 2026-09-06

## Context

First-title evidence gives two useful structural facts without giving the numeric decay formula:

1. A Saturn direct-play record says store popularity falls daily and relates that loss to the store evaluation/rating.
2. The first-title PS/SS FAQ says the skipped period after representative day 4 applies only one day-equivalent popularity loss, not one loss for every skipped calendar day.

Research basis:
- `docs/research/ss-parking-connectivity-and-popularity-decay-2026-09-06.md`
- `docs/research/month-skip-fire-grace-and-town-growth-2026-09-05.md`

The exact rating range, per-rating loss, timing, rounding and PS parity for the rating dependency are still unresolved.

## Decision

1. Keep popularity as an explicit `0..100` runtime value.
2. Store an optional rating snapshot separately; an unknown rating remains `None`.
3. Add `PopularityDecayOpportunity` instead of applying a guessed daily decrement.
4. Ordinary day processing can record one `ORDINARY_DAY` decay opportunity.
5. Month skip processing can record one `MONTH_SKIP` decay opportunity for the entire skipped period, matching the FAQ's one-day-equivalent rule.
6. Each opportunity captures the popularity and rating that existed when the decay became due.
7. A future recovered policy, direct video observation or explicit caller may resolve the opportunity by supplying the resulting popularity value.
8. Resolution cannot increase popularity and is rejected if another popularity-changing event has already invalidated the captured `before` value. Event ordering must be resolved explicitly rather than silently overwriting a newer value.

## Evidence boundary

The `MONTH_SKIP` application count is supported by first-title PS/SS FAQ evidence. The rating-dependent ordinary decay relationship is currently Saturn direct-play evidence and is not promoted to a universal PS/SS numeric formula.

## Explicitly unresolved

This decision does not choose:

- the rating display range,
- daily loss at each rating,
- whether higher rating always means smaller loss,
- whether any rating eliminates loss,
- exact midnight/event ordering,
- PS equality of the rating-dependent rule,
- whether promotion and decay on the same timestamp are ordered gain-first or decay-first,
- whether all popularity-loss causes share the month-skip exception.

Those remain replaceable policy/data inputs.
