class_name ProgramRivals
extends RefCounted

# CONFIRMED_BINARY 8002A8E0. Economics are supplied by the game's real store
# simulation; no geometric "pressure score" is treated as a monthly loss.
static func review(rivals: Array, own_count: int, month: int) -> Dictionary:
    for rival in rivals:
        var profit := int(rival.get("monthly_profit_yen", 0))
        var streak := (int(rival.get("deficit_months", 0)) + 1) & 65535 if profit < 0 else 0
        rival["deficit_months"] = streak
        var serial := int(rival.get("serial", 1))
        var force_close := serial == 1 and own_count == 9 and month == 1
        var signed_streak := ((streak + 32768) & 65535) - 32768
        if not force_close and (signed_streak < 6 or (serial == 1 and rivals.size() >= 2)):
            continue
        return {"closed": str(rival["id"])}
    return {"closed": ""}


static func find_site(town, permits: Array, rng) -> Vector2i:
    var mask := 8 | (4 if permits.has("tobacco") else 0) | (2 if permits.has("alcohol") else 0) | (1 if permits.has("medicine") else 0)
    var xs: int = rng.randi() % 59
    var ys: int = rng.randi() % 49
    for dy in 49:
        var y := (ys + dy) % 49
        for dx in 59:
            var x := (xs + dx) % 59
            if town.level(x, y) < 8:
                continue
            var ok := true
            for point in [Vector2i(x, y), Vector2i(x + 1, y), Vector2i(x, y + 1), Vector2i(x + 1, y + 1)]:
                if int(town.cells[point.y * 60 + point.x][4]) & mask:
                    ok = false
            if ok:
                return Vector2i(x, y)
    return Vector2i(-1, -1)
