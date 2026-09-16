import unittest

from conveni_sim.baseline_data import (
    CUSTOMER_ARCHETYPES,
    CUSTOMER_VISIT_SCHEDULE,
    FIXTURES,
    PRODUCT_CATEGORY_PRICING,
    STAFF_CANDIDATES,
    STRATEGY_GUIDE_FIXTURES,
    TOWN_BUILDINGS,
)
from conveni_sim.master_audit import (
    CUSTOMER_ARCHETYPE_RESEARCH_FIELDS,
    STAFF_IMPLEMENTATION_FIELDS,
    audit_customer_archetype,
    audit_staff,
)
from conveni_sim.models import EvidenceLevel

# These datasets were originally deferred as P1 (guide section 44: "large
# tables needing manual image-row cross-checking") when the strategy-guide
# full-decode summary was first imported. This module covers the follow-up
# pass that transcribed them from the primary page scans.


class StaffCandidateTests(unittest.TestCase):
    def test_all_35_candidates_load_with_unique_ids(self):
        self.assertEqual(len(STAFF_CANDIDATES), 35)
        ids = [s.id for s in STAFF_CANDIDATES]
        self.assertEqual(len(ids), len(set(ids)))

    def test_hourly_wage_derivation_matches_the_guides_own_formula_note(self):
        # salary_yen_per_day_24h is derived (hourly_wage * 24), not printed
        # directly; spot-check one candidate against her printed hourly wage.
        by_id = {s.id: s for s in STAFF_CANDIDATES}
        takenaka = by_id["takenaka_sayuri"]
        self.assertEqual(takenaka.salary_yen_per_day_24h.value, 280 * 24)

    def test_every_candidate_satisfies_the_staff_implementation_audit(self):
        for candidate in STAFF_CANDIDATES:
            result = audit_staff(candidate)
            # security_skill is intentionally left unknown for exactly one
            # candidate (丸山昭夫) whose printed value could not be read
            # with confidence; every other field must be known.
            if candidate.id == "maruyama_akio":
                self.assertEqual(result.unknown_fields, ("security_skill",))
            else:
                self.assertEqual(
                    set(result.known_fields), set(STAFF_IMPLEMENTATION_FIELDS)
                )

    def test_candidates_are_tagged_confirmed_official_strategy_guide(self):
        for candidate in STAFF_CANDIDATES:
            self.assertEqual(candidate.stamina.evidence, EvidenceLevel.CONFIRMED_OFFICIAL)
            self.assertIn("strategy guide", candidate.stamina.source)


class CustomerArchetypeTests(unittest.TestCase):
    def test_all_21_archetypes_load_with_unique_ids(self):
        self.assertEqual(len(CUSTOMER_ARCHETYPES), 21)
        ids = [a.id for a in CUSTOMER_ARCHETYPES]
        self.assertEqual(len(ids), len(set(ids)))

    def test_archetypes_do_not_invent_the_research_fields(self):
        # CustomerArchetypeDefinition's coarse research fields (spending
        # power profile, preferred products, patience/anger) are a
        # different, still-unresolved concept from the fine-grained
        # per-visit schedule table; archetypes must not claim to have them.
        for archetype in CUSTOMER_ARCHETYPES:
            result = audit_customer_archetype(archetype)
            self.assertEqual(result.unknown_fields, CUSTOMER_ARCHETYPE_RESEARCH_FIELDS)

    def test_every_visit_row_references_a_known_archetype(self):
        archetype_ids = {a.id for a in CUSTOMER_ARCHETYPES}
        for row in CUSTOMER_VISIT_SCHEDULE:
            self.assertIn(row.archetype_id, archetype_ids)

    def test_visit_schedule_has_140_rows_and_covers_every_archetype(self):
        self.assertEqual(len(CUSTOMER_VISIT_SCHEDULE), 140)
        covered = {row.archetype_id for row in CUSTOMER_VISIT_SCHEDULE}
        self.assertEqual(covered, {a.id for a in CUSTOMER_ARCHETYPES})

    def test_visit_rows_carry_a_primary_or_secondary_wanted_product(self):
        for row in CUSTOMER_VISIT_SCHEDULE:
            has_primary = row.primary_wanted_product is not None
            has_secondary = len(row.secondary_wanted_products.value) > 0
            self.assertTrue(has_primary or has_secondary, row)

    def test_wanted_products_reference_known_categories(self):
        known = {c.id for c in PRODUCT_CATEGORY_PRICING}
        for row in CUSTOMER_VISIT_SCHEDULE:
            if row.primary_wanted_product is not None:
                self.assertIn(row.primary_wanted_product.value, known)
            for pid in row.secondary_wanted_products.value:
                self.assertIn(pid, known)


class TownBuildingTests(unittest.TestCase):
    def test_all_59_buildings_load_with_unique_ids(self):
        self.assertEqual(len(TOWN_BUILDINGS), 59)
        ids = [b.id for b in TOWN_BUILDINGS]
        self.assertEqual(len(ids), len(set(ids)))

    def test_overnight_and_daytime_buildings_are_both_represented(self):
        overnight = [b for b in TOWN_BUILDINGS if b.active_overnight.value]
        daytime = [b for b in TOWN_BUILDINGS if not b.active_overnight.value]
        self.assertGreater(len(overnight), 0)
        self.assertGreater(len(daytime), 0)

    def test_no_customer_buildings_have_no_wanted_products(self):
        by_id = {b.id: b for b in TOWN_BUILDINGS}
        for building_id in ("vacant_lot", "road", "railway", "town_hall_lot", "inducement_lot"):
            self.assertEqual(by_id[building_id].wanted_products.value, ())

    def test_wanted_products_reference_known_categories(self):
        known = {c.id for c in PRODUCT_CATEGORY_PRICING}
        for building in TOWN_BUILDINGS:
            for pid in building.wanted_products.value:
                self.assertIn(pid, known)


class FixtureCompatibleCategoriesTests(unittest.TestCase):
    def test_ambient_shelf_categories_match_the_guides_own_column(self):
        by_id = {f.id: f for f in STRATEGY_GUIDE_FIXTURES}
        self.assertEqual(
            by_id["small_ambient_shelf"].compatible_product_categories.value,
            ("bread", "instant_food", "snacks", "books", "stationery",
             "electronics", "retort_food", "seasoning", "daily_goods", "underwear"),
        )

    def test_dedicated_cases_map_to_exactly_one_category(self):
        by_id = {f.id: f for f in STRATEGY_GUIDE_FIXTURES}
        self.assertEqual(by_id["oden_case"].compatible_product_categories.value, ("oden",))
        self.assertEqual(by_id["hot_drink_case"].compatible_product_categories.value, ("hot_drink",))
        self.assertEqual(
            by_id["steamed_bun_case"].compatible_product_categories.value, ("chinese_steamed_bun",)
        )

    def test_registers_with_no_listed_product_stay_unknown(self):
        by_id = {f.id: f for f in STRATEGY_GUIDE_FIXTURES}
        self.assertIsNone(by_id["register_1"].compatible_product_categories)
        self.assertIsNone(by_id["register_3"].compatible_product_categories)

    def test_copiers_in_the_main_fixture_table_handle_copy_paper(self):
        by_id = {f.id: f for f in FIXTURES}
        self.assertEqual(by_id["copier_a"].compatible_product_categories.value, ("copy_paper",))
        self.assertEqual(by_id["copier_b"].compatible_product_categories.value, ("copy_paper",))


class ProductSeasonalDemandTests(unittest.TestCase):
    def test_seasonal_categories_are_flagged(self):
        by_id = {c.id: c for c in PRODUCT_CATEGORY_PRICING}
        self.assertEqual(by_id["cold_drink"].seasonal_demand.value, "summer")
        self.assertEqual(by_id["ice_cream"].seasonal_demand.value, "summer")
        self.assertEqual(by_id["hot_drink"].seasonal_demand.value, "winter")
        self.assertEqual(by_id["oden"].seasonal_demand.value, "winter")
        self.assertEqual(by_id["chinese_steamed_bun"].seasonal_demand.value, "winter")

    def test_non_seasonal_categories_stay_unflagged(self):
        by_id = {c.id: c for c in PRODUCT_CATEGORY_PRICING}
        for category_id in ("bento", "bread", "alcohol", "tobacco", "cash"):
            self.assertIsNone(by_id[category_id].seasonal_demand)


if __name__ == "__main__":
    unittest.main()
