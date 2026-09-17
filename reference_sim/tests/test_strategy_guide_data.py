import unittest

from conveni_sim.baseline_data import (
    FIXTURES,
    PRODUCT_CATEGORY_PRICING,
    SALARY_TABLE,
    STRATEGY_GUIDE_FIXTURES,
)
from conveni_sim.master_audit import FIXTURE_IMPLEMENTATION_FIELDS, audit_fixture
from conveni_sim.models import EvidenceLevel, EvidenceValue, ProductCategoryPricing


class StrategyGuideFixtureTests(unittest.TestCase):
    """Loading checks for the strategy-guide-sourced fixture rows.

    Guide policy (docs/research/strategy-guide-full-decode-2026-09-16.md
    section 0/17/44): confirmed table values must load as-is, must be
    tagged with source provenance, and must not silently fill fields the
    guide does not cover.
    """

    def test_all_new_fixture_ids_are_present_and_unique(self):
        by_id = {fixture.id: fixture for fixture in FIXTURES}
        self.assertEqual(len(by_id), len(FIXTURES), "duplicate fixture id in FIXTURES")
        for fixture in STRATEGY_GUIDE_FIXTURES:
            self.assertIn(fixture.id, by_id)

    def test_new_fixture_rows_are_tagged_confirmed_official_strategy_guide(self):
        for fixture in STRATEGY_GUIDE_FIXTURES:
            for field_name in (
                "footprint",
                "maintenance_yen_per_day",
                "purchase_price_yen",
                "capacity",
                "attention",
                "placement",
            ):
                value = getattr(fixture, field_name)
                self.assertIsInstance(value, EvidenceValue, f"{fixture.id}.{field_name}")
                self.assertEqual(value.evidence, EvidenceLevel.CONFIRMED_OFFICIAL)
                self.assertIn("strategy guide", value.source)

    def test_new_fixture_rows_do_not_invent_fields_the_guide_does_not_cover(self):
        # The guide's fixture table does not publish interaction_sides,
        # service_bonus, or security_bonus; those must stay UNKNOWN (None),
        # not be guessed. compatible_product_categories was later filled in
        # (a separate pass, from each fixture's own "取扱商品" column) for
        # most rows, but not for the registers with no listed product
        # ("取扱商品: なし") or the break rooms, which stay None.
        no_product_ids = {"register_1", "register_3", "break_room_1", "break_room_2"}
        for fixture in STRATEGY_GUIDE_FIXTURES:
            if fixture.id in no_product_ids:
                self.assertIsNone(fixture.compatible_product_categories)
            else:
                self.assertIsInstance(fixture.compatible_product_categories, EvidenceValue)
            self.assertIsNone(fixture.interaction_sides)
            self.assertIsNone(fixture.service_bonus)
            self.assertIsNone(fixture.security_bonus)

    def test_existing_confirmed_fixture_values_were_not_overwritten(self):
        # Cross-corroborated rows (copier_a/copier_b/potted_plant/fountain/
        # parking_*) must keep their pre-existing confirmed values; the guide
        # may only fill in previously-None fields on these ids.
        by_id = {fixture.id: fixture for fixture in FIXTURES}
        self.assertEqual(by_id["copier_a"].capacity.value, 20)
        self.assertEqual(by_id["copier_a"].maintenance_yen_per_day.value, 1_200)
        self.assertEqual(by_id["copier_a"].capacity.evidence, EvidenceLevel.CONFIRMED_VISUAL)
        self.assertEqual(by_id["copier_b"].capacity.value, 40)
        self.assertEqual(by_id["copier_b"].maintenance_yen_per_day.value, 1_440)

    def test_bench_maintenance_now_matches_the_guide(self):
        # RESOLVED 2026-09-17: an explicit one-off user instruction directed
        # that guide-vs-existing conflicts be settled in the guide's favor.
        # Guide reports 160 yen/day for the bench (independently confirmed
        # twice); the previous community-sourced 168 is superseded.
        by_id = {fixture.id: fixture for fixture in FIXTURES}
        bench = by_id["bench"]
        self.assertEqual(bench.maintenance_yen_per_day.value, 160)

    def test_new_fixtures_satisfy_the_implementation_field_audit(self):
        for fixture in STRATEGY_GUIDE_FIXTURES:
            result = audit_fixture(fixture)
            self.assertEqual(
                set(result.known_fields) | set(result.unknown_fields),
                set(FIXTURE_IMPLEMENTATION_FIELDS),
            )


class ProductCategoryPricingTests(unittest.TestCase):
    def test_all_categories_load_and_balance_to_100_percent(self):
        self.assertEqual(len(PRODUCT_CATEGORY_PRICING), 27)
        ids = [category.id for category in PRODUCT_CATEGORY_PRICING]
        self.assertEqual(len(ids), len(set(ids)))
        for category in PRODUCT_CATEGORY_PRICING:
            self.assertEqual(
                category.cost_rate_pct.value + category.margin_rate_pct.value, 100
            )

    def test_category_rejects_a_cost_and_margin_that_do_not_balance(self):
        evidence = EvidenceLevel.CONFIRMED_OFFICIAL
        with self.assertRaises(ValueError):
            ProductCategoryPricing(
                "broken",
                "broken",
                EvidenceValue(100, evidence, "test"),
                EvidenceValue(50, evidence, "test"),
                EvidenceValue(40, evidence, "test"),
            )

    def test_procurement_cost_is_derived_not_hardcoded(self):
        by_id = {category.id: category for category in PRODUCT_CATEGORY_PRICING}
        bento = by_id["bento"]
        self.assertEqual(bento.standard_retail_price_yen.value, 400)
        self.assertEqual(bento.cost_rate_pct.value, 60)
        self.assertEqual(bento.procurement_cost_yen, 240)

    def test_cash_category_has_zero_margin(self):
        by_id = {category.id: category for category in PRODUCT_CATEGORY_PRICING}
        cash = by_id["cash"]
        self.assertEqual(cash.margin_rate_pct.value, 0)
        self.assertEqual(cash.cost_rate_pct.value, 100)


class SalaryTableTests(unittest.TestCase):
    def test_salary_table_is_sorted_by_age_and_monotonically_increases(self):
        ages = [entry.age_years for entry in SALARY_TABLE]
        self.assertEqual(ages, sorted(ages))
        salaries = [entry.hourly_wage_yen.value for entry in SALARY_TABLE]
        self.assertEqual(salaries, sorted(salaries))

    def test_salary_entries_are_tagged_confirmed_official_strategy_guide(self):
        for entry in SALARY_TABLE:
            self.assertEqual(entry.hourly_wage_yen.evidence, EvidenceLevel.CONFIRMED_OFFICIAL)
            self.assertIn("strategy guide", entry.hourly_wage_yen.source)

    def test_salary_table_spans_the_guides_documented_age_range(self):
        ages = {entry.age_years for entry in SALARY_TABLE}
        self.assertEqual(ages, {15, 20, 25, 30, 35, 40, 45, 50, 55, 60})


if __name__ == "__main__":
    unittest.main()
