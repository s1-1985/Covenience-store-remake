"""CSRM-006: §21.3 転記データの記録を固定するテスト。

対象は docs/research/quick-reference-guide-part2-2026-09-19.md §5.4
（DATA 4 来客数表）と §3.9（駅ルール・シナリオ開始データ）。
いずれも参照専用で、挙動へ接続されていないことも併せて固定する。
"""

import unittest

from conveni_sim.baseline_data import (
    BEGINNER_RIVAL_START,
    DATA4_VISITOR_COUNTS_DAYTIME_ROWS,
    DATA4_VISITOR_COUNTS_OVERNIGHT_BUILDINGS,
    SCENARIOS,
    SCENARIO_STARTING_POPULATIONS,
    STATION_SPACING_RULE,
)


class Data4OvernightBuildingsTests(unittest.TestCase):
    def test_twenty_one_rows_with_estimated_building_pairing(self):
        self.assertEqual(len(DATA4_VISITOR_COUNTS_OVERNIGHT_BUILDINGS), 21)
        names = [row[0] for row in DATA4_VISITOR_COUNTS_OVERNIGHT_BUILDINGS]
        self.assertEqual(names[0], "消防署")
        self.assertEqual(names[-1], "本屋")

    def test_sample_counts_match_the_transcription(self):
        by_name = {row[0]: row for row in DATA4_VISITOR_COUNTS_OVERNIGHT_BUILDINGS}
        self.assertEqual(by_name["消防署"][1], (0, 5, 0, 0, 5, 0))
        self.assertEqual(by_name["駅(小)"][1], (560, 0, 2620, 1680, 0, 840))
        self.assertEqual(by_name["駅(大)"][1], (1120, 0, 1400, 2240, 560, 280))
        self.assertEqual(by_name["本屋"][1], (9, 8, 1, 6, 1, 0))
        self.assertEqual(by_name["駅(小)"][2:], ("確実", "やや少ない"))

    def test_uncertain_evening_cell_is_recorded_as_unknown_not_invented(self):
        by_name = {row[0]: row for row in DATA4_VISITOR_COUNTS_OVERNIGHT_BUILDINGS}
        # 住宅(小A) の夕は転記自体が UNCERTAIN。None（不明）で固定する。
        self.assertEqual(by_name["住宅(小A)"][1], (7, 10, None, 2, 0, 1))


class Data4DaytimeRowsTests(unittest.TestCase):
    def test_thirty_rows_in_printed_order_without_building_pairing(self):
        self.assertEqual(len(DATA4_VISITOR_COUNTS_DAYTIME_ROWS), 30)
        row_numbers = [row[0] for row in DATA4_VISITOR_COUNTS_DAYTIME_ROWS]
        self.assertEqual(row_numbers, list(range(1, 31)))
        # 建物名は構造上どこにも結び付けられていない（行番号のみ）。
        for row in DATA4_VISITOR_COUNTS_DAYTIME_ROWS:
            self.assertIsInstance(row[0], int)
            self.assertEqual(len(row[1]), 6)

    def test_sample_rows_match_the_transcription(self):
        by_number = {row[0]: row for row in DATA4_VISITOR_COUNTS_DAYTIME_ROWS}
        self.assertEqual(by_number[1][1], (0, 10, 0, 0, 0, 0))
        self.assertEqual(by_number[8][1], (0, 0, 43, 23, 0, 0))
        self.assertEqual(by_number[30][1], (7, 26, 4, 0, 0, 0))
        self.assertEqual(by_number[5][2:], ("だいたい", "確実"))

    def test_daytime_rows_have_no_late_night_or_early_morning_visitors(self):
        # 「朝から夜だけ客のいる建物」という見出しとの整合（転記側の交差検証）。
        for _, counts, _, _ in DATA4_VISITOR_COUNTS_DAYTIME_ROWS:
            self.assertEqual(counts[4], 0)
            self.assertEqual(counts[5], 0)


class StationSpacingRuleTests(unittest.TestCase):
    def test_rule_values(self):
        self.assertEqual(STATION_SPACING_RULE["railway_lines"].value, 2)
        self.assertEqual(STATION_SPACING_RULE["max_stations_per_line"].value, 2)
        self.assertEqual(STATION_SPACING_RULE["min_spacing_areas"].value, 40)


class ScenarioStartDataTests(unittest.TestCase):
    def test_supreme_scenario_is_recorded_with_unknown_objective(self):
        by_id = {scenario.id: scenario for scenario in SCENARIOS}
        self.assertIn("supreme", by_id)
        supreme = by_id["supreme"]
        self.assertEqual(supreme.initial_cash_yen.value, 150_000_000)
        # クリア条件は出典に記載が無く、不明として記録する（invent しない）。
        self.assertIsNone(supreme.objective.value)

    def test_existing_scenario_objectives_are_unchanged(self):
        by_id = {scenario.id: scenario for scenario in SCENARIOS}
        self.assertEqual(
            by_id["beginner"].objective.value,
            "metropolitan_government_after_population_threshold",
        )
        self.assertEqual(by_id["intermediate"].objective.value, "10_player_stores")
        self.assertEqual(by_id["advanced"].objective.value, "owner_rating_5_stars")

    def test_starting_populations(self):
        self.assertEqual(SCENARIO_STARTING_POPULATIONS["beginner"].value, 2_179)
        self.assertEqual(SCENARIO_STARTING_POPULATIONS["intermediate"].value, 1_880)
        self.assertEqual(SCENARIO_STARTING_POPULATIONS["advanced"].value, 2_849)
        self.assertIn("UNCERTAIN", SCENARIO_STARTING_POPULATIONS["advanced"].note)
        self.assertEqual(SCENARIO_STARTING_POPULATIONS["supreme"].value, 1_416)

    def test_beginner_rival_start_block(self):
        headquarters = BEGINNER_RIVAL_START["headquarters"]
        self.assertEqual(headquarters["popularity"].value, 20)
        self.assertEqual(headquarters["security"].value, 89)
        self.assertEqual(headquarters["cleaning"].value, 30)
        self.assertEqual(headquarters["service"].value, 30)
        branch = BEGINNER_RIVAL_START["branch"]
        self.assertEqual(branch["security"].value, 58)
        self.assertEqual(branch["service"].value, 31)
        self.assertEqual(branch["buyout_price_yen"].value, 46_721_490)
        facilities = BEGINNER_RIVAL_START["security_facilities"]
        self.assertEqual(facilities["police_box"].value, 2)
        self.assertEqual(facilities["fire_station"].value, 1)


if __name__ == "__main__":
    unittest.main()
