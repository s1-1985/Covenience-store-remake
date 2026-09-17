class_name StaffState
extends RefCounted

var staff_id: String
var position := Vector2i.ZERO
var state := "idle"
var route: Array[Vector2i] = []
var restock_target_product_id := ""
var restock_ticks_remaining := 0
var _start_position := Vector2i.ZERO


func _init(staff_config: Dictionary) -> void:
    staff_id = str(staff_config["id"])
    _start_position = _vec2i(staff_config["start_subcell"])
    assert(not staff_id.is_empty())
    reset()


func reset() -> void:
    position = _start_position
    state = "idle"
    route = []
    restock_target_product_id = ""
    restock_ticks_remaining = 0


func begin_restock(product_id: String, initial_route: Array[Vector2i]) -> void:
    assert(state == "idle" and not product_id.is_empty())
    restock_target_product_id = product_id
    restock_ticks_remaining = 0
    route = initial_route
    state = "to_restock"


func finish_restock() -> void:
    restock_target_product_id = ""
    restock_ticks_remaining = 0
    state = "idle"


func move_along_route(next_state: String) -> bool:
    if not route.is_empty():
        position = route.pop_front()
    if route.is_empty():
        state = next_state
        return true
    return false


func _vec2i(value: Array) -> Vector2i:
    return Vector2i(int(value[0]), int(value[1]))
