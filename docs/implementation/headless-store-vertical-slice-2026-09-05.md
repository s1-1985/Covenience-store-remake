# Headless store vertical slice — 2026-09-05

The reference simulation now has enough connected pieces to execute a minimal store transaction end to end without inventing the still-unknown AI and timing formulas.

## Connected path

A caller can now drive:

```text
customer enters
 -> pathfinds to merchandise interaction side
 -> explicit product/quantity selection
 -> fixture inventory decreases
 -> normal checkout or self-service candidate flow
 -> staffed checkout service when applicable
 -> sale settlement to cash ledger
 -> customer leaves
```

The same composed runtime also supports:

```text
staff replenishes fixture
 -> inventory increases
 -> procurement cost event
 -> cash decreases
 -> replenishment work event recorded
```

and:

```text
explicit day-end
 -> daily cash summary
 -> optional SS-compatible negative-cash bankruptcy check
```

## `StoreRuntimeHarness`

`reference_sim/conveni_sim/store_runtime.py` composes:
- `StoreGrid`
- `DynamicTrafficHarness`
- `CustomerLifecycleHarness`
- `StoreStaffRoster`
- `CheckoutStationRuntime`
- `StoreInventoryRuntime`
- `StorePurchaseRuntime`
- `StoreCashLedger`
- `StoreCleaningRuntime`

It is intentionally a **headless composition layer**, not a new source of gameplay rules.

## Still caller-supplied / unresolved

The vertical slice does not decide:
- which customers spawn;
- which products they want;
- purchase quantity;
- add-on/impulse probability;
- staff task priorities;
- checkout duration;
- staff movement timing;
- stamina costs/recovery rates;
- automatic reorder point/quantity;
- dirt generation rate;
- customer-share formula;
- month-end aggregation.

This is deliberate. Strategy-guide or stronger observation data can later fill those policies while the connected state/data flow remains unchanged.

## Why this milestone matters

Before this point the repository contained separately testable pieces. After this milestone, the project has a single executable reference route from a customer's physical store visit through inventory and checkout into cash, plus a replenishment/cost route back into inventory.

That gives the future Android client a concrete gameplay-domain boundary to port instead of designing UI/art against disconnected mock values.
