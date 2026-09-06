import unittest

from conveni_sim.minimal_day_scenario import (
    MinimalRepresentativeDayScenarioConfig,
    MinimalScenarioLayout,
    MinimalScenarioProduct,
    MinimalScenarioStaff,
    MinimalScenarioTiming,
    build_minimal_representative_day_scenario,
)
from conveni_sim.operating_time import OperatingHours
from conveni_sim.scenario_policies import ScheduledScenarioCustomer
from conveni_sim.staff import StaffTask
from conveni_sim.staff_work_interruption import StaffWorkInterruptionContext
from conveni_sim.store_grid import Direction, GridPoint


class InterruptAfterFiveMinutes:
    """Synthetic regression policy; not an original-game threshold."""

    def should_interrupt(self, context: StaffWorkInterruptionContext):
        return (
            context.checkout_demand_present
            and context.work.elapsed_game_minutes >= 5
        )


class AlwaysRequestInterrupt:
    def should_interrupt(self, context: StaffWorkInterruptionContext):
        return True


class StaffWorkInterruptionTests(unittest.TestCase):
    def make_config(self, *, arrivals=True):
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
            arrivals=(ScheduledScenarioCustomer(22 * 60 + 21, "c1"),) if arrivals else (),
            initial_cash_yen=1_000,
            operating_hours=OperatingHours.twenty_four_hours(),
            start_hour=22,
            start_minute=20,
            year=1,
            month=1,
            day=1,
            checkout_staff_capacity=1,
        )

    def test_default_keeps_active_replenishment_locked_despite_checkout_demand(self):
        scenario = build_minimal_representative_day_scenario(self.make_config())
        run = scenario.run()

        self.assertTrue(all(step.staff_work_interruptions == () for step in run.steps))
        first_replenish_end = next(
            step.clock.current_minute_of_day
            for step in run.steps
            if any(item.completed for item in step.staff_work_timing)
        )
        first_checkout_start = next(
            step.clock.current_minute_of_day
            for step in run.steps
            if any(item.service_started is not None for item in step.checkout_selections)
        )
        self.assertGreaterEqual(first_checkout_start, first_replenish_end)

    def test_explicit_policy_can_release_work_and_select_checkout_same_step(self):
        scenario = build_minimal_representative_day_scenario(
            self.make_config(),
            staff_work_interruption_policy=InterruptAfterFiveMinutes(),
        )
        run = scenario.run()

        interrupted_step = next(
            step
            for step in run.steps
            if any(item.interrupted for item in step.staff_work_interruptions)
        )
        interruption = next(
            item for item in interrupted_step.staff_work_interruptions if item.interrupted
        )
        self.assertEqual(interruption.context.work.task, StaffTask.REPLENISH)
        self.assertGreater(interruption.context.total_waiting_checkout_customers, 0)
        self.assertGreaterEqual(interruption.context.work.elapsed_game_minutes, 5)
        self.assertTrue(
            any(item.service_started is not None for item in interrupted_step.checkout_selections)
        )

    def test_true_request_does_not_interrupt_without_checkout_demand(self):
        scenario = build_minimal_representative_day_scenario(
            self.make_config(arrivals=False),
            staff_work_interruption_policy=AlwaysRequestInterrupt(),
        )
        scenario.orchestrator.step(1)  # assigns replenishment
        second = scenario.orchestrator.step(1)  # evaluates active work with no queue

        self.assertEqual(len(second.staff_work_interruptions), 1)
        self.assertTrue(second.staff_work_interruptions[0].requested)
        self.assertFalse(second.staff_work_interruptions[0].interrupted)
        self.assertFalse(second.staff_work_interruptions[0].context.checkout_demand_present)


if __name__ == "__main__":
    unittest.main()
