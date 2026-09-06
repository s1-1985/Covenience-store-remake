# 0063 — Replay observed replenish/clean assignment starts with explicit targets

## Decision

Explicit in-coverage `REPLENISH_START` and `CLEAN_START` observations may drive staff task assignment when the caller explicitly opts in and supplies an explicit mapping from the observed target identifier to the runtime target id.

The replay policy receives the factual current in-game minute from `StoreStepOrchestrator`. It will not start an observed task before its annotated minute. If the mapped target is not currently an objective work candidate, the rule remains pending; the policy does not fall back to another shelf, floor cell or task.

For replenishment, observed fixture ids must be mapped explicitly to runtime inventory-slot ids. For cleaning, the observation note used as a target label must be mapped explicitly to a runtime cleaning target id.

## Why

The shared observation vocabulary already records replenish/clean starts. Replaying these events removes the synthetic staff task-priority/start-time assumption for observed windows without pretending that the original autonomous priority formula has been recovered.

## Safety boundary

This does not establish:

- an original staff priority formula,
- checkout interrupt thresholds,
- automatic observed-fixture to inventory-slot inference,
- automatic floor-cell inference,
- fallback target selection,
- a duration, stamina or quantity rule,
- sub-minute timing or video/game-time conversion.

Observed start replay is intentionally strict: missing target evidence remains unresolved rather than being approximated.