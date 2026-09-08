class_name StaffRoster
extends RefCounted

const StaffStateScript := preload("res://scripts/domain/staff_state.gd")

var members: Dictionary = {}
var checkout_staff_id: String
var _member_configs: Array


func _init(staff_config: Dictionary) -> void:
    checkout_staff_id = str(staff_config["checkout_staff_id"])
    _member_configs = staff_config["members"].duplicate(true)
    assert(not checkout_staff_id.is_empty() and not _member_configs.is_empty())
    reset()


func reset() -> void:
    members.clear()
    for member_config in _member_configs:
        var staff = StaffStateScript.new(member_config)
        assert(not members.has(staff.staff_id))
        members[staff.staff_id] = staff
    assert(members.has(checkout_staff_id))


func checkout_staff():
    assert(members.has(checkout_staff_id))
    return members[checkout_staff_id]


func all_staff() -> Array:
    return members.values()
