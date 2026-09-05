import unittest

from conveni_sim.customer_demand import (
    CustomerArrivalIntent,
    CustomerDemandCoordinator,
)
from conveni_sim.customer_share import CustomerShareInputs
from conveni_sim.operating_time import OperatingHours, SubdayClock
from conveni_sim.store_grid import GridPoint, StoreGrid
from conveni_sim.store_runtime import CustomerAdmissionStatus, StoreRuntimeHarness


class RecordingDemandPolicy:
    def __init__(self, intents=()):
        self.intents = tuple(intents)
        self.contexts = []

    def arrivals_for(self, context):
        self.contexts.append(context)
        return self.intents


class CustomerDemandPolicyTests(unittest.TestCase):
    def make_runtime(self, *, hours=None, hour=12, minute=0):
        return StoreRuntimeHarness(
            StoreGrid(3, 3),
            initial_cash_yen=1000,
            operating_hours=hours,
            subday_clock=SubdayClock(hour, minute),
        )

    def intent(self, customer_id="c1"):
        return CustomerArrivalIntent(
            customer_id,
            entry_point=GridPoint(0, 0),
            exit_point=GridPoint(0, 2),
        )

    def test_context_exposes_known_runtime_inputs_without_computing_demand(self):
        runtime = self.make_runtime(hours=OperatingHours.twenty_four_hours(), hour=13, minute=5)
        runtime.customer_share.set_inputs(
            CustomerShareInputs(
                popularity=72,
                weather="rain",
                nearby_population=2400,
            )
        )
        runtime.customer_share.apply_share(43, source="test observation")
        policy = RecordingDemandPolicy()

        result = CustomerDemandCoordinator(runtime, policy).evaluate()

        self.assertEqual(result.intents, ())
        self.assertEqual(result.admissions, ())
        context = policy.contexts[-1]
        self.assertEqual(context.minute_of_day, 13 * 60 + 5)
        self.assertEqual(context.customer_share_percent, 43)
        self.assertEqual(context.share_inputs.popularity, 72)
        self.assertEqual(context.share_inputs.weather, "rain")
        self.assertTrue(context.store_open)

    def test_policy_intent_is_admitted_only_through_open_store_gate(self):
        runtime = self.make_runtime(hours=OperatingHours.twenty_four_hours())
        policy = RecordingDemandPolicy((self.intent(),))

        result = CustomerDemandCoordinator(runtime, policy).evaluate()

        self.assertEqual(len(result.admissions), 1)
        self.assertEqual(result.admissions[0].status, CustomerAdmissionStatus.ADMITTED)
        self.assertEqual(runtime.customers.customer("c1").id, "c1")
        self.assertEqual(runtime.purchases.basket("c1").customer_id, "c1")

    def test_closed_store_rejects_policy_intent_without_creating_customer(self):
        runtime = self.make_runtime(hours=OperatingHours.from_hm(7, 0, 23, 0), hour=6)
        policy = RecordingDemandPolicy((self.intent(),))

        result = CustomerDemandCoordinator(runtime, policy).evaluate()

        self.assertEqual(result.admissions[0].status, CustomerAdmissionStatus.STORE_CLOSED)
        with self.assertRaises(KeyError):
            runtime.customers.customer("c1")
        with self.assertRaises(KeyError):
            runtime.purchases.basket("c1")

    def test_unknown_opening_state_is_not_silently_treated_as_open(self):
        runtime = self.make_runtime(hours=None)
        policy = RecordingDemandPolicy((self.intent(),))

        result = CustomerDemandCoordinator(runtime, policy).evaluate()

        self.assertIsNone(result.context.store_open)
        self.assertEqual(
            result.admissions[0].status,
            CustomerAdmissionStatus.OPEN_STATE_UNKNOWN,
        )

    def test_temporary_closure_overrides_twenty_four_hour_schedule(self):
        runtime = self.make_runtime(hours=OperatingHours.twenty_four_hours())
        runtime.set_temporary_closure(True)
        policy = RecordingDemandPolicy((self.intent(),))

        result = CustomerDemandCoordinator(runtime, policy).evaluate()

        self.assertFalse(result.context.store_open)
        self.assertEqual(result.admissions[0].status, CustomerAdmissionStatus.STORE_CLOSED)


if __name__ == "__main__":
    unittest.main()
