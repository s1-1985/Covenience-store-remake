# Decision 0079: Add provisional fixture rotation and complete layout reset

## Status

Accepted.

## Context

Fixture rotation is visually confirmed in first-title research, and the prototype Reset control is
documented as restoring the initial vertical-slice state. After mutable relocation was added, Reset
restored actors, inventory, and cash but accidentally retained the edited layout. Rotation was also
still unavailable even though layout state now supported transactional editing.

Exact original rotation controls, pivot rules, interaction-face transformation, edit restrictions,
and costs remain incomplete.

## Decision

- Preserve an immutable deep copy of the configured fixture layout in `StoreLayout`.
- Make full simulation reset restore that configured layout as well as actors and economy.
- Add clockwise quarter-turn rotation for the selected fixture.
- Rotate the footprint around its origin and transform the existing interaction subcell by the same
  grid rotation.
- Run rotation through the same transactional occupancy, staff-cell, and route checks as movement.
- Expose rotation as a separate touch-friendly button after fixture selection.

Four accepted clockwise rotations must reproduce the exact original fixture geometry. A rejected
rotation restores the complete prior fixture snapshot.

## Evidence boundary

Only the existence of fixture rotation is treated as confirmed at this stage. Clockwise-only UI,
the origin pivot, interaction-cell transform, between-visit gate, validation policy, and absence of
cost are PROVISIONAL. They must be replaced when manual/video/binary evidence resolves the original
editing contract.

## Consequences

- Reset once again matches its documented whole-scenario behavior.
- Rotation and relocation share an atomic rollback mechanism.
- Mutable edits never modify the source JSON dictionary or the immutable reset snapshot.
- Fixture purchase, sale, arbitrary interaction-face selection, saved layouts, and original modal
  reconstruction remain future work.
