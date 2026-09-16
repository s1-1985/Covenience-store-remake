class_name StaffState
extends RefCounted

var staff_id: String
var position := Vector2i.ZERO
var state := "waiting_checkout"
var _start_position := Vector2i.ZERO


func _init(staff_config: Dictionary) -> void:
    staff_id = str(staff_config["id"])
    _start_position = _vec2i(staff_config["start_subcell"])
    assert(not staff_id.is_empty())
    reset()


func reset() -> void:
    position = _start_position
    state = "waiting_checkout"


func _vec2i(value: Array) -> Vector2i:
    return Vector2i(int(value[0]), int(value[1]))
