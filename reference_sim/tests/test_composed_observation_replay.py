import unittest

from conveni_sim.composed_observation_replay import (
    ComposedObservationReplaySelection,
    validate_minimal_day_with_composed_observation_replay,
)
from conveni_sim.minimal_day_scenario import (
    MinimalRepresentativeDayScenarioConfig,
    MinimalScenarioLayout,
    MinimalScenarioProduct,
    MinimalScenarioStaff,
    MinimalScenarioTiming,
    build_minimal_representative_day_scenario,
)
from conveni_sim.observation_anger_replay import (
    ObservationAngerReplayMapping,
    ObservedAngerBasis,
)
from conveni_sim.observation_checkout_replay import ObservationCheckoutDurationReplayMapping
from conveni_sim.observation_comparison import ObservationIdentityMapping
from conveni_sim.observation_day_adapter import ObservationDayCoverage
from conveni_sim.observation_replay import ObservationArrivalReplayMapping
from conveni_sim.operating_time import OperatingHours
from conveni_sim.scenario_checkout_anger import ServiceElapsedScenarioAngerPolicy
from conveni_sim.scenario_policies import ScheduledScenarioCustomer
from conveni_sim.simulation_observations import RepresentativeDayObservationExporter
from conveni_sim.staff import StaffTask
from conveni_sim.store_grid import Direction, GridPoint


class ComposedObservationReplayTests(unittest.TestCase):
    def make_config(self, *, arrival_minute: int, checkout_minutes: int):
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
                checkout_game_minutes=checkout_minutes,
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
            arrivals=(ScheduledScenarioCustomer(arrival_minute, "c1"),),
            initial_cash_yen=1_000,
            operating_hours=OperatingHours.twenty_four_hours(),
            start_hour=23,
            start_minute=30,
            year=1,
            month=1,
            day=1,
            checkout_staff_capacity=1,
        )

    def make_observed_timeline(self):
        source_config = self.make_config(
            arrival_minute=23 * 60 + 31,
            checkout_minutes=3,
        )
        source_scenario = build_minimal_representative_day_scenario(
            source_config,
            checkout_anger_policy=ServiceElapsedScenarioAngerPolicy(2),
        )
        source_run = source_scenario.run()
        return RepresentativeDayObservationExporter().export(
            source_run,
            source_scenario.runtime,
            source_id="synthetic-source-observation",
        )

    def test_arrival_duration_and_anger_can_be_replayed_into_one_exact_run(self):
        observed = self.make_observed_timeline()
        target_config = self.make_config(
            arrival_minute=23 * 60 + 40,
            checkout_minutes=99,
        )
        coverage = ObservationDayCoverage(
            1,
            1,
            1,
            start_minute_inclusive=23 * 60 + 30,
            end_minute_exclusive=24 * 60,
        )

        result = validate_minimal_day_with_composed_observation_replay(
            target_config,
            observed,
            coverage,
            selection=ComposedObservationReplaySelection(
                arrivals=ObservationArrivalReplayMapping(True),
                checkout_durations=ObservationCheckoutDurationReplayMapping(True),
                anger=ObservationAngerReplayMapping(True),
                anger_basis=ObservedAngerBasis.SERVICE_ELAPSED,
            ),
        )

        self.assertIsNotNone(result.arrival_plan)
        self.assertIsNotNone(result.checkout_duration_plan)
        self.assertIsNotNone(result.anger_plan)
        self.assertEqual(result.arrival_plan.schedule[0].minute_of_day, 23 * 60 + 31)
        self.assertEqual(result.checkout_duration_plan.rules[0].required_game_minutes, 3)
        self.assertEqual(result.anger_plan.rules[0].trigger_after_game_minutes, 2)
        self.assertEqual(result.replay_config.timing.checkout_game_minutes, 99)
        self.assertEqual(
            result.validation.validation.metrics.completed_checkout_sales,
            1,
        )
        self.assertTrue(result.validation.event_comparison.exact_event_match)
        self.assertEqual(result.validation.event_comparison.unmatched_observed, ())
        self.assertEqual(result.validation.event_comparison.unmatched_simulated, ())

    def test_each_replay_seam_is_independently_optional(self):
        observed = self.make_observed_timeline()
        target_config = self.make_config(
            arrival_minute=23 * 60 + 31,
            checkout_minutes=3,
        )
        coverage = ObservationDayCoverage(
            1,
            1,
            1,
            start_minute_inclusive=23 * 60 + 30,
            end_minute_exclusive=24 * 60,
        )

        result = validate_minimal_day_with_composed_observation_replay(
            target_config,
            observed,
            coverage,
            selection=ComposedObservationReplaySelection(
                checkout_durations=ObservationCheckoutDurationReplayMapping(True),
            ),
        )

        self.assertIsNone(result.arrival_plan)
        self.assertIsNotNone(result.checkout_duration_plan)
        self.assertIsNone(result.anger_plan)

    def test_anger_mapping_and_basis_must_be_selected_together(self):
        with self.assertRaises(ValueError):
            ComposedObservationReplaySelection(
                anger=ObservationAngerReplayMapping(True),
            )
        with self.assertRaises(ValueError):
            ComposedObservationReplaySelection(
                anger_basis=ObservedAngerBasis.SERVICE_ELAPSED,
            )

    def test_replaying_arrivals_rejects_a_second_customer_id_mapping_layer(self):
        observed = self.make_observed_timeline()
        with self.assertRaises(ValueError):
            validate_minimal_day_with_composed_observation_replay(
                self.make_config(
                    arrival_minute=23 * 60 + 40,
                    checkout_minutes=99,
                ),
                observed,
                ObservationDayCoverage(
                    1,
                    1,
                    1,
                    start_minute_inclusive=23 * 60 + 30,
                    end_minute_exclusive=24 * 60,
                ),
                selection=ComposedObservationReplaySelection(
                    arrivals=ObservationArrivalReplayMapping(True),
                ),
                identity_mapping=ObservationIdentityMapping(
                    customer_ids=(("c1", "other-runtime-id"),),
                ),
            )


if __name__ == "__main__":
    unittest.main()
