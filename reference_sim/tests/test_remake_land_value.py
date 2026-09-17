import unittest

from conveni_sim.remake_land_value import RemakeBalancedLandValuePolicy
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


if __name__ == "__main__":
    unittest.main()
