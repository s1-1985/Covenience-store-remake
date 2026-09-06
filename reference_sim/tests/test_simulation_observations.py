import unittest

from conveni_sim.minimal_day_scenario import (
    MinimalRepresentativeDayScenarioConfig,
    MinimalScenarioLayout,
    MinimalScenarioProduct,
    MinimalScenarioStaff,
    MinimalScenarioTiming,
    build_minimal_representative_day_scenario,
)
from conveni_sim.observations import ObservationKind
from conveni_sim.operating_time import OperatingHours
from conveni_sim.scenario_checkout_anger import ServiceElapsedScenarioAngerPolicy
from conveni_sim.scenario_policies import ScheduledScenarioCustomer
from conveni_sim.simulation_observations import RepresentativeDayObservationExporter
from conveni_sim.staff import StaffTask
from conveni_sim.store_grid import Direction, GridPoint


class SimulationObservationExporterTests(unittest.TestCase):
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
                checkout_game_minutes=12,
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
            arrivals=tuple(
                ScheduledScenarioCustomer(22 * 60 + 21 + index, f"c{index + 1}")
                for index in range(4)
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

    def test_clustered_run_exports_same_checkout_vocabulary_as_video_observations(self):
        scenario = build_minimal_representative_day_scenario(
            self.make_config(),
            checkout_anger_policy=ServiceElapsedScenarioAngerPolicy(10),
        )
        run = scenario.run()

        timeline = RepresentativeDayObservationExporter().export(run, scenario.runtime)
        kinds = [event.kind for event in timeline.events]

        self.assertEqual(kinds.count(ObservationKind.CUSTOMER_ARRIVAL), 4)
        self.assertEqual(kinds.count(ObservationKind.CHECKOUT_QUEUE_ENTER), 4)
        self.assertEqual(kinds.count(ObservationKind.CHECKOUT_SERVICE_START), 4)
        self.assertEqual(kinds.count(ObservationKind.CHECKOUT_ANGER), 4)
        self.assertEqual(kinds.count(ObservationKind.CHECKOUT_SERVICE_END), 4)

        service_durations = timeline.checkout_service_durations()
        self.assertEqual(len(service_durations), 4)
        self.assertEqual({item.game_minutes for item in service_durations}, {12})

        service_to_anger = timeline.checkout_service_to_first_anger_durations()
        self.assertEqual(len(service_to_anger), 4)
        self.assertEqual({item.game_minutes for item in service_to_anger}, {10})

        queue_to_anger = timeline.checkout_queue_to_first_anger_durations()
        self.assertEqual(len(queue_to_anger), 4)
        self.assertGreater(max(item.game_minutes for item in queue_to_anger), 10)

        total = timeline.checkout_total_durations()
        self.assertEqual(len(total), 4)
        self.assertGreater(max(item.game_minutes for item in total), 12)

    def test_export_preserves_nondecreasing_game_timestamps(self):
        scenario = build_minimal_representative_day_scenario(
            self.make_config(),
            checkout_anger_policy=ServiceElapsedScenarioAngerPolicy(10),
        )
        timeline = RepresentativeDayObservationExporter().export(
            scenario.run(),
            scenario.runtime,
        )

        ordinal = [event.game_time.representative_ordinal_minute for event in timeline.events]
        self.assertEqual(ordinal, sorted(ordinal))


if __name__ == "__main__":
    unittest.main()
