extends SceneTree

const People = preload("res://scripts/domain/program_people.gd")
const Customer = preload("res://scripts/domain/customer_state.gd")
const Audio = preload("res://scripts/domain/program_audio.gd")
var game
var sound

func _initialize() -> void:
    call_deferred("run")

func hear() -> Array:
    sound.source_history.clear()
    game._play_event_sounds()
    return sound.source_history.duplicate()

func run() -> void:
    change_scene_to_file("res://scenes/main.tscn")
    await process_frame
    await process_frame
    game = current_scene
    game.paused = true
    game.set_process(false)
    var s = game.simulation
    s.economy.cash_yen = 1000000000
    assert(s.try_buy_store_site(Vector2i(26, 12)))
    game._sync_site_selection()
    game.selecting_site = false
    sound = root.get_node("SoundManager")
    sound.enabled = true
    sound.set_source_settings(0)
    game._play_event_sounds()

    # Deliberately reversed chronology, duplicates and a shared cleaning/refill bit.
    for event in ["staff_exhausted", "source_cleaning_completed", "self_service_sale",
        "checkout_completed", "checkout_staff_finished", "checkout_staff_started",
        "shoplifting", "source_restock_completed", "shoplifting"]:
        s._record_event(event)
    assert(hear() == [21, 22, 23, 10, 9, 24, 25])
    assert(hear().is_empty(), "Redraw must not replay consumed events")

    # Existing sale producer: original immediate SE9, no checkout SE10.
    var p = Customer.new({"id": "audio-direct"})
    var product = s.inventory.get_product(s.inventory.product_order[0])
    var cash: int = s.economy.cash_yen
    s._settle_source_immediate(p, {"product_id": product.product_id, "unit_price_yen": 100, "quantity": 2})
    assert(s.economy.cash_yen == cash + 200)
    assert(hear() == [9])

    # Theft failure is silent. Success emits only bit4, not a cash sale.
    for worker in s.staff.all_staff():
        worker.security_skill = 0
    p.group_size = 1
    p.visit = {"manners": 0}
    product.stock_units = 0
    assert(not s._source_try_theft(p, product.product_id))
    assert(hear().is_empty())
    product.stock_units = 1
    cash = s.economy.cash_yen
    assert(s._source_try_theft(p, product.product_id))
    assert(s.economy.cash_yen == cash)
    assert(hear() == [21])

    # Actual native clean completion, including an unsuccessful first attempt.
    var cleaner = s.staff.members["staff-2"]
    var cell := Vector2i(2, 2)
    cleaner.position = cell
    cleaner.source_goal = cell
    cleaner.source_direction = 0
    cleaner.source_goal_direction = 0
    cleaner.source_state = 4
    cleaner.stamina = cleaner.stamina_max
    cleaner.cleaning_skill = 100
    s.minute_of_day = 1
    s.config.store.source_floor[1][1] = 3
    s._program_rng.seed = 1
    People.employee(s, cleaner, 1)
    assert(hear().is_empty())
    var done := false
    for i in 100:
        People.employee(s, cleaner, 1)
        if cleaner.source_goal.x < 0:
            done = true
            break
    assert(done and int(s.config.store.source_floor[1][1]) == 0)
    assert(hear() == [24])

    # Exhaustion notification belongs to the active -> return-to-rest branch.
    cleaner.source_state = 1
    cleaner.stamina = 0
    cleaner.source_goal = cell
    People.employee(s, cleaner, 1)
    assert(cleaner.source_state == 3 and hear() == [25])
    People.employee(s, cleaner, 1)
    assert(hear().is_empty(), "Already returning to rest does not repeat exhaustion")

    # Main's selected-store guard applies to every new mapping.
    for event in Audio.EVENT_FLAGS:
        s._record_event(event, {"store_index": s.viewed_store + 1})
    assert(hear().is_empty())
    sound.set_source_settings(1)
    s._record_event("self_service_sale")
    game._play_event_sounds()
    assert(not sound._source_tracks[9].playing)
    sound.set_source_settings(0)
    assert(hear().is_empty(), "Unmuting must not replay old events")
    print("OPERATING_AUDIO_PASS eight producer mappings, original bit order/shared-bit coalescing, direct sale/theft/clean/exhaustion, hidden store, settings, no redraw replay")
    game.free()
    await process_frame
    quit()
