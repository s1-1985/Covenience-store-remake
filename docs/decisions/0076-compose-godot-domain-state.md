# Decision 0076: Compose the Godot vertical slice from reusable domain state

## Status

Accepted.

## Context

The first playable Godot slice kept layout/pathfinding, inventory, cash, customer state, staff
state, and orchestration in one simulation script. That was suitable for proving the transaction
loop, but it made the next customer, fixture-placement, and staff milestones likely to duplicate
or couple unrelated state.

The client inputs are still explicitly provisional. Refactoring ownership must not turn its
prototype timing, price, stock, layout, or scripted customer sequence into claims about the
original PS/SS rules.

## Decision

Split the existing state into small engine-native `RefCounted` objects:

- `StoreLayout` owns grid bounds, fixture occupancy, interaction lookup, and static pathfinding;
- `InventoryState` owns the configured product and its current shelf stock;
- `EconomyState` owns cash and completed-sale settlement;
- `CustomerState` owns one customer's position, route, phase, basket flag, and action timers;
- `StaffState` owns one staff member's identity, position, and current prototype state.

`VerticalSliceSimulation` remains the deterministic orchestrator. It advances the same scripted
visit and exposes one combined snapshot for the HUD, but no longer owns duplicate domain fields.

## Evidence boundary

This is an architecture-only change. It preserves the manual customer admission boundary and all
values in `vertical_slice.json` as PROVISIONAL. The object split does not establish original
demand, purchasing, staff task selection, pathfinding, checkout timing, inventory, or economy
rules.

## Consequences

- Future customers and staff can use independent state objects instead of adding parallel fields
  to the orchestrator.
- Fixture placement can replace or rebuild `StoreLayout` without taking ownership of cash or
  actors.
- The smoke test continues to cross the full scene and transaction boundary.
- Evidence-backed policies can later replace individual orchestration decisions without silently
  changing unrelated domain state.
