extends SceneTree

const VerticalSliceSimulationScript := preload("res://scripts/vertical_slice_simulation.gd")
const CONFIG_PATH := "res://data/vertical_slice.json"
const MAIN_SCENE_PATH := "res://scenes/main.tscn"
const MAX_STEPS := 256


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
