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
        self.assertEqual(self.config["schema_version"], 14)
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
            self.assertGreaterEqual(product["restock_unit_cost_yen"], 0)
        self.assertGreaterEqual(self.config["economy"]["initial_cash_yen"], 0)
        restock = self.config["provisional_restock"]
        self.assertIn(restock["product_id"], product_ids)
        self.assertGreater(restock["quantity"], 0)
        self.assertGreaterEqual(restock["total_cost_yen"], 0)

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
        self.assertIn(self.config["provisional_restock"]["staff_id"], staff_ids)
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
        self.assertIn('run/main_scene="res://scenes/main_menu.tscn"', project)
        self.assertIn('GameLaunchState="*res://scripts/game_launch_state.gd"', project)
        for relative in (
            "scenes/main.tscn",
            "scenes/main_menu.tscn",
            "scripts/main.gd",
            "scripts/main_menu.gd",
            "scripts/game_launch_state.gd",
            "scripts/save_game_service.gd",
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
            "scripts/domain/chain_visitor_milestone.gd",
            "scripts/domain/store_events.gd",
            "scripts/domain/checkout_timing.gd",
            "scripts/domain/restock_timing.gd",
            "scripts/domain/staff_roster.gd",
            "scripts/domain/runtime_event_log.gd",
            "scripts/domain/demand_policy.gd",
        ):
            self.assertTrue((GAME_ROOT / relative).is_file(), relative)

        scene = (GAME_ROOT / "scenes" / "main.tscn").read_text(encoding="utf-8")
        self.assertIn('res://scripts/main.gd', scene)
        self.assertIn('res://scripts/store_view.gd', scene)

        menu_scene = (GAME_ROOT / "scenes" / "main_menu.tscn").read_text(encoding="utf-8")
        self.assertIn('res://scripts/main_menu.gd', menu_scene)

        # The entry point (main_menu.tscn) must actually lead back to the
        # gameplay scene (main.tscn) it replaced as run/main_scene.
        main_menu_script = (GAME_ROOT / "scripts" / "main_menu.gd").read_text(
            encoding="utf-8"
        )
        self.assertIn('GAMEPLAY_SCENE_PATH := "res://scenes/main.tscn"', main_menu_script)

    def test_basic_menu_ui_wires_new_game_continue_quit_and_in_game_save_load(self):
        main_menu_script = (GAME_ROOT / "scripts" / "main_menu.gd").read_text(
            encoding="utf-8"
        )
        main_script = (GAME_ROOT / "scripts" / "main.gd").read_text(encoding="utf-8")
        launch_state = (GAME_ROOT / "scripts" / "game_launch_state.gd").read_text(
            encoding="utf-8"
        )
        main_scene = (GAME_ROOT / "scenes" / "main.tscn").read_text(encoding="utf-8")
        smoke = (GAME_ROOT / "scripts" / "headless_smoke.gd").read_text(encoding="utf-8")

        # Main menu: New Game / Continue / Quit.
        self.assertIn("func _on_new_game_pressed() -> void:", main_menu_script)
        self.assertIn("func _on_continue_pressed() -> void:", main_menu_script)
        self.assertIn("func _on_quit_pressed() -> void:", main_menu_script)
        self.assertIn("get_tree().quit()", main_menu_script)
        # New Game must not silently touch an existing save file.
        self.assertNotIn("delete_save", main_menu_script)

        # A parameterless autoload is the only way to pass "continue" across
        # change_scene_to_file(), since Godot scenes cannot take arguments.
        self.assertIn("var continue_from_save := false", launch_state)
        self.assertIn("GameLaunchState.continue_from_save = true", main_menu_script)
        self.assertIn("GameLaunchState.continue_from_save", main_script)
        # The flag must be consumed (reset to false) once read, not left set
        # for every future fresh game entered directly.
        self.assertIn("GameLaunchState.continue_from_save = false", main_script)

        # In-game menu: Save / Load / Quit to Menu, using the same
        # SaveGameService task #28 already built (not a second, parallel
        # save mechanism).
        self.assertIn("func _on_save_pressed() -> void:", main_script)
        self.assertIn("func _on_load_pressed() -> void:", main_script)
        self.assertIn("func _on_quit_to_menu_pressed() -> void:", main_script)
        self.assertIn("_save_service.save_to_path(simulation)", main_script)
        self.assertIn("_save_service.load_from_path(simulation)", main_script)
        self.assertIn('name="SaveButton"', main_scene)
        self.assertIn('name="LoadButton"', main_scene)
        self.assertIn('name="QuitToMenuButton"', main_scene)

        self.assertIn("main scene is missing expected node", smoke)
        self.assertIn("main menu scene is missing expected node", smoke)
        self.assertIn(
            "the Continue button must start disabled when no save file exists", smoke
        )

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
            "RuntimeEventLogScript": "runtime_event_log.gd",
        }
        for script_name, filename in expected.items():
            self.assertIn(script_name, simulation)
            self.assertIn(filename, simulation)

        self.assertIn("var record: Dictionary = economy.settle_basket(", simulation)
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
        self.assertIn('"customer_leaving_without_sale"', simulation)
        self.assertIn("sellout revenue must equal", smoke)
        self.assertIn("sale ledger revenue must reconcile with cash", smoke)
        self.assertIn("sale ledger must retain an immutable basket snapshot", smoke)

    def test_runtime_event_log_exports_cause_neutral_observation_snapshot(self):
        event_log = (GAME_ROOT / "scripts" / "domain" / "runtime_event_log.gd").read_text(
            encoding="utf-8"
        )
        simulation = (GAME_ROOT / "scripts" / "vertical_slice_simulation.gd").read_text(
            encoding="utf-8"
        )
        smoke = (GAME_ROOT / "scripts" / "headless_smoke.gd").read_text(encoding="utf-8")

        self.assertIn('"sequence": _next_sequence', event_log)
        self.assertIn('"details": details.duplicate(true)', event_log)
        self.assertIn("func snapshot() -> Array:", event_log)
        self.assertIn("func count_type", event_log)
        self.assertIn("func observation_snapshot() -> Dictionary:", simulation)
        self.assertIn('"provisional": true', simulation)
        for event_type in (
            "customer_entered",
            "customer_reached_product",
            "product_picked",
            "product_unavailable",
            "checkout_started",
            "checkout_completed",
            "customer_exited",
            "fixture_relocated",
            "fixture_rotated",
            "inventory_restock",
        ):
            self.assertIn(f'"{event_type}"', simulation)
        self.assertIn("event log sequence must be contiguous", smoke)
        self.assertIn("event log snapshots must be immutable copies", smoke)
        self.assertIn("provisional scenario boundary", smoke)

    def test_explicit_restock_records_stock_expense_and_event_without_formula(self):
        inventory = (GAME_ROOT / "scripts" / "domain" / "inventory_catalog.gd").read_text(
            encoding="utf-8"
        )
        economy = (GAME_ROOT / "scripts" / "domain" / "economy_state.gd").read_text(
            encoding="utf-8"
        )
        simulation = (GAME_ROOT / "scripts" / "vertical_slice_simulation.gd").read_text(
            encoding="utf-8"
        )
        smoke = (GAME_ROOT / "scripts" / "headless_smoke.gd").read_text(encoding="utf-8")

        self.assertIn("func add_explicit_units", inventory)
        self.assertIn("func record_explicit_expense", economy)
        self.assertIn("func recorded_expenses_yen", economy)
        self.assertIn("func apply_explicit_restock", simulation)
        self.assertIn('"expenses": economy.expense_records.duplicate(true)', simulation)
        self.assertIn("explicit restock must create one immutable expense record", smoke)
        self.assertIn("restocked product did not return to the sale flow", smoke)

    def test_customer_visits_are_retained_and_passive_demand_flow_stays_single_customer(self):
        # Renamed from ..._without_inventing_concurrent_arrivals: task #36
        # added a real concurrent-customer path (see
        # test_concurrent_customers_are_supported_via_the_explicit_admission_path
        # below), so "no concurrent arrivals anywhere" is no longer true of
        # this client as a whole. What is still true, and still asserted
        # here, is that the fully-automatic passive demand flow
        # (demand_admit_if_due(), gated by the original single-customer
        # can_admit()) deliberately was not changed and stays exactly as
        # single-customer as before. start_next_customer() -- the manual
        # "Admit next customer" button -- did gain concurrency; see the next
        # test.
        roster = (GAME_ROOT / "scripts" / "domain" / "customer_roster.gd").read_text(
            encoding="utf-8"
        )
        simulation = (GAME_ROOT / "scripts" / "vertical_slice_simulation.gd").read_text(
            encoding="utf-8"
        )
        smoke = (GAME_ROOT / "scripts" / "headless_smoke.gd").read_text(
            encoding="utf-8"
        )
        self.assertIn("func can_admit() -> bool:", roster)
        self.assertIn('active().phase == "done"', roster)
        self.assertIn("customers[customer_id] = customer", roster)
        self.assertIn("func demand_admit_if_due() -> bool:", simulation)
        self.assertIn("not customers.can_admit():\n        return false\n    if not demand", simulation)
        self.assertIn("each visit must retain a distinct customer state", smoke)
        self.assertIn("customer ids must remain unique", smoke)
        self.assertIn(
            "demand-driven admission must be blocked while a customer visit is still active",
            smoke,
        )

    def test_concurrent_customers_are_supported_via_the_explicit_admission_path(self):
        roster = (GAME_ROOT / "scripts" / "domain" / "customer_roster.gd").read_text(
            encoding="utf-8"
        )
        simulation = (GAME_ROOT / "scripts" / "vertical_slice_simulation.gd").read_text(
            encoding="utf-8"
        )
        store_view = (GAME_ROOT / "scripts" / "store_view.gd").read_text(encoding="utf-8")
        main = (GAME_ROOT / "scripts" / "main.gd").read_text(encoding="utf-8")
        smoke = (GAME_ROOT / "scripts" / "headless_smoke.gd").read_text(encoding="utf-8")
        config = self.config

        # max_concurrent_customers is a REMAKE_BALANCED_DEFAULT scope
        # decision (no strategy-guide/wiki source states a capacity), not a
        # recovered original limit.
        customer = config["customer"]
        self.assertIn("max_concurrent_customers", customer)
        self.assertGreaterEqual(customer["max_concurrent_customers"], 1)
        self.assertIn("REMAKE_BALANCED_DEFAULT", customer["max_concurrent_customers_evidence_note"])

        self.assertIn("func can_admit_concurrent() -> bool:", roster)
        self.assertIn("func all_settled() -> bool:", roster)
        self.assertIn("func active_customers() -> Array:", roster)

        # can_admit_concurrent() (not the single-customer can_admit()) gates
        # both the explicit/observed admission path and the manual "Admit
        # next customer" button, so a player can actually reach concurrent
        # customers through play, not only through the observed/scripted
        # path -- only the fully-automatic passive demand flow
        # (demand_admit_if_due(), covered by the previous test) stays
        # single-customer.
        self.assertIn("func start_explicit_customer", simulation)
        self.assertIn("func start_next_customer() -> bool:\n    if is_game_over or not customers.can_admit_concurrent():", simulation)
        self.assertIn("not customers.can_admit_concurrent()", simulation)

        # Layout-edit-safety gates were moved off can_admit() to all_settled():
        # with more than one customer possibly active, can_admit() alone only
        # reflects the single most-recently-admitted customer and could
        # wrongly read as "safe to edit" while an earlier customer is still
        # mid-visit.
        for guarded_function in (
            "func try_purchase_fixture(",
            "func try_relocate_fixture(",
            "func try_rotate_fixture_clockwise(",
            "func try_purchase_permit(",
            "func try_procure_product(",
            "func try_purchase_promotion(",
            "func try_expand_chain(",
            "func apply_explicit_restock(",
        ):
            self.assertIn(guarded_function, simulation)
        self.assertIn("not customers.all_settled()", simulation)

        # The single checkout fixture/staff still serializes service: a
        # customer that finishes shopping queues rather than starting
        # checkout immediately, and only one customer is dispatched off the
        # queue at a time.
        self.assertIn("_checkout_queue", simulation)
        self.assertIn("func _dispatch_checkout_queue() -> void:", simulation)
        self.assertIn('"waiting_checkout"', simulation)

        # Rendering and the HUD were both updated to show every active
        # customer, not only the single most-recently-admitted one.
        self.assertIn("simulation.customers.active_customers()", store_view)
        self.assertIn("active_customers", main)

        self.assertIn(
            "a second customer with an identical plan must be admittable while the first is still shopping",
            smoke,
        )
        self.assertIn(
            "a third customer must not be admittable once max_concurrent_customers",
            smoke,
        )
        self.assertIn(
            "no more than one customer may occupy the single checkout's service slot at once",
            smoke,
        )
        self.assertIn(
            "start_next_customer() must be able to admit a second customer while the first is still active",
            smoke,
        )
        self.assertIn(
            "start_next_customer() must be rejected once max_concurrent_customers is already reached",
            smoke,
        )
        self.assertIn(
            "second customer never had to wait in the checkout queue behind the first",
            smoke,
        )

    def test_sample_layouts_can_be_loaded_and_are_destructive_not_undoable(self):
        simulation = (GAME_ROOT / "scripts" / "vertical_slice_simulation.gd").read_text(
            encoding="utf-8"
        )
        layout = (GAME_ROOT / "scripts" / "domain" / "store_layout.gd").read_text(
            encoding="utf-8"
        )
        main = (GAME_ROOT / "scripts" / "main.gd").read_text(encoding="utf-8")
        scene = (GAME_ROOT / "scenes" / "main.tscn").read_text(encoding="utf-8")
        smoke = (GAME_ROOT / "scripts" / "headless_smoke.gd").read_text(encoding="utf-8")
        config = self.config

        # Sample-layout existence and its destructive/non-reversible loading
        # are CONFIRMED first-title evidence
        # (docs/research/ss-layout-entrance-register-and-chain-
        # cannibalization-2026-09-06.md section 3); the exact content of any
        # sample is not, so every sample here must be tagged
        # REMAKE_BALANCED_DEFAULT rather than presented as recovered data.
        self.assertIn("sample_layouts", config)
        self.assertGreaterEqual(len(config["sample_layouts"]), 1)
        sample_ids = set()
        for sample in config["sample_layouts"]:
            self.assertIn("sample_id", sample)
            self.assertIn("REMAKE_BALANCED_DEFAULT", sample["evidence_note"])
            sample_ids.add(sample["sample_id"])
            fixture_ids = {f["id"] for f in sample["fixtures"]}
            self.assertIn(config["simulation"]["checkout_fixture_id"], fixture_ids)
        self.assertIn("default_layout", sample_ids)
        self.assertIn("with_bench", sample_ids)

        self.assertIn("func try_load_sample_layout(sample_id: String) -> bool:", simulation)
        self.assertIn("not customers.all_settled()", simulation)

        # No undo/resale mechanic is invented: reusing an already-owned
        # fixture id is free, a genuinely new one costs its normal catalog
        # price, and there is no separate "sell fixture"/"restore previous
        # layout" path -- matching the research note's own boundary ("Keep
        # `load sample`, `sell/remove fixture`, and `restore previous
        # layout` as separate research questions").
        self.assertIn("purchase_price_yen", simulation)
        self.assertNotIn("func try_sell_fixture", simulation)
        self.assertNotIn("func try_undo_sample_layout", simulation)

        # Loading a sample that would strand currently-stocked inventory on
        # a fixture the sample omits is rejected outright, rather than this
        # client inventing an auto-clear-inventory rule the evidence does
        # not describe.
        self.assertIn("func fixture_snapshot_is_valid", layout)
        self.assertIn(
            "a sample that omits a fixture holding procured stock must be rejected",
            smoke,
        )

        # Reachable from ordinary play through dedicated HUD controls, not
        # only a scripted/test-only path.
        self.assertIn('name="SampleLayoutOption"', scene)
        self.assertIn('name="LoadSampleLayoutButton"', scene)
        self.assertIn("func _on_load_sample_layout_pressed() -> void:", main)
        self.assertIn("simulation.try_load_sample_layout(sample_id)", main)

    def test_economy_actions_are_reachable_from_the_ui_not_only_headless_smoke(self):
        # Before task #38, vertical_slice_simulation.gd already implemented
        # try_purchase_fixture/try_purchase_permit/try_procure_product/
        # try_purchase_promotion/try_expand_chain/apply_explicit_restock,
        # but main.gd called none of them: a player could not buy a
        # fixture, get a permit, stock a product, run a promotion, restock
        # a shelf, or expand the chain at all, only headless_smoke.gd could
        # reach these methods. This asserts every one of them is now wired
        # to an actual HUD control.
        main = (GAME_ROOT / "scripts" / "main.gd").read_text(encoding="utf-8")
        scene = (GAME_ROOT / "scenes" / "main.tscn").read_text(encoding="utf-8")
        smoke = (GAME_ROOT / "scripts" / "headless_smoke.gd").read_text(encoding="utf-8")

        for node_name in (
            "FixtureCatalogOption",
            "BuyFixtureButton",
            "PermitOption",
            "BuyPermitButton",
            "ProductCatalogOption",
            "ProcureFixtureOption",
            "ProcureProductButton",
            "RestockProductOption",
            "RestockButton",
            "PromotionOption",
            "BuyPromotionButton",
            "ExpandChainButton",
        ):
            self.assertIn('name="%s"' % node_name, scene)

        for call in (
            "simulation.try_purchase_fixture(catalog_id, instance_id, origin_subcell, interaction)",
            "simulation.try_purchase_permit(permit_id)",
            "simulation.try_procure_product(catalog_id, instance_id, fixture_id)",
            "simulation.apply_explicit_restock(product_id, staff_id, quantity, total_cost_yen)",
            "simulation.try_purchase_promotion(promotion_id)",
            "simulation.try_expand_chain()",
        ):
            self.assertIn(call, main)

        # Buying a new fixture reuses the same tap-to-target flow relocate
        # already uses (store_view's fixture_relocation_requested signal),
        # via a sentinel prefix on the pending selection, rather than a
        # second bespoke input mode.
        self.assertIn("NEW_FIXTURE_SELECTION_PREFIX", main)
        self.assertIn("func _on_fixture_relocation_requested(fixture_id: String, origin_subcell: Vector2i) -> void:", main)
        self.assertIn("func _try_place_new_fixture(catalog_id: String, origin_subcell: Vector2i) -> void:", main)

        # The catalog has no interaction-point data of its own for a newly
        # bought fixture; main.gd derives one from the existing convention
        # (one subcell outside the footprint) rather than requiring a
        # second tap, and gives up rather than guessing past that.
        self.assertIn("func _find_open_interaction_cell", main)
        self.assertIn("Vector2i(-1, -1)", main)

        # Neither the interaction-cell placement heuristic above nor the
        # restock button's batch-size default below are recovered original
        # rules; both must say so in-code with the project's own
        # REMAKE_BALANCED_DEFAULT tag (a doc/PR description alone is not
        # enough), the same discipline domain-layer files like
        # checkout_timing.gd already follow.
        self.assertIn("REMAKE_BALANCED_DEFAULT (task #38): the catalog only records a fixture's", main)
        self.assertIn("REMAKE_BALANCED_DEFAULT (task #38): apply_explicit_restock() takes an", main)

        # The status panel grew enough new controls (fixture/permit/
        # product/restock/promotion/chain, on top of everything task #35-37
        # already added) that it needed to become scrollable rather than
        # spilling off the bottom of the window.
        self.assertIn('type="ScrollContainer"', scene)

        # Covered end-to-end (not just presence-checked) by a headless_smoke
        # scenario that actually enters the scene tree, since this task
        # exercises main.gd itself rather than only
        # vertical_slice_simulation.gd.
        self.assertIn("(load(MAIN_SCENE_PATH) as PackedScene).instantiate()", smoke)
        self.assertIn("_on_buy_fixture_pressed()", smoke)
        self.assertIn("_on_procure_product_pressed()", smoke)
        self.assertIn("_on_restock_pressed()", smoke)
        self.assertIn("_on_buy_promotion_pressed()", smoke)
        self.assertIn("_on_expand_chain_pressed()", smoke)
        self.assertIn(
            "buying a promotion must not charge cash until its scheduled trigger fires",
            smoke,
        )

    def test_demand_driven_customer_arrival_is_a_tagged_remake_default(self):
        demand = self.config["demand"]
        for key in (
            "nearby_population",
            "customer_share_percent",
            "daily_visit_rate_per_population",
            "opening_minutes_per_day",
            "bad_weather_visit_multiplier",
            "rng_seed",
        ):
            self.assertIn(key, demand)
        self.assertGreaterEqual(demand["nearby_population"], 0)
        self.assertGreaterEqual(demand["customer_share_percent"], 0.0)
        self.assertLessEqual(demand["customer_share_percent"], 100.0)
        self.assertGreater(demand["opening_minutes_per_day"], 0)

        demand_policy = (GAME_ROOT / "scripts" / "domain" / "demand_policy.gd").read_text(
            encoding="utf-8"
        )
        simulation = (GAME_ROOT / "scripts" / "vertical_slice_simulation.gd").read_text(
            encoding="utf-8"
        )
        main = (GAME_ROOT / "scripts" / "main.gd").read_text(encoding="utf-8")
        smoke = (GAME_ROOT / "scripts" / "headless_smoke.gd").read_text(encoding="utf-8")

        self.assertIn("REMAKE_BALANCED_DEFAULT", demand_policy)
        self.assertIn("func expected_arrivals_per_minute() -> float:", demand_policy)
        self.assertIn("func customer_arrives_this_minute() -> bool:", demand_policy)
        self.assertIn("func demand_admit_if_due() -> bool:", simulation)
        self.assertIn("func tick_idle_for_demand() -> bool:", simulation)
        self.assertIn("simulation.tick_idle_for_demand()", main)
        self.assertIn("a saturated demand rate must always admit a customer", smoke)
        self.assertIn("a zero demand rate must never admit a customer", smoke)
        self.assertIn(
            "demand-driven admission must be blocked while a customer visit is still active",
            smoke,
        )

    def test_town_state_and_rival_dilution_are_tagged_and_wired_into_demand(self):
        town = self.config["town"]
        for key in ("population", "store_count_including_rivals"):
            self.assertIn(key, town)
        self.assertGreaterEqual(town["population"], 0)
        self.assertGreaterEqual(town["store_count_including_rivals"], 0)

        town_state = (GAME_ROOT / "scripts" / "domain" / "town_state.gd").read_text(
            encoding="utf-8"
        )
        land_value_policy = (
            GAME_ROOT / "scripts" / "domain" / "land_value_policy.gd"
        ).read_text(encoding="utf-8")
        demand_policy = (GAME_ROOT / "scripts" / "domain" / "demand_policy.gd").read_text(
            encoding="utf-8"
        )
        simulation = (GAME_ROOT / "scripts" / "vertical_slice_simulation.gd").read_text(
            encoding="utf-8"
        )
        smoke = (GAME_ROOT / "scripts" / "headless_smoke.gd").read_text(encoding="utf-8")

        # TownState mirrors reference_sim/conveni_sim/town.py: tracked state
        # only, no invented spatial/map simulation.
        self.assertIn("class_name TownState", town_state)
        self.assertIn("var population: int", town_state)
        self.assertIn("var store_count_including_rivals: int", town_state)

        # LandValuePolicy is a REMAKE_BALANCED_DEFAULT placeholder ported
        # from reference_sim/conveni_sim/remake_land_value.py, informational
        # only (no feature yet consumes it).
        self.assertIn("REMAKE_BALANCED_DEFAULT", land_value_policy)
        self.assertIn("func local_development_factor(town) -> float:", land_value_policy)
        self.assertIn("func time_inflation_factor(elapsed_years: float) -> float:", land_value_policy)
        self.assertIn("func current_land_price_yen(", land_value_policy)
        self.assertIn("informational only in this client", land_value_policy)

        # Rival dilution reuses reference_sim's confirmed constants
        # (remake_customer_share.py's RIVAL_DILUTION_PER_COMPETITOR /
        # MAX_RIVAL_DILUTION) but applies them to the whole expected-visitor
        # estimate rather than a 0-100 customer-share score: service/
        # security/cleaning stats exist since task #27 (store_value.gd) but
        # feed the monthly star rating, not a customer_share_percent
        # formula here, and assortment breadth still has no stat at all.
        self.assertIn("var rival_store_count: int", demand_policy)
        self.assertIn("const RIVAL_DILUTION_PER_COMPETITOR := 0.08", demand_policy)
        self.assertIn("const MAX_RIVAL_DILUTION := 0.6", demand_policy)
        self.assertIn("scope simplification", demand_policy)

        self.assertIn("town = TownStateScript.new(config[\"town\"])", simulation)
        self.assertIn(
            "demand.rival_store_count = max(0, town.store_count_including_rivals - 1)",
            simulation,
        )
        self.assertIn("BASE_LAND_PRICE_YEN := 20_000_000", simulation)
        self.assertIn('"land_value_yen":', simulation)

        # What is deliberately NOT implemented: no rival AI decision logic
        # (remake_rival_policy.py) is ported, since no rival-store entity
        # exists in Godot yet for such a decision to act upon.
        self.assertNotIn("RemakeBalancedRivalPolicy", simulation)
        self.assertNotIn("rival_policy", simulation.lower())

        self.assertIn("rival dilution must reduce expected arrivals", smoke)
        self.assertIn("rival dilution must be capped at MAX_RIVAL_DILUTION", smoke)
        self.assertIn("land_value_yen must match LandValuePolicy's formula", smoke)

    def test_chain_expansion_ports_confirmed_visitor_milestone_and_store_count_target(self):
        chain_visitor_milestone = (
            GAME_ROOT / "scripts" / "domain" / "chain_visitor_milestone.gd"
        ).read_text(encoding="utf-8")
        store_events = (GAME_ROOT / "scripts" / "domain" / "store_events.gd").read_text(
            encoding="utf-8"
        )
        simulation = (GAME_ROOT / "scripts" / "vertical_slice_simulation.gd").read_text(
            encoding="utf-8"
        )
        smoke = (GAME_ROOT / "scripts" / "headless_smoke.gd").read_text(encoding="utf-8")

        # ChainVisitorMilestone: CONFIRMED first-title evidence (a +100
        # popularity event every 10,000 cumulative chain visitors), ported
        # verbatim from visitor_milestone.py, not a REMAKE_BALANCED_DEFAULT
        # guess.
        self.assertIn("const THRESHOLD_STEP := 10000", chain_visitor_milestone)
        self.assertIn("const POPULARITY_GAIN := 100", chain_visitor_milestone)
        self.assertIn("func observe_total_visitors(", chain_visitor_milestone)
        self.assertIn("func pop_due(", chain_visitor_milestone)
        self.assertIn(
            "A skipped threshold (crossed without an exact observed multiple) is",
            chain_visitor_milestone,
        )

        # StoreEvents: CONFIRMED_OFFICIAL magazine/contest eligibility gate
        # and prize formula, ported verbatim; the "may or may not be
        # picked" draw itself is deliberately never rolled here.
        self.assertIn("CONFIRMED_OFFICIAL", store_events)
        self.assertIn("const TOWN_POPULATION_THRESHOLD := 10000", store_events)
        self.assertIn("const STORE_COUNT_THRESHOLD := 5", store_events)
        self.assertIn("const CONTEST_PRIZE_YEN_PER_STORE := 10000000", store_events)
        self.assertIn("func magazine_or_contest_event_is_eligible(", store_events)
        self.assertIn("func compute_contest_prize_yen(", store_events)

        # PLAYER_STORE_COUNT_SCENARIO_TARGET is explicitly tagged weaker
        # than REMAKE_BALANCED_DEFAULT (PROVISIONAL), since its own
        # community source (PROJECT_MEMORY.md section 14) is itself
        # unverified.
        self.assertIn("const PLAYER_STORE_COUNT_SCENARIO_TARGET := 10", simulation)
        self.assertIn("PROVISIONAL, not CONFIRMED_OFFICIAL", simulation)
        self.assertIn("func try_expand_chain() -> bool:", simulation)
        self.assertIn("func chain_expansion_cost_yen() -> int:", simulation)
        self.assertIn(
            "if player_store_count >= PLAYER_STORE_COUNT_SCENARIO_TARGET:", simulation
        )
        self.assertIn("clear_condition_met = true", simulation)
        # The expansion cost reuses task #26's land-value infrastructure
        # rather than inventing a second, unrelated price.
        self.assertIn(
            "_land_value_policy.current_land_price_yen(\n        BASE_LAND_PRICE_YEN, town,",
            simulation,
        )
        self.assertIn("func _observe_chain_visitor_milestone() -> void:", simulation)
        self.assertIn("func _fire_due_chain_visitor_milestones() -> void:", simulation)

        self.assertIn(
            "a successful chain expansion must increment player_store_count by exactly 1", smoke
        )
        self.assertIn(
            "clear_condition_met must be set once player_store_count reaches the scenario target",
            smoke,
        )
        self.assertIn(
            "a fired chain visitor milestone must apply exactly its configured popularity_gain",
            smoke,
        )

    def test_save_load_round_trips_progress_and_rejects_incompatible_saves(self):
        simulation = (GAME_ROOT / "scripts" / "vertical_slice_simulation.gd").read_text(
            encoding="utf-8"
        )
        save_service = (GAME_ROOT / "scripts" / "save_game_service.gd").read_text(
            encoding="utf-8"
        )
        economy_state = (GAME_ROOT / "scripts" / "domain" / "economy_state.gd").read_text(
            encoding="utf-8"
        )
        inventory_catalog = (
            GAME_ROOT / "scripts" / "domain" / "inventory_catalog.gd"
        ).read_text(encoding="utf-8")
        store_layout = (GAME_ROOT / "scripts" / "domain" / "store_layout.gd").read_text(
            encoding="utf-8"
        )
        smoke = (GAME_ROOT / "scripts" / "headless_smoke.gd").read_text(encoding="utf-8")

        self.assertIn("func save_state() -> Dictionary:", simulation)
        self.assertIn("func load_state(data: Dictionary) -> bool:", simulation)
        # An incompatible save (wrong scenario/schema) is an expected,
        # recoverable rejection (returns false), not a crash.
        self.assertIn('if str(data.get("scenario_id", "")) != str(config["scenario_id"]):', simulation)
        self.assertIn('if int(data.get("config_schema_version", -1)) != int(config["schema_version"]):', simulation)

        self.assertIn("class_name SaveGameService", save_service)
        self.assertIn("func save_to_path(", save_service)
        self.assertIn("func load_from_path(", save_service)
        self.assertIn('const DEFAULT_SAVE_PATH := "user://saves/vertical_slice_save.json"', save_service)

        self.assertIn("func snapshot() -> Dictionary:", economy_state)
        self.assertIn("func restore_snapshot(data: Dictionary) -> void:", economy_state)
        self.assertIn("func snapshot() -> Array:", inventory_catalog)
        self.assertIn("func restore_snapshot(snapshot_data: Array) -> void:", inventory_catalog)
        self.assertIn("func fixture_snapshot_is_valid(snapshot: Array) -> bool:", store_layout)

        # Deliberately not restored: mid-visit customer/staff walk state --
        # both come back to whatever a fresh reset() already produces.
        self.assertIn("Deliberately not saved/restored", simulation)

        self.assertIn(
            "a loaded simulation must restore the exact saved cash", smoke
        )
        self.assertIn(
            "loading a save with a different scenario_id must be rejected", smoke
        )
        self.assertIn(
            "a save file round trip must preserve the exact saved cash", smoke
        )

    def test_store_rating_ports_confirmed_guide_thresholds_into_the_monthly_loop(self):
        store = self.config["store"]
        self.assertIn("size_tier", store)
        for member in self.config["staff"]["members"]:
            for key in ("service_skill", "security_skill", "cleaning_skill"):
                self.assertIn(key, member)
                self.assertGreaterEqual(member[key], 0)

        store_rating = (GAME_ROOT / "scripts" / "domain" / "store_rating.gd").read_text(
            encoding="utf-8"
        )
        store_value = (GAME_ROOT / "scripts" / "domain" / "store_value.gd").read_text(
            encoding="utf-8"
        )
        staff_state = (GAME_ROOT / "scripts" / "domain" / "staff_state.gd").read_text(
            encoding="utf-8"
        )
        simulation = (GAME_ROOT / "scripts" / "vertical_slice_simulation.gd").read_text(
            encoding="utf-8"
        )
        smoke = (GAME_ROOT / "scripts" / "headless_smoke.gd").read_text(encoding="utf-8")

        # store_rating.gd/store_value.gd are CONFIRMED_OFFICIAL ports of the
        # guide's own published table, not a REMAKE_BALANCED_DEFAULT guess.
        self.assertIn("CONFIRMED_OFFICIAL", store_rating)
        self.assertIn("CONFIRMED_OFFICIAL", store_value)
        self.assertIn("func star_rank_for_internal_value(internal_value: int) -> int:", store_rating)
        self.assertIn("func evaluate_monthly_rating_change(", store_rating)
        self.assertIn('"min_service": 60, "min_security": 75, "min_cleaning": 85, "min_sales_yen": 5000000', store_rating)
        self.assertIn("func compute_service_value(", store_value)
        self.assertIn("func compute_security_value(", store_value)
        self.assertIn("func compute_cleaning_value(", store_value)
        self.assertIn('"small": 1.5,', store_value)
        self.assertIn('"medium": 1.65,', store_value)
        self.assertIn('"large": 1.8,', store_value)

        # No skill-growth system is ported yet: the three fields are static
        # REMAKE_BALANCED_DEFAULT config values on StaffState.
        self.assertIn("var service_skill: int", staff_state)
        self.assertIn("var security_skill: int", staff_state)
        self.assertIn("var cleaning_skill: int", staff_state)
        self.assertIn("REMAKE_BALANCED_DEFAULT", staff_state)

        # Wired into the monthly game loop, not just defined standalone.
        self.assertIn("func _evaluate_store_rating(monthly_sales_yen: int) -> void:", simulation)
        self.assertIn("_evaluate_store_rating(monthly_sales_yen)", simulation)
        self.assertIn('"internal_rating_value": internal_rating_value,', simulation)
        self.assertIn('"star_rating": star_rating,', simulation)
        # price_change_pct is always 0: no price-setting mechanic exists yet.
        self.assertIn(
            "_store_rating.evaluate_monthly_rating_change(\n        internal_rating_value, 0,",
            simulation,
        )

        # What is deliberately NOT implemented: the police-box/fire-station
        # security facility bonus (no such fixtures/spatial search exist
        # yet) and the per-event rating deltas (angry customer/shoplifting/
        # donation), since the underlying trigger events aren't wired into
        # this client either.
        self.assertNotIn("facility_coverage", store_value)
        self.assertNotIn("police_box", simulation.lower())

        self.assertIn("star_rank_for_internal_value must match the guide's confirmed breakpoints", smoke)
        self.assertIn("exactly one store_rating_evaluated event must be recorded at month end", smoke)

    def test_named_staff_candidate_roster_ports_all_35_confirmed_official_entries(self):
        from conveni_sim.baseline_data import STAFF_CANDIDATES

        self.assertIn("staff_candidates", self.config)
        self.assertIn("staff_candidates_evidence_note", self.config)
        self.assertIn("CONFIRMED_OFFICIAL", self.config["staff_candidates_evidence_note"])

        candidates = self.config["staff_candidates"]
        self.assertEqual(len(candidates), 35)
        self.assertEqual(len(candidates), len(STAFF_CANDIDATES))

        ids = [entry["candidate_id"] for entry in candidates]
        self.assertEqual(len(ids), len(set(ids)))

        # Every candidate ports digit-for-digit from reference_sim's own
        # STAFF_CANDIDATES tuple, not a re-transcription that could drift.
        reference_by_id = {c.id: c for c in STAFF_CANDIDATES}
        self.assertEqual(set(ids), set(reference_by_id.keys()))
        for entry in candidates:
            reference = reference_by_id[entry["candidate_id"]]
            self.assertEqual(entry["display_name"], reference.display_name.value)
            self.assertEqual(entry["age_years"], reference.starting_age_years.value)
            self.assertEqual(
                entry["salary_yen_per_day_24h"], reference.salary_yen_per_day_24h.value
            )
            for field, value_obj in (
                ("stamina", reference.stamina),
                ("academic_background", reference.academic_background),
                ("agility", reference.agility),
                ("sociability", reference.sociability),
                ("education", reference.education),
                ("service_skill", reference.service_skill),
                ("register_skill", reference.register_skill),
                ("cleaning_skill", reference.cleaning_skill),
                ("replenishment_skill", reference.replenishment_skill),
                ("service_skill_growth_ceiling", reference.service_skill_growth_ceiling),
                ("register_skill_growth_ceiling", reference.register_skill_growth_ceiling),
                ("cleaning_skill_growth_ceiling", reference.cleaning_skill_growth_ceiling),
                (
                    "replenishment_skill_growth_ceiling",
                    reference.replenishment_skill_growth_ceiling,
                ),
                ("security_skill_growth_ceiling", reference.security_skill_growth_ceiling),
            ):
                self.assertEqual(entry[field], value_obj.value)
            # security_skill is the one field allowed to be null (exactly
            # one candidate's printed value could not be read with
            # confidence), never guessed to fill the gap.
            expected_security = (
                reference.security_skill.value if reference.security_skill is not None else None
            )
            self.assertEqual(entry["security_skill"], expected_security)
        self.assertEqual(
            sum(1 for entry in candidates if entry["security_skill"] is None), 1
        )

        # The two active roster slots now bind to real named candidates
        # instead of a flat, identical placeholder repeated on both.
        members = self.config["staff"]["members"]
        self.assertEqual(len(members), 2)
        candidates_by_id = {entry["candidate_id"]: entry for entry in candidates}
        for member in members:
            self.assertIn("candidate_id", member)
            self.assertIn(member["candidate_id"], candidates_by_id)
            bound = candidates_by_id[member["candidate_id"]]
            for key in (
                "service_skill",
                "security_skill",
                "cleaning_skill",
                "register_skill",
                "replenishment_skill",
            ):
                self.assertEqual(member[key], bound[key])
        member_candidate_ids = [member["candidate_id"] for member in members]
        self.assertEqual(len(member_candidate_ids), len(set(member_candidate_ids)))

        staff_state = (GAME_ROOT / "scripts" / "domain" / "staff_state.gd").read_text(
            encoding="utf-8"
        )
        self.assertIn("task #32", staff_state)

    def test_register_skill_checkout_timing_is_a_tagged_remake_default(self):
        from conveni_sim.baseline_data import STAFF_CANDIDATES

        checkout_timing = (
            GAME_ROOT / "scripts" / "domain" / "checkout_timing.gd"
        ).read_text(encoding="utf-8")
        staff_state = (GAME_ROOT / "scripts" / "domain" / "staff_state.gd").read_text(
            encoding="utf-8"
        )
        simulation = (GAME_ROOT / "scripts" / "vertical_slice_simulation.gd").read_text(
            encoding="utf-8"
        )

        # The evidence note is explicit that this scaling shape is invented
        # by this project, not a recovered original formula -- the research
        # note it cites confirms only a qualitative effect.
        self.assertIn("REMAKE_BALANCED_DEFAULT", checkout_timing)
        self.assertIn("not a recovered original formula", checkout_timing)
        self.assertIn("func required_ticks(register_skill: int, reference_ticks: int) -> int:", checkout_timing)
        self.assertIn("const MIN_CHECKOUT_TICKS := 1", checkout_timing)

        # REFERENCE_REGISTER_SKILL must actually be the median of the ported
        # 35-candidate roster, not an arbitrary number.
        register_skills = sorted(c.register_skill.value for c in STAFF_CANDIDATES)
        median = register_skills[len(register_skills) // 2]
        self.assertEqual(len(register_skills) % 2, 1)
        self.assertIn(f"const REFERENCE_REGISTER_SKILL := {median}", checkout_timing)

        self.assertIn("var register_skill: int", staff_state)
        self.assertIn('register_skill = int(staff_config.get("register_skill", 0))', staff_state)

        # Wired into the actual checkout-start transition, not just defined
        # standalone.
        self.assertIn("const CheckoutTimingScript := preload", simulation)
        # Task #36 moved this assignment out of the per-customer step() match
        # statement into _dispatch_checkout_queue(), the single choke point
        # that now hands the shared checkout fixture to the next queued
        # customer (concurrent customers no longer let every customer start
        # checkout the instant they arrive).
        self.assertIn(
            "customer.checkout_ticks_remaining = _checkout_timing.required_ticks(\n"
            "        checkout_staff.register_skill, _checkout_ticks\n"
            "    )",
            simulation,
        )

        # checkout_ticks itself is documented as reinterpreted, not silently
        # redefined without a trace.
        self.assertIn("checkout_ticks_evidence_note", self.config["simulation"])
        self.assertIn(
            "REFERENCE_REGISTER_SKILL", self.config["simulation"]["checkout_ticks_evidence_note"]
        )

        smoke = (GAME_ROOT / "scripts" / "headless_smoke.gd").read_text(encoding="utf-8")
        self.assertIn(
            "required_ticks must return reference_ticks unchanged exactly at REFERENCE_REGISTER_SKILL",
            smoke,
        )
        self.assertIn("required_ticks must never fall below MIN_CHECKOUT_TICKS", smoke)

    def test_replenishment_skill_restock_timing_is_a_tagged_remake_default(self):
        from conveni_sim.baseline_data import STAFF_CANDIDATES

        restock_timing = (
            GAME_ROOT / "scripts" / "domain" / "restock_timing.gd"
        ).read_text(encoding="utf-8")
        staff_state = (GAME_ROOT / "scripts" / "domain" / "staff_state.gd").read_text(
            encoding="utf-8"
        )
        simulation = (GAME_ROOT / "scripts" / "vertical_slice_simulation.gd").read_text(
            encoding="utf-8"
        )

        # The evidence note is explicit that this scaling shape is invented
        # by this project (reusing CheckoutTiming's shape), not a recovered
        # original formula -- the research notes it cites confirm only a
        # qualitative effect.
        self.assertIn("REMAKE_BALANCED_DEFAULT", restock_timing)
        self.assertIn("not a recovered original formula", restock_timing)
        self.assertIn(
            "func required_ticks(replenishment_skill: int, reference_ticks: int) -> int:",
            restock_timing,
        )
        self.assertIn("const MIN_RESTOCK_TICKS := 1", restock_timing)

        # REFERENCE_REPLENISHMENT_SKILL must actually be the median of the
        # ported 35-candidate roster, not an arbitrary number.
        replenishment_skills = sorted(c.replenishment_skill.value for c in STAFF_CANDIDATES)
        median = replenishment_skills[len(replenishment_skills) // 2]
        self.assertEqual(len(replenishment_skills) % 2, 1)
        self.assertIn(f"const REFERENCE_REPLENISHMENT_SKILL := {median}", restock_timing)

        self.assertIn("var replenishment_skill: int", staff_state)
        self.assertIn(
            'replenishment_skill = int(staff_config.get("replenishment_skill", 0))', staff_state
        )

        # Wired into the actual restock-start transition, not just defined
        # standalone.
        self.assertIn("const RestockTimingScript := preload", simulation)
        self.assertIn(
            "staff_member.restock_ticks_remaining = _restock_timing.required_ticks(\n"
            "                        staff_member.replenishment_skill, _restock_ticks\n"
            "                    )",
            simulation,
        )

        # restock_ticks itself is documented as reinterpreted, not silently
        # redefined without a trace.
        self.assertIn("restock_ticks_evidence_note", self.config["simulation"])
        self.assertIn(
            "REFERENCE_REPLENISHMENT_SKILL", self.config["simulation"]["restock_ticks_evidence_note"]
        )

        smoke = (GAME_ROOT / "scripts" / "headless_smoke.gd").read_text(encoding="utf-8")
        self.assertIn(
            "required_ticks must return reference_ticks unchanged exactly at "
            "REFERENCE_REPLENISHMENT_SKILL",
            smoke,
        )
        self.assertIn("required_ticks must never fall below MIN_RESTOCK_TICKS", smoke)

    def test_customer_share_percent_is_wired_into_monthly_store_rating(self):
        from conveni_sim import remake_customer_share

        customer_share = (
            GAME_ROOT / "scripts" / "domain" / "customer_share.gd"
        ).read_text(encoding="utf-8")
        simulation = (GAME_ROOT / "scripts" / "vertical_slice_simulation.gd").read_text(
            encoding="utf-8"
        )
        smoke = (GAME_ROOT / "scripts" / "headless_smoke.gd").read_text(encoding="utf-8")

        # The evidence note is explicit that this weighted combination is
        # invented by this project's reference_sim source, not a recovered
        # original formula, and that this port mirrors it field-for-field.
        self.assertIn("REMAKE_BALANCED_DEFAULT", customer_share)
        self.assertIn("not a recovered original formula", customer_share)
        self.assertIn(
            "func compute_customer_share_percent(", customer_share
        )

        # The six weights, the assortment saturation point, and the
        # full-day-minutes constant must actually match
        # remake_customer_share.py's own values, not just resemble them.
        self.assertIn(
            f"const POPULARITY_WEIGHT := {remake_customer_share.POPULARITY_WEIGHT}", customer_share
        )
        self.assertIn(
            f"const SERVICE_WEIGHT := {remake_customer_share.SERVICE_WEIGHT}", customer_share
        )
        self.assertIn(
            f"const CLEANING_WEIGHT := {remake_customer_share.CLEANING_WEIGHT}", customer_share
        )
        self.assertIn(
            f"const SECURITY_WEIGHT := {remake_customer_share.SECURITY_WEIGHT}", customer_share
        )
        self.assertIn(
            f"const ASSORTMENT_WEIGHT := {remake_customer_share.ASSORTMENT_WEIGHT}", customer_share
        )
        self.assertIn(
            f"const HOURS_WEIGHT := {remake_customer_share.HOURS_WEIGHT}", customer_share
        )
        self.assertEqual(
            sum((
                remake_customer_share.POPULARITY_WEIGHT,
                remake_customer_share.SERVICE_WEIGHT,
                remake_customer_share.CLEANING_WEIGHT,
                remake_customer_share.SECURITY_WEIGHT,
                remake_customer_share.ASSORTMENT_WEIGHT,
                remake_customer_share.HOURS_WEIGHT,
            )),
            1.0,
        )
        self.assertIn(
            f"const ASSORTMENT_SATURATION_PRODUCT_COUNT := "
            f"{remake_customer_share.ASSORTMENT_SATURATION_PRODUCT_COUNT}",
            customer_share,
        )
        self.assertEqual(remake_customer_share.FULL_DAY_MINUTES, 24 * 60)
        self.assertIn("const FULL_DAY_MINUTES := 24 * 60", customer_share)

        # Deliberately not ported: the Python source's weather/rival dilution
        # and its "unknown factor" renormalization branch, since this client
        # already applies weather/rival dilution downstream in demand_policy.gd
        # and always knows all six factors by the time this is called.
        self.assertNotIn("BAD_WEATHER_PENALTY", customer_share)
        self.assertNotIn("RIVAL_DILUTION_PER_COMPETITOR", customer_share)

        # Wired into the actual monthly store-rating evaluation, not just
        # defined standalone, and its output overwrites demand.customer_share_percent.
        self.assertIn("const CustomerShareScript := preload", simulation)
        self.assertIn(
            "demand.customer_share_percent = float(_customer_share.compute_customer_share_percent(",
            simulation,
        )
        self.assertIn("inventory.products.size()", simulation)
        self.assertIn("demand.opening_minutes_per_day", simulation)

        # demand.customer_share_percent's config value is documented as only
        # an initial value, now overwritten monthly -- not silently
        # redefined without a trace.
        self.assertIn(
            "task #44", self.config["demand"]["evidence_note"]
        )
        self.assertIn(
            "CustomerShare.compute_customer_share_percent()", self.config["demand"]["evidence_note"]
        )

        self.assertIn(
            "compute_customer_share_percent must score 100 when every factor is maxed out", smoke
        )
        self.assertIn(
            "compute_customer_share_percent must score 0 when every factor is at its floor", smoke
        )
        self.assertIn(
            "customer_share_percent must be recomputed from CustomerShare.compute_customer_share_percent()",
            smoke,
        )

    def test_promotions_port_confirmed_reference_sim_timing_and_apply_at_trigger(self):
        promotions = self.config["promotions"]
        promotion_ids = [entry["promotion_id"] for entry in promotions]
        self.assertEqual(len(promotion_ids), len(set(promotion_ids)))
        self.assertIn("direct_mail", promotion_ids)
        for entry in promotions:
            for key in ("promotion_id", "cost_yen", "popularity_gain", "trigger_day", "trigger_hour"):
                self.assertIn(key, entry)
            self.assertGreater(entry["cost_yen"], 0)
            self.assertGreater(entry["popularity_gain"], 0)
            self.assertTrue(1 <= entry["trigger_day"] <= 4)
            self.assertTrue(0 <= entry["trigger_hour"] <= 23)

        direct_mail = next(entry for entry in promotions if entry["promotion_id"] == "direct_mail")
        self.assertEqual(direct_mail["cost_yen"], 100000)
        self.assertEqual(direct_mail["popularity_gain"], 12)
        self.assertEqual(direct_mail["trigger_day"], 2)
        self.assertEqual(direct_mail["trigger_hour"], 10)

        simulation = (GAME_ROOT / "scripts" / "vertical_slice_simulation.gd").read_text(
            encoding="utf-8"
        )
        smoke = (GAME_ROOT / "scripts" / "headless_smoke.gd").read_text(encoding="utf-8")

        self.assertIn("func try_purchase_promotion(promotion_id: String) -> bool:", simulation)
        self.assertIn("func _fire_due_promotions() -> void:", simulation)
        self.assertIn("func _fire_promotion(scheduled: Dictionary) -> void:", simulation)
        self.assertIn("_promotions_used_this_month", simulation)
        self.assertIn(
            "a promotion's cost must not be charged until its scheduled event fires", smoke
        )
        self.assertIn(
            "scheduling the same promotion method twice in one month must be rejected", smoke
        )
        self.assertIn(
            "a fired promotion must apply exactly its configured popularity_gain", smoke
        )
        self.assertIn(
            "a fired promotion must deduct exactly its configured cost at trigger time", smoke
        )
        self.assertIn(
            "scheduling a promotion after its trigger moment has already passed this month must be rejected",
            smoke,
        )

    def test_permits_and_product_procurement_port_confirmed_reference_sim_data(self):
        permits = self.config["permits"]
        permit_ids = [entry["permit_id"] for entry in permits]
        self.assertEqual(len(permit_ids), len(set(permit_ids)))
        self.assertIn("tobacco", permit_ids)
        for entry in permits:
            for key in ("permit_id", "fee_yen"):
                self.assertIn(key, entry)
            self.assertGreater(entry["fee_yen"], 0)

        product_catalog = self.config["product_catalog"]
        catalog_ids = [entry["catalog_id"] for entry in product_catalog]
        self.assertEqual(len(catalog_ids), len(set(catalog_ids)))
        for entry in product_catalog:
            for key in ("catalog_id", "sale_price_yen", "restock_unit_cost_yen", "initial_stock_units"):
                self.assertIn(key, entry)
            self.assertGreater(entry["sale_price_yen"], 0)
            self.assertGreaterEqual(entry["restock_unit_cost_yen"], 0)
            self.assertGreater(entry["initial_stock_units"], 0)

        tobacco_fixture = next(
            entry for entry in self.config["fixture_catalog"] if entry["catalog_id"] == "small_tobacco_vending"
        )
        self.assertEqual(tobacco_fixture.get("required_permit_id"), "tobacco")

        inventory_catalog = (GAME_ROOT / "scripts" / "domain" / "inventory_catalog.gd").read_text(
            encoding="utf-8"
        )
        simulation = (GAME_ROOT / "scripts" / "vertical_slice_simulation.gd").read_text(
            encoding="utf-8"
        )
        smoke = (GAME_ROOT / "scripts" / "headless_smoke.gd").read_text(encoding="utf-8")

        self.assertIn("func add_product(product_config: Dictionary) -> bool:", inventory_catalog)
        self.assertIn("func try_purchase_permit(permit_id: String) -> bool:", simulation)
        self.assertIn("func has_permit(permit_id: String) -> bool:", simulation)
        self.assertIn("func try_procure_product(", simulation)
        self.assertIn(
            "a permit-gated fixture purchase must be rejected without the permit", smoke
        )
        self.assertIn(
            "permit-gated product procurement must be rejected without the permit", smoke
        )
        self.assertIn(
            "a permit-gated fixture purchase must be accepted once the permit is held", smoke
        )
        self.assertIn(
            "permit-gated product procurement must be accepted once the permit is held", smoke
        )
        self.assertIn(
            "procuring a second product onto an already-occupied fixture must be rejected", smoke
        )

    def test_product_category_catalog_expansion_ports_confirmed_reference_sim_pricing(self):
        from conveni_sim.baseline_data import PRODUCT_CATEGORY_PRICING

        catalog_by_id = {entry["catalog_id"]: entry for entry in self.config["product_catalog"]}
        reference_by_id = {category.id: category for category in PRODUCT_CATEGORY_PRICING}

        # "cash" (現金) is the guide's own zero-margin instrument row, tied to
        # a キャッシュディスペンサー (cash dispenser) fixture -- an ATM-like
        # mechanic distinct from a restockable shelf product, and no such
        # fixture/mechanic exists in this client. It is deliberately excluded
        # from this catalog port rather than treated as an ordinary product.
        self.assertNotIn("cash", catalog_by_id)

        ported_ids = set(catalog_by_id) - {"tobacco"}
        expected_ids = set(reference_by_id) - {"cash", "tobacco"}
        self.assertEqual(ported_ids, expected_ids)

        permit_ids = {entry["permit_id"] for entry in self.config["permits"]}
        for catalog_id, entry in catalog_by_id.items():
            reference = reference_by_id[catalog_id]

            # initial_stock_units must be this category's own CONFIRMED_
            # OFFICIAL max_capacity, not an arbitrary flat constant (task
            # #42 correction of task #39's original flat "10" for every
            # category regardless of scale): the number itself has to be
            # traceable to real per-category evidence, an analogy-based
            # derivation, even though "start at full capacity" as the rule
            # for choosing that number is still this project's own
            # REMAKE_BALANCED_DEFAULT assumption.
            self.assertEqual(entry["initial_stock_units"], reference.max_capacity.value)

            if catalog_id == "tobacco":
                continue
            expected_price = reference.standard_retail_price_yen.value
            expected_cost = expected_price - reference.profit_per_unit_yen.value
            self.assertEqual(entry["sale_price_yen"], expected_price)
            self.assertEqual(entry["restock_unit_cost_yen"], expected_cost)
            self.assertIn("CONFIRMED_OFFICIAL", entry["evidence_note"])
            self.assertIn("REMAKE_BALANCED_DEFAULT", entry["evidence_note"])
            required_permit_id = entry.get("required_permit_id")
            if required_permit_id is not None:
                self.assertIn(required_permit_id, permit_ids)

        # Only alcohol/medicine have a corresponding permit ported into this
        # file (see test_permits_and_product_procurement_port_confirmed_
        # reference_sim_data above); every other category is deliberately
        # left unrestricted rather than inventing a permit requirement the
        # guide does not state.
        self.assertEqual(catalog_by_id["alcohol"].get("required_permit_id"), "alcohol")
        self.assertEqual(catalog_by_id["medicine"].get("required_permit_id"), "medicine")
        for catalog_id, entry in catalog_by_id.items():
            if catalog_id in ("tobacco", "alcohol", "medicine"):
                continue
            self.assertNotIn("required_permit_id", entry)

    def test_fixture_purchase_catalog_ports_confirmed_reference_sim_prices(self):
        catalog = self.config["fixture_catalog"]
        self.assertGreaterEqual(len(catalog), 1)
        catalog_ids = [entry["catalog_id"] for entry in catalog]
        self.assertEqual(len(catalog_ids), len(set(catalog_ids)))
        for entry in catalog:
            for key in ("catalog_id", "kind", "footprint_tiles", "purchase_price_yen"):
                self.assertIn(key, entry)
            self.assertGreater(entry["purchase_price_yen"], 0)
            self.assertEqual(len(entry["footprint_tiles"]), 2)

        layout = (GAME_ROOT / "scripts" / "domain" / "store_layout.gd").read_text(
            encoding="utf-8"
        )
        simulation = (GAME_ROOT / "scripts" / "vertical_slice_simulation.gd").read_text(
            encoding="utf-8"
        )
        smoke = (GAME_ROOT / "scripts" / "headless_smoke.gd").read_text(encoding="utf-8")

        self.assertIn("func try_add_fixture(fixture_config: Dictionary) -> bool:", layout)
        self.assertIn("func try_purchase_fixture(", simulation)
        self.assertIn("_fixture_catalog", simulation)
        self.assertIn("_required_routes_are_reachable() or not _all_staff_are_walkable()", simulation)
        self.assertIn("a valid, affordable fixture purchase must be accepted", smoke)
        self.assertIn("a duplicate fixture instance id must be rejected", smoke)
        self.assertIn("an unknown fixture catalog id must be rejected", smoke)
        self.assertIn("purchasing on top of an existing fixture must be rejected", smoke)
        self.assertIn(
            "a fixture purchase costing more than available cash must be rejected", smoke
        )

    def test_parking_fixtures_port_confirmed_reference_sim_data(self):
        from conveni_sim.baseline_data import FIXTURES

        catalog_by_id = {entry["catalog_id"]: entry for entry in self.config["fixture_catalog"]}
        reference_by_id = {f.id: f for f in FIXTURES}
        for catalog_id in ("parking_ground", "parking_two_story", "parking_tower"):
            self.assertIn(catalog_id, catalog_by_id)
            entry = catalog_by_id[catalog_id]
            reference = reference_by_id[catalog_id]
            self.assertEqual(entry["kind"], "parking")
            self.assertEqual(
                entry["footprint_tiles"], list(reference.footprint.value)
            )
            self.assertEqual(
                entry["purchase_price_yen"], reference.purchase_price_yen.value
            )
            self.assertEqual(
                entry["maintenance_yen_per_day"], reference.maintenance_yen_per_day.value
            )
            self.assertEqual(
                entry["parking_capacity"], reference.parking_capacity.value
            )
            self.assertIs(entry["blocks_pedestrian"], reference.blocks_pedestrian.value)
            self.assertEqual(entry["placement"], reference.placement.value)
            self.assertIn("CONFIRMED", entry["evidence_note"])

        layout = (GAME_ROOT / "scripts" / "domain" / "store_layout.gd").read_text(
            encoding="utf-8"
        )
        store_view = (GAME_ROOT / "scripts" / "store_view.gd").read_text(encoding="utf-8")
        smoke = (GAME_ROOT / "scripts" / "headless_smoke.gd").read_text(encoding="utf-8")

        # No kind-specific carve-out was added to StoreLayout: every fixture
        # already blocks its full footprint unconditionally regardless of
        # kind, so parking's confirmed blocks_pedestrian fact requires no
        # new placement mechanic, only the informational catalog field
        # above.
        self.assertIn("for fixture in fixtures:", layout)
        self.assertIn('elif fixture["kind"] == "parking":', store_view)
        self.assertIn("a valid parking fixture purchase must be accepted", smoke)
        self.assertIn(
            "a placed parking fixture's footprint must not be walkable, same as any other fixture",
            smoke,
        )

    def test_shelf_fixture_catalog_expansion_ports_confirmed_reference_sim_data(self):
        from conveni_sim.baseline_data import FIXTURES

        catalog_by_id = {entry["catalog_id"]: entry for entry in self.config["fixture_catalog"]}
        reference_by_id = {f.id: f for f in FIXTURES}

        # Mechanics this client does not implement -- multi-register
        # checkout routing, a copier/print service, an ATM-like cash
        # dispenser, and a staff break/rest room -- are deliberately
        # excluded from this port, the same reasoning task #39 used to
        # exclude the "cash" product category.
        excluded_ids = {
            "register_1", "register_2", "register_3", "register_4",
            "copier_a", "copier_b", "indoor_dispenser",
            "break_room_1", "break_room_2", "vending_machine",
        }
        for excluded_id in excluded_ids:
            self.assertNotIn(excluded_id, catalog_by_id)

        # Every other reference_sim fixture not already in the catalog
        # before this task (the 3 amenity + 3 parking + 2 shelf entries)
        # must now be ported.
        pre_existing_ids = {
            "potted_plant", "bench", "fountain",
            "parking_ground", "parking_two_story", "parking_tower",
            "small_ambient_shelf", "small_tobacco_vending",
        }
        expected_new_ids = set(reference_by_id) - excluded_ids - pre_existing_ids
        actual_new_ids = set(catalog_by_id) - pre_existing_ids
        self.assertEqual(actual_new_ids, expected_new_ids)

        for catalog_id in actual_new_ids:
            entry = catalog_by_id[catalog_id]
            reference = reference_by_id[catalog_id]
            self.assertEqual(entry["kind"], "shelf")
            self.assertEqual(entry["footprint_tiles"], list(reference.footprint.value))
            self.assertEqual(entry["purchase_price_yen"], reference.purchase_price_yen.value)
            self.assertEqual(
                entry["maintenance_yen_per_day"], reference.maintenance_yen_per_day.value
            )
            self.assertIn("CONFIRMED_OFFICIAL", entry["evidence_note"])
            required_permit_id = entry.get("required_permit_id")
            if required_permit_id is not None:
                self.assertIn(
                    required_permit_id,
                    [permit["permit_id"] for permit in self.config["permits"]],
                )

        # Only the tobacco-dedicated vending fixture is permit-gated, same
        # precedent as the existing small_tobacco_vending entry.
        self.assertEqual(catalog_by_id["large_tobacco_vending"].get("required_permit_id"), "tobacco")
        for catalog_id in actual_new_ids - {"large_tobacco_vending"}:
            self.assertNotIn("required_permit_id", catalog_by_id[catalog_id])

        # No kind-specific carve-out is needed: main.gd's fixture catalog UI
        # and try_purchase_fixture are already fully generic over kind, and
        # any fixture without its own store_view.gd branch already falls
        # back to the existing default blue "SHELF" rendering, which is
        # correct for every entry added here (they are all kind="shelf").
        store_view = (GAME_ROOT / "scripts" / "store_view.gd").read_text(encoding="utf-8")
        self.assertIn('var label := "SHELF"', store_view)

    def test_fixture_capacity_and_compatibility_are_wired_into_procurement(self):
        from conveni_sim.baseline_data import FIXTURES

        catalog_by_id = {entry["catalog_id"]: entry for entry in self.config["fixture_catalog"]}
        reference_by_id = {f.id: f for f in FIXTURES}
        product_catalog_ids = {entry["catalog_id"] for entry in self.config["product_catalog"]}

        shelf_ids = [
            catalog_id for catalog_id, entry in catalog_by_id.items() if entry["kind"] == "shelf"
        ]
        self.assertEqual(len(shelf_ids), 29)

        for catalog_id in shelf_ids:
            entry = catalog_by_id[catalog_id]
            reference = reference_by_id[catalog_id]
            self.assertEqual(entry["capacity"], reference.capacity.value)
            self.assertEqual(
                entry["compatible_product_categories"],
                list(reference.compatible_product_categories.value),
            )
            self.assertIn("CONFIRMED_OFFICIAL", entry["evidence_note"])
            # Every compatible category this fixture lists must itself be a
            # real product_catalog entry, or the compatibility check would
            # silently accept a category this client never lets the player
            # procure in the first place.
            for category in entry["compatible_product_categories"]:
                self.assertIn(category, product_catalog_ids)

        # copy_paper/parcel_delivery_form are real product_catalog entries
        # (task #39) but reference_sim's own compatible_fixtures_text for
        # them names コピー機/レジ (copier/register), both fixtures this
        # client deliberately excluded (task #41) since neither mechanic
        # exists here. No shelf-kind fixture lists them as compatible,
        # which is the correct, evidence-consistent result of that earlier
        # exclusion, not a gap in this task.
        all_compatible = {
            category
            for entry in catalog_by_id.values()
            for category in entry.get("compatible_product_categories", [])
        }
        self.assertNotIn("copy_paper", all_compatible)
        self.assertNotIn("parcel_delivery_form", all_compatible)

        # No amenity/parking/checkout entry carries either field: they
        # never hold products, and reference_sim's own FIXTURES agrees
        # (capacity/compatible_product_categories are None for all of them).
        for catalog_id, entry in catalog_by_id.items():
            if entry["kind"] != "shelf":
                self.assertNotIn("capacity", entry)
                self.assertNotIn("compatible_product_categories", entry)

        simulation = (GAME_ROOT / "scripts" / "vertical_slice_simulation.gd").read_text(
            encoding="utf-8"
        )
        smoke = (GAME_ROOT / "scripts" / "headless_smoke.gd").read_text(encoding="utf-8")

        # Wired into the actual procurement transition, not just present as
        # data: a fixture without its own catalog_id (the prototype
        # scenario's shelf-1/shelf-2) has no confirmed data to check and
        # stays unrestricted rather than inventing a rule for it.
        self.assertIn(
            "if fixture_catalog_entry.has(\"compatible_product_categories\"):", simulation
        )
        self.assertIn("if not compatible_categories.has(catalog_id):", simulation)
        self.assertIn('if fixture_catalog_entry.has("capacity"):', simulation)
        self.assertIn(
            "initial_stock_units = min(initial_stock_units, int(fixture_catalog_entry[\"capacity\"]))",
            simulation,
        )

        self.assertIn(
            "a procured product must start with its configured initial stock, "
            "capped at the fixture's own capacity",
            smoke,
        )
        self.assertIn(
            "procuring a product onto a fixture whose compatible_product_categories "
            "excludes it must be rejected",
            smoke,
        )
        self.assertIn(
            "procuring a product a fixture's compatible_product_categories does "
            "include must be accepted",
            smoke,
        )

    def test_fixture_maintenance_is_charged_daily(self):
        from conveni_sim.baseline_data import FIXTURES

        reference_by_id = {f.id: f for f in FIXTURES}

        # Every fixture_catalog entry's own maintenance_yen_per_day is
        # CONFIRMED_OFFICIAL, matching reference_sim's FIXTURES exactly --
        # this task only changes whether it's consumed, not the values.
        for entry in self.config["fixture_catalog"]:
            if "maintenance_yen_per_day" not in entry:
                # small_ambient_shelf/small_tobacco_vending never carried
                # this field (predates this task, tasks #32/#41's own
                # scope), so there is nothing here for them to be charged.
                continue
            reference = reference_by_id[entry["catalog_id"]]
            self.assertEqual(
                entry["maintenance_yen_per_day"], reference.maintenance_yen_per_day.value
            )

        simulation = (GAME_ROOT / "scripts" / "vertical_slice_simulation.gd").read_text(
            encoding="utf-8"
        )
        smoke = (GAME_ROOT / "scripts" / "headless_smoke.gd").read_text(encoding="utf-8")

        # Wired into the actual day-boundary transition, not just present
        # as data. A fixture with no fixture_catalog origin (shelf-1/
        # shelf-2/checkout-1, from before the catalog system existed) has
        # no confirmed maintenance figure to charge and is skipped, same
        # precedent as the compatibility/capacity check task #45 added.
        self.assertIn("func _apply_daily_fixture_maintenance() -> void:", simulation)
        self.assertIn("_apply_daily_fixture_maintenance()", simulation)
        self.assertIn(
            'if catalog_id.is_empty() or not _fixture_catalog.has(catalog_id):', simulation
        )
        self.assertIn('"fixture_maintenance", minute_of_day, total_maintenance_yen', simulation)
        self.assertIn('_record_event("fixture_maintenance_charged"', simulation)

        # Task #50: maintenance_yen_per_day is a 24-hour-basis figure that
        # must be scaled down to the store's configured
        # opening_minutes_per_day, not charged flat regardless of hours --
        # CONFIRMED_OFFICIAL (docs/research/quick-reference-guide-part1-
        # 2026-09-19.md section 1.2). The floor-rounding itself is this
        # project's own REMAKE_BALANCED_DEFAULT choice.
        self.assertIn(
            "func _scale_yen_to_configured_business_hours(value_at_24h_basis: int) -> int:",
            simulation,
        )
        self.assertIn(
            "total_maintenance_yen += _scale_yen_to_configured_business_hours(", simulation
        )
        self.assertIn("REMAKE_BALANCED_DEFAULT", simulation)
        self.assertIn("demand.opening_minutes_per_day", simulation)

        # No stale "unconsumed" claim should remain anywhere in the catalog
        # after this task (the same kind of drift task #43 corrected for
        # service/security/cleaning_skill).
        for entry in self.config["fixture_catalog"]:
            self.assertNotIn("maintenance_yen_per_day is still not consumed", entry["evidence_note"])
            self.assertNotIn("remains unconsumed", entry["evidence_note"])

        self.assertIn(
            "a day with no catalog-purchased fixtures must not record a "
            "fixture_maintenance_charged event",
            smoke,
        )
        self.assertIn(
            "daily fixture maintenance must deduct exactly the sum of every "
            "owned fixture's maintenance_yen_per_day",
            smoke,
        )

    def test_staff_wages_are_charged_daily(self):
        from conveni_sim.baseline_data import STAFF_CANDIDATES

        candidates_by_id = {c.id: c for c in STAFF_CANDIDATES}
        members = self.config["staff"]["members"]
        self.assertEqual(len(members), 2)

        # salary_yen_per_day_24h on each active staff.members entry must be
        # CONFIRMED_OFFICIAL, duplicated verbatim from that member's own
        # bound candidate card, the same pattern the five skills already
        # follow (task #32).
        for member in members:
            bound = candidates_by_id[member["candidate_id"]]
            self.assertEqual(
                member["salary_yen_per_day_24h"], bound.salary_yen_per_day_24h.value
            )

        staff_state = (GAME_ROOT / "scripts" / "domain" / "staff_state.gd").read_text(
            encoding="utf-8"
        )
        simulation = (GAME_ROOT / "scripts" / "vertical_slice_simulation.gd").read_text(
            encoding="utf-8"
        )
        smoke = (GAME_ROOT / "scripts" / "headless_smoke.gd").read_text(encoding="utf-8")

        self.assertIn("var salary_yen_per_day_24h: int", staff_state)
        self.assertIn(
            'salary_yen_per_day_24h = int(staff_config.get("salary_yen_per_day_24h", 0))',
            staff_state,
        )

        # Wired into the actual day-boundary transition, not just present
        # as data.
        self.assertIn("func _apply_daily_staff_wages() -> void:", simulation)
        self.assertIn("_apply_daily_staff_wages()", simulation)
        self.assertIn('"staff_wages", minute_of_day, total_wages_yen', simulation)
        self.assertIn('_record_event("staff_wages_charged"', simulation)

        # Task #50: salary_yen_per_day_24h is a 24-hour-basis figure that
        # must be scaled down to the store's configured
        # opening_minutes_per_day (wage = hourly_rate x business_hours),
        # not charged flat regardless of hours -- CONFIRMED_OFFICIAL,
        # stated twice independently (docs/research/quick-reference-guide-
        # part1-2026-09-19.md section 1.2). This client still has no
        # shift/hours-worked tracking for *individual* staff, but the
        # guide's formula scales by the store's business hours, not by
        # each staff member's personal hours worked, so none is needed.
        self.assertIn(
            "func _scale_yen_to_configured_business_hours(value_at_24h_basis: int) -> int:",
            simulation,
        )
        self.assertIn(
            "total_wages_yen += _scale_yen_to_configured_business_hours(", simulation
        )
        self.assertIn("REMAKE_BALANCED_DEFAULT", simulation)

        # No stale claim should remain anywhere after this task (the same
        # kind of drift task #43 corrected for service/security/
        # cleaning_skill, and task #46 corrected for fixture maintenance).
        self.assertNotIn(
            "stamina/academic_background/agility/sociability/education/age_years/salary/growth",
            self.config["staff_candidates_evidence_note"],
        )

        self.assertIn("exactly one staff_wages_charged event must be recorded", smoke)

    def test_staff_skill_growth_ceilings_are_wired_into_work_event_growth(self):
        from conveni_sim.baseline_data import STAFF_CANDIDATES

        candidates_by_id = {c.id: c for c in STAFF_CANDIDATES}
        members = self.config["staff"]["members"]
        self.assertEqual(len(members), 2)

        # Every *_skill_growth_ceiling on each active staff.members entry
        # must be CONFIRMED_OFFICIAL, duplicated verbatim from that
        # member's own bound candidate card -- the same pattern the five
        # skills and salary_yen_per_day_24h already follow (tasks #32/#47).
        ceiling_fields = (
            "service_skill_growth_ceiling",
            "register_skill_growth_ceiling",
            "cleaning_skill_growth_ceiling",
            "replenishment_skill_growth_ceiling",
            "security_skill_growth_ceiling",
        )
        for member in members:
            bound = candidates_by_id[member["candidate_id"]]
            for field in ceiling_fields:
                self.assertEqual(member[field], getattr(bound, field).value)

        staff_state = (GAME_ROOT / "scripts" / "domain" / "staff_state.gd").read_text(
            encoding="utf-8"
        )
        for field in ceiling_fields:
            self.assertIn("var %s: int" % field, staff_state)
            self.assertIn('staff_config.get("%s", 0)' % field, staff_state)
        # Skill growth must be undone by reset(), not just position/state,
        # now that skills are no longer static for a StaffState's lifetime.
        self.assertIn("service_skill = _start_service_skill", staff_state)
        self.assertIn("register_skill = _start_register_skill", staff_state)

        growth = (GAME_ROOT / "scripts" / "domain" / "staff_growth.gd").read_text(
            encoding="utf-8"
        )
        self.assertIn("class_name StaffGrowth", growth)
        self.assertIn("REMAKE_BALANCED_DEFAULT", growth)
        self.assertIn("CONFIRMED_COMMUNITY", growth)
        self.assertIn("func apply_checkout_growth(staff_member) -> Array[Dictionary]:", growth)
        self.assertIn("func apply_replenish_growth(staff_member) -> Array[Dictionary]:", growth)

        simulation = (GAME_ROOT / "scripts" / "vertical_slice_simulation.gd").read_text(
            encoding="utf-8"
        )
        smoke = (GAME_ROOT / "scripts" / "headless_smoke.gd").read_text(encoding="utf-8")

        # Wired into the two real work-task completion points, not just
        # present as an unused class.
        self.assertIn("_staff_growth.apply_checkout_growth(", simulation)
        self.assertIn("_staff_growth.apply_replenish_growth(", simulation)
        self.assertIn('_record_event("staff_skill_growth"', simulation)

        # Explicit restock (the instant UI action, apply_explicit_restock())
        # must stay distinct from the automatic work-task growth trigger:
        # it models no staff work time at all, so it must never call into
        # StaffGrowth.
        explicit_restock_body = simulation.split("func apply_explicit_restock(")[1].split(
            "\nfunc "
        )[0]
        self.assertNotIn("_staff_growth", explicit_restock_body)

        self.assertIn(
            "must grow the checkout staff's register_skill/service_skill by +1", smoke
        )
        self.assertIn(
            "must grow the restock staff's replenishment/cleaning/security skills by +1", smoke
        )
        self.assertIn("exactly one staff_skill_growth event must be recorded per completed", smoke)

        # No stale claim should remain anywhere after this task (the same
        # kind of drift task #43 corrected for service/security/
        # cleaning_skill, and task #46/#47 corrected for their own fields).
        self.assertNotIn("growth ceilings remain unconsumed", self.config["staff_candidates_evidence_note"])
        self.assertNotIn(
            "these values are static starting points that never change on their own",
            self.config["staff"]["skill_evidence_note"],
        )
        self.assertIn("REMAKE_BALANCED_DEFAULT", self.config["staff"]["skill_evidence_note"])

    def test_checkout_anger_penalty_is_wired_into_checkout_service(self):
        from conveni_sim.checkout_anger_penalty import (
            CHECKOUT_ANGER_AFFECTED_SKILLS,
            CHECKOUT_ANGER_SKILL_DELTA,
        )

        self.assertEqual(CHECKOUT_ANGER_SKILL_DELTA, -2)
        affected_skill_names = {skill.value for skill in CHECKOUT_ANGER_AFFECTED_SKILLS}
        self.assertEqual(
            affected_skill_names,
            {"register", "replenishment", "security", "cleaning", "service"},
        )

        anger = (GAME_ROOT / "scripts" / "domain" / "checkout_anger.gd").read_text(
            encoding="utf-8"
        )
        self.assertIn("class_name CheckoutAnger", anger)
        self.assertIn("CONFIRMED_COMMUNITY", anger)
        self.assertIn("REMAKE_BALANCED_DEFAULT", anger)
        self.assertIn("const SKILL_DELTA := -2", anger)
        self.assertIn("const MINIMUM_SKILL_VALUE := 0", anger)
        self.assertIn("func trigger_ticks(reference_ticks: int) -> int:", anger)
        self.assertIn("func apply_penalty(staff_member) -> Dictionary:", anger)
        for skill_field in (
            "register_skill",
            "replenishment_skill",
            "security_skill",
            "cleaning_skill",
            "service_skill",
        ):
            self.assertIn('results["%s"]' % skill_field, anger)

        simulation = (GAME_ROOT / "scripts" / "vertical_slice_simulation.gd").read_text(
            encoding="utf-8"
        )
        smoke = (GAME_ROOT / "scripts" / "headless_smoke.gd").read_text(encoding="utf-8")
        customer_state = (GAME_ROOT / "scripts" / "domain" / "customer_state.gd").read_text(
            encoding="utf-8"
        )

        self.assertIn("var checkout_assigned_ticks := 0", customer_state)
        self.assertIn("var checkout_anger_triggered := false", customer_state)

        # Wired into the real checkout-service tick, not just present as an
        # unused class.
        self.assertIn("_checkout_anger.trigger_ticks(_checkout_ticks)", simulation)
        self.assertIn("_checkout_anger.apply_penalty(", simulation)
        self.assertIn('_record_event("checkout_anger_triggered"', simulation)
        self.assertIn(
            "customer.checkout_assigned_ticks = customer.checkout_ticks_remaining", simulation
        )

        self.assertIn(
            "must trigger exactly one checkout_anger_triggered event", smoke
        )
        self.assertIn("must lower register_skill by 2, clamped at the floor", smoke)

        self.assertIn(
            "REMAKE_BALANCED_DEFAULT", self.config["simulation"]["checkout_anger_evidence_note"]
        )

        # Task #51: a direct re-read of the strategy guide (book pp.34-35,
        # "店員全員の能力が下がってしまう") confirmed CONFIRMED_OFFICIAL that
        # the penalty is store-wide, not scoped to whichever staff member
        # happened to be serving -- correcting task #49's original scoping.
        self.assertIn("CONFIRMED_OFFICIAL", self.config["simulation"]["checkout_anger_evidence_note"])
        self.assertIn(
            "penalty applies to EVERY active staff member",
            self.config["simulation"]["checkout_anger_evidence_note"],
        )
        self.assertIn("for angered_staff_member in staff.all_staff():", simulation)
        self.assertIn(
            "must also lower the non-checkout staff member's register_skill by 2", smoke
        )
        self.assertIn(
            "CONFIRMED_COMMUNITY", self.config["simulation"]["checkout_anger_evidence_note"]
        )

    def test_bankruptcy_and_time_limit_game_over_are_confirmed_terminal_rules(self):
        simulation = (GAME_ROOT / "scripts" / "vertical_slice_simulation.gd").read_text(
            encoding="utf-8"
        )
        smoke = (GAME_ROOT / "scripts" / "headless_smoke.gd").read_text(encoding="utf-8")

        self.assertIn("const GAME_OVER_YEAR_LIMIT := 100", simulation)
        self.assertIn("const MONTHS_PER_YEAR := 12", simulation)
        self.assertIn("func _evaluate_terminal_state() -> void:", simulation)
        self.assertIn("func _trigger_game_over(reason: String) -> void:", simulation)
        self.assertIn("if economy.cash_yen < 0:", simulation)
        self.assertIn('_trigger_game_over("bankrupt")', simulation)
        self.assertIn('_trigger_game_over("time_limit_exceeded")', simulation)
        self.assertIn("if is_game_over:", simulation)
        self.assertIn(
            "negative cash at a month boundary must trigger bankrupt game over", smoke
        )
        self.assertIn(
            "exactly zero cash at a month boundary must remain unresolved, not bankrupt", smoke
        )
        self.assertIn(
            "exceeding 100 years without a clear condition must trigger time_limit_exceeded game over",
            smoke,
        )
        self.assertIn(
            "meeting the clear condition must prevent the time-limit game over", smoke
        )
        self.assertIn("step() must be a no-op once the simulation is game over", smoke)

    def test_representative_day_month_cycle_uses_the_confirmed_4x8_multiplier(self):
        simulation = (GAME_ROOT / "scripts" / "vertical_slice_simulation.gd").read_text(
            encoding="utf-8"
        )
        economy = (GAME_ROOT / "scripts" / "domain" / "economy_state.gd").read_text(
            encoding="utf-8"
        )
        smoke = (GAME_ROOT / "scripts" / "headless_smoke.gd").read_text(encoding="utf-8")

        self.assertIn("const REPRESENTATIVE_DAYS_PER_MONTH := 4", simulation)
        self.assertIn("const MONTH_MULTIPLIER := 8", simulation)
        self.assertIn("CONFIRMED_OFFICIAL", simulation)
        self.assertIn("func _advance_minute_of_day() -> void:", simulation)
        self.assertIn("func _handle_day_boundary() -> void:", simulation)
        self.assertIn("func _settle_month_end() -> void:", simulation)
        self.assertIn("four_day_net_result_yen * MONTH_MULTIPLIER", simulation)
        self.assertIn("func record_month_end_settlement(", economy)
        self.assertIn(
            "month-end cash must equal the pre-settlement cash plus the x8 adjustment", smoke
        )
        self.assertIn(
            "the settlement record must retain month_result_yen = four_day_net_result_yen * 8",
            smoke,
        )

    def test_automatic_restock_task_assignment_is_disabled_by_default_and_provisional(self):
        simulation_config = self.config["simulation"]
        for key in (
            "restock_ticks",
            "restock_trigger_stock_units_at_or_below",
            "restock_task_enabled",
        ):
            self.assertIn(key, simulation_config)
        self.assertGreater(simulation_config["restock_ticks"], 0)
        self.assertGreaterEqual(simulation_config["restock_trigger_stock_units_at_or_below"], 0)
        self.assertIs(simulation_config["restock_task_enabled"], False)

        staff_state = (GAME_ROOT / "scripts" / "domain" / "staff_state.gd").read_text(
            encoding="utf-8"
        )
        simulation = (GAME_ROOT / "scripts" / "vertical_slice_simulation.gd").read_text(
            encoding="utf-8"
        )
        smoke = (GAME_ROOT / "scripts" / "headless_smoke.gd").read_text(encoding="utf-8")

        self.assertIn("func begin_restock(product_id: String", staff_state)
        self.assertIn("func finish_restock() -> void:", staff_state)
        self.assertIn("func _step_restock_tasks() -> void:", simulation)
        self.assertIn("func _assign_idle_restock_tasks() -> void:", simulation)
        self.assertIn("if not _restock_task_enabled:", simulation)
        self.assertIn("_any_restock_task_active()", simulation)
        self.assertIn(
            "an idle non-checkout staff member must be dispatched once a product sells out",
            smoke,
        )
        self.assertIn(
            "fixture relocation must be blocked while a restock task is active", smoke
        )
        self.assertIn(
            "a completed restock task must return the product to its configured initial stock",
            smoke,
        )

    def test_explicit_customer_admission_accepts_observed_identity_and_plan(self):
        roster = (GAME_ROOT / "scripts" / "domain" / "customer_roster.gd").read_text(
            encoding="utf-8"
        )
        simulation = (GAME_ROOT / "scripts" / "vertical_slice_simulation.gd").read_text(
            encoding="utf-8"
        )
        smoke = (GAME_ROOT / "scripts" / "headless_smoke.gd").read_text(encoding="utf-8")

        self.assertIn("func admit_default", roster)
        self.assertIn("func admit_explicit", roster)
        self.assertIn("func default_plan() -> Array[String]", roster)
        self.assertIn("func start_explicit_customer", simulation)
        self.assertIn("func _product_plan_is_valid", simulation)
        self.assertIn('"planned_product_ids": customer.planned_product_ids.duplicate()', simulation)
        self.assertIn('"observed-customer-1"', smoke)
        self.assertIn("duplicate explicit customer identity must be rejected", smoke)
        self.assertIn("explicit plan with unknown product must be rejected", smoke)

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

    def test_godot_ci_imports_project_before_running_smoke(self):
        workflow = (
            REPO_ROOT / ".github" / "workflows" / "reference-tests.yml"
        ).read_text(encoding="utf-8")
        smoke = (GAME_ROOT / "scripts" / "headless_smoke.gd").read_text(encoding="utf-8")

        self.assertIn('load(MAIN_SCENE_PATH) as PackedScene', smoke)
        self.assertIn('main_scene.instantiate()', smoke)
        editor_command = "godot --headless --editor --path game --quit"
        smoke_command = "godot --headless --path game --script res://scripts/headless_smoke.gd"
        self.assertIn(editor_command, workflow)
        self.assertIn(smoke_command, workflow)
        self.assertLess(workflow.index(editor_command), workflow.index(smoke_command))
        self.assertIn('timeout-minutes: 5', workflow)

    def test_direct_headless_script_does_not_require_global_class_cache(self):
        custom_types = (
            "VerticalSliceSimulation",
            "StoreLayout",
            "InventoryState",
            "InventoryCatalog",
            "EconomyState",
            "CustomerState",
            "CustomerRoster",
            "StaffState",
            "StaffRoster",
            "RuntimeEventLog",
            "DemandPolicy",
        )
        scripts = list((GAME_ROOT / "scripts").rglob("*.gd"))
        for script_path in scripts:
            source = script_path.read_text(encoding="utf-8")
            for custom_type in custom_types:
                self.assertNotIn(
                    f": {custom_type}",
                    source,
                    f"{script_path.relative_to(GAME_ROOT)} relies on global class cache",
                )
                self.assertNotIn(
                    f"-> {custom_type}",
                    source,
                    f"{script_path.relative_to(GAME_ROOT)} relies on global class cache",
                )

        smoke = (GAME_ROOT / "scripts" / "headless_smoke.gd").read_text(encoding="utf-8")
        self.assertIn("var initial_cash: int =", smoke)
        self.assertIn("var initial_fixture_snapshot: Array =", smoke)
        self.assertIn("func _run_visit(simulation) -> int:", smoke)

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
