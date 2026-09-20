import math
import unittest

from conveni_sim.remake_town_spatial import (
    PERMIT_EXCLUSION_DISTANCE_TILES,
    STORE_CONSTRUCTION_MIN_DISTANCE_TILES,
    TRADE_AREA_RADIUS_TILES_BY_ARRIVAL_METHOD,
    can_acquire_permit_at,
    can_construct_store_at,
    chebyshev_distance_tiles,
    facility_area_tiles_within_range,
    trade_area_overlap_ratio,
)


class ConfirmedConstantsTests(unittest.TestCase):
    def test_store_construction_min_distance_matches_the_guide_diagram(self):
        self.assertEqual(STORE_CONSTRUCTION_MIN_DISTANCE_TILES, 5)

    def test_permit_exclusion_distances_match_the_guide_diagram(self):
        self.assertEqual(
            PERMIT_EXCLUSION_DISTANCE_TILES,
            {"tobacco": 7, "alcohol": 11, "medicine": 15},
        )

    def test_trade_area_radii_match_the_guide_table(self):
        self.assertEqual(
            TRADE_AREA_RADIUS_TILES_BY_ARRIVAL_METHOD,
            {"徒歩": 20, "自転車": 40, "バイク": 60, "自動車": 70},
        )


class ChebyshevDistanceTests(unittest.TestCase):
    def test_same_position_is_zero_distance(self):
        self.assertEqual(chebyshev_distance_tiles((3, 4), (3, 4)), 0)

    def test_pure_horizontal_or_vertical_step(self):
        self.assertEqual(chebyshev_distance_tiles((0, 0), (5, 0)), 5)
        self.assertEqual(chebyshev_distance_tiles((0, 0), (0, 5)), 5)

    def test_diagonal_step_counts_as_the_larger_axis_not_the_sum(self):
        # Chebyshev, not Manhattan: (3, 4) away is distance 4, not 7.
        self.assertEqual(chebyshev_distance_tiles((0, 0), (3, 4)), 4)


class CanConstructStoreAtTests(unittest.TestCase):
    def test_far_enough_from_every_existing_store_is_allowed(self):
        self.assertTrue(can_construct_store_at((10, 10), [(0, 0), (0, 20)]))

    def test_exactly_the_minimum_distance_is_allowed(self):
        self.assertTrue(can_construct_store_at((5, 0), [(0, 0)]))

    def test_one_tile_closer_than_the_minimum_is_rejected(self):
        self.assertFalse(can_construct_store_at((4, 0), [(0, 0)]))

    def test_rejected_if_too_close_to_any_one_existing_store(self):
        self.assertFalse(can_construct_store_at((10, 10), [(0, 0), (12, 10)]))

    def test_no_existing_stores_is_always_allowed(self):
        self.assertTrue(can_construct_store_at((0, 0), []))


class CanAcquirePermitAtTests(unittest.TestCase):
    def test_far_enough_from_every_existing_holder_is_allowed(self):
        self.assertTrue(can_acquire_permit_at("tobacco", (0, 0), [(20, 20)]))

    def test_exactly_the_permit_radius_is_allowed(self):
        self.assertTrue(can_acquire_permit_at("tobacco", (7, 0), [(0, 0)]))

    def test_one_tile_closer_than_the_permit_radius_is_rejected(self):
        self.assertFalse(can_acquire_permit_at("tobacco", (6, 0), [(0, 0)]))

    def test_larger_radius_permits_reject_from_further_away(self):
        # medicine's 15-tile radius is stricter than tobacco's 7-tile one.
        self.assertTrue(can_acquire_permit_at("tobacco", (10, 0), [(0, 0)]))
        self.assertFalse(can_acquire_permit_at("medicine", (10, 0), [(0, 0)]))

    def test_no_other_holders_is_always_allowed(self):
        self.assertTrue(can_acquire_permit_at("alcohol", (0, 0), []))

    def test_unknown_permit_id_raises(self):
        with self.assertRaises(KeyError):
            can_acquire_permit_at("does-not-exist", (0, 0), [(0, 0)])


class TradeAreaOverlapRatioTests(unittest.TestCase):
    def test_far_apart_circles_do_not_overlap(self):
        self.assertEqual(trade_area_overlap_ratio((0, 0), 20, (1000, 0), 20), 0.0)

    def test_identical_position_and_radius_fully_overlaps(self):
        self.assertEqual(trade_area_overlap_ratio((0, 0), 20, (0, 0), 20), 1.0)

    def test_smaller_circle_entirely_inside_larger_one_is_full_overlap(self):
        # radius 20 circle centered 5 away from a radius 70 circle's center
        # is entirely contained (5 + 20 <= 70).
        self.assertEqual(trade_area_overlap_ratio((0, 0), 70, (5, 0), 20), 1.0)

    def test_partial_overlap_is_strictly_between_zero_and_one(self):
        ratio = trade_area_overlap_ratio((0, 0), 20, (30, 0), 20)
        self.assertGreater(ratio, 0.0)
        self.assertLess(ratio, 1.0)

    def test_more_overlap_as_circles_move_closer(self):
        far = trade_area_overlap_ratio((0, 0), 20, (35, 0), 20)
        near = trade_area_overlap_ratio((0, 0), 20, (15, 0), 20)
        self.assertLess(far, near)

    def test_symmetric_in_its_two_stores(self):
        ratio_ab = trade_area_overlap_ratio((0, 0), 20, (25, 0), 40)
        ratio_ba = trade_area_overlap_ratio((25, 0), 40, (0, 0), 20)
        self.assertAlmostEqual(ratio_ab, ratio_ba)

    def test_zero_radius_never_overlaps(self):
        self.assertEqual(trade_area_overlap_ratio((0, 0), 0, (0, 0), 20), 0.0)

    def test_negative_radius_rejected(self):
        with self.assertRaises(ValueError):
            trade_area_overlap_ratio((0, 0), -1, (0, 0), 20)

    def test_matches_confirmed_radii_by_arrival_method(self):
        # A 徒歩(on-foot, radius 20) customer's trade area barely reaches a
        # store 40 tiles away, while a 自動車(car, radius 70) customer's does
        # with room to spare -- sanity-checks the CONFIRMED_OFFICIAL radii
        # actually drive a materially different overlap outcome.
        walk_radius = TRADE_AREA_RADIUS_TILES_BY_ARRIVAL_METHOD["徒歩"]
        car_radius = TRADE_AREA_RADIUS_TILES_BY_ARRIVAL_METHOD["自動車"]
        self.assertEqual(
            trade_area_overlap_ratio((0, 0), walk_radius, (45, 0), walk_radius), 0.0
        )
        self.assertGreater(
            trade_area_overlap_ratio((0, 0), car_radius, (45, 0), car_radius), 0.0
        )


class FacilityAreaTilesWithinRangeTests(unittest.TestCase):
    def test_facility_entirely_within_range_counts_every_footprint_tile(self):
        # A 2x2 police box 10 tiles away from the store, well within a
        # 16-tile range: all 4 footprint tiles count.
        self.assertEqual(facility_area_tiles_within_range((0, 0), (10, 0), (2, 2), 16), 4)

    def test_facility_straddling_the_range_boundary_counts_only_in_range_tiles(self):
        # A 2x2 footprint at x=16..17: only the x=16 column (distance
        # exactly 16, still in range) counts; x=17 (distance 17) does not.
        self.assertEqual(facility_area_tiles_within_range((0, 0), (16, 0), (2, 2), 16), 2)

    def test_facility_entirely_outside_range_counts_zero(self):
        self.assertEqual(facility_area_tiles_within_range((0, 0), (17, 0), (2, 2), 16), 0)

    def test_larger_footprint_counts_more_tiles_when_fully_in_range(self):
        # fire_station's confirmed (2, 3) footprint vs police_box's (2, 2).
        police_box_tiles = facility_area_tiles_within_range((0, 0), (5, 5), (2, 2), 16)
        fire_station_tiles = facility_area_tiles_within_range((0, 0), (5, 5), (2, 3), 16)
        self.assertEqual(police_box_tiles, 4)
        self.assertEqual(fire_station_tiles, 6)
        self.assertGreater(fire_station_tiles, police_box_tiles)

    def test_zero_range_only_counts_a_footprint_tile_exactly_at_the_store(self):
        self.assertEqual(facility_area_tiles_within_range((0, 0), (0, 0), (1, 1), 0), 1)
        self.assertEqual(facility_area_tiles_within_range((0, 0), (1, 0), (1, 1), 0), 0)

    def test_negative_footprint_dimension_rejected(self):
        with self.assertRaises(ValueError):
            facility_area_tiles_within_range((0, 0), (0, 0), (-1, 2), 16)

    def test_negative_range_rejected(self):
        with self.assertRaises(ValueError):
            facility_area_tiles_within_range((0, 0), (0, 0), (2, 2), -1)

    def test_feeds_confirmed_bonus_formula_via_security_facility_coverage(self):
        # Task #61 integration: the spatial count this function produces is
        # exactly what store_value.SecurityFacilityCoverage expects as
        # police_box_area_tiles/fire_station_area_tiles -- the first actual
        # caller of that class's *_area_tiles fields computed from real
        # positions instead of a caller-supplied constant.
        from conveni_sim.store_value import (
            FIRE_STATION_BONUS_PER_AREA_TILE,
            POLICE_BOX_BONUS_PER_AREA_TILE,
            SECURITY_FACILITY_RANGE_TILES,
            SecurityFacilityCoverage,
        )

        store_position = (0, 0)
        police_box_tiles = facility_area_tiles_within_range(
            store_position, (5, 5), (2, 2), SECURITY_FACILITY_RANGE_TILES
        )
        fire_station_tiles = facility_area_tiles_within_range(
            store_position, (-5, -5), (2, 3), SECURITY_FACILITY_RANGE_TILES
        )
        coverage = SecurityFacilityCoverage(
            police_box_area_tiles=police_box_tiles, fire_station_area_tiles=fire_station_tiles
        )
        self.assertEqual(coverage.police_box_bonus, police_box_tiles * POLICE_BOX_BONUS_PER_AREA_TILE)
        self.assertEqual(coverage.fire_station_bonus, fire_station_tiles * FIRE_STATION_BONUS_PER_AREA_TILE)
        self.assertTrue(coverage.has_any_protection)


if __name__ == "__main__":
    unittest.main()
