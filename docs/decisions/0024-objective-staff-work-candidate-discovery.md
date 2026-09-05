# Decision 0024 — Discover objective staff work before applying staff AI

Date: 2026-09-06

## Decision

Separate factual work discovery from staff task selection.

The reference simulation may derive the following candidate work from current runtime state without inventing an AI priority formula:

- checkout work when a registered checkout has at least one customer currently waiting,
- replenishment work when an inventory slot has free capacity,
- cleaning work for each currently dirty floor cell.

These candidates are then supplied to the existing replaceable `StaffTaskPolicyCoordinator`. Every staff member receives the same objective candidate set; the policy still decides independently whether each available staff member chooses checkout, replenishment, cleaning, or no task.

## Why

First-title evidence establishes that staff do not behave like a globally optimized scheduler:

- customers may wait while staff continue replenishment,
- two staff can head toward the same checkout,
- low-stamina staff can leave checkout work,
- checkout order is not strictly FIFO.

Therefore candidate discovery must not silently become a global priority system.

## Candidate semantics

### Checkout

A checkout candidate exists only when `refresh_waiting()` reports at least one waiting customer. The candidate target is the checkout fixture instance ID.

The discovery layer does not select which customer will be served and does not reserve the checkout for one staff member.

### Replenishment

A replenishment candidate exists whenever an inventory slot is below capacity. The target is the inventory slot ID.

This does not assert a reorder threshold, preferred fill level, pack size, quantity, or urgency.

### Cleaning

A cleaning candidate exists for each already-recorded dirty floor cell. The target ID uses the internal form `floor:<x>:<y>`.

The discovery layer does not create dirt and does not decide cleaning route order or duration.

## Ordering

Candidate tuple ordering is deterministic for repeatable tests and logs only. It is not a task-priority rule and must not be interpreted as checkout > replenishment > cleaning behavior.

## Still unresolved

- relative task priorities,
- queue-length / wait-time thresholds,
- inventory thresholds and refill quantities,
- cleaning route selection,
- distance weighting,
- staff skill effects on task choice,
- task reconsideration cadence,
- movement duration to work targets,
- work duration and interruption behavior.

These remain policy/timing concerns to be filled from video and guide evidence later.
