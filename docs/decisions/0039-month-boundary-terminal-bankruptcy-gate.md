# Decision 0039: month-boundary terminal bankruptcy gate

## Status
Accepted for the evidence-safe reference runtime.

## Context

First-title PS footage in `docs/research/video-v03-october-bankruptcy-2026-09-06.md` shows 1Y Oct 4 23:58 cash at ¥697,211, followed by 1Y Nov 1 00:00 cash at -¥121,360 and an immediate bankruptcy message/splash. The ordinary monthly report and sales/rank notifications are not shown before the terminal sequence. Earlier SS research independently supports negative-cash bankruptcy at a day boundary.

The footage does not reveal the components of the ¥818,571 month-boundary debit, and no zero-cash boundary sample exists. The four representative-day aggregation formula is also unresolved.

## Decision

Add a `MonthBoundaryTerminalGate` that is evaluated only after caller-controlled, evidence-backed settlement events have already been written to `StoreCashLedger`.

The gate:

- treats exact negative cash as bankruptcy under the currently supported first-title rule;
- exposes bankruptcy as a terminal outcome that suppresses ordinary month-start presentation;
- keeps zero cash `UNDETERMINED` until a zero-balance sample or source resolves the comparison operator;
- keeps any ledger containing unknown cash effects `UNDETERMINED`;
- allows the zero-cash rule to be supplied later as data/policy without changing orchestration code.

## Explicit non-decisions

This change does not define:

- month-end or month-start settlement components;
- the ¥818,571 observed delta as a reusable formula or constant;
- 4 representative days → monthly financial aggregation;
- ordering among individual settlement components;
- whether a monthly report can be reopened after the bankruptcy splash;
- the exact zero-cash bankruptcy rule.

## Consequence

Month-boundary orchestration can now preserve the observed terminal ordering without fabricating any financial formula. Future guidebook values can populate settlement data independently of the terminal gate.
