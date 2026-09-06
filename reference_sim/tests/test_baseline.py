import unittest

from conveni_sim.baseline_data import (
    FIXTURES,
    PERMITS,
    PROMOTIONS,
    STORE_VARIANTS,
    TOWN_FACILITIES,
)
from conveni_sim.clock import RepresentativeDayType, SimulationClock
from conveni_sim.models import EvidenceLevel


class BaselineDataTests(unittest.TestCase):
    def test_all_five_promotions_total_9_6m(self):
        self.assertEqual(sum(p.cost_yen.value for p in PROMOTIONS), 9_600_000)

    def test_direct_mail_values_and_payment_timing_are_video_confirmed(self):
        direct_mail = next(item for item in PROMOTIONS if item.id == "direct_mail")
        for value in (
            direct_mail.cost_yen,
            direct_mail.popularity_gain,
            direct_mail.trigger_day,
            direct_mail.trigger_hour,
            direct_mail.payment_timing,
        ):
            self.assertEqual(value.evidence, EvidenceLevel.CONFIRMED_VISUAL)

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

    def test_video_confirmed_copier_values(self):
        by_id = {fixture.id: fixture for fixture in FIXTURES}
        copier_a = by_id["copier_a"]
        copier_b = by_id["copier_b"]

        self.assertEqual(copier_a.capacity.value, 20)
        self.assertEqual(copier_a.attention.value, 10)
        self.assertEqual(copier_a.purchase_price_yen.value, 1_500)
        self.assertEqual(copier_a.maintenance_yen_per_day.value, 1_200)
        self.assertEqual(copier_a.capacity.evidence, EvidenceLevel.CONFIRMED_VISUAL)

        self.assertEqual(copier_b.capacity.value, 40)
        self.assertEqual(copier_b.attention.value, 15)
        self.assertEqual(copier_b.purchase_price_yen.value, 2_000)
        self.assertEqual(copier_b.maintenance_yen_per_day.value, 1_440)
        self.assertEqual(copier_b.capacity.evidence, EvidenceLevel.CONFIRMED_VISUAL)

        self.assertIsNone(copier_a.footprint)
        self.assertIsNone(copier_b.compatible_product_categories)

    def test_video_confirmed_town_facility_aid_values(self):
        by_id = {facility.id: facility for facility in TOWN_FACILITIES}
        self.assertEqual(by_id["police_box"].inducement_aid_yen.value, 400_000)
        self.assertEqual(by_id["company"].inducement_aid_yen.value, 5_400_000)
        self.assertEqual(by_id["pool"].inducement_aid_yen.value, 1_800_000)
        self.assertEqual(by_id["vocational_school"].inducement_aid_yen.value, 4_800_000)
        self.assertEqual(by_id["university"].inducement_aid_yen.value, 9_800_000)
        for facility_id in ("police_box", "company", "vocational_school", "university"):
            self.assertEqual(
                by_id[facility_id].inducement_aid_yen.evidence,
                EvidenceLevel.CONFIRMED_VISUAL,
            )

    def test_university_population_observation_range_matches_research(self):
        by_id = {facility.id: facility for facility in TOWN_FACILITIES}
        university = by_id["university"]
        self.assertEqual(university.observed_population_range.value, (500, 800))
        self.assertEqual(university.observed_population_range.evidence, EvidenceLevel.PROVISIONAL)

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
