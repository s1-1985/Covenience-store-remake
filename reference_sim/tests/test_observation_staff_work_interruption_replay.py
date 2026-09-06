import unittest

from conveni_sim.minimal_day_scenario import (
    MinimalRepresentativeDayScenarioConfig,
    MinimalScenarioLayout,
    MinimalScenarioProduct,
    MinimalScenarioStaff,
    MinimalScenarioTiming,
    build_minimal_representative_day_scenario,
)
from conveni_sim.observation_day_adapter import ObservationDayCoverage
from conveni_sim.observation_staff_work_interruption_replay import (
    ObservationStaffWorkInterruptionReplayAdapter,
    ObservationStaffWorkInterruptionReplayMapping,
)
from conveni_sim.observations import GameTimestamp, GameplayObservationTimeline, ObservationKind
from conveni_sim.operating_time import OperatingHours
from conveni_sim.representative_day_metrics import ObservedRepresentativeDayMetrics
from conveni_sim.representative_day_validation import validate_minimal_day_with_event_comparison
from conveni_sim.scenario_policies import ScheduledScenarioCustomer
from conveni_sim.simulation_observations import RepresentativeDayObservationExporter
from conveni_sim.staff import StaffTask
from conveni_sim.staff_work_interruption import StaffWorkInterruptionContext
from conveni_sim.store_grid import Direction, GridPoint


class InterruptAfterFiveMinutes:
    """Synthetic source policy for round-trip regression only."""

    def should_interrupt(self, context: StaffWorkInterruptionContext):
        return context.work.elapsed_game_minutes >= 5


class ObservationStaffWorkInterruptionReplayTests(unittest.TestCase):
    def make_config(self):
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
                initial_units=7,
                unit_procurement_cost_yen=50,
                unit_sale_price_yen=100,
                purchase_quantity=1,
            ),
            staff=MinimalScenarioStaff(
                stamina_max=None,
                register_skill=40,
                task_order=(StaffTask.CHECKOUT, StaffTask.REPLENISH),
            ),
            timing=MinimalScenarioTiming(
                step_game_minutes=1,
                checkout_game_minutes=1,
                checkout_stamina_cost=None,
                replenish_game_minutes=20,
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
            arrivals=(ScheduledScenarioCustomer(22 * 60 + 21, "c1"),),
            initial_cash_yen=1_000,
            operating_hours=OperatingHours.twenty_four_hours(),
            start_hour=22,
            start_minute=20,
            year=1,
            month=1,
            day=1,
            checkout_staff_capacity=1,
        )

    def coverage(self):
        return ObservationDayCoverage(
            1,
            1,
            1,
            start_minute_inclusive=22 * 60 + 20,
            end_minute_exclusive=24 * 60,
        )

    def test_requires_explicit_opt_in(self):
        with self.assertRaises(ValueError):
            ObservationStaffWorkInterruptionReplayAdapter().build_plan(
                GameplayObservationTimeline("video"),
                self.coverage(),
            )

    def test_partial_start_and_partial_interrupt_remain_unpaired(self):
        start_only = GameplayObservationTimeline("start-only")
        start_only.add(
            ObservationKind.REPLENISH_START,
            GameTimestamp.from_hm(1, 1, 1, 22, 30),
            staff_id="s1",
            fixture_id="shelf",
        )
        plan = ObservationStaffWorkInterruptionReplayAdapter().build_plan(
            start_only,
            self.coverage(),
            mapping=ObservationStaffWorkInterruptionReplayMapping(True),
        )
        self.assertEqual(plan.rules, ())
        self.assertEqual(len(plan.unpaired_starts), 1)
        self.assertEqual(plan.unpaired_interrupts, ())

        interrupt_only = GameplayObservationTimeline("interrupt-only")
        interrupt_only.add(
            ObservationKind.REPLENISH_INTERRUPT,
            GameTimestamp.from_hm(1, 1, 1, 22, 35),
            staff_id="s1",
            fixture_id="shelf",
        )
        plan = ObservationStaffWorkInterruptionReplayAdapter().build_plan(
            interrupt_only,
            self.coverage(),
            mapping=ObservationStaffWorkInterruptionReplayMapping(True),
        )
        self.assertEqual(plan.rules, ())
        self.assertEqual(plan.unpaired_starts, ())
        self.assertEqual(len(plan.unpaired_interrupts), 1)

    def test_source_interruption_round_trips_through_observation_policy(self):
        config = self.make_config()
        source = build_minimal_representative_day_scenario(
            config,
            staff_work_interruption_policy=InterruptAfterFiveMinutes(),
        )
        source_run = source.run()
        observed = RepresentativeDayObservationExporter().export(
            source_run,
            source.runtime,
            source_id="synthetic-interruption-source",
        )
        interruption_events = [
            event
            for event in observed.events
            if event.kind is ObservationKind.REPLENISH_INTERRUPT
        ]
        self.assertEqual(len(interruption_events), 1)

        adapter = ObservationStaffWorkInterruptionReplayAdapter()
        plan = adapter.build_plan(
            observed,
            self.coverage(),
            mapping=ObservationStaffWorkInterruptionReplayMapping(True),
        )
        self.assertEqual(len(plan.rules), 1)
        self.assertEqual(plan.rules[0].task, StaffTask.REPLENISH)
        self.assertEqual(plan.rules[0].interrupt_after_game_minutes, 5)

        result = validate_minimal_day_with_event_comparison(
            config,
            observed,
            self.coverage(),
            staff_work_interruption_policy=adapter.build_policy(plan),
        )
        replay_interruptions = [
            event
            for event in result.simulated_timeline.events
            if event.kind is ObservationKind.REPLENISH_INTERRUPT
        ]
        self.assertEqual(len(replay_interruptions), 1)
        self.assertEqual(
            replay_interruptions[0].game_time.minute_of_day,
            interruption_events[0].game_time.minute_of_day,
        )
        self.assertTrue(result.event_comparison.exact_event_match)

    def test_elapsed_threshold_does_not_force_interrupt_without_real_checkout_demand(self):
        timeline = GameplayObservationTimeline("video")
        timeline.add(
            ObservationKind.REPLENISH_START,
            GameTimestamp.from_hm(1, 1, 1, 22, 21),
            staff_id="scenario-staff",
            fixture_id="scenario-shelf",
        )
        timeline.add(
            ObservationKind.REPLENISH_INTERRUPT,
            GameTimestamp.from_hm(1, 1, 1, 22, 22),
            staff_id="scenario-staff",
            fixture_id="scenario-shelf",
        )
        adapter = ObservationStaffWorkInterruptionReplayAdapter()
        plan = adapter.build_plan(
            timeline,
            self.coverage(),
            mapping=ObservationStaffWorkInterruptionReplayMapping(True),
        )
        policy = adapter.build_policy(plan)

        # No customer exists yet at the observed elapsed threshold. The runtime
        # coordinator must not invent checkout demand just to satisfy the replay.
        config = self.make_config()
        shifted = MinimalRepresentativeDayScenarioConfig(
            layout=config.layout,
            product=config.product,
            staff=config.staff,
            timing=config.timing,
            arrivals=(ScheduledScenarioCustomer(22 * 60 + 40, "c1"),),
            initial_cash_yen=config.initial_cash_yen,
            operating_hours=config.operating_hours,
            start_hour=config.start_hour,
            start_minute=config.start_minute,
            year=config.year,
            month=config.month,
            day=config.day,
            checkout_staff_capacity=config.checkout_staff_capacity,
        )
        result = validate_minimal_day_with_event_comparison(
            shifted,
            timeline,
            self.coverage(),
            staff_work_interruption_policy=policy,
        )
        simulated_interrupts = [
            event
            for event in result.simulated_timeline.events
            if event.kind is ObservationKind.REPLENISH_INTERRUPT
        ]
        self.assertTrue(simulated_interrupts)
        self.assertGreater(
            simulated_interrupts[0].game_time.minute_of_day,
            22 * 60 + 22,
        )
        self.assertFalse(result.event_comparison.exact_event_match)


if __name__ == "__main__":
    unittest.main()
