extends SceneTree

func _initialize() -> void:
    call_deferred("_run")

func _run() -> void:
    change_scene_to_file("res://scenes/main_menu.tscn")
    await process_frame
    await process_frame
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
    phone._fallback_notice_queue.clear()
    phone._finish_notice()
    sim.notifications.reset()
    sim._record_event("manager_report", {"text": "先の通知"})
    sim._record_event("manager_report", {"text": "後の通知"})
    game._refresh_ui()
    assert(phone.notice.visible and "先の通知" in phone.notice_label.text)
    assert(sim.notifications.queue[2 * 160] == 1)
    # Save while the first notice is visible; preserve the active text and pending second.
    var data: Dictionary = JSON.parse_string(JSON.stringify(sim.save_state()))
    var before: Dictionary = JSON.parse_string(JSON.stringify(sim.notifications.snapshot()))
    assert(sim.load_state(data))
    var after: Dictionary = JSON.parse_string(JSON.stringify(sim.notifications.snapshot()))
    assert(after == before)
    phone._pump_notices()
    assert("先の通知" in phone.notice_label.text)
    var tap := InputEventMouseButton.new()
    tap.button_index = MOUSE_BUTTON_LEFT
    tap.pressed = true
    phone.notice.gui_input.emit(tap)
    phone._pump_notices()
    assert("後の通知" in phone.notice_label.text)
    phone._finish_notice()
    sim.notifications.reset()
    # Actual month-close caller, not a UI-only label injection.
    sim._settle_month_end()
    phone._pump_notices()
    assert("月次報告" in phone.notice_label.text)
    assert("他経費" in phone.notice_label.text)
    assert("町人口" in phone.notice_label.text)
    phone._finish_notice()
    sim.notifications.reset()
    sim._annual_sales_yen = 700000000
    sim.internal_rating_value = 90
    sim.month_count = 12
    sim._annual_review()
    phone._pump_notices()
    assert("年間オーナー評価" in phone.notice_label.text)
    assert("700,000,000" in phone.notice_label.text)
    assert(sim.notifications.word(0x800e3bb0) == 700000000)
    # Reject malformed queue before changing the live game; accept older JSON without it.
    var broken := data.duplicate(true)
    broken["source_notifications"]["queue"] = []
    var current_cash: int = sim.economy.cash_yen
    assert(not sim.load_state(broken))
    assert(sim.economy.cash_yen == current_cash)
    data.erase("source_notifications")
    assert(sim.load_state(data))
    assert(sim.notifications.word(0x801398b4) == 0)
    for slot in 50:
        assert(sim.notifications.queue[slot * 160] == 0)
    print("SOURCE_NOTIFICATIONS_UI_PASS ordered notices, active JSON resume, tap, monthly/annual reports, legacy JSON")
    quit()
