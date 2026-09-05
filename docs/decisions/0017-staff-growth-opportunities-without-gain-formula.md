# Decision 0017 — staff work records growth opportunities without inventing gain formulas

Date: 2026-09-06

## Context

First-title staff research supports a two-layer staff model: hiring-screen attributes and runtime operational skills are distinct. It also supports these task-to-growth links:

- checkout work can grow register skill,
- replenishment work can grow replenishment skill,
- floor cleaning can grow cleaning skill.

Manager education affects subordinate growth speed, and ordinary work growth is constrained by per-skill base caps. However, the exact gain amount, manager-education multiplier, probability/rounding behavior and many individual starting values/caps remain unresolved. Security time-growth remains only provisional.

The original also has event-driven boosts that can exceed the ordinary base cap, so the runtime must not permanently clamp every stored value to that cap.

Primary research basis:
- `docs/research/staff-mechanics-model-2026-09-05.md`
- first-title staff/FAQ evidence already summarized under `docs/research/`

## Decision

1. Keep runtime skills and ordinary base caps as separate optional values on `StaffRuntimeState`.
2. Missing values remain absent/unknown; no zero/default skill is synthesized.
3. Completing checkout, replenishment or cleaning records a `StaffGrowthOpportunity` for the matching skill.
4. Recording an opportunity does **not** mutate the skill automatically.
5. Each opportunity captures the current subordinate work-event count plus the current manager identity and manager-education snapshot when known.
6. A future recovered growth policy, direct observation or controlled caller may resolve the opportunity by supplying the resulting skill value explicitly.
7. Normal work resolution may not exceed a known ordinary base cap.
8. Runtime values are nevertheless allowed to already exceed the base cap so future magazine/event boosts can be represented without data loss.
9. Do not generate automatic security/service/education growth from time or generic work until stronger evidence defines those triggers.

## Consequence

The simulator can now run work events and preserve every confirmed growth trigger before the guidebook tables and exact formula are known. Later data can be inserted without redesigning checkout/replenishment/cleaning flow: a recovered policy only needs to resolve queued opportunities.

The captured manager snapshot also prevents future policy code from accidentally applying a manager who was assigned after the work event occurred.

## Explicitly unresolved

This decision does not choose:

- `+1` or any other universal gain per action,
- manager education multiplier or thresholds,
- growth probability and rounding,
- exact individual starting runtime skills,
- exact individual cap exceptions,
- security growth timing,
- magazine-event gain amount,
- anger penalty exactness or timing.

Those remain data/research inputs rather than guessed engine constants.
