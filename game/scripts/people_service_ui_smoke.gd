extends SceneTree

const People = preload("res://scripts/domain/program_people.gd")

func _initialize() -> void:
    call_deferred("_run")

func _capture(name: String) -> void:
    if DisplayServer.get_name() != "headless":
        await RenderingServer.frame_post_draw
        root.get_texture().get_image().save_png("user://" + name + ".png")

func _run() -> void:
    var sound = root.get_node("SoundManager")
    sound.enabled = true
    sound.set_source_settings(0)
    change_scene_to_file("res://scenes/main_menu.tscn")
    await process_frame
    await process_frame
    current_scene.new_game_button.pressed.emit()
    await process_frame
    await process_frame
    var game = current_scene
    game.paused = true
    game.set_process(false)
    game._on_site_tapped(Vector2i(26, 12))
    game.site_buy_button.pressed.emit()
    game.find_child("BuildStoreButton", true, false).pressed.emit()
    var sim = game.simulation
    var view = game.store_view
    game.phone_ui.close_window()
    game.phone_ui.notice.visible = false
    assert(sim.staff.all_staff().size() == 3)
    # A real opened store with everyone resting used to draw ZERO staff.
    for slot in 3:
        var worker = sim.staff.all_staff()[slot]
        People.enter_rest(sim, worker, slot)
        assert(worker.source_state == 0 and view._staff_is_visible(worker))
    game._refresh_ui()
    await _capture("people-resting")
    var worker = sim.staff.all_staff()[0]
    var old_id: String = worker.candidate_id
    worker.candidate_id = ""
    assert(not view._staff_is_visible(worker))
    worker.candidate_id = old_id
    # Both populations use distinct native-derived feet, preserving heads.
    assert("REMAKE_BALANCED_DEFAULT" in game.config["sound"]["people_presentation_evidence_note"])
    for appearance in [0, 38, 43]:
        for direction in ["down", "up", "left", "right"]:
            var a: Image = view._program_person_texture(appearance, direction, "A").get_image()
            var b: Image = view._program_person_texture(appearance, direction, "B").get_image()
            assert(a.get_region(Rect2i(0, 0, 16, 12)).get_data() == b.get_region(Rect2i(0, 0, 16, 12)).get_data())
            assert(a.get_data() != b.get_data())
    # Real movement interpolation switches feet while stationary figures freeze.
    view.tick_serial = 10
    view.tick_progress = 1.0
    view._moving_center("test", Vector2i(4, 4))
    view.tick_serial += 1
    view.tick_progress = 0.25
    var first: Array = view._moving_center("test", Vector2i(5, 4))
    view.tick_progress = 0.75
    var second: Array = view._moving_center("test", Vector2i(5, 4))
    assert(first[1] == "A" and second[1] == "B" and first[0].x < second[0].x)
    view.tick_serial += 1
    assert(view._moving_center("test", Vector2i(5, 4))[1] == "A")
    sound.source_history.clear()
    var heard_register := false
    var heard_start := false
    var staff_walked := false
    var customer_walked := false
    var starts := {}
    for person in sim.staff.all_staff():
        starts[person.staff_id] = person.position
    var captured_stride := false
    for i in 1200:
        var before_positions := {}
        view.tick_progress = 1.0
        for person in sim.staff.all_staff():
            before_positions[person.staff_id] = person.position
            view._moving_center("s:" + person.staff_id, person.position)
        sim.tick()
        view.tick_serial += 1
        game._refresh_ui()
        if not captured_stride:
            for person in sim.staff.all_staff():
                var old: Vector2i = before_positions[person.staff_id]
                if person.source_state > 0 and person.position != old and maxi(absi(person.position.x - old.x), absi(person.position.y - old.y)) == 1:
                    view.tick_progress = 0.25
                    view._moving_center("s:" + person.staff_id, person.position)
                    await _capture("people-stride-a")
                    view.tick_progress = 0.75
                    assert(view._moving_center("s:" + person.staff_id, person.position)[1] == "B")
                    await _capture("people-stride-b")
                    captured_stride = true
                    break
        heard_register = heard_register or sound.source_history.has(10)
        heard_start = heard_start or sound.source_history.has(22)
        for person in sim.staff.all_staff():
            if person.source_state > 0 and person.position != starts[person.staff_id]:
                staff_walked = true
        for customer in sim.customers.active_customers():
            if customer.source_state >= 2 and customer.position.x >= 0 and not customer.route.is_empty():
                customer_walked = true
        if i % 80 == 0:
            await process_frame
    assert(sim.economy.completed_sales > 0 and heard_register and heard_start)
    assert(staff_walked and customer_walked)
    assert(captured_stride)
    view.tick_progress = 1.0
    await _capture("people-working")
    # Complete the actual native service-arrival transition with no customers.
    for customer in sim.customers.active_customers():
        customer.phase = "done"
    worker.source_state = 1
    worker.position = worker.source_goal if worker.source_goal.x >= 0 else sim.layout.entry
    worker.source_goal = worker.position
    worker.source_direction = 1
    worker.source_goal_direction = 1
    worker.stamina = worker.stamina_max
    sound.source_history.clear()
    People.employee(sim, worker, 0)
    game._play_event_sounds()
    assert(sound.source_history.has(23))
    var before: int = sound.source_history.size()
    game._play_event_sounds()
    assert(sound.source_history.size() == before) # paused refresh never repeats.
    sound.source_history.clear()
    sim._record_event("checkout_completed", {"store_index": sim.viewed_store + 1})
    game._play_event_sounds()
    assert(not sound.source_history.has(10)) # unseen branch must remain quiet.
    sound.set_source_settings(1)
    assert(not sound.play_source(10) and not sound.play_source(22) and not sound.play_source(23))
    sound.set_source_settings(0)
    assert(sound.play_source(10) and sound.play_source(22) and sound.play_source(23))
    sound.stop_music()
    sound.stop_source_voice()
    for player in sound._source_tracks:
        player.stop()
        player.stream = null
    await process_frame
    await process_frame
    print("PEOPLE_SERVICE_UI_PASS resting workers, empty slots, 12 stride pairs, interpolation, actual sales SE10 and work VOS22/23, settings and no repeats; sales=", sim.economy.completed_sales)
    quit()
