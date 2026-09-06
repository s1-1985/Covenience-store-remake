import unittest
from types import SimpleNamespace

from conveni_sim.checkout_ownership_conflict import (
    CheckoutConflictLoserDecision,
    CheckoutConflictLoserDisposition,
    CheckoutOwnershipConflictDecision,
)
from conveni_sim.checkout_pre_service_departure import (
    CheckoutPreServiceAction,
    CheckoutPreServiceDecision,
)
from conveni_sim.customer import CustomerState, PurchaseFlow
from conveni_sim.observations import ObservationKind
from conveni_sim.simulation_observations import RepresentativeDayObservationExporter
from conveni_sim.staff import StaffTask
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


class ReturnBeforeService:
    def decide(self, context):
        return CheckoutPreServiceDecision(
            CheckoutPreServiceAction.RETURN_TO_BREAK_ROOM,
            break_room_target_id="break-room",
        )


class CheckoutStaffReturnObservationTests(unittest.TestCase):
    def make_runtime(self, *, two_staff=False):
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
        if two_staff:
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

    def export_single_step(self, runtime, step):
        run = SimpleNamespace(
            year=1,
            month=1,
            day=1,
            steps=(step,),
            step_snapshots=(SimpleNamespace(staff=()),),
        )
        return RepresentativeDayObservationExporter().export(run, runtime)

    def test_ownership_conflict_break_room_loser_exports_cause_neutral_return(self):
        runtime = self.make_runtime(two_staff=True)
        self.add_waiting_customer(runtime)
        orchestrator = StoreStepOrchestrator(
            runtime,
            staff_policy=ChooseCheckoutTask(),
            checkout_policy=ChooseFirstWaitingCustomer(),
            checkout_ownership_policy=ChooseSecondReturnFirst(),
        )

        step = orchestrator.step(0)
        timeline = self.export_single_step(runtime, step)
        returns = [
            event
            for event in timeline.events
            if event.kind is ObservationKind.CHECKOUT_STAFF_RETURN_TO_BREAK_ROOM
        ]

        self.assertEqual(len(returns), 1)
        self.assertEqual(returns[0].staff_id, "s1")
        self.assertEqual(returns[0].fixture_id, "checkout")
        service_starts = [
            event
            for event in timeline.events
            if event.kind is ObservationKind.CHECKOUT_SERVICE_START
        ]
        self.assertEqual(len(service_starts), 1)
        self.assertEqual(service_starts[0].staff_id, "s2")
        self.assertLess(returns[0].sequence, service_starts[0].sequence)

    def test_pre_service_departure_exports_same_cause_neutral_return(self):
        runtime = self.make_runtime()
        self.add_waiting_customer(runtime)
        orchestrator = StoreStepOrchestrator(
            runtime,
            staff_policy=ChooseCheckoutTask(),
            checkout_policy=ChooseFirstWaitingCustomer(),
            checkout_pre_service_departure_policy=ReturnBeforeService(),
        )

        step = orchestrator.step(0)
        timeline = self.export_single_step(runtime, step)
        returns = [
            event
            for event in timeline.events
            if event.kind is ObservationKind.CHECKOUT_STAFF_RETURN_TO_BREAK_ROOM
        ]

        self.assertEqual(len(returns), 1)
        self.assertEqual(returns[0].staff_id, "s1")
        self.assertEqual(returns[0].fixture_id, "checkout")
        self.assertFalse(
            any(
                event.kind is ObservationKind.CHECKOUT_SERVICE_START
                for event in timeline.events
            )
        )


if __name__ == "__main__":
    unittest.main()
