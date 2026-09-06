import unittest

from conveni_sim.economy import CashDirection, FinancialEventKind, StoreCashLedger
from conveni_sim.inducement import InducementPlacementSession, InducementPlacementState


class InducementPlacementSessionTests(unittest.TestCase):
    def test_company_aid_is_reserved_and_fully_returned_on_cancel(self):
        ledger = StoreCashLedger(7_330_572)
        session = InducementPlacementSession(
            facility_id="company",
            aid_yen=5_400_000,
            ledger=ledger,
        )

        self.assertEqual(ledger.known_cash_yen, 1_930_572)
        self.assertEqual(session.aid_debit_event.kind, FinancialEventKind.INDUCEMENT)
        self.assertEqual(session.aid_debit_event.direction, CashDirection.DEBIT)

        session.record_quote("tile-a", placeable=False)
        quote = session.record_quote(
            "tile-b",
            placeable=True,
            displayed_total_yen=6_800_000,
        )
        self.assertGreater(quote.displayed_total_yen, ledger.known_cash_yen)

        refund = session.cancel()
        self.assertEqual(session.state, InducementPlacementState.CANCELLED)
        self.assertEqual(refund.direction, CashDirection.CREDIT)
        self.assertEqual(refund.amount_yen, 5_400_000)
        self.assertEqual(ledger.known_cash_yen, 7_330_572)

    def test_pool_repeats_the_same_reserve_and_refund_behavior(self):
        ledger = StoreCashLedger(7_331_292)
        session = InducementPlacementSession(
            facility_id="pool",
            aid_yen=1_800_000,
            ledger=ledger,
        )
        self.assertEqual(ledger.known_cash_yen, 5_531_292)
        session.record_quote("tile-a", placeable=True, displayed_total_yen=4_200_000)
        session.record_quote("tile-b", placeable=True, displayed_total_yen=7_300_000)
        session.cancel()
        self.assertEqual(ledger.known_cash_yen, 7_331_292)

    def test_cancel_is_one_shot_and_quotes_stop_after_cancel(self):
        session = InducementPlacementSession(
            facility_id="pool",
            aid_yen=1_800_000,
            ledger=StoreCashLedger(2_000_000),
        )
        session.cancel()
        with self.assertRaises(ValueError):
            session.cancel()
        with self.assertRaises(ValueError):
            session.record_quote("tile-a", placeable=True)


if __name__ == "__main__":
    unittest.main()
