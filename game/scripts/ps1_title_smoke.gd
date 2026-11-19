extends SceneTree
func _initialize() -> void:
    call_deferred("_run")
func capture(title, name: String) -> void:
    if DisplayServer.get_name() == "headless": return
    title.surface.queue_redraw()
    await process_frame
    await RenderingServer.frame_post_draw
    root.get_texture().get_image().save_png(OS.get_environment("CONVENI_CAPTURE_DIR").path_join("title-"+name+".png"))
func _run() -> void:
    change_scene_to_file("res://scenes/main_menu.tscn")
    await process_frame
    await process_frame
    var menu = current_scene
    var title = menu.ps_title
    title.set_process(false)
    title.phase = "intro"
    title.tick = 0
    title.y = -267
    title.bounce_mode = 0
    title.bounce_count = 1
    title.velocity = 1
    title.accept()
    assert(title.phase == "intro","Early Start must not skip the original bounce")
    for i in 125: title.step_title()
    assert(title.phase == "start" and title.y == -95)
    await capture(title,"start")
    title.accept()
    assert(title.phase == "hide")
    var steps := 0
    while title.phase == "hide":
        title.step_title()
        steps += 1
        assert(steps <= 26)
    assert(steps == 26 and title.heights == [0,0,0,0,0,0,0,0,0,0])
    while title.phase == "reveal": title.step_title()
    assert(title.phase == "menu" and title.heights == [16,16,16,16,16,16,16,16,16,16])
    await capture(title,"menu")
    title.selected = 0
    title.accept()
    assert(menu.get_node("Panel").visible and not title.visible)
    menu._on_quit_pressed()
    assert(title.visible and not menu.get_node("Panel").visible)
    title.cancel()
    assert(title.phase == "intro" and title.y == -267)
    print("PS_TITLE_PASS original 125-tick bounce, Start gate, 26-tick strips, two choices and scenario return")
    menu.free()
    quit()
