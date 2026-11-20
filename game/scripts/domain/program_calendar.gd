extends RefCounted
# CONFIRMED_BINARY: 325E0 counter,29334 midnight,52DBC display,29524 effect.
static func initial() -> Dictionary:
    return {"pending":0,"festival":0,"last_midnight":-1,"event":{},"boundary":{}}

static func arrival(total: int, heads: int, pending: int) -> Dictionary:
    var next := (total+heads)&0xffffffff
    return {"total":next,"pending":next/10000 if next/10000>(total&0xffffffff)/10000 else pending}

static func midnight_kind(month: int, period: int, pending: int) -> String:
    if month==8 and period==4:return "festival"
    return "celebration" if pending>0 and pending<0x80000000 else ""

static func display_total(stores: Array) -> int:
    var total := 0
    for row in stores:
        if row.active and int(row.owner)==0:total=(total+int(row.entered))&0xffffffff
    return total

static func celebration_popularity(value: int, active: bool, owner: int) -> int:
    return 100 if active or owner==0 else value

static func valid(data: Variant) -> bool:
    if not data is Dictionary:return false
    for key in ["pending","festival","last_midnight"]:
        var value = data.get(key)
        if (not value is int and not value is float) or float(value)!=floorf(float(value)):return false
    if data.pending<0 or data.pending>0xffffffff or int(data.festival) not in [0,1] or data.last_midnight< -1:return false
    if not data.get("event") is Dictionary or not data.get("boundary") is Dictionary:return false
    var e:Dictionary=data.event
    if not e.is_empty():
        if e.get("kind") not in ["festival","celebration"]:return false
        for key in ["units","variant","wait_updates","day"]:
            var v = e.get(key)
            if (not v is int and not v is float) or float(v)!=floorf(float(v)) or v<0:return false
        if int(e.variant) not in [0,1] or e.wait_updates>120:return false
        if e.kind=="celebration" and (e.units<1 or e.units>429496):return false
        if data.boundary.is_empty():return false
    if e.is_empty() and not data.boundary.is_empty():return false
    var tail:Dictionary=data.boundary
    if not tail.is_empty():
        if not tail.get("closing") is bool:return false
        if tail.closing:
            if not tail.get("statement") is Dictionary or not tail.get("capital") is float and not tail.get("capital") is int:return false
            var statement:Dictionary=tail.statement
            for key in ["monthly","four_day_net_result_yen","month_result_yen","adjustment_yen","one_off_yen"]:
                if not statement.has(key):return false
            for key in ["four_day_net_result_yen","month_result_yen","adjustment_yen","one_off_yen"]:
                var v = statement[key]
                if (not v is int and not v is float) or float(v)!=floorf(float(v)):return false
            for section in ["representative","monthly"]:
                if not statement.get(section) is Dictionary:return false
                for field in ["sales_yen","maintenance_yen","wages_yen","promotion_yen","goods_yen"]:
                    var v = statement[section].get(field)
                    if (not v is int and not v is float) or float(v)!=floorf(float(v)):return false
            if float(tail.capital)!=floorf(float(tail.capital)):return false
    return true

static func normalized(data: Dictionary) -> Dictionary:
    var state: Dictionary = data.duplicate(true)
    for key in ["pending","festival","last_midnight"]:state[key]=int(state[key])
    if not state.event.is_empty():
        for key in ["units","variant","wait_updates","day"]:state.event[key]=int(state.event[key])
    if bool(state.boundary.get("closing",false)):
        state.boundary.capital=int(state.boundary.capital)
        var statement: Dictionary = state.boundary.statement
        for key in ["four_day_net_result_yen","month_result_yen","adjustment_yen","one_off_yen"]:statement[key]=int(statement[key])
        for section in ["representative","monthly"]:
            for field in ["sales_yen","maintenance_yen","wages_yen","promotion_yen","goods_yen"]:statement[section][field]=int(statement[section][field])
    return state
