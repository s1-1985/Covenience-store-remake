extends SceneTree
var game
var ui
func _initialize() -> void:call_deferred("run")
func tap(p:Vector2) -> void:
    ui._fallback_notice_queue.clear()
    for i in 12:
        if ui.notice.visible:ui._finish_notice()
        ui._pump_notices()
    for down in [true,false]:
        var e:=InputEventScreenTouch.new()
        e.position=Vector2(160,0)+p*3
        e.pressed=down
        e.index=0
        root.push_input(e,true)
        await process_frame
func run() -> void:
    change_scene_to_file("res://scenes/main.tscn")
    await process_frame
    await process_frame
    game=current_scene
    game.paused=true
    game.set_process(false)
    ui=game.phone_ui
    var s=game.simulation
    s.economy.cash_yen=1000000000
    assert(s.try_buy_store_site(Vector2i(26,12)))
    game._sync_site_selection()
    game.selecting_site=false
    game.site_panel.hide()
    game.store_type_panel.hide()
    if ui.notice.visible:ui._finish_notice()
    var cash:int=s.economy.cash_yen
    ui.open_window("advertising")
    await process_frame
    await process_frame
    await tap(Vector2(68,110))
    assert(ui._ad_draft.has("direct_mail") and s.source_promotions.is_empty() and s.economy.cash_yen==cash)
    ui.close_window()
    ui.open_window("advertising")
    await process_frame
    await process_frame
    assert(ui._ad_draft.is_empty())
    await tap(Vector2(68,110))
    await tap(Vector2(68,110))
    assert(ui._ad_draft.is_empty())
    await tap(Vector2(68,110))
    await tap(Vector2(244,110))
    await tap(Vector2(210,191))
    assert(ui.screen.is_empty() and s.source_promotions.size()==2 and s.economy.cash_yen==cash)
    assert(s.try_buy_store_site(Vector2i(3,3),"small_top") and s.select_store(1))
    ui.open_window("advertising")
    await process_frame
    await process_frame
    assert(ui._ad_draft.size()==2)
    await tap(Vector2(68,110))
    await tap(Vector2(244,110))
    await tap(Vector2(210,191))
    assert(s.source_promotions.is_empty())
    ui.open_window("advertising")
    await process_frame
    await process_frame
    await tap(Vector2(68,110))
    assert(s.try_commit_source_promotions(["radio"]))
    await tap(Vector2(210,191))
    assert(ui.screen=="advertising" and s.source_promotions.has("radio") and not s.source_promotions.has("direct_mail"))
    ui.close_window()
    s.economy.cash_yen=0
    s.minute_of_day=23*60
    s._days_completed_this_month=3
    ui.open_window("advertising")
    await process_frame
    await process_frame
    await tap(Vector2(68,110))
    await tap(Vector2(210,191))
    assert(s.source_promotions.has("direct_mail"),"Past time and low cash must not prevent selection")
    if ui.notice.visible:ui._finish_notice()
    ui._fallback_notice_queue.clear()
    ui._source_notice_visible=false
    s.notifications.reset()
    ui._heard_sequence=int(s.event_log.records[-1].sequence)
    s._days_completed_this_month=1
    s.minute_of_day=600
    s._fire_source_promotions()
    game._refresh_ui()
    assert(not s.source_promotions.has("direct_mail"))
    assert(ui._source_notice_visible and s.notifications.current.kind==4)
    assert(s.notifications.current.context.event_type=="promotion_cancelled")
    assert(ui._fallback_notice_queue.is_empty(),"Source notification must not duplicate the fallback notice")
    ui._finish_notice()
    s.notifications.reset()
    ui._fallback_notice_queue.clear()
    ui._source_notice_visible=false
    s.source_rival_promotions=["tv"]
    s._days_completed_this_month=0
    s.minute_of_day=19*60
    s._rival_cash_yen=0
    s._fire_source_promotions()
    game._refresh_ui()
    assert(ui._source_notice_visible and s.notifications.current.kind==4)
    assert(s.notifications.current.sounds==[29])
    var shown:String=ui._notice_text("promotion_fired",s.notifications.current.context.details)
    assert("ライバル" in shown and game.tr("tv") in shown)
    assert(ui._fallback_notice_queue.is_empty())
    ui._finish_notice()
    print("ADVERTISING_UI_PASS native multi-select toggle/cancel/commit, no advance debit, company sharing, stale rejection, past-time low-cash setup and single source cancellation notice")
    ui.hits.clear()
    ui._active_action=Callable()
    ui._pending_taps.clear()
    game.free()
    game=null
    ui=null
    await process_frame
    quit()
