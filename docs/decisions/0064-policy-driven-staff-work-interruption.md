# 0064 — Keep active work committed by default; expose checkout interruption as a policy

## Decision

Active timed `REPLENISH` / `CLEAN` work remains locked by default even when checkout demand appears. Checkout demand alone does not cancel an in-progress task.

A new optional `StaffWorkInterruptionPolicy` may inspect factual active-work elapsed time and current waiting-customer counts by checkout fixture. Only an explicit `True` request while checkout demand actually exists releases the active work assignment. Ordinary staff-task selection then runs in the same store step and may choose checkout.

Interrupted work is unregistered and the matching staff assignment is released to idle. No automatic resume semantics are invented; the underlying target remains objectively actionable and may be selected later by the active task policy.

## Evidence

First-title dedicated FAQ research (B+) reports that staff can continue replenishment or other work even while customers wait at checkout, instead of always switching immediately. The exact interruption threshold/condition is unknown.

## Why

A hard-coded `if queue: cancel_work()` contradicts observed first-title behavior, while a permanent non-interruptible lock would also overstate the evidence. A replaceable boundary preserves the observed commitment while leaving the unknown threshold testable.

## Safety boundary

This decision does not establish:

- a queue-length threshold,
- an elapsed-work threshold,
- a probability of interruption,
- whether interrupted work resumes from prior progress,
- which checkout is chosen after interruption,
- whether PS/SS differ,
- any stamina condition.

Numeric interruption rules used in tests are synthetic regression inputs only.