import unittest

from conveni_sim.checkout_pre_service_departure import (
    CheckoutPreServiceAction,
    CheckoutPreServiceDecision,
    CheckoutPreServiceDepartureCoordinator,
    CheckoutPreServiceDepartureStatus,
)
from conveni_sim.customer import CustomerState, PurchaseFlow
from conveni_sim.staff import StaffCondition, StaffTask
from conveni_sim.staff_task_policy import StaffTaskDecision
from conveni_sim.store_grid import Direction, GridPoint, StoreGrid
from conveni_sim.store_runtime import StoreRuntimeHarness
from conveni_sim.store_step import StoreStepOrchestrator


class ChooseCheckoutTask:
    def choose_task(self, context):
        for candidate in context.candidates:
            if candidate.task is StaffTask.CHECKOUT:
                return StaffTaskDecision(candidate.task, target_id=candidate.target_id)
        return None


class ChooseFirstWaitingCustomer:
    def choose_customer(self, context):
        return context.waiting_customer_ids[0] if context.waiting_customer_ids else None


class UnresolvedDeparture:
    def decide(self, context):
        return None


class ProceedDeparture:
    def __init__(self):
        self.contexts = []

    def decide(self, context):
        self.contexts.append(context)
        return CheckoutPreServiceDecision(CheckoutPreServiceAction.PROCEED_TO_SERVICE)


class ReturnToBreakRoom:
    def decide(self, context):
        return CheckoutPreServiceDecision(
            CheckoutPreServiceAction.RETURN_TO_BREAK_ROOM,
            break_room_target_id="break-room",
        )


class BombPolicy:
    def decide(self, context):
        raise AssertionError("policy must not run without factual checkout demand")


class CheckoutPreServiceDepartureTests(unittest.TestCase):
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
        runtime.staff.add_staff("s1", stamina_max=2)
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

    def make_orchestrator(self, runtime, departure_policy):
        return StoreStepOrchestrator(
            runtime,
            staff_policy=ChooseCheckoutTask(),
            checkout_policy=ChooseFirstWaitingCustomer(),
            checkout_pre_service_departure_policy=departure_policy,
        )

    def test_no_waiting_demand_does_not_consult_departure_policy(self):
        runtime = self.make_runtime()
        runtime.staff.assign_task("s1", StaffTask.CHECKOUT, target_id="checkout")

        evaluation = CheckoutPreServiceDepartureCoordinator(runtime).evaluate_staff(
            "s1",
            BombPolicy(),
        )

        self.assertEqual(
            evaluation.status,
            CheckoutPreServiceDepartureStatus.NOT_APPLICABLE,
        )
        self.assertEqual(evaluation.context.waiting_customer_ids, ())
        self.assertEqual(evaluation.context.stamina_current, 2)
        self.assertEqual(evaluation.context.stamina_max, 2)

    def test_unresolved_departure_blocks_service_without_mutating_assignment(self):
        runtime = self.make_runtime()
        self.add_waiting_customer(runtime)

        result = self.make_orchestrator(runtime, UnresolvedDeparture()).step(0)

        self.assertEqual(len(result.checkout_pre_service_departures), 1)
        self.assertEqual(
            result.checkout_pre_service_departures[0].status,
            CheckoutPreServiceDepartureStatus.UNRESOLVED,
        )
        self.assertEqual(result.checkout_selections, ())
        staff = runtime.staff.staff_member("s1")
        self.assertEqual(staff.condition, StaffCondition.AVAILABLE)
        self.assertEqual(staff.task, StaffTask.CHECKOUT)
        self.assertEqual(staff.target_id, "checkout")
        self.assertEqual(staff.stamina_current, 2)

    def test_explicit_proceed_exposes_factual_stamina_and_starts_service(self):
        runtime = self.make_runtime()
        self.add_waiting_customer(runtime)
        policy = ProceedDeparture()

        result = self.make_orchestrator(runtime, policy).step(0)

        self.assertEqual(len(policy.contexts), 1)
        context = policy.contexts[0]
        self.assertEqual(context.staff_id, "s1")
        self.assertEqual(context.checkout_fixture_id, "checkout")
        self.assertEqual(context.stamina_current, 2)
        self.assertEqual(context.stamina_max, 2)
        self.assertEqual(context.free_service_slots, 1)
        self.assertEqual(context.waiting_customer_ids, ("c1",))
        self.assertEqual(
            result.checkout_pre_service_departures[0].status,
            CheckoutPreServiceDepartureStatus.PROCEED,
        )
        self.assertEqual(len(result.checkout_selections), 1)
        self.assertEqual(runtime.checkout("checkout").customer_being_served_by("s1"), "c1")

    def test_explicit_return_to_break_room_keeps_stamina_unchanged(self):
        runtime = self.make_runtime()
        self.add_waiting_customer(runtime)

        result = self.make_orchestrator(runtime, ReturnToBreakRoom()).step(0)

        self.assertEqual(
            result.checkout_pre_service_departures[0].status,
            CheckoutPreServiceDepartureStatus.DEPARTED,
        )
        self.assertEqual(result.checkout_selections, ())
        staff = runtime.staff.staff_member("s1")
        self.assertEqual(staff.condition, StaffCondition.RETURNING_TO_BREAK_ROOM)
        self.assertEqual(staff.task, StaffTask.RETURN_TO_BREAK_ROOM)
        self.assertEqual(staff.target_id, "break-room")
        self.assertEqual(staff.stamina_current, 2)
        self.assertEqual(runtime.customers.customer("c1").state, CustomerState.WAITING_CHECKOUT)
        self.assertIsNone(runtime.checkout("checkout").customer_being_served_by("s1"))


if __name__ == "__main__":
    unittest.main()
