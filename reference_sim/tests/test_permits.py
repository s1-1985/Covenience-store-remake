import unittest

from conveni_sim.economy import FinancialEventKind, StoreCashLedger
from conveni_sim.models import EvidenceLevel, EvidenceValue, PermitDefinition
from conveni_sim.permits import (
    PermitApplicationOutcome,
    PermitApplicationTrigger,
    PermitEligibility,
    StorePermitRuntime,
)


def permit_definition(permit_id, fee_yen=None):
    fee = (
        None
        if fee_yen is None
        else EvidenceValue(
            fee_yen,
            EvidenceLevel.CONFIRMED_VISUAL,
            "test fixture",
        )
    )
    return PermitDefinition(
        id=permit_id,
        fee_yen=fee,
        exclusion_distance_tiles=None,
        eligibility_is_independent=EvidenceValue(
            True,
            EvidenceLevel.CONFIRMED_COMMUNITY,
            "first-title research",
        ),
    )


class StorePermitRuntimeTests(unittest.TestCase):
    def make_runtime(self):
        cash = StoreCashLedger(10000)
        permits = StorePermitRuntime(
            (
                permit_definition("tobacco", 1000),
                permit_definition("alcohol"),
                permit_definition("medicine", 2500),
            ),
            cash,
        )
        return permits, cash

    def test_eligible_remodel_application_acquires_one_independent_permit(self):
        permits, cash = self.make_runtime()

        result = permits.apply(
            "tobacco",
            trigger=PermitApplicationTrigger.REMODEL,
            eligibility=PermitEligibility.ELIGIBLE,
        )

        self.assertTrue(result.acquired)
        self.assertEqual(result.fee_yen, 1000)
        self.assertEqual(permits.owned_permits, frozenset({"tobacco"}))
        self.assertFalse(permits.owns("alcohol"))
        self.assertFalse(permits.owns("medicine"))
        self.assertEqual(cash.known_cash_yen, 9000)
        self.assertEqual(result.financial_event.kind, FinancialEventKind.PERMIT)

    def test_unknown_fee_is_preserved_as_unknown_cash_effect(self):
        permits, cash = self.make_runtime()

        result = permits.apply(
            "alcohol",
            trigger=PermitApplicationTrigger.REMODEL,
            eligibility=PermitEligibility.ELIGIBLE,
        )

        self.assertTrue(result.acquired)
        self.assertIsNone(result.fee_yen)
        self.assertIsNone(result.financial_event.amount_yen)
        self.assertFalse(cash.cash_is_exact)
        self.assertEqual(cash.known_cash_yen, 10000)

    def test_explicit_observed_fee_can_fill_unknown_master_value(self):
        permits, cash = self.make_runtime()

        result = permits.apply(
            "alcohol",
            trigger=PermitApplicationTrigger.REMODEL,
            eligibility=PermitEligibility.ELIGIBLE,
            fee_yen_override=1800,
        )

        self.assertEqual(result.fee_yen, 1800)
        self.assertEqual(cash.known_cash_yen, 8200)
        self.assertTrue(cash.cash_is_exact)

    def test_ineligible_permit_does_not_mutate_owned_state_or_cash(self):
        permits, cash = self.make_runtime()

        result = permits.apply(
            "medicine",
            trigger=PermitApplicationTrigger.REMODEL,
            eligibility=PermitEligibility.INELIGIBLE,
        )

        self.assertEqual(result.outcome, PermitApplicationOutcome.INELIGIBLE)
        self.assertFalse(permits.owns("medicine"))
        self.assertEqual(cash.events, ())

    def test_unknown_eligibility_remains_unresolved(self):
        permits, cash = self.make_runtime()

        result = permits.apply(
            "medicine",
            trigger=PermitApplicationTrigger.REMODEL,
            eligibility=PermitEligibility.UNKNOWN,
        )

        self.assertEqual(
            result.outcome,
            PermitApplicationOutcome.ELIGIBILITY_UNKNOWN,
        )
        self.assertFalse(permits.owns("medicine"))
        self.assertEqual(cash.events, ())

    def test_new_store_trigger_is_not_silently_enabled(self):
        permits, cash = self.make_runtime()

        result = permits.apply(
            "tobacco",
            trigger=PermitApplicationTrigger.NEW_STORE,
            eligibility=PermitEligibility.ELIGIBLE,
        )

        self.assertEqual(
            result.outcome,
            PermitApplicationOutcome.TRIGGER_UNCONFIRMED,
        )
        self.assertFalse(permits.owns("tobacco"))
        self.assertEqual(cash.events, ())

    def test_reapplying_owned_permit_does_not_charge_twice(self):
        permits, cash = self.make_runtime()
        permits.apply(
            "tobacco",
            trigger=PermitApplicationTrigger.REMODEL,
            eligibility=PermitEligibility.ELIGIBLE,
        )

        result = permits.apply(
            "tobacco",
            trigger=PermitApplicationTrigger.REMODEL,
            eligibility=PermitEligibility.ELIGIBLE,
        )

        self.assertEqual(result.outcome, PermitApplicationOutcome.ALREADY_OWNED)
        self.assertEqual(len(cash.events), 1)
        self.assertEqual(cash.known_cash_yen, 9000)


if __name__ == "__main__":
    unittest.main()
