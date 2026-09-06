# Decision 0041 — Run a representative day without evaluating next-day work before close

Date: 2026-09-06

## Context

The next large implementation milestone is one small store running one representative day through the composed demand, traffic, purchase, checkout, staff-work and rest layers.

`StoreStepOrchestrator.step(game_minutes)` intentionally advances the game clock before evaluating the policies in that step. Therefore an ordinary step from 23:50 by 10 game minutes would first move the clock to 00:00 and then evaluate demand, traffic and staff work at the next day's time. Closing the previous day's ledger after such a step would mix next-day activity into the previous day.

The first-title evidence does not justify changing the orchestrator's established ordering merely to support a day runner.

## Decision

Add `RepresentativeDayRunner` with a caller-supplied positive game-minute step cadence.

For each run it:

1. repeatedly invokes `StoreStepOrchestrator.step()` without allowing an ordinary step to cross midnight;
2. shortens the final ordinary step as needed so the runtime reaches exactly 23:59;
3. closes the current cash-ledger day at 23:59;
4. advances the runtime clock by one boundary-only game minute to 00:00 without evaluating demand/traffic/work policies;
5. advances the separate four-representative-day `SimulationClock` exactly once;
6. returns the individual step results, day-end result, boundary clock result and optional month boundary.

## Evidence-safe boundary

This runner does **not** define:

- a default store-step cadence;
- a video-second/game-minute ratio;
- day-end or month-end hidden costs;
- the four-day-to-month financial aggregation formula;
- autonomous values for demand, purchase choice, staff priority, work duration, checkout duration or rest recovery;
- month-start notification/report ordering;
- month-boundary bankruptcy settlement components.

Those remain in their existing policy/data layers.

## Consequence

The reference simulator can now execute a whole representative day as one operation while preserving a clean accounting/calendar boundary. The returned per-step history is suitable for later comparison against observed arrivals, queues, stamina, stock and cash without baking observation-derived coefficients into the runner itself.
