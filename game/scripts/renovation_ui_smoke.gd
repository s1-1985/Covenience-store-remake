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
    assert(s.try_buy_store_site(Vector2i(3,3),"small_top"))
    game._sync_site_selection()
    game.selecting_site=false
    game.site_panel.hide()
    game.store_type_panel.hide()
    if ui.notice.visible:ui._finish_notice()
    s.select_store(0)
    s.try_set_business_hours("24h")
    ui._navigate("renovation")
    await process_frame
    await process_frame
    assert(ui.screen=="close_shop")
    await tap(Vector2(130,147))
    assert(ui.screen=="renovation" and not s.is_open_now())
    var cash:int=s.economy.cash_yen
    var old:String=s.store_type_id
    await tap(Vector2(160,107))
    assert(ui.screen=="renovation_confirm" and s.economy.cash_yen==cash and s.store_type_id==old)
    await tap(Vector2(80,178))
    assert(ui.screen=="renovation" and s.economy.cash_yen==cash)
    await tap(Vector2(160,107))
    s.economy.cash_yen=11999999
    await tap(Vector2(210,178))
    assert(s.store_type_id==old and s.economy.cash_yen==11999999)
    s.economy.cash_yen=12000000
    await tap(Vector2(210,178))
    assert(ui.screen=="interior" and not s.renovation_session.is_empty() and s.economy.cash_yen==0 and not s.is_open_now())
    ui.close_window()
    await process_frame
    await process_frame
    assert(ui.screen=="renovation_finish")
    await tap(Vector2(170,120))
    assert(ui.screen=="interior")
    ui.close_window()
    await process_frame
    await process_frame
    await tap(Vector2(170,150))
    assert(ui.screen.is_empty() and s.renovation_session.is_empty() and s.economy.cash_yen==0 and s.is_open_now())
    assert(s.store_type_id==str(s.store_types()[2].id))
    assert(game.store_view.simulation==s and game.config==s.config)
    s.economy.cash_yen=1000000000
    ui._navigate("renovation")
    await process_frame
    await process_frame
    await tap(Vector2(130,147))
    await tap(Vector2(160,107))
    await tap(Vector2(170,150))
    assert(ui.screen=="renovation_permits")
    await tap(Vector2(200,88))
    await tap(Vector2(170,188))
    assert(ui.screen=="renovation_confirm" and ui._renovation_permits.size()==1)
    await tap(Vector2(210,178))
    assert(not s.renovation_session.is_empty() and s.has_permit("tobacco"))
    assert(s.try_set_source_floor(5))
    var saved:Dictionary=JSON.parse_string(JSON.stringify(s.save_state()))
    var restored=load("res://scripts/vertical_slice_simulation.gd").new(s.config)
    assert(restored.load_state(saved))
    game.simulation=restored
    s=restored
    game._store_layout_changed()
    ui.close_hours=""
    ui._resume_renovation_edit()
    assert(ui.screen=="interior" and not ui.close_hours.is_empty())
    ui.close_window()
    await process_frame
    await process_frame
    await tap(Vector2(170,180))
    assert(ui.screen=="renovation" and s.renovation_session.is_empty() and s.economy.cash_yen==1000000000)
    assert(s.store_type_id==str(s.store_types()[2].id) and not s.has_permit("tobacco"))
    ui.close_window()
    assert(s.is_open_now())
    # Closing a temporary-closure flow after changing selected store must
    # restore the hours of the original store, not overwrite the other one.
    s.economy.cash_yen=1000000000
    ui._navigate("renovation")
    await process_frame
    await process_frame
    await tap(Vector2(130,147))
    assert(not s.is_open_now())
    s.select_store(1)
    s.try_set_business_hours("closed")
    ui.close_window()
    assert(s.business_hours_id=="closed")
    s.select_store(0)
    assert(s.business_hours_id=="24h")
    print("RENOVATION_UI_PASS temporary closure, selection/cancel without debit, insufficient-cash revalidation, exact payment, restored hours and UID-bound cleanup")
    ui.hits.clear()
    ui._active_action=Callable()
    ui._pending_taps.clear()
    game.free()
    game=null
    ui=null
    await process_frame
    quit()
