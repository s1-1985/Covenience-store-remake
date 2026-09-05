import unittest

from conveni_sim.checkout_selection_policy import CheckoutSelectionCoordinator
from conveni_sim.customer import CustomerState, PurchaseFlow
from conveni_sim.staff import StaffTask
from conveni_sim.store_grid import Direction, GridPoint, StoreGrid
from conveni_sim.store_runtime import StoreRuntimeHarness


class SelectCustomerPolicy:
    def __init__(self, customer_id):
        self.customer_id = customer_id
        self.contexts = []

    def choose_customer(self, context):
        self.contexts.append(context)
        return self.customer_id


class CheckoutSelectionPolicyTests(unittest.TestCase):
    def make_runtime(self, *, capacity=1):
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
        runtime.add_checkout("checkout", simultaneous_staff_capacity=capacity)
        runtime.inventory.add_slot(
            "bread-slot",
            fixture_id="shelf",
            product_id="bread",
            capacity_units=10,
            initial_units=6,
        )
        return runtime

    def advance_until(self, runtime, customer_id, state, *, limit=100):
        for _ in range(limit):
            if runtime.customers.customer(customer_id).state is state:
                return
            runtime.customers.tick()
        self.fail(f"customer {customer_id} did not reach {state}")

    def add_waiting_customer(self, runtime, customer_id, *, price):
        runtime.add_customer(
            customer_id,
            entry_point=GridPoint(0, 0),
            exit_point=GridPoint(0, 8),
            merchandise_fixture_ids=("shelf",),
            checkout_fixture_id="checkout",
        )
        self.advance_until(runtime, customer_id, CustomerState.AT_MERCHANDISE)
        runtime.customer_pick_and_continue(
            customer_id,
            "bread-slot",
            quantity=1,
            unit_sale_price_yen=price,
            flow=PurchaseFlow.CHECKOUT_REQUIRED,
        )
        self.advance_until(runtime, customer_id, CustomerState.WAITING_CHECKOUT)

    def test_policy_may_choose_later_waiting_customer_without_forcing_fifo(self):
        runtime = self.make_runtime()
        runtime.staff.add_staff("s1")
        self.add_waiting_customer(runtime, "c1", price=100)
        self.add_waiting_customer(runtime, "c2", price=200)
        runtime.staff.assign_task("s1", StaffTask.CHECKOUT, target_id="checkout")
        policy = SelectCustomerPolicy("c2")

        result = CheckoutSelectionCoordinator(runtime).evaluate("s1", policy)

        self.assertEqual(result.context.waiting_customer_ids, ("c1", "c2"))
        self.assertEqual(result.selected_customer_id, "c2")
        self.assertIsNotNone(result.service_started)
        self.assertEqual(runtime.checkout("checkout").customer_being_served_by("s1"), "c2")
        self.assertEqual(runtime.cash.known_cash_yen, 1_000)
        self.assertFalse(runtime.purchases.basket("c2").settled)

    def test_service_completion_is_explicit_and_settles_only_selected_customer(self):
        runtime = self.make_runtime()
        runtime.staff.add_staff("s1")
        self.add_waiting_customer(runtime, "c1", price=100)
        self.add_waiting_customer(runtime, "c2", price=200)
        runtime.staff.assign_task("s1", StaffTask.CHECKOUT, target_id="checkout")
        coordinator = CheckoutSelectionCoordinator(runtime)
        coordinator.evaluate("s1", SelectCustomerPolicy("c2"))

        completion = runtime.finish_checkout_sale("checkout", staff_id="s1")

        self.assertEqual(completion.settlement.customer_id, "c2")
        self.assertEqual(completion.settlement.exact_total_yen, 200)
        self.assertEqual(runtime.cash.known_cash_yen, 1_200)
        self.assertTrue(runtime.purchases.basket("c2").settled)
        self.assertFalse(runtime.purchases.basket("c1").settled)
        self.assertEqual(runtime.customers.customer("c2").state, CustomerState.LEAVING)
        self.assertEqual(runtime.customers.customer("c1").state, CustomerState.WAITING_CHECKOUT)

    def test_policy_cannot_select_customer_from_outside_waiting_set(self):
        runtime = self.make_runtime()
        runtime.staff.add_staff("s1")
        self.add_waiting_customer(runtime, "c1", price=100)
        runtime.staff.assign_task("s1", StaffTask.CHECKOUT, target_id="checkout")

        with self.assertRaises(ValueError):
            CheckoutSelectionCoordinator(runtime).evaluate("s1", SelectCustomerPolicy("missing"))

        self.assertEqual(runtime.checkout("checkout").active_services, ())
        self.assertFalse(runtime.purchases.basket("c1").settled)

    def test_full_checkout_capacity_prevents_second_service_start_without_guessing_queue_order(self):
        runtime = self.make_runtime(capacity=1)
        runtime.staff.add_staff("s1")
        runtime.staff.add_staff("s2")
        self.add_waiting_customer(runtime, "c1", price=100)
        self.add_waiting_customer(runtime, "c2", price=200)
        runtime.staff.assign_task("s1", StaffTask.CHECKOUT, target_id="checkout")
        runtime.staff.assign_task("s2", StaffTask.CHECKOUT, target_id="checkout")
        coordinator = CheckoutSelectionCoordinator(runtime)
        coordinator.evaluate("s1", SelectCustomerPolicy("c1"))

        second = coordinator.evaluate("s2", SelectCustomerPolicy("c2"))

        self.assertEqual(second.context.free_service_slots, 0)
        self.assertIsNone(second.selected_customer_id)
        self.assertIsNone(second.service_started)
        self.assertEqual(runtime.checkout("checkout").customer_being_served_by("s1"), "c1")
        self.assertIsNone(runtime.checkout("checkout").customer_being_served_by("s2"))


if __name__ == "__main__":
    unittest.main()
