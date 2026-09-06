import unittest

from conveni_sim.checkout_anger_timing import CheckoutAngerTimingContext
from conveni_sim.minimal_day_scenario import (
    MinimalRepresentativeDayScenarioConfig,
    MinimalScenarioLayout,
    MinimalScenarioProduct,
    MinimalScenarioStaff,
    MinimalScenarioTiming,
    SCENARIO_CHECKOUT_ID,
    SCENARIO_STAFF_ID,
    build_minimal_representative_day_scenario,
)
from conveni_sim.observation_anger_replay import (
    ObservationAngerReplayAdapter,
    ObservationAngerReplayMapping,
    ObservedAngerBasis,
)
from conveni_sim.observation_comparison import ObservationIdentityMapping
from conveni_sim.observation_day_adapter import ObservationDayCoverage
from conveni_sim.observations import GameTimestamp, GameplayObservationTimeline, ObservationKind
from conveni_sim.operating_time import OperatingHours
from conveni_sim.scenario_policies import ScheduledScenarioCustomer
from conveni_sim.simulation_observations import RepresentativeDayObservationExporter
from conveni_sim.staff import StaffTask
from conveni_sim.store_grid import Direction, GridPoint


class ObservationAngerReplayTests(unittest.TestCase):
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
                checkout_game_minutes=5,
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

    def test_replay_requires_explicit_anger_pair_semantics(self):
        timeline = GameplayObservationTimeline("video")
        timeline.add(
            ObservationKind.CHECKOUT_QUEUE_ENTER,
            GameTimestamp.from_hm(1, 1, 1, 10, 0),
            customer_id="c1",
            fixture_id=SCENARIO_CHECKOUT_ID,
        )
        timeline.add(
            ObservationKind.CHECKOUT_ANGER,
            GameTimestamp.from_hm(1, 1, 1, 10, 3),
            customer_id="c1",
            fixture_id=SCENARIO_CHECKOUT_ID,
        )

        with self.assertRaises(ValueError):
            ObservationAngerReplayAdapter().build_plan(
                timeline,
                ObservationDayCoverage(1, 1, 1),
                basis=ObservedAngerBasis.QUEUE_ELAPSED,
            )

    def test_queue_basis_uses_explicit_pair_and_identity_mapping(self):
        timeline = GameplayObservationTimeline("video")
        timeline.add(
            ObservationKind.CHECKOUT_QUEUE_ENTER,
            GameTimestamp.from_hm(1, 1, 1, 10, 0),
            customer_id="video-c1",
            fixture_id="video-register",
        )
        timeline.add(
            ObservationKind.CHECKOUT_ANGER,
            GameTimestamp.from_hm(1, 1, 1, 10, 7),
            customer_id="video-c1",
            fixture_id="video-register",
        )

        adapter = ObservationAngerReplayAdapter()
        plan = adapter.build_plan(
            timeline,
            ObservationDayCoverage(1, 1, 1),
            basis=ObservedAngerBasis.QUEUE_ELAPSED,
            mapping=ObservationAngerReplayMapping(True),
            identity_mapping=ObservationIdentityMapping(
                customer_ids=(("video-c1", "c1"),),
                fixture_ids=(("video-register", SCENARIO_CHECKOUT_ID),),
            ),
        )

        self.assertEqual(len(plan.rules), 1)
        rule = plan.rules[0]
        self.assertEqual(rule.customer_id, "c1")
        self.assertEqual(rule.fixture_id, SCENARIO_CHECKOUT_ID)
        self.assertIsNone(rule.staff_id)
        self.assertEqual(rule.trigger_after_game_minutes, 7)

    def test_service_basis_policy_stays_unknown_for_unobserved_service(self):
        timeline = GameplayObservationTimeline("video")
        timeline.add(
            ObservationKind.CHECKOUT_SERVICE_START,
            GameTimestamp.from_hm(1, 1, 1, 10, 0),
            customer_id="c1",
            staff_id=SCENARIO_STAFF_ID,
            fixture_id=SCENARIO_CHECKOUT_ID,
        )
        timeline.add(
            ObservationKind.CHECKOUT_ANGER,
            GameTimestamp.from_hm(1, 1, 1, 10, 3),
            customer_id="c1",
            staff_id=SCENARIO_STAFF_ID,
            fixture_id=SCENARIO_CHECKOUT_ID,
        )
        adapter = ObservationAngerReplayAdapter()
        policy = adapter.build_policy(
            adapter.build_plan(
                timeline,
                ObservationDayCoverage(1, 1, 1),
                basis=ObservedAngerBasis.SERVICE_ELAPSED,
                mapping=ObservationAngerReplayMapping(True),
            )
        )

        known = CheckoutAngerTimingContext(
            customer_id="c1",
            checkout_fixture_id=SCENARIO_CHECKOUT_ID,
            current_absolute_minute=13,
            waiting_started_at_absolute_minute=8,
            service_started_at_absolute_minute=10,
            active_staff_id=SCENARIO_STAFF_ID,
            waiting_customer_count=1,
            active_service_count=1,
        )
        before = CheckoutAngerTimingContext(
            customer_id="c1",
            checkout_fixture_id=SCENARIO_CHECKOUT_ID,
            current_absolute_minute=12,
            waiting_started_at_absolute_minute=8,
            service_started_at_absolute_minute=10,
            active_staff_id=SCENARIO_STAFF_ID,
            waiting_customer_count=1,
            active_service_count=1,
        )
        unknown = CheckoutAngerTimingContext(
            customer_id="c2",
            checkout_fixture_id=SCENARIO_CHECKOUT_ID,
            current_absolute_minute=20,
            waiting_started_at_absolute_minute=8,
            service_started_at_absolute_minute=10,
            active_staff_id=SCENARIO_STAFF_ID,
            waiting_customer_count=1,
            active_service_count=1,
        )

        self.assertFalse(policy.should_trigger(before))
        self.assertTrue(policy.should_trigger(known))
        self.assertIsNone(policy.should_trigger(unknown))

    def test_partial_window_anger_without_anchor_remains_unpaired(self):
        timeline = GameplayObservationTimeline("video")
        timeline.add(
            ObservationKind.CHECKOUT_SERVICE_START,
            GameTimestamp.from_hm(1, 1, 1, 9, 59),
            customer_id="c1",
            staff_id=SCENARIO_STAFF_ID,
            fixture_id=SCENARIO_CHECKOUT_ID,
        )
        timeline.add(
            ObservationKind.CHECKOUT_ANGER,
            GameTimestamp.from_hm(1, 1, 1, 10, 2),
            customer_id="c1",
            staff_id=SCENARIO_STAFF_ID,
            fixture_id=SCENARIO_CHECKOUT_ID,
        )

        plan = ObservationAngerReplayAdapter().build_plan(
            timeline,
            ObservationDayCoverage(
                1,
                1,
                1,
                start_minute_inclusive=10 * 60,
                end_minute_exclusive=11 * 60,
            ),
            basis=ObservedAngerBasis.SERVICE_ELAPSED,
            mapping=ObservationAngerReplayMapping(True),
        )

        self.assertEqual(plan.rules, ())
        self.assertEqual(plan.unpaired_anchors, ())
        self.assertEqual(len(plan.unpaired_angers), 1)

    def test_repeated_anger_after_first_pair_is_not_turned_into_second_rule(self):
        timeline = GameplayObservationTimeline("video")
        timeline.add(
            ObservationKind.CHECKOUT_QUEUE_ENTER,
            GameTimestamp.from_hm(1, 1, 1, 10, 0),
            customer_id="c1",
            fixture_id=SCENARIO_CHECKOUT_ID,
        )
        for minute in (3, 5):
            timeline.add(
                ObservationKind.CHECKOUT_ANGER,
                GameTimestamp.from_hm(1, 1, 1, 10, minute),
                customer_id="c1",
                fixture_id=SCENARIO_CHECKOUT_ID,
            )

        plan = ObservationAngerReplayAdapter().build_plan(
            timeline,
            ObservationDayCoverage(1, 1, 1),
            basis=ObservedAngerBasis.QUEUE_ELAPSED,
            mapping=ObservationAngerReplayMapping(True),
        )

        self.assertEqual(len(plan.rules), 1)
        self.assertEqual(plan.rules[0].trigger_after_game_minutes, 3)
        self.assertEqual(len(plan.unpaired_angers), 1)

    def test_observed_service_threshold_drives_autonomous_anger_timing(self):
        timeline = GameplayObservationTimeline("video")
        timeline.add(
            ObservationKind.CHECKOUT_SERVICE_START,
            GameTimestamp.from_hm(1, 1, 1, 10, 0),
            customer_id="c1",
            staff_id=SCENARIO_STAFF_ID,
            fixture_id=SCENARIO_CHECKOUT_ID,
        )
        timeline.add(
            ObservationKind.CHECKOUT_ANGER,
            GameTimestamp.from_hm(1, 1, 1, 10, 2),
            customer_id="c1",
            staff_id=SCENARIO_STAFF_ID,
            fixture_id=SCENARIO_CHECKOUT_ID,
        )
        adapter = ObservationAngerReplayAdapter()
        policy = adapter.build_policy(
            adapter.build_plan(
                timeline,
                ObservationDayCoverage(1, 1, 1),
                basis=ObservedAngerBasis.SERVICE_ELAPSED,
                mapping=ObservationAngerReplayMapping(True),
            )
        )
        scenario = build_minimal_representative_day_scenario(
            self.make_config(),
            checkout_anger_policy=policy,
        )

        run = scenario.run()
        exported = RepresentativeDayObservationExporter().export(
            run,
            scenario.runtime,
            source_id="sim",
        )
        anger_durations = exported.checkout_service_to_first_anger_durations()

        self.assertEqual(len(anger_durations), 1)
        self.assertEqual(anger_durations[0].game_minutes, 2)
        self.assertIsNotNone(scenario.checkout_anger_penalties)
        self.assertEqual(len(scenario.checkout_anger_penalties.events), 1)


if __name__ == "__main__":
    unittest.main()
