import unittest

from conveni_sim.minimal_day_scenario import (
    MinimalRepresentativeDayScenarioConfig,
    MinimalScenarioLayout,
    MinimalScenarioProduct,
    MinimalScenarioStaff,
    MinimalScenarioTiming,
    SCENARIO_STAFF_ID,
)
from conveni_sim.observation_day_adapter import (
    ObservationDayCoverage,
    ObservationDayMetricMapping,
)
from conveni_sim.observations import (
    GameTimestamp,
    GameplayObservationTimeline,
    ObservationKind,
)
from conveni_sim.operating_time import OperatingHours
from conveni_sim.representative_day_metrics import (
    ObservedRepresentativeDayMetrics,
    ObservedStaffMinimum,
)
from conveni_sim.representative_day_validation import (
    validate_minimal_day_from_observation_timeline,
    validate_minimal_representative_day,
)
from conveni_sim.scenario_policies import ScheduledScenarioCustomer
from conveni_sim.staff import StaffTask
from conveni_sim.store_grid import Direction, GridPoint


class RepresentativeDayValidationTests(unittest.TestCase):
    def make_config(self):
        return MinimalRepresentativeDayScenarioConfig(
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

    def test_build_run_measure_compare_is_one_validation_call(self):
        result = validate_minimal_representative_day(
            self.make_config(),
            ObservedRepresentativeDayMetrics(
                admitted_arrivals=1,
                completed_checkout_sales=1,
                known_cash_delta_yen=20,
                staff_minimums=(ObservedStaffMinimum(SCENARIO_STAFF_ID, 0),),
            ),
        )

        self.assertEqual(result.metrics.admitted_arrivals, 1)
        self.assertEqual(result.metrics.completed_checkout_sales, 1)
        self.assertEqual(result.metrics.known_cash_delta_yen, 20)
        self.assertTrue(result.comparison.deltas)
        self.assertTrue(all(delta.delta == 0 for delta in result.comparison.deltas))
        self.assertEqual(result.run.boundary_snapshot.minute_of_day, 0)

    def test_full_day_timeline_can_feed_validation_without_manual_metric_conversion(self):
        timeline = GameplayObservationTimeline("V03-validation-test")
        timeline.add(
            ObservationKind.CUSTOMER_ARRIVAL,
            GameTimestamp.from_hm(1, 1, 1, 23, 31),
            customer_id="observed-c1",
        )
        timeline.add(
            ObservationKind.STAMINA_SNAPSHOT,
            GameTimestamp.from_hm(1, 1, 1, 23, 40),
            staff_id=SCENARIO_STAFF_ID,
            numeric_value=0,
        )
        timeline.add(
            ObservationKind.CHECKOUT_SERVICE_END,
            GameTimestamp.from_hm(1, 1, 1, 23, 45),
            customer_id="observed-c1",
            staff_id=SCENARIO_STAFF_ID,
            fixture_id="scenario-checkout",
        )

        result = validate_minimal_day_from_observation_timeline(
            self.make_config(),
            timeline,
            ObservationDayCoverage(1, 1, 1),
            mapping=ObservationDayMetricMapping(
                customer_arrival_means_admitted=True,
                checkout_service_end_means_completed_sale=True,
            ),
        )

        self.assertEqual(result.observation.comparison_targets.admitted_arrivals, 1)
        self.assertEqual(result.observation.comparison_targets.completed_checkout_sales, 1)
        by_name = {
            delta.metric: delta.delta
            for delta in result.validation.comparison.deltas
        }
        self.assertEqual(by_name["admitted_arrivals"], 0)
        self.assertEqual(by_name["completed_checkout_sales"], 0)
        self.assertEqual(by_name[f"staff:{SCENARIO_STAFF_ID}:minimum_stamina"], 0)

    def test_partial_timeline_stays_window_only_through_validation_loop(self):
        timeline = GameplayObservationTimeline("partial-test")
        timeline.add(
            ObservationKind.CUSTOMER_ARRIVAL,
            GameTimestamp.from_hm(1, 1, 1, 23, 31),
            customer_id="observed-c1",
        )
        timeline.add(
            ObservationKind.CHECKOUT_SERVICE_END,
            GameTimestamp.from_hm(1, 1, 1, 23, 45),
            customer_id="observed-c1",
        )

        result = validate_minimal_day_from_observation_timeline(
            self.make_config(),
            timeline,
            ObservationDayCoverage(
                1,
                1,
                1,
                start_minute_inclusive=23 * 60 + 30,
                end_minute_exclusive=24 * 60,
            ),
            mapping=ObservationDayMetricMapping(
                customer_arrival_means_admitted=True,
                checkout_service_end_means_completed_sale=True,
            ),
        )

        self.assertEqual(result.observation.window_arrival_count, 1)
        self.assertEqual(result.observation.window_checkout_service_end_count, 1)
        self.assertIsNone(result.observation.comparison_targets.admitted_arrivals)
        self.assertEqual(result.validation.comparison.deltas, ())


if __name__ == "__main__":
    unittest.main()
