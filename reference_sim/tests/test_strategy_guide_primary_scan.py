import unittest

from conveni_sim.baseline_data import FIXTURES, PROMOTIONS, SALARY_TABLE, STORE_VARIANTS, TOWN_FACILITIES
from conveni_sim.models import EvidenceLevel


class PrimaryScanPromotionTests(unittest.TestCase):
    """Checks against a direct read of the strategy guide's own page scans
    (docs/research/strategy-guide-full-decode-2026-09-16.md was built from a
    summary; these tests are grounded in the original PDF pages), which
    resolved the previously-recorded airship/radio/tv popularity_gain
    conflict in the guide's favor (4 independent primary-source
    confirmations vs. one WIKI-derived figure).
    """

    def test_airship_radio_tv_popularity_gain_matches_the_guide_not_the_wiki(self):
        by_id = {promo.id: promo for promo in PROMOTIONS}
        self.assertEqual(by_id["airship"].popularity_gain.value, 40)
        self.assertEqual(by_id["radio"].popularity_gain.value, 60)
        self.assertEqual(by_id["tv"].popularity_gain.value, 90)
        for promo_id in ("airship", "radio", "tv"):
            self.assertEqual(
                by_id[promo_id].popularity_gain.evidence, EvidenceLevel.CONFIRMED_OFFICIAL
            )

    def test_promotion_cost_and_timing_were_not_touched_by_the_popularity_fix(self):
        by_id = {promo.id: promo for promo in PROMOTIONS}
        self.assertEqual(by_id["airship"].cost_yen.value, 1_000_000)
        self.assertEqual(by_id["airship"].trigger_day.value, 3)
        self.assertEqual(by_id["airship"].trigger_hour.value, 15)
        self.assertEqual(by_id["radio"].cost_yen.value, 3_000_000)
        self.assertEqual(by_id["tv"].cost_yen.value, 5_000_000)


class PrimaryScanServiceBonusTests(unittest.TestCase):
    def test_potted_plant_service_bonus_matches_the_guide(self):
        by_id = {fixture.id: fixture for fixture in FIXTURES}
        self.assertEqual(by_id["potted_plant"].service_bonus.value, 2)

    def test_bench_and_fountain_service_bonus_now_match_the_guide(self):
        # RESOLVED 2026-09-17: an explicit one-off user instruction directed
        # that guide-vs-existing conflicts be settled in the guide's favor.
        # Guide reports bench=+4 and fountain=+30, independently confirmed
        # twice each; the previous wiki-derived values (3 and 25) are
        # superseded.
        by_id = {fixture.id: fixture for fixture in FIXTURES}
        self.assertEqual(by_id["bench"].service_bonus.value, 4)
        self.assertEqual(by_id["fountain"].service_bonus.value, 30)


class PrimaryScanStoreVariantTests(unittest.TestCase):
    def test_previously_unknown_construction_prices_are_now_filled(self):
        by_id = {variant.id: variant for variant in STORE_VARIANTS}
        self.assertEqual(by_id["small_bottom"].construction_price_yen.value, 6_000_000)
        self.assertEqual(by_id["medium_top"].construction_price_yen.value, 12_000_000)
        self.assertEqual(by_id["medium_bottom"].construction_price_yen.value, 12_000_000)
        self.assertEqual(by_id["large_top"].construction_price_yen.value, 18_000_000)
        self.assertEqual(by_id["large_bottom"].construction_price_yen.value, 18_000_000)

    def test_editable_floor_now_matches_the_guides_store_data_table(self):
        # RESOLVED 2026-09-17 (same instruction as the service-bonus fix
        # above). The guide's own 店舗データ table gives every variant's
        # 店舗内 dimensions directly; none matched the previous
        # visual-reconstruction-derived (8, 13) / (13, 14) values, which are
        # superseded. store1/3/5 -> *_top and store2/4/6 -> *_bottom is an
        # inferred pairing by list order, not a confirmed orientation match.
        by_id = {variant.id: variant for variant in STORE_VARIANTS}
        self.assertEqual(by_id["small_top"].editable_floor.value, (5, 8))
        self.assertEqual(by_id["small_bottom"].editable_floor.value, (8, 5))
        self.assertEqual(by_id["medium_top"].editable_floor.value, (7, 10))
        self.assertEqual(by_id["medium_bottom"].editable_floor.value, (10, 7))
        self.assertEqual(by_id["large_top"].editable_floor.value, (8, 12))
        self.assertEqual(by_id["large_bottom"].editable_floor.value, (12, 8))


class PrimaryScanTownFacilityTests(unittest.TestCase):
    def test_new_facilities_are_present_with_footprint_and_aid(self):
        by_id = {facility.id: facility for facility in TOWN_FACILITIES}
        for facility_id, footprint, aid_yen in (
            ("mansion", (2, 3), 4_200_000),
            ("gym", (2, 3), 4_200_000),
            ("athletic_field", (4, 5), 2_000_000),
            ("event_hall", (2, 2), 6_000_000),
            ("kindergarten", (2, 3), 1_200_000),
            ("elementary_school", (4, 4), 3_200_000),
            ("middle_school", (5, 5), 5_000_000),
            ("high_school", (6, 6), 7_200_000),
            ("park", (2, 2), 2_000_000),
            ("aquarium", (3, 3), 2_700_000),
            ("zoo", (6, 6), 7_200_000),
            ("amusement_park", (7, 7), 9_800_000),
        ):
            self.assertIn(facility_id, by_id)
            self.assertEqual(by_id[facility_id].footprint.value, footprint)
            self.assertEqual(by_id[facility_id].inducement_aid_yen.value, aid_yen)

    def test_existing_facility_inducement_aid_was_not_changed(self):
        # These 6 aid amounts were independently confirmed, not replaced.
        by_id = {facility.id: facility for facility in TOWN_FACILITIES}
        self.assertEqual(by_id["police_box"].inducement_aid_yen.value, 400_000)
        self.assertEqual(by_id["company"].inducement_aid_yen.value, 5_400_000)
        self.assertEqual(by_id["pool"].inducement_aid_yen.value, 1_800_000)
        self.assertEqual(by_id["vocational_school"].inducement_aid_yen.value, 4_800_000)
        self.assertEqual(by_id["university"].inducement_aid_yen.value, 9_800_000)

    def test_fire_station_inducement_aid_was_filled_in_not_invented(self):
        by_id = {facility.id: facility for facility in TOWN_FACILITIES}
        fire_station = by_id["fire_station"]
        self.assertEqual(fire_station.inducement_aid_yen.value, 600_000)
        self.assertEqual(fire_station.footprint.value, (2, 3))


class PrimaryScanSalaryTableTests(unittest.TestCase):
    def test_hourly_wage_matches_the_guides_own_generating_formula(self):
        for entry in SALARY_TABLE:
            self.assertEqual(entry.hourly_wage_yen.value, entry.age_years * 10 + 100)


if __name__ == "__main__":
    unittest.main()
