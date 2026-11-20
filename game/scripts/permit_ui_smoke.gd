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
    game._sync_site_selection()
    game.selecting_site=false
    game.site_panel.hide()
    game.store_type_panel.hide()
    if ui.notice.visible: ui._finish_notice()
    ui.open_window("permits")
    await process_frame
    await process_frame
    var cash: int=s.economy.cash_yen
    for y in [88,112,136]: await tap(Vector2(200,y))
    assert(ui._permit_selected.size()==3)
    assert(s.economy.cash_yen==cash and s._permits_held.is_empty(),"Selection is provisional")
    await tap(Vector2(210,188))
    assert(ui.screen=="permit_confirm")
    await tap(Vector2(80,180))
    assert(ui.screen=="permits" and ui._permit_selected.size()==3 and s.economy.cash_yen==cash)
    await tap(Vector2(210,188))
    s.economy.cash_yen=19999999
    await tap(Vector2(210,180))
    assert(ui.screen=="permit_confirm" and s._permits_held.is_empty() and s.economy.cash_yen==19999999)
    s.economy.cash_yen=20000000
    await tap(Vector2(210,180))
    assert(ui.screen=="permits" and s._permits_held.size()==3 and s.economy.cash_yen==0)
    var count: int=s.economy.expense_records.size()
    await tap(Vector2(200,88))
    assert(s.economy.expense_records.size()==count,"Held permit cannot be purchased twice")
    ui.close_window()
    ui.open_window("permits")
    assert(ui._permit_selected.is_empty())
    print("PERMIT_UI_PASS native selection, no debit before commit, cancel preservation, insufficient cash revalidation, exact payment and duplicate guard")
    ui.hits.clear()
    ui._active_action=Callable()
    ui._pending_taps.clear()
    game.free()
    game=null
    ui=null
    await process_frame
    quit()
