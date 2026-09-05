import unittest

from conveni_sim.customer import CustomerState, PurchaseFlow
from conveni_sim.customer_purchase_policy import (
    CustomerPurchaseCoordinator,
    CustomerPurchaseDecision,
    MerchandiseOffer,
)
from conveni_sim.store_grid import Direction, GridPoint, StoreGrid
from conveni_sim.store_runtime import StoreRuntimeHarness


class RecordingPurchasePolicy:
    def __init__(self, decision=None):
        self.decision = decision
        self.contexts = []

    def choose_purchase(self, context):
        self.contexts.append(context)
        return self.decision


class CustomerPurchasePolicyTests(unittest.TestCase):
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
        grid.place_fixture(
            instance_id="vending",
            fixture_id="synthetic_vending",
            origin_subcell=GridPoint(8, 2),
            footprint_tiles=(1, 1),
            interaction_side=Direction.NORTH,
        )
        runtime = StoreRuntimeHarness(grid, initial_cash_yen=1_000)
        runtime.inventory.add_slot(
            "bread-slot",
            fixture_id="shelf",
            product_id="bread",
            capacity_units=10,
            initial_units=5,
        )
        runtime.inventory.add_slot(
            "empty-slot",
            fixture_id="shelf",
            product_id="sold-out",
            capacity_units=10,
            initial_units=0,
        )
        runtime.inventory.add_slot(
            "drink-slot",
            fixture_id="vending",
            product_id="drink",
            capacity_units=10,
            initial_units=3,
        )
        return runtime

    def advance_until(self, runtime, customer_id, state, *, limit=100):
        for _ in range(limit):
            if runtime.customers.customer(customer_id).state is state:
                return
            runtime.customers.tick()
        self.fail(f"customer {customer_id} did not reach {state}")

    def add_shelf_customer(self, runtime, *, checkout=True):
        runtime.add_customer(
            "c1",
            entry_point=GridPoint(0, 0),
            exit_point=GridPoint(0, 8),
            merchandise_fixture_ids=("shelf",),
            checkout_fixture_id="checkout" if checkout else None,
        )
        self.advance_until(runtime, "c1", CustomerState.AT_MERCHANDISE)

    def offers(self):
        return (
            MerchandiseOffer("bread-slot", 120, PurchaseFlow.CHECKOUT_REQUIRED),
            MerchandiseOffer("empty-slot", 90, PurchaseFlow.CHECKOUT_REQUIRED),
            MerchandiseOffer("drink-slot", 150, PurchaseFlow.SELF_SERVICE_CANDIDATE),
        )

    def test_context_exposes_only_in_stock_offers_at_current_fixture(self):
        runtime = self.make_runtime()
        self.add_shelf_customer(runtime)
        policy = RecordingPurchasePolicy()
        coordinator = CustomerPurchaseCoordinator(runtime, self.offers())

        result = coordinator.evaluate("c1", policy)

        self.assertIsNone(result.decision)
        self.assertEqual(runtime.customers.customer("c1").state, CustomerState.AT_MERCHANDISE)
        context = policy.contexts[-1]
        self.assertEqual(context.current_fixture_id, "shelf")
        self.assertEqual([offer.slot_id for offer in context.offers], ["bread-slot"])
        self.assertEqual(context.offers[0].product_id, "bread")
        self.assertEqual(context.offers[0].unit_sale_price_yen, 120)
        self.assertEqual(context.basket_line_count, 0)

    def test_buy_decision_uses_existing_inventory_and_customer_flow(self):
        runtime = self.make_runtime()
        self.add_shelf_customer(runtime)
        policy = RecordingPurchasePolicy(CustomerPurchaseDecision.buy("bread-slot", 2))
        coordinator = CustomerPurchaseCoordinator(runtime, self.offers())

        result = coordinator.evaluate("c1", policy)

        self.assertIsNotNone(result.pick_result)
        self.assertEqual(runtime.inventory.slot("bread-slot").units, 3)
        basket = runtime.purchases.basket("c1")
        self.assertEqual(len(basket.lines), 1)
        self.assertEqual(basket.lines[0].quantity, 2)
        self.assertEqual(basket.lines[0].unit_sale_price_yen, 120)
        self.assertEqual(
            runtime.customers.customer("c1").state,
            CustomerState.APPROACHING_CHECKOUT,
        )

    def test_explicit_skip_advances_without_inventory_or_basket_mutation(self):
        runtime = self.make_runtime()
        self.add_shelf_customer(runtime)
        policy = RecordingPurchasePolicy(CustomerPurchaseDecision.skip())
        coordinator = CustomerPurchaseCoordinator(runtime, self.offers())

        result = coordinator.evaluate("c1", policy)

        self.assertIsNone(result.pick_result)
        self.assertEqual(runtime.inventory.slot("bread-slot").units, 5)
        self.assertEqual(runtime.purchases.basket("c1").lines, [])
        session = runtime.customers.customer("c1")
        self.assertEqual(session.state, CustomerState.LEAVING)
        self.assertEqual(session.interacted_fixture_ids, ())

    def test_policy_cannot_select_offer_from_another_fixture(self):
        runtime = self.make_runtime()
        self.add_shelf_customer(runtime)
        policy = RecordingPurchasePolicy(CustomerPurchaseDecision.buy("drink-slot"))
        coordinator = CustomerPurchaseCoordinator(runtime, self.offers())

        with self.assertRaises(ValueError):
            coordinator.evaluate("c1", policy)

        self.assertEqual(runtime.inventory.slot("drink-slot").units, 3)
        self.assertEqual(runtime.inventory.slot("bread-slot").units, 5)
        self.assertEqual(runtime.purchases.basket("c1").lines, [])

    def test_policy_cannot_buy_more_than_current_stock(self):
        runtime = self.make_runtime()
        self.add_shelf_customer(runtime)
        policy = RecordingPurchasePolicy(CustomerPurchaseDecision.buy("bread-slot", 6))
        coordinator = CustomerPurchaseCoordinator(runtime, self.offers())

        with self.assertRaises(ValueError):
            coordinator.evaluate("c1", policy)

        self.assertEqual(runtime.inventory.slot("bread-slot").units, 5)
        self.assertEqual(runtime.purchases.basket("c1").lines, [])


if __name__ == "__main__":
    unittest.main()
