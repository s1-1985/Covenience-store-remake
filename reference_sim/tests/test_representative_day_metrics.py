import unittest

from conveni_sim.minimal_day_scenario import (
    MinimalRepresentativeDayScenarioConfig,
    MinimalScenarioLayout,
    MinimalScenarioProduct,
    MinimalScenarioStaff,
    MinimalScenarioTiming,
    SCENARIO_SLOT_ID,
    SCENARIO_STAFF_ID,
    build_minimal_representative_day_scenario,
)
from conveni_sim.operating_time import OperatingHours
from conveni_sim.representative_day_metrics import (
    ObservedInventoryEnding,
    ObservedRepresentativeDayMetrics,
    ObservedStaffMinimum,
    compare_representative_day_metrics,
    derive_representative_day_metrics,
)
from conveni_sim.scenario_policies import ScheduledScenarioCustomer
from conveni_sim.staff import StaffTask
from conveni_sim.store_grid import Direction, GridPoint


class RepresentativeDayMetricsTests(unittest.TestCase):
    def make_run(self):
        config = MinimalRepresentativeDayScenarioConfig(
            layout=MinimalScenarioLayout(
                width_tiles=5,
                height_tiles=5,
                shelf_origin_subcell=GridPoint(4, 4),
                shelf_footprint_tiles=(1, 1),
                shelf_interaction_side=Direction.NORTH,
                checkout_origin_subcell=GridPoint(6, 4),
                checkout_footprint_tiles=(1, 1),
                checkout_interaction_side=Direction.NORTH,
                entry_point=GridPoint(0, 0),
                exit_point=GridPoint(0, 8),
            ),
            product=MinimalScenarioProduct(
                product_id="bread",
                capacity_units=3,
                initial_units=2,
                unit_procurement_cost_yen=50,
                unit_sale_price_yen=120,
                purchase_quantity=1,
            ),
            staff=MinimalScenarioStaff(
                stamina_max=4,
                register_skill=40,
                task_order=(StaffTask.CHECKOUT, StaffTask.REPLENISH, StaffTask.CLEAN),
                replenishment_skill=5,
                replenishment_cap=7,
            ),
            timing=MinimalScenarioTiming(
                step_game_minutes=1,
                checkout_game_minutes=1,
                checkout_stamina_cost=2,
                replenish_game_minutes=1,
                clean_game_minutes=1,
                replenish_up_to_quantity=1,
                replenish_stamina_cost=1,
                clean_stamina_cost=1,
                break_room_target_id="break-room",
                return_to_break_room_game_minutes=1,
                recovery_interval_game_minutes=1,
                recovery_amount=4,
            ),
            arrivals=(ScheduledScenarioCustomer(23 * 60 + 31, "c1"),),
            initial_cash_yen=1_000,
            operating_hours=OperatingHours.twenty_four_hours(),
            start_hour=23,
            start_minute=30,
            year=1,
            month=1,
            day=1,
            checkout_staff_capacity=1,
        )
        return build_minimal_representative_day_scenario(config).run()

    def test_derives_factual_metrics_from_full_day_trace(self):
        metrics = derive_representative_day_metrics(self.make_run())

        self.assertEqual(metrics.attempted_arrivals, 1)
        self.assertEqual(metrics.admitted_arrivals, 1)
        self.assertEqual(metrics.store_closed_rejections, 0)
        self.assertEqual(metrics.completed_checkout_sales, 1)
        self.assertEqual(metrics.known_checkout_revenue_yen, 120)
        self.assertTrue(metrics.checkout_revenue_is_exact)
        self.assertEqual(metrics.peak_active_checkout_services, 1)
        self.assertEqual(metrics.total_customer_sessions, 1)
        self.assertEqual(metrics.exited_customers, 1)
        self.assertEqual(metrics.known_cash_delta_yen, 20)
        self.assertEqual(metrics.day_known_credits_yen, 120)
        self.assertEqual(metrics.day_known_debits_yen, 100)

        self.assertEqual(len(metrics.staff), 1)
        self.assertEqual(metrics.staff[0].staff_id, SCENARIO_STAFF_ID)
        self.assertEqual(metrics.staff[0].minimum_stamina, 0)
        self.assertEqual(metrics.staff[0].ending_stamina, 4)
        self.assertEqual(metrics.inventory[0].slot_id, SCENARIO_SLOT_ID)
        self.assertEqual(metrics.inventory[0].ending_units, 3)

    def test_comparison_only_emits_explicit_observation_targets(self):
        metrics = derive_representative_day_metrics(self.make_run())
        observed = ObservedRepresentativeDayMetrics(
            attempted_arrivals=1,
            completed_checkout_sales=2,
            known_cash_delta_yen=25,
            staff_minimums=(
                ObservedStaffMinimum(SCENARIO_STAFF_ID, 1),
                ObservedStaffMinimum("missing-staff", 5),
            ),
            inventory_endings=(ObservedInventoryEnding(SCENARIO_SLOT_ID, 2),),
        )

        comparison = compare_representative_day_metrics(metrics, observed)
        by_name = {delta.metric: delta for delta in comparison.deltas}

        self.assertEqual(by_name["attempted_arrivals"].delta, 0)
        self.assertEqual(by_name["completed_checkout_sales"].delta, -1)
        self.assertEqual(by_name["known_cash_delta_yen"].delta, -5)
        self.assertEqual(
            by_name[f"staff:{SCENARIO_STAFF_ID}:minimum_stamina"].delta,
            -1,
        )
        self.assertIsNone(by_name["staff:missing-staff:minimum_stamina"].simulated_value)
        self.assertIsNone(by_name["staff:missing-staff:minimum_stamina"].delta)
        self.assertEqual(by_name[f"inventory:{SCENARIO_SLOT_ID}:ending_units"].delta, 1)
        self.assertNotIn("admitted_arrivals", by_name)


if __name__ == "__main__":
    unittest.main()
