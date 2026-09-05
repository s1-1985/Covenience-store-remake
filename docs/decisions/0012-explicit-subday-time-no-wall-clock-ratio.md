# Decision 0012 — sub-day time is explicit; video seconds are not an engine constant

Date: 2026-09-05

## Context

User-provided first-title gameplay video provides a visible 24-hour in-game clock. One continuous observed segment advances approximately `13:16 -> 13:24 -> 13:32 -> 13:40` over successive one-second video samples, suggesting about eight in-game minutes per video second in that local segment.

That observation is valuable for measurement, but it does **not** prove a universal engine ratio. Playback/simulation speed, menus, pausing and capture conditions can change the apparent relationship.

The first-title research also supports configurable opening hours, including very short midnight operation in strategy discussion, but the exact salary prorating and demand formulas for shortened hours remain unresolved.

## Decision

Add an engine-independent sub-day clock that advances only by explicit **in-game minutes**.

Add an operating-hours interval model that supports:

- ordinary same-day windows;
- overnight windows;
- explicit 24-hour operation;
- closed/empty intervals.

Do not encode `video seconds -> game minutes` as a constant.

## Consequences

This gives later systems a stable time coordinate for:

- replaying measured video observations;
- customer-arrival samples;
- checkout/service duration samples;
- store open/closed gating;
- labor/maintenance experiments;
- midnight/day-boundary behavior.

The following remain unknown and outside this layer:

- real-time/video-time speed ratio;
- customer spawn rate by game minute;
- checkout duration formula;
- staff stamina drain rate;
- salary prorating by opening hours;
- exact month-end aggregation.

The uploaded video's local ~8 game-minutes/video-second segment remains an observation anchor only, not a production constant.
