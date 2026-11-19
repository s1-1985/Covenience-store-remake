extends SceneTree
var game
var ui
func _initialize() -> void: call_deferred("run")
func tap(p: Vector2) -> void:
    ui._fallback_notice_queue.clear()
    for i in 12:
        if ui.notice.visible: ui._finish_notice()
        ui._pump_notices()
    for down in [true,false]:
        var e:=InputEventScreenTouch.new()
        e.position=Vector2(160,0)+p*3
        e.index=0
        e.pressed=down
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
    assert(s.try_buy_store_site(Vector2i(3,3),"small_top"))
    game._sync_site_selection()
    game.selecting_site=false
    game.site_panel.hide()
    game.store_type_panel.hide()
    if ui.notice.visible: ui._finish_notice()
    ui.open_window("sell_store")
    await process_frame
    await process_frame
    await tap(Vector2(276,78))
    assert(s.active_store==1)
    assert(s.try_set_business_hours("closed"))
    ui.surface.queue_redraw()
    await process_frame
    await process_frame
    await tap(Vector2(200,164))
    assert(ui.screen=="sell_store_confirm" and s.store_count()==2)
    await tap(Vector2(80,164))
    assert(ui.screen=="sell_store" and s.store_count()==2)
    await tap(Vector2(200,164))
    assert(ui.screen=="sell_store_confirm")
    s.try_set_business_hours("24h")
    await tap(Vector2(200,162))
    assert(s.store_count()==2 and ui.screen=="sell_store","Sale must revalidate open state after confirmation")
    s.try_set_business_hours("closed")
    ui.surface.queue_redraw()
    await process_frame
    await process_frame
    await tap(Vector2(200,164))
    await tap(Vector2(200,162))
    assert(s.store_count()==1 and game.town_view.visible and ui.screen.is_empty())
    assert(game.store_view.simulation==s and game.config==s.config)
    print("GRAPH_SALE_UI_PASS native selector, confirmation cancel, stale-open rejection, sale, refreshed town and bound remaining store")
    ui.hits.clear()
    ui._active_action=Callable()
    ui._pending_taps.clear()
    game.free()
    game=null
    ui=null
    await process_frame
    quit()
