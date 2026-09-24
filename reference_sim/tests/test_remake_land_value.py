import unittest

from conveni_sim.remake_land_value import (
    EXISTING_BUILDING_ACQUISITION_RATE,
    NEW_BRANCH_LAND_AREA_COUNT,
    RemakeBalancedLandValuePolicy,
)
from conveni_sim.town import TownState


class RemakeBalancedLandValuePolicyValidationTests(unittest.TestCase):
    def test_negative_base_price_rejected(self):
        policy = RemakeBalancedLandValuePolicy()
        with self.assertRaises(ValueError):
            policy.current_land_price_yen(-1, TownState(), elapsed_years=0)

    def test_negative_elapsed_years_rejected(self):
        policy = RemakeBalancedLandValuePolicy()
        with self.assertRaises(ValueError):
            policy.current_land_price_yen(1_000_000, TownState(), elapsed_years=-1)
        with self.assertRaises(ValueError):
            policy.time_inflation_factor(-1)


class RemakeBalancedLandValuePolicyBehaviorTests(unittest.TestCase):
    def test_undeveloped_town_at_year_zero_returns_base_price_unchanged(self):
        policy = RemakeBalancedLandValuePolicy()
        town = TownState(population=0, store_count_including_rivals=0)
        self.assertEqual(policy.current_land_price_yen(20_000_000, town, elapsed_years=0), 20_000_000)

    def test_time_alone_inflates_price(self):
        policy = RemakeBalancedLandValuePolicy()
        town = TownState()
        price_year_0 = policy.current_land_price_yen(20_000_000, town, elapsed_years=0)
        price_year_5 = policy.current_land_price_yen(20_000_000, town, elapsed_years=5)
        price_year_10 = policy.current_land_price_yen(20_000_000, town, elapsed_years=10)
        self.assertLess(price_year_0, price_year_5)
        self.assertLess(price_year_5, price_year_10)

    def test_local_development_alone_inflates_price(self):
        policy = RemakeBalancedLandValuePolicy()
        undeveloped = TownState(population=0, store_count_including_rivals=0)
        developed = TownState(population=20_000, store_count_including_rivals=8)
        price_undeveloped = policy.current_land_price_yen(20_000_000, undeveloped, elapsed_years=0)
        price_developed = policy.current_land_price_yen(20_000_000, developed, elapsed_years=0)
        self.assertLess(price_undeveloped, price_developed)

    def test_fully_developed_town_hits_max_development_factor(self):
        policy = RemakeBalancedLandValuePolicy()
        town = TownState(population=20_000, store_count_including_rivals=8)
        factor = policy.local_development_factor(town)
        self.assertAlmostEqual(factor, policy.max_local_development_factor)

    def test_development_factor_never_exceeds_max_beyond_reference_values(self):
        policy = RemakeBalancedLandValuePolicy()
        town = TownState(population=1_000_000, store_count_including_rivals=500)
        factor = policy.local_development_factor(town)
        self.assertAlmostEqual(factor, policy.max_local_development_factor)

    def test_development_and_time_factors_compound(self):
        policy = RemakeBalancedLandValuePolicy()
        base_town = TownState()
        developed_town = TownState(population=20_000, store_count_including_rivals=8)

        price_base_year_0 = policy.current_land_price_yen(20_000_000, base_town, elapsed_years=0)
        price_developed_year_10 = policy.current_land_price_yen(
            20_000_000, developed_town, elapsed_years=10
        )

        self.assertLess(price_base_year_0, price_developed_year_10)

    def test_custom_annual_inflation_rate_of_zero_freezes_time_factor(self):
        policy = RemakeBalancedLandValuePolicy(annual_inflation_rate=0.0)
        self.assertEqual(policy.time_inflation_factor(0), 1.0)
        self.assertEqual(policy.time_inflation_factor(50), 1.0)


class LandPurchaseCostYenTests(unittest.TestCase):
    def test_negative_area_count_rejected(self):
        policy = RemakeBalancedLandValuePolicy()
        with self.assertRaises(ValueError):
            policy.land_purchase_cost_yen(20_000_000, -1, TownState(), elapsed_years=0)

    def test_negative_existing_building_price_rejected(self):
        policy = RemakeBalancedLandValuePolicy()
        with self.assertRaises(ValueError):
            policy.land_purchase_cost_yen(
                20_000_000,
                1,
                TownState(),
                elapsed_years=0,
                existing_building_construction_price_yen=-1,
            )

    def test_vacant_lot_cost_is_per_area_price_times_area_count(self):
        # Task #60: 必要金額=土地代 (エリア地価×エリア数) -- a vacant lot
        # (no existing_building_construction_price_yen) costs exactly the
        # per-area rate times the area count, undeveloped/year-0 so the
        # per-area rate equals the base rate unchanged.
        policy = RemakeBalancedLandValuePolicy()
        town = TownState(population=0, store_count_including_rivals=0)
        cost = policy.land_purchase_cost_yen(1_000_000, 100, town, elapsed_years=0)
        self.assertEqual(cost, 1_000_000 * 100)

    def test_zero_area_count_is_free_land_cost(self):
        policy = RemakeBalancedLandValuePolicy()
        cost = policy.land_purchase_cost_yen(1_000_000, 0, TownState(), elapsed_years=0)
        self.assertEqual(cost, 0)

    def test_larger_area_count_costs_more(self):
        policy = RemakeBalancedLandValuePolicy()
        town = TownState()
        small = policy.land_purchase_cost_yen(1_000_000, 100, town, elapsed_years=0)
        large = policy.land_purchase_cost_yen(1_000_000, 196, town, elapsed_years=0)
        self.assertLess(small, large)

    def test_occupied_lot_adds_exactly_the_confirmed_50_percent_acquisition_rate(self):
        # Task #60: CONFIRMED_OFFICIAL 建物買収費 = 建物評価額の50%.
        self.assertEqual(EXISTING_BUILDING_ACQUISITION_RATE, 0.5)
        policy = RemakeBalancedLandValuePolicy()
        town = TownState(population=0, store_count_including_rivals=0)
        vacant_cost = policy.land_purchase_cost_yen(1_000_000, 100, town, elapsed_years=0)
        occupied_cost = policy.land_purchase_cost_yen(
            1_000_000, 100, town, elapsed_years=0, existing_building_construction_price_yen=6_000_000
        )
        self.assertEqual(occupied_cost, vacant_cost + 3_000_000)

    def test_occupied_lot_with_zero_valued_building_equals_vacant_lot_cost(self):
        policy = RemakeBalancedLandValuePolicy()
        town = TownState()
        vacant_cost = policy.land_purchase_cost_yen(1_000_000, 100, town, elapsed_years=0)
        occupied_cost = policy.land_purchase_cost_yen(
            1_000_000, 100, town, elapsed_years=0, existing_building_construction_price_yen=0
        )
        self.assertEqual(occupied_cost, vacant_cost)

    def test_development_and_time_factors_still_apply_per_area(self):
        policy = RemakeBalancedLandValuePolicy()
        base_town = TownState()
        developed_town = TownState(population=20_000, store_count_including_rivals=8)
        cost_base_year_0 = policy.land_purchase_cost_yen(1_000_000, 100, base_town, elapsed_years=0)
        cost_developed_year_10 = policy.land_purchase_cost_yen(
            1_000_000, 100, developed_town, elapsed_years=10
        )
        self.assertLess(cost_base_year_0, cost_developed_year_10)

    def test_new_branch_opening_uses_the_confirmed_4_area_constant(self):
        # Task #65/decision 0135: the guide states an exact area count (4)
        # for opening a new branch specifically, distinct from the
        # total_area_tiles-derived inference used elsewhere.
        self.assertEqual(NEW_BRANCH_LAND_AREA_COUNT, 4)
        policy = RemakeBalancedLandValuePolicy()
        town = TownState()
        per_area_cost = policy.land_purchase_cost_yen(1_000_000, 1, town, elapsed_years=0)
        new_branch_cost = policy.land_purchase_cost_yen(
            1_000_000, NEW_BRANCH_LAND_AREA_COUNT, town, elapsed_years=0
        )
        self.assertEqual(new_branch_cost, per_area_cost * NEW_BRANCH_LAND_AREA_COUNT)


if __name__ == "__main__":
    unittest.main()
