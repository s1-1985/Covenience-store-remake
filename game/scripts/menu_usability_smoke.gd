extends SceneTree
var game
var ui
func _initialize() -> void: call_deferred("run")
func finger(at: Vector2, down: bool, cancel := false) -> void:
    var e:=InputEventScreenTouch.new()
    e.position=at
    e.pressed=down
    e.canceled=cancel
    e.index=0
    root.push_input(e,true)
    await process_frame
func tap(p: Vector2) -> void:
    if ui.notice.visible: ui._finish_notice()
    await finger(Vector2(160,0)+p*3,true)
    await finger(Vector2(160,0)+p*3,false)
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
    ui.open_window("root")
    await process_frame
    await process_frame
    var point:=Vector2(160,0)+Vector2(65,85)*3
    await finger(point,true)
    assert(ui.screen=="root","Press must select, not execute")
    await finger(point+Vector2(400,0),false)
    assert(ui.screen=="root","Slide off must cancel")
    await finger(point,true)
    await finger(point,false,true)
    assert(ui.screen=="root","OS canceled gesture must not execute")
    await tap(Vector2(65,85))
    assert(ui.screen=="realestate")
    ui.close_window()
    ui.open_window("candidates")
    await process_frame
    await process_frame
    var original_pool: Array=ui._hiring_candidates.duplicate()
    await tap(Vector2(123,69))
    await tap(Vector2(123,69))
    assert(ui.page==2)
    var roster: String=ui._person_id(game.simulation.staff,0)
    await tap(Vector2(200,195))
    assert(ui._person_id(game.simulation.staff,0)==roster,"Full slots must not be overwritten")
    if ui.notice.visible: ui._finish_notice()
    await tap(Vector2(70,204)) # go to dismissal without leaving personnel flow
    assert(ui.screen=="dismiss")
    await tap(Vector2(65,155)) # select third staff
    var leaving: String=ui._person_id(game.simulation.staff,2)
    await tap(Vector2(200,195))
    assert(ui.screen=="dismiss_confirm")
    assert(ui._person_id(game.simulation.staff,2)==leaving,"Dismissal needs confirmation")
    await tap(Vector2(90,158)) # back
    assert(ui.screen=="dismiss" and ui.slot==2)
    assert(ui._person_id(game.simulation.staff,2)==leaving)
    await tap(Vector2(200,195))
    await tap(Vector2(200,158)) # explicit dismissal
    assert(ui.screen=="dismiss" and ui._person_id(game.simulation.staff,2).is_empty())
    if ui.notice.visible: ui._finish_notice()
    var seed: int=game.simulation._program_rng.seed
    ui.handle_cancel()
    await process_frame
    assert(ui.screen=="candidates" and ui.page==2)
    assert(ui._hiring_candidates==original_pool and game.simulation._program_rng.seed==seed,"Back must restore candidates without RNG consumption")
    assert(ui.slot==2,"Return from dismissal should select the new vacancy")
    var selected: String=ui._hiring_candidates[2]
    await tap(Vector2(200,195))
    assert(ui._person_id(game.simulation.staff,2)==selected)
    print("MENU_USABILITY_PASS release activation, slide/cancel no-op, full roster guard, dismissal cancel/commit, back restores page/pool/RNG, vacancy hire")
    quit()
