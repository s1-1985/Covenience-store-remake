# Decision 0002 — Use a configurable sub-tile compatibility grid

Date: 2026-09-05

## Decision

The reference simulation represents each researched store tile as **2 x 2 internal subcells by default**.

This choice exists so the implementation can represent first-title observations where roughly **0.5 tile** of contact/gap is enough for an interaction or passage, while one-tile aisles are materially more reliable.

## Important limitation

This is **not** a claim that the original PS/SS executable internally used a half-tile navigation grid.

The original internal coordinate/collision system remains unknown. Therefore `subcells_per_tile` is configurable and the Android production client must not hard-code a literal original-engine interpretation from this decision.

## What this enables now

- fixture footprint placement without losing half-tile reachability;
- rotated rectangular fixtures;
- a directional interaction edge;
- editable/blocked cell masks;
- reachability tests around obstacles;
- future congestion experiments at finer-than-one-tile resolution.

## Current pathfinding scope

The reference layer uses deterministic four-neighbor BFS only as a **layout reachability oracle**.

It does not yet claim to reproduce:

- the original customer's exact path-selection heuristic;
- dynamic NPC collision avoidance;
- queue formation rules;
- movement speed;
- congestion retry timing;
- diagonal/subpixel movement.

Those remain separate behavioral research/implementation tasks.

## Evidence basis

First-title-specific research currently supports:

- fixtures have a usable side/direction;
- fixtures can be rotated;
- approximately 0.5 tile of contact can be sufficient for use;
- 0.5-tile gaps are prone to congestion;
- one-tile aisles are practically recommended;
- checkout/entrance fronts benefit from roughly two tiles;
- multiple routes can allow detours around congestion;
- parking fixture cells are non-walkable.

Primary research note:
- `docs/research/store-dimensions-and-fixture-costs-2026-09-05.md`
