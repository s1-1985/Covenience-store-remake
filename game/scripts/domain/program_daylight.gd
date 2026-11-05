class_name ProgramDaylight
extends RefCounted
# CONFIRMED_BINARY: town_daylight.py / 80066234, unsigned minute clock.
static func rgb(clock: int) -> Array[int]:
    clock &= 0xffffffff
    var hour := (clock / 60) % 24
    var minute := clock % 60
    var values: Array[int]
    if hour in [4, 5]:
        var gray := 68 + 30 * (hour - 4) + minute / 2
        values = [gray, gray, gray]
    elif hour == 17:
        values = [minute - 128, -128 - minute / 2, -128 - minute / 2]
    elif hour == 18:
        values = [-68 - 2 * minute, 98 - minute / 2, 98 - minute / 2]
    else:
        var gray := 128 if hour >= 6 and hour <= 16 else 68
        values = [gray, gray, gray]
    return [values[0] & 255, values[1] & 255, values[2] & 255]

static func color(clock: int) -> Color:
    var bytes := rgb(clock)
    return Color(float(bytes[0]) / 128.0, float(bytes[1]) / 128.0, float(bytes[2]) / 128.0)
