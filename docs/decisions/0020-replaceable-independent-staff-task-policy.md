# Decision 0020 — staff task selection is replaceable and independent per staff member

Date: 2026-09-06

## Context

First-title staff/FAQ evidence supports several non-optimal behaviors:

- a waiting checkout does not globally force every available worker to prioritize the register,
- staff can continue replenishment while customers wait,
- two staff can independently head toward the same checkout,
- low-stamina staff can leave checkout coverage and return to rest,
- checkout service order is not guaranteed FIFO.

At the same time, the exact original priority formula, urgency thresholds, travel-time weighting and conflict resolution are not recovered.

Research basis:
- `docs/research/staff-mechanics-model-2026-09-05.md`
- first-title staff/FAQ evidence already summarized under `docs/research/`

## Decision

1. Add a `StaffTaskPolicy` protocol rather than hard-coding an optimal priority list.
2. Candidate discovery is caller-supplied. The policy layer does not decide when stock is low enough, a queue is urgent enough, or dirt is important enough.
3. A candidate has only a task, target and optional reason; no invented numeric priority score is attached.
4. Each available staff member is asked independently for a decision.
5. A policy may return no decision even when a checkout candidate exists; this preserves the possibility of original-style coverage gaps.
6. Multiple staff may choose the same target. Do not add a global deduplicating optimizer at this layer.
7. Rest/return-to-break-room remains condition-driven by the existing stamina state machine rather than a normal work candidate.
8. A chosen decision must match one of the supplied candidates, preventing a policy from silently creating unsupported work needs.
9. Provide a deterministic scripted policy for tests and observation replay only; it is not a claim about the original AI.

## Consequence

The reference simulator now has a stable seam for future staff-AI reconstruction:

`known work needs -> per-staff candidate context -> replaceable policy -> explicit roster assignment`

Video-derived or guide-derived priority rules can later replace the scripted/test policy without changing checkout, replenishment, cleaning or stamina subsystems.

## Explicitly unresolved

This decision does not choose:

- checkout vs replenishment vs cleaning priority,
- queue-length or waiting-time thresholds,
- target-distance weighting,
- manager effects on task choice,
- staff-skill effects on task choice,
- conflict resolution when two staff choose one register,
- whether a worker deliberately chooses idle work over a known candidate,
- exact timing/cadence at which the original AI reconsiders a task.
