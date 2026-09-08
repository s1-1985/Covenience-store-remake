# Decision 0083: Admit observed customers with explicit identity and product plan

## Status

Accepted.

## Context

Customer rosters retained completed visits, but every admission still used an auto-generated ID and
one scenario-wide product plan. An observation replay could not preserve an external customer label
or provide a different directly observed product order without replacing the default prototype data.

Original demand, arrival timing, product selection, and incidental-purchase policies remain
unrecovered.

## Decision

Keep the existing default manual-admission control and add a separate explicit admission boundary
that accepts:

- a caller-provided unique customer ID; and
- a nonempty ordered list of known product IDs.

Reject admission while another customer is active, duplicate/empty IDs, unknown products, duplicate
products in one plan, empty plans, and plans whose required route is unreachable. Record the accepted
plan with the cause-neutral `customer_entered` event.

The headless harness exercises this boundary with a reversed explicit product order and confirms
that the provided identity is retained and cannot be admitted twice.

## Evidence boundary

This API accepts already-observed or deliberately scripted facts. It does not decide when a customer
arrives or what they want. The default plan, the smoke plan, ID format, validation constraints, and
one-active-customer restriction remain PROVISIONAL rather than original demand rules.

## Consequences

- Future video/emulator adapters can preserve observation-local customer identity and product order.
- Default UI admission continues to use the isolated prototype scenario plan.
- Arrival scheduling, concurrent customers, repeated product visits, quantities, substitutions, and
  incidental purchases remain separate policy work.
