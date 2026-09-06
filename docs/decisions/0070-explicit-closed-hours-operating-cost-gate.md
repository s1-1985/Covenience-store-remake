# 0070 — Explicit closed-hours operating cost gate

## Decision

Add a generic `record_operating_cost_if_open(...)` seam to `StoreCashLedger`.

The seam only decides whether a caller-classified operating cost accrues while the store is open to customers. It does not calculate any wage, maintenance rate, hourly coefficient, rounding rule, or category membership.

`record_labor_cost_if_open(...)` remains as a compatibility wrapper over the new generic gate.

Procurement is explicitly rejected by the operating-cost gate and continues to be recorded through `record_procurement_mutation(...)`, because first-title evidence indicates that staff may continue restocking while closed and the corresponding procurement spending can still reduce cash.

## Evidence

`docs/research/closed-hours-cost-boundary-2026-09-06.md` records first-title PS/SS dedicated FAQ evidence that:

- labor and other operating/maintenance costs stop while closed or temporarily closed;
- staff cleaning/restocking may continue while closed;
- replenishment procurement spending can therefore remain active during closed hours.

## Evidence-safe boundary

This change intentionally leaves the following UNKNOWN:

- which exact maintenance categories are governed by the closed-hours rule;
- whether all fixture costs behave identically;
- proportionality to open minutes/hours;
- wage and maintenance rates;
- rounding and charge timing;
- parity between normal closed hours and temporary closure;
- PS/SS differences.

The caller must therefore classify a cost as operating before using the gate. Unknown amounts remain `None` and continue to make the cash ledger inexact rather than being treated as zero.

## Consequences

The economy runtime can now represent the observed structural distinction without inventing numeric tables: operating-cost accrual can stop during closure while inventory procurement remains independently chargeable. Future guidebook data can populate rates and category mappings without changing this boundary.
