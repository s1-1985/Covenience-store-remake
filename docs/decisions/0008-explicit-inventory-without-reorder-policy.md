# Decision 0008 — Implement explicit fixture inventory without inventing reorder policy

Date: 2026-09-05

## Decision

Add a stock ledger that can represent customer depletion, fixture capacity and staff replenishment, but require capacity, quantities and procurement cost to be supplied explicitly until the first-title master data is recovered.

## Evidence basis

First-title research already supports:
- customers physically acquire products from store fixtures;
- staff perform replenishment work as a distinct task;
- replenishment work is a confirmed staff-growth trigger;
- replenishment purchases can still reduce cash while the store is closed, even when many other operating costs are suspended;
- fixture/product compatibility and capacity are gameplay-relevant master data, but the complete values are still missing.

Relevant research:
- `docs/research/behavior-rules-evidence-2026-09-05.md`
- `docs/research/staff-mechanics-model-2026-09-05.md`
- `docs/research/research-checkpoint-2026-09-05.md`

## Runtime boundary

Implement now:

```text
FixtureInventorySlot
- fixture instance id
- product id
- explicit capacity
- current units
- optional explicit unit procurement cost

StoreInventoryRuntime
- customer stock withdrawal
- explicit replenishment
- mutation history
- known procurement-cost subtotal
- flag when procurement cost is unknown
```

A successful staff replenishment records one completed `REPLENISH` work event. The quantity moved is deliberately separate from the count of replenishment task completions.

## Deliberately unresolved

Do not invent:
- fixture capacities;
- stock pack sizes;
- automatic reorder point;
- automatic replenishment quantity;
- whether every product purchase consumes exactly one abstract unit;
- procurement cost for products whose guide data has not been recovered;
- restock stamina cost;
- restock duration;
- restock movement/pathing;
- replenishment-skill growth beyond the already-recorded work event.

Therefore customer product withdrawal and staff replenishment quantities are caller-supplied operations. Unknown procurement cost remains `None`; it is not converted to zero.

## Why this is useful before the guidebooks arrive

Once product/fixture data pages are supplied, recovered capacities and procurement costs can be loaded into this runtime without changing the customer, staff, checkout or economy architecture. It also gives future month/economy tests an explicit replenishment-cost event stream instead of hiding inventory spending inside an invented formula.
