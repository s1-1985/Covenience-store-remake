extends SceneTree
var game
var ui
func _initialize() -> void: call_deferred("run")
func tap(at: Vector2) -> void:
    for down in [true,false]:
        var e:=InputEventScreenTouch.new()
        e.position=at
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
    assert(game.simulation.try_buy_store_site(Vector2i(26,12)))
    game._sync_site_selection()
    game.selecting_site=false
    game.site_panel.hide()
    game.store_type_panel.hide()
    if ui.notice.visible: ui._finish_notice()
    assert(game.simulation.try_dismiss_source_staff("staff-3"))
    ui.open_window("candidates")
    await process_frame
    await process_frame
    var old_id: String=ui._person_id(game.simulation.staff,2)
    await tap(Vector2(160,0)+Vector2(123,69)*3)
    assert(ui.page==1)
    await tap(Vector2(160,0)+Vector2(123,69)*3)
    assert(ui.page==2 and ui.selection==21)
    assert(ui._person_id(game.simulation.staff,2)==old_id,"Browsing must not change staff")
    var selected: String=ui._hiring_candidates[2]
    var pool: Array=ui._hiring_candidates.duplicate()
    var seed: int=game.simulation._program_rng.seed
    for i in 35: await process_frame
    assert(ui._hiring_candidates==pool,"Redraw must not resample candidates")
    assert(game.simulation._program_rng.seed==seed,"Redraw must not consume game RNG")
    await tap(Vector2(160,0)+Vector2(210,120)*3)
    assert(ui._person_id(game.simulation.staff,2)==old_id,"Info card must not hire on tap")
    await tap(Vector2(1200,342))
    assert(ui._person_id(game.simulation.staff,2)==selected,"Circle must hire selected candidate, not advance the arrow")
    assert(ui.page==2,"Circle must not run next-candidate action")
    if ui.notice.visible: ui._finish_notice()
    assert(game.simulation.try_dismiss_source_staff("staff-3"))
    var next: String=ui._hiring_candidates[2]
    await tap(Vector2(160,0)+Vector2(200,195)*3)
    assert(ui._person_id(game.simulation.staff,2)==next,"Visible hire button must commit the same decision")
    print("PERSONNEL_DECISION_PASS stable candidate pool and RNG across redraw; browse twice then circle hires selected candidate; info card inert; explicit hire works")
    quit()
