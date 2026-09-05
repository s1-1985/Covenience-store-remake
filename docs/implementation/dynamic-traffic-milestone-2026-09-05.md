# Dynamic traffic milestone — 2026-09-05

Implemented on top of the store-grid compatibility layer:

- unique dynamic-agent occupancy;
- point goals and fixture-interaction-edge goals;
- route planning that treats other agents as temporary obstacles;
- simultaneous destination contention detection;
- blocked/wait tick counters;
- configurable reroute-after-blockage experiments;
- explicit `UNREACHABLE` / `BLOCKED` / `MOVING` / `ARRIVED` states.

This is intentionally a **congestion experiment harness**, not a claim that the original game moved one half-tile per tick or used the same conflict policy.

The original values still needed before this can become faithful customer movement are:

- movement speed/timing;
- collision retry rules;
- reroute timing/trigger;
- per-entity priority rules;
- queue formation and abandonment;
- path preference when several equal routes exist.

The next safe layer after this is a minimal customer lifecycle built from observed states (enter -> approach merchandise -> checkout/leave) while keeping purchase-choice and impatience formulas pluggable/unknown.
