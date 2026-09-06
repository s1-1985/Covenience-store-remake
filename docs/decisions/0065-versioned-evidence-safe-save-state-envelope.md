# Decision 0065: versioned evidence-safe save state envelope

## Context

The reference simulation now has many independently testable stateful runtimes, while exact first-title formulas and large guidebook-derived tables remain intentionally unresolved. A persistence layer is needed before those unknowns are filled, but serializing guessed defaults would turn research gaps into accidental rules.

## Decision

Add `SaveStateEnvelope` as a small versioned persistence boundary.

- The envelope stores named subsystem components as JSON-compatible values only.
- `None` and explicit unknown markers are preserved exactly.
- Missing components remain missing; the save layer does not manufacture defaults.
- Component schemas remain owned by their respective runtimes/data adapters.
- The outer envelope rejects unknown top-level keys so migrations cannot silently ignore incompatible metadata.
- The envelope itself contains no economic formula, AI priority, duration, price, or original-game constant.

## Why now

This gives later clock, store, staff, customer, event, rival, and economy state adapters a stable target without coupling persistence to unfinished research tables. Guidebook values can therefore be added later as component data instead of requiring a persistence redesign.

## Evidence boundary

This is an architecture decision, not evidence that the 1997 PS/SS title used this file format, schema version, or save representation. The original game's save-file layout is not being reconstructed here.

## Still unresolved

- which runtime components are required for a complete playable save;
- exact original save slots/UI and serialization format;
- migration policy after component schemas become concrete;
- whether transient pathfinding/queue calculations should be serialized or rebuilt;
- original-game behavior when saving during modal/event/transition states.
