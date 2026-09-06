# 0062 — Replay observed replenish/clean durations without inferring effects

## Decision

Explicit in-coverage `REPLENISH_START -> REPLENISH_END` and `CLEAN_START -> CLEAN_END` observation pairs may be replayed as per-staff/per-task work durations when the caller explicitly opts in.

The replay layer does **not** infer replenishment quantity, stamina cost, break-room target, task priority or task target from those duration observations. Completion payloads continue to come from the scenario's explicit inputs.

Repeated observed work by the same staff/task is replayed by chronological occurrence index. Partial pairs remain unresolved and are surfaced in the replay plan.

## Why

The video observation vocabulary already captures replenish/clean start and end events. Using those measured game-minute spans lets us remove one synthetic timing assumption while keeping unrelated unknowns independent.

## Safety boundary

This decision does not establish:

- an original replenish/clean duration formula,
- a skill-to-duration formula,
- an original replenishment quantity,
- an original stamina cost,
- a target-selection or task-priority rule,
- a default duration for unobserved work,
- sub-minute timing or video/game-time conversion.

Unobserved work remains unresolved by the observation-backed duration policy.