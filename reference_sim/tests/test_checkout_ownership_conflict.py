import unittest

from conveni_sim.checkout_ownership_conflict import (
    CheckoutConflictLoserDecision,
    CheckoutConflictLoserDisposition,
    CheckoutOwnershipConflictCoordinator,
    CheckoutOwnershipConflictDecision,
    CheckoutOwnershipConflictStatus,
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


class LeaveConflictUnresolved:
    def resolve(self, context):
        return None


class ChooseSecondReturnFirst:
    def resolve(self, context):
        return CheckoutOwnershipConflictDecision(
            owner_staff_ids=("s2",),
            loser_decisions=(
                CheckoutConflictLoserDecision(
                    "s1",
                    CheckoutConflictLoserDisposition.RETURN_TO_BREAK_ROOM,
                    break_room_target_id="break-room",
                ),
            ),
        )


class BombPolicy:
    def resolve(self, context):
        raise AssertionError("policy must not be called without factual checkout demand")


class MissingLoserPolicy:
    def resolve(self, context):
        return CheckoutOwnershipConflictDecision(
            owner_staff_ids=("s1",),
            loser_decisions=(),
        )


class CheckoutOwnershipConflictTests(unittest.TestCase):
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
        runtime.staff.add_staff("s1", stamina_max=5)
        runtime.staff.add_staff("s2", stamina_max=5)
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

    def assign_both_to_checkout(self, runtime):
        runtime.staff.assign_task("s1", StaffTask.CHECKOUT, target_id="checkout")
        runtime.staff.assign_task("s2", StaffTask.CHECKOUT, target_id="checkout")

    def test_no_checkout_demand_is_not_promoted_to_a_conflict(self):
        runtime = self.make_runtime()
        self.assign_both_to_checkout(runtime)
        evaluation = CheckoutOwnershipConflictCoordinator(runtime).evaluate_checkout(
            "checkout",
            BombPolicy(),
        )

        self.assertEqual(evaluation.status, CheckoutOwnershipConflictStatus.NO_CONFLICT)
        self.assertEqual(evaluation.context.waiting_customer_ids, ())
        self.assertEqual(evaluation.context.contender_staff_ids, ("s1", "s2"))

    def test_unresolved_conflict_does_not_invent_a_winner_from_roster_order(self):
        runtime = self.make_runtime()
        self.add_waiting_customer(runtime)
        orchestrator = StoreStepOrchestrator(
            runtime,
            staff_policy=ChooseCheckoutTask(),
            checkout_policy=ChooseFirstWaitingCustomer(),
            checkout_ownership_policy=LeaveConflictUnresolved(),
        )

        result = orchestrator.step(0)

        self.assertEqual(len(result.checkout_ownership_conflicts), 1)
        conflict = result.checkout_ownership_conflicts[0]
        self.assertEqual(conflict.status, CheckoutOwnershipConflictStatus.UNRESOLVED)
        self.assertEqual(conflict.context.contender_staff_ids, ("s1", "s2"))
        self.assertEqual(result.checkout_selections, ())
        self.assertIsNone(runtime.checkout("checkout").customer_being_served_by("s1"))
        self.assertIsNone(runtime.checkout("checkout").customer_being_served_by("s2"))

    def test_explicit_owner_can_start_service_and_loser_can_return_to_break_room(self):
        runtime = self.make_runtime()
        self.add_waiting_customer(runtime)
        orchestrator = StoreStepOrchestrator(
            runtime,
            staff_policy=ChooseCheckoutTask(),
            checkout_policy=ChooseFirstWaitingCustomer(),
            checkout_ownership_policy=ChooseSecondReturnFirst(),
        )

        result = orchestrator.step(0)

        conflict = result.checkout_ownership_conflicts[0]
        self.assertEqual(conflict.status, CheckoutOwnershipConflictStatus.RESOLVED)
        self.assertEqual(conflict.decision.owner_staff_ids, ("s2",))
        self.assertEqual(len(result.checkout_selections), 1)
        self.assertEqual(result.checkout_selections[0].staff_id, "s2")
        self.assertEqual(runtime.checkout("checkout").customer_being_served_by("s2"), "c1")

        loser = runtime.staff.staff_member("s1")
        self.assertEqual(loser.condition, StaffCondition.RETURNING_TO_BREAK_ROOM)
        self.assertEqual(loser.task, StaffTask.RETURN_TO_BREAK_ROOM)
        self.assertEqual(loser.target_id, "break-room")
        self.assertEqual(loser.stamina_current, 5)

    def test_resolved_decision_must_account_for_every_contender(self):
        runtime = self.make_runtime()
        self.add_waiting_customer(runtime)
        self.assign_both_to_checkout(runtime)

        with self.assertRaises(ValueError):
            CheckoutOwnershipConflictCoordinator(runtime).evaluate_checkout(
                "checkout",
                MissingLoserPolicy(),
            )

        self.assertEqual(runtime.staff.staff_member("s1").task, StaffTask.CHECKOUT)
        self.assertEqual(runtime.staff.staff_member("s2").task, StaffTask.CHECKOUT)
        self.assertIsNone(runtime.checkout("checkout").customer_being_served_by("s1"))
        self.assertIsNone(runtime.checkout("checkout").customer_being_served_by("s2"))


if __name__ == "__main__":
    unittest.main()
