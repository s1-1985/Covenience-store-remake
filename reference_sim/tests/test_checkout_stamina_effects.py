import unittest

from conveni_sim.checkout_selection_policy import CheckoutSelectionCoordinator
from conveni_sim.checkout_service_timing import (
    CheckoutServiceCompletionEffects,
    CheckoutServiceTimingCoordinator,
)
from conveni_sim.customer import CustomerState, PurchaseFlow
from conveni_sim.staff import StaffCondition, StaffTask
from conveni_sim.staff_rest_timing import StaffRestTimingCoordinator
from conveni_sim.store_grid import Direction, GridPoint, StoreGrid
from conveni_sim.store_runtime import StoreRuntimeHarness
from conveni_sim.store_step import StoreStepOrchestrator


class SelectFirstWaiting:
    def choose_customer(self, context):
        return context.waiting_customer_ids[0] if context.waiting_customer_ids else None


class FixedDuration:
    def __init__(self, minutes):
        self.minutes = minutes

    def required_game_minutes(self, context):
        return self.minutes


class FixedEffects:
    def __init__(self, stamina_cost, break_room_target_id="break-room"):
        self.effects = CheckoutServiceCompletionEffects(
            stamina_cost=stamina_cost,
            break_room_target_id=break_room_target_id,
        )

    def completion_effects(self, context):
        return self.effects


class NoRestTransition:
    def transition(self, context):
        return None


class CheckoutStaminaEffectsTests(unittest.TestCase):
    def make_runtime(self, *, stamina_max):
        grid = StoreGrid(5, 5)
        grid.place_fixture(
            instance_id="shelf",
            fixture_id="synthetic_shelf",
            origin_subcell=GridPoint(4, 4),
            footprint_tiles=(1, 1),
            interaction_side=Direction.NORTH,
        )
        grid.place_fixture(
            instance_id="checkout",
            fixture_id="synthetic_checkout",
            origin_subcell=GridPoint(6, 4),
            footprint_tiles=(1, 1),
            interaction_side=Direction.NORTH,
        )
        runtime = StoreRuntimeHarness(grid, initial_cash_yen=1_000)
        runtime.add_checkout("checkout", simultaneous_staff_capacity=1)
        runtime.staff.add_staff("s1", stamina_max=stamina_max)
        runtime.inventory.add_slot(
            "bread-slot",
            fixture_id="shelf",
            product_id="bread",
            capacity_units=3,
            initial_units=2,
        )
        return runtime

    def advance_until(self, runtime, state, *, limit=100):
        for _ in range(limit):
            if runtime.customers.customer("c1").state is state:
                return
            runtime.customers.tick()
        self.fail(f"customer did not reach {state}")

    def start_service(self, runtime):
        runtime.add_customer(
            "c1",
            entry_point=GridPoint(0, 0),
            exit_point=GridPoint(0, 8),
            merchandise_fixture_ids=("shelf",),
            checkout_fixture_id="checkout",
        )
        self.advance_until(runtime, CustomerState.AT_MERCHANDISE)
        runtime.customer_pick_and_continue(
            "c1",
            "bread-slot",
            quantity=1,
            unit_sale_price_yen=120,
            flow=PurchaseFlow.CHECKOUT_REQUIRED,
        )
        self.advance_until(runtime, CustomerState.WAITING_CHECKOUT)
        runtime.staff.assign_task("s1", StaffTask.CHECKOUT, target_id="checkout")
        return CheckoutSelectionCoordinator(runtime).evaluate(
            "s1", SelectFirstWaiting()
        ).service_started

    def test_explicit_checkout_stamina_cost_can_enter_break_room_return_state(self):
        runtime = self.make_runtime(stamina_max=1)
        record = self.start_service(runtime)
        timing = CheckoutServiceTimingCoordinator(runtime)
        timing.register_started(record)
        runtime.advance_game_minutes(1)

        result = timing.evaluate_staff(
            "s1",
            FixedDuration(1),
            completion_effects_policy=FixedEffects(1),
        )

        self.assertTrue(result.completed)
        self.assertEqual(result.completion_effects.stamina_cost, 1)
        self.assertEqual(runtime.cash.known_cash_yen, 1_120)
        self.assertTrue(runtime.purchases.basket("c1").settled)
        staff = runtime.staff.staff_member("s1")
        self.assertEqual(staff.stamina_current, 0)
        self.assertEqual(staff.condition, StaffCondition.RETURNING_TO_BREAK_ROOM)
        self.assertEqual(staff.task, StaffTask.RETURN_TO_BREAK_ROOM)
        self.assertEqual(staff.target_id, "break-room")

    def test_unknown_stamina_rejects_effect_before_sale_settlement(self):
        runtime = self.make_runtime(stamina_max=None)
        record = self.start_service(runtime)
        timing = CheckoutServiceTimingCoordinator(runtime)
        timing.register_started(record)
        runtime.advance_game_minutes(1)

        with self.assertRaises(ValueError):
            timing.evaluate_staff(
                "s1",
                FixedDuration(1),
                completion_effects_policy=FixedEffects(1),
            )

        self.assertEqual(runtime.cash.known_cash_yen, 1_000)
        self.assertFalse(runtime.purchases.basket("c1").settled)
        self.assertEqual(runtime.checkout("checkout").customer_being_served_by("s1"), "c1")
        self.assertEqual(len(timing.active_states), 1)

    def test_store_step_registers_checkout_zero_stamina_for_future_rest_step(self):
        runtime = self.make_runtime(stamina_max=1)
        record = self.start_service(runtime)
        timing = CheckoutServiceTimingCoordinator(runtime)
        timing.register_started(record)
        rest = StaffRestTimingCoordinator(runtime)
        orchestrator = StoreStepOrchestrator(
            runtime,
            checkout_timing=timing,
            checkout_duration_policy=FixedDuration(1),
            checkout_completion_effects_policy=FixedEffects(1),
            staff_rest_timing=rest,
            staff_rest_transition_policy=NoRestTransition(),
        )

        result = orchestrator.step(1)

        self.assertTrue(result.checkout_timing[0].completed)
        self.assertEqual(result.staff_rest_timing, ())
        self.assertEqual(runtime.staff.staff_member("s1").condition, StaffCondition.RETURNING_TO_BREAK_ROOM)
        self.assertEqual(len(rest.active_states), 1)


if __name__ == "__main__":
    unittest.main()
