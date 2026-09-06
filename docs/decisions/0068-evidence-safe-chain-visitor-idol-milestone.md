# 0068 Evidence-safe chain visitor idol milestone

## Status
Accepted

## Context
First-title PS/SS research added in PR #174 records a chain-wide milestone event: every 10,000 cumulative visitors across all player stores, an idol one-day-owner event is scheduled for 00:00 on the day after the milestone notification. The event is free, gives the same +100 popularity effect as TV promotion, and applies to all player stores present when the event fires.

The same research leaves several mechanics unresolved: whether merely crossing a threshold without observing the exact multiple must trigger, how multiple thresholds crossed in one interval are queued, how the representative-day/month-skip boundary maps to the next calendar day, and same-tick store-open/close ordering.

## Decision
Add a chain-level `ChainVisitorMilestoneRuntime` that:

- tracks cumulative visitor observations and the next 10,000-visitor threshold;
- schedules an event only when an exact threshold total is explicitly observed;
- records the confirmed free cost and +100 popularity payload;
- schedules the trigger as next absolute game day at 00:00;
- does not snapshot store IDs at reservation time, so callers can resolve current player stores at fire time;
- rejects threshold-skipping observations rather than inventing catch-up semantics.

The runtime deliberately uses a calendar-agnostic absolute `day_index`. This preserves the confirmed next-day boundary without inventing how day 4 -> month skip -> next month is represented internally.

## Consequences
The milestone scheduler can be connected later to the customer-entry telemetry and popularity runtime without changing its evidence boundary. New evidence can add crossing/catch-up semantics or calendar mapping without replacing the chain counter model.

## Unresolved
- threshold crossing without an exact 10,000 multiple observation;
- multiple milestone crossings in one update or month;
- exact integration with representative day 4 and month skip;
- same-tick ordering against store opening, closure, sale, or construction completion;
- whether temporarily closed stores receive the effect;
- PS/SS behavioral differences.

## Evidence
- `docs/research/` material merged by PR #174, first-title PS/SS promotion research only.
