# Decision 0018 — preserve the four representative day samples before month aggregation

Date: 2026-09-06

## Context

First-title evidence supports the following month structure:

- only day 1 through day 4 are normally simulated,
- the recovered composition is three weekdays plus one holiday,
- after day 4 the calendar advances to the next month,
- the monthly result is derived from the representative days,
- the exact aggregation/extrapolation formula and skipped-day finance remain unresolved.

Research basis:
- `docs/research/month-aggregation-current-rerelease-delta-2026-09-05.md`
- existing `SimulationClock` behavior and first-title month-skip research

The reference simulator already models the day 4 -> next-month boundary, but did not yet retain the four `DayEndResult` samples as one explicit month-level input object.

## Decision

1. Add `RepresentativeMonthRecorder` around the existing `SimulationClock`.
2. Each representative-day close stores the raw `DayEndResult` together with year/month/day and weekday/holiday classification.
3. Day 1 through day 3 return no month result.
4. Closing day 4 advances the calendar and returns a `RepresentativeMonthSample` containing the recorded raw days and `MonthBoundary`.
5. Do not average, multiply, weight, extrapolate or synthesize day 5+ values in this layer.
6. Mark a sample as complete only when the recorded day sequence is exactly `(1, 2, 3, 4)`.
7. If a recorder starts mid-month, retain only the available records and mark the boundary sample incomplete rather than inventing missing representative days.

## Consequence

The simulator now has a stable seam between:

`representative-day execution -> raw four-day sample -> future recovered month aggregation policy`

This allows video observations and guidebook formulas to be compared against exactly the same day-level inputs later. It also makes the unresolved formula explicit instead of burying an assumed multiplier inside the clock or economy ledger.

## Explicitly unresolved

This decision does not choose:

- the monthly sales/revenue multiplier,
- weekday/holiday weighting beyond preserving day type,
- skipped-day procurement/labor/maintenance handling,
- month-end rounding,
- month-end event ordering,
- bankruptcy evaluation at the month boundary,
- the interaction of a next-day 00:00 event scheduled after representative day 4.

Those remain separate research and implementation items.
