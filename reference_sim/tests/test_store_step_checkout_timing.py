import unittest

from conveni_sim.checkout_service_timing import CheckoutServiceTimingCoordinator
from conveni_sim.customer import CustomerState, PurchaseFlow
from conveni_sim.staff import StaffTask
from conveni_sim.staff_task_policy import StaffTaskDecision
from conveni_sim.store_grid import Direction, GridPoint, StoreGrid
from conveni_sim.store_runtime import CheckoutSaleCompletion, StoreRuntimeHarness
from conveni_sim.store_step import StoreStepOrchestrator


class ChooseCheckoutPolicy:
    def choose_task(self, context):
        for candidate in context.candidates:
            if candidate.task is StaffTask.CHECKOUT:
                return StaffTaskDecision(candidate.task, target_id=candidate.target_id)
        return None


class ChooseFirstWaitingCustomer:
    def choose_customer(self, context):
        return context.waiting_customer_ids[0] if context.waiting_customer_ids else None


class FixedDurationPolicy:
    def __init__(self, duration):
        self.duration = duration

    def required_game_minutes(self, context):
        return self.duration


class StoreStepCheckoutTimingTests(unittest.TestCase):
    def make_runtime(self):
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
        runtime.staff.add_staff("s1")
        runtime.inventory.add_slot(
            "bread-slot",
            fixture_id="shelf",
            product_id="bread",
            capacity_units=5,
            initial_units=2,
        )
        return runtime

    def advance_until(self, runtime, state, *, limit=100):
        for _ in range(limit):
            if runtime.customers.customer("c1").state is state:
                return
            runtime.customers.tick()
        self.fail(f"customer did not reach {state}")

    def add_waiting_customer(self, runtime):
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

    def test_store_steps_register_elapsed_and_complete_checkout(self):
        runtime = self.make_runtime()
        self.add_waiting_customer(runtime)
        timing = CheckoutServiceTimingCoordinator(runtime)
        orchestrator = StoreStepOrchestrator(
            runtime,
            staff_policy=ChooseCheckoutPolicy(),
            checkout_policy=ChooseFirstWaitingCustomer(),
            checkout_timing=timing,
            checkout_duration_policy=FixedDurationPolicy(3),
        )

        started = orchestrator.step(0)

        self.assertEqual(started.checkout_timing, ())
        self.assertEqual(len(started.checkout_selections), 1)
        self.assertEqual(len(timing.active_states), 1)
        self.assertEqual(timing.active_states[0].customer_id, "c1")
        self.assertEqual(runtime.cash.known_cash_yen, 1_000)

        waiting = orchestrator.step(2)

        self.assertEqual(len(waiting.checkout_timing), 1)
        self.assertFalse(waiting.checkout_timing[0].completed)
        self.assertEqual(waiting.checkout_timing[0].context.elapsed_game_minutes, 2)
        self.assertFalse(runtime.purchases.basket("c1").settled)
        self.assertEqual(runtime.cash.known_cash_yen, 1_000)

        completed = orchestrator.step(1)

        self.assertEqual(len(completed.checkout_timing), 1)
        self.assertTrue(completed.checkout_timing[0].completed)
        self.assertIsInstance(completed.checkout_timing[0].sale, CheckoutSaleCompletion)
        self.assertEqual(completed.checkout_timing[0].sale.settlement.exact_total_yen, 120)
        self.assertEqual(timing.active_states, ())
        self.assertTrue(runtime.purchases.basket("c1").settled)
        self.assertEqual(runtime.cash.known_cash_yen, 1_120)

    def test_checkout_timing_inputs_must_be_supplied_as_a_pair(self):
        runtime = self.make_runtime()
        timing = CheckoutServiceTimingCoordinator(runtime)

        with self.assertRaises(ValueError):
            StoreStepOrchestrator(runtime, checkout_timing=timing)
        with self.assertRaises(ValueError):
            StoreStepOrchestrator(
                runtime,
                checkout_duration_policy=FixedDurationPolicy(3),
            )


if __name__ == "__main__":
    unittest.main()
