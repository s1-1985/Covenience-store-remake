class_name ProgramProgression
extends RefCounted

const LIMITS := [[50000, 100000, 200000, 400000, 500000], [100000000, 200000000, 300000000, 400000000, 600000000], [3000, 8000, 14000, 18000, 20000], [10, 30, 50, 70, 90]]

# CONFIRMED_BINARY: progression.py, 8003EAD4 / 8002A864 / 8005A228 / 8006D8EC.
static func signed8(value: int) -> int:
    value &= 255
    return value - 256 if value >= 128 else value

static func store_milestone(stores: Array, mode: int, flags: int, pending: int) -> Dictionary:
    var count := 0
    for store in stores.slice(0, 10):
        if bool(store.get("active", false)) and int(store.get("flags", 0)) & 0x8000 == 0:
            count += 1
    if count % 5:
        return {"count": count, "flags": flags, "pending": pending, "notify": false}
    if count == 10 and signed8(mode) == 1:
        return {"count": count, "flags": flags | 2, "pending": 1, "notify": false}
    return {"count": count, "flags": flags, "pending": pending, "notify": true}

static func terminal_guard(cash: int, year: int, serial: int, mode: int, pending: int) -> Dictionary:
    var signed_cash := ((cash + 0x80000000) & 0xffffffff) - 0x80000000
    var signed_year := ((year + 0x80000000) & 0xffffffff) - 0x80000000
    var signed_serial := ((serial + 32768) & 65535) - 32768
    if signed_cash < 0 or signed_year >= 99 or signed_serial >= 99:
        return {"mode": 255, "pending": 4}
    return {"mode": mode & 255, "pending": pending & 0xffffffff}

static func menu_limit(flags: int) -> int:
    return 4 if signed8(flags) == 7 else 3

static func presentation_plan(pending: int) -> Dictionary:
    if pending < 0 or pending > 4:
        return {}
    return {"scene": [0, 1, 2, 2, 3][pending], "extra_flow": pending < 4}

static func owner_rating(stores: Array, visitors: int, population: int) -> Dictionary:
    if stores.is_empty():
        return {"parts": [0, 0, 0, 0, 0], "total": 0, "annual_sales": 0, "mean_rating": 0}
    var sales := 0
    var rating := 0
    for store in stores:
        var value := int(store["annual_sales"])
        var next := ((sales + value + 2147483648) & 4294967295) - 2147483648
        sales = 2147483647 if sales > 0 and value > 0 and next < 0 else next
        rating += int(store["rating"])
    var mean := rating / stores.size()
    var values := [visitors & 4294967295, sales, population, mean]
    var parts: Array = [2 * stores.size()]
    var total := 2 * stores.size()
    for i in 4:
        var points := 0
        for threshold in LIMITS[i]:
            points += 4 * int(values[i] >= threshold)
        parts.append(points)
        total += points
    return {"parts": parts, "total": 100 if total >= 96 else total, "annual_sales": sales, "mean_rating": mean}
