class_name CheckoutAnger
extends RefCounted

# --- CONFIRMED_COMMUNITY / REMAKE_BALANCED_DEFAULT house rule -------------
#
# Ported from reference_sim/conveni_sim/checkout_anger_penalty.py +
# checkout_anger_timing.py. CONFIRMED_COMMUNITY: first-title dedicated
# community research states that checkout anger lowers register,
# replenishment, security, cleaning and service by exactly -2 each, while
# education and stamina are unaffected (docs/research/checkout-staff-
# dispatch-evidence-2026-09-05.md section 5, PROJECT_MEMORY.md section 6:
# "Low register skill can make checkout extremely slow and cause customer
# anger"). The lower-bound floor for the penalty is NOT confirmed by any
# source; MINIMUM_SKILL_VALUE reuses `0`, the same non-negative floor this
# codebase already enforces on every skill field elsewhere (StaffState's
# own asserts), rather than inventing a new number for this one mechanic.
#
# The trigger threshold (when does a slow checkout actually make the
# customer angry) is REMAKE_BALANCED_DEFAULT: reference_sim's own
# checkout_anger_timing.py deliberately leaves it to a caller-supplied
# policy ("the coordinator never invents an anger threshold"). Rather than
# inventing an unrelated absolute wait-time number, this client anchors the
# threshold to the same confirmed relationship CheckoutTiming (task #33)
# already implements: the guide's own fact is specifically that a LOW
# register_skill makes checkout SERVICE take extremely long, so the trigger
# is expressed as a multiple of the reference (median-skill) service
# duration CheckoutTiming already computes, not a new standalone constant.
# A staff member at or above the reference register_skill (this vertical
# slice's staff-1/staff-2 both are) never crosses it; only a
# below-reference hire actually risks angering a customer, matching the
# guide's own causal story.
const SKILL_DELTA := -2
const MINIMUM_SKILL_VALUE := 0
const TRIGGER_MULTIPLIER := 2.0


# Ticks a checkout service may run before the customer becomes angry, given
# `reference_ticks` (this client's `simulation.checkout_ticks` config value,
# i.e. the duration at CheckoutTiming.REFERENCE_REGISTER_SKILL).
func trigger_ticks(reference_ticks: int) -> int:
    assert(reference_ticks > 0)
    return int(ceil(float(reference_ticks) * TRIGGER_MULTIPLIER))


# Applies the confirmed -2 penalty to every affected skill on staff_member,
# clamped at MINIMUM_SKILL_VALUE. Returns {"skill_name": {"before", "after"}}
# for every skill actually changed (a skill already at the floor still
# reports before == after, since the -2 delta always "applies", it just has
# no further room to move).
func apply_penalty(staff_member) -> Dictionary:
    var results: Dictionary = {}
    results["register_skill"] = _apply(staff_member, "register_skill")
    results["replenishment_skill"] = _apply(staff_member, "replenishment_skill")
    results["security_skill"] = _apply(staff_member, "security_skill")
    results["cleaning_skill"] = _apply(staff_member, "cleaning_skill")
    results["service_skill"] = _apply(staff_member, "service_skill")
    return results


func _apply(staff_member, skill_field: String) -> Dictionary:
    var before: int
    match skill_field:
        "register_skill":
            before = staff_member.register_skill
        "replenishment_skill":
            before = staff_member.replenishment_skill
        "security_skill":
            before = staff_member.security_skill
        "cleaning_skill":
            before = staff_member.cleaning_skill
        "service_skill":
            before = staff_member.service_skill
        _:
            push_error("Unknown checkout-anger skill field: %s" % skill_field)
            return {}
    var after: int = max(MINIMUM_SKILL_VALUE, before + SKILL_DELTA)
    match skill_field:
        "register_skill":
            staff_member.register_skill = after
        "replenishment_skill":
            staff_member.replenishment_skill = after
        "security_skill":
            staff_member.security_skill = after
        "cleaning_skill":
            staff_member.cleaning_skill = after
        "service_skill":
            staff_member.service_skill = after
    return {"before": before, "after": after}
