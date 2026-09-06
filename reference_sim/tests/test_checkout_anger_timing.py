import unittest

from conveni_sim.checkout_anger_penalty import CheckoutAngerPenaltyRuntime
from conveni_sim.checkout_anger_timing import CheckoutAngerTimingCoordinator
from conveni_sim.checkout_service_timing import CheckoutServiceTimingCoordinator
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


class FixedDurationPolicy:
    def __init__(self, duration):
        self.duration = duration

    def required_game_minutes(self, context):
        return self.duration


class TriggerAtServiceElapsed:
    def __init__(self, minutes):
        self.minutes = minutes

    def should_trigger(self, context):
        elapsed = context.service_elapsed_game_minutes
        return elapsed is not None and elapsed >= self.minutes


class TriggerAtTotalElapsed:
    def __init__(self, minutes):
        self.minutes = minutes

    def should_trigger(self, context):
        return context.total_checkout_elapsed_game_minutes >= self.minutes


class CheckoutAngerTimingTests(unittest.TestCase):
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

    def test_service_elapsed_trigger_records_one_penalty_before_checkout_completes(self):
        runtime = self.make_runtime()
        self.add_waiting_customer(runtime)
        penalty = CheckoutAngerPenaltyRuntime(runtime.staff)
        anger = CheckoutAngerTimingCoordinator(runtime, penalty)
        checkout_timing = CheckoutServiceTimingCoordinator(runtime)
        orchestrator = StoreStepOrchestrator(
            runtime,
            staff_policy=ChooseCheckoutPolicy(),
            checkout_policy=ChooseFirstWaitingCustomer(),
            checkout_timing=checkout_timing,
            checkout_duration_policy=FixedDurationPolicy(3),
            checkout_anger_timing=anger,
            checkout_anger_policy=TriggerAtServiceElapsed(2),
        )

        started = orchestrator.step(0)
        self.assertEqual(started.checkout_anger_timing[0].context.service_elapsed_game_minutes, None)
        self.assertEqual(len(anger.active_states), 1)
        self.assertEqual(anger.state("c1").service_started_at_absolute_minute, 0)

        one_minute = orchestrator.step(1)
        self.assertFalse(one_minute.checkout_anger_timing[0].triggered)
        self.assertEqual(one_minute.checkout_anger_timing[0].context.service_elapsed_game_minutes, 1)
        self.assertEqual(penalty.events, ())

        angry = orchestrator.step(1)
        self.assertTrue(angry.checkout_anger_timing[0].triggered)
        self.assertEqual(angry.checkout_anger_timing[0].context.service_elapsed_game_minutes, 2)
        self.assertEqual(len(penalty.events), 1)
        self.assertEqual(penalty.events[0].staff_id, "s1")
        self.assertFalse(runtime.purchases.basket("c1").settled)

        completed = orchestrator.step(1)
        self.assertEqual(len(penalty.events), 1)
        self.assertTrue(completed.checkout_timing[0].completed)
        self.assertTrue(runtime.purchases.basket("c1").settled)

    def test_trigger_without_active_staff_is_not_assigned_to_a_guessed_employee(self):
        runtime = self.make_runtime()
        self.add_waiting_customer(runtime)
        penalty = CheckoutAngerPenaltyRuntime(runtime.staff)
        anger = CheckoutAngerTimingCoordinator(runtime, penalty)
        anger.sync_from_runtime()

        runtime.advance_game_minutes(2)
        evaluation = anger.evaluate_all(TriggerAtTotalElapsed(1))[0]

        self.assertTrue(evaluation.trigger_requested)
        self.assertFalse(evaluation.triggered)
        self.assertIsNone(evaluation.penalty_event)
        self.assertEqual(penalty.events, ())
        self.assertFalse(anger.state("c1").anger_triggered)

    def test_anger_timing_inputs_must_be_supplied_as_a_pair(self):
        runtime = self.make_runtime()
        penalty = CheckoutAngerPenaltyRuntime(runtime.staff)
        anger = CheckoutAngerTimingCoordinator(runtime, penalty)

        with self.assertRaises(ValueError):
            StoreStepOrchestrator(runtime, checkout_anger_timing=anger)
        with self.assertRaises(ValueError):
            StoreStepOrchestrator(runtime, checkout_anger_policy=TriggerAtTotalElapsed(1))


if __name__ == "__main__":
    unittest.main()
