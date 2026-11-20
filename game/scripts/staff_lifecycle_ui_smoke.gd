extends SceneTree
var game
var ui
func _initialize() -> void: call_deferred("run")
func tap(p:Vector2) -> void:
    if ui.notice.visible: ui._finish_notice()
    for down in [true,false]:
        var e:=InputEventScreenTouch.new()
        e.position=Vector2(160,0)+p*3;e.pressed=down;e.index=0
        root.push_input(e,true)
        await process_frame
func run() -> void:
    change_scene_to_file("res://scenes/main.tscn")
    await process_frame
    await process_frame
    game=current_scene;game.set_process(false);game.paused=true;ui=game.phone_ui
    var s=game.simulation
    s.economy.cash_yen=1000000000
    assert(s.try_buy_store_site(Vector2i(26,12)))
    game._sync_site_selection();game.selecting_site=false
    game.site_panel.hide();game.store_type_panel.hide()
    if ui.notice.visible: ui._finish_notice()
    var p=s.staff.members["staff-3"]
    var id:String=p.candidate_id
    p.register_skill=92;p.salary_yen_per_day_24h=13789;p.stamina=1;p.source_assignment_experience=4
    ui.open_window("dismiss")
    await process_frame
    await tap(Vector2(65,155))
    await tap(Vector2(200,195))
    assert(ui.screen=="dismiss_confirm" and s.staff.members.has("staff-3"))
    await tap(Vector2(90,158))
    assert(s.staff.members["staff-3"].stamina==1 and not s._unassigned_staff.has(id),"Cancel has no lifecycle side effects")
    await tap(Vector2(200,195));await tap(Vector2(200,158))
    assert(not s.staff.members.has("staff-3") and int(s._unassigned_staff[id].salary_yen_per_day_24h)==13789)
    ui.close_window();ui.open_window("candidates")
    # Fix the UI's already-sampled pool to the known released person, without
    # changing RNG. Tests the same portrait and visible hire-button path.
    ui._hiring_candidates.assign([id]);ui.page=0;ui.slot=2
    await process_frame
    await process_frame
    await tap(Vector2(200,195))
    p=s.staff.members["staff-3"]
    assert(p.candidate_id==id and p.register_skill==92 and p.salary_yen_per_day_24h==13789 and p.source_assignment_experience==5)
    ui.close_window();ui.open_window("transfer")
    ui.transfer_store=s.active_store;ui.slot=2;ui.transfer_slot=1
    p.stamina=1
    await process_frame
    await process_frame
    await tap(Vector2(153,211))
    p=s.staff.members["staff-2"]
    assert(p.candidate_id==id and p.stamina==p.stamina_max and p.source_assignment_experience==6)
    print("STAFF_LIFECYCLE_UI_PASS dismissal cancel and confirm, rehire retained person through touch, same-store assignment decision")
    quit()
