# Decision 0082: Export a cause-neutral runtime event log

## Status

Accepted.

## Context

The production slice retained final customer state and completed sales, but intermediate facts such
as reaching a shelf, encountering unavailable stock, starting checkout, and exiting were reduced to
one mutable display string. That prevented deterministic runs from being compared with observation
timelines without reconstructing events from final state.

Original event IDs, internal logs, timestamp precision, and causality fields are not recovered.

## Decision

Add an append-only runtime event log with a local contiguous sequence, prototype minute-of-day,
event type, and deep-copied factual details. Record explicit events for admission, reaching planned
products, pickup/unavailability, checkout start/completion, exit, and accepted fixture edits.

Expose a versioned observation snapshot containing the event log, sale ledger, and current inventory.
The export is explicitly marked `provisional: true` and names its source scenario. Reset clears prior
events and begins the new run with its initial explicit admission.

## Evidence boundary

The event log describes what this deterministic prototype did; it does not assert that the original
game used these event names, ordering keys, timestamps, or storage format. Event records remain
cause-neutral: for example, an unavailable product is recorded without inferring demand substitution
or customer patience. This is a comparison/export seam, not an original simulation formula.

## Consequences

- Intermediate runtime facts survive beyond the last HUD message.
- Snapshots can be compared with future video/emulator observation adapters.
- Deep copies prevent consumers from rewriting recorded history.
- Calendar dates, original event taxonomy, replay import, persistence, and confidence/evidence tags
  remain separate work.
