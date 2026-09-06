import unittest

from conveni_sim.economy import (
    BankruptcyPolicy,
    CashDirection,
    DayEndOutcome,
    FinancialEventKind,
    StoreCashLedger,
)
from conveni_sim.inventory import StoreInventoryRuntime


class EconomyTests(unittest.TestCase):
    def test_known_sale_and_cost_update_exact_cash(self):
        ledger = StoreCashLedger(1_000)
        ledger.record_sale(500, source_id="checkout-1")
        ledger.record_cost(FinancialEventKind.PROMOTION, 200)

        self.assertEqual(ledger.known_cash_yen, 1_300)
        self.assertTrue(ledger.cash_is_exact)
        self.assertEqual(ledger.events[0].direction, CashDirection.CREDIT)
        self.assertEqual(ledger.events[1].direction, CashDirection.DEBIT)

    def test_unknown_cash_effect_is_not_treated_as_zero_exact_balance(self):
        ledger = StoreCashLedger(
            1_000,
            bankruptcy_policy=BankruptcyPolicy(check_negative_cash_at_end_of_day=True),
        )
        ledger.record_cost(FinancialEventKind.OTHER, None, note="unrecovered source value")

        self.assertEqual(ledger.known_cash_yen, 1_000)
        self.assertFalse(ledger.cash_is_exact)
        result = ledger.close_day()
        self.assertEqual(result.outcome, DayEndOutcome.UNDETERMINED)
        self.assertEqual(result.summary.unknown_debit_events, 1)

    def test_known_inventory_replenishment_can_feed_procurement_ledger(self):
        inventory = StoreInventoryRuntime()
        inventory.add_slot(
            "slot-1",
            fixture_id="shelf-1",
            product_id="bread",
            capacity_units=10,
            unit_procurement_cost_yen=80,
        )
        mutation = inventory.replenish("slot-1", 3)

        ledger = StoreCashLedger(10_000)
        event = ledger.record_procurement_mutation(mutation)

        self.assertEqual(event.kind, FinancialEventKind.PROCUREMENT)
        self.assertEqual(event.amount_yen, 240)
        self.assertEqual(ledger.known_cash_yen, 9_760)

    def test_unknown_procurement_cost_stays_unknown_in_cash_ledger(self):
        inventory = StoreInventoryRuntime()
        inventory.add_slot(
            "slot-1",
            fixture_id="shelf-1",
            product_id="bread",
            capacity_units=10,
        )
        mutation = inventory.replenish("slot-1", 3)

        ledger = StoreCashLedger(10_000)
        event = ledger.record_procurement_mutation(mutation)

        self.assertIsNone(event.amount_yen)
        self.assertFalse(ledger.cash_is_exact)
        self.assertEqual(ledger.known_cash_yen, 10_000)

    def test_closed_hours_do_not_record_labor_cost(self):
        ledger = StoreCashLedger(10_000)
        event = ledger.record_labor_cost_if_open(500, store_open=False, staff_id="staff-1")

        self.assertIsNone(event)
        self.assertEqual(ledger.events, ())
        self.assertEqual(ledger.known_cash_yen, 10_000)

    def test_open_hours_can_record_labor_cost(self):
        ledger = StoreCashLedger(10_000)
        event = ledger.record_labor_cost_if_open(500, store_open=True, staff_id="staff-1")

        self.assertIsNotNone(event)
        self.assertEqual(event.kind, FinancialEventKind.LABOR)
        self.assertEqual(ledger.known_cash_yen, 9_500)

    def test_closed_hours_suppress_explicit_operating_maintenance_cost(self):
        ledger = StoreCashLedger(10_000)
        event = ledger.record_operating_cost_if_open(
            FinancialEventKind.FIXTURE_MAINTENANCE,
            700,
            store_open=False,
            source_id="fixture-1",
        )

        self.assertIsNone(event)
        self.assertEqual(ledger.events, ())
        self.assertEqual(ledger.known_cash_yen, 10_000)

    def test_open_hours_can_record_explicit_operating_maintenance_cost(self):
        ledger = StoreCashLedger(10_000)
        event = ledger.record_operating_cost_if_open(
            FinancialEventKind.FIXTURE_MAINTENANCE,
            None,
            store_open=True,
            source_id="fixture-1",
            note="rate still unknown",
        )

        self.assertIsNotNone(event)
        self.assertEqual(event.kind, FinancialEventKind.FIXTURE_MAINTENANCE)
        self.assertIsNone(event.amount_yen)
        self.assertFalse(ledger.cash_is_exact)

    def test_procurement_cannot_be_misclassified_as_open_hours_operating_cost(self):
        ledger = StoreCashLedger(10_000)

        with self.assertRaises(ValueError):
            ledger.record_operating_cost_if_open(
                FinancialEventKind.PROCUREMENT,
                300,
                store_open=False,
            )

    def test_closed_hours_restock_procurement_remains_chargeable(self):
        inventory = StoreInventoryRuntime()
        inventory.add_slot(
            "slot-1",
            fixture_id="shelf-1",
            product_id="bread",
            capacity_units=10,
            unit_procurement_cost_yen=80,
        )
        mutation = inventory.replenish("slot-1", 3)
        ledger = StoreCashLedger(10_000)

        event = ledger.record_procurement_mutation(mutation)

        self.assertEqual(event.kind, FinancialEventKind.PROCUREMENT)
        self.assertEqual(event.amount_yen, 240)
        self.assertEqual(ledger.known_cash_yen, 9_760)

    def test_shared_default_does_not_assume_ss_bankruptcy_timing(self):
        ledger = StoreCashLedger(100)
        ledger.record_cost(FinancialEventKind.OTHER, 200)

        result = ledger.close_day()
        self.assertEqual(result.summary.known_cash_yen, -100)
        self.assertEqual(result.outcome, DayEndOutcome.NOT_EVALUATED)

    def test_ss_compatible_policy_bankrupts_negative_exact_cash_at_day_end(self):
        ledger = StoreCashLedger(
            100,
            bankruptcy_policy=BankruptcyPolicy(check_negative_cash_at_end_of_day=True),
        )
        ledger.record_cost(FinancialEventKind.OTHER, 200)

        result = ledger.close_day()
        self.assertEqual(result.outcome, DayEndOutcome.BANKRUPT)

    def test_ss_compatible_policy_keeps_zero_cash_solvent(self):
        ledger = StoreCashLedger(
            100,
            bankruptcy_policy=BankruptcyPolicy(check_negative_cash_at_end_of_day=True),
        )
        ledger.record_cost(FinancialEventKind.OTHER, 100)

        result = ledger.close_day()
        self.assertEqual(result.outcome, DayEndOutcome.SOLVENT)

    def test_day_summary_resets_event_window_but_cash_remains_cumulative(self):
        ledger = StoreCashLedger(1_000)
        ledger.record_sale(100)
        first = ledger.close_day()
        self.assertEqual(first.summary.known_credits_yen, 100)
        self.assertEqual(first.summary.known_cash_yen, 1_100)

        ledger.record_cost(FinancialEventKind.OTHER, 50)
        second = ledger.close_day()
        self.assertEqual(second.summary.known_credits_yen, 0)
        self.assertEqual(second.summary.known_debits_yen, 50)
        self.assertEqual(second.summary.known_cash_yen, 1_050)


if __name__ == "__main__":
    unittest.main()
