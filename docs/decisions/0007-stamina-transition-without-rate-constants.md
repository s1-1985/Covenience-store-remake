# Decision 0007 — Implement stamina state transitions without inventing rate constants

Date: 2026-09-05

## Decision

Represent the confirmed staff stamina lifecycle now, but require all stamina consumption/recovery amounts to be supplied explicitly until the original numeric rates are recovered.

## Evidence

First-title staff research supports:
- register, replenishment and cleaning work consume stamina;
- when stamina reaches 0, the staff member returns to the break room;
- the staff member rests until stamina is fully recovered;
- agility appears to increase the chance of recovering 2 stamina instead of 1, but the probability rule is observational/provisional;
- register/replenishment/cleaning work are also skill-growth triggers, while exact growth handling is not fully uniform.

Primary research:
- `docs/research/staff-mechanics-model-2026-09-05.md`
- `docs/research/behavior-rules-evidence-2026-09-05.md`

## Runtime states

```text
AVAILABLE
  -> work
  -> stamina reaches 0
RETURNING_TO_BREAK_ROOM
  -> explicit break-room arrival
RESTING
  -> explicit recovery events
  -> stamina == stamina_max
AVAILABLE
```

`RETURN_TO_BREAK_ROOM` is represented separately from `REST` so future pathing can attach the staff entity to an actual break-room fixture/destination.

## Unknowns deliberately left open

Do not add default constants for:
- stamina cost per checkout;
- stamina cost per replenishment;
- stamina cost per cleaning action;
- rest recovery per simulation tick;
- agility-to-double-recovery probability;
- travel speed to/from the break room;
- whether all work types consume the same amount.

The API therefore accepts an explicit stamina cost/recovery amount when a test or future policy has evidence for one. If the staff member's stamina value itself is unknown, explicit stamina mutation is rejected instead of guessing.

## Work-event counters

Completed checkout/replenishment/cleaning events are counted independently of stamina. These counters are intended as input for later staff-growth reconstruction.

This is important because the current evidence supports task-linked growth, but the interaction with manager education, caps, exceptions and event-driven cap overflow must remain replaceable.
