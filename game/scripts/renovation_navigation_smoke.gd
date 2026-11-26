extends SceneTree
var game
var ui
func _initialize() -> void:call_deferred("run")
func check(ok:bool,message:String)->bool:
    if not ok:
        push_error(message)
        quit(1)
    return ok
func run()->void:
    change_scene_to_file("res://scenes/main.tscn")
    await process_frame
    await process_frame
    game=current_scene
    game.set_process(false)
    game.paused=true
    ui=game.phone_ui
    var sim=game.simulation
    sim.economy.cash_yen=1000000000
    if not check(sim.try_buy_store_site(Vector2i(26,12)) and sim.try_buy_store_site(Vector2i(3,3),"small_top"),"Store setup failed"):return
    game._sync_site_selection()
    game.selecting_site=false
    game.select_store(0)
    sim.try_set_business_hours("closed")
    if not check(sim.begin_renovation_edit("medium_top",[],sim._store_uid,sim.store_type_id),"Renovation setup failed"):return
    sim.renovation_session.restore_hours="24h"
    ui._resume_renovation_edit()
    if ui.notice.visible:ui._finish_notice()
    ui._fallback_notice_queue.clear()
    var uid:int=sim._store_uid
    var cash:int=sim.economy.cash_yen
    # Exit refusal must stop the rest of each navigation action.
    ui.open_window("view")
    await process_frame
    var options:Array=ui.hits.filter(func(hit):return hit.index==1)
    if not check(options.size()==1,"View menu missing"):return
    options[0].action.call()
    if not check(ui.screen=="renovation_finish" and game.store_view.visible and not game.town_view.visible,"Town navigation continued after renovation exit was blocked"):return
    ui.open_window("root")
    await process_frame
    options=ui.hits.filter(func(hit):return hit.index==0)
    options[0].action.call()
    if not check(ui.screen=="renovation_finish","Store navigation replaced the renovation finish dialog"):return
    ui.open_window("realestate")
    await process_frame
    options=ui.hits.filter(func(hit):return hit.index==0)
    options[0].action.call()
    if not check(ui.screen=="renovation_finish" and not game.choosing_new_store and not game.selecting_site,"New-store navigation started inside unfinished renovation"):return
    # Selecting the overview must also leave the current camera untouched
    # when close_window redirects to the finish dialog.
    ui.store_camera.zoom_at(1.5,Vector2(640,400))
    var camera:Transform2D=game.store_view.transform
    ui.open_window("stores")
    await process_frame
    options=ui.hits.filter(func(hit):return hit.index==1)
    options[0].action.call()
    if not check(ui.screen=="renovation_finish" and sim._store_uid==uid and game.store_view.transform==camera,"Blocked overview selection changed the editing camera/store"):return
    if not check(sim.economy.cash_yen==cash and sim.business_hours_id=="closed" and not sim.renovation_session.is_empty(),"Blocked navigation committed or canceled the renovation"):return
    await process_frame
    options=ui.hits.filter(func(hit):return hit.index==0)
    options[0].action.call()
    if not check(ui.screen=="interior" and game.store_view.visible,"Continue did not return to the editing store"):return
    ui.close_window()
    await process_frame
    options=ui.hits.filter(func(hit):return hit.index==1)
    options[0].action.call()
    if not check(sim.renovation_session.is_empty() and ui.screen.is_empty() and sim.business_hours_id=="24h","Explicit renovation completion failed"):return
    # Once finished, the same navigation is allowed again.
    ui._navigate("show_town")
    if not check(game.town_view.visible and not game.store_view.visible,"Town navigation stayed blocked after finish"):return
    ui._navigate("enter")
    if not check(ui.screen=="store" and game.store_view.visible,"Store navigation stayed blocked after finish"):return
    ui._navigate("new_store")
    if not check(game.choosing_new_store and game.selecting_site,"New-store navigation stayed blocked after finish"):return
    game.cancel_new_store()
    game.free()
    print("RENOVATION_NAVIGATION_PASS blocked exits preserve finish dialog, store/camera/cash/hours; explicit finish restores normal navigation")
    quit()
