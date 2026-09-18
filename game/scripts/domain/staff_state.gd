class_name StaffState
extends RefCounted

var staff_id: String
var position := Vector2i.ZERO
var state := "idle"
var route: Array[Vector2i] = []
var restock_target_product_id := ""
var restock_ticks_remaining := 0
var service_skill: int
var security_skill: int
var cleaning_skill: int
var register_skill: int
var _start_position := Vector2i.ZERO


func _init(staff_config: Dictionary) -> void:
    staff_id = str(staff_config["id"])
    _start_position = _vec2i(staff_config["start_subcell"])
    # CONFIRMED: the guide's skill-growth model (register/service/
    # replenishment/cleaning/security, book page 26) exists, but this
    # client has not ported the growth system itself yet (no work-event
    # counting, no manager-education bonus) -- see
    # reference_sim/conveni_sim/staff.py's StaffRuntimeState/
    # StaffGrowthOpportunity. These four fields are therefore static for
    # the lifetime of a StaffState and never change on their own, whatever
    # their starting value's own evidence level is. The vertical slice's
    # `data/vertical_slice.json` now sources staff-1/staff-2's starting
    # values from two of the 35 named CONFIRMED_OFFICIAL strategy-guide
    # candidates in that file's `staff_candidates` (task #32), not an
    # arbitrary guess; a caller that omits a field here still silently
    # falls back to a REMAKE_BALANCED_DEFAULT `0` rather than asserting,
    # since this class has no way to tell a real candidate's config apart
    # from a placeholder one. register_skill is consumed by
    # `CheckoutTiming` (task #33) to vary checkout duration per staff
    # member instead of a single flat tick count for everyone.
    service_skill = int(staff_config.get("service_skill", 0))
    security_skill = int(staff_config.get("security_skill", 0))
    cleaning_skill = int(staff_config.get("cleaning_skill", 0))
    register_skill = int(staff_config.get("register_skill", 0))
    assert(not staff_id.is_empty())
    assert(service_skill >= 0 and security_skill >= 0 and cleaning_skill >= 0)
    assert(register_skill >= 0)
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
