extends SceneTree
var game
var ui
func _initialize() -> void:call_deferred("run")
func tap(p:Vector2) -> void:
    if ui.notice.visible:ui._finish_notice()
    for down in [true,false]:
        var e:=InputEventScreenTouch.new()
        e.position=Vector2(160,0)+p*3;e.pressed=down;e.index=0
        root.push_input(e,true)
        await process_frame
func run() -> void:
    change_scene_to_file("res://scenes/main.tscn")
    await process_frame
    await process_frame
    game=current_scene;game.paused=true;game.set_process(false);ui=game.phone_ui
    var s=game.simulation;s.economy.cash_yen=1000000000
    assert(s.try_buy_store_site(Vector2i(26,12)))
    game._sync_site_selection();game.selecting_site=false;game.site_panel.hide();game.store_type_panel.hide()
    if ui.notice.visible:ui._finish_notice()
    var p=s.staff.members["staff-3"];var id:String=p.candidate_id
    var hourly:int=p.salary_yen_per_day_24h/24;p.stamina=7;p.register_skill=73
    var raises:Dictionary=s._candidate_raises.get(id,{})
    raises.age_years=126-int(s._staff_candidate_catalog[id].age_years);s._candidate_raises[id]=raises
    s.month_count=12;s._apply_source_annual_personnel(1)
    var wage:int=preload("res://scripts/domain/program_annual_personnel.gd").wage(hourly)*24
    assert(p.salary_yen_per_day_24h==wage and p.stamina==7 and p.stamina_max==100)
    ui.open_window("dismiss");await process_frame
    await tap(Vector2(65,155));await tap(Vector2(200,195));await tap(Vector2(200,158))
    assert(not s.staff.members.has("staff-3") and int(s._unassigned_staff[id].salary_yen_per_day_24h)==wage)
    ui.close_window();ui.open_window("candidates")
    ui._hiring_candidates.assign([id]);ui.page=0;ui.slot=2
    await process_frame
    await process_frame
    assert(int(s._candidate_figures(id).age_years)==127 and int(s._candidate_figures(id).salary_yen_per_day_24h)==wage)
    var seed:int=s._program_rng.seed
    ui.surface.queue_redraw();await process_frame;await process_frame
    assert(s._program_rng.seed==seed)
    await tap(Vector2(200,195))
    p=s.staff.members["staff-3"]
    assert(p.candidate_id==id and p.salary_yen_per_day_24h==wage and p.stamina_max==100 and p.register_skill==73)
    print("ANNUAL_PERSONNEL_UI_PASS yearly figures reach personnel card, touch dismissal/rehire retains raised wage/max/skills, redraw leaves RNG unchanged")
    game.free()
    await process_frame
    quit()
