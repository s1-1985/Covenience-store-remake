class_name RuntimeEventLog
extends RefCounted

var records: Array[Dictionary] = []
var _next_sequence := 1


func reset() -> void:
    records.clear()
    _next_sequence = 1


func append(event_type: String, minute_of_day: int, details: Dictionary = {}) -> Dictionary:
    assert(not event_type.is_empty())
    assert(minute_of_day >= 0 and minute_of_day < 24 * 60)
    var record := {
        "sequence": _next_sequence,
        "event_type": event_type,
        "minute_of_day": minute_of_day,
        "details": details.duplicate(true),
    }
    _next_sequence += 1
    records.append(record)
    return record.duplicate(true)


func snapshot() -> Array:
    return records.duplicate(true)


func count_type(event_type: String) -> int:
    var total := 0
    for record in records:
        if record["event_type"] == event_type:
            total += 1
    return total
