extends RefCounted

# CONFIRMED_BINARY 80027624..27770. The control is the signed scenario
# byte CD8A8, not a player-advertising probability or a new random default.
static func rival_selection(entries: Array, cash: int, control: int, rng) -> Array:
    var roll: int = rng.randi() % 4
    if roll > control: return []
    for index in range(entries.size()-1,-1,-1):
        if cash >= int(entries[index].cost_yen)*10:
            return [str(entries[index].promotion_id)]
    return []

# 80027A5C..27C64: no second cash gate. The payment is made once if
# an active rival exists; selection itself never reserves or debits cash.
static func rival_actions(entries: Array, enabled: Array, period: int, hour: int) -> Array:
    var actions: Array = []
    for entry in entries:
        if enabled.has(str(entry.promotion_id)) and period==int(entry.trigger_day) and hour==int(entry.trigger_hour):
            actions.append({"promotion_id":str(entry.promotion_id),"cost_yen":int(entry.cost_yen),"gain":int(entry.popularity_gain)})
    return actions
# CONFIRMED_BINARY 800275F8: exact representative period/hour at minute0,
# persistent company flags; insufficient cash (<5*cost) disables that flag.
static func plan(entries: Array, enabled: Array, period: int, hour: int, minute: int, cash: int) -> Dictionary:
    var active: Array = enabled.duplicate()
    var actions: Array = []
    if minute != 0: return {"enabled":active,"actions":actions,"cash_yen":cash}
    for entry in entries:
        var id := str(entry.promotion_id)
        if not active.has(id) or period!=int(entry.trigger_day) or hour!=int(entry.trigger_hour): continue
        var cost := int(entry.cost_yen)
        var fired := cash>=cost*5
        if fired: cash-=cost
        else: active.erase(id)
        actions.append({"promotion_id":id,"fired":fired,"cost_yen":cost,"gain":int(entry.popularity_gain)})
    return {"enabled":active,"actions":actions,"cash_yen":cash}
