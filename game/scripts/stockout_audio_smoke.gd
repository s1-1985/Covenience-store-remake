extends SceneTree
func _initialize() -> void:call_deferred("run")
func run() -> void:
    change_scene_to_file("res://scenes/main.tscn")
    await process_frame
    await process_frame
    var game=current_scene;game.paused=true;game.set_process(false)
    var s=game.simulation;s.economy.cash_yen=1000000000
    assert(s.try_buy_store_site(Vector2i(26,12)))
    game._sync_site_selection();game.selecting_site=false;game.site_panel.hide();game.store_type_panel.hide()
    if game.phone_ui.notice.visible:game.phone_ui._finish_notice()
    var sound=root.get_node("SoundManager")
    game._play_event_sounds();sound.source_history.clear()
    var product=s.inventory.get_product(s.inventory.product_order[0])
    product.initial_stock_units=40;product.stock_units=26
    var worker=s.staff.members["staff-2"];worker.replenishment_skill=100
    worker.restock_target_product_id=product.product_id
    s._complete_restock(worker);game._play_event_sounds()
    assert(product.stock_units==37 and not sound.source_history.has(24),"Partial refill is silent")
    worker.restock_target_product_id=product.product_id
    s._complete_restock(worker);game._play_event_sounds()
    assert(product.stock_units==40 and sound.source_history.count(24)==1)
    game._play_event_sounds();assert(sound.source_history.count(24)==1)
    # A simulated branch does not speak over the currently displayed store.
    assert(s.try_buy_store_site(Vector2i(3,3),"small_top"))
    s.select_store(0);game._play_event_sounds();sound.source_history.clear()
    s._switch_store(1)
    product=s.inventory.get_product(s.inventory.product_order[0]);product.stock_units=product.initial_stock_units-1
    worker=s.staff.members["staff-2"];worker.replenishment_skill=100;worker.restock_target_product_id=product.product_id
    s._complete_restock(worker);s._switch_store(0);game._play_event_sounds()
    assert(not sound.source_history.has(24),"Background refill must not play selected-store voice")
    print("STOCKOUT_AUDIO_PASS partial silence, full-only original ID24 once, no redraw replay, background-store guard")
    quit()
