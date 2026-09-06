# Decision 0067: evidence-gated closed interior-edit dirt reset

## Context

First-title-only PS/SS research merged in PR #170 records a B+ community observation: entering interior edit while the store is outside business hours or temporarily closed clears all visible floor dirt.

The existing `StoreCleaningRuntime` already owns an explicit set of dirty floor cells and intentionally does not invent a dirt-generation rate. The new observation should therefore reuse that state instead of adding a parallel cleanliness model.

Several important facts remain unresolved: exact PS/SS platform coverage, whether the trigger occurs on entering or committing interior edit, whether an equivalent path exists while open, and whether the reset changes the separate store cleanliness parameter or customer-share state.

## Decision

Add an explicit `InteriorEditDirtResetPolicy` to `StoreCleaningRuntime`.

- Default behavior remains disabled and makes no platform claim.
- A caller may explicitly enable the observed compatibility rule.
- `enter_interior_edit(is_closed_for_business=...)` clears the current dirty-cell set only when both the policy is enabled and the caller states that the store is closed for business.
- The reset is recorded separately from ordinary staff cleaning actions.
- The reset does not create a staff work completion, stamina change, skill-growth opportunity, cleanliness-value mutation, customer-share recalculation, or cash event.
- The runtime does not decide whether the store is closed; business-hours / temporary-closure state remains the responsibility of the existing caller-side store-state boundary.

## Why this is evidence-safe

This models only the directly observed state transition and keeps uncertain causal details outside the runtime. It does not infer a numerical cleanliness effect or silently promote a B+ observation into a universal PS/SS default.

Keeping the behavior behind a replaceable policy also lets later direct footage or guidebook evidence narrow platform coverage or trigger timing without changing the dirty-cell representation.

## Explicitly unresolved

- PS and SS individual coverage.
- Whether opening, confirming, leaving, rebuilding, or loading a sample layout is the exact trigger.
- Behavior if an interior-edit path exists while the store is open.
- Whether the separate cleanliness parameter changes.
- Whether customer share/popularity is recalculated immediately afterward.
- Whether remodel, sale, layout load, or other edit flows share the same reset.
