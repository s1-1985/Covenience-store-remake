# Decision 0047: record checkout-anger -2 penalties separately from unresolved stat floors

## Status
Accepted for the evidence-safe reference runtime.

## Context

First-title dedicated staff research records a concrete checkout consequence: when a customer becomes angry because checkout handling is too slow, the staff member's runtime work abilities other than education are reduced by 2.

Affected:
- register -2
- replenishment -2
- security -2
- cleaning -2
- service -2

Unaffected by this consequence:
- education
- stamina

The same source does not establish the minimum/floor for those runtime skills. The runtime also does not yet contain an evidence-backed customer patience/anger trigger.

## Decision

Add `CheckoutAngerPenaltyRuntime` with a two-stage boundary:

1. `record(staff_id)` records the confirmed -2 event and snapshots the five affected skill values without mutating them.
2. `resolve(sequence, minimum_by_skill=...)` applies the event only when an explicit minimum is supplied for every affected skill.

Resolution:
- is atomic;
- requires all five current values to be known;
- rejects a stale event if any affected value changed since recording;
- clamps each result to the caller-supplied minimum;
- never changes education or stamina.

The anger trigger itself remains outside this runtime until checkout patience/anger timing is recovered or explicitly supplied by an observation/replay policy.

## Evidence-safe boundary

This change does not assume:
- a zero stat floor;
- any other minimum value;
- the waiting/service duration that causes anger;
- whether every angry customer applies exactly one event in every circumstance;
- additional popularity, sales, security, or customer-share consequences.

## Evidence

- `docs/research/staff-growth-penalty-recovery-2026-09-06.md`, section 5.
