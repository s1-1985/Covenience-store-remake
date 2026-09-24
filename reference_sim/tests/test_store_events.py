import unittest

from conveni_sim.store_events import (
    DONATION_CASH_THRESHOLD_YEN,
    METROPOLITAN_GOVERNMENT_POPULATION_THRESHOLD,
    STORE_COUNT_THRESHOLD,
    TOWN_POPULATION_THRESHOLD,
    FireOrRobberyRisk,
    compute_contest_prize_yen,
    donation_event_is_eligible,
    magazine_or_contest_event_is_eligible,
    metropolitan_government_is_induced,
    scenario_time_limit_exceeded,
    shoplifting_is_possible,
)
from conveni_sim.store_value import SecurityFacilityCoverage, NO_SECURITY_FACILITY_COVERAGE

# Event-trigger conditions transcribed from the strategy guide's event-guide
# table (docs/research/strategy-guide-fixture-crosscheck-2026-09-16.md
# section 7), implemented here for the first time; see decision 0079.


class DonationEligibilityTests(unittest.TestCase):
    def test_eligible_at_threshold(self):
        self.assertTrue(donation_event_is_eligible(DONATION_CASH_THRESHOLD_YEN))

    def test_not_eligible_below_threshold(self):
        self.assertFalse(donation_event_is_eligible(DONATION_CASH_THRESHOLD_YEN - 1))

    def test_rejects_negative_cash(self):
        with self.assertRaises(ValueError):
            donation_event_is_eligible(-1)


class MagazineContestEligibilityTests(unittest.TestCase):
    def test_eligible_at_both_thresholds(self):
        self.assertTrue(
            magazine_or_contest_event_is_eligible(TOWN_POPULATION_THRESHOLD, STORE_COUNT_THRESHOLD)
        )

    def test_not_eligible_with_too_few_stores(self):
        self.assertFalse(
            magazine_or_contest_event_is_eligible(TOWN_POPULATION_THRESHOLD, STORE_COUNT_THRESHOLD - 1)
        )

    def test_not_eligible_with_too_small_population(self):
        self.assertFalse(
            magazine_or_contest_event_is_eligible(TOWN_POPULATION_THRESHOLD - 1, STORE_COUNT_THRESHOLD)
        )

    def test_contest_prize_scales_with_store_count(self):
        self.assertEqual(compute_contest_prize_yen(7), 70_000_000)

    def test_rejects_negative_inputs(self):
        with self.assertRaises(ValueError):
            magazine_or_contest_event_is_eligible(-1, 5)
        with self.assertRaises(ValueError):
            compute_contest_prize_yen(-1)


class MetropolitanGovernmentInducementTests(unittest.TestCase):
    def test_induced_at_threshold(self):
        self.assertEqual(METROPOLITAN_GOVERNMENT_POPULATION_THRESHOLD, 20_000)
        self.assertTrue(
            metropolitan_government_is_induced(METROPOLITAN_GOVERNMENT_POPULATION_THRESHOLD)
        )

    def test_not_induced_below_threshold(self):
        self.assertFalse(
            metropolitan_government_is_induced(METROPOLITAN_GOVERNMENT_POPULATION_THRESHOLD - 1)
        )

    def test_rejects_negative_population(self):
        with self.assertRaises(ValueError):
            metropolitan_government_is_induced(-1)


class ShopliftingTests(unittest.TestCase):
    def test_possible_when_manner_exceeds_security(self):
        self.assertTrue(shoplifting_is_possible(80, 79))

    def test_not_possible_when_security_is_equal_or_higher(self):
        self.assertFalse(shoplifting_is_possible(80, 80))
        self.assertFalse(shoplifting_is_possible(80, 90))


class FireOrRobberyRiskTests(unittest.TestCase):
    def test_unprotected_with_no_coverage(self):
        risk = FireOrRobberyRisk(NO_SECURITY_FACILITY_COVERAGE, store_popularity=50, store_security_value=60)
        self.assertTrue(risk.is_unprotected)
        self.assertTrue(risk.risk_factors_present)

    def test_protected_with_any_coverage(self):
        coverage = SecurityFacilityCoverage(police_box_area_tiles=1)
        risk = FireOrRobberyRisk(coverage, store_popularity=10, store_security_value=60)
        self.assertFalse(risk.is_unprotected)
        self.assertFalse(risk.popularity_exceeds_security)
        self.assertFalse(risk.risk_factors_present)

    def test_popularity_exceeding_security_is_a_risk_factor_even_when_protected(self):
        coverage = SecurityFacilityCoverage(police_box_area_tiles=1)
        risk = FireOrRobberyRisk(coverage, store_popularity=90, store_security_value=60)
        self.assertFalse(risk.is_unprotected)
        self.assertTrue(risk.popularity_exceeds_security)
        self.assertTrue(risk.risk_factors_present)

    def test_rejects_out_of_range_popularity(self):
        with self.assertRaises(ValueError):
            FireOrRobberyRisk(NO_SECURITY_FACILITY_COVERAGE, store_popularity=101, store_security_value=0)


class GameOverTimeLimitTests(unittest.TestCase):
    def test_exceeded_after_year_100_without_clear(self):
        self.assertTrue(scenario_time_limit_exceeded(101, clear_condition_met=False))

    def test_not_exceeded_at_year_100(self):
        self.assertFalse(scenario_time_limit_exceeded(100, clear_condition_met=False))

    def test_not_exceeded_when_clear_condition_met(self):
        self.assertFalse(scenario_time_limit_exceeded(150, clear_condition_met=True))

    def test_rejects_year_below_one(self):
        with self.assertRaises(ValueError):
            scenario_time_limit_exceeded(0, clear_condition_met=False)


if __name__ == "__main__":
    unittest.main()
