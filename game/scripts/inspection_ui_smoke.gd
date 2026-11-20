extends SceneTree
var game
var ui
func _initialize() -> void:call_deferred("run")
func clear_notices() -> void:
    ui._fallback_notice_queue.clear()
    for i in 12:
        if ui.notice.visible:ui._finish_notice()
        ui._pump_notices()
func tap_global(point:Vector2) -> void:
    clear_notices()
    for down in [true,false]:
        var event:=InputEventScreenTouch.new()
        event.index=0;event.position=point;event.pressed=down
        root.push_input(event,true)
        await process_frame
func tap(point:Vector2) -> void:await tap_global(Vector2(160,0)+point*3)
func map_tap(id:String) -> void:
    var sim=game.simulation
    var index:int=sim._rival_index(id)
    var origin:Vector2i=sim._rival_stores[index].position
    game.town_view.visible=true;game.store_view.visible=false
    game.town_view.view_origin_tile=Vector2i(clampi(origin.x-2,0,20),clampi(origin.y-2,0,24))
    var point:Vector2=game.town_view.position+Vector2(origin-game.town_view.view_origin_tile)*game.town_view.map_tile_pixels+Vector2.ONE*game.town_view.map_tile_pixels/2
    await tap_global(point)
    await process_frame
func run() -> void:
    change_scene_to_file("res://scenes/main.tscn")
    await process_frame
    await process_frame
    game=current_scene;game.paused=true;game.set_process(false)
    ui=game.phone_ui
    assert(str(ui.rival_actions.evidence_note).contains("REMAKE_BALANCED_DEFAULT") and int(ui.rival_actions.inspection_fee_yen)==500000)
    var s=game.simulation
    s.economy.cash_yen=1000000000
    assert(s.try_buy_store_site(Vector2i(26,12)))
    game._sync_site_selection()
    var hq:String=s._rival_stores[0].id
    var branch:String=s._rival_stores[1].id
    s.notifications.reset()
    var cash:int=s.economy.cash_yen
    await map_tap(hq)
    assert(ui.screen=="rival_actions" and not game.rival_panel.visible)
    await tap(Vector2(150,100))
    assert(ui.screen=="rival_confirm" and s.economy.cash_yen==cash and not s.rival_investigated(hq))
    await tap(Vector2(95,175))
    assert(ui.screen=="rival_actions" and s.economy.cash_yen==cash)
    await tap(Vector2(150,100))
    await tap(Vector2(220,175))
    assert(ui.screen=="rival_details" and s.rival_investigated(hq) and s.economy.cash_yen==cash-500000)
    await tap(Vector2(160,195))
    await map_tap(hq)
    assert(ui.screen=="rival_details" and s.economy.cash_yen==cash-500000)
    # Known flag1 opens detail only, with no buyout action in that child path.
    assert(ui.hits.size()==1)
    await tap(Vector2(160,195))
    s.try_set_business_hours("closed")
    s.minute_of_day=1438;s._days_completed_this_month=3
    s._advance_minute_of_day()
    assert(not s.rival_investigated(hq))
    await map_tap(hq)
    assert(ui.screen=="rival_actions")
    await tap(Vector2(150,132))
    assert(ui.screen=="rival_confirm" and not bool(ui._rival_request.allowed))
    assert(ui._rival_error.contains("本店"))
    await tap(Vector2(160,175))
    ui.close_window()
    await map_tap(branch)
    # Stale confirmation stays on screen without payment or model changes.
    await tap(Vector2(150,100))
    ui._rival_request.month=int(ui._rival_request.month)-1
    var count:int=s.economy.expense_records.size()
    await tap(Vector2(220,175))
    assert(ui.screen=="rival_confirm" and not ui._rival_error.is_empty() and s.economy.expense_records.size()==count)
    await tap(Vector2(160,175))
    await tap(Vector2(150,132))
    assert(ui.screen=="rival_confirm" and bool(ui._rival_request.allowed))
    var fee:int=ui._rival_request.cost_yen
    var seller:int=s._rival_cash_yen
    cash=s.economy.cash_yen
    await tap(Vector2(95,175))
    assert(s.store_count()==1 and s.economy.cash_yen==cash)
    await tap(Vector2(150,132))
    await tap(Vector2(220,175))
    assert(ui.screen.is_empty() and s.store_count()==2 and s._rival_index(branch)<0)
    assert(s.economy.cash_yen==cash-fee and s._rival_cash_yen==seller+fee)
    assert(game.town_view.visible and not game.rival_panel.visible)
    print("INSPECTION_UI_PASS native map tap, original three choices/known detail, confirm/cancel, monthly reinspection, HQ refusal, stale request and direct acquisition with single payment")
    clear_notices()
    ui.hits.clear();ui._active_action=Callable();ui._pending_taps.clear()
    game.free();game=null;ui=null
    await process_frame
    quit()
