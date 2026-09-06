# Convenience Store Remake — Godot production client

This directory is the first production-client seed for the Android-targeted remake.

The Python code under `reference_sim/` remains the compatibility/reference simulator used to recover, test, and compare first-title behavior. The Godot client is the actual player-facing game implementation and should consume recovered rules only after they are evidence-safe enough to promote out of provisional prototype data.

## Current vertical slice

The initial scene deliberately uses generated primitives and text only. It does not reuse original game sprites, logos, music, text dumps, or other copyrighted assets.

The current playable loop is:

1. one customer enters the store;
2. the customer pathfinds to a shelf interaction point;
3. one product is removed from shelf stock;
4. the customer pathfinds to the checkout;
5. the staff member performs a timed prototype checkout;
6. sale cash is added;
7. the customer pathfinds to the exit;
8. the HUD shows game time, cash, stock, customer state, staff state, completed sales, and the last event.

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
- **Space** — Pause / Resume shortcut.

## Architecture direction

- `scripts/vertical_slice_simulation.gd` — deterministic prototype domain state; no rendering.
- `scripts/store_view.gd` — generated 2D visualization only.
- `scripts/main.gd` — client orchestration and HUD binding.
- `data/vertical_slice.json` — explicit provisional inputs.
- `scenes/main.tscn` — player-facing scene composition.
- `reference_sim/` — compatibility oracle and evidence-backed validation, not a runtime dependency of the Godot app.

The next production steps are to replace this single scripted customer with reusable customer/staff/store domain objects, port evidence-backed contracts from `reference_sim`, and then add touch-first store interaction and fixture placement without changing unresolved original rules silently.
