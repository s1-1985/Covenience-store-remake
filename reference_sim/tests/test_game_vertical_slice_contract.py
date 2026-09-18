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
        self.assertEqual(self.config["schema_version"], 12)
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
        # estimate rather than a 0-100 customer-share score, since this
        # client has no service/cleaning/security/assortment stats yet.
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
