# Decision 0051 — Keep checkout anger timing policy-driven

## Decision

Track each checkout-required customer's factual checkout timing in the reference simulator:

- first minute observed in `WAITING_CHECKOUT`;
- start of each contiguous active checkout-service segment;
- pre-service wait elapsed time;
- active-service elapsed time;
- total checkout elapsed time;
- current active cashier, when one exists;
- current queue/service counts.

A replaceable `CheckoutAngerTriggerPolicy` decides whether those facts are sufficient to trigger anger. The timing coordinator itself does not define a patience threshold or decide whether queue wait, active service, or their sum is the original trigger.

When a policy requests anger while a cashier is actively serving the customer, the coordinator records the already recovered checkout-anger penalty through `CheckoutAngerPenaltyRuntime`. The same customer cannot trigger the penalty repeatedly during one checkout lifecycle.

If a policy requests anger while no cashier is active, no employee is guessed. The request remains non-consuming and may be evaluated again later.

## Why

First-title research supports the consequence of checkout anger, including the -2 work-skill penalty, but the exact anger/patience condition is still unresolved. Video observation also needs to distinguish time spent merely waiting from time spent actively being processed by a cashier.

## Store-step ordering

Existing checkout pressure is evaluated immediately after the game clock advances and before timed checkout completion. This prevents a threshold reached on the completion step from being skipped by settlement.

Newly waiting customers and newly started services are timestamped later in the same step but are not evaluated again until a later step, preventing zero-time anger events.

## Not decided here

This decision does **not** define:

- customer patience duration;
- whether queue wait contributes to anger;
- whether only active register processing contributes;
- register-skill-to-patience or duration formulas;
- anger animation duration;
- abandonment behavior;
- which employee receives a consequence when anger occurs before service;
- any runtime skill floor for the -2 consequence.
