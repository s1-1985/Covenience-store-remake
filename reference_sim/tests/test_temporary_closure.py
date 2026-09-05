import unittest

from conveni_sim.operating_time import OperatingHours, SubdayClock
from conveni_sim.store_grid import StoreGrid
from conveni_sim.store_runtime import StoreRuntimeHarness


class TemporaryClosureTests(unittest.TestCase):
    def make_store(self, *, hour=23, minute=59, operating_hours=None):
        return StoreRuntimeHarness(
            StoreGrid(2, 2),
            initial_cash_yen=1_000,
            operating_hours=operating_hours,
            subday_clock=SubdayClock(hour, minute),
        )

    def test_temporary_closure_overrides_unknown_schedule(self):
        store = self.make_store(hour=12, minute=0)
        self.assertIsNone(store.store_open)
        store.set_temporary_closure(True)
        self.assertFalse(store.store_open)

    def test_temporary_closure_suppresses_labor_cost(self):
        store = self.make_store(
            hour=12,
            minute=0,
            operating_hours=OperatingHours.twenty_four_hours(),
        )
        store.set_temporary_closure(True)
        event = store.record_labor_cost_current_time(100, staff_id="s1")
        self.assertIsNone(event)
        self.assertEqual(store.cash.known_cash_yen, 1_000)

    def test_temporary_closure_at_midnight_sets_share_to_zero(self):
        store = self.make_store(operating_hours=OperatingHours.twenty_four_hours())
        store.customer_share.apply_share(58, source="pre-closure observation")
        store.set_temporary_closure(True)

        store.advance_game_minutes(1)

        self.assertEqual(store.customer_share.current_share_percent, 0)
        self.assertFalse(store.customer_share.recalculation_pending)
        snapshot = store.customer_share.history[-1]
        self.assertEqual(snapshot.share_percent, 0)
        self.assertIn("temporary closure", snapshot.source)

    def test_ordinary_scheduled_closed_midnight_does_not_force_zero(self):
        store = self.make_store(
            operating_hours=OperatingHours.from_hm(7, 0, 23, 0),
        )
        store.customer_share.apply_share(58, source="previous day")
        self.assertFalse(store.store_open)

        store.advance_game_minutes(1)

        self.assertEqual(store.customer_share.current_share_percent, 58)
        self.assertTrue(store.customer_share.recalculation_pending)

    def test_reopening_before_midnight_waits_for_date_change_refresh(self):
        store = self.make_store(operating_hours=OperatingHours.twenty_four_hours())
        store.customer_share.apply_share(0, source="closed previous day")
        store.set_temporary_closure(True)
        store.set_temporary_closure(False)

        self.assertEqual(store.customer_share.current_share_percent, 0)
        self.assertTrue(store.store_open)
        store.advance_game_minutes(1)
        self.assertTrue(store.customer_share.recalculation_pending)
        self.assertEqual(store.customer_share.current_share_percent, 0)


if __name__ == "__main__":
    unittest.main()
