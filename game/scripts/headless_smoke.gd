extends SceneTree

const VerticalSliceSimulationScript := preload("res://scripts/vertical_slice_simulation.gd")
const DemandPolicyScript := preload("res://scripts/domain/demand_policy.gd")
const CONFIG_PATH := "res://data/vertical_slice.json"
const MAIN_SCENE_PATH := "res://scenes/main.tscn"
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
    main_instance.free()

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
    if not simulation.try_relocate_fixture(shelf_id, Vector2i(4, 6)):
        _fail("valid completed-visit fixture relocation was rejected")
        return
    if simulation.layout.fixture_origin(shelf_id) != Vector2i(4, 6):
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
    var expected_four_day_net_result_yen: int = cash_before_month_end - 1000

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
    var expected_month_result_yen: int = (
        expected_four_day_net_result_yen * MONTH_MULTIPLIER_FOR_TEST
    )
    var expected_cash_after_month_end: int = cash_before_month_end + (
        expected_month_result_yen - expected_four_day_net_result_yen
    )
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

    print("Vertical-slice headless smoke passed in %d steps." % steps)
    quit(0)


func _run_visit(simulation) -> int:
    var steps := 0
    while simulation.customers.active().phase != "done" and steps < MAX_STEPS:
        simulation.step()
        steps += 1
    return steps


func _fail(message: String) -> void:
    push_error(message)
    quit(1)
