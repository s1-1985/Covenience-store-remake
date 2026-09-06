import unittest

from conveni_sim.clock import SimulationClock
from conveni_sim.operating_time import SubdayClock
from conveni_sim.representative_day_runner import RepresentativeDayRunner
from conveni_sim.store_grid import StoreGrid
from conveni_sim.store_runtime import StoreRuntimeHarness
from conveni_sim.store_step import StoreStepOrchestrator


class RepresentativeDayRunnerTests(unittest.TestCase):
    def make_runner(self, *, hour=0, minute=0, year=1, month=1, day=1):
        runtime = StoreRuntimeHarness(
            StoreGrid(3, 3),
            initial_cash_yen=1_000,
            subday_clock=SubdayClock(hour, minute),
        )
        calendar = SimulationClock(year=year, month=month, day=day)
        orchestrator = StoreStepOrchestrator(runtime)
        return runtime, calendar, RepresentativeDayRunner(orchestrator, calendar)

    def test_last_ordinary_step_stops_at_2359_before_boundary_only_advance(self):
        runtime, calendar, runner = self.make_runner(hour=23, minute=50)

        result = runner.run(step_game_minutes=10)

        self.assertEqual(len(result.steps), 1)
        self.assertEqual(result.steps[0].clock.previous_minute_of_day, 23 * 60 + 50)
        self.assertEqual(result.steps[0].clock.current_minute_of_day, 23 * 60 + 59)
        self.assertEqual(result.steps[0].clock.days_crossed, 0)
        self.assertEqual(result.boundary_clock.previous_minute_of_day, 23 * 60 + 59)
        self.assertEqual(result.boundary_clock.current_minute_of_day, 0)
        self.assertEqual(result.boundary_clock.days_crossed, 1)
        self.assertEqual(runtime.subday_clock.minute_of_day, 0)
        self.assertEqual(calendar.day, 2)

    def test_step_cadence_is_caller_supplied_and_final_step_is_shortened(self):
        _, _, runner = self.make_runner()

        result = runner.run(step_game_minutes=600)

        self.assertEqual(len(result.steps), 3)
        self.assertEqual(
            [
                (step.clock.previous_minute_of_day, step.clock.current_minute_of_day)
                for step in result.steps
            ],
            [(0, 600), (600, 1200), (1200, 1439)],
        )
        self.assertTrue(all(step.clock.days_crossed == 0 for step in result.steps))
        self.assertEqual(result.simulated_game_minutes, 1439)

    def test_day_end_ledger_closes_before_midnight_boundary(self):
        runtime, _, runner = self.make_runner(hour=23, minute=59)
        runtime.cash.record_sale(120, source_id="checkout")

        result = runner.run(step_game_minutes=10)

        self.assertEqual(result.steps, ())
        self.assertEqual(result.day_end.summary.known_credits_yen, 120)
        self.assertEqual(result.day_end.summary.known_debits_yen, 0)
        self.assertEqual(result.cash_before_yen, 1_120)
        self.assertEqual(result.cash_after_yen, 1_120)

    def test_fourth_representative_day_advances_calendar_month_and_year(self):
        _, calendar, runner = self.make_runner(
            hour=23,
            minute=59,
            year=1,
            month=12,
            day=4,
        )

        result = runner.run(step_game_minutes=5)

        self.assertIsNotNone(result.month_boundary)
        self.assertEqual(result.month_boundary.previous_year, 1)
        self.assertEqual(result.month_boundary.previous_month, 12)
        self.assertEqual(result.month_boundary.next_year, 2)
        self.assertEqual(result.month_boundary.next_month, 1)
        self.assertEqual((calendar.year, calendar.month, calendar.day), (2, 1, 1))

    def test_nonpositive_step_cadence_is_rejected(self):
        _, _, runner = self.make_runner()
        with self.assertRaises(ValueError):
            runner.run(step_game_minutes=0)


if __name__ == "__main__":
    unittest.main()
