extends SceneTree
var game
func _initialize() -> void: call_deferred("run")
func check(ok: bool, message: String) -> bool:
    if not ok:
        push_error(message)
        quit(1)
    return ok
func finger(at: Vector2, down: bool, index := 0) -> void:
    var e := InputEventScreenTouch.new()
    e.position=at;e.pressed=down;e.index=index
    root.push_input(e,true)
    await process_frame
func run() -> void:
    change_scene_to_file("res://scenes/main.tscn")
    await process_frame
    await process_frame
    game=current_scene
    game.set_process(false)
    game.paused=true
    game.simulation.economy.cash_yen=1000000000
    if not check(game.simulation.try_buy_store_site(Vector2i(26,12)),"Store setup failed"):return
    game._sync_site_selection()
    game.selecting_site=false
    var ui=game.phone_ui
    if ui.notice.visible:ui._finish_notice()
    ui.close_window()
    game._notification(MainLoop.NOTIFICATION_APPLICATION_PAUSED)
    game._notification(MainLoop.NOTIFICATION_APPLICATION_FOCUS_IN)
    if not check(game._app_suspended,"FOCUS_IN resumed an application that is still PAUSED"):return
    game.paused=false
    var serial:int=game.store_view.tick_serial
    var debt:float=game.accumulator
    game._clock_last_us=Time.get_ticks_usec()-10000000
    game._process(1.0)
    if not check(game.store_view.tick_serial==serial and game.accumulator==debt,"Suspension advanced the simulation"):return
    game._notification(MainLoop.NOTIFICATION_APPLICATION_FOCUS_OUT)
    game._notification(MainLoop.NOTIFICATION_APPLICATION_RESUMED)
    if not check(game._app_suspended,"RESUMED ignored the remaining focus loss"):return
    game._notification(MainLoop.NOTIFICATION_APPLICATION_FOCUS_IN)
    if not check(not game._app_suspended and game._clock_last_us==0,"Fully resumed application did not reset its wall clock"):return
    game.paused=true
    # A held rail action must be canceled, not released into a speed change.
    var speed:int=game.speed
    await finger(Vector2(80,45),true)
    game._notification(MainLoop.NOTIFICATION_APPLICATION_PAUSED)
    game._notification(MainLoop.NOTIFICATION_APPLICATION_RESUMED)
    await finger(Vector2(80,45),false)
    if not check(game.speed==speed,"A pre-suspension rail press fired on return"):return
    # A new gesture after return still works.
    await finger(Vector2(80,45),true)
    await finger(Vector2(80,45),false)
    if not check(game.speed!=speed,"Fresh rail input stopped working after resume"):return
    # Camera fingers are dropped without resetting the player's view.
    ui.store_camera.zoom_at(2.0,Vector2(640,400))
    var zoom:Vector2=game.store_view.scale
    var position:Vector2=game.store_view.global_position
    await finger(Vector2(640,400),true,3)
    game._notification(MainLoop.NOTIFICATION_APPLICATION_FOCUS_OUT)
    game._notification(MainLoop.NOTIFICATION_APPLICATION_FOCUS_IN)
    if not check(ui.store_camera._points.is_empty(),"A camera finger survived suspension"):return
    if not check(game.store_view.scale==zoom and game.store_view.global_position==position,"Suspension reset the store view"):return
    # Source menu taps cannot activate a callback from the old press.
    ui.open_window("system")
    var fired:Array=[]
    ui._pending_taps[9]={"screen":ui.screen,"rect":Rect2(0,0,320,240),"action":func():fired.append(true)}
    game._notification(MainLoop.NOTIFICATION_APPLICATION_PAUSED)
    game._notification(MainLoop.NOTIFICATION_APPLICATION_RESUMED)
    await finger(Vector2(640,400),false,9)
    if not check(fired.is_empty(),"An old menu action fired on resume"):return
    ui.close_window()
    # A pending layout move is a preview, not a transaction on resume.
    game.store_view.show()
    var moves:Array=[]
    game.store_view.fixture_relocation_requested.connect(func(_id,_cell):moves.append(true))
    game.store_view._drag_fixture=str(game.simulation.layout.fixtures[0].id)
    game.store_view._drag_start_cell=Vector2i(0,0)
    game.store_view._drag_cell=Vector2i(1,1)
    game._notification(MainLoop.NOTIFICATION_APPLICATION_FOCUS_OUT)
    game._notification(MainLoop.NOTIFICATION_APPLICATION_FOCUS_IN)
    var release:=InputEventScreenTouch.new()
    release.position=Vector2(640,400);release.pressed=false
    game.store_view._unhandled_input(release)
    if not check(moves.is_empty(),"A canceled fixture preview moved furniture on resume"):return
    # Map release must not select a site/building from an old press either.
    game.store_view.hide()
    game.town_view.show()
    ui.layout_screen()
    var selections:Array=[]
    game.town_view.map_tapped.connect(func(_tile):selections.append(true))
    release.position=game.town_view.global_position+Vector2(50,50)
    var press:=InputEventScreenTouch.new()
    press.position=release.position;press.pressed=true
    game.town_view._unhandled_input(press)
    game._notification(MainLoop.NOTIFICATION_APPLICATION_PAUSED)
    game._notification(MainLoop.NOTIFICATION_APPLICATION_RESUMED)
    game.town_view._unhandled_input(release)
    if not check(selections.is_empty(),"A map release selected a building after resume"):return
    if not check(game.paused,"Lifecycle notifications changed the player's pause choice"):return
    game.free()
    await process_frame
    print("MOBILE_RESUME_PASS independent pause/focus state, stopped clock/debt, canceled rail/menu/camera/fixture/map gestures, fresh input and zoom preserved")
    quit()
