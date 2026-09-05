# Decision 0001 — Start with simulation/data code before final art

Date: 2026-09-05

## Decision

Begin implementation with an engine-independent, executable reference simulation/data layer. Do **not** begin final image production yet.

## Why

Open-web research has reached diminishing returns for the remaining high-value numeric masters. The ordered strategy guides are the likely next major static-data source. Meanwhile, enough structure is known to safely implement:

- evidence-tagged baseline data contracts;
- store variant placeholders with unknown fields preserved as unknown;
- fixture/service/parking anchors;
- promotion anchors;
- permit definitions with per-permit eligibility;
- scenario anchors;
- four-representative-day calendar behavior.

Final art is deferred because exact fixture inventory, footprints, screen composition and touch adaptation are still being refined. Creating polished images now risks rework and accidentally anchoring layout decisions before the master tables arrive.

## Art policy during early implementation

Use placeholders only (simple geometric blocks/icons created by the project). Do not reuse original copyrighted sprites, logos or UI art.

## Production engine

Not selected by this decision. The reference model stays portable. A production-engine decision (Godot/native/libGDX/etc.) should be made after the first reference-simulation milestone and Android input/rendering requirements are written down.

## Research continues in parallel

Implementation does not close research. New guidebook/video/manual evidence should update the reference data and tests first, then the production client.
