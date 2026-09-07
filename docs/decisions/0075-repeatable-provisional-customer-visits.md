# Decision 0075: Make provisional customer visits repeatable without inventing demand

## Status

Accepted.

## Context

The first Godot vertical slice stopped permanently after one customer exited. That proved the
transaction path but did not let a player observe persistent stock and cash across visits or the
empty-shelf outcome.

Automatically spawning customers at a guessed interval would imply an unrecovered first-title
demand rule. The production client still needs a repeatable loop before that evidence exists.

## Decision

After a visit reaches `done`, expose an explicit **Admit next customer** action. Starting another
visit resets only transient customer state; cash, stock, completed sales, and completed visit counts
remain cumulative. The full Reset action still restores the provisional scenario.

The engine-native smoke test repeats visits until stock is exhausted and then runs one additional
visit. Stocked visits must settle normally, while the empty-shelf visit must exit without a sale.

## Evidence boundary

Manual admission is a prototype control, not a claim about original customer arrival timing,
demand volume, purchase probability, patience, or customer archetypes. Those rules remain behind
future evidence-backed or explicitly provisional policies.

## Consequences

- The playable slice now demonstrates persistent economy and inventory over multiple visits.
- Sellout behavior is covered by a Godot-native executable regression.
- A future arrival scheduler can call the same admission boundary without rewriting transaction
  progression.
