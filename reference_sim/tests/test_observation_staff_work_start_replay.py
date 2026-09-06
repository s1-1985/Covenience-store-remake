import unittest

from conveni_sim.minimal_day_scenario import (
    MinimalRepresentativeDayScenarioConfig,
    MinimalScenarioLayout,
    MinimalScenarioProduct,
    MinimalScenarioStaff,
    MinimalScenarioTiming,
)
from conveni_sim.observation_day_adapter import ObservationDayCoverage
from conveni_sim.observation_staff_work_start_replay import (
    ObservationStaffWorkStartReplayAdapter,
    ObservationStaffWorkStartReplayMapping,
)
from conveni_sim.observations import GameTimestamp, GameplayObservationTimeline, ObservationKind
from conveni_sim.operating_time import OperatingHours
from conveni_sim.representative_day_metrics import ObservedRepresentativeDayMetrics
from conveni_sim.representative_day_validation import validate_minimal_representative_day
from conveni_sim.staff import StaffTask
from conveni_sim.store_grid import Direction, GridPoint
from conveni_sim.simulation_observations import RepresentativeDayObservationExporter


class ObservationStaffWorkStartReplayTests(unittest.TestCase):
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

    def test_requires_explicit_opt_in_and_target_mapping(self):
        timeline = GameplayObservationTimeline("video")
        timeline.add(
            ObservationKind.REPLENISH_START,
            GameTimestamp.from_hm(1, 1, 1, 23, 32),
            staff_id="scenario-staff",
            fixture_id="scenario-shelf",
        )
        adapter = ObservationStaffWorkStartReplayAdapter()
        with self.assertRaises(ValueError):
            adapter.build_plan(timeline, ObservationDayCoverage(1, 1, 1))
        with self.assertRaises(ValueError):
            adapter.build_plan(
                timeline,
                ObservationDayCoverage(1, 1, 1),
                mapping=ObservationStaffWorkStartReplayMapping(True),
            )

    def test_observed_replenish_start_waits_until_explicit_minute(self):
        timeline = GameplayObservationTimeline("observed-work-start")
        timeline.add(
            ObservationKind.REPLENISH_START,
            GameTimestamp.from_hm(1, 1, 1, 23, 32),
            staff_id="scenario-staff",
            fixture_id="scenario-shelf",
        )
        coverage = ObservationDayCoverage(
            1,
            1,
            1,
            start_minute_inclusive=23 * 60 + 30,
            end_minute_exclusive=24 * 60,
        )
        adapter = ObservationStaffWorkStartReplayAdapter()
        plan = adapter.build_plan(
            timeline,
            coverage,
            mapping=ObservationStaffWorkStartReplayMapping(
                staff_work_start_means_runtime_assignment=True,
                replenish_fixture_targets=(("scenario-shelf", "scenario-slot"),),
            ),
        )
        policy = adapter.build_policy(plan)
        result = validate_minimal_representative_day(
            self.make_config(),
            ObservedRepresentativeDayMetrics(),
            staff_task_policy=policy,
        )
        exported = RepresentativeDayObservationExporter().export(
            result.run,
            result.scenario.runtime,
            source_id="replayed-work-start",
        )
        starts = [
            event
            for event in exported.events
            if event.kind is ObservationKind.REPLENISH_START
        ]
        self.assertEqual(len(starts), 1)
        self.assertEqual(starts[0].game_time.minute_of_day, 23 * 60 + 32)
        self.assertEqual(result.scenario.runtime.inventory.slot("scenario-slot").units, 2)

    def test_missing_expected_target_does_not_fall_back_to_other_candidate(self):
        timeline = GameplayObservationTimeline("observed-work-start")
        timeline.add(
            ObservationKind.REPLENISH_START,
            GameTimestamp.from_hm(1, 1, 1, 23, 31),
            staff_id="scenario-staff",
            fixture_id="unknown-observed-shelf",
        )
        adapter = ObservationStaffWorkStartReplayAdapter()
        plan = adapter.build_plan(
            timeline,
            ObservationDayCoverage(1, 1, 1),
            mapping=ObservationStaffWorkStartReplayMapping(
                staff_work_start_means_runtime_assignment=True,
                replenish_fixture_targets=(("unknown-observed-shelf", "nonexistent-slot"),),
            ),
        )
        result = validate_minimal_representative_day(
            self.make_config(),
            ObservedRepresentativeDayMetrics(),
            staff_task_policy=adapter.build_policy(plan),
        )
        exported = RepresentativeDayObservationExporter().export(
            result.run,
            result.scenario.runtime,
            source_id="no-fallback",
        )
        self.assertFalse(
            any(event.kind is ObservationKind.REPLENISH_START for event in exported.events)
        )
        self.assertEqual(result.scenario.runtime.inventory.slot("scenario-slot").units, 1)


if __name__ == "__main__":
    unittest.main()
