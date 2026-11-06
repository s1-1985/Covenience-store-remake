extends SceneTree
const Notices := preload("res://scripts/domain/program_notifications.gd")
const Starting := preload("res://scripts/domain/guide_starting_store.gd")
const Sim := preload("res://scripts/vertical_slice_simulation.gd")

func digest(bytes: PackedByteArray) -> String:
    var h := HashingContext.new()
    h.start(HashingContext.HASH_SHA256)
    h.update(bytes)
    return h.finish().hex_encode()

func _initialize() -> void:
    var fixtures: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://tests/fixtures/source_notifications.json"))
    for fixture in fixtures["cases"]:
        var n := Notices.new()
        var index := int(fixture["case"])
        for i in 8000:
            n.queue[i] = (i * 7 + index) & 255
        for slot in 50:
            n.queue[slot * 160] = int(fixture["occupied"].has(float(slot)))
        var body := PackedByteArray()
        for i in 120:
            body.append((i + index * 3) & 255)
        var a: Array = fixture["args"]
        assert(n.reserve(a[0], a[1], a[2], a[3], a[4], body) == int(fixture["slot"]))
        assert(digest(n.queue) == fixture["reserve_sha256"], str(index))
        for slot in fixture["occupied"]:
            n.queue[int(slot) * 160] = 0
        n.state.clear()
        for key in fixture["initial_state"]:
            n.put(int(str(key)), int(fixture["initial_state"][key]))
        n.text.fill(17)
        var result := n.consume(int(fixture["clock"]), fixture["stores"], 20000)
        assert((result.is_empty() and fixture["consumed"] == null) or (not result.is_empty() and result["slot"] == int(fixture["consumed"])), str(index))
        for key in fixture["state"]:
            assert(n.word(int(str(key))) == int(fixture["state"][key]), "%s:%s" % [index, key])
        assert(digest(n.queue) == fixture["queue_sha256"])
        assert(n.text == PackedByteArray(fixture["text"]))
        if not result.is_empty():
            assert(result["sounds"] == fixture["sounds"].map(func(v): return int(v)))
        var clone := Notices.new()
        assert(clone.restore(JSON.parse_string(JSON.stringify(n.snapshot()))))
        assert(clone.queue == n.queue and clone.text == n.text and clone.state == n.state)
    for fixture in fixtures["display_cases"]:
        var n := Notices.new()
        var a: Array = fixture["args"].map(func(v): return int(v))
        for pair in [[0x801398b4, a[0]], [0x801398b8, a[1]], [0x800e3be4, a[4]], [0x800e3bd8, a[7]], [0x800e3bda, a[8]]]:
            n.put(pair[0], pair[1])
        n.queue[2] = a[5] & 255
        var plan := n.display_plan(a[2], a[3], a[6])
        assert(plan["outcome"] == fixture["outcome"])
        assert(n.word(0x801398b4) == int(fixture["active"]))
        assert(n.word(0x801398b8) == int(fixture["timer"]))
        assert(JSON.parse_string(JSON.stringify(plan["calls"])) == fixture["calls"])
    var queue := Notices.new()
    var body := PackedByteArray()
    body.resize(120)
    assert(queue.reserve(7, 0, 100, 1, 0, body) == 1)
    assert(queue.reserve(3, 0, 34, 1, 0, body) == 2)
    assert(queue.consume(0)["slot"] == 1)
    assert(queue.consume(0).is_empty())
    assert(queue.display(0, 1) == "draw")
    assert(queue.word(0x801398b8) == 0)
    queue.frame()
    assert(queue.word(0x801398b4) == 1)
    assert(queue.display(0, 0) == "close")
    assert(queue.consume(0)["slot"] == 2)
    assert(queue.word(0x801398b8) == 60)
    queue.reset()
    for slot in 50:
        assert(queue.queue[slot * 160] == 0)
    assert("REMAKE_BALANCED_DEFAULT" in FileAccess.get_file_as_string("res://scripts/phone_ui.gd"))
    var config: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://data/vertical_slice.json"))
    assert("REMAKE_BALANCED_DEFAULT" in config["source_notification_presentation"]["evidence_note"])
    print("SOURCE_NOTIFICATIONS_PASS 96 byte/state + 640 display cases, audio closure, blocked dequeue and JSON")
    quit()
