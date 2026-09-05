import unittest

from conveni_sim.operating_time import OperatingHours, SubdayClock
from conveni_sim.store_grid import StoreGrid
from conveni_sim.store_runtime import StoreRuntimeHarness


class StoreOperatingTimeCompositionTests(unittest.TestCase):
    def make_runtime(self, *, operating_hours=None, hour=0, minute=0):
        return StoreRuntimeHarness(
            StoreGrid(2, 2),
            initial_cash_yen=1_000,
            operating_hours=operating_hours,
            subday_clock=SubdayClock(hour, minute),
        )

    def test_unknown_schedule_keeps_open_state_unknown(self):
        runtime = self.make_runtime(hour=12)
        self.assertIsNone(runtime.store_open)

    def test_known_schedule_tracks_explicit_game_time(self):
        runtime = self.make_runtime(
            operating_hours=OperatingHours.from_hm(9, 0, 17, 0),
            hour=8,
            minute=59,
        )
        self.assertFalse(runtime.store_open)
        runtime.advance_game_minutes(1)
        self.assertTrue(runtime.store_open)
        runtime.advance_game_minutes(8 * 60)
        self.assertFalse(runtime.store_open)

    def test_overnight_schedule_survives_midnight(self):
        runtime = self.make_runtime(
            operating_hours=OperatingHours.from_hm(20, 0, 4, 0),
            hour=23,
            minute=59,
        )
        self.assertTrue(runtime.store_open)
        result = runtime.advance_game_minutes(2)
        self.assertEqual(result.days_crossed, 1)
        self.assertTrue(runtime.store_open)

    def test_closed_time_suppresses_labor_cost(self):
        runtime = self.make_runtime(
            operating_hours=OperatingHours.from_hm(9, 0, 17, 0),
            hour=8,
            minute=0,
        )
        event = runtime.record_labor_cost_current_time(100, staff_id="staff-1")
        self.assertIsNone(event)
        self.assertEqual(runtime.cash.known_cash_yen, 1_000)

    def test_open_time_records_labor_cost(self):
        runtime = self.make_runtime(
            operating_hours=OperatingHours.from_hm(9, 0, 17, 0),
            hour=9,
            minute=0,
        )
        event = runtime.record_labor_cost_current_time(100, staff_id="staff-1")
        self.assertIsNotNone(event)
        self.assertEqual(event.amount_yen, 100)
        self.assertEqual(runtime.cash.known_cash_yen, 900)

    def test_unknown_schedule_cannot_silently_choose_labor_behavior(self):
        runtime = self.make_runtime(hour=9)
        with self.assertRaises(ValueError):
            runtime.record_labor_cost_current_time(100, staff_id="staff-1")
        self.assertEqual(runtime.cash.known_cash_yen, 1_000)

    def test_schedule_can_be_replaced_when_research_value_arrives(self):
        runtime = self.make_runtime(hour=1)
        self.assertIsNone(runtime.store_open)
        runtime.set_operating_hours(OperatingHours.from_hm(0, 0, 4, 0))
        self.assertTrue(runtime.store_open)
        runtime.set_operating_hours(None)
        self.assertIsNone(runtime.store_open)


if __name__ == "__main__":
    unittest.main()
