import unittest

from conveni_sim.staff import StaffSkill, StoreStaffRoster
from conveni_sim.store_evaluation import StoreEvaluationRuntime
from conveni_sim.store_grid import StoreGrid
from conveni_sim.store_value import SecurityFacilityCoverage


class StoreEvaluationServiceValueTests(unittest.TestCase):
    def test_none_when_no_staff_has_a_known_service_skill(self):
        roster = StoreStaffRoster()
        roster.add_staff("s1")
        runtime = StoreEvaluationRuntime(roster, StoreGrid(5, 5))

        self.assertIsNone(runtime.service_value())

    def test_averages_known_service_skills_and_adds_fixture_bonuses(self):
        roster = StoreStaffRoster()
        roster.add_staff("s1", runtime_skills={StaffSkill.SERVICE: 60})
        roster.add_staff("s2", runtime_skills={StaffSkill.SERVICE: 80})
        roster.add_staff("s3")  # no known service skill; excluded, not treated as 0
        runtime = StoreEvaluationRuntime(roster, StoreGrid(5, 5))

        self.assertEqual(runtime.service_value([2, 4]), 76.0)


class StoreEvaluationSecurityAndCleaningValueTests(unittest.TestCase):
    def test_none_when_grid_size_tier_is_unknown(self):
        roster = StoreStaffRoster()
        roster.add_staff("s1", runtime_skills={StaffSkill.SECURITY: 10, StaffSkill.CLEANING: 10})
        runtime = StoreEvaluationRuntime(roster, StoreGrid(5, 5))

        self.assertIsNone(runtime.security_value())
        self.assertIsNone(runtime.cleaning_value())

    def test_uses_size_tier_multiplier_and_facility_coverage(self):
        roster = StoreStaffRoster()
        roster.add_staff("s1", runtime_skills={StaffSkill.SECURITY: 10, StaffSkill.CLEANING: 10})
        roster.add_staff("s2", runtime_skills={StaffSkill.SECURITY: 20, StaffSkill.CLEANING: 20})
        grid = StoreGrid(5, 5, size_tier="medium")
        runtime = StoreEvaluationRuntime(roster, grid)

        self.assertEqual(runtime.cleaning_value(), (10 + 20) * 1.65)
        self.assertEqual(runtime.security_value(), (10 + 20) * 1.65)
        coverage = SecurityFacilityCoverage(police_box_area_tiles=2)
        self.assertEqual(runtime.security_value(coverage), (10 + 20) * 1.65 + 20)

    def test_size_tier_is_carried_from_store_variant(self):
        from conveni_sim.baseline_data import STORE_VARIANTS

        small_top = next(v for v in STORE_VARIANTS if v.id == "small_top")
        grid = StoreGrid.from_store_variant(small_top)

        self.assertEqual(grid.size_tier, "small")


class StoreEvaluationMonthEndTests(unittest.TestCase):
    def make_runtime(self):
        roster = StoreStaffRoster()
        roster.add_staff(
            "s1",
            runtime_skills={
                StaffSkill.SERVICE: 100,
                StaffSkill.SECURITY: 100,
                StaffSkill.CLEANING: 100,
            },
        )
        grid = StoreGrid(5, 5, size_tier="small")
        return StoreEvaluationRuntime(roster, grid)

    def test_raises_when_internal_rating_value_is_unknown(self):
        runtime = self.make_runtime()

        with self.assertRaises(ValueError):
            runtime.evaluate_month_end(price_change_pct=0, monthly_sales_yen=0)

    def test_raises_when_service_security_or_cleaning_is_unresolvable(self):
        roster = StoreStaffRoster()
        roster.add_staff("s1")  # no known skills at all
        runtime = StoreEvaluationRuntime(roster, StoreGrid(5, 5))
        runtime.set_internal_rating_value(50)

        with self.assertRaises(ValueError):
            runtime.evaluate_month_end(price_change_pct=0, monthly_sales_yen=0)

    def test_successful_evaluation_advances_internal_rating_value(self):
        runtime = self.make_runtime()
        runtime.set_internal_rating_value(50)

        evaluation = runtime.evaluate_month_end(
            price_change_pct=-30,
            monthly_sales_yen=20_000_000,
        )

        self.assertTrue(evaluation.upgrade_applies)
        self.assertEqual(runtime.internal_rating_value, evaluation.next_internal_value)
        self.assertEqual(runtime.internal_rating_value, 55)

    def test_set_internal_rating_value_rejects_out_of_range(self):
        runtime = self.make_runtime()

        with self.assertRaises(ValueError):
            runtime.set_internal_rating_value(101)
        with self.assertRaises(ValueError):
            runtime.set_internal_rating_value(-1)


class StoreEvaluationPointDeltaTests(unittest.TestCase):
    def test_raises_when_internal_rating_value_is_unknown(self):
        runtime = StoreEvaluationRuntime(StoreStaffRoster(), StoreGrid(5, 5))

        with self.assertRaises(ValueError):
            runtime.apply_point_delta(-1)

    def test_clamps_to_0_and_100(self):
        runtime = StoreEvaluationRuntime(StoreStaffRoster(), StoreGrid(5, 5))
        runtime.set_internal_rating_value(2)
        self.assertEqual(runtime.apply_point_delta(-5), 0)

        runtime.set_internal_rating_value(98)
        self.assertEqual(runtime.apply_point_delta(5), 100)


if __name__ == "__main__":
    unittest.main()
