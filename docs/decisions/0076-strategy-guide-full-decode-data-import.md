# Decision 0076: Import strategy-guide full-decode data into baseline_data.py

## Status

Accepted.

## Context

The user supplied `docs/research/strategy-guide-full-decode-2026-09-16.md`, Codex's own
extraction of implementable game-spec data from the physical strategy guide scans (本1/本2/
本2-1/本2-2). This is normally Codex's territory (`reference_sim/conveni_sim/`,
`docs/research/`, `docs/decisions/` per `docs/handoff/roles-and-workflow.md`), but the user gave
an explicit one-off request for Claude Code to read the document and implement it directly, which
the roles document's exception clause permits for a single turn.

The source document itself carries binding process rules (its own section 0/17/44): PS/SS-original
data only, separate confirmed table values from behavioral evidence from strategic inference from
UNKNOWN, never silently overwrite an existing confirmed value on conflict, keep raw guide units,
tag every added value with `source: strategy_guide` and page provenance, and defer the large
customer-preference/staff-candidate matrices (which require manual image-row cross-checking) to a
separate P1 pass.

## Decision

Implemented the P0 (safe to data-ify without image cross-checking) portion of the guide:

- **New fixtures** (`STRATEGY_GUIDE_FIXTURES`, `conveni_sim/baseline_data.py`): ~36 previously
  unmodeled fixtures (ambient shelves/wagons, refrigerated/frozen shelves/wagons, dedicated
  cases, event fixtures, vending machines, registers, break rooms) from guide section 4, each
  tagged `EvidenceLevel.CONFIRMED_OFFICIAL` / `STRATEGY_GUIDE`.
- **Existing fixture enrichment**: for `potted_plant`, `bench`, `fountain`, `parking_ground`,
  `parking_two_story`, `parking_tower`, `copier_a`, `copier_b`, filled in only previously-`None`
  fields (`purchase_price_yen`, `placement`, and `footprint` for the two copiers). No previously
  confirmed value was changed. Cross-corroboration (identical capacity/attention/price/maintenance
  between the guide and the existing `CONFIRMED_VISUAL`/`CONFIRMED_COMMUNITY` values for
  copier_a/copier_b/potted_plant/fountain/parking_*) was used to justify trusting the new fields on
  those same rows.
- **`ProductCategoryPricing`** (new dataclass in `models.py`) + `PRODUCT_CATEGORY_PRICING` (27
  rows, `baseline_data.py`): category-level standard price / cost-rate / margin-rate from guide
  section 3. This is coarser than the existing per-SKU `ProductDefinition` and does not replace it;
  `master_audit.py`'s `PRODUCT_IMPLEMENTATION_FIELDS` targets `ProductDefinition` only.
  `ProductCategoryPricing.__post_init__` enforces `cost_rate_pct + margin_rate_pct == 100`.
  `procurement_cost_yen` is a derived property (`price * cost_rate // 100`); the guide does not
  state a rounding rule, so no rounding convention beyond integer floor division is asserted as
  confirmed.
- **`SalaryTableEntry`** (new dataclass in `models.py`) + `SALARY_TABLE` (10 age-anchor rows,
  15–60 in 5-year steps, `baseline_data.py`): age → monthly salary from guide section 5.
- **`FixtureDefinition.placement`** (new optional field in `models.py`): indoor / outdoor /
  indoor_outdoor siting, previously unmodeled.

Not implemented this pass, with reasons recorded in
`docs/research/strategy-guide-fixture-crosscheck-2026-09-16.md`:

- **Store building sizes** (guide section 1): the existing `small_top` `editable_floor=(8,13)`
  does not match either the guide's 店内 (7x10=70) or 店舗外形 (9x10=90) column for `store_1`,
  despite an exact match on `construction_price_yen` (6,000,000). Column-to-field mapping is
  unresolved, so no `STORE_VARIANTS` value was added or changed.
- **Bench maintenance conflict**: guide says 160 yen/day; existing `CONFIRMED_COMMUNITY` value is
  168 yen/day. Existing value kept; conflict recorded, not resolved.
- **Promotion popularity conflict**: guide's airship/radio/tv `popularity_gain` (+40/+60/+90)
  differs from the existing `CONFIRMED_COMMUNITY` values (+30/+50/+100), even though cost and
  trigger day/hour match exactly between both sources. Existing `PROMOTIONS` values kept
  unchanged; conflict recorded.
- **Customer-preference and staff-candidate matrices**: guide's own section 44 flags these as
  requiring manual image-row cross-checking; deferred to a separate PR per the guide's own P1
  classification.

## Evidence boundary

All newly added values are `EvidenceLevel.CONFIRMED_OFFICIAL` with `source` citing
`docs/research/strategy-guide-full-decode-2026-09-16.md`. No numeric value was invented,
interpolated, or unit-converted; guide values are stored as printed. Fields the guide's fixture
table does not cover (`compatible_product_categories`, `interaction_sides`, `service_bonus`,
`security_bonus` on the new rows) remain `None`, not guessed.

Tests: `reference_sim/tests/test_strategy_guide_data.py` verifies the new tables load, are
uniquely keyed, carry the expected evidence tagging, do not silently fill uncovered fields, and
that `ProductCategoryPricing` rejects an unbalanced cost/margin pair. `test_baseline.py` and
`test_master_schema.py` were updated to reflect the newly-filled (previously `None`) fields on
`copier_a`/`copier_b`/`potted_plant` rather than asserting their old unknown state.
