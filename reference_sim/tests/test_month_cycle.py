import unittest

from conveni_sim.clock import RepresentativeDayType, SimulationClock
from conveni_sim.economy import DayEndOutcome, DayEndResult, DaySummary
from conveni_sim.month_cycle import RepresentativeMonthRecorder


class RepresentativeMonthRecorderTests(unittest.TestCase):
    def make_day_end(self, marker: int) -> DayEndResult:
        return DayEndResult(
            outcome=DayEndOutcome.NOT_EVALUATED,
            summary=DaySummary(
                known_credits_yen=marker,
                known_debits_yen=0,
                unknown_credit_events=0,
                unknown_debit_events=0,
                known_cash_yen=10_000 + marker,
                cash_is_exact=True,
            ),
        )

    def test_month_boundary_returns_raw_day1_to_day4_sample(self):
        recorder = RepresentativeMonthRecorder(SimulationClock(year=1, month=6, day=1))
        sample = None
        for marker in (101, 202, 303, 404):
            sample = recorder.close_representative_day(self.make_day_end(marker))

        self.assertIsNotNone(sample)
        assert sample is not None
        self.assertEqual((sample.year, sample.month), (1, 6))
        self.assertEqual(sample.representative_days, (1, 2, 3, 4))
        self.assertTrue(sample.complete_four_day_sample)
        self.assertEqual(
            tuple(record.day_type for record in sample.records),
            (
                RepresentativeDayType.WEEKDAY,
                RepresentativeDayType.WEEKDAY,
                RepresentativeDayType.WEEKDAY,
                RepresentativeDayType.HOLIDAY,
            ),
        )
        self.assertEqual(
            tuple(record.day_end.summary.known_credits_yen for record in sample.records),
            (101, 202, 303, 404),
        )
        self.assertEqual((recorder.clock.year, recorder.clock.month, recorder.clock.day), (1, 7, 1))
        self.assertEqual(recorder.current_records, ())

    def test_no_month_sample_is_returned_before_day_four(self):
        recorder = RepresentativeMonthRecorder()

        self.assertIsNone(recorder.close_representative_day(self.make_day_end(1)))
        self.assertIsNone(recorder.close_representative_day(self.make_day_end(2)))
        self.assertIsNone(recorder.close_representative_day(self.make_day_end(3)))
        self.assertEqual(tuple(record.day for record in recorder.current_records), (1, 2, 3))

    def test_december_boundary_rolls_year_without_month_formula(self):
        recorder = RepresentativeMonthRecorder(SimulationClock(year=2, month=12, day=1))
        sample = None
        for marker in range(4):
            sample = recorder.close_representative_day(self.make_day_end(marker))

        assert sample is not None
        self.assertEqual(
            (
                sample.boundary.previous_year,
                sample.boundary.previous_month,
                sample.boundary.next_year,
                sample.boundary.next_month,
            ),
            (2, 12, 3, 1),
        )
        self.assertEqual((recorder.clock.year, recorder.clock.month, recorder.clock.day), (3, 1, 1))

    def test_midmonth_start_is_marked_incomplete_instead_of_inventing_missing_days(self):
        recorder = RepresentativeMonthRecorder(SimulationClock(year=1, month=3, day=3))
        recorder.close_representative_day(self.make_day_end(3))
        sample = recorder.close_representative_day(self.make_day_end(4))

        assert sample is not None
        self.assertEqual(sample.representative_days, (3, 4))
        self.assertFalse(sample.complete_four_day_sample)
        self.assertEqual(len(sample.weekday_records), 1)
        self.assertEqual(len(sample.holiday_records), 1)


if __name__ == "__main__":
    unittest.main()
