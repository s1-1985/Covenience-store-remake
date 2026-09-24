import unittest

from conveni_sim.baseline_data import (
    ANNUAL_CALENDAR,
    BUSINESS_HOURS_PRESETS,
    FIXTURES,
    MONTHLY_WEATHER_PERCENTAGES,
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

    def test_scenario_initial_rival_topology_matches_the_confirmed_long_play_records(self):
        by_id = {scenario.id: scenario for scenario in SCENARIOS}

        beginner = by_id["beginner"]
        self.assertIsNone(beginner.initial_rival_store_roles)
        self.assertEqual(beginner.initial_rival_branch_exists.value, True)
        self.assertEqual(beginner.initial_rival_branch_exists.evidence, EvidenceLevel.CONFIRMED_COMMUNITY)

        intermediate = by_id["intermediate"]
        self.assertEqual(
            intermediate.initial_rival_store_roles.value, ("headquarters", "branch", "branch")
        )
        self.assertEqual(
            intermediate.initial_rival_store_roles.evidence, EvidenceLevel.CONFIRMED_COMMUNITY
        )
        self.assertIsNone(intermediate.rival_can_open_branches_after_start)

        advanced = by_id["advanced"]
        self.assertEqual(advanced.initial_rival_store_roles.value, ("headquarters",))
        self.assertEqual(advanced.rival_can_open_branches_after_start.value, True)

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

    def test_store_variant_building_area_breakdown_matches_the_guide(self):
        # Task #57: 建物面積 breakdown (総面積/建物全体/床面積/店外スペース) from
        # the guide's own 店舗データ table (book pages 106-109),
        # cross-checked value-for-value against 本2.pdf; see
        # docs/research/strategy-guide-shopkeeper-manual-part2-2026-09-19.md
        # section 4.1. Distinct from editable_floor (店舗内, the in-store
        # placement grid).
        by_id = {variant.id: variant for variant in STORE_VARIANTS}
        expected = {
            "small_top": (100, 70, 40, 30),
            "small_bottom": (100, 70, 40, 30),
            "medium_top": (144, 108, 70, 36),
            "medium_bottom": (144, 108, 70, 36),
            "large_top": (196, 154, 108, 42),
            "large_bottom": (196, 154, 108, 42),
        }
        for variant_id, (total, whole_building, floor, exterior) in expected.items():
            variant = by_id[variant_id]
            self.assertEqual(variant.total_area_tiles.value, total)
            self.assertEqual(variant.whole_building_area_tiles.value, whole_building)
            self.assertEqual(variant.floor_area_tiles.value, floor)
            self.assertEqual(variant.exterior_space_tiles.value, exterior)
            for field in (
                variant.total_area_tiles,
                variant.whole_building_area_tiles,
                variant.floor_area_tiles,
                variant.exterior_space_tiles,
            ):
                self.assertEqual(field.evidence, EvidenceLevel.CONFIRMED_OFFICIAL)
        # total_area_tiles is not simply width*height of editable_floor (a
        # different, smaller in-store placement grid) -- confirms these are
        # genuinely separate figures, not a derivable duplicate.
        small_top = by_id["small_top"]
        self.assertNotEqual(
            small_top.total_area_tiles.value,
            small_top.editable_floor.value[0] * small_top.editable_floor.value[1],
        )

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

    def test_monthly_weather_percentages_each_sum_to_100(self):
        # Decision 0132: re-verified 2026-09-24 at 400dpi against the same
        # quick reference book page 3 the 2026-09-19 pass flagged 3 rows of
        # (July/September/December) as not summing to 100 at reduced
        # confidence. Every one of the 12 rows now sums exactly.
        self.assertEqual(len(MONTHLY_WEATHER_PERCENTAGES), 12)
        for entry in MONTHLY_WEATHER_PERCENTAGES:
            total = (
                entry.clear_percent.value
                + entry.fine_percent.value
                + entry.cloudy_percent.value
                + entry.rain_or_snow_percent.value
                + entry.storm_percent.value
            )
            self.assertEqual(total, 100, f"month={entry.month}")
            self.assertEqual(entry.clear_percent.evidence, EvidenceLevel.CONFIRMED_OFFICIAL)

    def test_business_hours_presets_match_the_guides_clock_diagram(self):
        by_label = {entry.label.value: entry for entry in BUSINESS_HOURS_PRESETS}
        self.assertEqual(
            set(by_label),
            {
                "AM10:00~PM6:00",
                "AM7:00~PM11:00",
                "AM11:00~AM2:00",
                "PM0:00~AM4:00",
                "PM7:00~AM11:00",
                "24時間営業",
                "臨時休業",
            },
        )
        # Preset 3 is transcribed verbatim even though the guide's own
        # printed duration label doesn't arithmetically match its own
        # printed start/end times (11:00~2:00 is 15h, not the printed 16h) --
        # re-verified directly against the source scan, not a scan-legibility
        # guess. This project does not silently correct the source.
        preset_3 = by_label["AM11:00~AM2:00"]
        self.assertEqual(preset_3.printed_label.value, "16時間営業")
        self.assertEqual(preset_3.hours.value.open_minute, 11 * 60)
        self.assertEqual(preset_3.hours.value.close_minute, 2 * 60)
        closed = by_label["臨時休業"]
        self.assertIsNone(closed.hours)
        for entry in BUSINESS_HOURS_PRESETS:
            self.assertEqual(entry.label.evidence, EvidenceLevel.CONFIRMED_OFFICIAL)

    def test_annual_calendar_has_one_entry_per_month_with_four_days_each(self):
        self.assertEqual(sorted(entry.month for entry in ANNUAL_CALENDAR), list(range(1, 13)))
        for entry in ANNUAL_CALENDAR:
            self.assertEqual(len(entry.day_types.value), 4)
            self.assertIn(entry.season.value, {"冬期", "夏期"})
            for day_type in entry.day_types.value:
                self.assertIn(day_type, {"weekday", "holiday"})


class ClockTests(unittest.TestCase):
    def test_representative_day_type_matches_the_guides_annual_calendar(self):
        # Task #63/decision 0132: representative_day_type now reads
        # baseline_data.ANNUAL_CALENDAR (book page 3) instead of a "day==4 is
        # the only holiday" simplification. Exercise every (month, day) pair
        # the table defines, rather than duplicating its literal values here.
        for entry in ANNUAL_CALENDAR:
            for day_index, expected in enumerate(entry.day_types.value):
                clock = SimulationClock(month=entry.month, day=day_index + 1)
                self.assertEqual(
                    clock.representative_day_type,
                    RepresentativeDayType(expected),
                    f"month={entry.month} day={day_index + 1}",
                )

    def test_march_is_three_weekdays_and_a_holiday(self):
        # A representative month that does still follow the common
        # 3-weekday + 1-holiday shape (most months do; January/May/August/
        # December each carry one extra 休日 -- see ANNUAL_CALENDAR).
        clock = SimulationClock(month=3, day=1)
        self.assertEqual(clock.representative_day_type, RepresentativeDayType.WEEKDAY)
        clock.advance_day()
        self.assertEqual(clock.representative_day_type, RepresentativeDayType.WEEKDAY)
        clock.advance_day()
        self.assertEqual(clock.representative_day_type, RepresentativeDayType.WEEKDAY)
        clock.advance_day()
        self.assertEqual(clock.representative_day_type, RepresentativeDayType.HOLIDAY)

    def test_january_has_a_holiday_on_day_one_too(self):
        # January deviates from the common shape (holiday, weekday, weekday,
        # holiday) -- plausibly New Year's Day, per ANNUAL_CALENDAR's own
        # docstring inference, not a stated fact.
        clock = SimulationClock(month=1, day=1)
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
