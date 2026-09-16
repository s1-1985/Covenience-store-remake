# Decision 0085: Staff skill growth ceilings from the guide's per-candidate cards

## Status

Accepted.

## Context

Decision 0080 found a second growth-ceiling number per skill for all 35 staff candidates in
the strategy guide's consolidated DATA LIST table (book pages 90-91), but declined to
transcribe it: a cross-check on that specific table produced a mismatch (秋本三四郎's
`academic_background` read as `65` there against an already-confirmed `70`), which meant
the compact table's dense, small-font layout could not be trusted for column alignment.

The user pushed back explicitly on leaving this flagged-but-undone, and asked for the data
to actually be incorporated rather than reported as a gap. This decision covers that
follow-up: the same growth-ceiling numbers exist a second time, in a different, much more
reliable source already partially read earlier in this session — the guide's large-font,
explicitly-labeled per-candidate cards (book pages 126-133, one card per person, with a
numbered legend on page 126 defining exactly what each field means).

## Decision

Added `StaffDefinition.{service,register,cleaning,replenishment,security}_skill_growth_ceiling`
(new `Optional[EvidenceValue]` fields, `models.py`) and populated all 35 candidates in
`STAFF_CANDIDATES` (`baseline_data.py`) from these per-candidate cards.

**Verification, not just a second guess:** before trusting a single ceiling digit, every
candidate's already-confirmed initial skill set (`service_skill`/`register_skill`/
`cleaning_skill`/`replenishment_skill`/`security_skill`, sourced from these same cards in
an earlier pass, decision 0078) was read back from this card and compared against the
existing `STAFF_CANDIDATES` values. All 34 candidates with a known security_skill matched
on all 5 initial values, digit for digit — unlike the compact DATA LIST table, this source
does not exhibit the earlier alignment problem. The one candidate whose initial
`security_skill` is `None` (丸山昭夫) still has all 5 growth-ceiling values transcribed,
since the ceiling is read from a separate, independently legible cell on the same card.

Also confirmed and folded into `CustomerVisitProfile`'s docstring (`models.py`): the same
page's numbered legend (items 7-17) gives full, unambiguous definitions for the customer
visit table's ス/素/マ/集/買/価/距/サ/平/休 column abbreviations
(stamina/quickness/manner/focus/shopping-importance/price-sensitivity/distance-sensitivity/
service-sensitivity/weekday-share/holiday-share) — previously only abbreviated without a
confirmed definition. **Not decomposed into 10 named fields**, despite a dedicated second
re-read attempt this pass: re-parsing the same archetype's adjacent data rows independently
produced different digit counts (9 vs. 11) at the available scan resolution, the same kind
of inconsistency that blocked this the first time (decision 0078). Unlike the staff-skill
case above, there is no independently-known reference value to cross-check a customer row
against, so this gap is reported honestly rather than papered over with an unverifiable
row-to-field mapping.

## Evidence boundary

Growth ceilings are `EvidenceLevel.CONFIRMED_OFFICIAL` citing `STRATEGY_GUIDE`, justified by
the 34/34 cross-check above. The customer-table column *labels* are now confirmed with the
same evidence level; the per-row *values* remain in `behavior_stats_raw` as before, with the
reason now stated precisely (digit-count inconsistency, not incomplete effort).

Tests: `reference_sim/tests/test_strategy_guide_deferred_datasets.py`
(`StaffGrowthCeilingTests`) checks all 35 candidates have all 5 ceilings, spot-checks two
candidates' exact values, and asserts ceiling >= initial for every known pair (an internal
consistency check that passed for all 35 without needing any adjustment). Full suite: 557
passed, 1 xfailed (pre-existing, unrelated).
