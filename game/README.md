# Convenience Store Remake — Godot production client

This directory is the first production-client seed for the Android-targeted remake.

The Python code under `reference_sim/` remains the compatibility/reference simulator used to recover, test, and compare first-title behavior. The Godot client is the actual player-facing game implementation and should consume recovered rules only after they are evidence-safe enough to promote out of provisional prototype data.

## Current vertical slice

The initial scene deliberately uses generated primitives and text only. It does not reuse original game sprites, logos, music, text dumps, or other copyrighted assets.

The current playable loop is:

1. one customer enters the store;
2. the customer follows an explicit provisional visit plan across product-shelf interaction points;
3. one unit of each available planned product is added to a basket;
4. after the plan, a customer with a nonempty basket pathfinds to the checkout;
5. the staff member performs a timed prototype checkout;
6. sale cash is added;
7. the customer pathfinds to the exit;
8. the HUD shows game time, cash, aggregate stock, current basket, customer state, staff state,
   completed sales/visits, and the last event;
9. after a customer exits, the player can admit another customer while preserving stock and cash.

Each successful checkout also appends an immutable prototype sale record linking the customer,
minute-of-day, basket lines, and total. This ledger is factual telemetry for the explicit slice;
its IDs and shape are not a reconstruction of an original receipt system.

The runtime also retains a cause-neutral event timeline for admissions, product visits,
pickup/unavailability, checkout, exit, and accepted layout edits. A versioned provisional
observation snapshot exposes those events with sales and inventory for future evidence comparison;
it is not an original event format or causality model.

An explicit non-UI restock boundary can return a caller-specified quantity to a known product while
recording the caller-specified procurement total as an immutable expense. It deliberately contains
no capacity, reorder trigger, supplier-price, delivery, or autonomous staff-selection formula.

Each manual admission now creates a distinct customer record. Completed records are retained rather
than reusing one mutable customer object. The current slice intentionally permits only one active
customer because original concurrent-arrival and collision rules have not yet been recovered.
An additional non-UI admission boundary accepts a caller-provided unique customer ID and explicit
known-product order for future observation replay; it still makes no arrival or purchase decision.

The store renderer also shows the tile/subcell grid, fixture footprints, interaction points, entry/exit points, customer, and staff.

## Important evidence boundary

`data/vertical_slice.json` is explicitly marked `provisional: true`.

Its layout, tick rate, shopping duration, checkout duration, initial cash, stock, and price exist only to make the first visible client executable. They are **not claims that the original PS/SS game used those values or formulas**.

As original behavior becomes confirmed through research, observation replay, emulator experiments, or later disc reverse engineering, production rules should replace provisional inputs deliberately and with tests.

## Run

1. Install Godot 4.x.
2. Import `game/project.godot`.
3. Run the project (`F6/F5` depending on editor workflow; the configured main scene is `res://scenes/main.tscn`).

Controls:

- **Pause / Resume** — pause automatic prototype ticks.
- **Step** — execute exactly one prototype simulation step while paused.
- **Reset** — restore the initial vertical-slice state.
- **Admit next customer** — start another visit after the current customer exits.
- **Prototype layout relocation** — after a visit finishes, tap/click a fixture and then an empty
  grid cell. Invalid or route-breaking moves are rejected atomically. This interaction is
  PROVISIONAL and is not a reconstruction of the original construction menu.
- **Rotate selected fixture clockwise** — rotate the selected fixture by one quarter turn after a
  visit. The control, pivot, and interaction-point transformation remain PROVISIONAL even though
  fixture rotation itself is visually confirmed in first-title research.
- **Reset** also discards layout edits and restores the complete configured prototype scenario.
- **Space** — Pause / Resume shortcut.

## Headless validation

With Godot 4.3 available, load the main scene and execute the deterministic vertical slice without a display:

```bash
godot --headless --path game --script res://scripts/headless_smoke.gd
```

The smoke script first loads and instantiates the configured main scene, then verifies repeat visits
through sellout: each stocked visit completes a sale,
stock and cash stay consistent, and a later empty-shelf visit exits without creating revenue. CI
runs both the Godot import and this executable smoke check in addition to the Python contracts.

## Architecture direction

- `scripts/vertical_slice_simulation.gd` — deterministic prototype orchestration and combined
  read-only snapshots; no rendering.
- `scripts/domain/store_layout.gd` — store bounds, fixture occupancy, interaction points, and
  static pathfinding.
- `scripts/domain/inventory_state.gd` — provisional product identity, shelf stock, and price state.
- `scripts/domain/inventory_catalog.gd` — product-ID lookup, aggregate stock, explicit fixture
  bindings, and sellout reconciliation.
- `scripts/domain/economy_state.gd` — cash and completed-sale settlement state.
  It also retains immutable cause-neutral sale records for reconciliation and later observation
  export.
- `scripts/domain/customer_state.gd` — one customer's route, phase, position, explicit visit plan,
  basket lines, and action timers.
- `scripts/domain/customer_roster.gd` — unique customer identity, retained visit state, and the
  explicit single-active-customer admission boundary.
- `scripts/domain/staff_state.gd` — one staff member's identity, position, and prototype task state.
- `scripts/domain/staff_roster.gd` — configured staff membership and the explicitly selected
  provisional checkout staff; it does not choose tasks autonomously.
- `scripts/domain/runtime_event_log.gd` — immutable sequenced facts for deterministic observation
  export; event names and timestamp shape remain provisional.
- `scripts/store_view.gd` — generated 2D visualization only.
- `scripts/main.gd` — client orchestration and HUD binding.
- `scripts/headless_smoke.gd` — Godot-native deterministic executable check.
- `data/vertical_slice.json` — explicit provisional inputs.
- `scenes/main.tscn` — player-facing scene composition.
- `reference_sim/` — compatibility oracle and evidence-backed validation, not a runtime dependency of the Godot app.

The vertical slice now composes reusable engine-native layout, customer, staff, inventory, and
economy state objects plus explicit actor rosters. The next production steps are to connect those
rosters and explicit product plans to evidence-backed observation replay, introduce demand or
concurrency only behind separately identified policies, and expand store interaction without
changing unresolved original rules silently.
