extends SceneTree

const Sim = preload("res://scripts/vertical_slice_simulation.gd")
const Start = preload("res://scripts/domain/guide_starting_store.gd")
var game
var sound

func setup():
    var base: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://data/vertical_slice.json"))
    return Sim.new(Start.apply(base))

func hear() -> Array:
    sound.source_history.clear()
    game._play_event_sounds()
    return sound.source_history.duplicate()

func _initialize() -> void:
    call_deferred("run")

func run() -> void:
    change_scene_to_file("res://scenes/main.tscn")
    await process_frame
    await process_frame
    game = current_scene
    game.paused = true
    game.set_process(false)
    var s = game.simulation
    s.economy.cash_yen = 1000000000
    assert(s.try_buy_store_site(Vector2i(26, 12)))
    game._sync_site_selection()
    game.selecting_site = false
    sound = root.get_node("SoundManager")
    var original_bits: int = sound.source_settings_bits
    var original_enabled: bool = sound.enabled
    sound.enabled = true
    sound.set_source_settings(0)
    hear()
    var seed_before: int = s._program_rng.seed
    var clock_before: int = s.minute_of_day
    sound.set_source_settings(1)
    for event in ["staff_exhausted", "self_service_sale", "self_service_sale", "checkout_completed"]:
        s._record_event(event)
    for redraw in 3:
        assert(hear().is_empty(), "SE OFF must not dispatch or clear pending flags")
        assert(s.source_audio_flags == 0x1600)
    assert(s._program_rng.seed == seed_before and s.minute_of_day == clock_before)
    # The flags survive JSON even though the UI has already consumed the log.
    var saved: Dictionary = JSON.parse_string(JSON.stringify(s.save_state()))
    var copy = setup()
    assert(copy.load_state(saved))
    assert(copy.source_audio_flags == 0x1600)
    game.simulation = copy
    assert(hear().is_empty())
    sound.set_source_settings(0)
    assert(hear() == [10, 9, 25], "Pending source bits dispatch once in ascending bit order")
    assert(hear().is_empty() and copy.source_audio_flags == 0)
    game.simulation = s
    assert(hear() == [10, 9, 25])

    # Background stores have their own pending bits, not an audible global queue.
    assert(s.try_buy_store_site(Vector2i(3, 3), "small_top"))
    assert(s.store_count() == 2)
    hear()
    s._switch_store(1)
    s.source_audio_flags = 0
    s._record_event("source_restock_completed")
    s._record_event("source_cleaning_completed")
    assert(s.take_source_audio_requests(1, sound.source_catalog.event_tones).is_empty())
    assert(s.source_audio_flags == 0x0800)
    s._switch_store(0)
    s._record_event("self_service_sale")
    assert(hear() == [9])
    assert(s.store_field(1, "source_audio_flags") == 0x0800)
    saved = JSON.parse_string(JSON.stringify(s.save_state()))
    var branch_copy = setup()
    assert(branch_copy.load_state(saved))
    assert(branch_copy.store_field(1, "source_audio_flags") == 0x0800)
    assert(branch_copy.select_store(1))
    game.simulation = branch_copy
    assert(hear() == [24], "Selecting a store releases its retained, coalesced bit")
    assert(hear().is_empty())
    assert(branch_copy.select_store(0))
    assert(hear().is_empty())

    # Old client saves lack this field. Do not replay their event history.
    saved.source_runtime.erase("audio_flags")
    for block in saved.branches:
        block.source_runtime.erase("audio_flags")
    assert(branch_copy.load_state(saved))
    for i in branch_copy.store_count():
        assert(branch_copy.store_field(i, "source_audio_flags") == 0)
    branch_copy._record_event("self_service_sale")
    branch_copy.reset()
    assert(branch_copy.source_audio_flags == 0)
    sound.set_source_settings(original_bits)
    sound.enabled = original_enabled
    game.simulation = s
    game.free()
    await process_frame
    print("PENDING_AUDIO_PASS SE-off carryover, duplicate coalescing, ascending order, per-store guard/switch/JSON, old saves, reset, no RNG/clock change")
    quit()
