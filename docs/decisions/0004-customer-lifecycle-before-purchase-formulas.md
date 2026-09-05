# Decision 0004 — Implement customer lifecycle before purchase formulas

Date: 2026-09-05

## Decision

Implement the observable customer state transitions that are already supported by first-title evidence, while leaving product choice, add-on purchase probability, patience, queue policy and checkout duration external/unresolved.

## Evidence-supported structure

The first title visibly/observationally supports a normal flow equivalent to:

```text
enter
-> approach merchandise
-> interact/pick merchandise
-> checkout/wait
-> leave
```

It also supports player selection of an individual customer and forced ejection (`つまみだす`).

Separate PS evidence strongly suggests vending-machine purchases can complete without the normal checkout path and that a customer may then continue into the store. This remains strong-provisional rather than fully confirmed.

## Implementation rule

The lifecycle controller therefore receives an **explicit merchandise fixture order from its caller**. It does not decide what a customer wants.

Likewise, after a merchandise interaction the caller explicitly classifies that interaction as:

- `CHECKOUT_REQUIRED`
- `SELF_SERVICE_CANDIDATE`

No probability is attached to either path yet.

Checkout completion is also an explicit event. Merely waiting at the checkout never auto-completes a sale in this layer, because register skill/service-time formulas remain unresolved.

## Deliberately absent

Do not add yet:

- primary-product selection weights;
- incidental/add-on purchase probability;
- customer budget distribution;
- patience/anger thresholds;
- checkout queue geometry;
- checkout service duration;
- theft probability;
- abandonment probability;
- customer archetype numerical modifiers.

These become pluggable policies once guide/video evidence is strong enough.

## Why this is useful

The state machine gives the project an executable place to attach later evidence without rebuilding pathing or rendering. It also lets future tests distinguish a structural flow bug from an uncertain economic/AI formula.
