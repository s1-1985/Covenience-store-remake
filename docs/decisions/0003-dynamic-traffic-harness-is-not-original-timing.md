# Decision 0003 — Dynamic traffic harness is not original timing

Date: 2026-09-05

## Decision

Add a minimal dynamic occupancy/congestion harness on top of `StoreGrid`, but keep every timing-sensitive behavior configurable or explicitly unresolved.

## Why now

First-title evidence is already strong enough to require:

- individual customer/staff entities;
- physical blocking/congestion;
- fixture-facing interaction points;
- the possibility of detours when another route exists.

What is **not** yet recovered is the exact original timing/policy for:

- movement speed;
- collision retry interval;
- who gets priority when two NPCs want the same space;
- how long an NPC waits before rerouting;
- whether a route is recomputed every step or only after blockage;
- exact queue behavior.

## Harness rules

The current harness therefore uses conservative experiment rules:

- at most one dynamic agent per internal subcell;
- a harness tick permits at most one subcell step;
- simultaneous contention for the same destination makes all contenders wait;
- moving into a cell occupied at the start of the tick is rejected;
- `reroute_after_blocked_ticks` defaults to `None` because the original threshold is unknown;
- tests may supply a synthetic reroute threshold to prove the capability exists.

These are **test-harness semantics**, not claims about the PS/SS executable.

## Intended use

Use the harness to test whether researched layouts can naturally produce:

- bottlenecks;
- blocked interaction faces;
- single-route failure;
- alternative-route detours;
- waiting accumulation;
- future checkout queue experiments.

When stronger video/guide evidence is recovered, replace/tune only the congestion policy rather than rewriting the store-layout model.
