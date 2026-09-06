import unittest

from conveni_sim.customer import CustomerState, PurchaseFlow
from conveni_sim.store_grid import Direction, GridPoint, StoreGrid
from conveni_sim.store_runtime import StoreRuntimeHarness


class RemovedCheckoutIntegrityTests(unittest.TestCase):
    def make_runtime(self):
        grid = StoreGrid(6, 6)
        grid.place_fixture(
            instance_id="shelf",
            fixture_id="f1",
            origin_subcell=GridPoint(4, 4),
            footprint_tiles=(1, 1),
            interaction_side=Direction.NORTH,
        )
        grid.place_fixture(
            instance_id="checkout",
            fixture_id="f2",
            origin_subcell=GridPoint(8, 4),
            footprint_tiles=(1, 1),
            interaction_side=Direction.NORTH,
        )
        runtime = StoreRuntimeHarness(grid, initial_cash_yen=5_000_000)
        runtime.add_checkout("checkout", simultaneous_staff_capacity=1)
        runtime.staff.add_staff("s1")
        runtime.inventory.add_slot(
            "slot-a",
            fixture_id="shelf",
            product_id="bread",
            capacity_units=10,
            initial_units=5,
        )
        return runtime

    def test_removed_checkout_rejects_new_customer_route(self):
        runtime = self.make_runtime()
        runtime.grid.remove_fixture("checkout")

        with self.assertRaises(ValueError):
            runtime.add_customer(
                "c1",
                entry_point=GridPoint(0, 0),
                exit_point=GridPoint(0, 10),
                merchandise_fixture_ids=("shelf",),
                checkout_fixture_id="checkout",
            )

        self.assertEqual(runtime.customers.customers, ())

    def test_removed_checkout_rejects_service_before_sale_mutation(self):
        runtime = self.make_runtime()
        runtime.add_customer(
            "c1",
            entry_point=GridPoint(0, 0),
            exit_point=GridPoint(0, 10),
            merchandise_fixture_ids=("shelf",),
            checkout_fixture_id="checkout",
        )
        for _ in range(80):
            if runtime.customers.customer("c1").state is CustomerState.AT_MERCHANDISE:
                break
            runtime.customers.tick()
        runtime.customer_pick_and_continue(
            "c1",
            "slot-a",
            quantity=1,
            unit_sale_price_yen=120,
            flow=PurchaseFlow.CHECKOUT_REQUIRED,
        )
        for _ in range(80):
            if runtime.customers.customer("c1").state is CustomerState.WAITING_CHECKOUT:
                break
            runtime.customers.tick()

        cash_before = runtime.cash.known_cash_yen
        runtime.grid.remove_fixture("checkout")
        with self.assertRaises(ValueError):
            runtime.begin_checkout_service("checkout", staff_id="s1", customer_id="c1")

        self.assertEqual(runtime.cash.known_cash_yen, cash_before)
        self.assertFalse(runtime.purchases.basket("c1").settled)

    def test_removed_checkout_rejects_finish_before_settlement(self):
        runtime = self.make_runtime()
        runtime.add_customer(
            "c1",
            entry_point=GridPoint(0, 0),
            exit_point=GridPoint(0, 10),
            merchandise_fixture_ids=("shelf",),
            checkout_fixture_id="checkout",
        )
        for _ in range(80):
            if runtime.customers.customer("c1").state is CustomerState.AT_MERCHANDISE:
                break
            runtime.customers.tick()
        runtime.customer_pick_and_continue(
            "c1",
            "slot-a",
            quantity=1,
            unit_sale_price_yen=120,
            flow=PurchaseFlow.CHECKOUT_REQUIRED,
        )
        for _ in range(80):
            if runtime.customers.customer("c1").state is CustomerState.WAITING_CHECKOUT:
                break
            runtime.customers.tick()
        runtime.begin_checkout_service("checkout", staff_id="s1", customer_id="c1")

        cash_before = runtime.cash.known_cash_yen
        runtime.grid.remove_fixture("checkout")
        with self.assertRaises(ValueError):
            runtime.finish_checkout_sale("checkout", staff_id="s1")

        self.assertEqual(runtime.cash.known_cash_yen, cash_before)
        self.assertFalse(runtime.purchases.basket("c1").settled)


if __name__ == "__main__":
    unittest.main()
