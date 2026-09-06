# 0071 Explicit compressed month-tail transition

## Context

First-title PS/SS research merged in PR #178 records that ordinary time progression runs through representative days 1..4 and day 5 through calendar month end is compressed into a transition to the next month. The same first-title evidence says popularity receives one day-equivalent decay across that compressed tail rather than one decay for every skipped calendar day.

The reference runtime already had two separate pieces of this behavior:

- `RepresentativeMonthRecorder` preserves day 1..4 and advances to the next month without synthesizing day 5+ finance.
- `StorePopularityRuntime.record_month_skip_decay()` records exactly one unresolved month-skip popularity decay opportunity.

What was missing was an explicit boundary event connecting a completed representative-month sample to the compressed month tail without implying that skipped days are ordinary ticks.

## Decision

Add `MonthTailTransitionRuntime` and `MonthTailTransition`.

A transition:

1. Requires a complete representative sample containing days 1, 2, 3, and 4.
2. Records one explicit transition for the completed year/month and its existing `MonthBoundary`.
3. Does not create day 5+ `DayEndResult` records or loop over calendar tail days.
4. Optionally records exactly one existing `MONTH_SKIP` popularity-decay opportunity for each explicitly supplied store.
5. Validates all popularity target IDs before recording any opportunity so a bad input cannot leave partial state.
6. Does not itself resolve the popularity loss amount.
7. Rejects recording the same month-tail transition twice.

## Evidence-safe boundary

This runtime does **not** decide or synthesize any of the following for the compressed interval:

- sales or customer counts,
- procurement, labor, maintenance, or other finance,
- staff task progress, stamina, or ability growth,
- cleanliness or security changes,
- customer-share recalculation,
- rival AI decisions,
- construction or town population progress,
- random/event draws,
- the numeric popularity decay formula,
- February/30-day/31-day differences,
- PS/SS implementation differences not directly observed.

Those effects must remain separate explicit inputs/policies until stronger first-title evidence exists.

## Consequences

The month model can now distinguish `active day 1..4` from `compressed month tail` in runtime state without pretending that the tail is a series of normal days. Future guidebook-derived aggregation rules can attach to this transition boundary instead of forcing changes into the representative-day recorder or calendar clock.
