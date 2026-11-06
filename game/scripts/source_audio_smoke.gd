extends SceneTree
const Policy := preload("res://scripts/domain/program_audio.gd")

func _initialize() -> void:
    call_deferred("_run")

func _run() -> void:
    var fixture: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://tests/fixtures/source_audio.json"))
    var catalog: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://data/source_audio.json"))
    for row in fixture["settings"]:
        var settings := Policy.settings(int(row["bits"]))
        for key in row["expected"]:
            assert(settings[key] == int(row["expected"][key]))
    for row in fixture["dispatch"]:
        var request := Policy.dispatch(int(row["identifier"]), int(row["guard"]), int(row["enabled"]))
        assert(request["kind"] == row["expected"]["kind"])
        if row["expected"].has("index"):
            assert(request["index"] == int(row["expected"]["index"]))
    for row in fixture["main"]:
        var result := Policy.main_requests(int(row["flags"]), int(row["enabled"]), int(row["selected"]) == 1, int(row["month"]), int(row["extra"]), catalog["event_tones"])
        assert(result["requests"] == row["requested_ids"].map(func(value): return int(value)))
        assert(result["flags"] == (0 if int(row["enabled"]) != 0 and int(row["selected"]) == 1 else int(row["flags"])))
    for pair in [["xa", 130], ["bgm", 7], ["se", 16], ["vos", 12]]:
        assert(catalog[pair[0]].size() == pair[1])
        for entry in catalog[pair[0]]:
            var stream := load("res://assets/audio/source/" + str(entry["file"])) as AudioStream
            assert(stream != null and absf(stream.get_length() - float(entry["duration"])) < 0.01)
    assert("REMAKE_BALANCED_DEFAULT" in catalog["sequence_evidence_note"])
    var sound = root.get_node("SoundManager")
    var original_bits: int = sound.source_settings_bits
    var original_enabled: bool = sound.enabled
    sound.enabled = true
    sound.set_source_settings(0)
    sound.stop_music()
    assert(sound.play_source(28) and sound.source_voice_active())
    sound._process(3.1)
    assert(sound.source_voice_active())
    sound._process(0.2)
    assert(not sound.source_voice_active())
    sound.set_source_settings(1)
    assert(not sound.play_source(0))
    assert(not sound.play_source(16))
    assert(sound.play_source(28)) # SE OFF does not mute XA in original dispatcher.
    assert(not sound.play_source(158)) # excluded raw row130, no invented sound.
    assert(sound.play_source(-1) and not sound.source_voice_active())
    sound.set_source_settings(0)
    assert(sound.play_source(0))
    assert(sound.play_source(16))
    assert(sound.play_source_bgm(6))
    assert(not sound.play_source(28)) # original credit/BGM6 guard.
    sound.stop_music()
    sound.set_source_settings(original_bits)
    sound.set_enabled(false)
    for player in sound._source_tracks:
        player.stream = null
    await process_frame
    await process_frame
    sound.set_enabled(original_enabled)
    print("SOURCE_AUDIO_PASS independent dispatch/settings/main flag cases; 165 source resources; voice-finished clock; SE OFF/XA separation and BGM6 guard")
    quit()
