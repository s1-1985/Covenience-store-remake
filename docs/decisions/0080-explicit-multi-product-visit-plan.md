# Decision 0080: Exercise multiple products through an explicit visit plan

## Status

Accepted.

## Context

The first Godot transaction loop had one global stock count, one price, and one boolean indicating
whether the customer held a product. That shape could not represent multiple product fixtures or a
basket, and it encouraged later demand work to become coupled to a single hard-coded shelf.

The original purchase-choice, incidental-purchase, quantity, and product-priority formulas remain
unrecovered. A client-side autonomous shopping policy would therefore be premature.

## Decision

- Replace the single inventory object with an `InventoryCatalog` keyed by explicit product IDs.
- Keep one `InventoryState` per product, including its explicit fixture binding, stock, and price.
- Give each prototype customer an explicit ordered `visit_plan_product_ids` input.
- Visit each planned product fixture in order, taking at most the explicitly scripted one unit when
  stock exists and recording an immutable basket line at the observed price.
- Skip unavailable planned products. Go to checkout when the basket is nonempty, or leave without a
  sale after all planned products are unavailable.
- Settle the whole basket atomically as one completed sale.

The data schema advances to version 4 and the visible prototype includes two product fixtures so
the multi-product boundary is exercised rather than remaining unused architecture.

## Evidence boundary

Product fixtures, stock, baskets, and multi-item purchases are compatible with the confirmed
high-level game loop. The product identities, visit order, one-unit quantity, prices, stock counts,
shopping duration, and behavior when one planned product is unavailable are PROVISIONAL inputs.
The explicit visit plan is test scaffolding, not a recovered demand or purchase-choice algorithm.

## Consequences

- Additional products no longer require parallel fields in the orchestrator.
- Customer basket state records product, quantity, and unit price before settlement.
- Sellout validation can reconcile final cash against every configured product's explicit initial
  stock and price.
- Demand fitting, incidental purchase, product substitution, quantities, restocking, and product
  selection UI remain separate evidence-driven work.
