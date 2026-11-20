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
    var initial:Dictionary=s.source_price_settings()
    var id:String=initial.keys()[0]
    ui.open_window("prices")
    await process_frame
    await process_frame
    await tap(Vector2(200,115))
    assert(int(ui._price_draft[id])==int(initial[id])+1 and s.source_price_settings()==initial)
    ui.close_window()
    ui.open_window("prices")
    await process_frame
    await process_frame
    await tap(Vector2(160,147))
    assert(ui.screen=="stock_prices")
    await tap(Vector2(289,76))
    assert(int(ui._price_draft[id])==int(initial[id])+1)
    await tap(Vector2(40,205))
    assert(ui.screen=="prices" and ui._price_draft==initial)
    await tap(Vector2(160,147))
    await tap(Vector2(289,76))
    await tap(Vector2(260,205))
    assert(ui.screen=="prices" and int(ui._price_draft[id])==int(initial[id])+1)
    await tap(Vector2(200,187))
    assert(ui.screen=="price_confirm" and s.source_price_settings()==initial)
    await tap(Vector2(80,178))
    await tap(Vector2(200,187))
    await tap(Vector2(210,178))
    assert(ui.screen.is_empty() and s.source_price_setting(id)==int(initial[id])+1)
    ui.open_window("prices")
    ui._price_draft[id]=100
    await process_frame
    await process_frame
    var bounded:Dictionary=ui._price_draft.duplicate()
    await tap(Vector2(200,115))
    assert(ui._price_draft==bounded,"Group at upper bound must not partly move other categories")
    ui.close_window()
    ui.open_window("prices")
    ui.open_window("stock_prices")
    ui._price_draft[id]=100
    await process_frame
    await process_frame
    await tap(Vector2(289,76))
    assert(int(ui._price_draft[id])==100)
    ui._price_draft[id]=0
    await process_frame
    await process_frame
    await tap(Vector2(250,76))
    assert(int(ui._price_draft[id])==0)
    ui.close_window()
    ui.open_window("prices")
    await process_frame
    await process_frame
    await tap(Vector2(200,115))
    await tap(Vector2(200,187))
    assert(s.try_set_product_price(id,s.source_price_setting(id)+1))
    var actual:Dictionary=s.source_price_settings()
    await tap(Vector2(210,178))
    assert(ui.screen=="price_confirm" and s.source_price_settings()==actual)
    ui.close_window()
    assert(s.try_buy_store_site(Vector2i(3,3),"small_top"))
    ui.open_window("prices")
    await process_frame
    await process_frame
    await tap(Vector2(200,115))
    await tap(Vector2(200,187))
    assert(s.select_store(1))
    var branch:Dictionary=s.source_price_settings()
    await tap(Vector2(210,178))
    assert(s.source_price_settings()==branch and ui.screen=="price_confirm")
    print("PRICING_UI_PASS native plus/minus, draft-only edits, individual cancel/keep, final confirm, group bound and stale value/store rejection")
    ui.hits.clear()
    ui._active_action=Callable()
    ui._pending_taps.clear()
    game.free()
    game=null
    ui=null
    await process_frame
    quit()
