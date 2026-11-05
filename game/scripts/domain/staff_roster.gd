class_name StaffRoster
extends RefCounted

const StaffStateScript := preload("res://scripts/domain/staff_state.gd")

var members: Dictionary = {}
var checkout_staff_id: String
var _default_checkout_staff_id: String
var _member_configs: Array


func _init(staff_config: Dictionary) -> void:
    _default_checkout_staff_id = str(staff_config["checkout_staff_id"])
    checkout_staff_id = _default_checkout_staff_id
    _member_configs = staff_config["members"].duplicate(true)
    assert(not checkout_staff_id.is_empty() and not _member_configs.is_empty())
    reset()


func reset() -> void:
    checkout_staff_id = _default_checkout_staff_id
    members.clear()
    for member_config in _member_configs:
        var staff = StaffStateScript.new(member_config)
        assert(not members.has(staff.staff_id))
        members[staff.staff_id] = staff
    assert(members.has(checkout_staff_id))


func checkout_staff():
    if not members.has(checkout_staff_id):
        var vacant = StaffStateScript.new(_member_configs[0])
        vacant.candidate_id = ""
        vacant.state = "vacant"
        vacant.position = Vector2i(-1, -1)
        return vacant
    return members[checkout_staff_id]


func all_staff() -> Array:
    var result: Array = []
    var ids: Array = members.keys()
    ids.sort()
    for id in ids:
        result.append(members[id])
    return result


# Task #118: gives register duty to `staff_id`. The two swap posts: the new
# cashier's post becomes the register front, the old cashier's becomes the
# post the new one had.
func hand_over_checkout(staff_id: String) -> bool:
    if staff_id == checkout_staff_id or not members.has(staff_id):
        return false
    var previous = members[checkout_staff_id]
    var next = members[staff_id]
    var register_post: Vector2i = previous.home_position()
    previous.set_home_position(next.home_position())
    next.set_home_position(register_post)
    checkout_staff_id = staff_id
    return true
