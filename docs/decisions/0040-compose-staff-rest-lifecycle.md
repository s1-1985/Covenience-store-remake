# Decision 0040 — Compose staff rest lifecycle without rate constants

Date: 2026-09-06

## Context

Decision 0007 already models the confirmed first-title stamina state machine:

`AVAILABLE -> RETURNING_TO_BREAK_ROOM -> RESTING -> AVAILABLE`

but break-room arrival and stamina recovery still require direct caller calls. After the timed checkout and replenish/clean work lifecycles were composed into `StoreStepOrchestrator`, this explicit seam prevents a representative store day from progressing autonomously once a staff member reaches zero stamina.

The first-title evidence confirms the state order, but not the travel duration to the break room, recovery cadence, recovery amount, or the agility-to-double-recovery probability.

## Decision

Add `StaffRestTimingCoordinator` and optionally compose it into `StoreStepOrchestrator`.

The coordinator:

- timestamps `RETURNING_TO_BREAK_ROOM` and `RESTING` states in game minutes;
- exposes elapsed time, stamina values and the supplied break-room target to a replaceable transition policy;
- moves returning staff into `RESTING` only when the policy explicitly requests break-room arrival;
- applies only an explicit positive recovery amount while resting;
- removes the tracked lifecycle only after the existing roster state machine reports full recovery;
- preserves `None`/unknown stamina values rather than inventing them.

If a replenish/clean completion consumes the final stamina point during a store step, the new returning state is registered at the end of that step but is not advanced to break-room arrival in the same step. This avoids an implicit zero-time travel assumption.

## Evidence-safe boundary

This change does **not** define:

- travel time or movement speed to the break room;
- a default recovery interval or recovery amount;
- the agility probability for recovering 2 instead of 1;
- checkout stamina cost;
- whether work may be interrupted before a completion event;
- exact staff sprite/pathing behavior while returning or resting;
- any production-game tick-to-game-minute ratio.

All such values remain policy/data inputs until stronger first-title evidence is available.

## Consequence

A policy-driven store step can now carry a staff member from a zero-stamina work completion through return, rest and full recovery without external mutation calls, while retaining the original unknown numeric rules as explicit seams.
