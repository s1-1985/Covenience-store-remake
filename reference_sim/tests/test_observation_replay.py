import unittest

from conveni_sim.minimal_day_scenario import (
    MinimalRepresentativeDayScenarioConfig,
    MinimalScenarioLayout,
    MinimalScenarioProduct,
    MinimalScenarioStaff,
    MinimalScenarioTiming,
)
from conveni_sim.observation_day_adapter import ObservationDayCoverage
from conveni_sim.observation_replay import (
    ObservationArrivalReplayAdapter,
    ObservationArrivalReplayMapping,
    ObservationArrivalReplayPlan,
    validate_minimal_day_replaying_observed_arrivals,
)
from conveni_sim.observations import (
    GameTimestamp,
    GameplayObservationTimeline,
    ObservationKind,
)
from conveni_sim.operating_time import OperatingHours
from conveni_sim.scenario_policies import ScheduledScenarioCustomer
from conveni_sim.staff import StaffTask
from conveni_sim.store_grid import Direction, GridPoint


class ObservationArrivalReplayTests(unittest.TestCase):
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
                initial_units=3,
                unit_procurement_cost_yen=50,
                unit_sale_price_yen=120,
                purchase_quantity=1,
            ),
            staff=MinimalScenarioStaff(
                stamina_max=None,
                register_skill=40,
                task_order=(StaffTask.CHECKOUT,),
            ),
            timing=MinimalScenarioTiming(
                step_game_minutes=1,
                checkout_game_minutes=2,
                checkout_stamina_cost=None,
                replenish_game_minutes=1,
                clean_game_minutes=1,
                replenish_up_to_quantity=1,
                replenish_stamina_cost=None,
                clean_stamina_cost=None,
                break_room_target_id=None,
                return_to_break_room_game_minutes=1,
                recovery_interval_game_minutes=1,
                recovery_amount=1,
            ),
            arrivals=(ScheduledScenarioCustomer(23 * 60 + 31, "synthetic-original"),),
            initial_cash_yen=1_000,
            operating_hours=OperatingHours.twenty_four_hours(),
            start_hour=23,
            start_minute=30,
            year=1,
            month=1,
            day=1,
            checkout_staff_capacity=1,
        )

    def test_replay_requires_explicit_arrival_semantics(self):
        timeline = GameplayObservationTimeline("video")
        timeline.add(
            ObservationKind.CUSTOMER_ARRIVAL,
            GameTimestamp.from_hm(1, 1, 1, 10, 0),
            customer_id="c1",
        )

        with self.assertRaises(ValueError):
            ObservationArrivalReplayAdapter().build_plan(
                timeline,
                ObservationDayCoverage(1, 1, 1),
            )

    def test_plan_filters_coverage_and_preserves_exact_minutes_and_ids(self):
        timeline = GameplayObservationTimeline("video")
        timeline.add(
            ObservationKind.CUSTOMER_ARRIVAL,
            GameTimestamp.from_hm(1, 1, 1, 8, 0),
            customer_id="outside",
        )
        timeline.add(
            ObservationKind.CUSTOMER_ARRIVAL,
            GameTimestamp.from_hm(1, 1, 1, 10, 7),
            customer_id="c1",
        )
        timeline.add(
            ObservationKind.CUSTOMER_ARRIVAL,
            GameTimestamp.from_hm(1, 1, 2, 10, 8),
            customer_id="other-day",
        )

        plan = ObservationArrivalReplayAdapter().build_plan(
            timeline,
            ObservationDayCoverage(
                1,
                1,
                1,
                start_minute_inclusive=9 * 60,
                end_minute_exclusive=11 * 60,
            ),
            mapping=ObservationArrivalReplayMapping(
                customer_arrival_means_demand_intent=True
            ),
        )

        self.assertEqual(plan.arrival_count, 1)
        self.assertEqual(plan.schedule[0].customer_id, "c1")
        self.assertEqual(plan.schedule[0].minute_of_day, 10 * 60 + 7)

    def test_missing_or_duplicate_customer_ids_are_not_invented(self):
        missing = GameplayObservationTimeline("missing-id")
        missing.add(
            ObservationKind.CUSTOMER_ARRIVAL,
            GameTimestamp.from_hm(1, 1, 1, 10, 0),
        )
        with self.assertRaises(ValueError):
            ObservationArrivalReplayAdapter().build_plan(
                missing,
                ObservationDayCoverage(1, 1, 1),
                mapping=ObservationArrivalReplayMapping(True),
            )

        duplicate = GameplayObservationTimeline("duplicate-id")
        duplicate.add(
            ObservationKind.CUSTOMER_ARRIVAL,
            GameTimestamp.from_hm(1, 1, 1, 10, 0),
            customer_id="c1",
        )
        duplicate.add(
            ObservationKind.CUSTOMER_ARRIVAL,
            GameTimestamp.from_hm(1, 1, 1, 10, 1),
            customer_id="c1",
        )
        with self.assertRaises(ValueError):
            ObservationArrivalReplayAdapter().build_plan(
                duplicate,
                ObservationDayCoverage(1, 1, 1),
                mapping=ObservationArrivalReplayMapping(True),
            )

    def test_replay_does_not_silently_drop_arrival_before_simulation_start(self):
        config = self.make_config()
        plan = ObservationArrivalReplayPlan(
            source_id="video",
            coverage=ObservationDayCoverage(1, 1, 1),
            schedule=(ScheduledScenarioCustomer(23 * 60 + 29, "early"),),
        )

        with self.assertRaises(ValueError):
            ObservationArrivalReplayAdapter().apply_to_config(config, plan)

    def test_one_call_replaces_synthetic_arrivals_and_compares_replayed_event(self):
        timeline = GameplayObservationTimeline("video")
        timeline.add(
            ObservationKind.CUSTOMER_ARRIVAL,
            GameTimestamp.from_hm(1, 1, 1, 23, 35),
            customer_id="video-c1",
        )
        coverage = ObservationDayCoverage(
            1,
            1,
            1,
            start_minute_inclusive=23 * 60 + 30,
            end_minute_exclusive=23 * 60 + 36,
        )

        result = validate_minimal_day_replaying_observed_arrivals(
            self.make_config(),
            timeline,
            coverage,
            replay_mapping=ObservationArrivalReplayMapping(
                customer_arrival_means_demand_intent=True
            ),
        )

        self.assertEqual(
            tuple(item.customer_id for item in result.replay_config.arrivals),
            ("video-c1",),
        )
        self.assertNotIn(
            "synthetic-original",
            tuple(item.customer_id for item in result.replay_config.arrivals),
        )
        self.assertEqual(result.validation.validation.metrics.attempted_arrivals, 1)
        arrival_pairs = [
            item
            for item in result.validation.event_comparison.matched
            if item.signature.kind is ObservationKind.CUSTOMER_ARRIVAL
        ]
        self.assertEqual(len(arrival_pairs), 1)
        self.assertEqual(arrival_pairs[0].game_minute_delta, 0)
        self.assertEqual(
            result.validation.event_comparison.unmatched_observed,
            (),
        )


if __name__ == "__main__":
    unittest.main()
