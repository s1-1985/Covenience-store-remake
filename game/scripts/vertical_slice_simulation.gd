class_name VerticalSliceSimulation
extends RefCounted

const StoreLayoutScript := preload("res://scripts/domain/store_layout.gd")
const InventoryCatalogScript := preload("res://scripts/domain/inventory_catalog.gd")
const EconomyStateScript := preload("res://scripts/domain/economy_state.gd")
const CustomerRosterScript := preload("res://scripts/domain/customer_roster.gd")
const StaffRosterScript := preload("res://scripts/domain/staff_roster.gd")
const RuntimeEventLogScript := preload("res://scripts/domain/runtime_event_log.gd")

var config: Dictionary
var layout
var inventory
var economy
var customers
var staff
var event_log

var minute_of_day: int
var last_event := "store opened"
var _checkout_interaction := Vector2i.ZERO
var _shopping_ticks: int
var _checkout_ticks: int
var _step_game_minutes: int


func _init(source_config: Dictionary) -> void:
    config = source_config.duplicate(true)
    _require_config()
    layout = StoreLayoutScript.new(config["store"], config["fixtures"])
    inventory = InventoryCatalogScript.new(config["products"])
    economy = EconomyStateScript.new(config["economy"])
    customers = CustomerRosterScript.new(config["customer"])
    staff = StaffRosterScript.new(config["staff"])
    event_log = RuntimeEventLogScript.new()
    var simulation: Dictionary = config["simulation"]
    _checkout_interaction = layout.interaction_for_fixture(
        str(simulation["checkout_fixture_id"]),
        "checkout"
    )
    _shopping_ticks = int(simulation["shopping_ticks"])
    _checkout_ticks = int(simulation["checkout_ticks"])
    _step_game_minutes = int(simulation["step_game_minutes"])
    assert(_shopping_ticks > 0 and _checkout_ticks > 0 and _step_game_minutes > 0)
    assert(float(simulation["tick_seconds"]) > 0.0)
    for staff_member in staff.all_staff():
        assert(layout.is_walkable(staff_member.position))
    assert(_required_routes_are_reachable())
    reset()


func reset() -> void:
    minute_of_day = int(config["simulation"]["start_minute_of_day"])
    layout.reset()
    inventory.reset()
    economy.reset()
    customers.reset()
    staff.reset()
    event_log.reset()
    _refresh_interactions()
    _start_default_customer()


func start_next_customer() -> bool:
    if not customers.can_admit():
        return false
    _start_default_customer()
    return true


func start_explicit_customer(customer_id: String, product_ids: Array[String]) -> bool:
    if not customers.can_admit() or customer_id.is_empty():
        return false
    if customers.customers.has(customer_id) or not _product_plan_is_valid(product_ids):
        return false
    var first_interaction := _product_interaction(product_ids[0])
    var customer = customers.admit_explicit(
        customer_id,
        layout.entry,
        layout.find_path(layout.entry, first_interaction),
        product_ids
    )
    _record_customer_entered(customer)
    return true


func apply_explicit_restock(
    product_id: String,
    staff_id: String,
    quantity: int,
    total_cost_yen: int
) -> bool:
    if not customers.can_admit() or quantity <= 0 or total_cost_yen < 0:
        return false
    if not inventory.products.has(product_id) or not staff.members.has(staff_id):
        return false
    var resulting_stock: int = inventory.add_explicit_units(product_id, quantity)
    var expense: Dictionary = economy.record_explicit_expense(
        "inventory_restock",
        minute_of_day,
        total_cost_yen,
        {"product_id": product_id, "quantity": quantity, "staff_id": staff_id}
    )
    _record_event("inventory_restock", {
        "product_id": product_id,
        "quantity": quantity,
        "staff_id": staff_id,
        "expense_id": expense["expense_id"],
        "resulting_stock_units": resulting_stock,
    })
    return true


func try_relocate_fixture(fixture_id: String, new_origin: Vector2i) -> bool:
    if not customers.can_admit():
        return false
    if layout.fixture_origin(fixture_id) == Vector2i(-1, -1):
        return false
    var previous: Array = layout.fixture_snapshot()
    if not layout.try_move_fixture(fixture_id, new_origin):
        return false
    _refresh_interactions()
    if not _required_routes_are_reachable() or not _all_staff_are_walkable():
        layout.restore_fixture_snapshot(previous)
        _refresh_interactions()
        return false
    _record_event("fixture_relocated", {
        "fixture_id": fixture_id,
        "origin_subcell": [new_origin.x, new_origin.y],
    })
    return true


func try_rotate_fixture_clockwise(fixture_id: String) -> bool:
    if not customers.can_admit():
        return false
    var previous: Array = layout.fixture_snapshot()
    if not layout.try_rotate_fixture_clockwise(fixture_id):
        return false
    _refresh_interactions()
    if not _required_routes_are_reachable() or not _all_staff_are_walkable():
        layout.restore_fixture_snapshot(previous)
        _refresh_interactions()
        return false
    _record_event("fixture_rotated", {"fixture_id": fixture_id})
    return true


func step() -> void:
    minute_of_day = (minute_of_day + _step_game_minutes) % (24 * 60)
    var customer = customers.active()
    var checkout_staff = staff.checkout_staff()
    match customer.phase:
        "to_shelf":
            if customer.move_along_route("shopping"):
                customer.shopping_ticks_remaining = _shopping_ticks
                _record_event("customer_reached_product", {
                    "customer_id": customer.customer_id,
                    "product_id": customer.current_product_id(),
                })
        "shopping":
            customer.shopping_ticks_remaining -= 1
            if customer.shopping_ticks_remaining <= 0:
                var product_id: String = customer.current_product_id()
                var line: Dictionary = inventory.try_take_one(product_id)
                if not line.is_empty():
                    customer.add_basket_line(line)
                    _record_event("product_picked", {
                        "customer_id": customer.customer_id,
                        "product_id": product_id,
                    })
                else:
                    _record_event("product_unavailable", {
                        "customer_id": customer.customer_id,
                        "product_id": product_id,
                    })
                customer.advance_plan()
                var next_product_id: String = customer.current_product_id()
                if not next_product_id.is_empty():
                    customer.phase = "to_shelf"
                    customer.route = layout.find_path(
                        customer.position,
                        _product_interaction(next_product_id)
                    )
                elif customer.basket.is_empty():
                    customer.phase = "leaving"
                    customer.route = layout.find_path(customer.position, layout.exit)
                    _record_event("customer_leaving_without_sale", {
                        "customer_id": customer.customer_id,
                    })
                else:
                    customer.phase = "to_checkout"
                    customer.route = layout.find_path(customer.position, _checkout_interaction)
        "to_checkout":
            if customer.move_along_route("checkout"):
                customer.checkout_ticks_remaining = _checkout_ticks
                checkout_staff.state = "checkout"
                _record_event("checkout_started", {
                    "customer_id": customer.customer_id,
                    "staff_id": checkout_staff.staff_id,
                })
        "checkout":
            customer.checkout_ticks_remaining -= 1
            if customer.checkout_ticks_remaining <= 0:
                if not customer.basket.is_empty():
                    var record: Dictionary = economy.settle_basket(
                        customer.customer_id,
                        minute_of_day,
                        customer.basket
                    )
                    customer.mark_settled(record)
                checkout_staff.state = "waiting_checkout"
                customer.phase = "leaving"
                customer.route = layout.find_path(customer.position, layout.exit)
                _record_event("checkout_completed", {
                    "customer_id": customer.customer_id,
                    "staff_id": checkout_staff.staff_id,
                    "transaction_id": customer.settled_transaction_id,
                })
        "leaving":
            if customer.move_along_route("done"):
                _record_event("customer_exited", {"customer_id": customer.customer_id})
        "done":
            last_event = "day slice complete"
        _:
            push_error("Unknown customer phase: %s" % customer.phase)


func clock_text() -> String:
    return "%02d:%02d" % [minute_of_day / 60, minute_of_day % 60]


func snapshot() -> Dictionary:
    var customer = customers.active()
    var checkout_staff = staff.checkout_staff()
    return {
        "minute_of_day": minute_of_day,
        "clock_text": clock_text(),
        "cash_yen": economy.cash_yen,
        "stock_units": inventory.total_stock_units(),
        "inventory": _inventory_snapshot(),
        "customer_id": customer.customer_id,
        "customer_phase": customer.phase,
        "customer_position": customer.position,
        "staff_id": checkout_staff.staff_id,
        "staff_state": checkout_staff.state,
        "staff_position": checkout_staff.position,
        "staff_count": staff.members.size(),
        "customer_basket_count": customer.basket.size(),
        "customer_basket_total_yen": customer.basket_total_yen(),
        "completed_sales": economy.completed_sales,
        "last_sale": economy.last_sale_record(),
        "expenses_yen": economy.recorded_expenses_yen(),
        "event_count": event_log.records.size(),
        "completed_visits": customers.completed_count(),
        "started_visits": customers.customers.size(),
        "last_event": last_event,
    }


func _start_default_customer() -> void:
    var plan: Array[String] = customers.default_plan()
    var customer = customers.admit_default(
        layout.entry,
        layout.find_path(
            layout.entry,
            _product_interaction(plan[0])
        )
    )
    _record_customer_entered(customer)


func _record_customer_entered(customer) -> void:
    _record_event("customer_entered", {
        "customer_id": customer.customer_id,
        "planned_product_ids": customer.planned_product_ids.duplicate(),
    })


func observation_snapshot() -> Dictionary:
    return {
        "schema_version": 1,
        "provisional": true,
        "scenario_id": str(config["scenario_id"]),
        "events": event_log.snapshot(),
        "sales": economy.sale_records.duplicate(true),
        "expenses": economy.expense_records.duplicate(true),
        "inventory": _inventory_snapshot(),
    }


func _record_event(event_type: String, details: Dictionary = {}) -> void:
    event_log.append(event_type, minute_of_day, details)
    last_event = event_type.replace("_", " ")


func _refresh_interactions() -> void:
    _checkout_interaction = layout.interaction_for_fixture(
        str(config["simulation"]["checkout_fixture_id"]),
        "checkout"
    )


func _required_routes_are_reachable() -> bool:
    var cursor: Vector2i = layout.entry
    for product_id in config["customer"]["visit_plan_product_ids"]:
        var interaction := _product_interaction(str(product_id))
        if not layout.has_path(cursor, interaction):
            return false
        cursor = interaction
    return layout.has_path(cursor, _checkout_interaction) and layout.has_path(
        _checkout_interaction,
        layout.exit
    )


func _product_interaction(product_id: String) -> Vector2i:
    var product = inventory.get_product(product_id)
    return layout.interaction_for_fixture(product.fixture_id, "shelf")


func _product_plan_is_valid(product_ids: Array[String]) -> bool:
    if product_ids.is_empty():
        return false
    var seen: Dictionary = {}
    for product_id in product_ids:
        if product_id.is_empty() or seen.has(product_id) or not inventory.products.has(product_id):
            return false
        seen[product_id] = true
    var cursor: Vector2i = layout.entry
    for product_id in product_ids:
        var interaction := _product_interaction(product_id)
        if not layout.has_path(cursor, interaction):
            return false
        cursor = interaction
    return layout.has_path(cursor, _checkout_interaction)


func _inventory_snapshot() -> Array[Dictionary]:
    var rows: Array[Dictionary] = []
    for product_id in inventory.product_order:
        var product = inventory.get_product(product_id)
        rows.append({
            "product_id": product.product_id,
            "fixture_id": product.fixture_id,
            "stock_units": product.stock_units,
            "sale_price_yen": product.sale_price_yen,
        })
    return rows


func _all_staff_are_walkable() -> bool:
    for staff_member in staff.all_staff():
        if not layout.is_walkable(staff_member.position):
            return false
    return true


func _require_config() -> void:
    assert(int(config.get("schema_version", -1)) == 5)
    for key in ["store", "fixtures", "products", "economy", "provisional_restock", "staff", "customer", "simulation"]:
        if not config.has(key):
            push_error("vertical slice config missing required key: %s" % key)
            assert(false)
    assert(config.get("provisional", false) == true)
    var simulation: Dictionary = config["simulation"]
    for key in ["start_minute_of_day", "tick_seconds", "step_game_minutes", "shopping_ticks", "checkout_ticks", "checkout_fixture_id"]:
        if not simulation.has(key):
            push_error("vertical slice simulation config missing required key: %s" % key)
            assert(false)
