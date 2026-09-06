import json
import unittest
from collections import deque
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
GAME_ROOT = REPO_ROOT / "game"
CONFIG_PATH = GAME_ROOT / "data" / "vertical_slice.json"


class GameVerticalSliceContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.config = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))

    def test_prototype_values_are_explicitly_marked_provisional(self):
        self.assertEqual(self.config["schema_version"], 1)
        self.assertIs(self.config["provisional"], True)
        self.assertTrue(self.config["evidence_note"].strip())
        self.assertIn("not claims", self.config["evidence_note"])

    def test_required_gameplay_sensitive_inputs_are_explicit(self):
        store = self.config["store"]
        simulation = self.config["simulation"]
        for key in (
            "width_tiles",
            "height_tiles",
            "subcells_per_tile",
            "entry_subcell",
            "exit_subcell",
        ):
            self.assertIn(key, store)
        for key in (
            "start_minute_of_day",
            "tick_seconds",
            "step_game_minutes",
            "shopping_ticks",
            "checkout_ticks",
        ):
            self.assertIn(key, simulation)

        self.assertGreater(store["width_tiles"], 0)
        self.assertGreater(store["height_tiles"], 0)
        self.assertGreater(store["subcells_per_tile"], 0)
        self.assertGreater(simulation["tick_seconds"], 0)
        self.assertGreater(simulation["step_game_minutes"], 0)
        self.assertGreaterEqual(simulation["start_minute_of_day"], 0)
        self.assertLess(simulation["start_minute_of_day"], 24 * 60)

    def test_fixture_ids_and_required_fixture_kinds_are_present(self):
        fixtures = self.config["fixtures"]
        ids = [fixture["id"] for fixture in fixtures]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertIn("shelf", {fixture["kind"] for fixture in fixtures})
        self.assertIn("checkout", {fixture["kind"] for fixture in fixtures})

    def test_prototype_economy_inputs_are_nonnegative(self):
        self.assertGreaterEqual(self.config["product"]["initial_stock_units"], 0)
        self.assertGreaterEqual(self.config["product"]["sale_price_yen"], 0)
        self.assertGreaterEqual(self.config["economy"]["initial_cash_yen"], 0)

    def test_entry_shelf_checkout_exit_route_is_reachable(self):
        store = self.config["store"]
        scale = store["subcells_per_tile"]
        width = store["width_tiles"] * scale
        height = store["height_tiles"] * scale
        blocked = set()
        interactions = {}

        for fixture in self.config["fixtures"]:
            ox, oy = fixture["origin_subcell"]
            fw, fh = fixture["footprint_tiles"]
            for y in range(oy, oy + fh * scale):
                for x in range(ox, ox + fw * scale):
                    self.assertTrue(0 <= x < width and 0 <= y < height)
                    blocked.add((x, y))
            point = tuple(fixture["interaction_subcell"])
            self.assertTrue(0 <= point[0] < width and 0 <= point[1] < height)
            self.assertNotIn(point, blocked)
            interactions[fixture["kind"]] = point

        entry = tuple(store["entry_subcell"])
        exit_point = tuple(store["exit_subcell"])
        self.assertNotIn(entry, blocked)
        self.assertNotIn(exit_point, blocked)

        self.assertTrue(self._reachable(entry, interactions["shelf"], width, height, blocked))
        self.assertTrue(
            self._reachable(
                interactions["shelf"],
                interactions["checkout"],
                width,
                height,
                blocked,
            )
        )
        self.assertTrue(
            self._reachable(interactions["checkout"], exit_point, width, height, blocked)
        )

    def test_godot_entry_scene_and_scripts_exist(self):
        project = (GAME_ROOT / "project.godot").read_text(encoding="utf-8")
        self.assertIn('run/main_scene="res://scenes/main.tscn"', project)
        for relative in (
            "scenes/main.tscn",
            "scripts/main.gd",
            "scripts/store_view.gd",
            "scripts/vertical_slice_simulation.gd",
        ):
            self.assertTrue((GAME_ROOT / relative).is_file(), relative)

        scene = (GAME_ROOT / "scenes" / "main.tscn").read_text(encoding="utf-8")
        self.assertIn('res://scripts/main.gd', scene)
        self.assertIn('res://scripts/store_view.gd', scene)

    @staticmethod
    def _reachable(start, goal, width, height, blocked):
        frontier = deque([start])
        visited = {start}
        while frontier:
            x, y = frontier.popleft()
            if (x, y) == goal:
                return True
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                candidate = (x + dx, y + dy)
                if candidate in visited or candidate in blocked:
                    continue
                if not (0 <= candidate[0] < width and 0 <= candidate[1] < height):
                    continue
                visited.add(candidate)
                frontier.append(candidate)
        return False


if __name__ == "__main__":
    unittest.main()
