class_name ProgramNotifications
extends RefCounted

# CONFIRMED_BINARY: event_queue.py / notification_display.py, analysis 2c00ba53.
# 8003ECD8 reservation, 8003EF44 consumer, 8005C79C reset, 8003FF00 display.
# Keep unknown bytes and the stale active text: kind 7/8 do not copy text.
const SLOTS := 50
const STRIDE := 160
const Progression := preload("res://scripts/domain/program_progression.gd")
var queue := PackedByteArray()
var state := {}
var text := PackedByteArray()
var contexts := {}
var current := {}

func _init() -> void:
    queue.resize(SLOTS * STRIDE)
    text.resize(120)
    reset()

static func signed8(value: int) -> int:
    value &= 255
    return value - 256 if value >= 128 else value

static func signed32(value: int) -> int:
    value &= 0xffffffff
    return value - 0x100000000 if value >= 0x80000000 else value

func word(address: int) -> int:
    return int(state.get(address, 0))

func put(address: int, value: int) -> void:
    state[address] = value & 0xffffffff

func reset() -> void:
    for slot in SLOTS:
        queue[slot * STRIDE] = 0
    for address in [0x80137968, 0x8013796c, 0x801398b0, 0x801398b4, 0x801398b8]:
        put(address, 0)
    contexts.clear()
    current.clear()

func reserve(kind: int, parameter: int, sound: int, mode: int, variant: int, body: PackedByteArray, context: Dictionary = {}) -> int:
    assert(body.size() == 120)
    for slot in range(0 if signed8(mode) == 5 else 1, SLOTS):
        var offset := slot * STRIDE
        if queue[offset] != 0:
            continue
        queue[offset] = 1
        queue[offset + 1] = variant & 255
        queue[offset + 2] = mode & 255
        for i in 120:
            queue[offset + 4 + i] = body[i]
        queue.encode_u32(offset + 132, kind & 0xffffffff)
        queue.encode_u32(offset + 136, parameter & 0xffffffff)
        queue.encode_u32(offset + 140, sound & 0xffffffff)
        contexts[str(slot)] = context.duplicate(true)
        return slot
    return -1

static func sound_request(sound: int) -> Array:
    if sound == -1:
        return []
    var translated := {100: 28, 101: 29, 119: 8, 110: 7}
    return [translated[sound]] if translated.has(sound) else ([sound] if sound < 100 else [])

func consume(clock: int, stores: Array = [], population: int = 0) -> Dictionary:
    if word(0x801398b4) != 0:
        return {}
    put(0x801398b0, 0)
    for slot in SLOTS:
        var offset := slot * STRIDE
        if queue[offset] == 0:
            continue
        put(0x801398b0, slot)
        var kind := signed32(queue.decode_u32(offset + 132))
        var parameter := signed32(queue.decode_u32(offset + 136))
        var sound := signed32(queue.decode_u32(offset + 140))
        var mode := signed8(queue[offset + 2])
        put(0x800e3be4, kind)
        put(0x800e3be8, parameter)
        if kind < 7:
            text = queue.slice(offset + 4, offset + 124)
        put(0x800cd7ec, 2 if kind == 3 else (1 if kind in [1, 2, 4, 5, 6, 7, 8] else 0))
        if mode == 1:
            for pair in [[0x800e3bd8, 56], [0x800e3bda, 104], [0x800e3bdc, 17], [0x800e3bde, 6], [0x800e3be0, 0]]:
                put(pair[0], pair[1])
            put(0x801398b8, {4: 280, 5: 390, 6: 360, 7: 1, 8: 1}.get(kind, 60))
            put(0x801398b4, 1)
        elif mode == 2:
            var early := clock / 69120 + 1 < 2 and (clock / 5760) % 12 + 1 < 3
            var values := [word(0x800e3c28), 0 if early else (word(0x800e3c28) - word(0x800e3c2c)) & 0xffffffff,
                word(0x800da974), 0 if early else (word(0x800da974) - word(0x800da978)) & 0xffffffff,
                word(0x800e36a8), (word(0x800e36a8) - word(0x800e36ac)) & 0xffffffff]
            for i in 6:
                put(0x800e3620 + i * 4, 0 if i < 5 and values[i] == 0x80000000 else values[i])
            put(0x801398b8, 240)
            put(0x801398b4, 1)
        elif mode == 3:
            var result := Progression.owner_rating(stores, word(0x800cd930), population)
            var values := [stores.size(), word(0x800cd930), result["annual_sales"], population, result["mean_rating"]]
            for i in 5:
                put(0x800e3ba8 + i * 4, values[i])
                put(0x800e3bc0 + i * 4, result["parts"][i])
            put(0x800cd80c, result["total"])
            var scenario := signed8(word(0x800cd948))
            if result["total"] == 100 and scenario in [2, 3]:
                put(0x800cd8a0, word(0x800cd8a0) | (4 if scenario == 2 else 8))
                put(0x800cd9b4, scenario)
            put(0x801398b8, 240)
            put(0x801398b4, 1)
        current = {"slot": slot, "kind": kind, "parameter": parameter, "mode": mode,
            "variant": signed8(queue[offset + 1]), "sounds": sound_request(sound),
            "context": contexts.get(str(slot), {}).duplicate(true)}
        contexts.erase(str(slot))
        queue[offset] = 0
        return current
    put(0x801398b0, 50)
    return {}

func display(audio_disabled: int, audio_status: int) -> String:
    return display_plan(audio_disabled, audio_status)["outcome"]

func display_plan(audio_disabled: int, audio_status: int, view: int = 0) -> Dictionary:
    if word(0x801398b4) != 1:
        return {"outcome": "inactive", "calls": []}
    if audio_disabled != 0 or audio_status == 0:
        put(0x801398b4, 0)
        return {"outcome": "close", "calls": [[0x80064e4c, [-1]]]}
    var calls: Array = []
    if view == 1:
        calls.append([0x80062a4c, [0, 0]])
        calls.append([0x80065974, []])
    calls.append([0x80018940, [6, 1]])
    var kind := signed32(word(0x800e3be4))
    if kind in [7, 8]:
        put(0x801398b8, 0)
    var slot := word(0x801398b0)
    var mode := signed8(queue[slot * STRIDE + 2]) if slot < SLOTS else 0
    match mode:
        1:
            var dx := 32 if kind == 0 else 72 if kind == 3 else 56
            calls.append([0x80067338, [_signed16(word(0x800e3bd8) + dx), _signed16(word(0x800e3bda) + 16), 0x800e3aa0]])
        2:
            calls.append([0x8006c048, [0, 64]])
        3:
            calls.append([0x8006c8b0, [16, 48]])
    return {"outcome": "draw", "calls": calls}

static func _signed16(value: int) -> int:
    value &= 65535
    return value - 65536 if value >= 32768 else value

func frame() -> void:
    if signed32(word(0x801398b8)) > 0:
        put(0x801398b8, word(0x801398b8) - 1)
    # A zero timer does not close the display; the audio status does.

func snapshot() -> Dictionary:
    return {"queue": Array(queue), "state": state.duplicate(), "text": Array(text),
        "contexts": contexts.duplicate(true), "current": current.duplicate(true)}

func restore(data: Dictionary) -> bool:
    if data.is_empty():
        reset()
        return true
    if not data.get("queue") is Array or data["queue"].size() != SLOTS * STRIDE or not data.get("text") is Array or data["text"].size() != 120:
        return false
    if not data.get("state") is Dictionary or not data.get("contexts") is Dictionary or not data.get("current") is Dictionary:
        return false
    for bytes in [data["queue"], data["text"]]:
        for value in bytes:
            if (not value is int and not value is float) or float(value) != floorf(float(value)) or value < 0 or value > 255:
                return false
    for key in data["state"]:
        if not str(key).is_valid_int() or (not data["state"][key] is int and not data["state"][key] is float):
            return false
    for key in data["contexts"]:
        if not str(key).is_valid_int() or int(str(key)) < 0 or int(str(key)) >= SLOTS or not data["contexts"][key] is Dictionary:
            return false
    var saved_current: Dictionary = data["current"]
    if not saved_current.is_empty():
        for key in ["slot", "kind", "mode", "parameter", "variant"]:
            if not saved_current.has(key) or (not saved_current[key] is int and not saved_current[key] is float):
                return false
        if not saved_current.get("context") is Dictionary or not saved_current.get("sounds") is Array:
            return false
    queue = PackedByteArray(data["queue"])
    text = PackedByteArray(data["text"])
    state.clear()
    for key in data["state"]:
        put(int(str(key)), int(data["state"][key]))
    contexts = data["contexts"].duplicate(true)
    current = data["current"].duplicate(true)
    return true
