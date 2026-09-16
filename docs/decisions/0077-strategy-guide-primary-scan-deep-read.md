# Decision 0077: Deep-read the strategy guide's primary page scans directly

## Status

Accepted.

## Context

Decision 0076 implemented P0 data from `docs/research/strategy-guide-full-decode-2026-09-16.md`,
Codex's own summary of the strategy guide. The user then supplied the original scanned pages
themselves (4 PDFs, 115 pages total, covering both the "新人店長実習マニュアル/攻略&データ
ブック" volume and the "レイアウトデザインセレクション" companion volume) and asked Claude Code
to read them directly and thoroughly, noting that Codex's summary had focused mainly on the
tabular data pages and that other pages (narrative strategy sections, Q&A, an "オール
テクニックガイド" formulas section, and a "DATA LIST" appendix) contain additional
implementation-relevant material the summary did not carry forward.

Per the roles-and-workflow.md exception clause, this is again a one-off explicit request to work
directly in `reference_sim/conveni_sim/`.

## Decision

Read all 115 pages across all 4 files page-by-page (poppler-utils installed to render PDF pages,
since the scans carry no text layer). Findings are recorded in
`docs/research/strategy-guide-fixture-crosscheck-2026-09-16.md` (extended) rather than a fresh
file, since they update or extend the same cross-check this decision's predecessor already
started.

Implemented from the primary scan (all either fill previously-`None` fields or are backed by
multiple independent primary-source confirmations that outweigh the source decision 0076 already
recorded a conflict against):

- **Resolved the airship/radio/tv promotion-popularity conflict** flagged in decision 0076: the
  guide's own advertising-data page and its separate "オールテクニックガイド" page both print
  +40/+60/+90, independently of the earlier full-decode summary reading. `PROMOTIONS` now uses
  these values (`CONFIRMED_OFFICIAL`); `cost_yen`/`trigger_day`/`trigger_hour` were already
  correct and untouched.
- **Corrected `SalaryTableEntry`'s field name and label**: the guide prints the table as
  "年齢別・社員の基本時給" (hourly, not monthly), and a separate page gives the exact
  generating formula `hourly_wage_yen = age_years * 10 + 100`, which reproduces every existing
  table point. Renamed `monthly_salary_yen` -> `hourly_wage_yen` in `models.py`; the numbers
  themselves were already correct.
- **Filled in previously-`None` `STORE_VARIANTS.construction_price_yen`** for
  `small_bottom`/`medium_top`/`medium_bottom`/`large_top`/`large_bottom` (6M/12M/12M/18M/18M
  yen), derived from a precise 6-row store-data table that also resolved most of the ambiguity
  decision 0076 flagged around the old `store_1..5` figures from the full-decode summary. No
  `editable_floor` value was touched — see the crosscheck note for a newly-found *internal* guide
  conflict (18,000,000 vs. 24,000,000 for the large tier, 7 sources vs. 1) and remaining
  `editable_floor` mismatches that stay unresolved.
- **Added `service_bonus` for `potted_plant`** (+2, matches the existing value exactly) and
  discovered (but did not apply, per the never-silently-overwrite policy) a numeric conflict on
  `bench` (existing +3 vs. guide +4) and `fountain` (existing +25 vs. guide +30).
- **Added a `TownFacilityAnchor.footprint` field** (`models.py`) and used it, together with a
  newly-read inducement-facility table, to add 12 new facilities (`mansion`, `gym`,
  `athletic_field`, `event_hall`, `kindergarten`, `elementary_school`, `middle_school`,
  `high_school`, `park`, `aquarium`, `zoo`, `amusement_park`) and to backfill previously-`None`
  `footprint`/`shopping_population` fields on the 6 pre-existing facilities that this table
  independently re-confirmed 6-for-6 against their existing `inducement_aid_yen` values.

## Not implemented this pass (recorded for follow-up)

The guide's "オールテクニックガイド" (all-technique guide) section prints several complete
formulas — store service/security/cleaning value, new-store land cost, promotion decay, the
full 5-star rating increase/decrease table, and a precise event-trigger table (donation,
shoplifting, fire/robbery, magazine feature, contest, idol) — none of which are wired into
`conveni_sim`'s runtime this pass. Connecting them to `store_runtime.py`/`checkout.py`/
`promotion.py`/`monthly_report.py` requires checking for overlap with existing logic and new
tests, which is a distinct engineering task from data import. All formulas are transcribed in the
crosscheck research note for that follow-up.

Also confirmed to exist and be readable, but deferred as P1 per the guide's own section 44
instruction (large tables needing manual image-row cross-checking): a ~30-person named staff
candidate roster, a ~20-archetype customer schedule/preference table, a ~40-building
customer-demand table, a complete fixture x product-category compatibility matrix, and
per-category restock-quantity/seasonal-flag data.

## Evidence boundary

All new values are `EvidenceLevel.CONFIRMED_OFFICIAL` citing the same `STRATEGY_GUIDE` source
already used by decision 0076 (the scans are the same physical source; only the reading method
changed from summary to primary). No formula was invented — every one transcribed here is printed
verbatim in the guide.

Tests: `reference_sim/tests/test_strategy_guide_primary_scan.py` covers the promotion fix, the
preserved (not-overwritten) service_bonus conflicts, the new store-variant prices, the new/backfilled
town facilities, and the hourly-wage formula. Existing tests were updated only where they asserted
the old (now-filled) `None` state.
