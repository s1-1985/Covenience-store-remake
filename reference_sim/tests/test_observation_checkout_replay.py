import unittest

from conveni_sim.checkout_service_timing import CheckoutServiceTimingContext
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
from conveni_sim.observation_checkout_replay import (
    ObservationCheckoutDurationReplayAdapter,
    ObservationCheckoutDurationReplayMapping,
)
from conveni_sim.observation_comparison import ObservationIdentityMapping
from conveni_sim.observation_day_adapter import ObservationDayCoverage
from conveni_sim.observations import GameTimestamp, GameplayObservationTimeline, ObservationKind
from conveni_sim.operating_time import OperatingHours
from conveni_sim.scenario_policies import ScheduledScenarioCustomer
from conveni_sim.simulation_observations import RepresentativeDayObservationExporter
from conveni_sim.staff import StaffTask
from conveni_sim.store_grid import Direction, GridPoint


class ObservationCheckoutDurationReplayTests(unittest.TestCase):
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
                checkout_game_minutes=99,
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

    def complete_pair_timeline(self):
        timeline = GameplayObservationTimeline("video")
        timeline.add(
            ObservationKind.CHECKOUT_SERVICE_START,
            GameTimestamp.from_hm(1, 1, 1, 10, 0),
            customer_id="c1",
            staff_id=SCENARIO_STAFF_ID,
            fixture_id=SCENARIO_CHECKOUT_ID,
        )
        timeline.add(
            ObservationKind.CHECKOUT_SERVICE_END,
            GameTimestamp.from_hm(1, 1, 1, 10, 2),
            customer_id="c1",
            staff_id=SCENARIO_STAFF_ID,
            fixture_id=SCENARIO_CHECKOUT_ID,
        )
        return timeline

    def test_replay_requires_explicit_service_pair_semantics(self):
        with self.assertRaises(ValueError):
            ObservationCheckoutDurationReplayAdapter().build_plan(
                self.complete_pair_timeline(),
                ObservationDayCoverage(1, 1, 1),
            )

    def test_complete_pair_becomes_exact_mapped_duration_rule(self):
        timeline = GameplayObservationTimeline("video")
        timeline.add(
            ObservationKind.CHECKOUT_SERVICE_START,
            GameTimestamp.from_hm(1, 1, 1, 10, 0),
            customer_id="video-c1",
            staff_id="video-staff",
            fixture_id="video-register",
        )
        timeline.add(
            ObservationKind.CHECKOUT_SERVICE_END,
            GameTimestamp.from_hm(1, 1, 1, 10, 7),
            customer_id="video-c1",
            staff_id="video-staff",
            fixture_id="video-register",
        )

        plan = ObservationCheckoutDurationReplayAdapter().build_plan(
            timeline,
            ObservationDayCoverage(1, 1, 1),
            mapping=ObservationCheckoutDurationReplayMapping(True),
            identity_mapping=ObservationIdentityMapping(
                customer_ids=(("video-c1", "c1"),),
                staff_ids=(("video-staff", SCENARIO_STAFF_ID),),
                fixture_ids=(("video-register", SCENARIO_CHECKOUT_ID),),
            ),
        )

        self.assertEqual(len(plan.rules), 1)
        rule = plan.rules[0]
        self.assertEqual(rule.customer_id, "c1")
        self.assertEqual(rule.staff_id, SCENARIO_STAFF_ID)
        self.assertEqual(rule.fixture_id, SCENARIO_CHECKOUT_ID)
        self.assertEqual(rule.required_game_minutes, 7)
        self.assertEqual(plan.unpaired_starts, ())
        self.assertEqual(plan.unpaired_ends, ())

    def test_partial_window_end_without_start_stays_unpaired_and_unknown(self):
        timeline = GameplayObservationTimeline("video")
        timeline.add(
            ObservationKind.CHECKOUT_SERVICE_START,
            GameTimestamp.from_hm(1, 1, 1, 9, 59),
            customer_id="c1",
            staff_id=SCENARIO_STAFF_ID,
            fixture_id=SCENARIO_CHECKOUT_ID,
        )
        timeline.add(
            ObservationKind.CHECKOUT_SERVICE_END,
            GameTimestamp.from_hm(1, 1, 1, 10, 3),
            customer_id="c1",
            staff_id=SCENARIO_STAFF_ID,
            fixture_id=SCENARIO_CHECKOUT_ID,
        )
        adapter = ObservationCheckoutDurationReplayAdapter()
        plan = adapter.build_plan(
            timeline,
            ObservationDayCoverage(
                1,
                1,
                1,
                start_minute_inclusive=10 * 60,
                end_minute_exclusive=11 * 60,
            ),
            mapping=ObservationCheckoutDurationReplayMapping(True),
        )
        policy = adapter.build_policy(plan)

        self.assertEqual(plan.rules, ())
        self.assertEqual(len(plan.unpaired_ends), 1)
        context = CheckoutServiceTimingContext(
            staff_id=SCENARIO_STAFF_ID,
            customer_id="c1",
            checkout_fixture_id=SCENARIO_CHECKOUT_ID,
            started_at_absolute_minute=0,
            current_absolute_minute=5,
            elapsed_game_minutes=5,
            register_skill=40,
            simultaneous_staff_capacity=1,
            stamina_current=None,
            stamina_max=None,
        )
        self.assertIsNone(policy.required_game_minutes(context))

    def test_missing_entity_id_is_rejected_instead_of_wildcarded(self):
        timeline = GameplayObservationTimeline("video")
        timeline.add(
            ObservationKind.CHECKOUT_SERVICE_START,
            GameTimestamp.from_hm(1, 1, 1, 10, 0),
            customer_id="c1",
            fixture_id=SCENARIO_CHECKOUT_ID,
        )

        with self.assertRaises(ValueError):
            ObservationCheckoutDurationReplayAdapter().build_plan(
                timeline,
                ObservationDayCoverage(1, 1, 1),
                mapping=ObservationCheckoutDurationReplayMapping(True),
            )

    def test_installed_observed_policy_overrides_synthetic_checkout_duration(self):
        adapter = ObservationCheckoutDurationReplayAdapter()
        plan = adapter.build_plan(
            self.complete_pair_timeline(),
            ObservationDayCoverage(1, 1, 1),
            mapping=ObservationCheckoutDurationReplayMapping(True),
        )
        policy = adapter.build_policy(plan)
        scenario = build_minimal_representative_day_scenario(self.make_config())
        adapter.install_policy(scenario, policy)

        run = scenario.run()
        exported = RepresentativeDayObservationExporter().export(
            run,
            scenario.runtime,
            source_id="sim",
        )
        durations = exported.checkout_service_durations()

        self.assertEqual(len(durations), 1)
        self.assertEqual(durations[0].game_minutes, 2)
        self.assertEqual(scenario.config.timing.checkout_game_minutes, 99)


if __name__ == "__main__":
    unittest.main()
