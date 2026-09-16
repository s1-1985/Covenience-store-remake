import unittest

from conveni_sim.store_value import (
    NO_SECURITY_FACILITY_COVERAGE,
    SecurityFacilityCoverage,
    compute_cleaning_value,
    compute_security_value,
    compute_service_value,
)

# Formulas transcribed from the strategy guide's "オールテクニックガイド"
# section (docs/research/strategy-guide-fixture-crosscheck-2026-09-16.md
# section 7), implemented here for the first time; see decision 0079.


class ServiceValueTests(unittest.TestCase):
    def test_averages_staff_and_adds_fixture_bonuses(self):
        # 社員3人のサービス値平均 + サービス設備の付加効果
        value = compute_service_value([60, 70, 80], [2, 4, 30])
        self.assertEqual(value, 70 + 36)

    def test_works_with_fewer_than_three_staff(self):
        value = compute_service_value([50], [])
        self.assertEqual(value, 50)

    def test_rejects_empty_staff_list(self):
        with self.assertRaises(ValueError):
            compute_service_value([], [2])

    def test_rejects_negative_skill_values(self):
        with self.assertRaises(ValueError):
            compute_service_value([-1], [])


class SecurityValueTests(unittest.TestCase):
    def test_applies_the_size_tier_multiplier(self):
        value = compute_security_value([20, 20, 20], "medium")
        self.assertAlmostEqual(value, 60 * 1.65)

    def test_adds_facility_bonus_when_supplied(self):
        coverage = SecurityFacilityCoverage(police_box_area_tiles=2, fire_station_area_tiles=1)
        value = compute_security_value([10], "small", coverage)
        self.assertAlmostEqual(value, 10 * 1.5 + 20 + 5)

    def test_facility_bonus_is_capped(self):
        coverage = SecurityFacilityCoverage(police_box_area_tiles=10, fire_station_area_tiles=10)
        self.assertEqual(coverage.police_box_bonus, 40)
        self.assertEqual(coverage.fire_station_bonus, 30)
        self.assertEqual(coverage.total_security_bonus, 70)

    def test_no_coverage_constant_has_zero_bonus(self):
        self.assertEqual(NO_SECURITY_FACILITY_COVERAGE.total_security_bonus, 0)
        self.assertFalse(NO_SECURITY_FACILITY_COVERAGE.has_any_protection)

    def test_rejects_unknown_size_tier(self):
        with self.assertRaises(ValueError):
            compute_security_value([1], "huge")

    def test_zero_staff_is_a_defined_zero_base(self):
        self.assertEqual(compute_security_value([], "small"), 0)


class CleaningValueTests(unittest.TestCase):
    def test_applies_the_size_tier_multiplier(self):
        value = compute_cleaning_value([10, 20, 30], "large")
        self.assertAlmostEqual(value, 60 * 1.8)

    def test_rejects_unknown_size_tier(self):
        with self.assertRaises(ValueError):
            compute_cleaning_value([1], "huge")


class SecurityFacilityCoverageProtectionTests(unittest.TestCase):
    def test_has_any_protection_true_with_either_facility(self):
        self.assertTrue(SecurityFacilityCoverage(police_box_area_tiles=1).has_any_protection)
        self.assertTrue(SecurityFacilityCoverage(fire_station_area_tiles=1).has_any_protection)

    def test_has_any_protection_false_with_neither(self):
        self.assertFalse(SecurityFacilityCoverage().has_any_protection)

    def test_rejects_negative_tile_counts(self):
        with self.assertRaises(ValueError):
            SecurityFacilityCoverage(police_box_area_tiles=-1)


if __name__ == "__main__":
    unittest.main()
