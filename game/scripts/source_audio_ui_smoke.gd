extends SceneTree

func _initialize() -> void:
    call_deferred("_run")

func _run() -> void:
    var sound = root.get_node("SoundManager")
    var original_bits: int = sound.source_settings_bits
    var original_enabled: bool = sound.enabled
    sound.enabled = true
    sound.set_source_settings(0)
    change_scene_to_file("res://scenes/main_menu.tscn")
    await process_frame
    await process_frame
    assert(sound.source_bgm_id == 0)
    current_scene.new_game_button.pressed.emit()
    await process_frame
    await process_frame
    var game = current_scene
    game.paused = true
    game._on_site_tapped(Vector2i(26, 12))
    game.site_buy_button.pressed.emit()
    game.find_child("BuildStoreButton", true, false).pressed.emit()
    var sim = game.simulation
    var phone = game.phone_ui
    phone.open_window("system")
    assert(sound.source_bgm_id == 2)
    game.find_child("SourceSESetting", true, false).pressed.emit()
    await process_frame
    assert(int(sound.source_settings()["se_enabled"]) == 0)
    assert(sim.config["source_settings_bits"] == 1)
    for index in [3, 4, 2]:
        game.find_child("SourceBGMSetting", true, false).pressed.emit()
        await process_frame
        assert(sound.source_bgm_id == index)
    game.find_child("SourceMonthlySetting", true, false).pressed.emit()
    await process_frame
    assert(sim.config["source_settings_bits"] == 3)
    phone._finish_notice()
    phone._fallback_notice_queue.clear()
    sim.notifications.reset()
    var ledger: int = sim.economy.month_end_records.size()
    sim._settle_month_end()
    assert(sim.economy.month_end_records.size() == ledger + 1)
    for slot in 50:
        if sim.notifications.queue[slot * 160] != 0:
            assert(sim.notifications.queue[slot * 160 + 2] != 2) # keep other events; suppress only monthly report.
    var saved: Dictionary = JSON.parse_string(JSON.stringify(sim.save_state()))
    sound.set_source_settings(0)
    assert(sim.load_state(saved))
    assert(sim.config["source_settings_bits"] == 3)
    var bad := saved.duplicate(true)
    bad["source_settings_bits"] = 768
    assert(not sim.load_state(bad))
    sound.set_source_settings(0)
    sim.notifications.reset()
    sim._record_event("manager_report", {"text": "音声終了確認"})
    phone._pump_notices()
    assert(phone.notice.visible and sound.source_voice_active())
    assert(sound.source_history[-1] == 34)
    for i in 500:
        sim.notifications.display(0, 1)
    phone._process(0.01)
    assert(phone.notice.visible) # reaching zero source timer is not audio completion.
    sound._process(30.0)
    phone._process(0.01)
    assert(not phone._source_notice_visible)
    sim._set_source_ending(1)
    game._refresh_ui()
    assert(sound.source_history[-1] == 60)
    game.ending_view.advance_frames(389)
    assert(game.ending_view.next_button.disabled)
    sound._process(30.0)
    game.ending_view.advance_frames(0)
    assert(not game.ending_view.next_button.disabled)
    game.ending_view.advance()
    assert(game.ending_view.stage == "credits" and sound.source_bgm_id == 6)
    game.ending_view.advance_frames(7120)
    game.ending_view.advance()
    assert(game.ending_view.stage == "save" and sound.source_bgm_id == -1)
    assert(sound.play_source(28) and sound.source_voice_active())
    change_scene_to_file("res://scenes/main_menu.tscn")
    await process_frame
    await process_frame
    assert(not sound.source_voice_active() and sound.source_bgm_id == 0)
    sound.set_source_settings(original_bits)
    sound.enabled = original_enabled
    print("SOURCE_AUDIO_UI_PASS original settings controls, monthly gating without lost ledger, JSON settings, notice voice-finished boundary, ending voice and credit BGM")
    quit()
