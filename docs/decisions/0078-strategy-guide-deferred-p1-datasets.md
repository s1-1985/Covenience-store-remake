# Decision 0078: Transcribe the strategy guide's deferred P1 datasets

## Status

Accepted.

## Context

Decisions 0076 and 0077 implemented the strategy guide's P0 (small, high-confidence)
data, and deferred five large tables as P1 per the guide's own section 44 instruction
("画像の行対応を手作業で確認すること" — large tables need manual image-row
cross-checking): a named staff-candidate roster, a customer-archetype visit-schedule
table, a general town-building demand table, a fixture x product-category compatibility
matrix, and per-category restock-quantity/seasonal-flag data.

The user asked directly whether more of the already-available scan data could be
implemented, and, on realizing the P1 tables were sitting in the same already-read PDF
files with no external blocker, asked for them to be transcribed rather than deferred
again. This decision covers that follow-up pass.

## Decision

Re-read the specific guide pages at full attention and transcribed:

- **`STAFF_CANDIDATES`** (`baseline_data.py`, new): 35 named staff candidates
  (book pages 127-133), each with age, hourly wage (`salary_yen_per_day_24h` derived as
  `hourly_wage * 24`, per the guide's own payroll formula), and the 5 skill stats plus
  stamina/agility/academic_background/sociability/education. One candidate's printed
  `security_skill` digit could not be read with confidence and was left `None` rather
  than guessed.
- **`CustomerVisitProfile`** (new dataclass, `models.py`) + **`CUSTOMER_ARCHETYPES`**
  (21 archetypes) + **`CUSTOMER_VISIT_SCHEDULE`** (140 rows, `baseline_data.py`,
  book pages 134-143): the guide's per-archetype, per-visit-time-slot table (arrival
  time, duration, arrival method, budget, wanted products). This is a new, separate
  dataclass rather than a forced fit into the existing coarse
  `CustomerArchetypeDefinition` (which stays populated only with `display_name`/
  `visual_archetype`, and still reports its own research fields — spending power,
  preferred products, patience/anger profile — as unknown; those are a different,
  still-unresolved concept). The guide's 9-column per-row behavioral tuning stats
  (ス/素/マ/集/買/価/距/サ/平/休) are kept as a single raw tuple
  (`behavior_stats_raw`) rather than 9 separately-named fields, because the exact
  digit count printed per row was not always legible as a clean 9-tuple at the source
  scan's resolution — mapping uncertain digits to specific named fields would have
  presented false precision.
- **`TownBuildingProfile`** (new dataclass) + **`TOWN_BUILDINGS`** (59 buildings,
  book pages 92-95): general town-building size/price/wanted-products/day-or-24h
  profiles. Distinct from `TownFacilityAnchor` (the smaller set of *inducible*
  facilities with an aid amount) — this is a broader "what's already on the map"
  table. The page's second, product-combo-keyed frequency table (deep-night-hours
  counts) was not tied to specific buildings and was not transcribed, since forcing
  a building mapping onto it would have been invented, not read.
- **`FixtureDefinition.compatible_product_categories`** filled in for ~30
  `STRATEGY_GUIDE_FIXTURES` rows and for `copier_a`/`copier_b`, sourced from each
  fixture's own "取扱商品" text column on the guide's per-fixture data pages
  (book pages 110-119) rather than the guide's separate fixture x category ○/×
  matrix elsewhere — the same information, read from a much more reliable source
  (large-font per-fixture text lists vs. a dense small-font 30-row x 26-column
  symbol grid). Registers with no listed product ("取扱商品: なし") and the break
  rooms are correctly left `None`.
- **`ProductCategoryPricing.seasonal_demand`** filled in for the 4 categories the
  guide's product table clearly flags as seasonal (`cold_drink`/`ice_cream` =
  summer, `hot_drink`/`oden`/`chinese_steamed_bun` = winter). The same table's other
  two numeric columns ("1回補給" restock quantity and a third, unlabeled column)
  were not transcribed — their exact column semantics could not be confidently read
  at the source resolution, and the accompanying sidebar text suggests they may be a
  derived "demand fluctuation example" rather than a flat constant, which would need
  further primary-source confirmation before being treated as `EXPLICIT_NUMERIC`.

## Evidence boundary

All new values are `EvidenceLevel.CONFIRMED_OFFICIAL` citing `STRATEGY_GUIDE`. Where a
specific digit or column could not be read with confidence, the field was left `None`
rather than guessed (the one staff `security_skill`, the two unlabeled DATA1 numeric
columns, the deep-night product-frequency table). This is a larger, denser transcription
pass than 0076/0077; per-digit confidence on the 9-column customer behavior-stat tuples
in particular is lower than on the large-font price/date/table data transcribed
earlier, and is flagged as such rather than asserted with equal confidence.

Tests: `reference_sim/tests/test_strategy_guide_deferred_datasets.py` covers row counts,
uniqueness, cross-references between the new tables and existing
`PRODUCT_CATEGORY_PRICING` ids, the one intentionally-`None` staff skill, the
intentionally-`None` register/break-room product categories, and the seasonal flags.
Existing tests were updated only where they asserted the old (now-filled) `None`/absent
state (`copier_a`/`copier_b` compatible_product_categories).
