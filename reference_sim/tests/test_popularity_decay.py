import unittest

from conveni_sim.promotion import PopularityDecayContext, StorePopularityRuntime


class PopularityDecayOpportunityTests(unittest.TestCase):
    def test_ordinary_day_records_rating_snapshot_without_guessing_loss(self):
        popularity = StorePopularityRuntime()
        popularity.add_store("main", popularity=82, rating=4)

        opportunity = popularity.record_ordinary_daily_decay("main")

        self.assertEqual(opportunity.context, PopularityDecayContext.ORDINARY_DAY)
        self.assertEqual(opportunity.before, 82)
        self.assertEqual(opportunity.rating_snapshot, 4)
        self.assertFalse(opportunity.resolved)
        self.assertIsNone(opportunity.applied_loss)
        self.assertEqual(popularity.popularity("main"), 82)

    def test_unknown_rating_stays_unknown(self):
        popularity = StorePopularityRuntime()
        popularity.add_store("main", popularity=50)

        opportunity = popularity.record_ordinary_daily_decay("main")

        self.assertIsNone(opportunity.rating_snapshot)
        self.assertEqual(popularity.popularity("main"), 50)

    def test_month_skip_records_one_day_equivalent_opportunity_only(self):
        popularity = StorePopularityRuntime()
        popularity.add_store("main", popularity=60, rating=3)

        opportunity = popularity.record_month_skip_decay("main")

        self.assertEqual(opportunity.context, PopularityDecayContext.MONTH_SKIP)
        self.assertEqual(len(popularity.decay_opportunities), 1)
        self.assertEqual(popularity.popularity("main"), 60)

    def test_explicit_resolution_applies_observed_after_value(self):
        popularity = StorePopularityRuntime()
        popularity.add_store("main", popularity=70, rating=2)
        opportunity = popularity.record_ordinary_daily_decay("main")

        resolved = popularity.resolve_decay_opportunity(opportunity.sequence, after=67)

        self.assertTrue(resolved.resolved)
        self.assertEqual(resolved.applied_loss, 3)
        self.assertEqual(popularity.popularity("main"), 67)
        self.assertEqual(popularity.unresolved_decay_opportunities, ())

    def test_decay_resolution_cannot_increase_popularity(self):
        popularity = StorePopularityRuntime()
        popularity.add_store("main", popularity=70)
        sequence = popularity.record_ordinary_daily_decay("main").sequence

        with self.assertRaises(ValueError):
            popularity.resolve_decay_opportunity(sequence, after=71)

    def test_decay_resolution_rejects_stale_snapshot_after_other_popularity_event(self):
        popularity = StorePopularityRuntime()
        popularity.add_store("main", popularity=70)
        opportunity = popularity.record_ordinary_daily_decay("main")
        # Simulate another known event being applied before this unresolved decay.
        popularity._popularity["main"] = 80

        with self.assertRaises(ValueError):
            popularity.resolve_decay_opportunity(opportunity.sequence, after=68)

    def test_rating_change_after_record_does_not_rewrite_snapshot(self):
        popularity = StorePopularityRuntime()
        popularity.add_store("main", popularity=70, rating=2)
        opportunity = popularity.record_ordinary_daily_decay("main")

        popularity.set_rating("main", 4)

        self.assertEqual(opportunity.rating_snapshot, 2)
        self.assertEqual(popularity.rating("main"), 4)

    def test_decay_cannot_be_resolved_twice(self):
        popularity = StorePopularityRuntime()
        popularity.add_store("main", popularity=40)
        sequence = popularity.record_ordinary_daily_decay("main").sequence
        popularity.resolve_decay_opportunity(sequence, after=39)

        with self.assertRaises(ValueError):
            popularity.resolve_decay_opportunity(sequence, after=38)


if __name__ == "__main__":
    unittest.main()
