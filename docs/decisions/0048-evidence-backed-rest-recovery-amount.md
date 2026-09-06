# Decision 0048: recover the 1-or-2 stamina amount without inventing timing or agility probability

## Status
Accepted for the evidence-safe reference runtime.

## Context

First-title dedicated staff research reports that staff resting in the break room normally recover 1 stamina at a recovery event, and sometimes recover 2. The chance of the +1 bonus increases with agility. The source gives only a player estimate for agility 100 and does not recover the probability curve or the interval between recovery checks.

The existing rest timing coordinator deliberately requires a caller-supplied transition policy and does not contain a recovery constant.

## Decision

Add:

- `EvidenceBackedRestRecoveryResolver`, which represents the recovered base +1 and optional +1 bonus;
- `RestRecoveryBonusPolicy`, which decides `True`, `False`, or `None` for the unresolved agility-linked bonus;
- `EvidenceBackedIntervalRestPolicy`, which requires explicit break-room return time and recovery-check interval, then emits a recovery transition of exactly 1 or 2 only when the bonus decision is resolved.

If the bonus policy returns `None`, the exact recovery amount remains unresolved and the eligible recovery tick does not mutate stamina or consume its timing baseline.

## Evidence-safe boundary

This change does not define:

- the time interval between recovery events;
- an agility-to-probability formula;
- a random-number generator or seed;
- the player-estimated agility-100 ~90% value as a hard-coded probability;
- any effect of walking, work type, manager education, or store state on recovery.

## Evidence

- `docs/research/staff-growth-penalty-recovery-2026-09-06.md`, section 8.
