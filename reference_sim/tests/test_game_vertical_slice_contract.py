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
        self.assertEqual(self.config["schema_version"], 4)
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
            "checkout_fixture_id",
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
        for fixture in fixtures:
            self.assertIn(fixture["rotation_quarter_turns"], range(4))
        fixtures_by_id = {fixture["id"]: fixture for fixture in fixtures}
        product_fixtures = [fixtures_by_id[product["fixture_id"]] for product in self.config["products"]]
        checkout_fixture = fixtures_by_id[
            self.config["simulation"]["checkout_fixture_id"]
        ]
        self.assertTrue(all(fixture["kind"] == "shelf" for fixture in product_fixtures))
        self.assertEqual(checkout_fixture["kind"], "checkout")

    def test_prototype_economy_inputs_are_nonnegative(self):
        self.assertGreaterEqual(len(self.config["products"]), 2)
        product_ids = [product["id"] for product in self.config["products"]]
        self.assertEqual(len(product_ids), len(set(product_ids)))
        for product in self.config["products"]:
            self.assertGreaterEqual(product["initial_stock_units"], 0)
            self.assertGreaterEqual(product["sale_price_yen"], 0)
        self.assertGreaterEqual(self.config["economy"]["initial_cash_yen"], 0)

    def test_actor_collection_inputs_are_explicit_and_unique(self):
        customer = self.config["customer"]
        staff = self.config["staff"]
        self.assertTrue(customer["id_prefix"].strip())
        self.assertGreaterEqual(len(customer["visit_plan_product_ids"]), 2)
        self.assertEqual(
            set(customer["visit_plan_product_ids"]),
            {product["id"] for product in self.config["products"]},
        )
        self.assertTrue(staff["checkout_staff_id"].strip())
        self.assertGreaterEqual(len(staff["members"]), 2)
        staff_ids = [member["id"] for member in staff["members"]]
        self.assertEqual(len(staff_ids), len(set(staff_ids)))
        self.assertIn(staff["checkout_staff_id"], staff_ids)
        for member in staff["members"]:
            self.assertEqual(len(member["start_subcell"]), 2)
            x, y = member["start_subcell"]
            store = self.config["store"]
            self.assertTrue(0 <= x < store["width_tiles"] * store["subcells_per_tile"])
            self.assertTrue(0 <= y < store["height_tiles"] * store["subcells_per_tile"])

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
            interactions[fixture["id"]] = point

        entry = tuple(store["entry_subcell"])
        exit_point = tuple(store["exit_subcell"])
        self.assertNotIn(entry, blocked)
        self.assertNotIn(exit_point, blocked)

        product_by_id = {product["id"]: product for product in self.config["products"]}
        cursor = entry
        for product_id in self.config["customer"]["visit_plan_product_ids"]:
            target = interactions[product_by_id[product_id]["fixture_id"]]
            self.assertTrue(self._reachable(cursor, target, width, height, blocked))
            cursor = target
        checkout = interactions[self.config["simulation"]["checkout_fixture_id"]]
        self.assertTrue(self._reachable(cursor, checkout, width, height, blocked))
        self.assertTrue(
            self._reachable(checkout, exit_point, width, height, blocked)
        )

    def test_godot_entry_scene_and_scripts_exist(self):
        project = (GAME_ROOT / "project.godot").read_text(encoding="utf-8")
        self.assertIn('run/main_scene="res://scenes/main.tscn"', project)
        for relative in (
            "scenes/main.tscn",
            "scripts/main.gd",
            "scripts/store_view.gd",
            "scripts/vertical_slice_simulation.gd",
            "scripts/headless_smoke.gd",
            "scripts/domain/store_layout.gd",
            "scripts/domain/inventory_state.gd",
            "scripts/domain/inventory_catalog.gd",
            "scripts/domain/economy_state.gd",
            "scripts/domain/customer_state.gd",
            "scripts/domain/customer_roster.gd",
            "scripts/domain/staff_state.gd",
            "scripts/domain/staff_roster.gd",
        ):
            self.assertTrue((GAME_ROOT / relative).is_file(), relative)

        scene = (GAME_ROOT / "scenes" / "main.tscn").read_text(encoding="utf-8")
        self.assertIn('res://scripts/main.gd', scene)
        self.assertIn('res://scripts/store_view.gd', scene)

    def test_vertical_slice_supports_repeat_customer_visits(self):
        simulation = (GAME_ROOT / "scripts" / "vertical_slice_simulation.gd").read_text(
            encoding="utf-8"
        )
        main = (GAME_ROOT / "scripts" / "main.gd").read_text(encoding="utf-8")
        scene = (GAME_ROOT / "scenes" / "main.tscn").read_text(encoding="utf-8")
        smoke = (GAME_ROOT / "scripts" / "headless_smoke.gd").read_text(encoding="utf-8")

        self.assertIn("func start_next_customer() -> bool:", simulation)
        self.assertIn('simulation.start_next_customer()', main)
        self.assertIn('name="NextCustomerButton"', scene)
        self.assertIn("while simulation.inventory.has_stock():", smoke)
        self.assertIn("sales_after_sellout", smoke)

    def test_vertical_slice_composes_separate_domain_state(self):
        simulation = (GAME_ROOT / "scripts" / "vertical_slice_simulation.gd").read_text(
            encoding="utf-8"
        )
        expected = {
            "StoreLayoutScript": "store_layout.gd",
            "InventoryCatalogScript": "inventory_catalog.gd",
            "EconomyStateScript": "economy_state.gd",
            "CustomerRosterScript": "customer_roster.gd",
            "StaffRosterScript": "staff_roster.gd",
        }
        for script_name, filename in expected.items():
            self.assertIn(script_name, simulation)
            self.assertIn(filename, simulation)

        self.assertIn("var record := economy.settle_basket(", simulation)
        self.assertIn("layout.find_path", simulation)
        self.assertIn("layout.interaction_for_fixture", simulation)
        self.assertNotIn("func _find_path", simulation)
        self.assertNotIn("var stock_units:", simulation)
        self.assertNotIn("var cash_yen:", simulation)

    def test_explicit_multi_product_plan_builds_a_basket_without_choice_ai(self):
        customer = (GAME_ROOT / "scripts" / "domain" / "customer_state.gd").read_text(
            encoding="utf-8"
        )
        catalog = (GAME_ROOT / "scripts" / "domain" / "inventory_catalog.gd").read_text(
            encoding="utf-8"
        )
        economy = (GAME_ROOT / "scripts" / "domain" / "economy_state.gd").read_text(
            encoding="utf-8"
        )
        simulation = (GAME_ROOT / "scripts" / "vertical_slice_simulation.gd").read_text(
            encoding="utf-8"
        )
        smoke = (GAME_ROOT / "scripts" / "headless_smoke.gd").read_text(encoding="utf-8")

        self.assertIn("planned_product_ids", customer)
        self.assertIn("func add_basket_line", customer)
        self.assertIn("func basket_total_yen", customer)
        self.assertIn("func try_take_one(product_id", catalog)
        self.assertIn("func settle_basket", economy)
        self.assertIn('"transaction_id":', economy)
        self.assertIn('"lines": lines.duplicate(true)', economy)
        self.assertIn("func sale_record_for_customer", economy)
        self.assertIn("func recorded_revenue_yen", economy)
        self.assertIn("func mark_settled", customer)
        self.assertIn("customer.advance_plan()", simulation)
        self.assertIn("customer.mark_settled(record)", simulation)
        self.assertIn("planned products unavailable; customer leaving", simulation)
        self.assertIn("sellout revenue must equal", smoke)
        self.assertIn("sale ledger revenue must reconcile with cash", smoke)
        self.assertIn("sale ledger must retain an immutable basket snapshot", smoke)

    def test_customer_visits_are_retained_without_inventing_concurrent_arrivals(self):
        roster = (GAME_ROOT / "scripts" / "domain" / "customer_roster.gd").read_text(
            encoding="utf-8"
        )
        smoke = (GAME_ROOT / "scripts" / "headless_smoke.gd").read_text(
            encoding="utf-8"
        )
        self.assertIn("func can_admit() -> bool:", roster)
        self.assertIn('active().phase == "done"', roster)
        self.assertIn("customers[customer_id] = customer", roster)
        self.assertIn("each visit must retain a distinct customer state", smoke)
        self.assertIn("customer ids must remain unique", smoke)

    def test_touch_layout_relocation_is_transactional_and_provisional(self):
        layout = (GAME_ROOT / "scripts" / "domain" / "store_layout.gd").read_text(
            encoding="utf-8"
        )
        simulation = (GAME_ROOT / "scripts" / "vertical_slice_simulation.gd").read_text(
            encoding="utf-8"
        )
        view = (GAME_ROOT / "scripts" / "store_view.gd").read_text(encoding="utf-8")
        scene = (GAME_ROOT / "scenes" / "main.tscn").read_text(encoding="utf-8")
        smoke = (GAME_ROOT / "scripts" / "headless_smoke.gd").read_text(encoding="utf-8")

        self.assertIn("func try_move_fixture", layout)
        self.assertIn("candidate_fixtures", layout)
        self.assertIn("func try_relocate_fixture", simulation)
        self.assertIn("not customers.can_admit()", simulation)
        self.assertIn("_required_routes_are_reachable()", simulation)
        self.assertIn("fixture_relocation_requested", view)
        self.assertIn("InputEventScreenTouch", view)
        self.assertIn('name="LayoutEditValue"', scene)
        self.assertIn("rejected fixture relocation must be atomic", smoke)
        self.assertIn("locked during an active visit", smoke)

    def test_fixture_rotation_and_reset_preserve_transaction_boundaries(self):
        layout = (GAME_ROOT / "scripts" / "domain" / "store_layout.gd").read_text(
            encoding="utf-8"
        )
        simulation = (GAME_ROOT / "scripts" / "vertical_slice_simulation.gd").read_text(
            encoding="utf-8"
        )
        main = (GAME_ROOT / "scripts" / "main.gd").read_text(encoding="utf-8")
        scene = (GAME_ROOT / "scenes" / "main.tscn").read_text(encoding="utf-8")
        smoke = (GAME_ROOT / "scripts" / "headless_smoke.gd").read_text(encoding="utf-8")

        self.assertIn("func try_rotate_fixture_clockwise", layout)
        self.assertIn("func fixture_snapshot", layout)
        self.assertIn("func restore_fixture_snapshot", layout)
        self.assertIn("layout.reset()", simulation)
        self.assertIn("func try_rotate_fixture_clockwise", simulation)
        self.assertIn("_on_rotate_fixture_pressed", main)
        self.assertIn('name="RotateFixtureButton"', scene)
        self.assertIn("four clockwise rotations must restore fixture geometry", smoke)
        self.assertIn("full reset must restore the configured fixture layout", smoke)

    def test_godot_smoke_loads_main_scene_without_redundant_editor_startup(self):
        workflow = (
            REPO_ROOT / ".github" / "workflows" / "reference-tests.yml"
        ).read_text(encoding="utf-8")
        smoke = (GAME_ROOT / "scripts" / "headless_smoke.gd").read_text(encoding="utf-8")

        self.assertIn('load(MAIN_SCENE_PATH) as PackedScene', smoke)
        self.assertIn('main_scene.instantiate()', smoke)
        self.assertNotIn(' --editor ', workflow)
        self.assertIn('timeout-minutes: 5', workflow)

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
