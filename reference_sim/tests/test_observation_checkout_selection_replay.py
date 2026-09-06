import unittest

from conveni_sim.checkout_selection_policy import CheckoutSelectionContext
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
from conveni_sim.observation_checkout_selection_replay import (
    ObservationCheckoutSelectionReplayAdapter,
    ObservationCheckoutSelectionReplayMapping,
)
from conveni_sim.observation_comparison import ObservationIdentityMapping
from conveni_sim.observation_day_adapter import ObservationDayCoverage
from conveni_sim.observations import GameTimestamp, GameplayObservationTimeline, ObservationKind
from conveni_sim.operating_time import OperatingHours
from conveni_sim.scenario_policies import ScheduledScenarioCustomer
from conveni_sim.simulation_observations import RepresentativeDayObservationExporter
from conveni_sim.staff import StaffTask
from conveni_sim.store_grid import Direction, GridPoint


class ObservationCheckoutSelectionReplayTests(unittest.TestCase):
    def test_replay_requires_explicit_service_start_semantics(self):
        timeline = GameplayObservationTimeline("video")
        timeline.add(
            ObservationKind.CHECKOUT_SERVICE_START,
            GameTimestamp.from_hm(1, 1, 1, 10, 0),
            customer_id="c1",
            staff_id="s1",
            fixture_id="checkout",
        )

        with self.assertRaises(ValueError):
            ObservationCheckoutSelectionReplayAdapter().build_plan(
                timeline,
                ObservationDayCoverage(1, 1, 1),
            )

    def test_plan_maps_explicit_ids_and_preserves_start_minute(self):
        timeline = GameplayObservationTimeline("video")
        timeline.add(
            ObservationKind.CHECKOUT_SERVICE_START,
            GameTimestamp.from_hm(1, 1, 1, 10, 7),
            customer_id="video-c1",
            staff_id="video-staff",
            fixture_id="video-register",
        )

        plan = ObservationCheckoutSelectionReplayAdapter().build_plan(
            timeline,
            ObservationDayCoverage(1, 1, 1),
            mapping=ObservationCheckoutSelectionReplayMapping(True),
            identity_mapping=ObservationIdentityMapping(
                customer_ids=(("video-c1", "c1"),),
                staff_ids=(("video-staff", "s1"),),
                fixture_ids=(("video-register", "checkout"),),
            ),
        )

        self.assertEqual(len(plan.rules), 1)
        rule = plan.rules[0]
        self.assertEqual((rule.customer_id, rule.staff_id, rule.fixture_id), ("c1", "s1", "checkout"))
        self.assertEqual(rule.start_minute_of_day, 10 * 60 + 7)

    def test_policy_never_starts_before_observed_minute(self):
        timeline = GameplayObservationTimeline("video")
        timeline.add(
            ObservationKind.CHECKOUT_SERVICE_START,
            GameTimestamp.from_hm(1, 1, 1, 10, 7),
            customer_id="c2",
            staff_id="s1",
            fixture_id="checkout",
        )
        adapter = ObservationCheckoutSelectionReplayAdapter()
        policy = adapter.build_policy(
            adapter.build_plan(
                timeline,
                ObservationDayCoverage(1, 1, 1),
                mapping=ObservationCheckoutSelectionReplayMapping(True),
            )
        )

        before = CheckoutSelectionContext(
            staff_id="s1",
            checkout_fixture_id="checkout",
            waiting_customer_ids=("c1", "c2"),
            active_service_count=0,
            simultaneous_staff_capacity=1,
            current_minute_of_day=10 * 60 + 6,
        )
        exact = CheckoutSelectionContext(
            staff_id="s1",
            checkout_fixture_id="checkout",
            waiting_customer_ids=("c1", "c2"),
            active_service_count=0,
            simultaneous_staff_capacity=1,
            current_minute_of_day=10 * 60 + 7,
        )

        self.assertIsNone(policy.choose_customer(before))
        self.assertEqual(policy.choose_customer(exact), "c2")

    def test_policy_does_not_skip_missing_expected_customer_for_another_waiter(self):
        timeline = GameplayObservationTimeline("video")
        timeline.add(
            ObservationKind.CHECKOUT_SERVICE_START,
            GameTimestamp.from_hm(1, 1, 1, 10, 0),
            customer_id="expected",
            staff_id="s1",
            fixture_id="checkout",
        )
        adapter = ObservationCheckoutSelectionReplayAdapter()
        policy = adapter.build_policy(
            adapter.build_plan(
                timeline,
                ObservationDayCoverage(1, 1, 1),
                mapping=ObservationCheckoutSelectionReplayMapping(True),
            )
        )
        context = CheckoutSelectionContext(
            staff_id="s1",
            checkout_fixture_id="checkout",
            waiting_customer_ids=("other",),
            active_service_count=0,
            simultaneous_staff_capacity=1,
            current_minute_of_day=10 * 60 + 10,
        )

        self.assertIsNone(policy.choose_customer(context))
        self.assertEqual(policy.pending_rule("s1", "checkout").customer_id, "expected")

    def make_non_fifo_config(self):
        return MinimalRepresentativeDayScenarioConfig(
            layout=MinimalScenarioLayout(
                width_tiles=7,
                height_tiles=6,
                shelf_origin_subcell=GridPoint(4, 4),
                shelf_footprint_tiles=(2, 1),
                shelf_interaction_side=Direction.NORTH,
                checkout_origin_subcell=GridPoint(8, 6),
                checkout_footprint_tiles=(2, 1),
                checkout_interaction_side=Direction.NORTH,
                entry_point=GridPoint(0, 0),
                exit_point=GridPoint(0, 10),
            ),
            product=MinimalScenarioProduct(
                product_id="bread",
                capacity_units=8,
                initial_units=8,
                unit_procurement_cost_yen=50,
                unit_sale_price_yen=100,
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
                traffic_reroute_after_blocked_ticks=1,
            ),
            arrivals=(
                ScheduledScenarioCustomer(22 * 60 + 21, "c1"),
                ScheduledScenarioCustomer(22 * 60 + 22, "c2"),
            ),
            initial_cash_yen=1_000,
            operating_hours=OperatingHours.twenty_four_hours(),
            start_hour=22,
            start_minute=20,
            year=1,
            month=1,
            day=1,
            checkout_staff_capacity=1,
        )

    def test_observed_policy_can_replay_later_arrival_before_earlier_waiter(self):
        timeline = GameplayObservationTimeline("video")
        for hour, minute, customer in ((23, 0, "c2"), (23, 3, "c1")):
            timeline.add(
                ObservationKind.CHECKOUT_SERVICE_START,
                GameTimestamp.from_hm(1, 1, 1, hour, minute),
                customer_id=customer,
                staff_id=SCENARIO_STAFF_ID,
                fixture_id=SCENARIO_CHECKOUT_ID,
            )
        adapter = ObservationCheckoutSelectionReplayAdapter()
        policy = adapter.build_policy(
            adapter.build_plan(
                timeline,
                ObservationDayCoverage(1, 1, 1),
                mapping=ObservationCheckoutSelectionReplayMapping(True),
            )
        )
        scenario = build_minimal_representative_day_scenario(self.make_non_fifo_config())
        scenario.orchestrator.checkout_policy = policy

        run = scenario.run()
        history = scenario.runtime.checkout(SCENARIO_CHECKOUT_ID).service_history
        self.assertEqual(tuple(item.customer_id for item in history), ("c2", "c1"))

        exported = RepresentativeDayObservationExporter().export(
            run,
            scenario.runtime,
            source_id="sim",
        )
        starts = [
            event
            for event in exported.events
            if event.kind is ObservationKind.CHECKOUT_SERVICE_START
        ]
        self.assertEqual(tuple(event.customer_id for event in starts), ("c2", "c1"))
        self.assertEqual(tuple(event.game_time.minute_of_day for event in starts), (23 * 60, 23 * 60 + 3))


if __name__ == "__main__":
    unittest.main()
