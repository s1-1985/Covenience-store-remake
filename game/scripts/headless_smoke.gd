extends SceneTree

const VerticalSliceSimulationScript := preload("res://scripts/vertical_slice_simulation.gd")
const DemandPolicyScript := preload("res://scripts/domain/demand_policy.gd")
const TownStateScript := preload("res://scripts/domain/town_state.gd")
const LandValuePolicyScript := preload("res://scripts/domain/land_value_policy.gd")
const StoreRatingScript := preload("res://scripts/domain/store_rating.gd")
const StoreValueScript := preload("res://scripts/domain/store_value.gd")
const SaveGameServiceScript := preload("res://scripts/save_game_service.gd")
const ChainVisitorMilestoneScript := preload("res://scripts/domain/chain_visitor_milestone.gd")
const StoreEventsScript := preload("res://scripts/domain/store_events.gd")
const CheckoutTimingScript := preload("res://scripts/domain/checkout_timing.gd")
const RestockTimingScript := preload("res://scripts/domain/restock_timing.gd")
const CustomerShareScript := preload("res://scripts/domain/customer_share.gd")
const StaffStateScript := preload("res://scripts/domain/staff_state.gd")
const StaffGrowthScript := preload("res://scripts/domain/staff_growth.gd")
const CheckoutAngerScript := preload("res://scripts/domain/checkout_anger.gd")
const GuideStartingStoreScript := preload("res://scripts/domain/guide_starting_store.gd")
const SoundSynthScript := preload("res://scripts/audio/sound_synth.gd")
const SoundThemesScript := preload("res://scripts/audio/sound_themes.gd")
const CONFIG_PATH := "res://data/vertical_slice.json"
const MAIN_SCENE_PATH := "res://scenes/main.tscn"
const MAIN_MENU_SCENE_PATH := "res://scenes/main_menu.tscn"
const MAX_STEPS := 256
const REPRESENTATIVE_DAYS_PER_MONTH_FOR_TEST := 4
const MONTH_MULTIPLIER_FOR_TEST := 8

# Task #72: a minimal duck-typed stand-in for VerticalSliceSimulation,
# exposing only the two fields town_view.gd's _town_points() actually reads
# (_player_store_position/_rival_stores), so the town-map bounding-box math
# can be exercised against a synthetic multi-rival roster without needing a
# second real simulation/scene instance.
class _FakeTownSimulation:
    var _player_store_position: Vector2i
    var _rival_stores: Array[Dictionary] = []


func _initialize() -> void:
    # Task #89: the UI scenarios below script coordinates in the small
    # prototype store; the guide starting store gets its own scenario.
    Engine.set_meta("use_prototype_store_for_tests", true)
    var main_scene := load(MAIN_SCENE_PATH) as PackedScene
    if main_scene == null:
        _fail("main scene could not be loaded")
        return
    var main_instance := main_scene.instantiate()
    if main_instance == null:
        _fail("main scene could not be instantiated")
        return
    # instantiate() alone does not enter the tree, so @onready vars (and
    # _ready()) do not run here; this only catches a structurally broken
    # scene file. Node paths this task added are checked explicitly below
    # since nothing else would validate them before an actual play session.
    for node_path in [
        "UI/Panel/Margin/Scroll/VBox/MenuButtons/SaveButton",
        "UI/Panel/Margin/Scroll/VBox/MenuButtons/LoadButton",
        "UI/Panel/Margin/Scroll/VBox/MenuButtons/QuitToMenuButton",
        "UI/Panel/Margin/Scroll/VBox/RatingValue",
        "UI/Panel/Margin/Scroll/VBox/TownValue",
        "UI/Panel/Margin/Scroll/VBox/SampleLayoutOption",
        "UI/Panel/Margin/Scroll/VBox/LoadSampleLayoutButton",
        "UI/Panel/Margin/Scroll/VBox/FixtureCatalogOption",
        "UI/Panel/Margin/Scroll/VBox/BuyFixtureButton",
        "UI/Panel/Margin/Scroll/VBox/PermitOption",
        "UI/Panel/Margin/Scroll/VBox/BuyPermitButton",
        "UI/Panel/Margin/Scroll/VBox/ProductCatalogOption",
        "UI/Panel/Margin/Scroll/VBox/ProcureFixtureOption",
        "UI/Panel/Margin/Scroll/VBox/ProcureProductButton",
        "UI/Panel/Margin/Scroll/VBox/RestockButton",
        "UI/Panel/Margin/Scroll/VBox/PromotionOption",
        "UI/Panel/Margin/Scroll/VBox/BuyPromotionButton",
        "UI/Panel/Margin/Scroll/VBox/ExpandChainButton",
        "UI/Panel/Margin/Scroll/VBox/EjectCustomerOption",
        "UI/Panel/Margin/Scroll/VBox/EjectCustomerButton",
        "UI/Panel/Margin/Scroll/VBox/PriceChangeSpinBox",
        "UI/Panel/Margin/Scroll/VBox/SetPricePolicyButton",
        "UI/Panel/Margin/Scroll/VBox/StaffSlotOption",
        "UI/Panel/Margin/Scroll/VBox/HireCandidateOption",
        "UI/Panel/Margin/Scroll/VBox/HireCandidateButton",
    ]:
        if main_instance.get_node_or_null(node_path) == null:
            _fail("main scene is missing expected node: %s" % node_path)
            return
    main_instance.free()

    var main_menu_scene := load(MAIN_MENU_SCENE_PATH) as PackedScene
    if main_menu_scene == null:
        _fail("main menu scene could not be loaded")
        return
    var main_menu_instance := main_menu_scene.instantiate()
    if main_menu_instance == null:
        _fail("main menu scene could not be instantiated")
        return
    for node_path in [
        "Panel/Margin/VBox/NewGameButton",
        "Panel/Margin/VBox/ContinueButton",
        "Panel/Margin/VBox/QuitButton",
        "Panel/Margin/VBox/StatusLabel",
    ]:
        if main_menu_instance.get_node_or_null(node_path) == null:
            _fail("main menu scene is missing expected node: %s" % node_path)
            return
    if not (main_menu_instance.get_node("Panel/Margin/VBox/ContinueButton") as Button).disabled:
        _fail("the Continue button must start disabled when no save file exists")
        return
    main_menu_instance.free()

    var parsed = JSON.parse_string(FileAccess.get_file_as_string(CONFIG_PATH))
    if typeof(parsed) != TYPE_DICTIONARY:
        _fail("vertical slice config did not parse as a dictionary")
        return

    var config: Dictionary = parsed

    # Task #87: the shipped config run the way main.gd runs it (tick()),
    # for one representative business day. Before this, arrivals were only
    # rolled once the store was empty (one visit at a time), two shoppers
    # meeting head-on could block each other forever, and automatic staff
    # restocking was switched off, so the restock clerk never moved.
    var live_simulation = VerticalSliceSimulationScript.new(config.duplicate(true))
    live_simulation.economy.cash_yen = 100_000_000
    var live_max_active := 0
    for live_minute in range(960):
        live_simulation.tick()
        live_max_active = max(live_max_active, live_simulation.customers.active_customers().size())
    if live_max_active < 2:
        _fail("more than one customer must be able to shop at the same time in the default game")
        return
    if int(live_simulation.snapshot()["completed_visits"]) < 10:
        _fail("customers must keep completing visits across a full day without gridlock")
        return
    if live_simulation.event_log.count_type("restock_started") < 1:
        _fail("staff must restock shelves on their own in the default game")
        return

    # Task #88 (guide p.16: お客さんがいないとき店員は休憩室で休んでいる):
    # over a full live day the staff must go rest and come back out.
    if live_simulation.event_log.count_type("staff_rest_started") < 1:
        _fail("staff must go rest in the break room while the store is empty")
        return
    if live_simulation.event_log.count_type("staff_returning_to_post") < 1:
        _fail("resting staff must come back out when customers arrive")
        return

    # Task #88, deterministic: with nobody in the store every staff member
    # walks to the break room door; once a customer is in, the checkout
    # staff member walks back behind the register, and nobody is rung up
    # until they are there.
    var rest_simulation = VerticalSliceSimulationScript.new(config.duplicate(true))
    rest_simulation.economy.cash_yen = 100_000_000
    var rest_door := Vector2i.ZERO
    for rest_fixture in rest_simulation.layout.fixtures:
        if str(rest_fixture["kind"]) == "break_room":
            rest_door = Vector2i(
                int(rest_fixture["interaction_subcell"][0]), int(rest_fixture["interaction_subcell"][1])
            )
    for rest_minute in range(120):
        rest_simulation.step()
    for rest_staff in rest_simulation.staff.all_staff():
        if rest_staff.rest_phase != "resting" or rest_staff.position != rest_door:
            _fail("every idle staff member must be resting at the break room door in an empty store")
            return
    var rest_checkout_staff = rest_simulation.staff.checkout_staff()
    if rest_simulation.event_log.count_type("staff_returning_to_post") != 0:
        _fail("nobody may leave the break room while the store stays empty")
        return
    if not rest_simulation.start_next_customer():
        _fail("a customer must be admissible while staff rest")
        return
    var rest_checkouts_before: int = rest_simulation.event_log.count_type("checkout_started")
    var rest_checkout_steps := 0
    while (
        rest_simulation.event_log.count_type("checkout_started") == rest_checkouts_before
        and rest_checkout_steps < MAX_STEPS
    ):
        rest_simulation.step()
        rest_checkout_steps += 1
    if rest_simulation.event_log.count_type("checkout_started") != rest_checkouts_before + 1:
        _fail("the customer must eventually be rung up after staff return from the break room")
        return
    if rest_checkout_staff.position != rest_checkout_staff.home_position() or rest_checkout_staff.rest_phase != "":
        _fail("checkout must only start once the checkout staff member is back behind the register")
        return

    # Task #89: the store every new game starts in -- the guide's p.48
    # store (12x8 tiles, 34 stocked shelves) -- run for a full business day.
    var guide_config: Dictionary = GuideStartingStoreScript.apply(config)
    if guide_config["store"]["width_tiles"] != 12 or guide_config["store"]["height_tiles"] != 8:
        _fail("the guide starting store must use the confirmed 12x8 large floor")
        return
    if config["store"]["width_tiles"] != 5:
        _fail("GuideStartingStore.apply() must not modify the config it is given")
        return
    var guide_simulation = VerticalSliceSimulationScript.new(guide_config)
    if guide_simulation.inventory.product_order.size() != 34:
        _fail("the guide starting store must stock one product per p.48 shelf")
        return
    var guide_max_active := 0
    for guide_minute in range(960):
        guide_simulation.tick()
        guide_max_active = max(guide_max_active, guide_simulation.customers.active_customers().size())
    if guide_simulation.is_game_over:
        _fail("the guide starting store must not go bankrupt on its first day")
        return
    if guide_max_active < 2 or int(guide_simulation.snapshot()["completed_visits"]) < 10:
        _fail("customers must shop concurrently and keep completing visits in the guide store")
        return
    var guide_sold_products: Dictionary = {}
    for guide_sale in guide_simulation.economy.sale_records:
        for guide_line in guide_sale["lines"]:
            guide_sold_products[str(guide_line["product_id"])] = true
    if guide_sold_products.size() < 10:
        _fail("customers in the guide store must buy across many different shelves")
        return
    # A busy guide store is rarely empty, so the break-room walk is checked
    # on a fresh copy that admits nobody after its opening customer leaves.
    var guide_rest_simulation = VerticalSliceSimulationScript.new(guide_config.duplicate(true))
    for guide_rest_minute in range(240):
        guide_rest_simulation.step()
    if not guide_rest_simulation.customers.all_settled():
        _fail("the guide store's opening customer must finish their visit")
        return
    for guide_rest_staff in guide_rest_simulation.staff.all_staff():
        if guide_rest_staff.rest_phase != "resting":
            _fail("staff must walk to the guide store's break room once it is empty")
            return

    # The scenarios below predate task #87 and script exact sell-out
    # sequences, so they keep automatic restocking off; the dedicated
    # restock scenario further down turns it back on explicitly.
    config["simulation"]["restock_task_enabled"] = false
    # They also predate task #88's starting break room (whose CONFIRMED
    # daily maintenance they don't account for, and whose rest walk would
    # delay their scripted checkouts), so it is taken out for them.
    config["fixtures"] = config["fixtures"].filter(
        func(fixture_config): return str(fixture_config["kind"]) != "break_room"
    )
    for legacy_sample_layout in config["sample_layouts"]:
        legacy_sample_layout["fixtures"] = legacy_sample_layout["fixtures"].filter(
            func(fixture_config): return str(fixture_config["kind"]) != "break_room"
        )
    var simulation = VerticalSliceSimulationScript.new(config)
    if simulation.staff.members.size() < 2:
        _fail("actor roster smoke requires multiple retained staff states")
        return
    # Task #91: 店長 + 店員2人 (クイックリファレンス p.6).
    if simulation.staff.members.size() != 3 or not simulation.staff.members.has(str(config["staff"]["manager_staff_id"])):
        _fail("a store must run with its manager plus two staff")
        return
    if simulation.staff.checkout_staff().staff_id != str(config["staff"]["checkout_staff_id"]):
        _fail("checkout staff selection must match the explicit provisional config")
        return
    var initial_cash: int = int(simulation.economy.cash_yen)
    var initial_stock: int = int(simulation.inventory.total_stock_units())
    var first_basket_total := 0
    var expected_selling_visits := 0
    for product_config in config["products"]:
        first_basket_total += int(product_config["sale_price_yen"])
        expected_selling_visits = max(
            expected_selling_visits,
            int(product_config["initial_stock_units"])
        )
    var initial_fixture_snapshot: Array = simulation.layout.fixture_snapshot()
    var steps: int = _run_visit(simulation)

    if simulation.customers.active().phase != "done":
        _fail("vertical slice did not complete within %d steps" % MAX_STEPS)
        return
    if simulation.economy.completed_sales != 1:
        _fail("vertical slice must complete exactly one sale")
        return
    if simulation.inventory.total_stock_units() != initial_stock - config["products"].size():
        _fail("first visit must remove one unit from each planned stocked product")
        return
    if simulation.economy.cash_yen != initial_cash + first_basket_total:
        _fail("vertical slice cash did not match the completed basket")
        return

    var shelf_id := str(config["products"][0]["fixture_id"])
    var initial_shelf_origin: Vector2i = simulation.layout.fixture_origin(shelf_id)
    for _turn in range(4):
        if not simulation.try_rotate_fixture_clockwise(shelf_id):
            _fail("valid fixture rotation was rejected")
            return
    if simulation.layout.fixture_snapshot() != initial_fixture_snapshot:
        _fail("four clockwise rotations must restore fixture geometry")
        return
    if simulation.try_relocate_fixture(shelf_id, Vector2i(-1, -1)):
        _fail("invalid fixture relocation must be rejected")
        return
    if simulation.layout.fixture_origin(shelf_id) != initial_shelf_origin:
        _fail("rejected fixture relocation must be atomic")
        return
    if not simulation.try_relocate_fixture(shelf_id, Vector2i(1, 10)):
        _fail("valid completed-visit fixture relocation was rejected")
        return
    if simulation.layout.fixture_origin(shelf_id) != Vector2i(1, 10):
        _fail("accepted fixture relocation did not update the layout")
        return

    var reversed_plan: Array[String] = []
    reversed_plan.assign(config["customer"]["visit_plan_product_ids"])
    reversed_plan.reverse()
    if not simulation.start_explicit_customer("observed-customer-1", reversed_plan):
        _fail("explicit customer plan could not be admitted")
        return
    steps += _run_visit(simulation)
    if simulation.customers.active().customer_id != "observed-customer-1":
        _fail("explicit customer identity was not retained")
        return
    if simulation.start_explicit_customer("observed-customer-1", reversed_plan):
        _fail("duplicate explicit customer identity must be rejected")
        return
    var unknown_plan: Array[String] = ["unknown-product"]
    if simulation.start_explicit_customer("observed-customer-2", unknown_plan):
        _fail("explicit plan with unknown product must be rejected")
        return

    while simulation.inventory.has_stock():
        if not simulation.start_next_customer():
            _fail("completed visit did not allow the next customer")
            return
        if simulation.try_relocate_fixture(shelf_id, initial_shelf_origin):
            _fail("fixture relocation must be locked during an active visit")
            return
        steps += _run_visit(simulation)
        if simulation.customers.active().phase != "done":
            _fail("repeat customer did not complete")
            return

    var sales_after_sellout: int = int(simulation.economy.completed_sales)
    if not simulation.start_next_customer():
        _fail("sellout visit could not start")
        return
    steps += _run_visit(simulation)
    if simulation.economy.completed_sales != sales_after_sellout:
        _fail("empty shelf visit must not create a sale")
        return
    if simulation.customers.completed_count() != simulation.customers.customers.size():
        _fail("every started visit must complete")
        return
    if simulation.customers.customers.size() != expected_selling_visits + 1:
        _fail("each visit must retain a distinct customer state")
        return
    if simulation.economy.cash_yen != (
        initial_cash + simulation.inventory.expected_full_sellout_revenue_yen()
    ):
        _fail("sellout revenue must equal the sum of explicit inventory values")
        return
    if simulation.economy.sale_records.size() != expected_selling_visits:
        _fail("sale ledger must contain exactly one record per selling visit")
        return
    if simulation.economy.recorded_revenue_yen() != (
        simulation.economy.cash_yen - initial_cash
    ):
        _fail("sale ledger revenue must reconcile with cash")
        return
    var transaction_ids: Dictionary = {}
    for record in simulation.economy.sale_records:
        if transaction_ids.has(record["transaction_id"]):
            _fail("sale transaction ids must be unique")
            return
        transaction_ids[record["transaction_id"]] = true
        if simulation.economy.sale_record_for_customer(record["customer_id"]).is_empty():
            _fail("selling customer must resolve to its sale record")
            return
    if not simulation.economy.sale_record_for_customer(
        simulation.customers.active().customer_id
    ).is_empty():
        _fail("empty-basket visit must not have a sale record")
        return
    if simulation.event_log.count_type("customer_entered") != expected_selling_visits + 1:
        _fail("event log must record every explicit admission")
        return
    if simulation.event_log.count_type("customer_exited") != expected_selling_visits + 1:
        _fail("event log must record every completed exit")
        return
    if simulation.event_log.count_type("checkout_completed") != expected_selling_visits:
        _fail("event log must record checkout only for selling visits")
        return
    var event_snapshot: Array = simulation.event_log.snapshot()
    for index in range(event_snapshot.size()):
        if int(event_snapshot[index]["sequence"]) != index + 1:
            _fail("event log sequence must be contiguous")
            return
    event_snapshot[0]["event_type"] = "mutated-outside-log"
    if simulation.event_log.records[0]["event_type"] == "mutated-outside-log":
        _fail("event log snapshots must be immutable copies")
        return
    var observation: Dictionary = simulation.observation_snapshot()
    if observation["provisional"] != true or observation["scenario_id"] != config["scenario_id"]:
        _fail("observation snapshot must retain its provisional scenario boundary")
        return
    if observation["events"].size() != simulation.event_log.records.size():
        _fail("observation snapshot must include the complete event log")
        return
    var observed_ids: Dictionary = {}
    for customer in simulation.customers.all_customers():
        if observed_ids.has(customer.customer_id):
            _fail("customer ids must remain unique")
            return
        observed_ids[customer.customer_id] = true

    var first_record_before_mutation: Dictionary = simulation.economy.sale_records[0].duplicate(true)
    var first_customer_id: String = str(first_record_before_mutation["customer_id"])
    var first_customer = simulation.customers.customers[first_customer_id]
    first_customer.basket[0]["unit_price_yen"] = 999999
    if simulation.economy.sale_records[0] != first_record_before_mutation:
        _fail("sale ledger must retain an immutable basket snapshot")
        return

    var restock: Dictionary = config["provisional_restock"]
    var cash_before_restock: int = int(simulation.economy.cash_yen)
    if not simulation.apply_explicit_restock(
        str(restock["product_id"]),
        str(restock["staff_id"]),
        int(restock["quantity"]),
        int(restock["total_cost_yen"])
    ):
        _fail("explicit restock input was rejected")
        return
    if simulation.economy.cash_yen != cash_before_restock - int(restock["total_cost_yen"]):
        _fail("explicit restock cost was not recorded in cash")
        return
    if simulation.economy.expense_records.size() != 1:
        _fail("explicit restock must create one immutable expense record")
        return
    var restocked_plan: Array[String] = [str(restock["product_id"])]
    if not simulation.start_explicit_customer("post-restock-customer", restocked_plan):
        _fail("restocked product could not be visited explicitly")
        return
    steps += _run_visit(simulation)
    if simulation.event_log.count_type("inventory_restock") != 1:
        _fail("explicit restock must create one cause-neutral runtime event")
        return
    if simulation.economy.sale_record_for_customer("post-restock-customer").is_empty():
        _fail("restocked product did not return to the sale flow")
        return

    simulation.reset()
    if simulation.layout.fixture_snapshot() != initial_fixture_snapshot:
        _fail("full reset must restore the configured fixture layout")
        return
    if simulation.economy.cash_yen != initial_cash or simulation.inventory.total_stock_units() != initial_stock:
        _fail("full reset must restore configured economy and inventory")
        return
    if simulation.customers.customers.size() != 1:
        _fail("full reset must replace retained visits with the initial customer")
        return
    if simulation.event_log.records.size() != 1:
        _fail("full reset must restart the event log with initial admission")
        return
    if not simulation.economy.expense_records.is_empty():
        _fail("full reset must clear explicit expense records")
        return

    var demand_config: Dictionary = config["demand"]
    var expected_configured_rate := (
        float(demand_config["nearby_population"])
        * (float(demand_config["customer_share_percent"]) / 100.0)
        * float(demand_config["daily_visit_rate_per_population"])
        / float(demand_config["opening_minutes_per_day"])
    )
    if abs(simulation.demand.expected_arrivals_per_minute() - expected_configured_rate) > 0.0000001:
        _fail("demand policy rate must match the configured population/share/rate formula")
        return

    var always_rng := RandomNumberGenerator.new()
    always_rng.seed = 1
    var always_policy = DemandPolicyScript.new({
        "nearby_population": 1000,
        "customer_share_percent": 100.0,
        "daily_visit_rate_per_population": 1.0,
        "opening_minutes_per_day": 1,
        "bad_weather_visit_multiplier": 1.0,
    }, always_rng)
    for _trial in range(20):
        if not always_policy.customer_arrives_this_minute():
            _fail("a saturated demand rate must always admit a customer")
            return

    var never_rng := RandomNumberGenerator.new()
    never_rng.seed = 1
    var never_policy = DemandPolicyScript.new({
        "nearby_population": 0,
        "customer_share_percent": 0.0,
        "daily_visit_rate_per_population": 0.0,
        "opening_minutes_per_day": 960,
        "bad_weather_visit_multiplier": 0.0,
    }, never_rng)
    for _trial in range(20):
        if never_policy.customer_arrives_this_minute():
            _fail("a zero demand rate must never admit a customer")
            return

    var bad_weather_rng := RandomNumberGenerator.new()
    bad_weather_rng.seed = 1
    var bad_weather_policy = DemandPolicyScript.new({
        "nearby_population": 1000,
        "customer_share_percent": 100.0,
        "daily_visit_rate_per_population": 0.05,
        "opening_minutes_per_day": 960,
        "bad_weather_visit_multiplier": 0.6,
        "is_bad_weather": true,
    }, bad_weather_rng)
    var expected_bad_weather_rate := (1000.0 * 1.0 * 0.05 * 0.6) / 960.0
    if abs(bad_weather_policy.expected_arrivals_per_minute() - expected_bad_weather_rate) > 0.0000001:
        _fail("bad weather must scale expected arrivals by the configured multiplier")
        return

    var saturated_demand_config: Dictionary = config.duplicate(true)
    saturated_demand_config["demand"] = {
        "nearby_population": 1000000,
        "customer_share_percent": 100.0,
        "daily_visit_rate_per_population": 1.0,
        "opening_minutes_per_day": 1,
        "bad_weather_visit_multiplier": 1.0,
        "is_bad_weather": false,
        "rng_seed": 7,
    }
    var demand_simulation = VerticalSliceSimulationScript.new(saturated_demand_config)
    if demand_simulation.customers.can_admit():
        _fail("a freshly reset simulation must start with an active default customer")
        return
    if demand_simulation.demand_admit_if_due():
        _fail("demand-driven admission must be blocked while a customer visit is still active")
        return
    if demand_simulation.customers.customers.size() != 1:
        _fail("blocked demand-driven admission must not create a customer record")
        return
    steps += _run_visit(demand_simulation)
    if demand_simulation.customers.active().phase != "done":
        _fail("demand-driven simulation's scripted visit must still complete")
        return
    var customers_before_demand_admission: int = demand_simulation.customers.customers.size()
    if not demand_simulation.demand_admit_if_due():
        _fail("a saturated demand rate must admit a customer once the store is empty")
        return
    if demand_simulation.customers.customers.size() != customers_before_demand_admission + 1:
        _fail("demand-driven admission must create exactly one new customer record")
        return
    if demand_simulation.customers.can_admit():
        _fail("a newly admitted demand-driven customer must occupy the store")
        return
    steps += _run_visit(demand_simulation)
    var minute_before_idle_tick: int = int(demand_simulation.minute_of_day)
    if not demand_simulation.tick_idle_for_demand():
        _fail("tick_idle_for_demand must also admit under a saturated demand rate")
        return
    if int(demand_simulation.minute_of_day) == minute_before_idle_tick:
        _fail("tick_idle_for_demand must advance the clock even while idle")
        return

    var restock_config: Dictionary = config.duplicate(true)
    restock_config["demand"] = {
        "nearby_population": 0,
        "customer_share_percent": 0.0,
        "daily_visit_rate_per_population": 0.0,
        "opening_minutes_per_day": 960,
        "bad_weather_visit_multiplier": 0.0,
        "is_bad_weather": false,
        "rng_seed": 3,
    }
    restock_config["simulation"]["restock_task_enabled"] = true
    restock_config["simulation"]["restock_ticks"] = 2
    restock_config["simulation"]["restock_trigger_stock_units_at_or_below"] = 0
    var restock_simulation = VerticalSliceSimulationScript.new(restock_config)
    var restock_staff_id := str(restock_config["provisional_restock"]["staff_id"])
    if restock_staff_id == str(restock_config["staff"]["checkout_staff_id"]):
        _fail("restock test config must designate a non-checkout staff member")
        return
    if restock_simulation.staff.members[restock_staff_id].state != "idle":
        _fail("a non-checkout staff member must start idle")
        return

    steps += _run_visit(restock_simulation)

    var restock_product_id := "prototype-bread"
    var restock_product = restock_simulation.inventory.get_product(restock_product_id)
    var restock_cash_before := int(restock_simulation.economy.cash_yen)
    while restock_product.stock_units > 0:
        if restock_simulation.inventory.try_take_one(restock_product_id).is_empty():
            _fail("directly depleting the restock test product must succeed while stock remains")
            return
    if restock_simulation.staff.members[restock_staff_id].state != "idle":
        _fail("depleting stock must not itself dispatch a restock task before the next tick")
        return

    restock_simulation.tick_idle_for_demand()
    if restock_simulation.staff.members[restock_staff_id].state == "idle":
        _fail("an idle non-checkout staff member must be dispatched once a product sells out")
        return
    if restock_simulation.staff.members[restock_staff_id].restock_target_product_id != restock_product_id:
        _fail("the dispatched staff member must target the sold-out product")
        return
    if restock_simulation.try_relocate_fixture(
        str(restock_config["products"][1]["fixture_id"]), Vector2i(0, 4)
    ):
        _fail("fixture relocation must be blocked while a restock task is active")
        return

    var restock_task_steps := 0
    while restock_simulation.staff.members[restock_staff_id].state != "idle" and restock_task_steps < MAX_STEPS:
        restock_simulation.tick_idle_for_demand()
        restock_task_steps += 1
    if restock_task_steps >= MAX_STEPS:
        _fail("the automatic restock task did not complete within %d steps" % MAX_STEPS)
        return
    if restock_product.stock_units != restock_product.initial_stock_units:
        _fail("a completed restock task must return the product to its configured initial stock")
        return
    if restock_simulation.event_log.count_type("inventory_restock") != 1:
        _fail("a completed automatic restock task must record exactly one inventory_restock event")
        return
    var expected_restock_cost: int = (
        restock_product.initial_stock_units * restock_product.restock_unit_cost_yen
    )
    if restock_simulation.economy.cash_yen != restock_cash_before - expected_restock_cost:
        _fail("automatic restock cost must match quantity times the configured unit cost")
        return

    # Task #48: the single checkout _run_visit() completed above and the
    # single automatic restock task just completed are each one confirmed
    # work-growth trigger, so staff-1 (checkout) and staff-2 (restock) must
    # each show the corresponding skills grown by exactly the unit growth,
    # and exactly one staff_skill_growth event per task.
    var checkout_growth_staff = restock_simulation.staff.members[
        str(restock_config["staff"]["checkout_staff_id"])
    ]
    if checkout_growth_staff.register_skill != 21 or checkout_growth_staff.service_skill != 18:
        _fail("a completed checkout task must grow the checkout staff's register_skill/service_skill by +1")
        return
    var restock_growth_staff = restock_simulation.staff.members[restock_staff_id]
    if (
        restock_growth_staff.replenishment_skill != 21
        or restock_growth_staff.cleaning_skill != 18
        or restock_growth_staff.security_skill != 21
    ):
        _fail("a completed restock task must grow the restock staff's replenishment/cleaning/security skills by +1")
        return
    if restock_simulation.event_log.count_type("staff_skill_growth") != 2:
        _fail("exactly one staff_skill_growth event must be recorded per completed checkout/restock task")
        return

    var other_product_id := "prototype-drink"
    var other_product = restock_simulation.inventory.get_product(other_product_id)
    if other_product.stock_units != other_product.initial_stock_units - 1:
        _fail("only the sold-out product should have been restocked; the other must be untouched")
        return

    var month_config: Dictionary = config.duplicate(true)
    month_config["demand"] = {
        "nearby_population": 0,
        "customer_share_percent": 0.0,
        "daily_visit_rate_per_population": 0.0,
        "opening_minutes_per_day": 960,
        "bad_weather_visit_multiplier": 0.0,
        "is_bad_weather": false,
        "rng_seed": 11,
    }
    var month_simulation = VerticalSliceSimulationScript.new(month_config)
    if month_simulation.day_count != 0 or month_simulation.month_count != 0:
        _fail("a freshly reset simulation must start at day 0 / month 0")
        return

    steps += _run_visit(month_simulation)
    var cash_after_initial_sale: int = int(month_simulation.economy.cash_yen)
    if not month_simulation.apply_explicit_restock("prototype-bread", "staff-2", 1, 50):
        _fail("explicit restock during the month-end test setup must be accepted")
        return
    var cash_before_month_end: int = int(month_simulation.economy.cash_yen)
    if cash_before_month_end != cash_after_initial_sale - 50:
        _fail("the manual restock expense must be reflected in cash before month end")
        return
    var day_count_before_month_end_loop: int = month_simulation.day_count

    var month_end_ticks := 0
    while month_simulation.day_count < REPRESENTATIVE_DAYS_PER_MONTH_FOR_TEST and month_end_ticks < 20000:
        month_simulation.tick_idle_for_demand()
        month_end_ticks += 1
    if month_end_ticks >= 20000:
        _fail("advancing to the end of the representative month took too long")
        return
    if month_simulation.day_count != REPRESENTATIVE_DAYS_PER_MONTH_FOR_TEST:
        _fail("day_count must equal REPRESENTATIVE_DAYS_PER_MONTH once the month ends")
        return
    if month_simulation.month_count != 1:
        _fail("exactly one month-end settlement must have occurred")
        return
    if month_simulation.economy.month_end_records.size() != 1:
        _fail("exactly one month_end settlement record must be retained")
        return
    if month_simulation.event_log.count_type("month_end_settlement") != 1:
        _fail("exactly one month_end_settlement event must be recorded")
        return
    # Task #47/#50: every day boundary crossed in the loop above also
    # charges each active staff member's own salary_yen_per_day_24h, scaled
    # to the configured opening_minutes_per_day, so the expected 4-day net
    # result must account for that alongside the manual restock above
    # (fixture maintenance stays 0 here: month_config never purchases a
    # catalog fixture).
    var daily_wages_yen := 0
    for staff_member_config in config["staff"]["members"]:
        daily_wages_yen += _expected_daily_yen_at_business_hours(
            int(staff_member_config.get("salary_yen_per_day_24h", 0)),
            int(month_config["demand"]["opening_minutes_per_day"])
        )
    var days_crossed_in_month_end_loop: int = (
        REPRESENTATIVE_DAYS_PER_MONTH_FOR_TEST - day_count_before_month_end_loop
    )
    var expected_four_day_net_result_yen: int = (
        cash_before_month_end - 1000 - daily_wages_yen * days_crossed_in_month_end_loop
    )
    var expected_month_result_yen: int = (
        expected_four_day_net_result_yen * MONTH_MULTIPLIER_FOR_TEST
    )
    # cash_after_settlement = cash_at_month_start + four_day_net_result_yen +
    # (month_result_yen - four_day_net_result_yen) = cash_at_month_start +
    # month_result_yen, by construction of _settle_month_end() -- simpler
    # and, since task #47, more robust than reusing cash_before_month_end
    # (no longer equal to cash right before settlement's own adjustment,
    # now that day-boundary expenses can fall between the two).
    var expected_cash_after_month_end: int = 1000 + expected_month_result_yen
    if month_simulation.economy.cash_yen != expected_cash_after_month_end:
        _fail("month-end cash must equal the pre-settlement cash plus the x8 adjustment")
        return
    var settlement_record: Dictionary = month_simulation.economy.month_end_records[0]
    if int(settlement_record["details"]["four_day_net_result_yen"]) != expected_four_day_net_result_yen:
        _fail("the settlement record must retain the exact four-day net result it aggregated")
        return
    if int(settlement_record["details"]["month_result_yen"]) != expected_month_result_yen:
        _fail("the settlement record must retain month_result_yen = four_day_net_result_yen * 8")
        return

    var bankruptcy_simulation = VerticalSliceSimulationScript.new(config.duplicate(true))
    bankruptcy_simulation.economy.cash_yen = -1
    bankruptcy_simulation._evaluate_terminal_state()
    if not bankruptcy_simulation.is_game_over or bankruptcy_simulation.game_over_reason != "bankrupt":
        _fail("negative cash at a month boundary must trigger bankrupt game over")
        return
    var minute_before_frozen_step: int = int(bankruptcy_simulation.minute_of_day)
    bankruptcy_simulation.step()
    if int(bankruptcy_simulation.minute_of_day) != minute_before_frozen_step:
        _fail("step() must be a no-op once the simulation is game over")
        return
    if bankruptcy_simulation.tick_idle_for_demand():
        _fail("tick_idle_for_demand() must return false once the simulation is game over")
        return
    if bankruptcy_simulation.start_next_customer():
        _fail("start_next_customer() must be rejected once the simulation is game over")
        return
    if bankruptcy_simulation.apply_explicit_restock("prototype-bread", "staff-2", 1, 10):
        _fail("apply_explicit_restock() must be rejected once the simulation is game over")
        return

    var zero_cash_simulation = VerticalSliceSimulationScript.new(config.duplicate(true))
    zero_cash_simulation.economy.cash_yen = 0
    zero_cash_simulation._evaluate_terminal_state()
    if zero_cash_simulation.is_game_over:
        _fail("exactly zero cash at a month boundary must remain unresolved, not bankrupt")
        return

    var time_limit_simulation = VerticalSliceSimulationScript.new(config.duplicate(true))
    time_limit_simulation.month_count = 1200
    time_limit_simulation._evaluate_terminal_state()
    if not time_limit_simulation.is_game_over or time_limit_simulation.game_over_reason != "time_limit_exceeded":
        _fail("exceeding 100 years without a clear condition must trigger time_limit_exceeded game over")
        return

    var cleared_simulation = VerticalSliceSimulationScript.new(config.duplicate(true))
    cleared_simulation.month_count = 1200
    cleared_simulation.clear_condition_met = true
    cleared_simulation._evaluate_terminal_state()
    if cleared_simulation.is_game_over:
        _fail("meeting the clear condition must prevent the time-limit game over")
        return

    var purchase_simulation = VerticalSliceSimulationScript.new(config.duplicate(true))
    steps += _run_visit(purchase_simulation)
    if purchase_simulation.customers.can_admit() != true:
        _fail("the purchase test's initial scripted visit must complete before purchasing")
        return
    var cash_before_any_purchase: int = int(purchase_simulation.economy.cash_yen)
    if purchase_simulation.try_purchase_fixture(
        "potted_plant", "amenity-occupied", Vector2i(1, 6), Vector2i(2, 5)
    ):
        _fail("purchasing on top of an existing fixture must be rejected")
        return
    if purchase_simulation.economy.cash_yen != cash_before_any_purchase:
        _fail("a rejected fixture purchase must not change cash")
        return
    if not purchase_simulation.try_purchase_fixture(
        "potted_plant", "amenity-1", Vector2i(1, 10), Vector2i(1, 9)
    ):
        _fail("a valid, affordable fixture purchase must be accepted")
        return
    if purchase_simulation.economy.cash_yen != cash_before_any_purchase - 1000:
        _fail("a fixture purchase must deduct exactly its configured purchase price")
        return
    if purchase_simulation.layout.fixture_origin("amenity-1") != Vector2i(1, 10):
        _fail("a purchased fixture must be placed at the requested origin")
        return
    if purchase_simulation.event_log.count_type("fixture_purchased") != 1:
        _fail("a completed fixture purchase must record exactly one fixture_purchased event")
        return
    if purchase_simulation.try_purchase_fixture(
        "bench", "amenity-1", Vector2i(4, 10), Vector2i(4, 9)
    ):
        _fail("a duplicate fixture instance id must be rejected")
        return
    if purchase_simulation.try_purchase_fixture(
        "unknown_catalog_entry", "amenity-2", Vector2i(4, 10), Vector2i(4, 9)
    ):
        _fail("an unknown fixture catalog id must be rejected")
        return
    var cash_before_unaffordable_purchase: int = int(purchase_simulation.economy.cash_yen)
    if purchase_simulation.try_purchase_fixture(
        "fountain", "amenity-4", Vector2i(1, 12), Vector2i(1, 11)
    ):
        _fail("a fixture purchase costing more than available cash must be rejected")
        return
    if purchase_simulation.economy.cash_yen != cash_before_unaffordable_purchase:
        _fail("a rejected fixture purchase must not change cash")
        return

    # Task #78: try_sell_fixture() -- CONFIRMED_OFFICIAL that "売却" exists
    # as an interior-edit command; the 50% refund and the specific
    # rejection rules below are this project's own REMAKE_BALANCED_DEFAULT
    # choices (see the function's own comment in vertical_slice_
    # simulation.gd).
    var sell_simulation = VerticalSliceSimulationScript.new(config.duplicate(true))
    steps += _run_visit(sell_simulation)
    if not sell_simulation.customers.all_settled():
        _fail("the sell test's initial scripted visit must complete before selling")
        return
    # Default starting cash (¥1,000) does not cover a shelf purchase plus
    # procuring a full shelf of stock (medium_ambient_shelf's capacity=80
    # x bread's restock_unit_cost_yen=150 = ¥12,000 alone); top up first,
    # same as other purchase-heavy scenarios in this file.
    sell_simulation.economy.cash_yen += 50_000
    if sell_simulation.try_sell_fixture("checkout-1"):
        _fail("selling the checkout fixture must be rejected")
        return
    if sell_simulation.try_sell_fixture("shelf-1"):
        _fail("selling a pre-catalog fixture with no catalog_id must be rejected (no price to refund from)")
        return
    if sell_simulation.try_sell_fixture("no-such-fixture"):
        _fail("selling an unknown fixture id must be rejected")
        return
    if not sell_simulation.try_purchase_fixture(
        "medium_ambient_shelf", "sell-shelf-1", Vector2i(1, 10), Vector2i(1, 9)
    ):
        _fail("sell test: setup shelf purchase failed")
        return
    if not sell_simulation.try_procure_product("bread", "sell-product-1", "sell-shelf-1"):
        _fail("sell test: setup product procurement failed")
        return
    if sell_simulation.try_sell_fixture("sell-shelf-1"):
        _fail("selling a fixture that still holds procured stock must be rejected")
        return
    if not sell_simulation.try_purchase_fixture(
        "potted_plant", "sell-amenity-1", Vector2i(6, 10), Vector2i(6, 9)
    ):
        _fail("sell test: setup amenity purchase failed")
        return
    var potted_plant_price := 0
    for entry in config["fixture_catalog"]:
        if str(entry["catalog_id"]) == "potted_plant":
            potted_plant_price = int(entry["purchase_price_yen"])
            break
    var cash_before_sell: int = int(sell_simulation.economy.cash_yen)
    if not sell_simulation.try_sell_fixture("sell-amenity-1"):
        _fail("selling a valid, unoccupied, non-checkout fixture must be accepted")
        return
    var expected_refund: int = (
        potted_plant_price * sell_simulation.FIXTURE_SELL_REFUND_PERCENT / 100
    )
    if sell_simulation.economy.cash_yen != cash_before_sell + expected_refund:
        _fail("selling a fixture must refund exactly FIXTURE_SELL_REFUND_PERCENT of its catalog price")
        return
    if sell_simulation.layout.fixtures_by_id.has("sell-amenity-1"):
        _fail("a sold fixture must actually be removed from the layout")
        return
    if sell_simulation.event_log.count_type("fixture_sold") != 1:
        _fail("a completed fixture sale must record exactly one fixture_sold event")
        return

    # Task #78: try_swap_fixtures() -- CONFIRMED_OFFICIAL that "入れ替え"
    # exists as a distinct interior-edit command; exchanging two already-
    # placed fixtures' positions is this project's own REMAKE_BALANCED_
    # DEFAULT reading of what it does (see the function's own comment).
    var swap_simulation = VerticalSliceSimulationScript.new(config.duplicate(true))
    steps += _run_visit(swap_simulation)
    if not swap_simulation.customers.all_settled():
        _fail("the swap test's initial scripted visit must complete before purchasing")
        return
    # Default starting cash (¥1,000) does not cover both fixtures this
    # scenario purchases (potted_plant ¥1,000 + bench ¥2,000).
    swap_simulation.economy.cash_yen += 50_000
    if not swap_simulation.try_purchase_fixture(
        "potted_plant", "swap-a", Vector2i(1, 10), Vector2i(1, 9)
    ):
        _fail(
            "swap test: setup fixture A purchase failed (cash=%d, is_game_over=%s, all_settled=%s, has_swap_a=%s)" % [
                int(swap_simulation.economy.cash_yen),
                str(swap_simulation.is_game_over),
                str(swap_simulation.customers.all_settled()),
                str(swap_simulation.layout.fixtures_by_id.has("swap-a")),
            ]
        )
        return
    if not swap_simulation.try_purchase_fixture(
        "bench", "swap-b", Vector2i(4, 10), Vector2i(4, 9)
    ):
        _fail("swap test: setup fixture B purchase failed")
        return
    var swap_a_origin_before: Vector2i = swap_simulation.layout.fixture_origin("swap-a")
    var swap_b_origin_before: Vector2i = swap_simulation.layout.fixture_origin("swap-b")
    if swap_simulation.try_swap_fixtures("swap-a", "swap-a"):
        _fail("swapping a fixture with itself must be rejected")
        return
    if swap_simulation.try_swap_fixtures("swap-a", "no-such-fixture"):
        _fail("swapping with an unknown fixture id must be rejected")
        return
    if not swap_simulation.try_swap_fixtures("swap-a", "swap-b"):
        _fail("swapping two valid, unoccupied fixtures must be accepted")
        return
    if swap_simulation.layout.fixture_origin("swap-a") != swap_b_origin_before:
        _fail("swap must move fixture A to fixture B's former origin")
        return
    if swap_simulation.layout.fixture_origin("swap-b") != swap_a_origin_before:
        _fail("swap must move fixture B to fixture A's former origin")
        return
    if swap_simulation.event_log.count_type("fixtures_swapped") != 1:
        _fail("a completed swap must record exactly one fixtures_swapped event")
        return

    var parking_simulation = VerticalSliceSimulationScript.new(config.duplicate(true))
    steps += _run_visit(parking_simulation)
    if not parking_simulation.try_purchase_fixture(
        "parking_ground", "parking-1", Vector2i(6, 12), Vector2i(5, 12)
    ):
        _fail("a valid parking fixture purchase must be accepted")
        return
    if parking_simulation.layout.fixture_origin("parking-1") != Vector2i(6, 12):
        _fail("a purchased parking fixture must be placed at the requested origin")
        return
    if parking_simulation.layout.is_walkable(Vector2i(6, 12)):
        _fail("a placed parking fixture's footprint must not be walkable, same as any other fixture")
        return

    # Task #36: start_next_customer() (the manual "Admit next customer"
    # button) now also supports concurrent admission, same as
    # start_explicit_customer() -- only the fully-automatic passive demand
    # flow (demand_admit_if_due(), tested above at "demand-driven admission
    # must be blocked while a customer visit is still active") deliberately
    # stays single-customer.
    var manual_admit_config: Dictionary = config.duplicate(true)
    manual_admit_config["customer"]["max_concurrent_customers"] = 2
    var manual_admit_simulation = VerticalSliceSimulationScript.new(manual_admit_config)
    steps += _run_visit(manual_admit_simulation)
    if not manual_admit_simulation.customers.all_settled():
        _fail("the manual-admit scenario's initial default customer should have finished draining")
        return
    if not manual_admit_simulation.start_next_customer():
        _fail("start_next_customer() could not admit the first customer of the manual-admit scenario")
        return
    if not manual_admit_simulation.start_next_customer():
        _fail("start_next_customer() must be able to admit a second customer while the first is still active (task #36)")
        return
    if manual_admit_simulation.start_next_customer():
        _fail("start_next_customer() must be rejected once max_concurrent_customers is already reached")
        return

    # Two customers admitted concurrently (both via the explicit/observed
    # path here, with an identical plan so their routes stay in lockstep for
    # a deterministic queueing test) must both be able to shop at once, but
    # the single checkout fixture/staff still serializes service: whichever
    # arrives at checkout second must wait in a FIFO queue rather than being
    # served simultaneously.
    var concurrent_config: Dictionary = config.duplicate(true)
    concurrent_config["customer"]["max_concurrent_customers"] = 2
    var concurrent_simulation = VerticalSliceSimulationScript.new(concurrent_config)
    steps += _run_visit(concurrent_simulation)
    var completed_before_concurrency: int = concurrent_simulation.customers.completed_count()
    var sales_before_concurrency: int = concurrent_simulation.economy.completed_sales
    var shared_plan: Array[String] = ["prototype-bread"]
    if not concurrent_simulation.start_explicit_customer("concurrent-a", shared_plan):
        _fail("first concurrent customer could not be admitted")
        return
    if concurrent_simulation.customers.all_settled():
        _fail("all_settled() must be false immediately after admitting a customer")
        return
    if not concurrent_simulation.start_explicit_customer("concurrent-b", shared_plan):
        _fail("a second customer with an identical plan must be admittable while the first is still shopping (task #36)")
        return
    if concurrent_simulation.start_explicit_customer("concurrent-c", shared_plan):
        _fail("a third customer must not be admittable once max_concurrent_customers (2) is already reached")
        return

    var concurrent_steps := 0
    var saw_simultaneous_wait := false
    var simultaneous_checkout_violation := false
    # Task #66: concurrent-a/concurrent-b share an identical plan, so their
    # find_path() routes are identical too -- both admitted in the same tick,
    # they start stacked on the entry subcell. The confirmed passage-width
    # rule (a 1/2-masu-wide corridor is exclusive) must then make the second
    # one wait a tick behind the first rather than overlapping it for the
    # rest of the walk. This checks that invariant across every tick of the
    # whole scenario, excluding the checkout interaction cell itself, where
    # queued customers are deliberately designed to converge (see
    # _subcell_is_free_for's own exemption).
    var position_collision_detected := false
    var concurrent_interaction_cells: Dictionary = {}
    for concurrent_fixture in concurrent_simulation.layout.fixtures:
        var concurrent_cell: Array = concurrent_fixture["interaction_subcell"]
        concurrent_interaction_cells[Vector2i(int(concurrent_cell[0]), int(concurrent_cell[1]))] = true
    var customer_b_stalled_while_moving := false
    var previous_customer_b_position: Vector2i = concurrent_simulation.customers.customer("concurrent-b").position
    while (
        concurrent_simulation.customers.completed_count() < completed_before_concurrency + 2
        and concurrent_steps < MAX_STEPS
    ):
        concurrent_simulation.step()
        concurrent_steps += 1
        var checkout_count := 0
        var waiting_count := 0
        var seen_positions: Dictionary = {}
        for customer in concurrent_simulation.customers.active_customers():
            if customer.phase == "checkout":
                checkout_count += 1
                continue  # deliberately converges on the checkout cell
            if customer.phase == "waiting_checkout":
                waiting_count += 1
                continue  # same shared cell, same exemption
            if customer.phase == "shopping":
                continue  # stationed at a shelf's interaction cell, same exemption
            # Task #87: two shoppers who finish at the same shelf leave from
            # its (shared, exempt) interaction cell on the same tick.
            if concurrent_interaction_cells.has(customer.position):
                continue
            if seen_positions.has(customer.position):
                position_collision_detected = true
            seen_positions[customer.position] = true
        if checkout_count > 1:
            simultaneous_checkout_violation = true
        if checkout_count == 1 and waiting_count >= 1:
            saw_simultaneous_wait = true
        if concurrent_simulation.customers.customers.has("concurrent-b"):
            var customer_b = concurrent_simulation.customers.customer("concurrent-b")
            var moving_phase: bool = customer_b.phase in ["to_shelf", "to_checkout", "leaving"]
            if moving_phase and customer_b.position == previous_customer_b_position:
                customer_b_stalled_while_moving = true
            previous_customer_b_position = customer_b.position
    steps += concurrent_steps

    if simultaneous_checkout_violation:
        _fail("no more than one customer may occupy the single checkout's service slot at once")
        return
    if not saw_simultaneous_wait:
        _fail("second customer never had to wait in the checkout queue behind the first")
        return
    if position_collision_detected:
        _fail("two in-transit customers must never occupy the same non-checkout subcell at once (task #66)")
        return
    if not customer_b_stalled_while_moving:
        _fail("the trailing customer must be forced to wait at least once by the passage-width rule (task #66); this scenario is not exercising it")
        return
    if concurrent_simulation.customers.completed_count() != completed_before_concurrency + 2:
        _fail("both concurrently-admitted customers must eventually complete their visit")
        return
    if concurrent_simulation.economy.completed_sales != sales_before_concurrency + 2:
        _fail("both concurrently-queued customers must each complete a sale")
        return
    if not concurrent_simulation.customers.all_settled():
        _fail("all_settled() must become true once every admitted customer is done")
        return
    if not concurrent_simulation.customers.can_admit_concurrent():
        _fail("can_admit_concurrent() must be true again once both customers are done")
        return

    # Task #52: ejecting a customer from the checkout queue/service avoids
    # them ever completing a sale (or triggering the anger penalty), and
    # frees the checkout resource for the next queued customer.
    var eject_config: Dictionary = config.duplicate(true)
    eject_config["customer"]["max_concurrent_customers"] = 2
    var eject_simulation = VerticalSliceSimulationScript.new(eject_config)
    var fresh_default_customer_id: String = eject_simulation.customers.active_customer_id
    if eject_simulation.try_eject_customer(fresh_default_customer_id):
        _fail("try_eject_customer() must be rejected for a customer still shopping (not yet at checkout)")
        return
    if eject_simulation.try_eject_customer("no-such-customer-id"):
        _fail("try_eject_customer() must be rejected for an unknown customer id")
        return
    steps += _run_visit(eject_simulation)
    var completed_before_eject: int = eject_simulation.customers.completed_count()
    var sales_before_eject: int = eject_simulation.economy.completed_sales
    var eject_plan: Array[String] = ["prototype-bread"]
    if not eject_simulation.start_explicit_customer("eject-a", eject_plan):
        _fail("first eject-scenario customer could not be admitted")
        return
    if not eject_simulation.start_explicit_customer("eject-b", eject_plan):
        _fail("second eject-scenario customer could not be admitted while the first is still shopping")
        return
    var eject_wait_ticks := 0
    while (
        eject_simulation.customers.customer("eject-a").phase != "checkout"
        and eject_wait_ticks < MAX_STEPS
    ):
        eject_simulation.step()
        eject_wait_ticks += 1
    steps += eject_wait_ticks
    if eject_wait_ticks >= MAX_STEPS:
        _fail("first eject-scenario customer never reached checkout")
        return
    if eject_simulation.staff.checkout_staff().state != "checkout":
        _fail("checkout staff must be busy serving the first eject-scenario customer")
        return
    if not eject_simulation.try_eject_customer("eject-a"):
        _fail("ejecting a customer currently being served must be accepted")
        return
    if eject_simulation.event_log.count_type("customer_ejected") != 1:
        _fail("exactly one customer_ejected event must be recorded")
        return
    if eject_simulation.staff.checkout_staff().state != "idle":
        _fail("ejecting the customer being served must immediately free the checkout staff")
        return
    if eject_simulation.customers.customer("eject-a").phase != "leaving":
        _fail("an ejected customer must transition to the leaving phase")
        return
    if eject_simulation.try_eject_customer("eject-a"):
        _fail("a customer already ejected (now leaving) must not be ejectable again")
        return

    var eject_finish_ticks := 0
    while (
        eject_simulation.customers.completed_count() < completed_before_eject + 2
        and eject_finish_ticks < MAX_STEPS
    ):
        eject_simulation.step()
        eject_finish_ticks += 1
    steps += eject_finish_ticks
    if eject_finish_ticks >= MAX_STEPS:
        _fail("both eject-scenario customers never finished their visit")
        return
    if eject_simulation.customers.customer("eject-a").settled_transaction_id != "":
        _fail("an ejected customer must never complete a sale")
        return
    if eject_simulation.economy.completed_sales != sales_before_eject + 1:
        _fail("only the non-ejected eject-scenario customer's sale should be recorded")
        return

    # Task #53: a configured price policy scales the unit price actually
    # charged when a customer picks up a product, is rejected below -100%
    # (a discount past 0% of list price), and feeds the monthly rating
    # evaluation via price_change_pct instead of always being 0.
    var price_simulation = VerticalSliceSimulationScript.new(config.duplicate(true))
    steps += _run_visit(price_simulation)
    if price_simulation.try_set_price_policy(-101):
        _fail("try_set_price_policy() must reject a price change below -100%")
        return
    if price_simulation.price_change_pct != 0:
        _fail("a rejected price policy change must not mutate price_change_pct")
        return
    if not price_simulation.try_set_price_policy(-50):
        _fail("a valid -50% price policy change must be accepted")
        return
    if price_simulation.price_change_pct != -50:
        _fail("try_set_price_policy() must update price_change_pct")
        return
    if price_simulation.event_log.count_type("price_policy_changed") != 1:
        _fail("exactly one price_policy_changed event must be recorded")
        return
    var expected_discounted_total_yen := 0
    for product_config in config["products"]:
        expected_discounted_total_yen += int(floor(float(int(product_config["sale_price_yen"])) * 0.5))
    var price_check_plan: Array[String] = []
    for product_config in config["products"]:
        price_check_plan.append(str(product_config["id"]))
    if not price_simulation.start_explicit_customer("price-check-customer", price_check_plan):
        _fail("could not admit a customer to verify the discounted price")
        return
    steps += _run_visit(price_simulation)
    var price_last_sale: Dictionary = price_simulation.economy.sale_record_for_customer("price-check-customer")
    if price_last_sale.is_empty():
        _fail("the price-policy scenario's second visit must complete a sale")
        return
    if int(price_last_sale["total_yen"]) != expected_discounted_total_yen:
        _fail("a purchase made under a -50% price policy must charge exactly half the list price (floored) per item")
        return

    # Task #56: try_hire_candidate() lets the player replace whoever
    # currently occupies a staff.members roster slot with a different
    # candidate from the 35-person staff_candidates pool, rejects an
    # unknown staff_id/candidate_id, and rejects hiring a candidate who is
    # already employed in the OTHER slot (a real person can't occupy both).
    var hire_simulation = VerticalSliceSimulationScript.new(config.duplicate(true))
    steps += _run_visit(hire_simulation)
    if hire_simulation.staff.members["staff-1"].candidate_id != "manda_machiko":
        _fail("staff-1 must start bound to its configured default candidate (manda_machiko)")
        return
    if hire_simulation.try_hire_candidate("staff-1", "sugawara_fumio"):
        _fail("try_hire_candidate() must reject hiring a candidate already employed in the other slot")
        return
    if hire_simulation.try_hire_candidate("staff-1", "no-such-candidate"):
        _fail("try_hire_candidate() must reject an unknown candidate_id")
        return
    if hire_simulation.try_hire_candidate("no-such-staff-slot", "takenaka_sayuri"):
        _fail("try_hire_candidate() must reject an unknown staff_id")
        return
    if hire_simulation.staff.members["staff-1"].candidate_id != "manda_machiko":
        _fail("a rejected hire must not mutate the roster slot")
        return
    if not hire_simulation.try_hire_candidate("staff-1", "takenaka_sayuri"):
        _fail("a valid hire (unemployed candidate into an existing slot) must be accepted")
        return
    if hire_simulation.staff.members["staff-1"].candidate_id != "takenaka_sayuri":
        _fail("try_hire_candidate() must update the roster slot's candidate_id")
        return
    if hire_simulation.staff.members["staff-1"].display_name != "竹中小百合":
        _fail("try_hire_candidate() must update the roster slot's display_name to the newly hired candidate's")
        return
    # takenaka_sayuri's register_skill (14) differs from manda_machiko's
    # (20, the config-derived starting value _run_visit() above already
    # exercised); confirms hire() actually re-baselines the skill fields
    # StaffState uses elsewhere (CheckoutTiming/RestockTiming/store rating),
    # not just the identity fields.
    if hire_simulation.staff.members["staff-1"].register_skill != 14:
        _fail("try_hire_candidate() must re-baseline the roster slot's skills to the newly hired candidate's")
        return
    if hire_simulation.event_log.count_type("staff_hired") != 1:
        _fail("exactly one staff_hired event must be recorded for the accepted hire")
        return
    # manda_machiko, now vacated from staff-1, must become hireable again
    # (into staff-2, replacing sugawara_fumio) -- the collision check only
    # looks at CURRENT occupants, not history.
    if not hire_simulation.try_hire_candidate("staff-2", "manda_machiko"):
        _fail("a candidate vacated from one slot must become hireable into another")
        return

    # Task #37: loading a built-in sample layout.
    var sample_layout_simulation = VerticalSliceSimulationScript.new(config.duplicate(true))
    steps += _run_visit(sample_layout_simulation)
    var cash_before_sample_load: int = sample_layout_simulation.economy.cash_yen
    if not sample_layout_simulation.try_load_sample_layout("default_layout"):
        _fail("loading a sample that reuses only already-owned fixture ids must always be accepted")
        return
    if sample_layout_simulation.economy.cash_yen != cash_before_sample_load:
        _fail("loading a sample that reuses only already-owned fixtures must not charge anything")
        return
    if sample_layout_simulation.try_load_sample_layout("with_bench"):
        _fail("loading a sample that adds a new fixture must be rejected when unaffordable")
        return
    sample_layout_simulation.economy.cash_yen += 100_000
    if not sample_layout_simulation.try_load_sample_layout("with_bench"):
        _fail("a valid, affordable sample layout must be accepted")
        return
    if not sample_layout_simulation.layout.fixtures_by_id.has("sample-bench-1"):
        _fail("loading the with_bench sample must add its bench fixture")
        return
    var cash_after_bench_load: int = sample_layout_simulation.economy.cash_yen
    if not sample_layout_simulation.try_load_sample_layout("with_bench"):
        _fail("re-loading a sample whose fixtures are all already owned must be accepted")
        return
    if sample_layout_simulation.economy.cash_yen != cash_after_bench_load:
        _fail("re-loading a sample must not charge again for fixtures it already owns")
        return
    if sample_layout_simulation.try_load_sample_layout("does-not-exist"):
        _fail("loading an unknown sample id must be rejected")
        return
    if not sample_layout_simulation.start_next_customer():
        _fail("could not start a customer to test the sample-layout edit lock")
        return
    if sample_layout_simulation.try_load_sample_layout("default_layout"):
        _fail("loading a sample layout must be locked during an active visit, same as other layout edits")
        return
    steps += _run_visit(sample_layout_simulation)

    # A sample that omits a fixture currently holding procured stock must be
    # rejected rather than silently discarding that inventory.
    var orphan_config: Dictionary = config.duplicate(true)
    var orphan_sample: Dictionary = (orphan_config["sample_layouts"][0] as Dictionary).duplicate(true)
    orphan_sample["sample_id"] = "test-only-omits-shelf-2"
    var orphan_fixtures: Array = []
    for fixture in (orphan_sample["fixtures"] as Array):
        if str((fixture as Dictionary)["id"]) != "shelf-2":
            orphan_fixtures.append(fixture)
    orphan_sample["fixtures"] = orphan_fixtures
    orphan_config["sample_layouts"].append(orphan_sample)
    var orphan_simulation = VerticalSliceSimulationScript.new(orphan_config)
    steps += _run_visit(orphan_simulation)
    if orphan_simulation.try_load_sample_layout("test-only-omits-shelf-2"):
        _fail("a sample that omits a fixture holding procured stock must be rejected, not silently discard it")
        return

    var permit_simulation = VerticalSliceSimulationScript.new(config.duplicate(true))
    steps += _run_visit(permit_simulation)
    if permit_simulation.has_permit("tobacco"):
        _fail("a fresh simulation must not start with any permits held")
        return
    if permit_simulation.try_purchase_permit("tobacco"):
        _fail("a permit purchase without sufficient cash must be rejected")
        return
    if permit_simulation.try_purchase_fixture(
        "small_tobacco_vending", "tobacco-shelf-1", Vector2i(4, 10), Vector2i(4, 9)
    ):
        _fail("a permit-gated fixture purchase must be rejected without the permit")
        return
    if permit_simulation.try_procure_product("tobacco", "tobacco-1", "shelf-1"):
        _fail("permit-gated product procurement must be rejected without the permit")
        return

    permit_simulation.economy.cash_yen = 20_000_000
    var cash_before_permit: int = int(permit_simulation.economy.cash_yen)
    if not permit_simulation.try_purchase_permit("tobacco"):
        _fail("an affordable permit purchase must be accepted")
        return
    if not permit_simulation.has_permit("tobacco"):
        _fail("has_permit must reflect a completed permit purchase")
        return
    if permit_simulation.economy.cash_yen != cash_before_permit - 7000000:
        _fail("a permit purchase must deduct exactly its configured fee")
        return
    if permit_simulation.try_purchase_permit("tobacco"):
        _fail("purchasing an already-held permit must be rejected")
        return
    if permit_simulation.event_log.count_type("permit_purchased") != 1:
        _fail("a completed permit purchase must record exactly one permit_purchased event")
        return

    var cash_before_vending_purchase: int = int(permit_simulation.economy.cash_yen)
    if not permit_simulation.try_purchase_fixture(
        "small_tobacco_vending", "tobacco-shelf-1", Vector2i(6, 10), Vector2i(6, 9)
    ):
        _fail("a permit-gated fixture purchase must be accepted once the permit is held")
        return
    if permit_simulation.economy.cash_yen != cash_before_vending_purchase - 600:
        _fail("the tobacco vending fixture purchase must deduct exactly its configured price")
        return

    var cash_before_procurement: int = int(permit_simulation.economy.cash_yen)
    if not permit_simulation.try_procure_product("tobacco", "tobacco-1", "tobacco-shelf-1"):
        _fail("permit-gated product procurement must be accepted once the permit is held")
        return
    var tobacco_catalog_entry: Dictionary = {}
    for catalog_entry in config["product_catalog"]:
        if str(catalog_entry["catalog_id"]) == "tobacco":
            tobacco_catalog_entry = catalog_entry
            break
    var tobacco_vending_catalog_entry: Dictionary = {}
    for fixture_catalog_entry in config["fixture_catalog"]:
        if str(fixture_catalog_entry["catalog_id"]) == "small_tobacco_vending":
            tobacco_vending_catalog_entry = fixture_catalog_entry
            break
    # Task #45: the fixture's own capacity caps how many units actually get
    # procured, which can be lower than the product catalog's own
    # initial_stock_units (itself the category's max_capacity, which can
    # assume a larger fixture than the one actually purchased here).
    var expected_procurement_quantity: int = min(
        int(tobacco_catalog_entry["initial_stock_units"]),
        int(tobacco_vending_catalog_entry["capacity"])
    )
    var expected_procurement_cost: int = (
        expected_procurement_quantity * int(tobacco_catalog_entry["restock_unit_cost_yen"])
    )
    if permit_simulation.economy.cash_yen != cash_before_procurement - expected_procurement_cost:
        _fail("product procurement cost must equal initial stock units times unit cost")
        return
    if permit_simulation.inventory.get_product("tobacco-1").stock_units != expected_procurement_quantity:
        _fail("a procured product must start with its configured initial stock, capped at the fixture's own capacity")
        return
    if permit_simulation.event_log.count_type("product_procured") != 1:
        _fail("a completed product procurement must record exactly one product_procured event")
        return
    if permit_simulation.try_procure_product("tobacco", "tobacco-2", "tobacco-shelf-1"):
        _fail("procuring a second product onto an already-occupied fixture must be rejected")
        return

    # Task #45: small_ambient_shelf's confirmed compatible_product_categories
    # does not include tobacco, so procuring it there must be rejected even
    # though both the permit and the catalog entry are otherwise valid.
    if not permit_simulation.try_purchase_fixture(
        "small_ambient_shelf", "incompatible-shelf-1", Vector2i(8, 10), Vector2i(8, 9)
    ):
        _fail("a valid fixture purchase for the compatibility-rejection test must be accepted")
        return
    if permit_simulation.try_procure_product("tobacco", "tobacco-incompatible", "incompatible-shelf-1"):
        _fail("procuring a product onto a fixture whose compatible_product_categories excludes it must be rejected")
        return
    if not permit_simulation.try_procure_product("bread", "bread-compatible", "incompatible-shelf-1"):
        _fail("procuring a product a fixture's compatible_product_categories does include must be accepted")
        return

    # Task #59: the CONFIRMED_OFFICIAL permit-exclusion distance rule (guide
    # book page 9) is now enforced against town.rival_stores. The default
    # scenario config has no rivals (a no-op, exercised implicitly by
    # permit_simulation above already succeeding with zero rivals present),
    # so this scenario configures its own rivals to exercise the actual
    # enforcement.
    var spatial_config: Dictionary = config.duplicate(true)
    spatial_config["town"] = (spatial_config["town"] as Dictionary).duplicate(true)
    # tobacco's exclusion_distance_tiles is 7: a rival at (6, 0) is distance
    # 6 from the player's store at (0, 0) -- inside the radius.
    spatial_config["town"]["rival_stores"] = [
        {"id": "rival-near-tobacco", "position": [6, 0], "permits_held": ["tobacco"]},
        {"id": "rival-far-alcohol", "position": [50, 50], "permits_held": ["alcohol"]},
    ]
    var spatial_simulation = VerticalSliceSimulationScript.new(spatial_config)
    steps += _run_visit(spatial_simulation)
    spatial_simulation.economy.cash_yen = 20_000_000
    if spatial_simulation.try_purchase_permit("tobacco"):
        _fail("try_purchase_permit() must reject a permit already held (within radius) by a configured rival")
        return
    # alcohol's exclusion_distance_tiles is 11: the rival at (50, 50) is far
    # outside it, and the near rival only holds tobacco, not alcohol -- so
    # alcohol must remain purchasable despite both rivals being configured.
    if not spatial_simulation.try_purchase_permit("alcohol"):
        _fail("try_purchase_permit() must not reject a permit no nearby rival holds")
        return
    # medicine's exclusion_distance_tiles is 15: still well outside either
    # rival's actual holdings, so also purchasable.
    if not spatial_simulation.try_purchase_permit("medicine"):
        _fail("try_purchase_permit() must not reject a permit unrelated to any configured rival's holdings")
        return
    # Moving the same rival just outside tobacco's 7-tile radius (distance
    # exactly 7, the boundary case) must flip the outcome to accepted.
    var boundary_config: Dictionary = config.duplicate(true)
    boundary_config["town"] = (boundary_config["town"] as Dictionary).duplicate(true)
    boundary_config["town"]["rival_stores"] = [
        {"id": "rival-at-boundary", "position": [7, 0], "permits_held": ["tobacco"]},
    ]
    var boundary_simulation = VerticalSliceSimulationScript.new(boundary_config)
    steps += _run_visit(boundary_simulation)
    boundary_simulation.economy.cash_yen = 20_000_000
    if not boundary_simulation.try_purchase_permit("tobacco"):
        _fail("try_purchase_permit() must accept a permit exactly at the exclusion radius boundary")
        return

    var promotion_simulation = VerticalSliceSimulationScript.new(config.duplicate(true))
    steps += _run_visit(promotion_simulation)
    if promotion_simulation.popularity != 0:
        _fail("a freshly reset simulation must start with zero popularity")
        return
    if promotion_simulation.try_purchase_promotion("unknown_promotion"):
        _fail("an unknown promotion id must be rejected")
        return
    var cash_before_scheduling: int = int(promotion_simulation.economy.cash_yen)
    if not promotion_simulation.try_purchase_promotion("direct_mail"):
        _fail("scheduling a promotion before its trigger moment this month must be accepted")
        return
    if promotion_simulation.economy.cash_yen != cash_before_scheduling:
        _fail("a promotion's cost must not be charged until its scheduled event fires")
        return
    if promotion_simulation.event_log.count_type("promotion_scheduled") != 1:
        _fail("a scheduled promotion must record exactly one promotion_scheduled event")
        return
    if promotion_simulation.try_purchase_promotion("direct_mail"):
        _fail("scheduling the same promotion method twice in one month must be rejected")
        return

    var day_count_before_promotion_wait: int = promotion_simulation.day_count
    var promotion_ticks := 0
    while promotion_simulation.popularity == 0 and promotion_ticks < 5000:
        promotion_simulation.tick_idle_for_demand()
        promotion_ticks += 1
    if promotion_ticks >= 5000:
        _fail("the scheduled direct_mail promotion did not fire within 5000 ticks")
        return
    if promotion_simulation.popularity != 12:
        _fail("a fired promotion must apply exactly its configured popularity_gain")
        return
    # Task #47/#50: reaching the promotion's trigger_day crosses at least
    # one day boundary, which now also charges staff wages (scaled to the
    # configured opening_minutes_per_day) for each day crossed.
    var promotion_daily_wages_yen := 0
    for staff_member_config in config["staff"]["members"]:
        promotion_daily_wages_yen += _expected_daily_yen_at_business_hours(
            int(staff_member_config.get("salary_yen_per_day_24h", 0)),
            int(config["demand"]["opening_minutes_per_day"])
        )
    var promotion_days_crossed: int = (
        promotion_simulation.day_count - day_count_before_promotion_wait
    )
    var expected_cash_after_promotion: int = (
        cash_before_scheduling - 100000 - promotion_daily_wages_yen * promotion_days_crossed
    )
    if promotion_simulation.economy.cash_yen != expected_cash_after_promotion:
        _fail("a fired promotion must deduct exactly its configured cost at trigger time")
        return
    if promotion_simulation.event_log.count_type("promotion_fired") != 1:
        _fail("a fired promotion must record exactly one promotion_fired event")
        return
    if promotion_simulation.try_purchase_promotion("newspaper"):
        _fail("scheduling a promotion after its trigger moment has already passed this month must be rejected")
        return

    var town_simulation_no_rivals = VerticalSliceSimulationScript.new(config.duplicate(true))
    if town_simulation_no_rivals.town.population != 2000:
        _fail("the vertical-slice config's town population must be ported into TownState unchanged")
        return
    if town_simulation_no_rivals.demand.rival_store_count != 0:
        _fail("the default vertical-slice config's town has no rivals, so rival_store_count must be zero")
        return
    var expected_default_land_value_yen := 24400000
    if int(town_simulation_no_rivals.snapshot()["land_value_yen"]) != expected_default_land_value_yen:
        _fail("land_value_yen must match LandValuePolicy's formula for the configured town at month 0")
        return

    var rival_town_config: Dictionary = config.duplicate(true)
    rival_town_config["town"]["store_count_including_rivals"] = 4
    var rival_simulation = VerticalSliceSimulationScript.new(rival_town_config)
    if rival_simulation.demand.rival_store_count != 3:
        _fail("rival_store_count must equal store_count_including_rivals minus the player's own store")
        return
    var no_rival_rate: float = town_simulation_no_rivals.demand.expected_arrivals_per_minute()
    var rival_rate: float = rival_simulation.demand.expected_arrivals_per_minute()
    var expected_rival_rate: float = no_rival_rate * (1.0 - 0.24)
    if abs(rival_rate - expected_rival_rate) > 0.0000001:
        _fail("rival dilution must reduce expected arrivals by RIVAL_DILUTION_PER_COMPETITOR per rival")
        return

    var capped_rival_config: Dictionary = config.duplicate(true)
    capped_rival_config["town"]["store_count_including_rivals"] = 31
    var capped_rival_simulation = VerticalSliceSimulationScript.new(capped_rival_config)
    if capped_rival_simulation.demand.rival_store_count != 30:
        _fail("rival_store_count must equal store_count_including_rivals minus the player's own store")
        return
    var capped_rate: float = capped_rival_simulation.demand.expected_arrivals_per_minute()
    var expected_capped_rate: float = no_rival_rate * (1.0 - 0.6)
    if abs(capped_rate - expected_capped_rate) > 0.0000001:
        _fail("rival dilution must be capped at MAX_RIVAL_DILUTION even with many rivals")
        return

    var land_value_policy = LandValuePolicyScript.new()
    var fully_developed_town = TownStateScript.new({"population": 20000, "store_count_including_rivals": 8})
    var max_development_price: int = land_value_policy.current_land_price_yen(
        20000000, fully_developed_town, 0.0
    )
    if max_development_price != 60000000:
        _fail("a town at or above both development reference points must reach the maximum local development factor")
        return
    var inflated_price: int = land_value_policy.current_land_price_yen(
        20000000, fully_developed_town, 1.0
    )
    var expected_inflated_price: int = int(round(20000000 * 3.0 * 1.05))
    if inflated_price != expected_inflated_price:
        _fail("current_land_price_yen must apply the annual inflation rate for elapsed_years > 0")
        return

    var store_rating = StoreRatingScript.new()
    var star_breakpoints := {
        0: 0, 19: 0, 20: 1, 39: 1, 40: 2, 59: 2, 60: 3, 79: 3, 80: 4, 99: 4, 100: 5,
    }
    for internal_value in star_breakpoints:
        if store_rating.star_rank_for_internal_value(internal_value) != star_breakpoints[internal_value]:
            _fail("star_rank_for_internal_value must match the guide's confirmed breakpoints")
            return

    var upgrade_and_downgrade_evaluation: Dictionary = store_rating.evaluate_monthly_rating_change(
        0, -5, 60.0, 75.0, 0.0, 0
    )
    # Task #86: internal value 0 is a ☆☆☆☆☆ store, evaluated against the
    # 0-star row both printed tables carry (-1% / 50 / 70 / 80 / 300万円).
    if int(upgrade_and_downgrade_evaluation["criteria_met"]) != 3:
        _fail("exactly 3 of the 5 zero-star-row upgrade criteria must be counted as met")
        return
    if not bool(upgrade_and_downgrade_evaluation["upgrade_applies"]):
        _fail("meeting >= UPGRADE_MIN_CRITERIA_MET criteria must apply the upgrade")
        return
    if int(upgrade_and_downgrade_evaluation["downgrade_points"]) != -2:
        _fail("downgrade points must equal -1 per failed downgrade criterion")
        return
    if int(upgrade_and_downgrade_evaluation["next_internal_value"]) != 3:
        _fail("next_internal_value must equal current + downgrade_points + UPGRADE_POINTS, clamped 0..100")
        return
    var zero_star_row_evaluation: Dictionary = store_rating.evaluate_monthly_rating_change(
        10, -1, 50.0, 70.0, 80.0, 3000000
    )
    if int(zero_star_row_evaluation["criteria_met"]) != 5 or int(zero_star_row_evaluation["downgrade_points"]) != 0:
        _fail("a zero-star store must be judged by its own printed row, not the one-star row")
        return

    var store_value = StoreValueScript.new()
    var service_value_check: float = store_value.compute_service_value([10, 30], [2, 4])
    if abs(service_value_check - 26.0) > 0.0000001:
        _fail("compute_service_value must equal the staff average plus the summed fixture bonuses")
        return
    var security_value_check: float = store_value.compute_security_value([10, 20], "small")
    if abs(security_value_check - 45.0) > 0.0000001:
        _fail("compute_security_value must equal the summed staff skill times the size-tier multiplier")
        return
    var cleaning_value_check: float = store_value.compute_cleaning_value([5, 15], "large")
    if abs(cleaning_value_check - 36.0) > 0.0000001:
        _fail("compute_cleaning_value must equal the summed staff skill times the size-tier multiplier")
        return

    var checkout_timing = CheckoutTimingScript.new()
    if checkout_timing.required_ticks(checkout_timing.REFERENCE_REGISTER_SKILL, 3) != 3:
        _fail("required_ticks must return reference_ticks unchanged exactly at REFERENCE_REGISTER_SKILL")
        return
    if checkout_timing.required_ticks(checkout_timing.REFERENCE_REGISTER_SKILL * 2, 3) != 2:
        _fail("required_ticks must decrease for a register_skill above the reference")
        return
    if checkout_timing.required_ticks(1, 3) != checkout_timing.REFERENCE_REGISTER_SKILL * 3:
        _fail("required_ticks must scale up sharply for a very low register_skill")
        return
    if checkout_timing.required_ticks(0, 3) != checkout_timing.REFERENCE_REGISTER_SKILL * 3:
        _fail("required_ticks must use the zero-skill guard rather than dividing by zero")
        return
    if checkout_timing.required_ticks(1000, 3) != checkout_timing.MIN_CHECKOUT_TICKS:
        _fail("required_ticks must never fall below MIN_CHECKOUT_TICKS")
        return

    var restock_timing = RestockTimingScript.new()
    if restock_timing.required_ticks(restock_timing.REFERENCE_REPLENISHMENT_SKILL, 3) != 3:
        _fail("required_ticks must return reference_ticks unchanged exactly at REFERENCE_REPLENISHMENT_SKILL")
        return
    if restock_timing.required_ticks(restock_timing.REFERENCE_REPLENISHMENT_SKILL * 2, 3) != 2:
        _fail("required_ticks must decrease for a replenishment_skill above the reference")
        return
    if restock_timing.required_ticks(1, 3) != restock_timing.REFERENCE_REPLENISHMENT_SKILL * 3:
        _fail("required_ticks must scale up sharply for a very low replenishment_skill")
        return
    if restock_timing.required_ticks(0, 3) != restock_timing.REFERENCE_REPLENISHMENT_SKILL * 3:
        _fail("required_ticks must use the zero-skill guard rather than dividing by zero")
        return
    if restock_timing.required_ticks(1000, 3) != restock_timing.MIN_RESTOCK_TICKS:
        _fail("required_ticks must never fall below MIN_RESTOCK_TICKS")
        return

    # Task #48: StaffGrowth unit coverage, isolated from the full
    # simulation the way CheckoutTiming/RestockTiming are tested above.
    var growth = StaffGrowthScript.new()
    var growth_staff = StaffStateScript.new({
        "id": "growth-test-staff",
        "start_subcell": [0, 0],
        "register_skill": 10,
        "service_skill": 10,
        "replenishment_skill": 10,
        "cleaning_skill": 10,
        "security_skill": 10,
        "register_skill_growth_ceiling": 12,
        "service_skill_growth_ceiling": 10,
        "replenishment_skill_growth_ceiling": 12,
        "cleaning_skill_growth_ceiling": 12,
        "security_skill_growth_ceiling": 12,
    })
    var checkout_growth_result: Array[Dictionary] = growth.apply_checkout_growth(growth_staff)
    if growth_staff.register_skill != 11:
        _fail("apply_checkout_growth must grow register_skill by the unit growth")
        return
    if growth_staff.service_skill != 10:
        _fail("apply_checkout_growth must not grow a skill already at its own growth ceiling")
        return
    if checkout_growth_result.size() != 1 or str(checkout_growth_result[0]["skill"]) != "register_skill":
        _fail("apply_checkout_growth must report only the skill that actually grew")
        return

    var replenish_growth_result: Array[Dictionary] = growth.apply_replenish_growth(growth_staff)
    if (
        growth_staff.replenishment_skill != 11
        or growth_staff.cleaning_skill != 11
        or growth_staff.security_skill != 11
    ):
        _fail("apply_replenish_growth must grow replenishment/cleaning/security skills by the unit growth")
        return
    if replenish_growth_result.size() != 3:
        _fail("apply_replenish_growth must report every skill that grew")
        return

    growth.apply_checkout_growth(growth_staff)
    if growth_staff.register_skill != 12:
        _fail("apply_checkout_growth must grow register_skill up to its own ceiling")
        return
    var clamped_growth_result: Array[Dictionary] = growth.apply_checkout_growth(growth_staff)
    if not clamped_growth_result.is_empty():
        _fail("apply_checkout_growth must report no growth once every mapped skill is at its ceiling")
        return
    growth_staff.reset()
    if growth_staff.register_skill != 10 or growth_staff.replenishment_skill != 10:
        _fail("StaffState.reset() must restore every skill to its config-derived starting value")
        return

    # Task #49: CheckoutAnger unit coverage, isolated the same way.
    var anger = CheckoutAngerScript.new()
    if anger.trigger_ticks(3) != 6:
        _fail("trigger_ticks must scale the reference duration by TRIGGER_MULTIPLIER")
        return
    var anger_staff = StaffStateScript.new({
        "id": "anger-test-staff",
        "start_subcell": [0, 0],
        "register_skill": 10,
        "service_skill": 1,
        "replenishment_skill": 10,
        "cleaning_skill": 10,
        "security_skill": 10,
        "register_skill_growth_ceiling": 10,
        "service_skill_growth_ceiling": 10,
        "replenishment_skill_growth_ceiling": 10,
        "cleaning_skill_growth_ceiling": 10,
        "security_skill_growth_ceiling": 10,
    })
    var penalty_results: Dictionary = anger.apply_penalty(anger_staff)
    if (
        anger_staff.register_skill != 8
        or anger_staff.replenishment_skill != 8
        or anger_staff.cleaning_skill != 8
        or anger_staff.security_skill != 8
    ):
        _fail("apply_penalty must lower register/replenishment/cleaning/security skills by exactly 2")
        return
    if anger_staff.service_skill != 0:
        _fail("apply_penalty must clamp a skill at MINIMUM_SKILL_VALUE rather than going negative")
        return
    if (
        int(penalty_results["service_skill"]["before"]) != 1
        or int(penalty_results["service_skill"]["after"]) != 0
    ):
        _fail("apply_penalty must report the actual before/after values, not the unclamped delta")
        return

    var customer_share = CustomerShareScript.new()
    if customer_share.compute_customer_share_percent(100, 100.0, 100.0, 100.0, 30, 1440) != 100:
        _fail("compute_customer_share_percent must score 100 when every factor is maxed out")
        return
    if customer_share.compute_customer_share_percent(0, 0.0, 0.0, 0.0, 0, 0) != 0:
        _fail("compute_customer_share_percent must score 0 when every factor is at its floor")
        return
    if customer_share.compute_customer_share_percent(0, 150.0, 0.0, 0.0, 0, 0) != int(
        round(customer_share.SERVICE_WEIGHT * 100.0)
    ):
        _fail("compute_customer_share_percent must clamp a service_value above 100 to 100")
        return

    var maintenance_config: Dictionary = config.duplicate(true)
    maintenance_config["demand"] = {
        "nearby_population": 0,
        "customer_share_percent": 0.0,
        "daily_visit_rate_per_population": 0.0,
        "opening_minutes_per_day": 960,
        "bad_weather_visit_multiplier": 0.0,
        "is_bad_weather": false,
        "rng_seed": 17,
    }
    var maintenance_simulation = VerticalSliceSimulationScript.new(maintenance_config)
    steps += _run_visit(maintenance_simulation)
    if maintenance_simulation.event_log.count_type("fixture_maintenance_charged") != 0:
        _fail("a day with no catalog-purchased fixtures must not record a fixture_maintenance_charged event")
        return
    var bench_catalog_entry: Dictionary = {}
    for fixture_catalog_entry in config["fixture_catalog"]:
        if str(fixture_catalog_entry["catalog_id"]) == "bench":
            bench_catalog_entry = fixture_catalog_entry
            break
    maintenance_simulation.economy.cash_yen = 1_000_000
    if not maintenance_simulation.try_purchase_fixture(
        "bench", "maintenance-bench-1", Vector2i(8, 10), Vector2i(8, 9)
    ):
        _fail("a valid fixture purchase for the maintenance test must be accepted")
        return
    var cash_before_maintenance: int = int(maintenance_simulation.economy.cash_yen)
    var maintenance_ticks := 0
    while maintenance_simulation.day_count < 1 and maintenance_ticks < 20000:
        maintenance_simulation.tick_idle_for_demand()
        maintenance_ticks += 1
    if maintenance_ticks >= 20000:
        _fail("advancing past the first day boundary took too long (maintenance test)")
        return
    if maintenance_simulation.event_log.count_type("fixture_maintenance_charged") != 1:
        _fail("exactly one fixture_maintenance_charged event must be recorded per day boundary crossed")
        return
    var maintenance_opening_minutes_per_day: int = int(maintenance_config["demand"]["opening_minutes_per_day"])
    var expected_daily_maintenance_yen: int = _expected_daily_yen_at_business_hours(
        int(bench_catalog_entry["maintenance_yen_per_day"]), maintenance_opening_minutes_per_day
    )
    # Task #47/#50: the same day boundary also charges each active staff
    # member's own salary_yen_per_day_24h, scaled to the configured
    # opening_minutes_per_day (exactly one day's worth here, since the loop
    # above stops at the first day boundary crossed).
    var expected_daily_wages_yen := 0
    for staff_member_config in config["staff"]["members"]:
        expected_daily_wages_yen += _expected_daily_yen_at_business_hours(
            int(staff_member_config.get("salary_yen_per_day_24h", 0)),
            maintenance_opening_minutes_per_day
        )
    var expected_cash_after_maintenance: int = (
        cash_before_maintenance - expected_daily_maintenance_yen - expected_daily_wages_yen
    )
    if maintenance_simulation.economy.cash_yen != expected_cash_after_maintenance:
        _fail("daily fixture maintenance must deduct exactly the sum of every owned fixture's maintenance_yen_per_day")
        return
    if maintenance_simulation.event_log.count_type("staff_wages_charged") != 1:
        _fail("exactly one staff_wages_charged event must be recorded per day boundary crossed")
        return

    var rating_config: Dictionary = config.duplicate(true)
    rating_config["demand"] = {
        "nearby_population": 0,
        "customer_share_percent": 0.0,
        "daily_visit_rate_per_population": 0.0,
        "opening_minutes_per_day": 960,
        "bad_weather_visit_multiplier": 0.0,
        "is_bad_weather": false,
        "rng_seed": 13,
    }
    var rating_simulation = VerticalSliceSimulationScript.new(rating_config)
    if rating_simulation.internal_rating_value != 0 or rating_simulation.star_rating != 0:
        _fail("a freshly reset simulation must start at internal_rating_value 0 / star_rating 0")
        return
    steps += _run_visit(rating_simulation)
    var single_sale_revenue_yen: int = rating_simulation.economy.recorded_revenue_yen()

    var rating_ticks := 0
    while (
        rating_simulation.day_count < REPRESENTATIVE_DAYS_PER_MONTH_FOR_TEST
        and rating_ticks < 20000
    ):
        rating_simulation.tick_idle_for_demand()
        rating_ticks += 1
    if rating_ticks >= 20000:
        _fail("advancing to the end of the representative month took too long (store rating test)")
        return
    if rating_simulation.event_log.count_type("store_rating_evaluated") != 1:
        _fail("exactly one store_rating_evaluated event must be recorded at month end")
        return

    var rating_event_details: Dictionary = {}
    for record in rating_simulation.event_log.records:
        if record["event_type"] == "store_rating_evaluated":
            rating_event_details = record["details"]
    var expected_monthly_sales_yen: int = single_sale_revenue_yen * MONTH_MULTIPLIER_FOR_TEST
    if int(rating_event_details["monthly_sales_yen"]) != expected_monthly_sales_yen:
        _fail("monthly_sales_yen fed into the store rating must equal the representative month's revenue x8")
        return
    # Task #48: the single checkout _run_visit() completed above is itself a
    # confirmed work-growth trigger, so staff-1's service_skill (and
    # register_skill) may already have grown past its config starting value
    # by the time this month-end rating fires -- service_value is therefore
    # read from the staff roster's own current (post-growth) state rather
    # than the pre-task-#48 hardcoded 17.0 average.
    var expected_service_value: float = 0.0
    var rating_staff: Array = rating_simulation.staff.all_staff()
    for rating_staff_member in rating_staff:
        expected_service_value += float(rating_staff_member.service_skill)
    expected_service_value /= rating_staff.size()
    if abs(float(rating_event_details["service_value"]) - expected_service_value) > 0.0000001:
        _fail("service_value must equal the average staff service_skill plus any fixture service bonuses")
        return
    # Task #91: summed over the whole roster (3 since the manager slot was
    # added) times the small store's 1.5 size-tier multiplier, instead of a
    # literal worked out for the old 2-person roster.
    var expected_security_value := 0.0
    var expected_cleaning_value := 0.0
    for rating_staff_member in rating_staff:
        expected_security_value += float(rating_staff_member.security_skill) * 1.5
        expected_cleaning_value += float(rating_staff_member.cleaning_skill) * 1.5
    if abs(float(rating_event_details["security_value"]) - expected_security_value) > 0.0000001:
        _fail("security_value must equal total staff security_skill times the store's size-tier multiplier")
        return
    if abs(float(rating_event_details["cleaning_value"]) - expected_cleaning_value) > 0.0000001:
        _fail("cleaning_value must equal total staff cleaning_skill times the store's size-tier multiplier")
        return
    # popularity=0, cleaning/security as computed above, 2 distinct stocked
    # products (assortment_score=10.0), opening_minutes_per_day=960
    # (hours_score=66.6667); service_value is expected_service_value above
    # (growth-dependent, see comment there). Recomputed with the same
    # CustomerShare class store_rating actually calls, rather than a
    # hand-derived literal that would go stale the moment checkout growth
    # changes service_value.
    var expected_customer_share_percent: int = customer_share.compute_customer_share_percent(
        0, expected_service_value, expected_cleaning_value, expected_security_value, 2, 960
    )
    if int(rating_event_details["customer_share_percent"]) != expected_customer_share_percent:
        _fail("customer_share_percent must be recomputed from CustomerShare.compute_customer_share_percent()")
        return
    if abs(rating_simulation.demand.customer_share_percent - float(expected_customer_share_percent)) > 0.0000001:
        _fail("demand.customer_share_percent must be overwritten by the monthly store rating evaluation")
        return
    if rating_simulation.star_rating != store_rating.star_rank_for_internal_value(
        rating_simulation.internal_rating_value
    ):
        _fail("star_rating must always equal star_rank_for_internal_value(internal_rating_value)")
        return
    if int(rating_simulation.snapshot()["star_rating"]) != rating_simulation.star_rating:
        _fail("snapshot() must expose the same star_rating the simulation tracks")
        return

    # Task #85: weather rolled from the CONFIRMED_OFFICIAL monthly table.
    var weather_categories: Array = config["weather"]["categories"]
    var weather_simulation = VerticalSliceSimulationScript.new(config.duplicate(true))
    for category_index in range(weather_categories.size()):
        weather_simulation._apply_weather(category_index)
        var expected_bad_weather: bool = config["weather"]["bad_weather_categories"].has(weather_categories[category_index])
        if weather_simulation.demand.is_bad_weather != expected_bad_weather:
            _fail("each weather category must set demand.is_bad_weather from bad_weather_categories")
            return
    # The bundled Noto Sans JP subset only contains glyphs the UI uses
    # (tools/build_conveni_font.py); a missing one renders as a blank box.
    var bundled_font: FontFile = load("res://fonts/ConveniJP.ttf")
    for weather_label_text in config["weather"]["display_labels"] + ["［", "］"]:
        for weather_character in str(weather_label_text):
            if not bundled_font.has_char(weather_character.unicode_at(0)):
                _fail("the bundled ConveniJP.ttf subset must contain every weather HUD glyph")
                return
    weather_simulation._apply_weather(3)
    if weather_simulation.weather_display_label() != "雨":
        _fail("the 雨・雪 weather category must display as the observed original HUD string 雨")
        return
    var weather_month_config: Dictionary = config.duplicate(true)
    weather_month_config["weather"]["monthly_percentages"][0] = [100, 0, 0, 0, 0]
    weather_month_config["weather"]["monthly_percentages"][1] = [0, 0, 0, 0, 100]
    var weather_month_simulation = VerticalSliceSimulationScript.new(weather_month_config)
    if weather_month_simulation.weather_category() != "快晴":
        _fail("the first day's weather must be rolled from month 1's row")
        return
    while weather_month_simulation.month_count == 0:
        weather_month_simulation._handle_day_boundary()
        if weather_month_simulation.month_count == 0 and weather_month_simulation.weather_category() != "快晴":
            _fail("every day of month 1 must keep rolling from month 1's row")
            return
    if weather_month_simulation.weather_category() != "荒天":
        _fail("the first day after a month rollover must roll from the new month's row")
        return
    var weather_twin_a = VerticalSliceSimulationScript.new(config.duplicate(true))
    var weather_twin_b = VerticalSliceSimulationScript.new(config.duplicate(true))
    for weather_day in range(12):
        if weather_twin_a.weather_category_index != weather_twin_b.weather_category_index:
            _fail("the same weather.rng_seed must reproduce the same daily weather sequence")
            return
        weather_twin_a._handle_day_boundary()
        weather_twin_b._handle_day_boundary()

    var save_config: Dictionary = config.duplicate(true)
    save_config["demand"] = {
        "nearby_population": 0,
        "customer_share_percent": 0.0,
        "daily_visit_rate_per_population": 0.0,
        "opening_minutes_per_day": 960,
        "bad_weather_visit_multiplier": 0.0,
        "is_bad_weather": false,
        "rng_seed": 19,
    }
    var save_simulation = VerticalSliceSimulationScript.new(save_config)
    steps += _run_visit(save_simulation)
    save_simulation.economy.cash_yen = 1_000_000
    if not save_simulation.try_purchase_fixture(
        "potted_plant", "amenity-save-1", Vector2i(1, 10), Vector2i(1, 9)
    ):
        _fail("the save/load test's fixture purchase setup must be accepted")
        return
    if not save_simulation.try_purchase_promotion("direct_mail"):
        _fail("the save/load test's promotion scheduling setup must be accepted")
        return
    # Task #56: a staff hire is a durable roster fact like the fixture/
    # promotion setup above -- staff.reset() (called by load_state()) would
    # otherwise silently revert staff-2 back to its config-derived default
    # candidate (sugawara_fumio) if staff_roster were not itself saved and
    # reapplied.
    if not save_simulation.try_hire_candidate("staff-2", "takenaka_sayuri"):
        _fail("the save/load test's staff hire setup must be accepted")
        return
    var save_setup_ticks := 0
    while (
        save_simulation.day_count < REPRESENTATIVE_DAYS_PER_MONTH_FOR_TEST
        and save_setup_ticks < 20000
    ):
        save_simulation.tick_idle_for_demand()
        save_setup_ticks += 1
    if save_setup_ticks >= 20000:
        _fail("advancing the save/load test's setup simulation took too long")
        return
    if save_simulation.month_count != 1 or save_simulation.popularity != 12:
        _fail("the save/load test's setup simulation must have settled one month and fired its promotion")
        return

    # Task #85: a weather different from whatever a fresh simulation rolls,
    # so the round trip below proves it was actually restored.
    save_simulation._apply_weather(4)
    var save_data: Dictionary = save_simulation.save_state()
    var loaded_simulation = VerticalSliceSimulationScript.new(save_config)
    if not loaded_simulation.load_state(save_data):
        _fail("loading a save produced by save_state() for the same config must be accepted")
        return
    if loaded_simulation.economy.cash_yen != save_simulation.economy.cash_yen:
        _fail("a loaded simulation must restore the exact saved cash")
        return
    if loaded_simulation.day_count != save_simulation.day_count:
        _fail("a loaded simulation must restore the exact saved day_count")
        return
    if loaded_simulation.month_count != save_simulation.month_count:
        _fail("a loaded simulation must restore the exact saved month_count")
        return
    if loaded_simulation.popularity != save_simulation.popularity:
        _fail("a loaded simulation must restore the exact saved popularity")
        return
    if loaded_simulation.internal_rating_value != save_simulation.internal_rating_value:
        _fail("a loaded simulation must restore the exact saved internal_rating_value")
        return
    if loaded_simulation.layout.fixture_origin("amenity-save-1") != Vector2i(1, 10):
        _fail("a loaded simulation must restore the exact saved fixture layout")
        return
    if loaded_simulation.inventory.total_stock_units() != save_simulation.inventory.total_stock_units():
        _fail("a loaded simulation must restore the exact saved inventory stock")
        return
    if loaded_simulation.staff.members["staff-2"].candidate_id != "takenaka_sayuri":
        _fail("a loaded simulation must restore the exact saved staff hire (staff-2 -> takenaka_sayuri)")
        return
    if loaded_simulation.staff.members["staff-1"].candidate_id != "manda_machiko":
        _fail("a loaded simulation must leave an un-hired-into staff slot at its config-derived default")
        return
    if loaded_simulation.weather_category_index != 4 or not loaded_simulation.demand.is_bad_weather:
        _fail("a loaded simulation must restore the saved weather and its bad-weather demand flag")
        return
    # +1: load_state() admits a fresh default customer once the loaded
    # layout is in place (customer/staff walk state is not saved/restored
    # -- see save_state()'s own comment), recording one more
    # customer_entered event on top of the restored history.
    if loaded_simulation.event_log.records.size() != save_simulation.event_log.records.size() + 1:
        _fail("a loaded simulation must restore the saved event log plus its own fresh customer_entered event")
        return
    if loaded_simulation.economy.sale_records.size() != save_simulation.economy.sale_records.size():
        _fail("a loaded simulation must restore the exact saved sale records")
        return
    if loaded_simulation.economy.month_end_records.size() != save_simulation.economy.month_end_records.size():
        _fail("a loaded simulation must restore the exact saved month-end records")
        return

    var mismatched_scenario_data: Dictionary = save_data.duplicate(true)
    mismatched_scenario_data["scenario_id"] = "wrong-scenario"
    if loaded_simulation.load_state(mismatched_scenario_data):
        _fail("loading a save with a different scenario_id must be rejected")
        return
    var mismatched_schema_data: Dictionary = save_data.duplicate(true)
    mismatched_schema_data["config_schema_version"] = -1
    if loaded_simulation.load_state(mismatched_schema_data):
        _fail("loading a save with a different config_schema_version must be rejected")
        return

    # Task #74: a genuine save/load bug found by directly auditing
    # load_state() against reset()'s own gap-clearing (the user asked to
    # check for gaps, not just add a new feature). reset() has always
    # cleared _checkout_queue right after resetting customers/staff;
    # load_state() never did, so a save taken while a second customer was
    # queued at checkout left that customer_id behind after customers.
    # reset() had already discarded the actual customer record -- the next
    # _dispatch_checkout_queue() call would then null-dereference it and
    # crash. Reproduce the queued state, then confirm a save/load round
    # trip is safe and the loaded simulation keeps running afterward.
    var queue_bug_config: Dictionary = config.duplicate(true)
    queue_bug_config["customer"]["max_concurrent_customers"] = 2
    var queue_bug_simulation = VerticalSliceSimulationScript.new(queue_bug_config)
    steps += _run_visit(queue_bug_simulation)
    var queue_bug_plan: Array[String] = ["prototype-bread"]
    if not queue_bug_simulation.start_explicit_customer("queue-bug-a", queue_bug_plan):
        _fail("queue-bug scenario: first customer could not be admitted")
        return
    if not queue_bug_simulation.start_explicit_customer("queue-bug-b", queue_bug_plan):
        _fail("queue-bug scenario: second customer could not be admitted")
        return
    var queue_bug_steps := 0
    while queue_bug_simulation._checkout_queue.is_empty() and queue_bug_steps < MAX_STEPS:
        queue_bug_simulation.step()
        queue_bug_steps += 1
    if queue_bug_simulation._checkout_queue.is_empty():
        _fail("queue-bug scenario: never got a second customer queued at checkout")
        return
    steps += queue_bug_steps

    var queue_bug_save_data: Dictionary = queue_bug_simulation.save_state()
    var queue_bug_loaded = VerticalSliceSimulationScript.new(queue_bug_config)
    if not queue_bug_loaded.load_state(queue_bug_save_data):
        _fail("loading a save taken with a non-empty checkout queue must be accepted")
        return
    if not queue_bug_loaded._checkout_queue.is_empty():
        _fail("load_state() must clear _checkout_queue like reset() does -- a stale queued customer_id no longer exists in the freshly-reset roster")
        return
    var queue_bug_post_load_steps := 0
    while not queue_bug_loaded.customers.all_settled() and queue_bug_post_load_steps < MAX_STEPS:
        queue_bug_loaded.step()
        queue_bug_post_load_steps += 1
    if queue_bug_post_load_steps >= MAX_STEPS:
        _fail("the loaded simulation did not settle after a save/load round trip taken mid-checkout-queue")
        return
    steps += queue_bug_post_load_steps

    var save_service = SaveGameServiceScript.new()
    var test_save_path := "user://saves/headless_smoke_test_save.json"
    save_service.delete_save(test_save_path)
    if save_service.load_from_path(save_simulation, test_save_path):
        _fail("loading from a path with no save file must be rejected")
        return
    if not save_service.save_to_path(save_simulation, test_save_path):
        _fail("saving to a writable user:// path must succeed")
        return
    if not save_service.save_exists(test_save_path):
        _fail("save_exists must report true once a save has been written")
        return
    var file_loaded_simulation = VerticalSliceSimulationScript.new(save_config)
    if not save_service.load_from_path(file_loaded_simulation, test_save_path):
        _fail("loading a save file just written by save_to_path must succeed")
        return
    if file_loaded_simulation.economy.cash_yen != save_simulation.economy.cash_yen:
        _fail("a save file round trip must preserve the exact saved cash")
        return
    if file_loaded_simulation.popularity != save_simulation.popularity:
        _fail("a save file round trip must preserve the exact saved popularity")
        return
    save_service.delete_save(test_save_path)
    if save_service.save_exists(test_save_path):
        _fail("delete_save must remove the save file")
        return

    var chain_visitor_milestone = ChainVisitorMilestoneScript.new()
    if not chain_visitor_milestone.observe_total_visitors(5000, 1, 9).is_empty():
        _fail("observing a total below the next threshold must not schedule an event")
        return
    var milestone_event: Dictionary = chain_visitor_milestone.observe_total_visitors(10000, 1, 9)
    if milestone_event.is_empty():
        _fail("observing an exact threshold multiple must schedule an event")
        return
    if int(milestone_event["trigger_day_index"]) != 2 or int(milestone_event["trigger_hour"]) != 0:
        _fail("a milestone must trigger at 00:00 on the day after it was observed")
        return
    if int(milestone_event["popularity_gain"]) != 100:
        _fail("a milestone's popularity gain must be exactly 100")
        return
    if not chain_visitor_milestone.pop_due(1, 23).is_empty():
        _fail("a milestone must not be due before its trigger day")
        return
    var due_events: Array[Dictionary] = chain_visitor_milestone.pop_due(2, 0)
    if due_events.size() != 1:
        _fail("a milestone must become due at exactly its trigger day/hour")
        return
    if not chain_visitor_milestone.pop_due(2, 0).is_empty():
        _fail("a fired milestone must not be popped as due a second time")
        return

    var store_events = StoreEventsScript.new()
    if store_events.magazine_or_contest_event_is_eligible(9999, 5):
        _fail("magazine/contest eligibility must require population >= 10000")
        return
    if store_events.magazine_or_contest_event_is_eligible(10000, 4):
        _fail("magazine/contest eligibility must require store_count_including_rivals >= 5")
        return
    if not store_events.magazine_or_contest_event_is_eligible(10000, 5):
        _fail("magazine/contest eligibility must accept the exact threshold values")
        return
    if store_events.compute_contest_prize_yen(7) != 70000000:
        _fail("the contest prize must equal store_count_including_rivals x 10,000,000 yen")
        return

    var chain_config: Dictionary = config.duplicate(true)
    chain_config["demand"] = {
        "nearby_population": 0,
        "customer_share_percent": 0.0,
        "daily_visit_rate_per_population": 0.0,
        "opening_minutes_per_day": 960,
        "bad_weather_visit_multiplier": 0.0,
        "is_bad_weather": false,
        "rng_seed": 23,
    }
    var chain_simulation = VerticalSliceSimulationScript.new(chain_config)
    if chain_simulation.player_store_count != 1:
        _fail("a freshly reset simulation must start with exactly one store in the chain")
        return
    steps += _run_visit(chain_simulation)
    var expansion_cost_yen: int = chain_simulation.chain_expansion_cost_yen()
    # Task #65: opening a new branch must cost exactly the guide's confirmed
    # 4-area land price (地価（4エリア分）), not the bare per-area rate
    # try_expand_chain() previously charged with an implicit ×1.
    var land_value_policy_check = LandValuePolicyScript.new()
    var expected_expansion_cost_yen: int = (
        land_value_policy_check.current_land_price_yen(
            VerticalSliceSimulationScript.BASE_LAND_PRICE_YEN,
            chain_simulation.town,
            float(chain_simulation.month_count) / chain_simulation.MONTHS_PER_YEAR
        ) * VerticalSliceSimulationScript.NEW_BRANCH_LAND_AREA_COUNT
    )
    if expansion_cost_yen != expected_expansion_cost_yen:
        _fail("chain_expansion_cost_yen must equal the per-area land price times the confirmed 4-area count")
        return
    if chain_simulation.try_expand_chain():
        _fail("expanding the chain without sufficient cash must be rejected")
        return
    chain_simulation.economy.cash_yen = expansion_cost_yen
    var cash_before_expansion: int = int(chain_simulation.economy.cash_yen)
    if not chain_simulation.try_expand_chain():
        _fail("expanding the chain with exactly sufficient cash must be accepted")
        return
    if chain_simulation.player_store_count != 2:
        _fail("a successful chain expansion must increment player_store_count by exactly 1")
        return
    if chain_simulation.economy.cash_yen != cash_before_expansion - expansion_cost_yen:
        _fail("a chain expansion must deduct exactly its computed cost")
        return
    if chain_simulation.event_log.count_type("chain_expanded") != 1:
        _fail("a successful chain expansion must record exactly one chain_expanded event")
        return
    if chain_simulation.clear_condition_met:
        _fail("clear_condition_met must not be set before reaching the scenario's store-count target")
        return

    var chain_snapshot: Dictionary = chain_simulation.snapshot()
    if int(chain_snapshot["player_store_count"]) != 2:
        _fail("snapshot() must expose the current player_store_count")
        return
    if int(chain_snapshot["chain_expansion_cost_yen"]) != chain_simulation.chain_expansion_cost_yen():
        _fail("snapshot() must expose the current chain_expansion_cost_yen")
        return

    chain_simulation.player_store_count = 10
    chain_simulation._evaluate_terminal_state()
    if not chain_simulation.clear_condition_met:
        _fail("clear_condition_met must be set once player_store_count reaches the scenario target")
        return

    var milestone_simulation = VerticalSliceSimulationScript.new(chain_config)
    steps += _run_visit(milestone_simulation)
    if milestone_simulation.popularity != 0:
        _fail("a freshly reset simulation must start with zero popularity (chain milestone test)")
        return
    milestone_simulation._chain_visitor_milestone.observe_total_visitors(
        10000, milestone_simulation.day_count + 1, milestone_simulation.minute_of_day / 60
    )
    var milestone_ticks := 0
    while milestone_simulation.popularity == 0 and milestone_ticks < 20000:
        milestone_simulation.tick_idle_for_demand()
        milestone_ticks += 1
    if milestone_ticks >= 20000:
        _fail("the observed chain visitor milestone did not fire within 20000 ticks")
        return
    if milestone_simulation.popularity != 100:
        _fail("a fired chain visitor milestone must apply exactly its configured popularity_gain")
        return
    if milestone_simulation.event_log.count_type("chain_visitor_milestone_fired") != 1:
        _fail("a fired chain visitor milestone must record exactly one event")
        return

    # Task #38: the economy-action buttons/OptionButtons main.gd wires up
    # (buy fixture, buy permit, stock product, restock, buy promotion,
    # expand chain) previously had no coverage beyond the underlying
    # simulation methods, since those methods were never reachable from the
    # UI at all. This exercises main.gd itself (unlike the rest of this
    # file, which drives vertical_slice_simulation.gd directly), so the
    # scene must actually enter the tree for its @onready bindings to
    # resolve.
    var economy_ui_scene: Node = (load(MAIN_SCENE_PATH) as PackedScene).instantiate()
    get_root().add_child(economy_ui_scene)
    await process_frame
    while not economy_ui_scene.simulation.customers.all_settled():
        economy_ui_scene.simulation.step()
        steps += 1
    economy_ui_scene.simulation.economy.cash_yen += 50_000_000

    # Task #76: visual-polish pass introducing game/themes/ui_theme.tres
    # (a hand-authored StyleBoxFlat/Theme resource, never validated by a
    # real Godot editor in this sandbox). Confirm it actually loaded as a
    # real Theme with the expected values, rather than silently failing to
    # parse and leaving the sidebar on the engine's default theme -- the
    # kind of resource-format mistake this sandbox has no other way to
    # catch before CI.
    var themed_panel: PanelContainer = economy_ui_scene.get_node("UI/Panel")
    if themed_panel.theme == null:
        _fail("UI/Panel must have the ui_theme.tres Theme resource assigned")
        return
    if int(themed_panel.theme.default_font_size) != 15:
        _fail("ui_theme.tres must set default_font_size to 15")
        return
    if not themed_panel.theme.has_stylebox("panel", "PanelContainer"):
        _fail("ui_theme.tres must define a PanelContainer panel style")
        return
    if not themed_panel.theme.has_stylebox("normal", "Button"):
        _fail("ui_theme.tres must define a Button normal style")
        return

    # Task #67: the first asset-wiring pass copied one sprite per
    # fixture_catalog entry into game/assets/fixtures/. Confirm every one of
    # them actually loads through StoreView's own lookup (proves the sprite
    # file exists, is named to match its catalog_id exactly, and imports as
    # a real Texture2D under the CI editor's fresh import pass) rather than
    # only checking the files exist on disk.
    for fixture_entry in config["fixture_catalog"]:
        var fixture_catalog_id := str(fixture_entry["catalog_id"])
        if economy_ui_scene.store_view._fixture_texture(fixture_catalog_id) == null:
            _fail("fixture sprite failed to load for catalog_id: %s" % fixture_catalog_id)
            return
    # The pre-catalog-system checkout-1 fixture (no catalog_id of its own)
    # falls back to the "register_1" sprite for display only; that sprite
    # isn't itself a fixture_catalog entry, so the loop above never checks it.
    if economy_ui_scene.store_view._fixture_texture("register_1") == null:
        _fail("fallback checkout sprite (register_1) failed to load")
        return

    # Task #68: second asset-wiring pass, product overlay sprites. Confirm
    # every product_catalog category's three stock-display states
    # (high/medium/low) load, except copy_paper -- the one category the
    # source package (assets/raw/conveni_products_remake_v3/README_CLAUDE.md)
    # explicitly never shipped a sprite for -- where the absence itself is
    # asserted, so the known gap can't silently grow or shrink unnoticed.
    for product_catalog_entry in config["product_catalog"]:
        var product_catalog_entry_id := str(product_catalog_entry["catalog_id"])
        for stock_display_state in economy_ui_scene.store_view.PRODUCT_STOCK_DISPLAY_STATES:
            var product_sprite_texture = economy_ui_scene.store_view._product_texture(
                product_catalog_entry_id, stock_display_state
            )
            if product_catalog_entry_id == "copy_paper":
                if product_sprite_texture != null:
                    _fail("expected no product overlay sprite for copy_paper, but one loaded")
                    return
            elif product_sprite_texture == null:
                _fail(
                    "product overlay sprite failed to load for catalog_id/state: %s/%s" % [
                        product_catalog_entry_id, stock_display_state
                    ]
                )
                return

    # The two pre-catalog-system prototype products (task #38) carry no
    # catalog_id of their own; store_view.gd's
    # FALLBACK_PRODUCT_CATALOG_ID_BY_PRODUCT_ID (REMAKE_BALANCED_DEFAULT,
    # docs/decisions/0138-product-overlay-sprite-wiring.md) stands in for
    # display only. Confirm the fallback resolves and a full-stock shelf
    # actually renders the "high" state end to end.
    var prototype_bread_product = economy_ui_scene.simulation.inventory.get_product("prototype-bread")
    if not prototype_bread_product.catalog_id.is_empty():
        _fail("prototype-bread was expected to carry no catalog_id (pre-catalog-system product)")
        return
    if economy_ui_scene.store_view._product_display_catalog_id(prototype_bread_product) != "bread":
        _fail("prototype-bread's display fallback did not resolve to the 'bread' catalog_id")
        return
    if economy_ui_scene.store_view._product_stock_display_state(
        prototype_bread_product.stock_units, prototype_bread_product.initial_stock_units
    ) != "high":
        _fail("a freshly-stocked prototype-bread shelf was expected to display the 'high' state")
        return
    var product_on_shelf_1 = economy_ui_scene.store_view._product_on_fixture("shelf-1")
    if product_on_shelf_1 == null or product_on_shelf_1.product_id != "prototype-bread":
        _fail("_product_on_fixture('shelf-1') did not resolve to prototype-bread")
        return

    # Task #69: third asset-wiring pass, staff walking sprites. Confirm every
    # one of the 35 staff_candidates positions resolves to its own sprite id
    # (list position -> "staff_%03d", REMAKE_BALANCED_DEFAULT, docs/decisions/
    # 0139-staff-sprite-wiring.md) and that all 4 shipped directions actually
    # load for each one under CI's fresh editor import.
    for candidate_index in range(config["staff_candidates"].size()):
        var expected_staff_sprite_id := "staff_%03d" % (candidate_index + 1)
        var candidate_id_at_index := str(config["staff_candidates"][candidate_index]["candidate_id"])
        if economy_ui_scene.store_view._staff_sprite_id_for_candidate(candidate_id_at_index) != expected_staff_sprite_id:
            _fail("candidate at index %d did not resolve to %s" % [candidate_index, expected_staff_sprite_id])
            return
        for staff_sprite_direction in economy_ui_scene.store_view.STAFF_SPRITE_DIRECTIONS:
            if economy_ui_scene.store_view._staff_texture(
                expected_staff_sprite_id,
                staff_sprite_direction,
                economy_ui_scene.store_view.STAFF_SPRITE_STATIC_PHASE
            ) == null:
                _fail(
                    "staff sprite failed to load for %s/%s" % [
                        expected_staff_sprite_id, staff_sprite_direction
                    ]
                )
                return
    if economy_ui_scene.store_view._staff_sprite_id_for_candidate("") != "":
        _fail("an empty candidate_id must resolve to no sprite")
        return
    if economy_ui_scene.store_view._staff_sprite_id_for_candidate("no-such-candidate") != "":
        _fail("an unknown candidate_id must resolve to no sprite")
        return

    # staff-1 (the scenario's checkout staff) is bound to the confirmed
    # manda_machiko candidate; confirm the live roster entry resolves
    # end-to-end, not just the raw lookup function in isolation.
    var checkout_staff_candidate_id: String = economy_ui_scene.simulation.staff.members["staff-1"].candidate_id
    if checkout_staff_candidate_id != "manda_machiko":
        _fail("staff-1 was expected to be bound to the confirmed 'manda_machiko' candidate")
        return
    if economy_ui_scene.store_view._staff_sprite_id_for_candidate(checkout_staff_candidate_id) != "staff_005":
        _fail("staff-1's bound candidate did not resolve to the expected sprite id")
        return

    # _staff_facing_direction() is a pure display-derivation function (no
    # confirmed original rule governs on-screen staff orientation, see
    # store_view.gd); exercise it directly with synthetic positions rather
    # than depending on a specific movement scenario happening to occur.
    if economy_ui_scene.store_view._staff_facing_direction("test-staff", Vector2i(5, 5)) != "down":
        _fail("a staff member with no prior recorded position must default to facing 'down'")
        return
    if economy_ui_scene.store_view._staff_facing_direction("test-staff", Vector2i(8, 5)) != "right":
        _fail("moving in +x must face 'right'")
        return
    if economy_ui_scene.store_view._staff_facing_direction("test-staff", Vector2i(8, 5)) != "right":
        _fail("an unchanged position must keep facing the previously resolved direction")
        return
    if economy_ui_scene.store_view._staff_facing_direction("test-staff", Vector2i(8, 2)) != "up":
        _fail("moving in -y must face 'up'")
        return

    # Task #70: fourth asset-wiring pass, customer walking sprites. Unlike
    # staff, no archetype/roster identity exists for customers in this
    # client at all, so sprite assignment is a pure hash of customer_id
    # (REMAKE_BALANCED_DEFAULT, docs/decisions/0140-customer-sprite-wiring.md)
    # rather than a position-based lookup. Confirm all 21 sprites' 4
    # directions load, the hash-based lookup is deterministic and uses the
    # expected naming convention, and the facing-direction derivation
    # (shared logic with staff, exercised the same way) behaves correctly.
    for customer_sprite_number in range(1, economy_ui_scene.store_view.CUSTOMER_SPRITE_COUNT + 1):
        var expected_customer_sprite_id := "customer_%02d" % customer_sprite_number
        for customer_sprite_direction in economy_ui_scene.store_view.CUSTOMER_SPRITE_DIRECTIONS:
            if economy_ui_scene.store_view._customer_texture(
                expected_customer_sprite_id,
                customer_sprite_direction,
                economy_ui_scene.store_view.CUSTOMER_SPRITE_STATIC_PHASE
            ) == null:
                _fail(
                    "customer sprite failed to load for %s/%s" % [
                        expected_customer_sprite_id, customer_sprite_direction
                    ]
                )
                return
    var first_customer_sprite_id: String = economy_ui_scene.store_view._customer_sprite_id_for_id("customer-1")
    if not first_customer_sprite_id.begins_with("customer_"):
        _fail("customer sprite id must use the 'customer_NN' naming convention")
        return
    if economy_ui_scene.store_view._customer_sprite_id_for_id("customer-1") != first_customer_sprite_id:
        _fail("_customer_sprite_id_for_id must be deterministic for the same customer_id")
        return
    if economy_ui_scene.store_view._customer_sprite_id_for_id("") != "":
        _fail("an empty customer_id must resolve to no sprite")
        return
    if economy_ui_scene.store_view._customer_facing_direction("test-customer", Vector2i(5, 5)) != "down":
        _fail("a customer with no prior recorded position must default to facing 'down'")
        return
    if economy_ui_scene.store_view._customer_facing_direction("test-customer", Vector2i(8, 5)) != "right":
        _fail("moving in +x must face 'right'")
        return
    if economy_ui_scene.store_view._customer_facing_direction("test-customer", Vector2i(8, 5)) != "right":
        _fail("an unchanged position must keep facing the previously resolved direction")
        return
    if economy_ui_scene.store_view._customer_facing_direction("test-customer", Vector2i(8, 2)) != "up":
        _fail("moving in -y must face 'up'")
        return

    # Task #71: first menu-UI asset pass. Unlike the world sprites above,
    # these icons are cropped directly from the strategy guide's own printed
    # menu-icon pages (CONFIRMED_VISUAL, not REMAKE_BALANCED_DEFAULT --
    # see main.gd's own note at MENU_ICON_DIR). Every fixture_catalog and
    # product_catalog entry already has a matching icon; confirm each
    # OptionButton item actually carries one after population.
    for fixture_catalog_index in range(economy_ui_scene._fixture_catalog_ids.size()):
        if economy_ui_scene.fixture_catalog_option.get_item_icon(fixture_catalog_index) == null:
            _fail(
                "fixture catalog menu icon failed to load for %s" % [
                    economy_ui_scene._fixture_catalog_ids[fixture_catalog_index]
                ]
            )
            return
    for product_catalog_index in range(economy_ui_scene._product_catalog_ids.size()):
        if economy_ui_scene.product_catalog_option.get_item_icon(product_catalog_index) == null:
            _fail(
                "product catalog menu icon failed to load for %s" % [
                    economy_ui_scene._product_catalog_ids[product_catalog_index]
                ]
            )
            return
    # hire_candidate_option's face icons reuse the task #69 staff sprite
    # numbering (position in staff_candidates), not a new mapping.
    for hire_candidate_index in range(economy_ui_scene._hire_candidate_ids.size()):
        if economy_ui_scene.hire_candidate_option.get_item_icon(hire_candidate_index) == null:
            _fail(
                "staff hire menu icon failed to load for %s" % [
                    economy_ui_scene._hire_candidate_ids[hire_candidate_index]
                ]
            )
            return

    var bench_index: int = economy_ui_scene._fixture_catalog_ids.find("bench")
    if bench_index < 0:
        _fail("economy UI: fixture catalog option did not include 'bench'")
        return
    economy_ui_scene.fixture_catalog_option.selected = bench_index
    economy_ui_scene._on_buy_fixture_pressed()
    if economy_ui_scene.store_view.selected_fixture_id != "__new:bench":
        _fail("economy UI: pressing Buy fixture must select the pending-placement sentinel")
        return
    economy_ui_scene._on_fixture_relocation_requested(
        economy_ui_scene.store_view.selected_fixture_id, Vector2i(1, 10)
    )
    if not economy_ui_scene.simulation.layout.fixtures_by_id.has("fixture-purchase-1"):
        _fail("economy UI: tapping an empty cell after Buy fixture must place the fixture")
        return
    if not economy_ui_scene.store_view.selected_fixture_id.is_empty():
        _fail("economy UI: placing a new fixture must clear the pending-placement selection")
        return

    var tobacco_permit_index: int = economy_ui_scene._permit_ids.find("tobacco")
    if tobacco_permit_index < 0:
        _fail("economy UI: permit option did not include 'tobacco'")
        return
    economy_ui_scene.permit_option.selected = tobacco_permit_index
    economy_ui_scene._on_buy_permit_pressed()
    if not economy_ui_scene.simulation.has_permit("tobacco"):
        _fail("economy UI: Buy permit must grant the selected permit")
        return

    # small_tobacco_vending (not small_ambient_shelf) so the tobacco
    # procurement below stays within this fixture's confirmed
    # compatible_product_categories (task #45).
    var shelf_index: int = economy_ui_scene._fixture_catalog_ids.find("small_tobacco_vending")
    if shelf_index < 0:
        _fail("economy UI: fixture catalog option did not include 'small_tobacco_vending'")
        return
    economy_ui_scene.fixture_catalog_option.selected = shelf_index
    economy_ui_scene._on_buy_fixture_pressed()
    economy_ui_scene._on_fixture_relocation_requested(
        economy_ui_scene.store_view.selected_fixture_id, Vector2i(4, 10)
    )
    var new_shelf_index: int = economy_ui_scene._procure_fixture_ids.find("fixture-purchase-2")
    if new_shelf_index < 0:
        _fail("economy UI: buying a shelf-kind fixture must refresh the procure-target option list")
        return

    var tobacco_product_index: int = economy_ui_scene._product_catalog_ids.find("tobacco")
    if tobacco_product_index < 0:
        _fail("economy UI: product catalog option did not include 'tobacco'")
        return
    economy_ui_scene.product_catalog_option.selected = tobacco_product_index
    economy_ui_scene.procure_fixture_option.selected = new_shelf_index
    economy_ui_scene._on_procure_product_pressed()
    if not economy_ui_scene.simulation.inventory.products.has("product-purchase-1"):
        _fail("economy UI: Stock product must procure onto the selected fixture")
        return
    # Task #79: no more separate restock option list to refresh -- the
    # newly-procured product becomes a valid contextual restock target as
    # soon as its own fixture is selected and its stock is low, checked via
    # store_view._product_on_fixture() directly.
    if economy_ui_scene.store_view._product_on_fixture("fixture-purchase-2") == null:
        _fail("economy UI: procuring a product must make it resolvable via _product_on_fixture")
        return

    # Task #68: try_procure_product() now threads its own catalog_id
    # argument onto the resulting InventoryState (previously discarded once
    # catalog_entry was looked up) so store_view.gd can pick the correct
    # product overlay sprite without guessing.
    var procured_tobacco_product = economy_ui_scene.simulation.inventory.get_product("product-purchase-1")
    if procured_tobacco_product.catalog_id != "tobacco":
        _fail("product-purchase-1 was expected to carry catalog_id 'tobacco'")
        return
    if economy_ui_scene.store_view._product_display_catalog_id(procured_tobacco_product) != "tobacco":
        _fail("product-purchase-1's display catalog_id did not resolve to 'tobacco'")
        return

    # Task #79: the restock command is now contextual to the selected
    # fixture, gated on that fixture's own stock level -- it is not an
    # always-available generic picker any more (see docs/decisions/0149-*.md
    # for the CONFIRMED_COMMUNITY owner testimony this responds to).
    economy_ui_scene.store_view.selected_fixture_id = "shelf-1"
    var bread_product_full = economy_ui_scene.simulation.inventory.get_product("prototype-bread")
    bread_product_full.stock_units = bread_product_full.initial_stock_units
    if economy_ui_scene._selected_fixture_restock_target() != null:
        _fail("economy UI: a full shelf has nothing to restock")
        return
    var cash_before_gated_restock_attempt: int = economy_ui_scene.simulation.economy.cash_yen
    economy_ui_scene._on_restock_pressed()
    if economy_ui_scene.simulation.economy.cash_yen != cash_before_gated_restock_attempt:
        _fail("economy UI: pressing Restock on a full shelf must not charge cash")
        return
    # Task #97: as soon as the shelf is short (「中身が減っていると」), even
    # by a few units and with customers in the store, it can be filled.
    bread_product_full.stock_units = bread_product_full.initial_stock_units - 3
    var restock_target = economy_ui_scene._selected_fixture_restock_target()
    if restock_target == null or restock_target.product_id != "prototype-bread":
        _fail("economy UI: restock target must resolve to the selected fixture's short product")
        return
    var cash_before_explicit_restock: int = economy_ui_scene.simulation.economy.cash_yen
    economy_ui_scene._on_restock_pressed()
    var bread_product = economy_ui_scene.simulation.inventory.get_product("prototype-bread")
    if bread_product.stock_units != bread_product.initial_stock_units:
        _fail("economy UI: Restock must fill the shelf back to full, not beyond")
        return
    if economy_ui_scene.simulation.economy.cash_yen != cash_before_explicit_restock - 3 * bread_product.restock_unit_cost_yen:
        _fail("economy UI: Restock must charge the missing units * restock_unit_cost_yen")
        return
    # Clear the selection this restock test made -- later checks in this same
    # scenario (e.g. the sell button below) assume nothing is selected by
    # default, same as before task #79 introduced fixture selection here.
    economy_ui_scene.store_view.selected_fixture_id = ""

    var promotion_index: int = economy_ui_scene._promotion_ids.find("direct_mail")
    if promotion_index < 0:
        _fail("economy UI: promotion option did not include 'direct_mail'")
        return
    economy_ui_scene.promotion_option.selected = promotion_index
    var cash_before_promotion: int = economy_ui_scene.simulation.economy.cash_yen
    economy_ui_scene._on_buy_promotion_pressed()
    if economy_ui_scene.simulation.economy.cash_yen != cash_before_promotion:
        _fail("economy UI: buying a promotion must not charge cash until its scheduled trigger fires")
        return

    # Task #65: chain_expansion_cost_yen() now charges the confirmed x4 area
    # multiplier, so top up cash to guarantee this scenario's earlier
    # spending (fixture/permit/product/restock/promotion purchases) hasn't
    # left too little for the expansion itself -- this test's point is the
    # UI wiring, not exercising the insufficient-cash rejection path (that
    # is already covered by the dedicated chain-expansion scenario above).
    economy_ui_scene.simulation.economy.cash_yen = max(
        economy_ui_scene.simulation.economy.cash_yen,
        economy_ui_scene.simulation.chain_expansion_cost_yen()
    )
    var store_count_before_expansion: int = economy_ui_scene.simulation.player_store_count
    economy_ui_scene._on_expand_chain_pressed()
    if economy_ui_scene.simulation.player_store_count != store_count_before_expansion + 1:
        _fail("economy UI: Expand chain must increase player_store_count by exactly one")
        return

    # Task #52: the eject-customer action reachable from the UI, not only
    # from VerticalSliceSimulation.try_eject_customer() directly.
    var eject_ui_plan: Array[String] = ["prototype-bread"]
    if not economy_ui_scene.simulation.start_explicit_customer("eject-ui-customer", eject_ui_plan):
        _fail("economy UI: could not admit a customer for the eject-UI scenario")
        return
    var eject_ui_ticks := 0
    while (
        economy_ui_scene.simulation.customers.customer("eject-ui-customer").phase != "checkout"
        and eject_ui_ticks < MAX_STEPS
    ):
        economy_ui_scene.simulation.step()
        eject_ui_ticks += 1
    steps += eject_ui_ticks
    if eject_ui_ticks >= MAX_STEPS:
        _fail("economy UI: eject-UI customer never reached checkout")
        return
    economy_ui_scene._refresh_eject_customer_option()
    var eject_ui_index: int = economy_ui_scene._eject_customer_ids.find("eject-ui-customer")
    if eject_ui_index < 0:
        _fail("economy UI: eject customer option did not include the customer at checkout")
        return
    economy_ui_scene.eject_customer_option.selected = eject_ui_index
    economy_ui_scene._on_eject_customer_pressed()
    if economy_ui_scene.simulation.customers.customer("eject-ui-customer").phase != "leaving":
        _fail("economy UI: pressing Eject customer must transition the selected customer to leaving")
        return

    # Task #56: the staff-hiring action reachable from the UI, not only from
    # VerticalSliceSimulation.try_hire_candidate() directly. try_hire_
    # candidate() is guarded by customers.all_settled() like every other
    # roster-affecting action, so the just-ejected customer must finish
    # leaving first.
    var hire_ui_settle_ticks := 0
    while (
        not economy_ui_scene.simulation.customers.all_settled()
        and hire_ui_settle_ticks < MAX_STEPS
    ):
        economy_ui_scene.simulation.step()
        hire_ui_settle_ticks += 1
    steps += hire_ui_settle_ticks
    if hire_ui_settle_ticks >= MAX_STEPS:
        _fail("economy UI: the ejected customer never settled before the hire-UI scenario")
        return
    var hire_ui_slot_index: int = economy_ui_scene._staff_slot_ids.find("staff-2")
    if hire_ui_slot_index < 0:
        _fail("economy UI: staff slot option did not include 'staff-2'")
        return
    economy_ui_scene.staff_slot_option.selected = hire_ui_slot_index
    economy_ui_scene._on_staff_slot_selected(hire_ui_slot_index)
    var hire_ui_candidate_index: int = economy_ui_scene._hire_candidate_ids.find("hamada_yuko")
    if hire_ui_candidate_index < 0:
        _fail("economy UI: hire candidate option did not include an unemployed candidate ('hamada_yuko')")
        return

    # CONFIRMED_OFFICIAL (third companion book): the pre-hire résumé stat
    # band (40-69="普通", 70-100="高い"). hamada_yuko's confirmed stats are
    # stamina=65/academic_background=55/agility=70/sociability=50, so the
    # displayed candidate text must show 普通/普通/高い/普通 for those four.
    if economy_ui_scene._resume_stat_band(69) != "普通" or economy_ui_scene._resume_stat_band(70) != "高い":
        _fail("_resume_stat_band did not split at the confirmed 40-69/70-100 boundary")
        return
    var hire_ui_candidate_text: String = economy_ui_scene.hire_candidate_option.get_item_text(hire_ui_candidate_index)
    if not hire_ui_candidate_text.contains("体力普通 学歴普通 敏捷性高い 社交性普通"):
        _fail("hire candidate option text did not show hamada_yuko's expected résumé stat bands")
        return

    economy_ui_scene.hire_candidate_option.selected = hire_ui_candidate_index
    economy_ui_scene._on_hire_candidate_pressed()
    if economy_ui_scene.simulation.staff.members["staff-2"].candidate_id != "hamada_yuko":
        _fail("economy UI: pressing Hire candidate must update the selected slot's candidate_id")
        return
    # The just-hired candidate must drop out of the OTHER slot's option
    # list (try_hire_candidate()'s own cross-slot collision rule), proving
    # _refresh_hire_candidate_option() actually re-filters after a hire
    # rather than only clearing/repopulating with the same stale set.
    var hire_ui_other_slot_index: int = economy_ui_scene._staff_slot_ids.find("staff-1")
    economy_ui_scene.staff_slot_option.selected = hire_ui_other_slot_index
    economy_ui_scene._on_staff_slot_selected(hire_ui_other_slot_index)
    if economy_ui_scene._hire_candidate_ids.find("hamada_yuko") >= 0:
        _fail("economy UI: a just-hired candidate must not remain selectable for the other slot")
        return

    # Task #72: town-map wiring. TownView draws only the two things this
    # client already tracks (_player_store_position/_rival_stores, added
    # in task #59 solely for permit-exclusion-distance math), not the 52
    # town-facility sprites (none of which depict a store, and this client
    # has no placement data for any of them -- see town_view.gd's own note).
    # First, exercise the toggle wiring end-to-end against the real scene
    # (default scenario: player at the origin, zero rival stores).
    if economy_ui_scene.town_view.visible:
        _fail("town view must start hidden behind the store view")
        return
    economy_ui_scene._on_show_town_map_pressed()
    if not economy_ui_scene.town_view.visible or economy_ui_scene.store_view.visible:
        _fail("pressing 'Show town map' must show the town view and hide the store view")
        return
    if economy_ui_scene.show_town_map_button.text != economy_ui_scene.tr("Show store"):
        _fail("the toggle button must relabel itself while showing the town view")
        return
    economy_ui_scene._on_show_town_map_pressed()
    if economy_ui_scene.town_view.visible or not economy_ui_scene.store_view.visible:
        _fail("pressing the toggle again must restore the store view")
        return
    var default_town_points: Array = economy_ui_scene.town_view._town_points(economy_ui_scene.simulation)
    if default_town_points.size() != 1 or default_town_points[0]["position"] != Vector2i.ZERO:
        _fail("the default scenario must show exactly one town marker at the origin")
        return

    # Then exercise the bounding-box math directly against a synthetic
    # multi-rival roster (a pure function, independent of any real
    # simulation/scenario data).
    var fake_town_simulation := _FakeTownSimulation.new()
    fake_town_simulation._player_store_position = Vector2i(0, 0)
    var fake_rival_stores: Array[Dictionary] = [
        {"id": "rival-a", "position": Vector2i(4, -3), "permits_held": []},
        {"id": "rival-b", "position": Vector2i(-2, 6), "permits_held": []},
    ]
    fake_town_simulation._rival_stores = fake_rival_stores
    var fake_town_points: Array = economy_ui_scene.town_view._town_points(fake_town_simulation)
    if fake_town_points.size() != 3:
        _fail("expected one marker for the player plus one per configured rival")
        return
    var fake_town_box: Dictionary = economy_ui_scene.town_view._bounding_box(fake_town_points)
    if fake_town_box["origin"] != Vector2i(-3, -4) or fake_town_box["size"] != Vector2i(9, 12):
        _fail("town view bounding box did not cover every marker with the expected margin")
        return
    # Task #90: with the guide p.11 beginner map in the config, the town
    # view draws that 41x35-tile town, sized to sit left of the panel.
    if economy_ui_scene.town_view.guide_map_tiles() != Vector2i(41, 35):
        _fail("the town view must draw the guide's beginner-map town")
        return
    var town_tile_pixels: float = economy_ui_scene.town_view.map_tile_pixels
    var town_shown: Vector2i = economy_ui_scene.town_view.view_tiles()
    var town_right_edge: float = economy_ui_scene.town_view.position.x + town_shown.x * town_tile_pixels
    if town_tile_pixels < 16.0 or town_right_edge > (economy_ui_scene.get_node("UI/Panel") as Control).offset_left:
        _fail("the town map must be legible and fit left of the side panel")
        return
    # Task #93: the view scrolls in whole tiles and stops at the town's edge.
    economy_ui_scene.town_view.view_origin_tile = Vector2i.ZERO
    economy_ui_scene.town_view.scroll_by_tiles(Vector2i(-5, -5))
    if economy_ui_scene.town_view.view_origin_tile != Vector2i.ZERO:
        _fail("the town view must not scroll past the town's top-left edge")
        return
    economy_ui_scene.town_view.scroll_by_tiles(Vector2i(1000, 1000))
    if economy_ui_scene.town_view.view_origin_tile != Vector2i(41, 35) - town_shown:
        _fail("the town view must stop at the town's bottom-right edge")
        return
    economy_ui_scene.town_view.center_on_store()

    # Task #78: EditModeOption/SellFixtureButton/DeselectFixtureButton wiring
    # against the real instantiated main.tscn scene. Reuses fixture-purchase-1
    # (bench, unoccupied) and fixture-purchase-2 (small_tobacco_vending,
    # already holding product-purchase-1 from the earlier "Stock product"
    # test above) rather than purchasing new fixtures, since both are still
    # present and their occupancy state is exactly what this test needs.
    # By this point the scene's many earlier purchases (fixtures, permit,
    # product, promotion, chain expansion) have drawn cash back down to
    # near the ¥1,000 starting amount, which does not cover the swap
    # test's own bench/potted_plant purchases below; top up again.
    economy_ui_scene.simulation.economy.cash_yen += 50_000
    if economy_ui_scene.sell_fixture_button.disabled != true:
        _fail("the sell button must start disabled with nothing selected")
        return
    economy_ui_scene.store_view.selected_fixture_id = "fixture-purchase-2"
    economy_ui_scene._refresh_ui()
    if economy_ui_scene.sell_fixture_button.disabled:
        _fail("the sell button must enable once a fixture is selected")
        return
    economy_ui_scene._on_sell_fixture_pressed()
    if not economy_ui_scene.simulation.layout.fixtures_by_id.has("fixture-purchase-2"):
        _fail("selling a fixture that still holds procured stock must be rejected, not silently removed")
        return
    economy_ui_scene.store_view.selected_fixture_id = "fixture-purchase-1"
    var cash_before_ui_sell: int = int(economy_ui_scene.simulation.economy.cash_yen)
    economy_ui_scene._on_sell_fixture_pressed()
    if economy_ui_scene.simulation.layout.fixtures_by_id.has("fixture-purchase-1"):
        _fail("selling an unoccupied, non-checkout fixture through the UI button must remove it")
        return
    if not economy_ui_scene.store_view.selected_fixture_id.is_empty():
        _fail("selling the selected fixture must clear the selection (it no longer exists)")
        return
    if economy_ui_scene.simulation.economy.cash_yen <= cash_before_ui_sell:
        _fail("selling a fixture through the UI button must actually refund cash")
        return

    # EditModeOption's default is "move" (existing tap-to-relocate
    # behavior, unit-tested at the store_view.gd level already); switching
    # it to "swap" (item id 1) must flip store_view.edit_mode.
    economy_ui_scene._on_edit_mode_selected(1)
    if economy_ui_scene.store_view.edit_mode != "swap":
        _fail("selecting the 'Swap' item must set store_view.edit_mode to 'swap'")
        return
    # Interaction cells go directly below each fixture's own footprint
    # (y=14, not sideways or immediately above) so that swapping -- which
    # shifts each fixture's interaction cell by the same delta as its
    # origin -- never lands one fixture's shifted interaction cell inside
    # the other's new footprint (both footprints stay in the y=12/13 rows)
    # nor inside fixture-purchase-2's still-standing footprint (task #45's
    # small_tobacco_vending is a 1x1-tile fixture, i.e. 2x2 subcells, so it
    # actually occupies BOTH y=10 and y=11 at x=4-5 -- not just y=10 as an
    # earlier, wrong version of this fix at y=11 assumed). Fixture B sits at
    # x=4 rather than x=5 since task #88's starting break room occupies
    # x=6-9, y=12-15 in the shipped layout this UI scene loads.
    if not economy_ui_scene.simulation.try_purchase_fixture(
        "bench", "swap-ui-a", Vector2i(1, 12), Vector2i(1, 14)
    ):
        _fail("swap test: setup fixture A purchase failed")
        return
    if not economy_ui_scene.simulation.try_purchase_fixture(
        "potted_plant", "swap-ui-b", Vector2i(4, 12), Vector2i(4, 14)
    ):
        _fail("swap test: setup fixture B purchase failed")
        return
    economy_ui_scene._on_fixture_swap_requested("swap-ui-a", "swap-ui-b")
    if economy_ui_scene.simulation.layout.fixture_origin("swap-ui-a") != Vector2i(4, 12):
        _fail("swapping through the UI signal handler must move fixture A to fixture B's origin")
        return
    if economy_ui_scene.simulation.layout.fixture_origin("swap-ui-b") != Vector2i(1, 12):
        _fail("swapping through the UI signal handler must move fixture B to fixture A's origin")
        return

    economy_ui_scene._on_deselect_fixture_pressed()
    if not economy_ui_scene.store_view.selected_fixture_id.is_empty():
        _fail("the Deselect button must clear the current fixture selection")
        return
    economy_ui_scene._on_edit_mode_selected(0)
    if economy_ui_scene.store_view.edit_mode != "move":
        _fail("selecting the 'Move' item must set store_view.edit_mode back to 'move'")
        return

    # Task #75: day/month progression and the game-over/scenario-clear
    # state were tracked by the simulation (snapshot()'s day_count/
    # month_count/is_game_over/game_over_reason/clear_condition_met) but
    # never surfaced anywhere in this UI -- economy actions already
    # silently stopped working once is_game_over was true, with no
    # on-screen explanation. Computed from the scene's own current
    # simulation state (not a hardcoded "day 0" assumption), since several
    # step() loops earlier in this same scenario may already have crossed
    # a day boundary. Several of those loops call simulation.step()
    # directly rather than through _process(), so _refresh_ui() must be
    # called explicitly here to be sure the label is not stale.
    economy_ui_scene._refresh_ui()
    # Task #77: the confirmed official PS-version screenshot (ss01, docs/
    # research/official-screenshot-evidence-2026-09-05.md section 1) shows
    # the date as year/month/day ("01年目01月01日"), not the month+day-of-4
    # format task #75 originally invented without checking that evidence.
    var expected_calendar_year: int = economy_ui_scene.simulation.month_count / economy_ui_scene.simulation.MONTHS_PER_YEAR + 1
    var expected_calendar_month: int = economy_ui_scene.simulation.month_count % economy_ui_scene.simulation.MONTHS_PER_YEAR + 1
    # Task #92: the game always runs in Japanese, so the expected text goes
    # through the same translation the label uses.
    var expected_calendar_text := economy_ui_scene.tr("Year %d · Month %d, Day %d") % [
        expected_calendar_year,
        expected_calendar_month,
        economy_ui_scene.simulation._days_completed_this_month + 1,
    ]
    if economy_ui_scene.calendar_label.text != expected_calendar_text:
        _fail("the calendar label must reflect the simulation's actual day/month progression")
        return
    # Task #85: original-style bracketed weather, one-character labels padded.
    if economy_ui_scene.weather_label.text != "［%s］" % economy_ui_scene.simulation.weather_display_label().rpad(2):
        _fail("the top bar must show the simulation's current weather in the original's bracketed form")
        return
    if economy_ui_scene.game_over_layer.visible:
        _fail("the game-over overlay must start hidden")
        return
    if economy_ui_scene.scenario_status_label.text != "":
        _fail("the scenario-clear label must start blank before the clear condition is met")
        return

    economy_ui_scene.simulation.clear_condition_met = true
    economy_ui_scene._refresh_ui()
    if economy_ui_scene.scenario_status_label.text.find("10") < 0 or economy_ui_scene.scenario_status_label.text.is_empty():
        _fail("the scenario-clear label must announce the target once clear_condition_met is true")
        return
    economy_ui_scene.simulation.clear_condition_met = false

    # Reuse the same direct _evaluate_terminal_state() technique the
    # reference bankruptcy/time-limit scenario above already uses (task
    # #65's own bankruptcy_simulation), since driving a real month boundary
    # through this scene's own step() loop would take far longer than this
    # check needs.
    economy_ui_scene.simulation.economy.cash_yen = -1
    economy_ui_scene.simulation._evaluate_terminal_state()
    economy_ui_scene._refresh_ui()
    if not economy_ui_scene.game_over_layer.visible:
        _fail("the game-over overlay must show once the simulation reports is_game_over")
        return
    if economy_ui_scene.game_over_reason_label.text != economy_ui_scene._game_over_reason_text("bankrupt"):
        _fail("the game-over overlay must show the bankrupt reason's translated text")
        return
    if not economy_ui_scene.paused:
        _fail("reaching game over must auto-pause the running simulation")
        return

    # "Play Again" (game_over_reset_button) is wired to the exact same
    # handler as the sidebar's own Reset button -- confirm it actually
    # clears is_game_over and hides the overlay again on the next refresh.
    economy_ui_scene._on_reset_pressed()
    if economy_ui_scene.simulation.is_game_over:
        _fail("Play Again must clear is_game_over via the existing full reset() path")
        return
    if economy_ui_scene.game_over_layer.visible:
        _fail("Play Again must hide the game-over overlay again")
        return

    economy_ui_scene.free()

    # Task #49/#51: an unusually slow checkout (a deliberately below-
    # reference register_skill) must trigger exactly one
    # checkout_anger_triggered event and apply the confirmed -2 penalty to
    # EVERY active staff member's five affected skills, not only the one
    # who served the customer (task #51 corrected this scope after
    # directly re-reading the strategy guide's own "店員全員の能力が下が
    # ってしまう" statement, book pp.34-35). register_skill/service_skill's
    # own growth ceilings are overridden to their post-anger floor here so
    # task #48's checkout-completion growth (+1 to those same two skills)
    # cannot also fire and complicate the expected value -- isolating this
    # scenario to the anger mechanic alone, the same technique the
    # StaffGrowth unit tests above already use to force a "no growth"
    # branch.
    var anger_config: Dictionary = config.duplicate(true)
    anger_config["demand"] = {
        "nearby_population": 0,
        "customer_share_percent": 0.0,
        "daily_visit_rate_per_population": 0.0,
        "opening_minutes_per_day": 960,
        "bad_weather_visit_multiplier": 0.0,
        "is_bad_weather": false,
        "rng_seed": 19,
    }
    var checkout_staff_id := str(anger_config["staff"]["checkout_staff_id"])
    var slow_staff_index := -1
    for i in anger_config["staff"]["members"].size():
        if str(anger_config["staff"]["members"][i]["id"]) == checkout_staff_id:
            slow_staff_index = i
            break
    if slow_staff_index < 0:
        _fail("checkout-anger test config must find the checkout staff member")
        return
    var anger_staff_config_before: Dictionary = (
        anger_config["staff"]["members"][slow_staff_index].duplicate(true)
    )
    anger_config["staff"]["members"][slow_staff_index]["register_skill"] = 1
    anger_config["staff"]["members"][slow_staff_index]["register_skill_growth_ceiling"] = 0
    anger_config["staff"]["members"][slow_staff_index]["service_skill_growth_ceiling"] = 0
    var anger_simulation = VerticalSliceSimulationScript.new(anger_config)
    steps += _run_visit(anger_simulation)
    if anger_simulation.event_log.count_type("checkout_anger_triggered") != 1:
        _fail("an unusually slow checkout must trigger exactly one checkout_anger_triggered event")
        return
    var angered_staff = anger_simulation.staff.members[checkout_staff_id]
    if angered_staff.register_skill != max(0, 1 - 2):
        _fail("checkout anger must lower register_skill by 2, clamped at the floor")
        return
    if angered_staff.service_skill != max(0, int(anger_staff_config_before["service_skill"]) - 2):
        _fail("checkout anger must lower service_skill by 2")
        return
    if (
        angered_staff.replenishment_skill
        != max(0, int(anger_staff_config_before["replenishment_skill"]) - 2)
    ):
        _fail("checkout anger must lower replenishment_skill by 2")
        return
    if angered_staff.cleaning_skill != max(0, int(anger_staff_config_before["cleaning_skill"]) - 2):
        _fail("checkout anger must lower cleaning_skill by 2")
        return
    if angered_staff.security_skill != max(0, int(anger_staff_config_before["security_skill"]) - 2):
        _fail("checkout anger must lower security_skill by 2")
        return

    # Task #51: the non-checkout staff member (who never served this
    # customer at all) must ALSO have every one of the same five skills
    # lowered by exactly 2, confirming the penalty is store-wide rather
    # than scoped to whichever staff member happened to be at the register.
    var other_staff_id := ""
    var other_staff_config_before: Dictionary = {}
    for staff_member_config in anger_config["staff"]["members"]:
        if str(staff_member_config["id"]) != checkout_staff_id:
            other_staff_id = str(staff_member_config["id"])
            other_staff_config_before = staff_member_config
            break
    if other_staff_id.is_empty():
        _fail("checkout-anger test config must find a second, non-checkout staff member")
        return
    var other_angered_staff = anger_simulation.staff.members[other_staff_id]
    if other_angered_staff.register_skill != max(0, int(other_staff_config_before["register_skill"]) - 2):
        _fail("checkout anger must also lower the non-checkout staff member's register_skill by 2")
        return
    if other_angered_staff.service_skill != max(0, int(other_staff_config_before["service_skill"]) - 2):
        _fail("checkout anger must also lower the non-checkout staff member's service_skill by 2")
        return
    if (
        other_angered_staff.replenishment_skill
        != max(0, int(other_staff_config_before["replenishment_skill"]) - 2)
    ):
        _fail("checkout anger must also lower the non-checkout staff member's replenishment_skill by 2")
        return
    if other_angered_staff.cleaning_skill != max(0, int(other_staff_config_before["cleaning_skill"]) - 2):
        _fail("checkout anger must also lower the non-checkout staff member's cleaning_skill by 2")
        return
    if other_angered_staff.security_skill != max(0, int(other_staff_config_before["security_skill"]) - 2):
        _fail("checkout anger must also lower the non-checkout staff member's security_skill by 2")
        return

    # Task #65: the same checkout_anger_triggered event must also roll the
    # guide's confirmed 1/6-chance store-rating penalty. The roll's outcome
    # is RNG-seed-dependent (rng_seed=19 in anger_config), so this only
    # checks that the field was actually recorded (proving the wiring ran)
    # rather than asserting a specific stochastic result.
    var anger_events: Array = anger_simulation.event_log.records
    var anger_event_details: Dictionary = {}
    var found_anger_event := false
    for record in anger_events:
        if record["event_type"] == "checkout_anger_triggered":
            anger_event_details = record["details"]
            found_anger_event = true
            break
    if not found_anger_event:
        _fail("checkout_anger_triggered event must be present in the event log")
        return
    if not anger_event_details.has("rating_penalty_applied"):
        _fail("checkout_anger_triggered event must record whether the rating penalty was rolled")
        return
    if typeof(anger_event_details["rating_penalty_applied"]) != TYPE_BOOL:
        _fail("rating_penalty_applied must be a bool")
        return
    # internal_rating_value starts at 0 in this scenario, so a -1 penalty
    # clamps right back to 0 either way -- this only confirms the clamp
    # itself never goes negative, not which branch was taken (see above).
    if anger_simulation.internal_rating_value < 0:
        _fail("internal_rating_value must never go negative")
        return

    # Task #55: a demand-driven customer's plan gets extended with
    # incidental-want products drawn from currently-stocked products beyond
    # the primary plan, but an explicitly-admitted (observation-replay)
    # customer's plan must stay exactly as given. A single extra stocked
    # product (beyond the default scenario's own two) makes this
    # deterministic regardless of RNG seed: with exactly one candidate,
    # that candidate must be the one incidental item selected.
    var incidental_simulation = VerticalSliceSimulationScript.new(config.duplicate(true))
    steps += _run_visit(incidental_simulation)
    incidental_simulation.economy.cash_yen += 50_000_000
    if not incidental_simulation.try_purchase_fixture(
        "small_ambient_shelf", "incidental-shelf-1", Vector2i(8, 10), Vector2i(8, 9)
    ):
        _fail("could not buy an extra shelf for the incidental-want scenario")
        return
    if not incidental_simulation.try_procure_product("bread", "incidental-extra-product", "incidental-shelf-1"):
        _fail("could not stock an extra product for the incidental-want scenario")
        return

    var explicit_plan: Array[String] = ["prototype-bread"]
    if not incidental_simulation.start_explicit_customer("explicit-plan-customer", explicit_plan):
        _fail("could not admit an explicit customer for the incidental-want scenario")
        return
    var explicit_customer = incidental_simulation.customers.customer("explicit-plan-customer")
    if explicit_customer.planned_product_ids != explicit_plan:
        _fail("start_explicit_customer() must never inflate the caller-supplied plan with incidental items")
        return
    steps += _run_visit(incidental_simulation)

    if not incidental_simulation.start_next_customer():
        _fail("could not admit a demand-driven customer for the incidental-want scenario")
        return
    var default_customer = incidental_simulation.customers.active()
    var expected_default_plan: Array[String] = []
    expected_default_plan.assign(config["customer"]["visit_plan_product_ids"])
    expected_default_plan.append("incidental-extra-product")
    if default_customer.planned_product_ids.size() != expected_default_plan.size():
        _fail("a demand-driven customer's plan must gain exactly one incidental item when exactly one stocked product is eligible")
        return
    for product_id in expected_default_plan:
        if not default_customer.planned_product_ids.has(product_id):
            _fail("a demand-driven customer's extended plan must include every expected primary and incidental product id")
            return
    if not default_customer.planned_product_ids.has("incidental-extra-product"):
        _fail("a demand-driven customer's incidental item must be drawn from currently-stocked products")
        return

    if not _check_store_site(config):
        return
    if not _check_sound(config):
        return
    if not _check_staff_work(config):
        return
    if not _check_rivals():
        return
    if not _check_stamina():
        return
    if not _check_rival_buyout():
        return
    if not _check_actions_while_open(config):
        return

    print("Vertical-slice headless smoke passed in %d steps." % steps)
    quit(0)


# Task #95: choosing and buying the store's 2x2 site on the guide town map.
# Expected prices are the ones tools/build_guide_town_map.py's site_quote()
# gives for the same squares (the contract test runs that side).
func _check_store_site(config: Dictionary) -> bool:
    var simulation = VerticalSliceSimulationScript.new(config)
    if simulation.store_site == null or simulation.has_store_site():
        _fail("the guide town map must give a site chooser with no site bought yet")
        return false
    var rules: Dictionary = config["guide_town_map"]["store_site"]
    if "REMAKE_BALANCED_DEFAULT" not in str(rules["evidence_note"]):
        _fail("the land price shape must stay tagged REMAKE_BALANCED_DEFAULT")
        return false
    if Vector2i(int(rules["footprint_tiles"][0]), int(rules["footprint_tiles"][1])) != Vector2i(2, 2):
        _fail("a store takes 2x2 squares on the town map (DATA4)")
        return false
    var vacant: Dictionary = simulation.store_site_quote(Vector2i(13, 21))
    if not bool(vacant["buildable"]) or int(vacant["total_yen"]) != 21_000_000 or int(vacant["building_yen"]) != 0:
        _fail("the vacant site (13, 21) must cost 21,000,000 yen: %s" % vacant)
        return false
    var with_house: Dictionary = simulation.store_site_quote(Vector2i(12, 20))
    if int(with_house["land_yen"]) != 27_000_000 or int(with_house["building_yen"]) != 10_000_000 or int(with_house["total_yen"]) != 37_000_000:
        _fail("a site with a house must cost its land plus half the house's value: %s" % with_house)
        return false
    if str(with_house["label"]).is_empty():
        _fail("a site with a building must name it")
        return false
    for blocked in [Vector2i(11, 20), Vector2i(5, 12), Vector2i(40, 34), Vector2i(-1, 3)]:
        if bool(simulation.store_site_quote(blocked)["buildable"]):
            _fail("roads, the railway and the map edge are not building sites: %s" % blocked)
            return false
    # Every start-of-game vacant lot costs between the guide's cheapest and
    # dearest vacant examples, and at least one sits at each end.
    var lowest := 1 << 40
    var highest := 0
    for y in 35:
        for x in 41:
            var quote: Dictionary = simulation.store_site_quote(Vector2i(x, y))
            if bool(quote["buildable"]) and int(quote["building_yen"]) == 0:
                lowest = mini(lowest, int(quote["land_yen"]))
                highest = maxi(highest, int(quote["land_yen"]))
    if lowest != 20_000_000 or highest > 30_000_000 or highest < 28_000_000:
        _fail("vacant lots must span the guide's 20,000,000-30,000,000 yen: %d-%d" % [lowest, highest])
        return false
    var permits: Dictionary = vacant["permits_available"]
    if not (permits.get("tobacco", false) and permits.get("alcohol", false) and permits.get("medicine", false)):
        _fail("with no rival stores every permit must be available at a site")
        return false
    # No store within 5 squares of another (guide p.7).
    var rival_config: Dictionary = config.duplicate(true)
    rival_config["town"]["rival_stores"] = [{"id": "rival-1", "position": [16, 24], "permits_held": ["tobacco"]}]
    var rival_simulation = VerticalSliceSimulationScript.new(rival_config)
    var near: Dictionary = rival_simulation.store_site_quote(Vector2i(13, 21))
    if bool(near["buildable"]) or str(near["reason"]) != "too_close_to_store":
        _fail("a site 3 squares from a rival store must be refused")
        return false
    var apart: Dictionary = rival_simulation.store_site_quote(Vector2i(16, 30))
    if not bool(apart["buildable"]) or bool(apart["permits_available"]["tobacco"]):
        _fail("5+ squares away the site is buildable, but inside the rival's 7-square tobacco range: %s" % apart)
        return false
    # Buying: needs the cash, pays it once, sets the store's catchment.
    if simulation.try_buy_store_site(Vector2i(13, 21)):
        _fail("the test budget cannot buy land")
        return false
    simulation.economy.cash_yen = 200_000_000
    if simulation.try_buy_store_site(Vector2i(11, 20)):
        _fail("a road square cannot be bought")
        return false
    if not simulation.try_buy_store_site(Vector2i(12, 20)):
        _fail("the house site must be buyable with 200,000,000 yen")
        return false
    if simulation.economy.cash_yen != 200_000_000 - 37_000_000:
        _fail("buying must pay the quoted 37,000,000 yen")
        return false
    if simulation.store_site_origin != Vector2i(12, 20) or simulation._player_store_position != Vector2i(12, 20):
        _fail("the bought site must become the store's position")
        return false
    if simulation.bought_buildings().size() != 1:
        _fail("the house on the site must be bought and cleared")
        return false
    var expected_population := int(round(
        float(config["demand"]["nearby_population"])
        * float(simulation.store_site.catchment_building_tiles(Vector2i(12, 20), simulation.bought_buildings()))
        / float(rules["mean_catchment_building_tiles"])
    ))
    if simulation.demand.nearby_population != expected_population:
        _fail("the store's nearby population must come from its site")
        return false
    if simulation.try_buy_store_site(Vector2i(30, 30)):
        _fail("a game has one store site")
        return false
    if int(simulation.snapshot()["land_value_yen"]) != 27_000_000:
        _fail("the HUD land value must be the bought site's own land price")
        return false
    # A denser catchment draws more people than a sparse one.
    var dense_population := int(simulation.store_site_quote(Vector2i(9, 4))["nearby_population"])
    var sparse_population := int(simulation.store_site_quote(Vector2i(0, 18))["nearby_population"])
    if dense_population <= sparse_population:
        _fail("a built-up site must draw more nearby population than an empty one")
        return false
    # Save/load keeps the site; reset (a new game) clears it.
    var saved: Dictionary = simulation.save_state()
    var reloaded = VerticalSliceSimulationScript.new(config)
    if not reloaded.load_state(saved):
        _fail("a save with a store site must load")
        return false
    if reloaded.store_site_origin != Vector2i(12, 20) or reloaded.bought_buildings() != simulation.bought_buildings():
        _fail("load must restore the site and the cleared buildings")
        return false
    if reloaded.demand.nearby_population != expected_population:
        _fail("load must restore the site's nearby population")
        return false
    simulation.reset()
    if simulation.has_store_site() or not simulation.bought_buildings().is_empty():
        _fail("a new game must start without a site")
        return false
    if simulation.demand.nearby_population != int(config["demand"]["nearby_population"]):
        _fail("a new game must restore the scenario's nearby population")
        return false
    return true


# Task #50: mirrors VerticalSliceSimulation._scale_yen_to_configured_business_hours()
# exactly, so these expected-value computations stay correct if that
# formula or its rounding convention ever changes.
func _expected_daily_yen_at_business_hours(value_at_24h_basis: int, opening_minutes_per_day: int) -> int:
    const MINUTES_PER_24H_DAY := 24 * 60
    return int(floor(float(value_at_24h_basis) * opening_minutes_per_day / float(MINUTES_PER_24H_DAY)))


func _run_visit(simulation) -> int:
    var steps := 0
    while simulation.customers.active().phase != "done" and steps < MAX_STEPS:
        simulation.step()
        steps += 1
    return steps


func _fail(message: String) -> void:
    push_error(message)
    quit(1)


# Task #96: the synthesized music and effects.
func _check_sound(config: Dictionary) -> bool:
    var sound: Dictionary = config["sound"]
    if "REMAKE_BALANCED_DEFAULT" not in str(sound["evidence_note"]):
        _fail("the sounds must stay tagged REMAKE_BALANCED_DEFAULT (this project's own)")
        return false
    var used: Array = sound["event_sfx"].values() + [sound["clear_sfx"], sound["button_sfx"], sound["refused_sfx"]]
    for id in used:
        if not SoundSynthScript.SFX_IDS.has(id):
            _fail("event sound %s has no synthesized effect" % id)
            return false
    for id in SoundSynthScript.SFX_IDS:
        var samples: PackedFloat32Array = SoundSynthScript.sfx_samples(id)
        if samples.size() < SoundSynthScript.MIX_RATE / 50 or samples.size() > SoundSynthScript.MIX_RATE * 3:
            _fail("sound effect %s must last between 20 ms and 3 s" % id)
            return false
        var peak := 0.0
        for value in samples:
            peak = maxf(peak, absf(value))
        if peak < 0.05 or peak > 1.0:
            _fail("sound effect %s must be audible and not clip (peak %f)" % [id, peak])
            return false
    if not is_equal_approx(SoundSynthScript.note_hz("A4"), 440.0) or not is_equal_approx(SoundSynthScript.note_hz("A5"), 880.0):
        _fail("note names must map to equal-tempered pitches")
        return false
    for theme_id in ["store", "town"]:
        var song: Dictionary = SoundThemesScript.theme(theme_id)
        if song["lead"].size() != song["bass"].size():
            _fail("each tune needs a bass bar for every melody bar")
            return false
        var bar: PackedFloat32Array = SoundSynthScript.render_song(song, 1)
        var expected := int(8 * (60.0 / float(song["bpm"]) / 2.0) * SoundSynthScript.MIX_RATE)
        if bar.size() != expected:
            _fail("one bar of %s must be 8 eighth notes long" % theme_id)
            return false
    var loop: AudioStreamWAV = SoundSynthScript.to_wav(SoundSynthScript.render_song(SoundThemesScript.TOWN, 1), true)
    if loop.loop_mode != AudioStreamWAV.LOOP_FORWARD or loop.mix_rate != SoundSynthScript.MIX_RATE:
        _fail("background music must loop")
        return false
    return true

# Task #97: staff clean and refill shelves as they go down; the shelf
# picture shows 0-9 items per tile; people slide between squares.
func _check_staff_work(config: Dictionary) -> bool:
    var work: Dictionary = config["guide_starting_store"]["staff_work"]
    if "REMAKE_BALANCED_DEFAULT" not in str(work["evidence_note"]):
        _fail("the staff work rules must stay tagged REMAKE_BALANCED_DEFAULT")
        return false
    var store_view_script = load("res://scripts/store_view.gd")
    for case in [[40, 40, 1, 9], [35, 40, 1, 8], [1, 40, 1, 1], [0, 40, 1, 0], [40, 40, 2, 18], [20, 40, 2, 9]]:
        if store_view_script.visible_item_count(case[0], case[1], case[2]) != case[3]:
            _fail("shelf picture item count for %s must be %d" % [case, case[3]])
            return false
    # A fresh copy: earlier checks change the shared config (e.g. restock).
    var fresh: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(CONFIG_PATH))
    var simulation = VerticalSliceSimulationScript.new(GuideStartingStoreScript.apply(fresh))
    var bread = simulation.inventory.get_product("product-bread-1")
    if simulation.restock_trigger_units(bread) != 35:
        _fail("a 40-unit shelf is refilled once it is at or below 8/9 full (35)")
        return false
    # Take items off one shelf: a staff member goes to refill it.
    bread.stock_units = 35
    var restocked := false
    var cleaned := false
    for tick in 1200:
        simulation.tick()
        if simulation.event_log.count_type("inventory_restock") > 0:
            restocked = true
        if simulation.event_log.count_type("staff_cleaned") > 0:
            cleaned = true
        if restocked and cleaned:
            break
    if not restocked:
        _fail("staff must refill a shelf that has gone down to its trigger level")
        return false
    if not cleaned:
        _fail("staff must clean where customers have walked")
        return false
    var checkout_id: String = simulation.staff.checkout_staff_id
    for event in simulation.event_log.records:
        if str(event["event_type"]) == "staff_cleaned" and str(event["details"]["staff_id"]) == checkout_id:
            _fail("the register clerk stays at the register instead of cleaning")
            return false
    # The prototype scenarios keep their old rules.
    var prototype = VerticalSliceSimulationScript.new(fresh)
    if prototype.restock_trigger_units(prototype.inventory.get_product("prototype-bread")) != int(fresh["simulation"]["restock_trigger_stock_units_at_or_below"]):
        _fail("the prototype store keeps its fixed restock trigger")
        return false
    # Smooth movement: halfway through a tick a mover is halfway between squares.
    var view = store_view_script.new()
    view.tick_serial = 1
    view.tick_progress = 1.0
    view._moving_center("x", Vector2i(2, 2))
    view.tick_serial = 2
    view.tick_progress = 0.5
    var halfway: Array = view._moving_center("x", Vector2i(3, 2))
    var expected_halfway: Vector2 = (view._cell_center(Vector2i(2, 2)) + view._cell_center(Vector2i(3, 2))) / 2.0
    if not (halfway[0] as Vector2).is_equal_approx(expected_halfway) or str(halfway[1]) != "B":
        _fail("a mover must be drawn halfway between squares halfway through a tick, on its second walk frame")
        return false
    view.tick_serial = 3
    view.tick_progress = 0.2
    var standing: Array = view._moving_center("x", Vector2i(3, 2))
    if not (standing[0] as Vector2).is_equal_approx(view._cell_center(Vector2i(3, 2))):
        _fail("a mover that did not move this tick stands still")
        return false
    view.free()
    return true

# Task #98: the rival's 本店 and 2号店 on the town map, sharing customers
# where their catchments overlap the player's store.
func _check_rivals() -> bool:
    var fresh: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(CONFIG_PATH))
    var guide_rivals: Array = fresh["guide_town_map"]["rival_stores"]
    if guide_rivals.size() != 2 or "REMAKE_BALANCED_DEFAULT" not in str(fresh["guide_town_map"]["evidence_note"]):
        _fail("the beginner map has the rival 本店 and 2号店, placed by a tagged REMAKE rule")
        return false
    var simulation = VerticalSliceSimulationScript.new(GuideStartingStoreScript.apply(fresh))
    if simulation._rival_stores.size() != 2 or simulation.town.store_count_including_rivals != 3:
        _fail("a new game must start with both rival stores in town")
        return false
    var hq: Vector2i = simulation._rival_stores[0]["position"]
    var near: Dictionary = simulation.store_site_quote(hq + Vector2i(3, 1))
    if bool(near["buildable"]):
        _fail("no store may be built within 5 squares of a rival")
        return false
    # A site sharing its catchment with the rival draws fewer people than it
    # would alone; a site far from both keeps them all.
    var shared_site := hq + Vector2i(6, 0)
    var alone: int = simulation.store_site.nearby_population(shared_site, 2000, [], [])
    var shared: int = int(simulation.store_site_quote(shared_site)["nearby_population"])
    if not bool(simulation.store_site_quote(shared_site)["buildable"]) or shared >= alone:
        _fail("a rival nearby must take part of a site's customers (%d vs %d alone)" % [shared, alone])
        return false
    simulation.economy.cash_yen = 200_000_000
    if not simulation.try_buy_store_site(Vector2i(13, 21)):
        _fail("the vacant site (13, 21) must be buyable in the real game")
        return false
    if simulation.demand.rival_store_count != 0:
        _fail("with rivals on the map, competition is the shared catchment, not the flat dilution too")
        return false
    return true

# Task #99: stamina -- work uses it up, at 0 the staff member rests in the
# break room until full, then goes back to work.
func _check_stamina() -> bool:
    var fresh: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(CONFIG_PATH))
    if not bool(fresh["guide_starting_store"]["staff_work"]["stamina_enabled"]):
        _fail("the real game must use stamina")
        return false
    var simulation = VerticalSliceSimulationScript.new(GuideStartingStoreScript.apply(fresh))
    var cleaner = simulation.staff.members["staff-3"]
    var expected_max: int = int(simulation._staff_candidate_catalog[cleaner.candidate_id]["stamina"])
    if cleaner.stamina_max != expected_max or cleaner.stamina != expected_max:
        _fail("a staff member starts with their printed 体力")
        return false
    cleaner.stamina = 1
    var exhausted_at := -1
    var rested_at := -1
    var back_to_work := false
    for tick in 3000:
        simulation.tick()
        if exhausted_at < 0 and cleaner.exhausted:
            exhausted_at = tick
        if exhausted_at >= 0 and rested_at < 0:
            if cleaner.state != "idle":
                _fail("an exhausted staff member takes no new task")
                return false
            if not cleaner.exhausted:
                rested_at = tick
                if cleaner.stamina != cleaner.stamina_max:
                    _fail("rest lasts until 体力 is full")
                    return false
        if rested_at >= 0 and cleaner.state in ["to_clean", "cleaning", "to_restock", "restocking"]:
            back_to_work = true
            break
    if exhausted_at < 0 or simulation.event_log.count_type("staff_exhausted") < 1:
        _fail("a finished task at 1 体力 must exhaust the staff member")
        return false
    if rested_at < 0 or not back_to_work:
        _fail("an exhausted staff member rests in the break room, recovers and goes back to work")
        return false
    # The prototype scenarios never tire.
    var prototype = VerticalSliceSimulationScript.new(fresh)
    prototype.staff.members["staff-2"].stamina = 1
    prototype._spend_stamina(prototype.staff.members["staff-2"])
    if prototype.staff.members["staff-2"].exhausted:
        _fail("stamina is off in the prototype scenarios")
        return false
    return true


# Task #100: economy actions that touch no fixture work while customers
# are in the store; layout edits still wait for them to leave.
func _check_actions_while_open(config: Dictionary) -> bool:
    var fresh: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(CONFIG_PATH))
    var simulation = VerticalSliceSimulationScript.new(fresh)
    simulation.economy.cash_yen = 500_000_000
    if simulation.customers.all_settled():
        _fail("a new simulation starts with a customer in the store")
        return false
    if not simulation.try_purchase_permit("tobacco"):
        _fail("a permit can be bought while customers are in the store")
        return false
    if not simulation.try_purchase_promotion("direct_mail"):
        _fail("advertising can be bought while customers are in the store")
        return false
    if not simulation.try_set_price_policy(-10):
        _fail("the price policy can change while customers are in the store")
        return false
    if not simulation.try_expand_chain():
        _fail("the chain can expand while customers are in the store")
        return false
    var shelf_id := str(fresh["fixtures"][0]["id"])
    if simulation.try_relocate_fixture(shelf_id, Vector2i(0, 12)):
        _fail("moving a fixture still waits for customers to leave")
        return false
    return true

# Task #101: investigating and buying out the rival's branch.
func _check_rival_buyout() -> bool:
    var fresh: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(CONFIG_PATH))
    var simulation = VerticalSliceSimulationScript.new(GuideStartingStoreScript.apply(fresh))
    simulation.economy.cash_yen = 200_000_000
    simulation.try_buy_store_site(Vector2i(13, 21))
    if simulation.rival_is_buyable("rival-hq") or simulation.try_buy_out_rival("rival-hq"):
        _fail("the rival 本店 cannot be bought")
        return false
    if simulation.rival_buyout_price_yen("rival-02") != 46_721_490:
        _fail("the 2号店 costs the guide's 46,721,490 at the start")
        return false
    var cash_before: int = simulation.economy.cash_yen
    if not simulation.try_investigate_rival("rival-02") or simulation.economy.cash_yen != cash_before - 600_000:
        _fail("investigating a rival costs 600,000")
        return false
    if simulation.try_investigate_rival("rival-02"):
        _fail("a rival is investigated once")
        return false
    var population_before: int = simulation.demand.nearby_population
    cash_before = simulation.economy.cash_yen
    if not simulation.try_buy_out_rival("rival-02"):
        _fail("the 2号店 can be bought with enough cash")
        return false
    if simulation.economy.cash_yen != cash_before - 46_721_490 or simulation.player_store_count != 2:
        _fail("buying out pays the price and adds a store to the chain")
        return false
    if simulation._rival_stores.size() != 1 or simulation.owned_branches.size() != 1 or simulation.rival_at(Vector2i(27, 9)) != "":
        _fail("the bought branch is no longer a rival")
        return false
    if simulation.demand.nearby_population < population_before:
        _fail("buying out a rival never loses the main store customers")
        return false
    var saved: Dictionary = simulation.save_state()
    var reloaded = VerticalSliceSimulationScript.new(GuideStartingStoreScript.apply(fresh))
    if not reloaded.load_state(saved) or reloaded.owned_branches.size() != 1 or reloaded._rival_stores.size() != 1 or not reloaded.rival_investigated("rival-02"):
        _fail("load must keep the bought branch and the investigation")
        return false
    reloaded.reset()
    if reloaded._rival_stores.size() != 2 or not reloaded.owned_branches.is_empty():
        _fail("a new game starts with both rivals again")
        return false
    return true
