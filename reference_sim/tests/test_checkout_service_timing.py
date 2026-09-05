import unittest

from conveni_sim.checkout_selection_policy import CheckoutSelectionCoordinator
from conveni_sim.checkout_service_timing import CheckoutServiceTimingCoordinator
from conveni_sim.customer import CustomerState, PurchaseFlow
from conveni_sim.operating_time import SubdayClock
from conveni_sim.staff import StaffSkill, StaffTask
from conveni_sim.store_grid import Direction, GridPoint, StoreGrid
from conveni_sim.store_runtime import StoreRuntimeHarness


class SelectCustomerPolicy:
    def choose_customer(self, context):
        return context.waiting_customer_ids[0] if context.waiting_customer_ids else None


class FixedDurationPolicy:
    def __init__(self, duration):
        self.duration = duration
        self.contexts = []

    def required_game_minutes(self, context):
        self.contexts.append(context)
        return self.duration


class CheckoutServiceTimingTests(unittest.TestCase):
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
        runtime = StoreRuntimeHarness(
            grid,
            initial_cash_yen=1_000,
            subday_clock=SubdayClock(10, 0),
        )
        runtime.add_checkout("checkout", simultaneous_staff_capacity=1)
        runtime.staff.add_staff(
            "s1",
            runtime_skills={StaffSkill.REGISTER: 42},
        )
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

    def start_service(self, runtime):
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
        return CheckoutSelectionCoordinator(runtime).evaluate(
            "s1", SelectCustomerPolicy()
        ).service_started

    def test_unknown_duration_keeps_service_active_without_settlement(self):
        runtime = self.make_runtime()
        record = self.start_service(runtime)
        timing = CheckoutServiceTimingCoordinator(runtime)
        timing.register_started(record)

        result = timing.evaluate_staff("s1", FixedDurationPolicy(None))

        self.assertFalse(result.completed)
        self.assertIsNone(result.required_game_minutes)
        self.assertEqual(runtime.cash.known_cash_yen, 1_000)
        self.assertFalse(runtime.purchases.basket("c1").settled)

    def test_context_exposes_elapsed_time_register_skill_and_checkout_capacity(self):
        runtime = self.make_runtime()
        record = self.start_service(runtime)
        timing = CheckoutServiceTimingCoordinator(runtime)
        timing.register_started(record)
        runtime.advance_game_minutes(3)
        policy = FixedDurationPolicy(10)

        result = timing.evaluate_staff("s1", policy)

        self.assertFalse(result.completed)
        self.assertEqual(result.context.elapsed_game_minutes, 3)
        self.assertEqual(result.context.register_skill, 42)
        self.assertEqual(result.context.simultaneous_staff_capacity, 1)

    def test_recovered_duration_completes_only_after_required_game_minutes(self):
        runtime = self.make_runtime()
        record = self.start_service(runtime)
        timing = CheckoutServiceTimingCoordinator(runtime)
        timing.register_started(record)
        policy = FixedDurationPolicy(4)

        runtime.advance_game_minutes(3)
        before = timing.evaluate_staff("s1", policy)
        self.assertFalse(before.completed)
        self.assertEqual(runtime.cash.known_cash_yen, 1_000)

        runtime.advance_game_minutes(1)
        after = timing.evaluate_staff("s1", policy)

        self.assertTrue(after.completed)
        self.assertEqual(after.sale.settlement.exact_total_yen, 120)
        self.assertEqual(runtime.cash.known_cash_yen, 1_120)
        self.assertTrue(runtime.purchases.basket("c1").settled)
        self.assertEqual(runtime.customers.customer("c1").state, CustomerState.LEAVING)
        self.assertEqual(timing.active_states, ())

    def test_future_start_time_is_rejected(self):
        runtime = self.make_runtime()
        record = self.start_service(runtime)
        with self.assertRaises(ValueError):
            CheckoutServiceTimingCoordinator(runtime).register_started(
                record,
                started_at_absolute_minute=runtime.subday_clock.absolute_minutes + 1,
            )

    def test_negative_duration_policy_is_rejected_without_settlement(self):
        runtime = self.make_runtime()
        record = self.start_service(runtime)
        timing = CheckoutServiceTimingCoordinator(runtime)
        timing.register_started(record)
        with self.assertRaises(ValueError):
            timing.evaluate_staff("s1", FixedDurationPolicy(-1))
        self.assertFalse(runtime.purchases.basket("c1").settled)


if __name__ == "__main__":
    unittest.main()
