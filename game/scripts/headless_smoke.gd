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
const CONFIG_PATH := "res://data/vertical_slice.json"
const MAIN_SCENE_PATH := "res://scenes/main.tscn"
const MAIN_MENU_SCENE_PATH := "res://scenes/main_menu.tscn"
const MAX_STEPS := 256
const REPRESENTATIVE_DAYS_PER_MONTH_FOR_TEST := 4
const MONTH_MULTIPLIER_FOR_TEST := 8


func _initialize() -> void:
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
        "UI/Panel/Margin/Scroll/VBox/RestockProductOption",
        "UI/Panel/Margin/Scroll/VBox/RestockButton",
        "UI/Panel/Margin/Scroll/VBox/PromotionOption",
        "UI/Panel/Margin/Scroll/VBox/BuyPromotionButton",
        "UI/Panel/Margin/Scroll/VBox/ExpandChainButton",
        "UI/Panel/Margin/Scroll/VBox/EjectCustomerOption",
        "UI/Panel/Margin/Scroll/VBox/EjectCustomerButton",
        "UI/Panel/Margin/Scroll/VBox/PriceChangeSpinBox",
        "UI/Panel/Margin/Scroll/VBox/SetPricePolicyButton",
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
    var simulation = VerticalSliceSimulationScript.new(config)
    if simulation.staff.members.size() < 2:
        _fail("actor roster smoke requires multiple retained staff states")
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
    while (
        concurrent_simulation.customers.completed_count() < completed_before_concurrency + 2
        and concurrent_steps < MAX_STEPS
    ):
        concurrent_simulation.step()
        concurrent_steps += 1
        var checkout_count := 0
        var waiting_count := 0
        for customer in concurrent_simulation.customers.active_customers():
            if customer.phase == "checkout":
                checkout_count += 1
            elif customer.phase == "waiting_checkout":
                waiting_count += 1
        if checkout_count > 1:
            simultaneous_checkout_violation = true
        if checkout_count == 1 and waiting_count >= 1:
            saw_simultaneous_wait = true
    steps += concurrent_steps

    if simultaneous_checkout_violation:
        _fail("no more than one customer may occupy the single checkout's service slot at once")
        return
    if not saw_simultaneous_wait:
        _fail("second customer never had to wait in the checkout queue behind the first")
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
    if int(upgrade_and_downgrade_evaluation["criteria_met"]) != 3:
        _fail("exactly 3 of the 5 rank-1 upgrade criteria must be counted as met")
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
    if abs(float(rating_event_details["security_value"]) - 57.0) > 0.0000001:
        _fail("security_value must equal total staff security_skill times the store's size-tier multiplier")
        return
    if abs(float(rating_event_details["cleaning_value"]) - 51.0) > 0.0000001:
        _fail("cleaning_value must equal total staff cleaning_skill times the store's size-tier multiplier")
        return
    # popularity=0, cleaning=51.0, security=57.0, 2 distinct stocked
    # products (assortment_score=10.0), opening_minutes_per_day=960
    # (hours_score=66.6667); service_value is expected_service_value above
    # (growth-dependent, see comment there). Recomputed with the same
    # CustomerShare class store_rating actually calls, rather than a
    # hand-derived literal that would go stale the moment checkout growth
    # changes service_value.
    var expected_customer_share_percent: int = customer_share.compute_customer_share_percent(
        0, expected_service_value, 51.0, 57.0, 2, 960
    )
    if int(rating_event_details["customer_share_percent"]) != expected_customer_share_percent:
        _fail("customer_share_percent must be recomputed from CustomerShare.compute_customer_share_percent()")
        return
    if abs(rating_simulation.demand.customer_share_percent - 25.0) > 0.0000001:
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
    if economy_ui_scene._restock_product_ids.find("product-purchase-1") < 0:
        _fail("economy UI: procuring a product must refresh the restock option list")
        return

    var bread_restock_index: int = economy_ui_scene._restock_product_ids.find("prototype-bread")
    if bread_restock_index < 0:
        _fail("economy UI: restock option did not include the default 'prototype-bread' product")
        return
    economy_ui_scene.restock_product_option.selected = bread_restock_index
    var stock_before_restock: int = economy_ui_scene.simulation.inventory.get_product("prototype-bread").stock_units
    var cash_before_explicit_restock: int = economy_ui_scene.simulation.economy.cash_yen
    economy_ui_scene._on_restock_pressed()
    var bread_product = economy_ui_scene.simulation.inventory.get_product("prototype-bread")
    if bread_product.stock_units != stock_before_restock + bread_product.initial_stock_units:
        _fail("economy UI: Restock must add exactly initial_stock_units of the selected product")
        return
    var expected_explicit_restock_cost: int = bread_product.initial_stock_units * bread_product.restock_unit_cost_yen
    if economy_ui_scene.simulation.economy.cash_yen != cash_before_explicit_restock - expected_explicit_restock_cost:
        _fail("economy UI: Restock must charge quantity * restock_unit_cost_yen")
        return

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

    print("Vertical-slice headless smoke passed in %d steps." % steps)
    quit(0)


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
