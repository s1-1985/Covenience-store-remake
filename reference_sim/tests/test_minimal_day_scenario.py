import unittest

from conveni_sim.customer import CustomerState
from conveni_sim.minimal_day_scenario import (
    MinimalRepresentativeDayScenarioConfig,
    MinimalScenarioLayout,
    MinimalScenarioProduct,
    MinimalScenarioStaff,
    MinimalScenarioTiming,
    SCENARIO_SLOT_ID,
    SCENARIO_STAFF_ID,
    build_minimal_representative_day_scenario,
)
from conveni_sim.operating_time import OperatingHours
from conveni_sim.scenario_policies import ScheduledScenarioCustomer
from conveni_sim.staff import StaffCondition, StaffTask
from conveni_sim.store_grid import Direction, GridPoint


class MinimalDayScenarioTests(unittest.TestCase):
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
                initial_units=2,
                unit_procurement_cost_yen=50,
                unit_sale_price_yen=120,
                purchase_quantity=1,
            ),
            staff=MinimalScenarioStaff(
                stamina_max=4,
                register_skill=40,
                task_order=(StaffTask.CHECKOUT, StaffTask.REPLENISH, StaffTask.CLEAN),
            ),
            timing=MinimalScenarioTiming(
                step_game_minutes=1,
                checkout_game_minutes=1,
                checkout_stamina_cost=2,
                replenish_game_minutes=1,
                clean_game_minutes=1,
                replenish_up_to_quantity=1,
                replenish_stamina_cost=1,
                clean_stamina_cost=1,
                break_room_target_id="break-room",
                return_to_break_room_game_minutes=1,
                recovery_interval_game_minutes=1,
                recovery_amount=4,
            ),
            arrivals=(
                ScheduledScenarioCustomer(23 * 60 + 31, "c1"),
            ),
            initial_cash_yen=1_000,
            operating_hours=OperatingHours.twenty_four_hours(),
            start_hour=23,
            start_minute=30,
            year=1,
            month=1,
            day=1,
            checkout_staff_capacity=1,
        )

    def test_one_customer_day_runs_from_arrival_through_sale_rest_and_exit(self):
        scenario = build_minimal_representative_day_scenario(self.make_config())

        result = scenario.run()

        customer = scenario.runtime.customers.customer("c1")
        staff = scenario.runtime.staff.staff_member(SCENARIO_STAFF_ID)

        self.assertEqual(customer.state, CustomerState.EXITED)
        self.assertTrue(scenario.runtime.purchases.basket("c1").settled)
        self.assertEqual(staff.condition, StaffCondition.AVAILABLE)
        self.assertEqual(staff.stamina_current, 4)
        self.assertEqual(staff.completed_count(StaffTask.CHECKOUT), 1)
        self.assertEqual(staff.completed_count(StaffTask.REPLENISH), 2)
        self.assertEqual(scenario.runtime.inventory.slot(SCENARIO_SLOT_ID).units, 3)

        self.assertEqual(result.day_end.summary.known_credits_yen, 120)
        self.assertEqual(result.day_end.summary.known_debits_yen, 100)
        self.assertEqual(result.cash_after_yen, 1_020)
        self.assertTrue(result.cash_is_exact_after)
        self.assertEqual(result.boundary_snapshot.minute_of_day, 0)
        self.assertEqual(scenario.calendar.day, 2)

        self.assertTrue(
            any(snapshot.active_checkout_services == 1 for snapshot in result.step_snapshots)
        )
        self.assertTrue(
            any(
                snapshot.staff[0].condition is StaffCondition.RETURNING_TO_BREAK_ROOM
                for snapshot in result.step_snapshots
            )
        )
        self.assertTrue(
            any(snapshot.customer_count(CustomerState.EXITED) == 1 for snapshot in result.step_snapshots)
        )

    def test_arrival_before_configured_start_is_rejected(self):
        config = self.make_config()
        with self.assertRaises(ValueError):
            MinimalRepresentativeDayScenarioConfig(
                layout=config.layout,
                product=config.product,
                staff=config.staff,
                timing=config.timing,
                arrivals=(ScheduledScenarioCustomer(23 * 60 + 29, "too-early"),),
                initial_cash_yen=config.initial_cash_yen,
                operating_hours=config.operating_hours,
                start_hour=config.start_hour,
                start_minute=config.start_minute,
                year=config.year,
                month=config.month,
                day=config.day,
                checkout_staff_capacity=config.checkout_staff_capacity,
            )


if __name__ == "__main__":
    unittest.main()
