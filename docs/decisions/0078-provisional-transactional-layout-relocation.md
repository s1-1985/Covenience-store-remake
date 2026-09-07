# Decision 0078: Add provisional transactional layout relocation

## Status

Accepted.

## Context

Free fixture layout and fixture-facing interaction are confirmed characteristics of the first
PS/SS title, but the exact editing workflow, construction restrictions, time behavior, and all
fixture geometry are not yet fully recovered. The Godot client nevertheless needs a touch-first
editing seam so layout work can advance without hard-coding an invented original menu flow.

## Decision

Add a deliberately small prototype relocation interaction:

1. after the active visit is complete, tap/click an existing fixture to select it;
2. tap/click an empty subcell to request a new origin;
3. move the fixture and its existing interaction point by the same offset;
4. accept the move only when it stays in bounds, avoids fixtures/entry/exit/staff, and preserves
   the entry-to-shelf-to-checkout-to-exit route;
5. reject invalid moves atomically, leaving the prior layout unchanged.

Editing remains locked during an active visit. Rendering reads the mutable `StoreLayout` rather
than the original JSON copy, so an accepted placement is immediately visible and is used by the
next explicitly admitted customer.

## Evidence boundary

The ability to arrange fixtures is evidence-backed at a high level. This particular tap sequence,
the completed-visit editing gate, moving an interaction point by translation, and all rejection
rules are PROVISIONAL client behavior. They do not claim to reproduce the original construction
menu, closure rules, costs, rotation behavior, path validation, or time passage.

## Consequences

- Touch and mouse input share one engine-native placement boundary.
- Placement cannot corrupt the active route or partially mutate layout on failure.
- Future recovered placement rules can replace the admission gate and validation policy without
  changing rendering or raw pointer handling.
- Rotation, purchasing/selling fixtures, persistence, and original modal UI remain separate work.
