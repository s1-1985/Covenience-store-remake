extends SceneTree
const Save = preload("res://scripts/save_game_service.gd")
class RedirectSave extends RefCounted:
    var path: String
    var service = Save.new()
    var refuse_save := false
    func save_exists() -> bool: return service.save_exists(path)
    func read_from_path() -> Dictionary: return service.read_from_path(path)
    func load_from_path(simulation) -> bool: return service.load_from_path(simulation,path)
    func save_to_path(simulation) -> bool:
        return false if refuse_save else service.save_to_path(simulation,path)
var path := ""
var service = Save.new()
func _initialize() -> void: call_deferred("run")
func check(ok: bool, message: String) -> bool:
    if not ok:
        service.delete_save(path)
        push_error(message)
        quit(1)
    return ok
func write_data(data) -> void:
    var file=FileAccess.open(path,FileAccess.WRITE)
    file.store_string(JSON.stringify(data))
    file.close()
func run() -> void:
    path="user://tests/save-feedback-%s.json" % Time.get_ticks_usec()
    change_scene_to_file("res://scenes/main.tscn")
    await process_frame
    await process_frame
    var game=current_scene
    game.set_process(false)
    game.paused=true
    game.simulation.economy.cash_yen=1000000000
    if not check(game.simulation.try_buy_store_site(Vector2i(26,12)),"Store setup failed"):return
    game._sync_site_selection()
    game.selecting_site=false
    var redirect=RedirectSave.new()
    redirect.path=path
    game._save_service=redirect
    var ui=game.phone_ui
    if ui.notice.visible:ui._finish_notice()
    ui._fallback_notice_queue.clear()
    ui.close_window()
    ui.open_window("system")
    await process_frame
    var options:Array=ui.hits.filter(func(hit):return hit.index==0)
    if not check(options.size()==1,"Save option missing"):return
    options[0].action.call()
    if not check(ui.notice.visible and ui.notice_label.text==game.tr("Game saved"),"PS system save has no visible success result"):return
    var original=FileAccess.get_file_as_string(path)
    ui._finish_notice()
    options[0].action.call()
    if not check(ui.notice.visible and ui.notice_label.text==game.tr("Game saved"),"Repeated PS save has no visible success result"):return
    if not check(not ui._fallback_notice_queue.has(game.tr("Game saved")),"Save result was shown twice"):return
    ui._finish_notice()
    redirect.refuse_save=true
    options[0].action.call()
    if not check(ui.notice.visible and ui.notice_label.text==game.tr("Save failed"),"PS system save has no visible failure result"):return
    if not check(FileAccess.get_file_as_string(path)==original,"Failed save replaced the saved file"):return
    ui._finish_notice()
    write_data([])
    options=ui.hits.filter(func(hit):return hit.index==1)
    options[0].action.call()
    if not check(ui.notice.visible and ui.notice_label.text==game.tr("No compatible save found") and ui.screen=="system","PS load failure has no visible result or loses its menu"):return
    ui._finish_notice()
    options[0].action.call()
    if not check(ui.notice.visible and ui.notice_label.text==game.tr("No compatible save found"),"Repeated PS load failure has no visible result"):return
    var broken=FileAccess.open(path,FileAccess.WRITE)
    broken.store_string("{")
    broken.close()
    if not check(service.read_from_path(path).is_empty(),"Truncated JSON was accepted"):return
    write_data([])
    var launch=root.get_node("GameLaunchState")
    change_scene_to_file("res://scenes/main_menu.tscn")
    await process_frame
    await process_frame
    var menu=current_scene
    menu._save_service=redirect
    menu.ps_title.phase="menu"
    menu.ps_title.selected=1
    menu.ps_title.accept()
    await process_frame
    if not check(current_scene==menu and not launch.continue_from_save and menu.ps_title.message==menu.tr("No compatible save found"),"Invalid save launched gameplay from the title"):return
    # A matching scenario with an unsupported schema passes the title's
    # lightweight read, but the actual simulation must refuse and return.
    var saved=JSON.parse_string(original)
    saved.save_schema_version=-1
    write_data(saved)
    launch.continue_from_save=true
    menu.free()
    var rejected_game=load("res://scenes/main.tscn").instantiate()
    rejected_game._save_service=redirect
    root.add_child(rejected_game)
    current_scene=rejected_game
    await process_frame
    await process_frame
    menu=current_scene
    if not check(menu!=rejected_game and menu.has_node("Panel") and menu.ps_title.message==menu.tr("No compatible save found"),"Rejected continue silently became a new game"):return
    if not check(menu.ps_title.phase=="menu" and menu.ps_title.selected==1 and not launch.continue_from_save,"Failed continue did not return to its visible title choice"):return
    # A valid cleared save remains a title operation and keeps its existing
    # unlock behavior. It must not reuse the old load-error message.
    saved.save_schema_version=JSON.parse_string(original).save_schema_version
    saved.source_progress.save_finished=255
    saved.source_progress.flags=7
    write_data(saved)
    menu._save_service=redirect
    menu.ps_title.accept()
    if not check(launch.progress_flags==7 and menu.ps_title.message=="クリア結果を読み込みました。" and not launch.continue_from_save,"Cleared-save title flow regressed"):return
    # Valid native JSON still resumes an existing store rather than taking
    # the rejection path. Test IO never touches the default user save.
    write_data(JSON.parse_string(original))
    launch.continue_from_save=true
    menu.free()
    var resumed=load("res://scenes/main.tscn").instantiate()
    resumed._save_service=redirect
    root.add_child(resumed)
    current_scene=resumed
    resumed.set_process(false)
    await process_frame
    await process_frame
    if not check(current_scene==resumed and resumed.simulation.has_store_site() and not resumed.selecting_site and not launch.continue_from_save,"Valid continue failed to restore its built store"):return
    service.delete_save(path)
    resumed.free()
    print("SAVE_FEEDBACK_PASS visible save success/failure and load failure; invalid title input rejected; failed continue returns; clear unlock preserved")
    quit()
