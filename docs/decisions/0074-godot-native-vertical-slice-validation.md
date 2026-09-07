# Decision 0074: Validate the production vertical slice with Godot itself

## Status

Accepted.

## Context

The production-client scaffold originally had Python contract tests for file presence, provisional
data boundaries, and route reachability. Those checks cannot prove that Godot can import the
project, parse its GDScript, instantiate the simulation, or execute the player-visible loop.

## Decision

CI performs one bounded Godot 4.3 headless command whenever `game/**` or the shared workflow changes.
The command:

1. loads and instantiates the project main scene, which parses its attached scripts;
2. executes `scripts/headless_smoke.gd` against the same provisional JSON consumed by the client.

The CI job has a five-minute timeout. A separate editor-mode import command is deliberately avoided:
the smoke script already loads the relevant scene and the extra editor startup made every PR wait
without increasing the behavioral coverage of this vertical slice.

The smoke check runs the deterministic slice to bounded completion and verifies multi-product
baskets, stock depletion, cash/ledger reconciliation, customer exit, layout editing, and reset.
Python contracts remain fast structural checks; they do not replace the engine-native run.

Because CI invokes `headless_smoke.gd` directly with `--script`, that script and its preload graph
must not depend on the editor-generated global class-name cache for static type resolution. Cross-
script variables use preloaded constructors with untyped references, while built-in values used by
the smoke script receive explicit built-in types when inference starts from such a reference.

## Evidence boundary

This validation asserts internal consistency only. It does not promote tick rate, route choice,
shopping duration, checkout duration, product price, stock, layout, or any other provisional
client input to a recovered first-title rule.

## Consequences

- GDScript parse and scene import errors fail CI instead of reaching a device build later.
- The first player-visible loop has an executable engine-level regression check.
- Future production-domain extraction can preserve this end-to-end contract while replacing the
  single-customer prototype incrementally.
