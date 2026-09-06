import unittest

from conveni_sim.economy import FinancialEventKind, StoreCashLedger
from conveni_sim.month_boundary import (
    MonthBoundaryBankruptcyPolicy,
    MonthBoundaryOutcome,
    MonthBoundaryTerminalGate,
)


class MonthBoundaryTerminalGateTests(unittest.TestCase):
    def test_negative_exact_cash_is_terminal_after_explicit_settlement(self):
        ledger = StoreCashLedger(697_211)
        ledger.record_cost(FinancialEventKind.OTHER, 818_571, note="observed month boundary delta")

        result = MonthBoundaryTerminalGate(ledger).evaluate()

        self.assertEqual(result.known_cash_yen, -121_360)
        self.assertTrue(result.cash_is_exact)
        self.assertEqual(result.outcome, MonthBoundaryOutcome.BANKRUPT)
        self.assertTrue(result.suppress_normal_month_start_presentation)

    def test_positive_exact_cash_continues(self):
        ledger = StoreCashLedger(1_000)
        ledger.record_cost(FinancialEventKind.OTHER, 250)

        result = MonthBoundaryTerminalGate(ledger).evaluate()

        self.assertEqual(result.outcome, MonthBoundaryOutcome.CONTINUE)
        self.assertFalse(result.suppress_normal_month_start_presentation)

    def test_zero_cash_stays_unknown_without_zero_rule(self):
        ledger = StoreCashLedger(1_000)
        ledger.record_cost(FinancialEventKind.OTHER, 1_000)

        result = MonthBoundaryTerminalGate(ledger).evaluate()

        self.assertEqual(result.known_cash_yen, 0)
        self.assertEqual(result.outcome, MonthBoundaryOutcome.UNDETERMINED)
        self.assertFalse(result.suppress_normal_month_start_presentation)

    def test_unknown_settlement_keeps_terminal_state_unknown(self):
        ledger = StoreCashLedger(1_000)
        ledger.record_cost(FinancialEventKind.OTHER, None)

        result = MonthBoundaryTerminalGate(ledger).evaluate()

        self.assertFalse(result.cash_is_exact)
        self.assertEqual(result.outcome, MonthBoundaryOutcome.UNDETERMINED)

    def test_future_zero_cash_rule_can_be_supplied_without_changing_gate(self):
        ledger = StoreCashLedger(0)
        policy = MonthBoundaryBankruptcyPolicy(bankrupt_when_zero=False)

        result = MonthBoundaryTerminalGate(ledger, policy=policy).evaluate()

        self.assertEqual(result.outcome, MonthBoundaryOutcome.CONTINUE)


if __name__ == "__main__":
    unittest.main()
