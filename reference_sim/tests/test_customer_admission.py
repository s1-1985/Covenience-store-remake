import unittest

from conveni_sim.operating_time import OperatingHours, SubdayClock
from conveni_sim.store_grid import GridPoint, StoreGrid
from conveni_sim.store_runtime import (
    CustomerAdmissionStatus,
    StoreRuntimeHarness,
)


class CustomerAdmissionGateTests(unittest.TestCase):
    def make_store(self, *, operating_hours=None, clock=None):
        return StoreRuntimeHarness(
            StoreGrid(3, 3),
            initial_cash_yen=1_000,
            operating_hours=operating_hours,
            subday_clock=clock if clock is not None else SubdayClock(),
        )

    def admit(self, store, customer_id="c1"):
        return store.admit_customer(
            customer_id,
            entry_point=GridPoint(0, 0),
            exit_point=GridPoint(2, 2),
        )

    def test_twenty_four_hour_store_admits_customer(self):
        store = self.make_store(operating_hours=OperatingHours.twenty_four_hours())

        result = self.admit(store)

        self.assertTrue(result.admitted)
        self.assertEqual(result.status, CustomerAdmissionStatus.ADMITTED)
        self.assertEqual(result.session.id, "c1")
        self.assertEqual(store.customers.customer("c1").id, "c1")

    def test_scheduled_closed_time_rejects_customer(self):
        store = self.make_store(
            operating_hours=OperatingHours.from_hm(7, 0, 23, 0),
            clock=SubdayClock(6, 59),
        )

        result = self.admit(store)

        self.assertFalse(result.admitted)
        self.assertEqual(result.status, CustomerAdmissionStatus.STORE_CLOSED)
        with self.assertRaises(KeyError):
            store.customers.customer("c1")

    def test_opening_boundary_allows_customer(self):
        store = self.make_store(
            operating_hours=OperatingHours.from_hm(7, 0, 23, 0),
            clock=SubdayClock(6, 59),
        )
        self.assertEqual(self.admit(store, "before").status, CustomerAdmissionStatus.STORE_CLOSED)

        store.advance_game_minutes(1)
        result = self.admit(store, "at-open")

        self.assertEqual(result.status, CustomerAdmissionStatus.ADMITTED)

    def test_temporary_closure_blocks_even_twenty_four_hour_store(self):
        store = self.make_store(operating_hours=OperatingHours.twenty_four_hours())
        store.set_temporary_closure(True)

        result = self.admit(store)

        self.assertEqual(result.status, CustomerAdmissionStatus.STORE_CLOSED)

    def test_unknown_opening_state_is_not_silently_admitted(self):
        store = self.make_store(operating_hours=None)

        result = self.admit(store)

        self.assertEqual(result.status, CustomerAdmissionStatus.OPEN_STATE_UNKNOWN)
        self.assertIsNone(result.session)
        with self.assertRaises(KeyError):
            store.customers.customer("c1")


if __name__ == "__main__":
    unittest.main()
