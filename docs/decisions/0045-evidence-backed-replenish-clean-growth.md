# Decision 0045: resolve only recovered replenish/clean growth increments

## Status
Accepted for the evidence-safe reference runtime.

## Context

The first-title dedicated staff research in `docs/research/staff-growth-penalty-recovery-2026-09-06.md` now gives explicit numeric growth for two work families:

- replenishment: +1 per completed replenishment action;
- floor cleaning: +1 per completed cleaning action.

The same source confirms register skill grows through checkout work, but does not recover the exact increment. It also supports separate normal growth caps and cap-bypass event behavior.

The runtime already records one `StaffGrowthOpportunity` for every completed checkout/replenish/clean work event, including the before value and normal base cap when known.

## Decision

Add an `EvidenceBackedStaffGrowthResolver` that:

- resolves replenishment opportunities by +1;
- resolves cleaning opportunities by +1;
- clamps normal growth to an explicitly known normal base cap;
- requires both the current skill value and normal base cap to be known;
- leaves checkout growth unresolved;
- leaves values already above the normal base cap untouched, preserving separate cap-bypass event semantics.

The resolver is optional at `StoreStepOrchestrator` composition time. When supplied, supported pending opportunities are evaluated after checkout and replenish/clean completion for that step.

## Evidence-safe boundary

This change does not define:

- the checkout/register growth increment;
- security or service growth triggers/rates;
- the mapping formula from hiring-screen education/agility/sociability to every individual base cap;
- manager-education modifiers beyond values already recorded on opportunities;
- a universal final stat cap;
- magazine-event growth amounts.

Unknown current values or caps remain pending instead of being converted to zero or guessed values.

## Evidence

- `docs/research/staff-growth-penalty-recovery-2026-09-06.md`, sections 3–6.
