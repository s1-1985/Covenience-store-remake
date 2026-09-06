# Decision 0038 — Policy-driven replenish and cleaning completion

Date: 2026-09-06

## Context

The store-step orchestration can already discover objective checkout/replenishment/cleaning candidates and ask a replaceable staff policy which task each available employee should take. Checkout now also has an optional timing coordinator that can carry an active service across steps until a supplied duration policy permits settlement.

Replenishment and floor cleaning still had a manual seam: assigning `StaffTask.REPLENISH` or `StaffTask.CLEAN` did not create any lifecycle that a later store step could complete. External code had to call `replenish_and_charge()` or `clean()` directly.

First-title work duration, replenishment quantity, stamina cost and interruption rules are not recovered well enough to hard-code.

## Decision

Add `StaffWorkTimingCoordinator` for non-checkout work (`REPLENISH` and `CLEAN`).

A registered assignment stores:

- staff id;
- task and target id;
- absolute in-game minute at assignment.

A replaceable `StaffWorkCompletionPolicy` receives current elapsed game minutes plus factual target state. It may:

- return `None` to keep work active;
- return `StaffWorkCompletionDecision` to complete the action now.

Replenishment completion requires an explicit positive quantity. Cleaning completion has no quantity. Optional stamina cost and break-room target remain caller supplied.

The coordinator invokes only the existing runtime actions:

- `StoreRuntimeHarness.replenish_and_charge()` for replenishment;
- `StoreCleaningRuntime.clean()` for cleaning.

Therefore inventory mutation, procurement cash events, staff work-event counts, growth opportunities and stamina transitions continue to use the existing single sources of truth.

`StoreStepOrchestrator` optionally composes the coordinator as a pair with a completion policy. Registered non-checkout work is evaluated immediately after the game clock advances. While active, that staff member is locked out of the generic task selector so an in-progress lifecycle is not silently overwritten. Newly assigned replenish/clean work is registered at the current absolute game minute for later steps.

## Stale shared targets

The existing staff task policy intentionally permits multiple employees to choose the same target because the original independent task-priority rule is unresolved.

If one employee completes a shared target first:

- a full inventory slot is no longer actionable for another registered replenishment;
- an already-clean floor cell is no longer actionable for another registered cleaning task.

The later stale assignment is released to idle without recording a completed work event. This is integrity cleanup, not an invented productivity rule.

## Evidence-safe boundary

This change does **not** define:

- replenishment or cleaning duration;
- replenishment quantity/reorder point;
- stamina consumption per action;
- travel speed to the target;
- task interruption/preemption priority;
- skill-growth amount;
- automatic dirt generation.

All unresolved values remain outside the coordinator and may stay unknown.

## Consequence

With explicit replacement policies supplied, the headless store loop can now carry checkout, replenishment and cleaning work across multiple game-time steps and complete their existing runtime effects without an external per-action finish call. This removes another manual seam on the path to one representative store day running autonomously.
