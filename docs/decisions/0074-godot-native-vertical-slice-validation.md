# Decision 0074: Validate the production vertical slice with Godot itself

## Status

Accepted.

## Context

The production-client scaffold originally had Python contract tests for file presence, provisional
data boundaries, and route reachability. Those checks cannot prove that Godot can import the
project, parse its GDScript, instantiate the simulation, or execute the player-visible loop.

## Decision

CI performs two Godot 4.3 headless checks whenever `game/**` or the shared workflow changes:

1. import the project and main scene in editor mode;
2. execute `scripts/headless_smoke.gd` against the same provisional JSON consumed by the client.

The smoke check runs the deterministic slice to a bounded completion and verifies exactly one
sale, one unit of stock depletion, the corresponding cash credit, and customer exit. Python
contracts remain as fast structural checks; they do not replace the engine-native run.

## Evidence boundary

This validation asserts internal consistency only. It does not promote tick rate, route choice,
shopping duration, checkout duration, product price, stock, layout, or any other provisional
client input to a recovered first-title rule.

## Consequences

- GDScript parse and scene import errors fail CI instead of reaching a device build later.
- The first player-visible loop has an executable engine-level regression check.
- Future production-domain extraction can preserve this end-to-end contract while replacing the
  single-customer prototype incrementally.
