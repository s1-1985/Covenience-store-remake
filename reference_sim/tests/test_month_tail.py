import unittest

from conveni_sim.clock import SimulationClock
from conveni_sim.economy import DayEndOutcome, DayEndResult, DaySummary
from conveni_sim.month_cycle import RepresentativeMonthRecorder
from conveni_sim.month_tail import MonthTailTransitionRuntime
from conveni_sim.promotion import PopularityDecayContext, StorePopularityRuntime


class MonthTailTransitionRuntimeTests(unittest.TestCase):
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

    def make_complete_sample(self):
        recorder = RepresentativeMonthRecorder(SimulationClock(year=3, month=8, day=1))
        sample = None
        for marker in (1, 2, 3, 4):
            sample = recorder.close_representative_day(self.make_day_end(marker))
        assert sample is not None
        return sample

    def test_records_explicit_tail_without_synthesizing_skipped_days(self):
        runtime = MonthTailTransitionRuntime()
        transition = runtime.record_transition(self.make_complete_sample())

        self.assertEqual((transition.year, transition.month), (3, 8))
        self.assertEqual(transition.popularity_decay_sequences, ())
        self.assertEqual(len(runtime.transitions), 1)

    def test_records_exactly_one_month_skip_decay_per_selected_store(self):
        popularity = StorePopularityRuntime()
        popularity.add_store("store-a", popularity=80, rating=None)
        popularity.add_store("store-b", popularity=55, rating=12)

        transition = MonthTailTransitionRuntime().record_transition(
            self.make_complete_sample(),
            popularity=popularity,
            popularity_store_ids=("store-a", "store-b"),
        )

        self.assertEqual(len(transition.popularity_decay_sequences), 2)
        opportunities = popularity.decay_opportunities
        self.assertEqual(len(opportunities), 2)
        self.assertTrue(
            all(item.context is PopularityDecayContext.MONTH_SKIP for item in opportunities)
        )
        self.assertEqual(tuple(item.before for item in opportunities), (80, 55))
        self.assertEqual(tuple(item.rating_snapshot for item in opportunities), (None, 12))
        self.assertEqual((popularity.popularity("store-a"), popularity.popularity("store-b")), (80, 55))

    def test_duplicate_store_ids_do_not_multiply_tail_decay(self):
        popularity = StorePopularityRuntime()
        popularity.add_store("store-a", popularity=80)

        transition = MonthTailTransitionRuntime().record_transition(
            self.make_complete_sample(),
            popularity=popularity,
            popularity_store_ids=("store-a", "store-a"),
        )

        self.assertEqual(len(transition.popularity_decay_sequences), 1)
        self.assertEqual(len(popularity.decay_opportunities), 1)

    def test_unknown_popularity_target_fails_before_partial_recording(self):
        popularity = StorePopularityRuntime()
        popularity.add_store("store-a", popularity=80)

        with self.assertRaises(KeyError):
            MonthTailTransitionRuntime().record_transition(
                self.make_complete_sample(),
                popularity=popularity,
                popularity_store_ids=("store-a", "missing"),
            )

        self.assertEqual(popularity.decay_opportunities, ())

    def test_incomplete_representative_month_is_rejected(self):
        recorder = RepresentativeMonthRecorder(SimulationClock(year=3, month=8, day=3))
        recorder.close_representative_day(self.make_day_end(3))
        sample = recorder.close_representative_day(self.make_day_end(4))
        assert sample is not None

        with self.assertRaises(ValueError):
            MonthTailTransitionRuntime().record_transition(sample)

    def test_same_month_transition_cannot_be_recorded_twice(self):
        runtime = MonthTailTransitionRuntime()
        sample = self.make_complete_sample()
        runtime.record_transition(sample)

        with self.assertRaises(ValueError):
            runtime.record_transition(sample)


if __name__ == "__main__":
    unittest.main()
