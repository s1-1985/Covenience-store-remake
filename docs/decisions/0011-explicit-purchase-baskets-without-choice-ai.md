# Decision 0011 — Keep purchase baskets explicit and separate from customer-choice AI

Date: 2026-09-05

## Decision

Connect customer item selection to inventory depletion and sale revenue now, but keep product choice, quantity choice, checkout-vs-self-service routing, abandonment and add-on probability outside the transaction runtime until those rules are recovered.

## Evidence basis

The first-title reconstruction already supports:
- customers physically visit merchandise fixtures;
- normal merchandise can require checkout;
- vending/self-service is a separate candidate flow;
- stock is depleted by customer purchases and replenished by staff;
- product prices exist and affect demand/customer share;
- exact product-choice and incidental/add-on formulas are still unresolved.

Therefore the safe implementation boundary is an explicit caller-supplied basket rather than an autonomous purchase AI.

## Runtime boundary

Implement now:

```text
CustomerBasket
- customer_id
- explicit purchase lines
- known subtotal
- unknown-price line count
- settled flag

PurchaseLine
- slot / fixture / product
- quantity
- explicit unit sale price or UNKNOWN

StorePurchaseRuntime
- open basket
- take explicit quantity from inventory
- attach explicit price to basket line
- settle basket into StoreCashLedger
- preserve unknown sale-price effects as unknown cash events
```

The caller decides when `settle()` occurs. That keeps both of these possible without hard-coding unverified behavior:

```text
normal store purchase -> staffed checkout -> settlement
self-service candidate -> self-service completion -> settlement
```

## Unknown-price handling

If a basket contains a mix of known and unknown prices:
- the known subtotal is credited normally;
- a second UNKNOWN sale event records the unresolved remainder;
- the cash ledger becomes inexact rather than silently assuming the unknown items cost zero.

## Deliberately unresolved

Do not invent:
- which product a customer wants;
- how many units a customer buys;
- add-on/impulse-purchase probability;
- spending-power or budget distribution;
- price rounding/tax rules;
- what happens to physically picked stock if a customer abandons a basket or is ejected;
- whether every self-service candidate settles instantly or at some other point;
- the exact relationship between a merchandise interaction animation and quantity purchased.
