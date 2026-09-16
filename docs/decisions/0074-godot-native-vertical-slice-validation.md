# Decision 0074: Validate the production vertical slice with Godot itself

## Status

Accepted.

## Context

The production-client scaffold originally had Python contract tests for file presence, provisional
data boundaries, and route reachability. Those checks cannot prove that Godot can import the
project, parse its GDScript, instantiate the simulation, or execute the player-visible loop.

## Decision

CI performs one bounded Godot 4.3 headless command whenever `game/**` or the shared workflow changes.
The job:

1. runs one bounded headless editor import to build the same script-class metadata a normal project
   open creates and to parse project resources;
2. executes `scripts/headless_smoke.gd` against the same provisional JSON consumed by the client;
3. loads and instantiates the project main scene from the smoke harness.

The CI job has a five-minute timeout. The editor import is required: direct `--script` startup does
not guarantee that the editor-generated global script-class cache exists in a clean checkout. The
import and executable smoke remain separate commands in the same job and workspace.

The smoke check runs the deterministic slice to bounded completion and verifies multi-product
baskets, stock depletion, cash/ledger reconciliation, customer exit, layout editing, and reset.
Python contracts remain fast structural checks; they do not replace the engine-native run.

The smoke preload graph also avoids depending on custom class annotations, so direct script parsing
remains robust even before cache generation. Built-in values used by the smoke script receive
explicit built-in types when inference starts from an untyped cross-script reference. The import
step is retained as defense in depth and as a project-resource validation boundary.

## Evidence boundary

This validation asserts internal consistency only. It does not promote tick rate, route choice,
shopping duration, checkout duration, product price, stock, layout, or any other provisional
client input to a recovered first-title rule.

## Consequences

- GDScript parse and scene import errors fail CI instead of reaching a device build later.
- The first player-visible loop has an executable engine-level regression check.
- Future production-domain extraction can preserve this end-to-end contract while replacing the
  single-customer prototype incrementally.
