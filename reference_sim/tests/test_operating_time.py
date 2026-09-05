import unittest

from conveni_sim.operating_time import MINUTES_PER_DAY, OperatingHours, SubdayClock


class SubdayClockTests(unittest.TestCase):
    def test_explicit_minute_advance_without_wall_clock_assumption(self):
        clock = SubdayClock(13, 16)
        result = clock.advance_minutes(8)
        self.assertEqual((clock.hour, clock.minute), (13, 24))
        self.assertEqual(result.days_crossed, 0)

    def test_midnight_crossing_is_reported(self):
        clock = SubdayClock(23, 55)
        result = clock.advance_minutes(10)
        self.assertEqual((clock.hour, clock.minute), (0, 5))
        self.assertEqual(result.days_crossed, 1)
        self.assertEqual(clock.elapsed_days, 1)

    def test_multiple_days_can_be_advanced_explicitly(self):
        clock = SubdayClock(1, 0)
        result = clock.advance_minutes(MINUTES_PER_DAY * 2 + 30)
        self.assertEqual((clock.hour, clock.minute), (1, 30))
        self.assertEqual(result.days_crossed, 2)

    def test_negative_advance_is_rejected(self):
        clock = SubdayClock()
        with self.assertRaises(ValueError):
            clock.advance_minutes(-1)


class OperatingHoursTests(unittest.TestCase):
    def test_normal_daytime_window(self):
        hours = OperatingHours.from_hm(9, 0, 17, 0)
        self.assertFalse(hours.is_open_at(8 * 60 + 59))
        self.assertTrue(hours.is_open_at(9 * 60))
        self.assertTrue(hours.is_open_at(16 * 60 + 59))
        self.assertFalse(hours.is_open_at(17 * 60))

    def test_overnight_window(self):
        hours = OperatingHours.from_hm(20, 0, 4, 0)
        self.assertTrue(hours.is_open_at(23 * 60))
        self.assertTrue(hours.is_open_at(3 * 60 + 59))
        self.assertFalse(hours.is_open_at(4 * 60))
        self.assertFalse(hours.is_open_at(12 * 60))

    def test_four_hour_midnight_window_is_representable(self):
        hours = OperatingHours.from_hm(0, 0, 4, 0)
        self.assertTrue(hours.is_open_at(0))
        self.assertTrue(hours.is_open_at(3 * 60 + 59))
        self.assertFalse(hours.is_open_at(4 * 60))

    def test_twenty_four_hour_operation_is_explicit(self):
        hours = OperatingHours.twenty_four_hours()
        for minute in (0, 1, 720, 1439):
            self.assertTrue(hours.is_open_at(minute))

    def test_equal_non_always_open_boundaries_are_empty(self):
        hours = OperatingHours.from_hm(0, 0, 0, 0)
        self.assertFalse(hours.is_open_at(0))
        self.assertFalse(hours.is_open_at(720))

    def test_clock_integration(self):
        hours = OperatingHours.from_hm(20, 0, 4, 0)
        clock = SubdayClock(3, 59)
        self.assertTrue(hours.is_open_clock(clock))
        clock.advance_minutes(1)
        self.assertFalse(hours.is_open_clock(clock))


if __name__ == "__main__":
    unittest.main()
