import unittest

from conveni_sim.customer import CustomerState, PurchaseFlow
from conveni_sim.economy import BankruptcyPolicy, DayEndOutcome, FinancialEventKind
from conveni_sim.staff import StaffTask
from conveni_sim.store_grid import Direction, GridPoint, StoreGrid
from conveni_sim.store_runtime import StoreRuntimeHarness


class StoreRuntimeIntegrationTests(unittest.TestCase):
    def make_grid(self):
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
        grid.place_fixture(
            instance_id="vending",
            fixture_id="synthetic_vending",
            origin_subcell=GridPoint(4, 2),
            footprint_tiles=(1, 1),
            interaction_side=Direction.NORTH,
        )
        return grid

    def advance_until(self, runtime, customer_id, state, *, limit=100):
        for _ in range(limit):
            if runtime.customers.customer(customer_id).state is state:
                return
            runtime.customers.tick()
        self.fail(f"customer {customer_id} did not reach {state}")

    def test_staffed_checkout_vertical_slice_reaches_sale_and_exit(self):
        runtime = StoreRuntimeHarness(self.make_grid(), initial_cash_yen=1_000)
        runtime.add_checkout("checkout", simultaneous_staff_capacity=1)
        runtime.staff.add_staff("staff-1")
        runtime.inventory.add_slot(
            "bread-slot",
            fixture_id="shelf",
            product_id="bread",
            capacity_units=10,
            initial_units=5,
            unit_procurement_cost_yen=80,
        )
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

        result = runtime.complete_checkout_sale(
            "checkout",
            staff_id="staff-1",
            customer_id="c1",
        )

        self.assertEqual(result.settlement.exact_total_yen, 120)
        self.assertEqual(runtime.inventory.slot("bread-slot").units, 4)
        self.assertEqual(runtime.cash.known_cash_yen, 1_120)
        self.assertEqual(runtime.customers.customer("c1").state, CustomerState.LEAVING)
        self.assertEqual(runtime.staff.staff_member("staff-1").completed_count(StaffTask.CHECKOUT), 1)

        self.advance_until(runtime, "c1", CustomerState.EXITED)

    def test_self_service_candidate_can_settle_without_checkout_runtime(self):
        runtime = StoreRuntimeHarness(self.make_grid(), initial_cash_yen=1_000)
        runtime.inventory.add_slot(
            "vending-slot",
            fixture_id="vending",
            product_id="drink",
            capacity_units=10,
            initial_units=4,
        )
        runtime.add_customer(
            "c1",
            entry_point=GridPoint(0, 0),
            exit_point=GridPoint(0, 8),
            merchandise_fixture_ids=("vending",),
        )

        self.advance_until(runtime, "c1", CustomerState.AT_MERCHANDISE)
        runtime.customer_pick_and_continue(
            "c1",
            "vending-slot",
            quantity=1,
            unit_sale_price_yen=150,
            flow=PurchaseFlow.SELF_SERVICE_CANDIDATE,
        )

        self.assertEqual(runtime.customers.customer("c1").state, CustomerState.LEAVING)
        settlement = runtime.settle_self_service("c1", source_id="vending")
        self.assertEqual(settlement.exact_total_yen, 150)
        self.assertEqual(runtime.cash.known_cash_yen, 1_150)

    def test_replenishment_can_charge_procurement_and_record_staff_work(self):
        runtime = StoreRuntimeHarness(self.make_grid(), initial_cash_yen=1_000)
        runtime.staff.add_staff("staff-1")
        runtime.inventory.add_slot(
            "bread-slot",
            fixture_id="shelf",
            product_id="bread",
            capacity_units=10,
            initial_units=1,
            unit_procurement_cost_yen=80,
        )

        result = runtime.replenish_and_charge(
            "bread-slot",
            2,
            staff_id="staff-1",
        )

        self.assertEqual(result.inventory_mutation.units_after, 3)
        self.assertEqual(result.procurement_event.amount_yen, 160)
        self.assertEqual(runtime.cash.known_cash_yen, 840)
        self.assertEqual(runtime.staff.staff_member("staff-1").completed_count(StaffTask.REPLENISH), 1)

    def test_checkout_registration_requires_a_placed_fixture(self):
        runtime = StoreRuntimeHarness(self.make_grid(), initial_cash_yen=1_000)
        with self.assertRaises(KeyError):
            runtime.add_checkout("missing-checkout", simultaneous_staff_capacity=1)

    def test_customer_pick_must_match_current_merchandise_fixture(self):
        runtime = StoreRuntimeHarness(self.make_grid(), initial_cash_yen=1_000)
        runtime.inventory.add_slot(
            "vending-slot",
            fixture_id="vending",
            product_id="drink",
            capacity_units=10,
            initial_units=4,
        )
        runtime.add_customer(
            "c1",
            entry_point=GridPoint(0, 0),
            exit_point=GridPoint(0, 8),
            merchandise_fixture_ids=("shelf",),
        )
        self.advance_until(runtime, "c1", CustomerState.AT_MERCHANDISE)

        with self.assertRaises(ValueError):
            runtime.customer_pick_and_continue(
                "c1",
                "vending-slot",
                quantity=1,
                unit_sale_price_yen=150,
                flow=PurchaseFlow.SELF_SERVICE_CANDIDATE,
            )

    def test_day_end_policy_is_composed_without_month_formula(self):
        runtime = StoreRuntimeHarness(
            self.make_grid(),
            initial_cash_yen=100,
            bankruptcy_policy=BankruptcyPolicy(check_negative_cash_at_end_of_day=True),
        )
        runtime.cash.record_cost(FinancialEventKind.OTHER, 200)
        result = runtime.close_day()
        self.assertEqual(result.outcome, DayEndOutcome.BANKRUPT)


if __name__ == "__main__":
    unittest.main()
