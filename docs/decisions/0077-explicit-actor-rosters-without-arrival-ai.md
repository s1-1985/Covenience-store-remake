# Decision 0077: Retain explicit actor rosters without inventing arrival AI

## Status

Accepted.

## Context

Decision 0076 extracted reusable customer and staff state objects, but the vertical-slice
orchestrator still held exactly one instance of each. Reusing that customer instance for every
visit also discarded the identity and terminal state of prior visits.

The original game's concurrent arrival timing, collision rules, checkout queue selection, and
general staff task assignment are not sufficiently recovered. Adding automatic or overlapping
actors here would silently turn prototype behavior into an unsupported compatibility claim.

## Decision

Add engine-native customer and staff rosters while preserving the explicit prototype boundary:

- every manual admission creates and retains a uniquely identified `CustomerState`;
- only the current customer may be active, and another admission is rejected until it is done;
- completed customer states remain available for validation and later observation tooling;
- every configured staff member receives an independent `StaffState`;
- the provisional data explicitly identifies which configured staff member serves the scripted
  checkout instead of guessing a task-selection policy.

The vertical-slice data schema advances to version 2 to make those collection inputs explicit.
The same schema identifies the product shelf and checkout fixture by ID so the runtime does not
silently select the first fixture of a matching kind once layouts contain several fixtures.

## Evidence boundary

The rosters are storage and identity boundaries, not original simulation rules. Sequential manual
admission does not claim that original customers arrive one at a time. The configured checkout
staff does not claim an original dispatch priority. Concurrent movement, congestion, queues,
staff selection, and demand remain unresolved and must be introduced only behind evidence-backed
or explicitly PROVISIONAL policies.

## Consequences

- A visit no longer mutates an earlier customer's terminal state back into an active state.
- Smoke validation can assert unique IDs and one retained terminal state per visit.
- Multiple staff can be represented without inventing autonomous work selection.
- A later explicit arrival replay or provisional scheduler can create actors through the same
  roster boundary.
