import unittest

from conveni_sim.customer import CustomerState, PurchaseFlow
from conveni_sim.staff import StaffTask
from conveni_sim.staff_task_policy import StaffTaskDecision
from conveni_sim.store_grid import Direction, GridPoint, StoreGrid
from conveni_sim.store_runtime import StoreRuntimeHarness
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


class StoreStepCheckoutSelectionTests(unittest.TestCase):
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

    def test_same_step_staff_assignment_can_start_checkout_without_finishing_it(self):
        runtime = self.make_runtime()
        self.add_waiting_customer(runtime)
        orchestrator = StoreStepOrchestrator(
            runtime,
            staff_policy=ChooseCheckoutPolicy(),
            checkout_policy=ChooseFirstWaitingCustomer(),
        )

        result = orchestrator.step(0)

        self.assertIsNotNone(result.staff_tasks)
        self.assertEqual(runtime.staff.staff_member("s1").task, StaffTask.CHECKOUT)
        self.assertEqual(len(result.checkout_selections), 1)
        self.assertEqual(result.checkout_selections[0].selected_customer_id, "c1")
        self.assertEqual(runtime.checkout("checkout").customer_being_served_by("s1"), "c1")
        self.assertEqual(runtime.cash.known_cash_yen, 1_000)
        self.assertFalse(runtime.purchases.basket("c1").settled)
        self.assertEqual(runtime.customers.customer("c1").state, CustomerState.WAITING_CHECKOUT)

    def test_active_service_is_not_reselected_on_later_steps(self):
        runtime = self.make_runtime()
        self.add_waiting_customer(runtime)
        orchestrator = StoreStepOrchestrator(
            runtime,
            staff_policy=ChooseCheckoutPolicy(),
            checkout_policy=ChooseFirstWaitingCustomer(),
        )
        orchestrator.step(0)

        later = orchestrator.step(1)

        self.assertEqual(later.checkout_selections, ())
        self.assertEqual(runtime.cash.known_cash_yen, 1_000)
        self.assertFalse(runtime.purchases.basket("c1").settled)

        completion = runtime.finish_checkout_sale("checkout", staff_id="s1")
        self.assertEqual(completion.settlement.exact_total_yen, 120)
        self.assertEqual(runtime.cash.known_cash_yen, 1_120)
        self.assertEqual(runtime.customers.customer("c1").state, CustomerState.LEAVING)


if __name__ == "__main__":
    unittest.main()
