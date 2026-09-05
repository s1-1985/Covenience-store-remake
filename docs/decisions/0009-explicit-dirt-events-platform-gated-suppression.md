# Decision 0009 — Model dirt as explicit events and keep cleaning-100 suppression platform-gated

Date: 2026-09-05

## Decision

Add a floor dirt/cleaning runtime now, but do not invent a dirt-generation rate. Keep the observed Saturn rule that cleaning 100 suppresses new dirt behind an explicit policy rather than making it a shared PS/SS default.

## Evidence basis

First-title research supports:
- floor cleaning is a distinct staff task;
- completing floor cleaning is a confirmed cleaning-skill growth trigger;
- cleaning work consumes stamina;
- store cleaning is one of the known customer-share inputs;
- a detailed Saturn play record reports that once cleaning reaches 100, the floor no longer becomes dirty.

The cleaning-100 statement is currently SS-specific community evidence. PS parity is not yet independently confirmed.

Relevant research:
- `docs/research/staff-mechanics-model-2026-09-05.md`
- `docs/research/behavior-rules-evidence-2026-09-05.md`
- `docs/research/ss-permit-cleaning-customer-actions-2026-09-05.md`

## Runtime boundary

Implement now:

```text
StoreCleaningRuntime
- explicit dirty-cell set
- explicit dirt events
- explicit cleaning actions
- one completed CLEAN work event per successful cleaning invocation
- optional explicit stamina cost
- cleaning history

DirtGenerationPolicy
- suppress_at_cleaning_value_or_above: Optional[int]
```

Default policy uses no suppression threshold.

A Saturn-compatible experiment may explicitly set:

```text
suppress_at_cleaning_value_or_above = 100
```

without asserting that value as a universal console invariant.

## Deliberately unresolved

Do not invent:
- dirt spawn probability/rate;
- dirt spawn locations;
- number of cells cleaned per original animation/action;
- exact mapping from staff cleaning skill to cleaning speed;
- cleaning stamina cost;
- PS parity of the SS cleaning-100 suppression behavior;
- cleaning contribution to the customer-share formula.

Dirt generation is therefore event-driven in the reference layer. Later observation/video/guide evidence can supply a generation policy without rewriting the store grid or staff runtime.
