# Decision 0043 — Apply checkout stamina effects only from explicit completion policy

Date: 2026-09-06

## Context

First-title evidence supports checkout/register work as a stamina-consuming work type, alongside replenishment and cleaning. The reference runtime already records checkout work completion for skill-growth opportunities, and timed checkout service can settle automatically across store steps, but checkout completion still has no path to consume stamina.

Replenishment/cleaning completion already accepts an explicit stamina cost and can enter the confirmed `RETURNING_TO_BREAK_ROOM` state. Leaving checkout disconnected would prevent an autonomous day from reproducing a staff member tiring from register work.

The exact checkout stamina cost and whether it varies by staff/register context remain unresolved.

## Decision

Extend `CheckoutServiceTimingCoordinator` with an optional `CheckoutServiceCompletionEffectsPolicy`.

The policy returns a `CheckoutServiceCompletionEffects` value containing:

- optional explicit `stamina_cost`;
- optional break-room target identifier.

When a timed checkout reaches its explicit duration:

1. completion effects are resolved and validated before settlement;
2. if a stamina cost is requested while the staff stamina value is unknown, the operation is rejected before cash/basket mutation;
3. the existing checkout sale path settles the basket and records the checkout work event;
4. the explicit stamina cost is then applied through the existing roster stamina state machine;
5. if stamina reaches zero, `StoreStepOrchestrator`'s existing rest coordinator sync registers the new return-to-break-room state for a later step.

## Evidence-safe boundary

This change does **not** define:

- a default checkout stamina cost;
- a formula relating register skill to stamina use;
- break-room travel duration;
- recovery amount/cadence;
- work interruption before checkout completion;
- customer abandonment or anger consequences;
- real-time/game-time mapping.

Omitting the effects policy preserves the prior no-stamina-mutation checkout behavior.

## Consequence

All three confirmed stamina-consuming store work families — checkout, replenishment and cleaning — can now feed the same evidence-safe return/rest/full-recovery lifecycle when an explicit policy supplies the currently unknown numeric effect.
