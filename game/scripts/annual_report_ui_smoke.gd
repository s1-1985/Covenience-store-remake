extends SceneTree
func _initialize() -> void:call_deferred("run")
func run() -> void:
    change_scene_to_file("res://scenes/main.tscn")
    await process_frame
    await process_frame
    var game=current_scene;game.paused=true;game.set_process(false)
    var s=game.simulation;var ui=game.phone_ui
    s.economy.cash_yen=1000000000;assert(s.try_buy_store_site(Vector2i(26,12)))
    s.try_set_business_hours("closed")
    s.notifications.reset();ui._fallback_notice_queue.clear();ui._source_notice_visible=false;ui.notice.hide()
    s._record_event("manager_report",{"text":"先の通知"})
    s._annual_sales_yen=700000000;s.month_count=12;s._annual_review()
    s.internal_rating_value=70;s.town.population=14000
    ui._pump_notices();assert("先の通知" in ui.notice_label.text)
    assert(s.last_owner_review.is_empty())
    var data:Dictionary=JSON.parse_string(JSON.stringify(s.save_state()));assert(s.load_state(data))
    s.town.population=14000
    ui._finish_notice();ui._pump_notices()
    assert(s.notifications.current.mode==3)
    assert("年間オーナー評価" in ui.notice_label.text and "700,000,000" in ui.notice_label.text)
    assert("14,000" in ui.notice_label.text and "平均評価 70" in ui.notice_label.text)
    assert(ui._fallback_notice_queue.is_empty())
    assert(s.last_owner_review.mean_rating==70 and s.last_owner_review.annual_sales==700000000)
    ui._finish_notice();ui._pump_notices()
    assert(not ui.notice.visible,"Annual report must not be queued again by redraw")
    print("ANNUAL_REPORT_UI_PASS earlier notice, JSON interruption, live inputs, readable annual report and no redraw duplicate")
    game.free()
    await process_frame
    quit()
