extends SceneTree
var game
var ui
var sound
func _initialize() -> void:call_deferred("run")
func touch(at: Vector2, down: bool, canceled := false) -> void:
    var event:=InputEventScreenTouch.new()
    event.index=0;event.position=at;event.pressed=down;event.canceled=canceled
    root.push_input(event,true)
    await process_frame
func tap(at: Vector2) -> void:
    await touch(at,true)
    await touch(at,false)
func run() -> void:
    change_scene_to_file("res://scenes/main.tscn")
    await process_frame
    await process_frame
    sound=root.get_node("SoundManager")
    var meta:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://assets/ps1/ui/calendar-source.json"))
    assert(str(meta.evidence_note).contains("REMAKE_BALANCED_DEFAULT") and int(meta.wait_calls)==120)
    game=current_scene;game.paused=true;game.set_process(false)
    ui=game.phone_ui;ui.set_process(false)
    var s=game.simulation
    s.economy.cash_yen=1000000000
    assert(s.try_buy_store_site(Vector2i(26,12)))
    game._sync_site_selection()
    s.try_set_business_hours("closed")
    s._chain_visitors_total=10002;s._store_visitor_heads=10002;s.source_calendar.pending=1
    s.minute_of_day=1438;s._advance_minute_of_day()
    game._refresh_ui()
    assert(s.source_calendar_blocked())
    var old_speed:int=game.speed
    assert(ui._process_calendar())
    assert(sound.source_history[-1]==59)
    # Before120 presentation updates neither tap nor menu/rail action skips it.
    await tap(Vector2(1190,342))
    await tap(Vector2(80,342))
    await tap(Vector2(80,48))
    assert(s.source_calendar_blocked() and game.speed==old_speed and ui.screen.is_empty())
    var frozen:String=JSON.stringify(s.save_state())
    var debt:float=game.accumulator
    game.speed=16;game._advance_simulation(60.0)
    assert(JSON.stringify(s.save_state())==frozen and game.accumulator==debt)
    s.source_calendar.event.wait_updates=120
    # Cancelled field gesture and emulated mouse echo cannot acknowledge.
    await touch(Vector2(600,300),true)
    await touch(Vector2(600,300),false,true)
    assert(s.source_calendar_blocked())
    var echo:=InputEventMouseButton.new();echo.device=-1;echo.button_index=MOUSE_BUTTON_LEFT;echo.pressed=true;echo.position=Vector2(600,300)
    root.push_input(echo,true);echo.pressed=false;root.push_input(echo,true)
    await process_frame
    assert(s.source_calendar_blocked())
    # Mid-presentation JSON preserves variant/counter/waits; voice restarts once.
    var saved:Dictionary=JSON.parse_string(JSON.stringify(s.save_state()))
    assert(s.load_state(saved))
    ui._process_calendar()
    assert(s.source_calendar_blocked() and int(s.source_calendar.event.wait_updates)==120)
    var count:int=sound.source_history.size()
    ui._process_calendar()
    assert(sound.source_history.size()==count)
    await tap(Vector2(1190,422)) # Original mask0x60 accepts cancel too.
    assert(not s.source_calendar_blocked() and s.popularity==100 and ui.screen.is_empty())
    assert(sound.source_history[-2]==-1 and sound.source_history[-1]==1)
    # Festival picture/voice and confirm, without popularity bonus.
    s.month_count=7;s._days_completed_this_month=2;s.minute_of_day=1438
    s.source_calendar.last_midnight=-1
    s._advance_minute_of_day();ui._process_calendar()
    assert(s.source_calendar.event.kind=="festival" and sound.source_history[-1]==58)
    var popularity:int=s.popularity
    s.source_calendar.event.wait_updates=120;ui._process_calendar()
    await tap(Vector2(1190,342))
    assert(not s.source_calendar_blocked() and int(s.source_calendar.festival)==1 and s.popularity==popularity)
    ui._process_calendar()
    for child in ui.touch_controls.get_children():
        if child is Button:assert(not child.disabled)
    print("CALENDAR_UI_PASS original sprites/sounds, early skip/menu rejection, 16x pause/debt, cancelled gesture/mouse echo, saved presentation, cancel/confirm and control restoration")
    sound.play_source(-1)
    ui.hits.clear();ui._active_action=Callable();ui._pending_taps.clear()
    game.free();game=null;ui=null
    await process_frame
    quit()
