# Decision 0081: Retain a cause-neutral sale ledger

## Status

Accepted.

## Context

The multi-product slice settled basket totals directly into cash and incremented a counter. That
proved the visible loop but discarded which customer bought which products and made it impossible
to reconcile completed sales with cash without reconstructing past mutable customer state.

Original receipt numbering, accounting storage, and exact transaction timestamps are not recovered.

## Decision

On successful checkout, append an immutable cause-neutral sale record containing:

- a prototype-local unique transaction ID;
- customer ID;
- current prototype minute-of-day;
- a deep copy of basket lines with product ID, quantity, and unit price;
- the computed transaction total.

Cash and completed-sale count derive from the accepted record. A customer can settle only once,
retains its transaction ID and settled total, and can be resolved back to its ledger entry. Reset
clears the ledger and restores its local sequence.

## Evidence boundary

The ledger records facts produced by the existing explicit prototype inputs. Its transaction-ID
format, timestamp granularity, storage shape, and UI presentation are PROVISIONAL and do not claim
to reproduce an original receipt or accounting subsystem. No demand, tax, cost, profit, or price
formula is introduced.

## Consequences

- Cash can be reconciled exactly against immutable completed transactions.
- Later observation export can consume stable customer/product/checkout facts.
- Mutating retained customer state cannot rewrite settled history.
- Refunds, voids, procurement cost, tax, daily reports, and persistence remain separate work.
