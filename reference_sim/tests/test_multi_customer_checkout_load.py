import unittest

from conveni_sim.customer import CustomerState
from conveni_sim.minimal_day_scenario import (
    MinimalRepresentativeDayScenarioConfig,
    MinimalScenarioLayout,
    MinimalScenarioProduct,
    MinimalScenarioStaff,
    MinimalScenarioTiming,
    SCENARIO_CHECKOUT_ID,
    build_minimal_representative_day_scenario,
)
from conveni_sim.operating_time import OperatingHours
from conveni_sim.representative_day_metrics import (
    ObservedRepresentativeDayMetrics,
    compare_representative_day_metrics,
    derive_representative_day_metrics,
)
from conveni_sim.scenario_checkout_anger import ServiceElapsedScenarioAngerPolicy
from conveni_sim.scenario_policies import ScheduledScenarioCustomer
from conveni_sim.staff import StaffTask
from conveni_sim.store_grid import Direction, GridPoint


class MultiCustomerCheckoutLoadTests(unittest.TestCase):
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
            arrivals=(
                ScheduledScenarioCustomer(22 * 60 + 21, "c1"),
                ScheduledScenarioCustomer(22 * 60 + 22, "c2"),
                ScheduledScenarioCustomer(22 * 60 + 23, "c3"),
                ScheduledScenarioCustomer(22 * 60 + 24, "c4"),
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

    def test_clustered_customers_create_queue_and_measurable_anger_events(self):
        scenario = build_minimal_representative_day_scenario(
            self.make_config(),
            checkout_anger_policy=ServiceElapsedScenarioAngerPolicy(10),
        )

        run = scenario.run()
        metrics = derive_representative_day_metrics(run)

        self.assertEqual(metrics.attempted_arrivals, 4)
        self.assertEqual(metrics.admitted_arrivals, 4)
        self.assertEqual(metrics.completed_checkout_sales, 4)
        self.assertEqual(metrics.checkout_anger_events, 4)
        self.assertEqual(metrics.known_checkout_revenue_yen, 400)
        self.assertEqual(metrics.known_cash_delta_yen, 400)
        self.assertEqual(metrics.peak_active_checkout_services, 1)
        self.assertGreaterEqual(metrics.peak_waiting_checkout_customers, 1)
        self.assertGreater(metrics.max_pre_service_wait_game_minutes, 0)
        self.assertEqual(metrics.max_checkout_service_game_minutes, 12)
        self.assertGreater(metrics.max_total_checkout_game_minutes, 12)
        self.assertEqual(metrics.exited_customers, 4)

        self.assertIsNotNone(scenario.checkout_anger_penalties)
        self.assertEqual(len(scenario.checkout_anger_penalties.events), 4)
        serviced_ids = tuple(
            record.customer_id
            for record in scenario.runtime.checkout(SCENARIO_CHECKOUT_ID).service_history
        )
        self.assertEqual(len(serviced_ids), 4)
        self.assertEqual(set(serviced_ids), {"c1", "c2", "c3", "c4"})
        self.assertTrue(
            all(
                scenario.runtime.customers.customer(customer_id).state is CustomerState.EXITED
                for customer_id in ("c1", "c2", "c3", "c4")
            )
        )

    def test_checkout_anger_count_is_sparse_comparison_metric(self):
        scenario = build_minimal_representative_day_scenario(
            self.make_config(),
            checkout_anger_policy=ServiceElapsedScenarioAngerPolicy(10),
        )
        metrics = derive_representative_day_metrics(scenario.run())

        comparison = compare_representative_day_metrics(
            metrics,
            ObservedRepresentativeDayMetrics(
                checkout_anger_events=3,
                max_checkout_service_game_minutes=11,
            ),
        )

        self.assertEqual(len(comparison.deltas), 2)
        by_metric = {item.metric: item for item in comparison.deltas}
        self.assertEqual(by_metric["checkout_anger_events"].delta, 1)
        self.assertEqual(by_metric["max_checkout_service_game_minutes"].simulated_value, 12)
        self.assertEqual(by_metric["max_checkout_service_game_minutes"].observed_value, 11)
        self.assertEqual(by_metric["max_checkout_service_game_minutes"].delta, 1)


if __name__ == "__main__":
    unittest.main()
