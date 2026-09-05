# Decision 0010 — Keep cash events explicit and day-end bankruptcy platform-gated

Date: 2026-09-05

## Decision

Introduce an explicit store cash ledger now, but do not invent the unresolved month-end aggregation formula or silently convert unknown costs to zero.

A detailed Saturn play record reports bankruptcy when cash is negative at the end of a day. Until PS parity is independently confirmed, this remains an opt-in policy for SS-compatible experiments rather than the shared default.

## Evidence basis

Current first-title research supports:
- sales increase cash;
- replenishment purchases decrease cash;
- during closed hours, labor and many operating costs are not charged;
- staff can still clean/replenish while the store is closed;
- replenishment purchases can therefore still reduce cash while closed;
- a Saturn play record reports game over if cash is negative at the end of the day;
- the day-5-to-month-end aggregation formula is still unresolved.

Relevant research:
- `docs/research/research-checkpoint-2026-09-05.md`
- `docs/research/behavior-rules-evidence-2026-09-05.md`
- `docs/research/ss-permit-cleaning-customer-actions-2026-09-05.md`

## Runtime boundary

Implement now:

```text
StoreCashLedger
- initial cash
- ordered financial events
- explicit credits/debits
- sale revenue event
- procurement event bridge from InventoryMutation
- explicit labor cost event while open
- unknown amount preservation
- per-day summary window
- cumulative known cash

BankruptcyPolicy
- check_negative_cash_at_end_of_day: bool

DayEndOutcome
- SOLVENT
- BANKRUPT
- UNDETERMINED
- NOT_EVALUATED
```

If any prior cash-affecting event is still unknown, the exact cash balance is not claimed. A bankruptcy check that depends on exact cash must therefore return `UNDETERMINED` rather than treating the missing amount as zero.

## Closed-hours handling

The current evidence is strong enough to make labor suppression explicit:

```text
store_open == false -> do not charge labor
```

However, the evidence says **many** operating costs stop rather than enumerating every category. Therefore this decision does not automatically suppress fixture maintenance or every other expense while closed. Those categories remain explicit until the exact charging rules are recovered.

Replenishment procurement remains independent of the store-open flag because the first-title evidence explicitly reports that staff may replenish while closed and the purchase cost still occurs.

## Deliberately unresolved

Do not invent:
- representative-4-day to month-end multiplier/aggregation;
- exact operating-cost schedule for every category;
- salary prorating formula for shorter opening hours;
- exact fixture-maintenance charge timing;
- PS parity of Saturn's end-of-day bankruptcy timing;
- sales-tax/rounding behavior if any;
- any rule that resolves unknown monetary values to zero.
