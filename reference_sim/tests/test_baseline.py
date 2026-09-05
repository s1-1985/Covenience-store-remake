import unittest

from conveni_sim.baseline_data import FIXTURES, PERMITS, PROMOTIONS, STORE_VARIANTS
from conveni_sim.clock import RepresentativeDayType, SimulationClock


class BaselineDataTests(unittest.TestCase):
    def test_all_five_promotions_total_9_6m(self):
        self.assertEqual(sum(p.cost_yen.value for p in PROMOTIONS), 9_600_000)

    def test_service_fixture_values(self):
        by_id = {fixture.id: fixture for fixture in FIXTURES}
        self.assertEqual(by_id["potted_plant"].service_bonus.value, 2)
        self.assertEqual(by_id["bench"].service_bonus.value, 3)
        self.assertEqual(by_id["fountain"].service_bonus.value, 25)

    def test_parking_values(self):
        by_id = {fixture.id: fixture for fixture in FIXTURES}
        self.assertEqual(by_id["parking_ground"].parking_capacity.value, 2)
        self.assertEqual(by_id["parking_two_story"].parking_capacity.value, 4)
        self.assertEqual(by_id["parking_tower"].parking_capacity.value, 20)

    def test_unknown_store_values_stay_unknown(self):
        by_id = {variant.id: variant for variant in STORE_VARIANTS}
        self.assertIsNone(by_id["medium_top"].construction_price_yen)
        self.assertIsNone(by_id["small_bottom"].orientation)

    def test_permits_are_independent_and_distances_unknown(self):
        self.assertEqual({p.id for p in PERMITS}, {"tobacco", "alcohol", "medicine"})
        for permit in PERMITS:
            self.assertTrue(permit.eligibility_is_independent.value)
            self.assertIsNone(permit.exclusion_distance_tiles)


class ClockTests(unittest.TestCase):
    def test_first_three_days_are_weekdays_and_fourth_is_holiday(self):
        clock = SimulationClock(day=1)
        self.assertEqual(clock.representative_day_type, RepresentativeDayType.WEEKDAY)
        clock.advance_day()
        self.assertEqual(clock.representative_day_type, RepresentativeDayType.WEEKDAY)
        clock.advance_day()
        self.assertEqual(clock.representative_day_type, RepresentativeDayType.WEEKDAY)
        clock.advance_day()
        self.assertEqual(clock.representative_day_type, RepresentativeDayType.HOLIDAY)

    def test_day_four_rolls_to_next_month_day_one(self):
        clock = SimulationClock(year=1, month=1, day=4)
        boundary = clock.advance_day()
        self.assertIsNotNone(boundary)
        self.assertEqual((clock.year, clock.month, clock.day), (1, 2, 1))

    def test_december_rolls_year(self):
        clock = SimulationClock(year=3, month=12, day=4)
        clock.advance_day()
        self.assertEqual((clock.year, clock.month, clock.day), (4, 1, 1))


if __name__ == "__main__":
    unittest.main()
