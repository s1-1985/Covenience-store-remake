import unittest

from conveni_sim.store_events import compute_contest_prize_yen, magazine_or_contest_event_is_eligible
from conveni_sim.town import TOTAL_STORE_CAP_INCLUDING_RIVALS, TownState


class TownStateTests(unittest.TestCase):
    def test_defaults_to_zero(self):
        town = TownState()
        self.assertEqual(town.population, 0)
        self.assertEqual(town.store_count_including_rivals, 0)

    def test_has_capacity_below_the_confirmed_combined_cap(self):
        self.assertEqual(TOTAL_STORE_CAP_INCLUDING_RIVALS, 10)
        town = TownState(store_count_including_rivals=9)
        self.assertTrue(town.has_capacity_for_new_store())

    def test_has_no_capacity_at_or_above_the_confirmed_combined_cap(self):
        town = TownState(store_count_including_rivals=TOTAL_STORE_CAP_INCLUDING_RIVALS)
        self.assertFalse(town.has_capacity_for_new_store())
        over_cap = TownState(store_count_including_rivals=TOTAL_STORE_CAP_INCLUDING_RIVALS + 1)
        self.assertFalse(over_cap.has_capacity_for_new_store())

    def test_rejects_negative_values(self):
        with self.assertRaises(ValueError):
            TownState(population=-1)
        with self.assertRaises(ValueError):
            TownState(store_count_including_rivals=-1)

    def test_feeds_directly_into_store_events_eligibility_checks(self):
        town = TownState(population=10_000, store_count_including_rivals=5)

        self.assertTrue(
            magazine_or_contest_event_is_eligible(town.population, town.store_count_including_rivals)
        )
        self.assertEqual(
            compute_contest_prize_yen(town.store_count_including_rivals),
            50_000_000,
        )

    def test_below_threshold_is_not_eligible(self):
        town = TownState(population=9_999, store_count_including_rivals=5)

        self.assertFalse(
            magazine_or_contest_event_is_eligible(town.population, town.store_count_including_rivals)
        )


if __name__ == "__main__":
    unittest.main()
