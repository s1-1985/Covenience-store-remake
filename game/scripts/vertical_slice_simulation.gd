class_name VerticalSliceSimulation
extends RefCounted

const CARDINAL_DIRECTIONS := [
    Vector2i(1, 0),
    Vector2i(-1, 0),
    Vector2i(0, 1),
    Vector2i(0, -1),
]

var config: Dictionary
var width_subcells: int
var height_subcells: int
var blocked: Dictionary = {}

var minute_of_day: int
var cash_yen: int
var stock_units: int
var sale_price_yen: int
var shopping_ticks_remaining: int = 0
var checkout_ticks_remaining: int = 0
var customer_position := Vector2i.ZERO
var staff_position := Vector2i.ZERO
var customer_phase := "to_shelf"
var staff_state := "waiting_checkout"
var customer_has_product := false
var last_event := "store opened"
var completed_sales := 0

var _route: Array[Vector2i] = []
var _entry := Vector2i.ZERO
var _exit := Vector2i.ZERO
var _shelf_interaction := Vector2i.ZERO
var _checkout_interaction := Vector2i.ZERO
var _shopping_ticks: int
var _checkout_ticks: int
var _step_game_minutes: int


func _init(source_config: Dictionary) -> void:
    config = source_config.duplicate(true)
    _require_config()
    var store: Dictionary = config["store"]
    var simulation: Dictionary = config["simulation"]
    width_subcells = int(store["width_tiles"]) * int(store["subcells_per_tile"])
    height_subcells = int(store["height_tiles"]) * int(store["subcells_per_tile"])
    _entry = _vec2i(store["entry_subcell"])
    _exit = _vec2i(store["exit_subcell"])
    _shopping_ticks = int(simulation["shopping_ticks"])
    _checkout_ticks = int(simulation["checkout_ticks"])
    _step_game_minutes = int(simulation["step_game_minutes"])
    _build_blocked_cells()
    for fixture in config["fixtures"]:
        if fixture["kind"] == "shelf":
            _shelf_interaction = _vec2i(fixture["interaction_subcell"])
        elif fixture["kind"] == "checkout":
            _checkout_interaction = _vec2i(fixture["interaction_subcell"])
    reset()


func reset() -> void:
    minute_of_day = int(config["simulation"]["start_minute_of_day"])
    cash_yen = int(config["economy"]["initial_cash_yen"])
    stock_units = int(config["product"]["initial_stock_units"])
    sale_price_yen = int(config["product"]["sale_price_yen"])
    customer_position = _entry
    staff_position = _vec2i(config["staff"]["start_subcell"])
    customer_phase = "to_shelf"
    staff_state = "waiting_checkout"
    customer_has_product = false
    shopping_ticks_remaining = 0
    checkout_ticks_remaining = 0
    completed_sales = 0
    last_event = "customer entered"
    _route = _find_path(customer_position, _shelf_interaction)


func step() -> void:
    minute_of_day = (minute_of_day + _step_game_minutes) % (24 * 60)
    match customer_phase:
        "to_shelf":
            _move_customer_along_route("shopping")
            if customer_phase == "shopping":
                shopping_ticks_remaining = _shopping_ticks
                last_event = "customer reached shelf"
        "shopping":
            shopping_ticks_remaining -= 1
            if shopping_ticks_remaining <= 0:
                if stock_units > 0:
                    stock_units -= 1
                    customer_has_product = true
                    customer_phase = "to_checkout"
                    _route = _find_path(customer_position, _checkout_interaction)
                    last_event = "customer picked product"
                else:
                    customer_phase = "leaving"
                    _route = _find_path(customer_position, _exit)
                    last_event = "shelf empty; customer leaving"
        "to_checkout":
            _move_customer_along_route("checkout")
            if customer_phase == "checkout":
                checkout_ticks_remaining = _checkout_ticks
                staff_state = "checkout"
                last_event = "checkout service started"
        "checkout":
            checkout_ticks_remaining -= 1
            if checkout_ticks_remaining <= 0:
                if customer_has_product:
                    cash_yen += sale_price_yen
                    completed_sales += 1
                customer_has_product = false
                staff_state = "waiting_checkout"
                customer_phase = "leaving"
                _route = _find_path(customer_position, _exit)
                last_event = "checkout completed"
        "leaving":
            _move_customer_along_route("done")
            if customer_phase == "done":
                last_event = "customer left store"
        "done":
            last_event = "day slice complete"
        _:
            push_error("Unknown customer phase: %s" % customer_phase)


func clock_text() -> String:
    return "%02d:%02d" % [minute_of_day / 60, minute_of_day % 60]


func snapshot() -> Dictionary:
    return {
        "minute_of_day": minute_of_day,
        "clock_text": clock_text(),
        "cash_yen": cash_yen,
        "stock_units": stock_units,
        "customer_phase": customer_phase,
        "customer_position": customer_position,
        "staff_state": staff_state,
        "staff_position": staff_position,
        "customer_has_product": customer_has_product,
        "completed_sales": completed_sales,
        "last_event": last_event,
    }


func _move_customer_along_route(next_phase: String) -> void:
    if _route.is_empty():
        customer_phase = next_phase
        return
    customer_position = _route.pop_front()
    if _route.is_empty():
        customer_phase = next_phase


func _find_path(start: Vector2i, goal: Vector2i) -> Array[Vector2i]:
    if start == goal:
        return []
    var frontier: Array[Vector2i] = [start]
    var head := 0
    var came_from: Dictionary = {start: start}
    while head < frontier.size():
        var current: Vector2i = frontier[head]
        head += 1
        for direction in CARDINAL_DIRECTIONS:
            var candidate := current + direction
            if not _inside(candidate):
                continue
            if blocked.has(candidate) and candidate != goal:
                continue
            if came_from.has(candidate):
                continue
            came_from[candidate] = current
            if candidate == goal:
                return _reconstruct_path(came_from, start, goal)
            frontier.append(candidate)
    push_error("No path between %s and %s" % [start, goal])
    return []


func _reconstruct_path(came_from: Dictionary, start: Vector2i, goal: Vector2i) -> Array[Vector2i]:
    var reversed_path: Array[Vector2i] = []
    var current := goal
    while current != start:
        reversed_path.append(current)
        current = came_from[current]
    reversed_path.reverse()
    return reversed_path


func _build_blocked_cells() -> void:
    blocked.clear()
    var scale := int(config["store"]["subcells_per_tile"])
    for fixture in config["fixtures"]:
        var origin := _vec2i(fixture["origin_subcell"])
        var footprint: Array = fixture["footprint_tiles"]
        var width := int(footprint[0]) * scale
        var height := int(footprint[1]) * scale
        for y in range(origin.y, origin.y + height):
            for x in range(origin.x, origin.x + width):
                blocked[Vector2i(x, y)] = true


func _inside(cell: Vector2i) -> bool:
    return cell.x >= 0 and cell.y >= 0 and cell.x < width_subcells and cell.y < height_subcells


func _vec2i(value: Array) -> Vector2i:
    return Vector2i(int(value[0]), int(value[1]))


func _require_config() -> void:
    for key in ["store", "fixtures", "product", "economy", "staff", "customer", "simulation"]:
        if not config.has(key):
            push_error("vertical slice config missing required key: %s" % key)
            assert(false)
    assert(config.get("provisional", false) == true)
    var simulation: Dictionary = config["simulation"]
    for key in ["start_minute_of_day", "tick_seconds", "step_game_minutes", "shopping_ticks", "checkout_ticks"]:
        if not simulation.has(key):
            push_error("vertical slice simulation config missing required key: %s" % key)
            assert(false)
