import unittest

from conveni_sim.baseline_data import (
    FIXTURES,
    PERMITS,
    PROMOTIONS,
    SCENARIOS,
    STORE_VARIANTS,
    TOWN_FACILITIES,
    TRADE_AREA_RADIUS_TILES,
)
from conveni_sim.clock import RepresentativeDayType, SimulationClock
from conveni_sim.models import EvidenceLevel


class BaselineDataTests(unittest.TestCase):
    def test_scenario_cash_uses_the_documented_community_evidence_level(self):
        by_id = {scenario.id: scenario for scenario in SCENARIOS}
        for scenario_id, expected_cash in (
            ("beginner", 200_000_000),
            ("intermediate", 150_000_000),
            ("advanced", 150_000_000),
        ):
            self.assertEqual(by_id[scenario_id].initial_cash_yen.value, expected_cash)
            self.assertEqual(
                by_id[scenario_id].initial_cash_yen.evidence,
                EvidenceLevel.CONFIRMED_COMMUNITY,
            )

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
        # bench/fountain: RESOLVED 2026-09-17 in the strategy guide's favor
        # (was 3/25 from the wiki; see test_strategy_guide_primary_scan.py).
        by_id = {fixture.id: fixture for fixture in FIXTURES}
        self.assertEqual(by_id["potted_plant"].service_bonus.value, 2)
        self.assertEqual(by_id["bench"].service_bonus.value, 4)
        self.assertEqual(by_id["fountain"].service_bonus.value, 30)

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

        self.assertEqual(copier_a.footprint.value, (1, 1))
        self.assertEqual(copier_b.footprint.value, (2, 1))
        self.assertEqual(copier_a.compatible_product_categories.value, ("copy_paper",))
        self.assertEqual(copier_b.compatible_product_categories.value, ("copy_paper",))

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
        self.assertEqual(by_id["medium_top"].construction_price_yen.value, 12_000_000)
        self.assertIsNone(by_id["small_bottom"].orientation)
        # medium_top.editable_floor was filled in 2026-09-17 from the
        # strategy guide's 店舗データ table; see
        # test_strategy_guide_primary_scan.py for the full set.
        self.assertEqual(by_id["medium_top"].editable_floor.value, (7, 10))

    def test_permit_fees_and_distances_match_the_guide(self):
        # RESOLVED 2026-09-17: previously both fields were None for every
        # permit; the guide's own "販売許可に必要な金額" table and distance
        # diagram (book pages 6-7) give explicit values for all three.
        self.assertEqual({p.id for p in PERMITS}, {"tobacco", "alcohol", "medicine"})
        by_id = {p.id: p for p in PERMITS}
        self.assertEqual(by_id["tobacco"].fee_yen.value, 7_000_000)
        self.assertEqual(by_id["tobacco"].exclusion_distance_tiles.value, 7)
        self.assertEqual(by_id["alcohol"].fee_yen.value, 3_000_000)
        self.assertEqual(by_id["alcohol"].exclusion_distance_tiles.value, 11)
        self.assertEqual(by_id["medicine"].fee_yen.value, 10_000_000)
        self.assertEqual(by_id["medicine"].exclusion_distance_tiles.value, 15)
        for permit in PERMITS:
            self.assertTrue(permit.eligibility_is_independent.value)

    def test_trade_area_radius_by_arrival_method_matches_the_guide(self):
        # New 2026-09-17: the guide's own "来店手段/エリア半径" table (book
        # page 31) directly answers part of what was previously recorded as
        # an unconfirmed trade-area radius formula.
        by_method = {entry.arrival_method.value: entry.radius.value for entry in TRADE_AREA_RADIUS_TILES}
        self.assertEqual(by_method, {"徒歩": 20, "自転車": 40, "バイク": 60, "自動車": 70})
        for entry in TRADE_AREA_RADIUS_TILES:
            self.assertEqual(entry.radius.evidence, EvidenceLevel.CONFIRMED_OFFICIAL)


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
