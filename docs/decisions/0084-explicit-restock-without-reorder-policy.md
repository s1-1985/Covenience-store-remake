# Decision 0084: Apply explicit restock inputs without a reorder policy

## Status

Accepted.

## Context

Replenishment is part of the confirmed first-title staff loop, but exact shelf capacity, reorder
quantity, procurement price, trigger timing, and autonomous staff-selection rules remain incomplete.
The production slice previously reached permanent sellout with no evidence-safe way to return stock.

## Decision

Add a caller-driven restock boundary that requires product ID, staff ID, positive quantity, and an
explicit total procurement cost. It is available only between visits, validates existing product and
staff identities, adds exactly the supplied units, deducts exactly the supplied cost, creates an
immutable expense record, and appends a cause-neutral `inventory_restock` runtime event.

The provisional scenario supplies one example restock input so headless validation can confirm that
stock returns to the ordinary visit, basket, checkout, sale-ledger, and cash flow.

## Evidence boundary

This boundary does not choose when, what, how much, or at what price to reorder. It does not impose an
unknown shelf capacity or infer that the named staff member autonomously selected the work. Quantity,
cost, between-visit gate, and example identities are PROVISIONAL caller inputs.

## Consequences

- Sellout is no longer a terminal architecture state.
- Procurement expenses and sales can be reconciled separately.
- Later staff-task or reorder policies can call the same mutation only after supplying their own
  evidence-backed decision.
- Capacity, delivery delay, storage, supplier pricing, automatic reorder, and replenishment movement
  remain separate work.
