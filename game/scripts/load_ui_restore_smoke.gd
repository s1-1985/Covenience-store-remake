extends SceneTree
const Save = preload("res://scripts/save_game_service.gd")
class RedirectSave extends RefCounted:
    var path: String
    var service = Save.new()
    func load_from_path(simulation) -> bool:
        return service.load_from_path(simulation,path)
var game
var path := ""
var service = Save.new()
func _initialize() -> void: call_deferred("run")
func check(ok: bool, message: String) -> bool:
    if not ok:
        service.delete_save(path)
        push_error(message)
        quit(1)
    return ok
func run() -> void:
    path="user://tests/load-ui-%s.json" % Time.get_ticks_usec()
    change_scene_to_file("res://scenes/main.tscn")
    await process_frame
    await process_frame
    game=current_scene
    game.set_process(false)
    game.paused=true
    var s=game.simulation
    s.economy.cash_yen=1000000000
    if not check(s.try_buy_store_site(Vector2i(26,12)),"Store setup failed"):return
    game._sync_site_selection()
    game.selecting_site=false
    var ui=game.phone_ui
    if ui.notice.visible:ui._finish_notice()
    ui.close_window()
    var redirect=RedirectSave.new()
    redirect.path=path
    game._save_service=redirect
    if not check(service.save_to_path(s,path),"Writing test save failed"):return
    game.start_new_store()
    if not check(game.choosing_new_store and game.selecting_site,"New-store selection was not active"):return
    game._on_load_pressed()
    if not check(not game.choosing_new_store and not game.selecting_site,"Loading a built store kept the old new-store selection active"):return
    # Use the real system-menu load action: closing its old editing context
    # must not overwrite the loaded store's saved opening hours.
    s.try_set_business_hours("24h")
    if not check(service.save_to_path(s,path),"Writing hours save failed"):return
    ui.open_window("system")
    await process_frame
    ui.close_hours="closed"
    ui._close_store_uid=s._store_uid
    var options:Array=ui.hits.filter(func(hit):return hit.index==1)
    if not check(options.size()==1,"System load option not found"):return
    options[0].action.call()
    if not check(s.business_hours_id=="24h","Old menu cleanup overwrote the loaded opening hours"):return
    if not check(ui.close_hours.is_empty() and ui.screen.is_empty(),"Old menu state remained after successful load"):return
    # Restore a real unfinished renovation directly into its saved editor.
    s.try_set_business_hours("closed")
    if not check(s.begin_renovation_edit("small_top",[],s._store_uid,s.store_type_id),"Renovation setup failed"):return
    s.renovation_session.restore_hours="24h"
    var uid:int=s.renovation_session.store_uid
    if not check(service.save_to_path(s,path),"Writing renovation save failed"):return
    s.finish_renovation_edit(false)
    ui.close_window()
    ui.open_window("system")
    await process_frame
    options=ui.hits.filter(func(hit):return hit.index==1)
    options[0].action.call()
    if not check(not s.renovation_session.is_empty() and ui.screen=="interior","Loaded renovation did not reopen its interior editor"):return
    if not check(ui._close_store_uid==uid and ui.close_hours=="24h" and s.business_hours_id=="closed","Saved renovation restore context was lost"):return
    # Unusable input leaves the live game and current menu intact.
    var before:String=JSON.stringify(s.save_state())
    var screen:String=ui.screen
    var file=FileAccess.open(path,FileAccess.WRITE)
    file.store_string("[]")
    file.close()
    game._on_load_pressed()
    if not check(JSON.stringify(s.save_state())==before and ui.screen==screen,"A failed load changed the live game/menu"):return
    service.delete_save(path)
    game.free()
    await process_frame
    print("LOAD_UI_RESTORE_PASS real JSON file, cancel old site selection, preserve loaded hours, resume saved renovation, failed load unchanged")
    quit()
