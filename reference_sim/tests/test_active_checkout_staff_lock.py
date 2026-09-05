import unittest

from conveni_sim.checkout_selection_policy import CheckoutSelectionCoordinator
from conveni_sim.customer import CustomerState, PurchaseFlow
from conveni_sim.staff import StaffTask
from conveni_sim.staff_task_policy import StaffTaskDecision
from conveni_sim.store_grid import Direction, GridPoint, StoreGrid
from conveni_sim.store_runtime import StoreRuntimeHarness
from conveni_sim.store_step import StoreStepOrchestrator


class FirstWaitingCustomerPolicy:
    def choose_customer(self, context):
        return context.waiting_customer_ids[0] if context.waiting_customer_ids else None


class PreferReplenishmentPolicy:
    def __init__(self):
        self.called_staff_ids = []

    def choose_task(self, context):
        self.called_staff_ids.append(context.staff_id)
        for candidate in context.candidates:
            if candidate.task is StaffTask.REPLENISH:
                return StaffTaskDecision(candidate.task, candidate.target_id)
        return None


class ActiveCheckoutStaffLockTests(unittest.TestCase):
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
            capacity_units=10,
            initial_units=5,
        )
        return runtime

    def advance_until(self, runtime, customer_id, state, *, limit=100):
        for _ in range(limit):
            if runtime.customers.customer(customer_id).state is state:
                return
            runtime.customers.tick()
        self.fail(f"customer {customer_id} did not reach {state}")

    def start_checkout_service(self, runtime):
        runtime.add_customer(
            "c1",
            entry_point=GridPoint(0, 0),
            exit_point=GridPoint(0, 8),
            merchandise_fixture_ids=("shelf",),
            checkout_fixture_id="checkout",
        )
        self.advance_until(runtime, "c1", CustomerState.AT_MERCHANDISE)
        runtime.customer_pick_and_continue(
            "c1",
            "bread-slot",
            quantity=1,
            unit_sale_price_yen=120,
            flow=PurchaseFlow.CHECKOUT_REQUIRED,
        )
        self.advance_until(runtime, "c1", CustomerState.WAITING_CHECKOUT)
        runtime.staff.assign_task("s1", StaffTask.CHECKOUT, target_id="checkout")
        CheckoutSelectionCoordinator(runtime).evaluate(
            "s1", FirstWaitingCustomerPolicy()
        )

    def test_active_checkout_service_locks_staff_out_of_generic_task_policy(self):
        runtime = self.make_runtime()
        self.start_checkout_service(runtime)
        policy = PreferReplenishmentPolicy()
        orchestrator = StoreStepOrchestrator(runtime, staff_policy=policy)

        result = orchestrator.step(1)

        self.assertEqual(policy.called_staff_ids, [])
        self.assertEqual(result.staff_tasks.unavailable_staff_ids, ("s1",))
        staff = runtime.staff.staff_member("s1")
        self.assertEqual(staff.task, StaffTask.CHECKOUT)
        self.assertEqual(staff.target_id, "checkout")
        self.assertEqual(runtime.checkout("checkout").customer_being_served_by("s1"), "c1")
        self.assertFalse(runtime.purchases.basket("c1").settled)

    def test_staff_becomes_eligible_for_generic_policy_after_explicit_checkout_finish(self):
        runtime = self.make_runtime()
        self.start_checkout_service(runtime)
        runtime.finish_checkout_sale("checkout", staff_id="s1")
        policy = PreferReplenishmentPolicy()
        orchestrator = StoreStepOrchestrator(runtime, staff_policy=policy)

        result = orchestrator.step(1)

        self.assertEqual(policy.called_staff_ids, ["s1"])
        self.assertEqual(result.staff_tasks.unavailable_staff_ids, ())
        self.assertEqual(runtime.staff.staff_member("s1").task, StaffTask.REPLENISH)
        self.assertEqual(runtime.staff.staff_member("s1").target_id, "bread-slot")


if __name__ == "__main__":
    unittest.main()
