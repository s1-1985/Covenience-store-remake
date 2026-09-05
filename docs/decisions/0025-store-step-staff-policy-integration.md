# Decision 0025 — Let caller-driven store steps optionally reconsider staff tasks

Date: 2026-09-06

## Decision

Extend the caller-driven `StoreStepOrchestrator` so a supplied staff policy may reconsider factual checkout/replenishment/cleaning candidates once per explicit `step()` call.

The store step order is now:

1. advance the caller-supplied number of in-game minutes,
2. optionally evaluate customer demand,
3. run one customer traffic tick,
4. optionally evaluate purchase decisions for customers physically at merchandise,
5. optionally discover current staff work candidates and apply one staff-task policy pass.

This order makes a purchase that reduces inventory visible to staff candidate discovery in the same caller-authorized step. It does not assert how often the original game reconsidered staff work.

## Why

The project now has separate evidence-safe boundaries for:

- customer demand,
- customer movement,
- product purchase choice,
- factual staff work discovery,
- independent staff task choice.

Connecting those boundaries is required before a one-store representative-day harness can be driven from recovered policies. The connection itself does not require inventing the missing formulas.

## Important boundary

Staff task selection is still not staff work execution.

A selected task does **not** automatically:

- move the staff member,
- choose a checkout customer,
- complete a checkout,
- decide a replenishment quantity,
- refill inventory,
- choose a cleaning route,
- clean a cell,
- consume stamina,
- advance skill growth.

Those events remain explicit until original timing and behavior are recovered.

## Cadence

The original task-reconsideration period is unresolved. Therefore the orchestrator does not own a timer for staff AI. A caller decides when to invoke `step()` and therefore when a policy evaluation opportunity exists.

## Still unresolved

- original customer/staff tick relationship,
- task reconsideration cadence,
- staff movement and interruption,
- checkout customer selection,
- checkout duration,
- replenish amount and work duration,
- cleaning target sequence and duration,
- stamina cost timing,
- simultaneous staff behavior at shared targets.
