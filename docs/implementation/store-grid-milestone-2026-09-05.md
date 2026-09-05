# Store-grid implementation milestone — 2026-09-05

This milestone begins the first layout/runtime code that is safe to build before the ordered strategy guides arrive.

Implemented:

- researched store dimensions can instantiate an engine-independent grid;
- default internal resolution is 2 subcells per researched tile, configurable;
- rectangular fixture footprints and 90-degree rotation;
- directional interaction edge rotation;
- editable mask support for future wall/entrance/bug-compatible layouts;
- static obstacles and fixture overlap rejection;
- confirmed parking definitions are marked pedestrian-blocking;
- deterministic four-neighbor shortest-path reachability;
- path-to-fixture targets the currently walkable interaction edge;
- unknown fixture footprints remain unplaceable rather than silently receiving guessed values.

Deliberately not implemented yet:

- exact customer path-selection heuristic;
- NPC-vs-NPC collision and congestion timing;
- checkout queue shape/service timing;
- customer primary/incidental purchase decision model;
- staff task priority;
- exact entrance/exit cells for every store variant;
- full fixture master.

The next safe implementation layer is dynamic occupancy/congestion and a minimal customer traversal harness, while exact formulas and numeric masters continue to wait for stronger evidence/strategy-guide extraction.
