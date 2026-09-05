import unittest

from conveni_sim.baseline_data import FIXTURES, STORE_VARIANTS
from conveni_sim.models import EvidenceLevel, EvidenceValue, FixtureDefinition
from conveni_sim.store_grid import Direction, GridPoint, PlacementError, StoreGrid


class StoreGridTests(unittest.TestCase):
    def test_small_store_uses_half_tile_internal_resolution(self):
        small_top = next(v for v in STORE_VARIANTS if v.id == "small_top")
        grid = StoreGrid.from_store_variant(small_top)
        self.assertEqual((grid.width_tiles, grid.height_tiles), (8, 13))
        self.assertEqual((grid.width_subcells, grid.height_subcells), (16, 26))

    def test_1x1_fixture_occupies_four_half_tile_subcells(self):
        grid = StoreGrid(4, 4)
        placement = grid.place_fixture(
            instance_id="plant-1",
            fixture_id="potted_plant",
            origin_subcell=GridPoint(2, 2),
            footprint_tiles=(1, 1),
        )
        self.assertEqual(len(placement.occupied_cells), 4)

    def test_rotation_swaps_rectangular_footprint_and_interaction_side(self):
        grid = StoreGrid(5, 5)
        placement = grid.place_fixture(
            instance_id="fixture-1",
            fixture_id="synthetic_1x2",
            origin_subcell=GridPoint(2, 2),
            footprint_tiles=(1, 2),
            rotation_quarter_turns=1,
            interaction_side=Direction.NORTH,
        )
        self.assertEqual((placement.width_subcells, placement.height_subcells), (4, 2))
        self.assertEqual(placement.interaction_side, Direction.EAST)

    def test_interaction_edge_is_addressable_at_half_tile_resolution(self):
        grid = StoreGrid(4, 4)
        grid.place_fixture(
            instance_id="shelf-1",
            fixture_id="synthetic_shelf",
            origin_subcell=GridPoint(2, 2),
            footprint_tiles=(1, 1),
            interaction_side=Direction.NORTH,
        )
        self.assertEqual(
            grid.interaction_cells("shelf-1"),
            frozenset({GridPoint(2, 1), GridPoint(3, 1)}),
        )

    def test_blocking_fixture_forces_path_detour(self):
        grid = StoreGrid(4, 3)
        grid.place_fixture(
            instance_id="barrier-1",
            fixture_id="synthetic_barrier",
            origin_subcell=GridPoint(2, 0),
            footprint_tiles=(1, 2),
        )
        path = grid.shortest_path(GridPoint(0, 0), GridPoint(5, 0))
        self.assertIsNotNone(path)
        self.assertGreater(len(path), 6)
        self.assertTrue(all(cell not in grid.blocked_cells for cell in path))

    def test_unknown_fixture_footprint_cannot_be_silently_placed(self):
        grid = StoreGrid(4, 4)
        unknown = next(f for f in FIXTURES if f.id == "vending_machine")
        with self.assertRaises(PlacementError):
            grid.place_definition(
                unknown,
                instance_id="vending-1",
                origin_subcell=GridPoint(0, 0),
            )

    def test_definition_can_explicitly_be_nonblocking(self):
        grid = StoreGrid(2, 2)
        synthetic = FixtureDefinition(
            "synthetic_nonblocking",
            EvidenceValue((1, 1), EvidenceLevel.HYPOTHESIS, "unit-test fixture"),
            blocks_pedestrian=EvidenceValue(False, EvidenceLevel.HYPOTHESIS, "unit-test fixture"),
        )
        grid.place_definition(
            synthetic,
            instance_id="nonblocking-1",
            origin_subcell=GridPoint(0, 0),
        )
        self.assertTrue(grid.is_walkable(GridPoint(0, 0)))

    def test_confirmed_parking_definitions_block_pedestrians(self):
        parking = [fixture for fixture in FIXTURES if fixture.id.startswith("parking_")]
        self.assertEqual(len(parking), 3)
        for fixture in parking:
            self.assertIsNotNone(fixture.blocks_pedestrian)
            self.assertTrue(fixture.blocks_pedestrian.value)
            self.assertEqual(fixture.blocks_pedestrian.evidence, EvidenceLevel.CONFIRMED_COMMUNITY)

    def test_unreachable_fixture_interaction_returns_none(self):
        grid = StoreGrid(3, 3)
        grid.place_fixture(
            instance_id="shelf-1",
            fixture_id="synthetic_shelf",
            origin_subcell=GridPoint(2, 2),
            footprint_tiles=(1, 1),
            interaction_side=Direction.NORTH,
        )
        grid.set_static_blocked(GridPoint(x, 1) for x in range(grid.width_subcells))
        self.assertIsNone(grid.shortest_path_to_fixture(GridPoint(0, 0), "shelf-1"))


if __name__ == "__main__":
    unittest.main()
