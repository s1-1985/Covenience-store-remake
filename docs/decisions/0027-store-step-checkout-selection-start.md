# Decision 0027 — Allow store steps to start, but not finish, checkout service

Date: 2026-09-06

## Decision

A caller-driven `StoreStepOrchestrator` may optionally run the replaceable checkout-customer selection policy after staff task selection.

The resulting step order is:

1. advance caller-supplied game minutes,
2. optional customer demand evaluation,
3. one customer traffic tick,
4. optional purchase decisions,
5. optional staff work discovery and task selection,
6. optional checkout customer selection and service start.

If a staff member was assigned to checkout in step 5 and a waiting customer is selected in step 6, service may begin in the same explicit step.

## Critical boundary

Starting checkout service is not completing checkout service.

The store step does not:

- advance a guessed checkout duration,
- settle the customer's basket,
- credit sale revenue,
- complete the customer checkout state,
- release the staff member.

Those remain pending until `finish_checkout_sale(...)` is called by an explicit observation/replay or a future recovered service-timing policy.

## Active services

A staff member already serving a customer is skipped by checkout selection on later store steps. This prevents repeated selection while leaving service duration unresolved.

## Why

This creates an executable chain from customer demand through physical shopping and staff assignment to the beginning of checkout service, while preserving the main dynamic unknown that video analysis is expected to recover: how long checkout actually takes under different staff/register conditions.

## Still unresolved

- checkout selection rule,
- service duration formula,
- exact service completion tick,
- two-person register cooperation,
- stamina interruption,
- queue abandonment,
- staff movement/travel to the register,
- original reconsideration cadence.
