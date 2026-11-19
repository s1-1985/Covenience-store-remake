extends SceneTree
var game
var ui
func _initialize() -> void:
    call_deferred("_run")
func touch(p: Vector2, pressed: bool, index := 0, canceled := false) -> void:
    var event := InputEventScreenTouch.new()
    event.position = Vector2(160,0)+p*3
    event.index = index
    event.pressed = pressed
    event.canceled = canceled
    ui._input(event)
func drag(p: Vector2, index := 0) -> void:
    var event := InputEventScreenDrag.new()
    event.position = Vector2(160,0)+p*3
    event.index = index
    ui._input(event)
func _run() -> void:
    change_scene_to_file("res://scenes/main.tscn")
    await process_frame
    await process_frame
    game = current_scene
    game.paused = true
    ui = game.phone_ui
    var sim = game.simulation
    assert(sim.try_buy_store_site(Vector2i(26,12)))
    game._sync_site_selection()
    game.selecting_site = false
    ui.close_window()
    ui.open_window("root")
    await process_frame
    await process_frame
    touch(Vector2(65,80),true)
    touch(Vector2(65,80),false)
    assert(ui.screen == "realestate","Native touch must open menus without mouse emulation")
    ui.close_window()
    # Two populated stores exercise an actual cross-store swap, not a mock.
    sim.economy.cash_yen = 1000000000
    assert(sim.try_buy_store_site(Vector2i(3,3),"small_top"))
    ui.open_window("transfer")
    ui.transfer_store = 1
    await process_frame
    await process_frame
    var first = sim.store_field(0,"staff").members["staff-1"]
    var second = sim.store_field(1,"staff").members.get("staff-2")
    # Source commit must clear an in-progress task from the old shop.
    var stamina: int = first.stamina
    var skill: int = first.register_skill
    first.source_state = 1
    first.source_goal = Vector2i(999,999)
    first.source_served = true
    first.route.assign([Vector2i(998,999)])
    touch(Vector2(40,75),true)
    drag(Vector2(272,123))
    # A second finger must not change the source or commit the drag.
    touch(Vector2(272,170),true,1)
    touch(Vector2(272,170),false,1)
    assert(sim.store_field(0,"staff").members["staff-1"] == first)
    touch(Vector2(272,123),false)
    assert(sim.store_field(1,"staff").members["staff-2"] == first)
    assert(sim.store_field(0,"staff").members.get("staff-1") == second)
    assert(first.source_state == 0 and first.source_goal == Vector2i(-1,-1))
    assert(first.route.is_empty() and not first.source_served)
    assert(first.stamina == stamina and first.register_skill == skill)
    assert(sim.active_store == 0 and sim.viewed_store == 0)
    if ui.notice.visible: ui._finish_notice()
    # Drop outside portraits, OS cancellation, and screen changes are no-ops.
    touch(Vector2(272,123),true)
    drag(Vector2(150,30))
    touch(Vector2(150,30),false)
    assert(sim.store_field(1,"staff").members["staff-2"] == first)
    touch(Vector2(272,123),true)
    drag(Vector2(40,75))
    touch(Vector2(40,75),false,0,true)
    assert(sim.store_field(1,"staff").members["staff-2"] == first)
    touch(Vector2(272,123),true)
    ui.close_window()
    touch(Vector2(40,75),false)
    assert(ui._staff_drag.is_empty())
    assert(sim.store_field(1,"staff").members["staff-2"] == first)
    # A click selects, and the existing confirmation follows the same swap API.
    ui.open_window("transfer")
    ui.transfer_store = 1
    await process_frame
    await process_frame
    touch(Vector2(272,123),true)
    touch(Vector2(272,123),false)
    assert(ui.transfer_slot == 1 and sim.store_field(1,"staff").members["staff-2"] == first)
    # Typography covers the former bitmap alphabet in the bundled font.
    for character in ui.glyphs:
        assert(ui.readable_font.has_char(str(character).unicode_at(0)),"Readable font lacks "+str(character))
    var saved: Dictionary = JSON.parse_string(JSON.stringify(sim.save_state()))
    var clone = sim.get_script().new(game.config.duplicate(true))
    assert(clone.load_state(saved))
    assert(clone.store_count() == 2)
    assert(clone.store_field(1,"staff").members["staff-2"].candidate_id == first.candidate_id)
    assert(clone.store_field(1,"staff").members["staff-2"].source_goal == Vector2i(-1,-1))
    var audio = root.get_node("SoundManager")
    audio._sfx_cache.clear()
    audio.play_sfx("door_chime")
    assert(audio._sfx_cache.is_empty(),"Unmapped aliases must not synthesize non-PS effects")
    audio.play_sfx("select")
    assert(audio.source_history[-1] == 1)
    print("PS_TOUCH_AUDIT_PASS native menu + cross-store drag/swap + multitouch/cancel/outside + source-only audio")
    ui.close_window()
    ui.hits.clear()
    ui._active_action = Callable()
    game.free()
    quit()
