# Decision 0034 — manager magazine event uses an explicit unresolved growth boundary

Date: 2026-09-06

## Context

First-title-only research added in PR #125 confirms an event in which a store with high cleaning can have its manager featured in a magazine, after which the manager's abilities rise.

Confirmed:

- the event exists in the 1997 PS/SS title;
- store cleaning is related to eligibility;
- manager ability values rise after the feature.

Still unknown:

- required cleaning threshold;
- event probability;
- evaluation/firing timing;
- which staff skills rise;
- per-skill increase amounts;
- repeatability for the same manager;
- PS/SS differences.

## Decision

Add `ManagerMagazineEventRuntime` as an explicit event ledger attached to `StoreRuntimeHarness`.

Recording the event requires an external observation/future policy call. The runtime does not inspect cleaning and decide eligibility by itself. `observed_cleaning` may be retained when known, but `None` remains a valid unknown value.

Recording creates an unresolved opportunity and snapshots the current manager skill values. It does not mutate any skill.

A separate explicit resolution call accepts observed/calculated post-event skill values and applies only those supplied values. Known skills may not be reduced by an event whose confirmed direction is growth.

## Evidence-safe boundary

This does not encode a threshold, probability, schedule, affected-skill set, growth delta, repeat rule or platform-specific behavior. Those can be supplied later from gameplay observation or guidebook data without changing the event ledger contract.

## Source

- `docs/research/customer-share-weather-hours-and-head-store-bias-2026-09-06.md`

No sequel values or behavior are used.
