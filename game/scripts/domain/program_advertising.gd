extends RefCounted
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
