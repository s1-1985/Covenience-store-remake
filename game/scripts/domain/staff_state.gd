class_name StaffState
extends RefCounted

var staff_id: String
# Task #56: identity fields the 35-candidate staff_candidates pool already
# carries per entry (CONFIRMED_OFFICIAL, task #32) but this class never
# stored -- there was no hiring UI to need them for until now. Not part of
# reset()'s work-growth restoration (identity isn't growth), but changed
# by hire() below and persisted through save/load like any other durable
# roster fact.
var candidate_id: String
var display_name: String
var position := Vector2i.ZERO
var state := "idle"
var route: Array[Vector2i] = []
var restock_target_product_id := ""
var restock_ticks_remaining := 0
# Task #88: where an otherwise-idle staff member is on the store floor's
# rest cycle (guide p.16: staff rest in the break room while no customers
# are in the store). "" = at/around their post, "to_break_room",
# "resting", "to_post". Kept separate from `state` so a resting staff
# member still counts as idle for restock assignment and for the
# "no work in progress" checks that gate player edits.
var rest_phase := ""
# Task #99: stamina (体力). stamina_max is the candidate's printed 体力;
# `exhausted` is set when stamina runs out and cleared once it is full again.
var stamina := 0
var stamina_max := 0
var exhausted := false
var service_skill: int
var security_skill: int
var cleaning_skill: int
var register_skill: int
var replenishment_skill: int
var salary_yen_per_day_24h: int
var service_skill_growth_ceiling: int
var register_skill_growth_ceiling: int
var cleaning_skill_growth_ceiling: int
var replenishment_skill_growth_ceiling: int
var security_skill_growth_ceiling: int
var _start_position := Vector2i.ZERO
var _start_service_skill: int
var _start_security_skill: int
var _start_cleaning_skill: int
var _start_register_skill: int
var _start_replenishment_skill: int


func _init(staff_config: Dictionary) -> void:
    staff_id = str(staff_config["id"])
    candidate_id = str(staff_config.get("candidate_id", ""))
    display_name = str(staff_config.get("display_name", ""))
    _start_position = _vec2i(staff_config["start_subcell"])
    # CONFIRMED: the guide's skill-growth model (register/service/
    # replenishment/cleaning/security, book page 26) exists. This client
    # now ports the work-event side of it (task #48:
    # `StaffGrowth.apply_checkout_growth()`/`apply_replenish_growth()`,
    # wired into `VerticalSliceSimulation` at checkout/restock task
    # completion) but not the manager-education bonus from
    # `reference_sim/conveni_sim/remake_staff_growth.py`, since this
    # vertical slice has no "who is the manager among staff.members"
    # designation to source a manager_education value from. The
    # `*_skill_growth_ceiling` fields below are each CONFIRMED_OFFICIAL
    # (the guide's own "能力の分岐ポイント" value per skill, ported
    # verbatim from the bound `staff_candidates` entry, same as the five
    # skills themselves), not invented caps. The vertical slice's
    # `data/vertical_slice.json` sources staff-1/staff-2's starting
    # values from two of the 35 named CONFIRMED_OFFICIAL strategy-guide
    # candidates in that file's `staff_candidates` (task #32 for the five
    # skills, task #47 for salary_yen_per_day_24h, task #48 for the five
    # growth ceilings -- the same duplication-from-candidate pattern each
    # time), not an arbitrary guess; a caller that omits a field here
    # still silently falls back to a REMAKE_BALANCED_DEFAULT `0` rather
    # than asserting, since this class has no way to tell a real
    # candidate's config apart from a placeholder one. register_skill is
    # consumed by `CheckoutTiming` (task #33) to vary checkout duration
    # per staff member instead of a single flat tick count for everyone;
    # replenishment_skill is consumed the same way by `RestockTiming`
    # (task #40) for restock duration; salary_yen_per_day_24h is consumed
    # by `VerticalSliceSimulation._apply_daily_staff_wages()` (task #47).
    service_skill = int(staff_config.get("service_skill", 0))
    security_skill = int(staff_config.get("security_skill", 0))
    cleaning_skill = int(staff_config.get("cleaning_skill", 0))
    register_skill = int(staff_config.get("register_skill", 0))
    replenishment_skill = int(staff_config.get("replenishment_skill", 0))
    salary_yen_per_day_24h = int(staff_config.get("salary_yen_per_day_24h", 0))
    service_skill_growth_ceiling = int(staff_config.get("service_skill_growth_ceiling", 0))
    register_skill_growth_ceiling = int(staff_config.get("register_skill_growth_ceiling", 0))
    cleaning_skill_growth_ceiling = int(staff_config.get("cleaning_skill_growth_ceiling", 0))
    replenishment_skill_growth_ceiling = int(
        staff_config.get("replenishment_skill_growth_ceiling", 0)
    )
    security_skill_growth_ceiling = int(staff_config.get("security_skill_growth_ceiling", 0))
    assert(not staff_id.is_empty())
    assert(service_skill >= 0 and security_skill >= 0 and cleaning_skill >= 0)
    assert(register_skill >= 0 and replenishment_skill >= 0 and salary_yen_per_day_24h >= 0)
    assert(
        service_skill_growth_ceiling >= 0 and register_skill_growth_ceiling >= 0
        and cleaning_skill_growth_ceiling >= 0
    )
    assert(
        replenishment_skill_growth_ceiling >= 0 and security_skill_growth_ceiling >= 0
    )
    _start_service_skill = service_skill
    _start_security_skill = security_skill
    _start_cleaning_skill = cleaning_skill
    _start_register_skill = register_skill
    _start_replenishment_skill = replenishment_skill
    reset()


# Restores every skill to its config-derived starting value, undoing any
# work-event growth (task #48) accumulated since this StaffState was
# constructed. Growth ceilings never change, so they are not part of this
# reset. This keeps `VerticalSliceSimulation.load_state()`'s existing
# "clears every subsystem back to its config-derived starting point"
# contract honest now that skills are no longer static for the lifetime of
# a StaffState -- skill growth itself is not part of the save/load format
# (see save_state()'s own note on what stays unsaved), so a save/load round
# trip currently reverts any accumulated growth rather than preserving it.
func reset() -> void:
    position = _start_position
    state = "idle"
    route = []
    restock_target_product_id = ""
    restock_ticks_remaining = 0
    rest_phase = ""
    service_skill = _start_service_skill
    security_skill = _start_security_skill
    cleaning_skill = _start_cleaning_skill
    register_skill = _start_register_skill
    replenishment_skill = _start_replenishment_skill


# Task #56: replaces whoever currently occupies this roster slot with a
# different candidate (CONFIRMED_OFFICIAL data from the same
# staff_candidates pool _init() already draws from), re-baselining every
# skill/ceiling/salary/identity field -- including _start_* -- so a later
# reset() (e.g. from load_state()) restores to the NEWLY hired person, not
# the one they replaced. staff_id and position stay put: they describe the
# store's own roster slot/register-front standing spot, not the person
# filling it. Any accumulated skill growth (task #48) the previous
# occupant had is discarded, matching how firing someone in a real
# register-front role doesn't carry their learned proficiency to whoever
# replaces them.
func hire(new_candidate_config: Dictionary) -> void:
    candidate_id = str(new_candidate_config.get("candidate_id", ""))
    display_name = str(new_candidate_config.get("display_name", ""))
    service_skill = int(new_candidate_config.get("service_skill", 0))
    security_skill = int(new_candidate_config.get("security_skill", 0))
    cleaning_skill = int(new_candidate_config.get("cleaning_skill", 0))
    register_skill = int(new_candidate_config.get("register_skill", 0))
    replenishment_skill = int(new_candidate_config.get("replenishment_skill", 0))
    salary_yen_per_day_24h = int(new_candidate_config.get("salary_yen_per_day_24h", 0))
    service_skill_growth_ceiling = int(new_candidate_config.get("service_skill_growth_ceiling", 0))
    register_skill_growth_ceiling = int(new_candidate_config.get("register_skill_growth_ceiling", 0))
    cleaning_skill_growth_ceiling = int(new_candidate_config.get("cleaning_skill_growth_ceiling", 0))
    replenishment_skill_growth_ceiling = int(
        new_candidate_config.get("replenishment_skill_growth_ceiling", 0)
    )
    security_skill_growth_ceiling = int(new_candidate_config.get("security_skill_growth_ceiling", 0))
    _start_service_skill = service_skill
    _start_security_skill = security_skill
    _start_cleaning_skill = cleaning_skill
    _start_register_skill = register_skill
    _start_replenishment_skill = replenishment_skill
    state = "idle"
    rest_phase = ""
    route = []
    restock_target_product_id = ""
    restock_ticks_remaining = 0


func begin_restock(product_id: String, initial_route: Array[Vector2i]) -> void:
    assert(state == "idle" and not product_id.is_empty())
    restock_target_product_id = product_id
    restock_ticks_remaining = 0
    rest_phase = ""
    route = initial_route
    state = "to_restock"


func finish_restock() -> void:
    restock_target_product_id = ""
    restock_ticks_remaining = 0
    state = "idle"


func home_position() -> Vector2i:
    return _start_position


func move_along_route(next_state: String) -> bool:
    if not route.is_empty():
        position = route.pop_front()
    if route.is_empty():
        state = next_state
        return true
    return false


func _vec2i(value: Array) -> Vector2i:
    return Vector2i(int(value[0]), int(value[1]))
