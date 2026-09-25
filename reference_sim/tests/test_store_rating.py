import unittest

from conveni_sim.store_rating import (
    ANGRY_CUSTOMER_DOWNGRADE_POINTS,
    DONATION_UPGRADE_POINTS,
    DOWNGRADE_THRESHOLDS_BY_CURRENT_STARS,
    SHOPLIFTING_DOWNGRADE_POINTS,
    UPGRADE_THRESHOLDS_BY_CURRENT_STARS,
    RatingMonthlyInputs,
    evaluate_monthly_rating_change,
    star_rank_for_internal_value,
)

# Formula transcribed from the strategy guide's "オールテクニックガイド"
# 評価関連 page (docs/research/strategy-guide-fixture-crosscheck-2026-09-16.md
# section 7), implemented here for the first time; see decision 0079.


class StarRankConversionTests(unittest.TestCase):
    def test_boundaries_match_the_guides_table(self):
        self.assertEqual(star_rank_for_internal_value(100), 5)
        self.assertEqual(star_rank_for_internal_value(80), 4)
        self.assertEqual(star_rank_for_internal_value(99), 4)
        self.assertEqual(star_rank_for_internal_value(60), 3)
        self.assertEqual(star_rank_for_internal_value(40), 2)
        self.assertEqual(star_rank_for_internal_value(20), 1)
        self.assertEqual(star_rank_for_internal_value(19), 0)
        self.assertEqual(star_rank_for_internal_value(0), 0)

    def test_rejects_out_of_range_value(self):
        with self.assertRaises(ValueError):
            star_rank_for_internal_value(101)
        with self.assertRaises(ValueError):
            star_rank_for_internal_value(-1)


class MonthlyRatingEvaluationTests(unittest.TestCase):
    def test_five_star_store_meeting_all_five_criteria_upgrades(self):
        inputs = RatingMonthlyInputs(
            current_internal_value=100,
            price_change_pct=-40,
            service_value=100,
            security_value=100,
            cleaning_value=100,
            monthly_sales_yen=20_000_000,
        )
        result = evaluate_monthly_rating_change(inputs)
        self.assertEqual(result.current_stars, 5)
        self.assertEqual(result.criteria_met, 5)
        self.assertTrue(result.upgrade_applies)
        self.assertEqual(result.downgrade_points, 0)
        self.assertEqual(result.net_point_change, 5)
        self.assertEqual(result.next_internal_value, 100)  # capped at 100

    def test_needs_at_least_three_of_five_criteria_not_all_five(self):
        # ★1 upgrade row: price<=-5, service>=60, security>=75, cleaning>=85, sales>=5,000,000
        inputs = RatingMonthlyInputs(
            current_internal_value=25,  # 1 star
            price_change_pct=-5,
            service_value=60,
            security_value=75,
            cleaning_value=0,  # fails
            monthly_sales_yen=0,  # fails
        )
        result = evaluate_monthly_rating_change(inputs)
        self.assertEqual(result.current_stars, 1)
        self.assertEqual(result.criteria_met, 3)
        self.assertTrue(result.upgrade_applies)

    def test_two_of_five_criteria_does_not_upgrade(self):
        inputs = RatingMonthlyInputs(
            current_internal_value=25,
            price_change_pct=-5,
            service_value=60,
            security_value=0,
            cleaning_value=0,
            monthly_sales_yen=0,
        )
        result = evaluate_monthly_rating_change(inputs)
        self.assertEqual(result.criteria_met, 2)
        self.assertFalse(result.upgrade_applies)

    def test_downgrade_is_minus_one_per_failed_criterion(self):
        # ★5 downgrade row: price>=1%, service<80, security<80, cleaning<100, sales<3,000,000
        inputs = RatingMonthlyInputs(
            current_internal_value=100,
            price_change_pct=5,  # fails (overpriced)
            service_value=50,  # fails
            security_value=90,  # ok
            cleaning_value=100,  # ok
            monthly_sales_yen=1_000_000,  # fails
        )
        result = evaluate_monthly_rating_change(inputs)
        self.assertEqual(result.downgrade_points, -3)
        self.assertFalse(result.upgrade_applies)
        self.assertEqual(result.next_internal_value, 97)

    def test_zero_star_store_uses_its_own_printed_row(self):
        # Task #86: both printed tables have a ☆☆☆☆☆ row (-1%以下 / 50 / 70
        # / 80 / 300万円以上), easier than the ★1 row.
        inputs = RatingMonthlyInputs(
            current_internal_value=10,
            price_change_pct=-1,
            service_value=50,
            security_value=70,
            cleaning_value=80,
            monthly_sales_yen=3_000_000,
        )
        result = evaluate_monthly_rating_change(inputs)
        self.assertEqual(result.current_stars, 0)
        self.assertEqual(result.criteria_met, 5)
        self.assertTrue(result.upgrade_applies)
        self.assertEqual(result.downgrade_points, 0)

    def test_thresholds_match_the_guides_printed_table_cell_for_cell(self):
        # Task #86: transcribed from the table printed identically on book
        # pages 39 and 75 (re-read at 5x render). Columns: price, service,
        # security, cleaning, sales.
        printed_increase = {
            5: (-30, 100, 100, 100, 15_000_000),
            4: (-20, 90, 90, 100, 10_000_000),
            3: (-15, 80, 85, 95, 9_000_000),
            2: (-10, 70, 80, 90, 7_000_000),
            1: (-5, 60, 75, 85, 5_000_000),
            0: (-1, 50, 70, 80, 3_000_000),
        }
        printed_decrease = {
            5: (1, 80, 80, 100, 3_000_000),
            4: (1, 70, 70, 95, 2_500_000),
            3: (1, 60, 65, 90, 2_000_000),
            2: (1, 50, 60, 85, 1_500_000),
            1: (1, 40, 55, 80, 1_000_000),
            0: (1, 30, 50, 75, 500_000),
        }
        for stars, row in printed_increase.items():
            t = UPGRADE_THRESHOLDS_BY_CURRENT_STARS[stars]
            self.assertEqual(
                (t.max_price_change_pct, t.min_service, t.min_security, t.min_cleaning, t.min_sales_yen),
                row,
                stars,
            )
        for stars, row in printed_decrease.items():
            t = DOWNGRADE_THRESHOLDS_BY_CURRENT_STARS[stars]
            self.assertEqual(
                (t.min_price_change_pct, t.below_service, t.below_security, t.below_cleaning, t.below_sales_yen),
                row,
                stars,
            )

    def test_next_internal_value_does_not_go_below_zero(self):
        inputs = RatingMonthlyInputs(
            current_internal_value=2,
            price_change_pct=5,
            service_value=0,
            security_value=0,
            cleaning_value=0,
            monthly_sales_yen=0,
        )
        result = evaluate_monthly_rating_change(inputs)
        self.assertEqual(result.next_internal_value, 0)

    def test_event_point_constants_are_available_for_callers_to_apply_separately(self):
        self.assertEqual(ANGRY_CUSTOMER_DOWNGRADE_POINTS, -1)
        self.assertEqual(SHOPLIFTING_DOWNGRADE_POINTS, -1)
        self.assertEqual(DONATION_UPGRADE_POINTS, 5)


if __name__ == "__main__":
    unittest.main()
