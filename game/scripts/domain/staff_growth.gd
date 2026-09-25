class_name StaffGrowth
extends RefCounted

# --- REMAKE_BALANCED_DEFAULT / CONFIRMED_COMMUNITY house rule -------------
#
# Ported from reference_sim/conveni_sim/staff_growth_resolution.py and
# remake_staff_growth.py. The strategy guide's own "仕事内容とパラメータ
# 変化の関係" diagram (book page 26) confirms each work task grows more than
# one skill at once: checkout -> register + service; replenish ->
# replenishment + cleaning + security (clean -> cleaning + security also
# exists per the guide, but this client has no standalone cleaning task/
# mechanic to hook it to, so that pair is not ported here). First-title
# dedicated community testing only measured a concrete per-action increment
# for ONE of the pairs this class resolves -- replenish growing
# replenishment_skill by +1 (EVIDENCE_BACKED_UNIT_GROWTH in
# staff_growth_resolution.py, CONFIRMED_COMMUNITY). The other four pairs
# (checkout->register, checkout->service, replenish->cleaning,
# replenish->security) have a confirmed *existence* but no confirmed
# *increment*; this project reuses the same +1 magnitude as a
# REMAKE_BALANCED_DEFAULT guess (the only magnitude ever evidenced for this
# kind of growth), exactly as remake_staff_growth.py's
# REMAKE_BALANCED_UNIT_GROWTH does for its own equivalent gap. Manager-
# education growth bonus (remake_staff_growth.py's
# MANAGER_TEACHING_BONUS_CHANCE_PER_EDUCATION_POINT) is deliberately NOT
# ported: this vertical slice has no "who is the manager among
# staff.members" designation to source a manager_education value from.
const UNIT_GROWTH := 1


# Returns one Dictionary per skill actually grown ({"skill", "before",
# "after"}); a skill already at its own growth ceiling is skipped, matching
# reference_sim's own cap-respecting resolve_growth_opportunity() /
# resolve_opportunity(). Growth ceilings are CONFIRMED_OFFICIAL (see
# staff_state.gd); the +1 magnitude applied here is the
# REMAKE_BALANCED_DEFAULT/CONFIRMED_COMMUNITY mix documented above.
func apply_checkout_growth(staff_member) -> Array[Dictionary]:
    var results: Array[Dictionary] = []
    _grow(staff_member, "register_skill", results)
    _grow(staff_member, "service_skill", results)
    return results


func apply_replenish_growth(staff_member) -> Array[Dictionary]:
    var results: Array[Dictionary] = []
    _grow(staff_member, "replenishment_skill", results)
    _grow(staff_member, "cleaning_skill", results)
    _grow(staff_member, "security_skill", results)
    return results


# Task #97: the guide's clean -> cleaning + security pair (book page 26),
# now that a cleaning task exists. Same +1 magnitude as above.
func apply_clean_growth(staff_member) -> Array[Dictionary]:
    var results: Array[Dictionary] = []
    _grow(staff_member, "cleaning_skill", results)
    _grow(staff_member, "security_skill", results)
    return results


func _grow(staff_member, skill_field: String, results: Array[Dictionary]) -> void:
    var before: int
    var ceiling: int
    match skill_field:
        "register_skill":
            before = staff_member.register_skill
            ceiling = staff_member.register_skill_growth_ceiling
        "service_skill":
            before = staff_member.service_skill
            ceiling = staff_member.service_skill_growth_ceiling
        "replenishment_skill":
            before = staff_member.replenishment_skill
            ceiling = staff_member.replenishment_skill_growth_ceiling
        "cleaning_skill":
            before = staff_member.cleaning_skill
            ceiling = staff_member.cleaning_skill_growth_ceiling
        "security_skill":
            before = staff_member.security_skill
            ceiling = staff_member.security_skill_growth_ceiling
        _:
            push_error("Unknown growth skill field: %s" % skill_field)
            return
    if before >= ceiling:
        return
    var after: int = min(before + UNIT_GROWTH, ceiling)
    match skill_field:
        "register_skill":
            staff_member.register_skill = after
        "service_skill":
            staff_member.service_skill = after
        "replenishment_skill":
            staff_member.replenishment_skill = after
        "cleaning_skill":
            staff_member.cleaning_skill = after
        "security_skill":
            staff_member.security_skill = after
    results.append({"skill": skill_field, "before": before, "after": after})
