import unittest

from conveni_sim.economy import StoreCashLedger
from conveni_sim.inventory import OutOfStockError, StoreInventoryRuntime
from conveni_sim.purchases import StorePurchaseRuntime


class PurchaseRuntimeTests(unittest.TestCase):
    def make_runtime(self):
        inventory = StoreInventoryRuntime()
        inventory.add_slot(
            "bread-slot",
            fixture_id="shelf-1",
            product_id="bread",
            capacity_units=10,
            initial_units=5,
        )
        inventory.add_slot(
            "drink-slot",
            fixture_id="cooler-1",
            product_id="drink",
            capacity_units=10,
            initial_units=5,
        )
        cash = StoreCashLedger(1_000)
        return inventory, cash, StorePurchaseRuntime(inventory, cash)

    def test_pick_decrements_inventory_and_adds_basket_line(self):
        inventory, _cash, purchases = self.make_runtime()
        purchases.open_basket("c1")

        result = purchases.pick_from_inventory(
            "c1",
            "bread-slot",
            quantity=2,
            unit_sale_price_yen=120,
        )

        self.assertEqual(inventory.slot("bread-slot").units, 3)
        self.assertEqual(result.purchase_line.quantity, 2)
        self.assertEqual(result.purchase_line.line_total_yen, 240)
        self.assertEqual(purchases.basket("c1").known_subtotal_yen, 240)

    def test_out_of_stock_propagates_without_creating_line(self):
        inventory, _cash, purchases = self.make_runtime()
        purchases.open_basket("c1")

        with self.assertRaises(OutOfStockError):
            purchases.pick_from_inventory(
                "c1",
                "bread-slot",
                quantity=6,
                unit_sale_price_yen=120,
            )

        self.assertEqual(purchases.basket("c1").lines, [])
        self.assertEqual(inventory.slot("bread-slot").units, 5)

    def test_known_price_basket_settlement_credits_cash(self):
        _inventory, cash, purchases = self.make_runtime()
        purchases.open_basket("c1")
        purchases.pick_from_inventory("c1", "bread-slot", quantity=2, unit_sale_price_yen=120)
        purchases.pick_from_inventory("c1", "drink-slot", quantity=1, unit_sale_price_yen=150)

        settlement = purchases.settle("c1", source_id="checkout-1")

        self.assertEqual(settlement.exact_total_yen, 390)
        self.assertEqual(cash.known_cash_yen, 1_390)
        self.assertTrue(cash.cash_is_exact)
        self.assertEqual(len(settlement.financial_events), 1)

    def test_unknown_price_line_preserves_known_subtotal_and_marks_cash_inexact(self):
        _inventory, cash, purchases = self.make_runtime()
        purchases.open_basket("c1")
        purchases.pick_from_inventory("c1", "bread-slot", quantity=1, unit_sale_price_yen=120)
        purchases.pick_from_inventory("c1", "drink-slot", quantity=1, unit_sale_price_yen=None)

        settlement = purchases.settle("c1")

        self.assertEqual(settlement.known_revenue_yen, 120)
        self.assertEqual(settlement.unknown_price_line_count, 1)
        self.assertIsNone(settlement.exact_total_yen)
        self.assertEqual(cash.known_cash_yen, 1_120)
        self.assertFalse(cash.cash_is_exact)
        self.assertEqual(len(settlement.financial_events), 2)
        self.assertEqual(settlement.financial_events[0].amount_yen, 120)
        self.assertIsNone(settlement.financial_events[1].amount_yen)

    def test_all_unknown_prices_create_unknown_sale_without_fake_zero_credit(self):
        _inventory, cash, purchases = self.make_runtime()
        purchases.open_basket("c1")
        purchases.pick_from_inventory("c1", "bread-slot", quantity=1, unit_sale_price_yen=None)

        settlement = purchases.settle("c1")

        self.assertEqual(settlement.known_revenue_yen, 0)
        self.assertEqual(len(settlement.financial_events), 1)
        self.assertIsNone(settlement.financial_events[0].amount_yen)
        self.assertEqual(cash.known_cash_yen, 1_000)
        self.assertFalse(cash.cash_is_exact)

    def test_cannot_settle_empty_basket(self):
        _inventory, _cash, purchases = self.make_runtime()
        purchases.open_basket("c1")
        with self.assertRaises(ValueError):
            purchases.settle("c1")

    def test_cannot_settle_twice_or_add_after_settlement(self):
        _inventory, _cash, purchases = self.make_runtime()
        purchases.open_basket("c1")
        purchases.pick_from_inventory("c1", "bread-slot", quantity=1, unit_sale_price_yen=120)
        purchases.settle("c1")

        with self.assertRaises(ValueError):
            purchases.settle("c1")
        with self.assertRaises(ValueError):
            purchases.pick_from_inventory(
                "c1",
                "drink-slot",
                quantity=1,
                unit_sale_price_yen=150,
            )

    def test_settlement_is_explicit_and_not_triggered_by_item_pick(self):
        _inventory, cash, purchases = self.make_runtime()
        purchases.open_basket("c1")
        purchases.pick_from_inventory("c1", "bread-slot", quantity=1, unit_sale_price_yen=120)

        self.assertEqual(cash.known_cash_yen, 1_000)
        self.assertEqual(purchases.settlements, ())


if __name__ == "__main__":
    unittest.main()
