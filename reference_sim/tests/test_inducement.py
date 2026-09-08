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
            displayed_site_cost_yen=6_800_000,
        )
        self.assertGreater(quote.displayed_site_cost_yen, ledger.known_cash_yen)

        refund = session.cancel()
        self.assertEqual(session.state, InducementPlacementState.CANCELLED)
        self.assertEqual(refund.direction, CashDirection.CREDIT)
        self.assertEqual(refund.amount_yen, 5_400_000)
        self.assertEqual(ledger.known_cash_yen, 7_330_572)

    def test_v03_pool_confirmation_debits_site_quote_in_addition_to_aid(self):
        ledger = StoreCashLedger(7_331_292)
        session = InducementPlacementSession(
            facility_id="pool",
            aid_yen=1_800_000,
            ledger=ledger,
        )
        self.assertEqual(ledger.known_cash_yen, 5_531_292)
        session.record_quote("tile-a", placeable=True, displayed_site_cost_yen=4_200_000)
        session.record_quote("tile-b", placeable=True, displayed_site_cost_yen=3_800_000)
        event = session.confirm()
        self.assertEqual(ledger.known_cash_yen, 1_731_292)
        self.assertEqual(event.amount_yen, 3_800_000)
        self.assertEqual(event.direction, CashDirection.DEBIT)
        self.assertEqual(event.kind, FinancialEventKind.INDUCEMENT)
        self.assertIs(session.confirmation_event, event)
        self.assertEqual(session.state, InducementPlacementState.CONFIRMED)
        self.assertIsNone(session.refund_event)

    def test_v01_police_box_replays_two_stage_payment(self):
        ledger = StoreCashLedger(80_600_145)
        session = InducementPlacementSession(
            facility_id="police_box", aid_yen=400_000, ledger=ledger,
        )
        self.assertEqual(ledger.known_cash_yen, 80_200_145)
        session.record_quote("tile-a", placeable=True, displayed_site_cost_yen=4_000_000)
        session.record_quote("tile-b", placeable=True, displayed_site_cost_yen=2_000_000)
        session.confirm()
        self.assertEqual(ledger.known_cash_yen, 78_200_145)
        for operation in (
            session.confirm, session.cancel,
            lambda: session.record_quote("tile-c", placeable=True),
        ):
            with self.assertRaises(ValueError):
                operation()
        self.assertEqual(ledger.known_cash_yen, 78_200_145)

    def test_invalid_current_quote_cannot_debit_or_reuse_older_quote(self):
        ledger = StoreCashLedger(10_000_000)
        session = InducementPlacementSession(
            facility_id="police_box", aid_yen=400_000, ledger=ledger,
        )
        with self.assertRaises(ValueError):
            session.confirm()
        session.record_quote("valid", placeable=True, displayed_site_cost_yen=2_000_000)
        for placeable, amount in ((False, 2_000_000), (True, None)):
            session.record_quote("current", placeable=placeable, displayed_site_cost_yen=amount)
            with self.assertRaises(ValueError):
                session.confirm()
            self.assertEqual(ledger.known_cash_yen, 9_600_000)
            self.assertEqual(session.state, InducementPlacementState.ACTIVE)
            self.assertIsNone(session.confirmation_event)
        session.cancel()
        self.assertEqual(ledger.known_cash_yen, 10_000_000)

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
            session.confirm()
        with self.assertRaises(ValueError):
            session.record_quote("tile-a", placeable=True)


if __name__ == "__main__":
    unittest.main()
