extends SceneTree
var game
var ui
func _initialize() -> void: call_deferred("run")
func check(ok: bool, message: String) -> bool:
    if not ok:
        push_error(message)
        quit(1)
    return ok
func finger(down: bool, pointer := 4) -> void:
    var event:=InputEventScreenTouch.new()
    event.position=Vector2(160,0)+Vector2(120,130)*3
    event.pressed=down
    event.index=pointer
    root.push_input(event,true)
func clear_notices() -> void:
    if ui.notice.visible:ui._finish_notice()
    ui._fallback_notice_queue.clear()
func run() -> void:
    change_scene_to_file("res://scenes/main.tscn")
    await process_frame
    await process_frame
    game=current_scene
    game.set_process(false)
    game.paused=true
    var sim=game.simulation
    sim.economy.cash_yen=1000000000
    if not check(sim.try_buy_store_site(Vector2i(26,12)),"First store setup failed"):return
    if not check(sim.try_buy_store_site(Vector2i(3,3),"small_top"),"Second store setup failed"):return
    game._sync_site_selection()
    game.selecting_site=false
    game.select_store(0)
    ui=game.phone_ui
    clear_notices()
    ui.close_window()
    ui.open_window("view")
    await process_frame
    # The painted view action closes its menu. It must never close the
    # new system menu when accept arrives before that menu's first paint.
    ui.open_window("system")
    ui.handle_accept()
    if not check(ui.screen=="system","Accept ran the previous screen action before redraw"):return
    clear_notices()
    ui.open_window("hours")
    var before:String=sim.business_hours_id
    var presets:Array=sim.business_hours_presets()
    var alternate:=0
    while str(presets[alternate].id)==before:alternate+=1
    ui.choice=alternate
    ui.selection=1
    await process_frame
    finger(true)
    if not check(not ui._pending_taps.is_empty(),"Hours confirmation press missing"):return
    ui.open_window("hours") # same name, different visit/selection
    finger(false)
    if not check(sim.business_hours_id==before,"Old tap survived reopening the same screen"):return
    clear_notices()
    ui.open_window("hours")
    ui.choice=alternate
    ui.selection=1
    await process_frame
    finger(true)
    game.select_store(1)
    var other_before:String=sim.business_hours_id
    clear_notices()
    finger(false)
    if not check(sim.business_hours_id==other_before,"Held confirmation changed the newly selected store"):return
    clear_notices()
    ui.open_window("hours")
    ui.choice=alternate
    ui.selection=1
    await process_frame
    finger(true)
    ui.handle_shoulder(1)
    var changed_choice:int=ui.choice
    finger(false)
    if not check(sim.business_hours_id==other_before,"Held confirmation applied an old hours choice"):return
    # New input on a freshly painted menu still commits the shown choice.
    ui.selection=1
    await process_frame
    finger(true)
    finger(false)
    if not check(sim.business_hours_id==str(presets[changed_choice].id),"Fresh hours confirmation no longer works"):return
    if not check(str(sim.store_field(0,"business_hours_id"))==before,"Confirmation affected the other store"):return
    game.free()
    print("MENU_CONTEXT_PASS no stale accept, same-screen tap, cross-store confirmation or old hours choice; fresh confirmation works")
    quit()
