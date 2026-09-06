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
from conveni_sim.observation_staff_work_replay import (
    ObservationStaffWorkDurationReplayAdapter,
    ObservationStaffWorkDurationReplayMapping,
)
from conveni_sim.observations import GameTimestamp, GameplayObservationTimeline, ObservationKind
from conveni_sim.operating_time import OperatingHours
from conveni_sim.representative_day_metrics import ObservedRepresentativeDayMetrics
from conveni_sim.representative_day_validation import validate_minimal_representative_day
from conveni_sim.scenario_policies import ScheduledScenarioCustomer
from conveni_sim.simulation_observations import RepresentativeDayObservationExporter
from conveni_sim.staff import StaffTask
from conveni_sim.store_grid import Direction, GridPoint


class ObservationStaffWorkReplayTests(unittest.TestCase):
    def make_config(self, *, replenish_minutes: int):
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
                capacity_units=2,
                initial_units=1,
                unit_procurement_cost_yen=50,
                unit_sale_price_yen=120,
                purchase_quantity=1,
            ),
            staff=MinimalScenarioStaff(
                stamina_max=None,
                register_skill=40,
                task_order=(StaffTask.REPLENISH,),
            ),
            timing=MinimalScenarioTiming(
                step_game_minutes=1,
                checkout_game_minutes=1,
                checkout_stamina_cost=None,
                replenish_game_minutes=replenish_minutes,
                clean_game_minutes=1,
                replenish_up_to_quantity=1,
                replenish_stamina_cost=None,
                clean_stamina_cost=None,
                break_room_target_id=None,
                return_to_break_room_game_minutes=1,
                recovery_interval_game_minutes=1,
                recovery_amount=1,
            ),
            arrivals=(),
            initial_cash_yen=1_000,
            operating_hours=OperatingHours.twenty_four_hours(),
            start_hour=23,
            start_minute=30,
            year=1,
            month=1,
            day=1,
            checkout_staff_capacity=1,
        )

    def test_requires_explicit_opt_in(self):
        timeline = GameplayObservationTimeline("video")
        with self.assertRaises(ValueError):
            ObservationStaffWorkDurationReplayAdapter().build_plan(
                timeline,
                ObservationDayCoverage(1, 1, 1),
            )

    def test_partial_pair_remains_unresolved(self):
        timeline = GameplayObservationTimeline("partial")
        timeline.add(
            ObservationKind.REPLENISH_START,
            GameTimestamp.from_hm(1, 1, 1, 10, 0),
            staff_id="s1",
            fixture_id="shelf",
        )
        plan = ObservationStaffWorkDurationReplayAdapter().build_plan(
            timeline,
            ObservationDayCoverage(
                1, 1, 1, start_minute_inclusive=10 * 60, end_minute_exclusive=10 * 60 + 5
            ),
            mapping=ObservationStaffWorkDurationReplayMapping(True),
        )
        self.assertEqual(plan.rules, ())
        self.assertEqual(len(plan.unpaired_starts), 1)
        self.assertEqual(plan.unpaired_ends, ())

    def test_observed_replenish_duration_overrides_synthetic_duration_only(self):
        source = build_minimal_representative_day_scenario(
            self.make_config(replenish_minutes=3)
        )
        source_run = source.run()
        observed = RepresentativeDayObservationExporter().export(
            source_run,
            source.runtime,
            source_id="synthetic-observed-work",
        )
        coverage = ObservationDayCoverage(
            1,
            1,
            1,
            start_minute_inclusive=23 * 60 + 30,
            end_minute_exclusive=24 * 60,
        )
        adapter = ObservationStaffWorkDurationReplayAdapter()
        plan = adapter.build_plan(
            observed,
            coverage,
            mapping=ObservationStaffWorkDurationReplayMapping(True),
        )
        self.assertEqual(len(plan.rules), 1)
        self.assertEqual(plan.rules[0].task, StaffTask.REPLENISH)
        self.assertEqual(plan.rules[0].required_game_minutes, 3)

        target_config = self.make_config(replenish_minutes=99)
        policy = adapter.build_policy(
            plan,
            replenish_up_to_quantity=target_config.timing.replenish_up_to_quantity,
            replenish_stamina_cost=target_config.timing.replenish_stamina_cost,
            clean_stamina_cost=target_config.timing.clean_stamina_cost,
            break_room_target_id=target_config.timing.break_room_target_id,
        )
        result = validate_minimal_representative_day(
            target_config,
            ObservedRepresentativeDayMetrics(),
            staff_work_completion_policy=policy,
        )
        exported = RepresentativeDayObservationExporter().export(
            result.run,
            result.scenario.runtime,
            source_id="replayed-work",
        )
        durations = []
        starts = {}
        for event in exported.events:
            if event.kind is ObservationKind.REPLENISH_START:
                starts[event.staff_id] = event
            elif event.kind is ObservationKind.REPLENISH_END:
                start = starts.pop(event.staff_id)
                durations.append(start.game_time.minutes_until(event.game_time))
        self.assertEqual(durations, [3])
        self.assertEqual(result.scenario.runtime.inventory.slot("scenario-slot").units, 2)
        self.assertEqual(result.replay if hasattr(result, "replay") else None, None)


if __name__ == "__main__":
    unittest.main()
