extends SceneTree
var game
func _initialize() -> void:call_deferred("run")
func run() -> void:
    change_scene_to_file("res://scenes/main.tscn")
    await process_frame
    await process_frame
    game=current_scene
    game.paused=true;game.set_process(false)
    var ui=game.phone_ui
    var s=game.simulation
    s.economy.cash_yen=1000000000
    assert(s.try_buy_store_site(Vector2i(26,12)))
    assert(s.try_buy_store_site(Vector2i(3,3),"small_top"))
    s.select_store(1)
    s.notifications.reset()
    ui._fallback_notice_queue.clear()
    ui._heard_sequence=int(s.event_log.records[-1].sequence)
    s.minute_of_day=0;s._days_completed_this_month=4
    s.economy.cash_yen=1500000001;s._rival_cash_yen=1500000001
    s._apply_source_donations()
    assert(ui._notice_text("company_donation",{"amount_yen":500000001}).contains("500,000,001"))
    game._refresh_ui()
    assert(ui.notice.visible and ui._source_notice_visible)
    assert(s.notifications.current.context.event_type=="company_donation")
    assert(s.notifications.current.context.details.company_wide and s.notifications.current.sounds==[29])
    assert(ui._fallback_notice_queue.is_empty())
    # Store/reload while the single source notification is on screen.
    var saved:Dictionary=JSON.parse_string(JSON.stringify(s.save_state()))
    assert(s.load_state(saved))
    game._refresh_ui()
    assert(ui._source_notice_visible and s.notifications.current.context.event_type=="company_donation")
    s._apply_source_donations()
    assert(s.economy.expense_records.filter(func(row):return row.expense_type=="company_donation").size()==1)
    # Original mode1 notices close when source audio is idle.
    ui._finish_notice()
    ui._pump_notices()
    assert(not ui.notice.visible and ui._fallback_notice_queue.is_empty())
    assert(s.economy.cash_yen==1000000000 and s.rival_donation_records.size()==1)
    print("DONATIONS_UI_PASS amount text, company-wide source notice, sound29, no rival popup or duplicate, mid-message JSON and source audio-end closure")
    ui.hits.clear()
    ui._active_action=Callable()
    ui._pending_taps.clear()
    game.free();game=null
    await process_frame
    quit()
