extends SceneTree
var game
var ui
func _initialize() -> void: call_deferred("run")
func finger(at: Vector2, down: bool, index := 0) -> void:
    var e := InputEventScreenTouch.new()
    e.position=at
    e.pressed=down
    e.index=index
    root.push_input(e,true)
    await process_frame
func tap(at: Vector2, mouse_echo := false) -> void:
    if ui.notice.visible: ui._finish_notice()
    await finger(at,true)
    await finger(at,false)
    if mouse_echo:
        for down in [true,false]:
            var e:=InputEventMouseButton.new()
            e.button_index=MOUSE_BUTTON_LEFT
            e.position=at
            e.pressed=down
            e.device=-1
            root.push_input(e,true)
            await process_frame
func move(at: Vector2,index := 0) -> void:
    var e:=InputEventScreenDrag.new()
    e.position=at
    e.index=index
    root.push_input(e,true)
    await process_frame
func run() -> void:
    change_scene_to_file("res://scenes/main.tscn")
    await process_frame
    await process_frame
    game=current_scene
    game.set_process(false)
    game.paused=true
    ui=game.phone_ui
    assert(game.simulation.try_buy_store_site(Vector2i(26,12)))
    game._sync_site_selection()
    game.selecting_site=false
    game.site_panel.hide()
    game.store_type_panel.hide()
    if ui.notice.visible: ui._finish_notice()
    ui.close_window()
    ui.layout_screen()
    var camera=ui.store_camera
    camera.reset_view()
    var rect: Rect2=camera.content_rect()
    var center: Vector2=game.store_view.global_position+rect.get_center()*game.store_view.scale
    assert(center.distance_to(camera.AREA.get_center())<1)
    # Touch + the OS mouse echo must perform exactly one action.
    await tap(Vector2(80,422),true)
    assert(ui.screen=="view")
    await tap(Vector2(160,0)+Vector2(100,90)*3)
    assert(game.town_view.visible and not game.store_view.visible)
    await tap(Vector2(80,422),true)
    await tap(Vector2(160,0)+Vector2(100,74)*3)
    assert(game.store_view.visible and not game.town_view.visible)
    for expected in [4,8,16,1]:
        await tap(Vector2(80,45),true)
        assert(game.speed==expected,"Speed must change once per finger gesture")
    for town in [false,true]:
        game.town_view.visible=town
        game.store_view.visible=not town
        await tap(Vector2(80,520),true)
        assert(ui.screen=="stores" and not ui.hits.is_empty())
        ui.close_window()
    game.town_view.hide()
    game.store_view.show()
    camera.reset_view()
    var scale_before: float=game.store_view.scale.x
    await finger(Vector2(500,400),true,0)
    await finger(Vector2(700,400),true,1)
    await move(Vector2(1000,400),1)
    await finger(Vector2(1000,400),false,1)
    await finger(Vector2(500,400),false,0)
    assert(game.store_view.scale.x>scale_before*2)
    assert(ui.screen.is_empty())
    var before: Vector2=game.store_view.global_position
    await finger(Vector2(640,400),true)
    await move(Vector2(740,480))
    await finger(Vector2(740,480),false)
    assert(game.store_view.global_position.distance_to(before)>20,"Zoomed store must pan")
    assert(ui.screen.is_empty(),"A pan must not select fixtures")
    # Compare whole game states: 16x scheduler and the same number of 1x ticks.
    var reference=game.simulation.get_script().new(game.config.duplicate(true))
    assert(reference.load_state(game.simulation.save_state()))
    game.paused=false
    game.speed=16
    game.accumulator=0
    var start_minute: int=game.simulation.minute_of_day
    game._advance_simulation(1.0)
    assert(game.accumulator>=8.0,"Frame cap must retain simulation debt")
    while game.accumulator>=game.tick_seconds: game._advance_simulation(0)
    assert(game.simulation.minute_of_day!=start_minute,"Speed test must actually advance the simulation")
    for i in 64: reference.tick()
    assert(JSON.stringify(game.simulation.save_state())==JSON.stringify(reference.save_state()),"16x must preserve clock, people, RNG, sales and every store exactly")
    print("MOBILE_CONTROLS_PASS single action with mouse echo; triangle switch; overview in both views; speed1/4/8/16; centered pinch/pan; 64 complete ticks match reference")
    quit()
