# Decision 0033 — permit application triggers are evidence-configurable

Date: 2026-09-06

## Context

Decision 0022 initially kept `NEW_STORE` present but blocked because the first-title evidence available at that time directly confirmed only the Saturn remodel path.

New first-title PlayStation research in `docs/research/ps-permit-type-specific-eligibility-2026-09-06.md` now directly records permit applications during new-store setup. The same research also shows that permit eligibility can differ by permit type at one site. It does not establish the Saturn new-store UI or the PlayStation remodel UI, nor does it recover exact exclusion distances or fees.

Hard-coding both application triggers as universally available would therefore overgeneralize evidence across platform paths. Continuing to hard-code `NEW_STORE` as unavailable would ignore the newly recovered PS evidence.

## Decision

1. `StorePermitRuntime` accepts an explicit set of `confirmed_application_triggers`.
2. The existing default remains `REMODEL` so current Saturn-oriented callers keep their prior behavior.
3. A PS evidence profile can explicitly enable `NEW_STORE` without implying that the same path is confirmed on Saturn.
4. An application through a trigger outside the configured evidence profile returns `TRIGGER_UNCONFIRMED` and mutates neither ownership nor cash.
5. Eligibility remains a per-permit explicit input (`ELIGIBLE`, `INELIGIBLE`, `UNKNOWN`). The runtime does not derive it from distance or nearby stores.
6. Permit fees remain data-driven/unknown-capable. No later-series fee or exclusion-distance value is imported.
7. The ledger note records the actual application trigger rather than assuming remodel.

## Consequence

The runtime can now replay the newly evidenced PS new-store permit flow while preserving a strict boundary between PS and SS confirmation. Future guidebook or video evidence can add a platform/revision profile at the composition layer without changing permit acquisition logic.

Decision 0022 remains historical context; its statement that the new-store path is unconfirmed is superseded only to the extent described here.

## Deferred

- exact tobacco/alcohol/medicine fees;
- exclusion distances and geometry;
- the formula/input used to determine per-type eligibility;
- PS remodel application UI;
- SS new-store application UI;
- whether permits can later be revoked or invalidated by nearby store changes;
- affordability behavior while a fee is unknown;
- platform/revision profile selection at the game-composition layer.

Later-series permit numbers and rules remain out of scope.
