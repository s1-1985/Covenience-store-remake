extends "res://scripts/phone_ui.gd"
# CONFIRMED_VISUAL: owner's 26 screenshots, 2026-11-18. Coordinates are
# native 320x240; only the two external touch rails are remake presentation.
const ORIGIN := Vector2(160, 0)
const ZOOM := 3.0
const PINK := Color("f4b9f5")
const BLUE := Color("80ddf2")
const DARK := Color("49483f")
var store_camera
var surface: Node2D
var glyphs: Dictionary
var portrait_codes: Dictionary
var profiles: Dictionary
var fixture_info: Dictionary
var font_pages: Array[Texture2D] = []
var hits: Array = []
var panel_rects: Array[Rect2] = []
var screen := ""
var history: Array[String] = []
var _history_states: Array[Dictionary] = []
var _restoring_menu := false
var _pending_taps: Dictionary = {}
var _dismiss_request: Dictionary = {}
var _sale_request: Dictionary = {}
var _renovation_request: Dictionary = {}
var _renovation_permits: Array[String] = []
var _close_target := "interior"
var _close_store_uid := -1
var _permit_selected: Array[String] = []
var _permit_request: Dictionary = {}
var _price_draft: Dictionary = {}
var _price_before: Dictionary = {}
var _price_individual_before: Dictionary = {}
var _price_uid := -1
var _price_name := ""
var _ad_draft: Array = []
var _ad_before: Array = []
var _rival_target := ""
var _rival_request: Dictionary = {}
var _rival_error := ""
var rival_actions: Dictionary = {}
var _calendar_key := ""
var _calendar_notice_source = null
var _calendar_touches: Dictionary = {}
var _calendar_mouse_down := false
var selection := 0
var choice := 0
var page := 0
var slot := 0
var person_index := 0
var _hiring_candidates: Array[String] = []
var transfer_store := 0
var transfer_slot := 0
var floor_mode := ""
var close_hours := ""
var _ready_ui := false
var _paint_age := 0.0
var _map_zoom_initialized := false
var _cursor := Vector2(-100, -100)
var _selected_rect := Rect2()
var _active_action := Callable()
var _company := "HUMANストア"
var readable_font: Font = preload("res://fonts/ConveniJP.ttf")
# Owner-authorized mobile gesture; the simulation's existing swap is unchanged.
var _staff_drag: Dictionary = {}
var _staff_drag_position := Vector2.ZERO
var _staff_drag_moved := false
var _staff_drag_pointer := -2
var _native_pointer := -1
var _claimed_touches: Dictionary = {}


func setup(owner_main) -> void:
    rival_actions=JSON.parse_string(FileAccess.get_file_as_string("res://data/source_rival_actions.json"))
    glyphs = JSON.parse_string(FileAccess.get_file_as_string("res://assets/ps1/ui/glyphs.json"))
    profiles = JSON.parse_string(FileAccess.get_file_as_string("res://assets/ps1/ui/profiles.json"))
    portrait_codes = JSON.parse_string(FileAccess.get_file_as_string("res://assets/ps1/ui/portraits.json"))
    fixture_info = JSON.parse_string(FileAccess.get_file_as_string("res://assets/ps1/ui/fixture-info.json"))
    for i in 2:
        font_pages.append(load("res://assets/ps1/ui/font_%d.png" % i))
    super.setup(owner_main)
    surface = Node2D.new()
    surface.name = "PS1Presentation"
    surface.position = ORIGIN
    surface.scale = Vector2.ONE * ZOOM
    surface.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
    surface.texture_repeat = CanvasItem.TEXTURE_REPEAT_ENABLED
    surface.draw.connect(func(): _draw_screen(surface))
    main.get_node("UI").add_child(surface)
    store_camera = preload("res://scripts/store_camera.gd").new()
    main.add_child(store_camera)
    store_camera.setup(main, self)
    _ready_ui = true
    main.store_view.fixture_selected.connect(_fixture_action)
    refresh()
    call_deferred("_resume_renovation_edit")

func _build_background() -> void:
    var background: ColorRect = main.get_node("Background")
    background.color = Color("2f7d68")
    var field := TextureRect.new()
    field.name = "PS1Field"
    field.texture = load("res://assets/ps1/ui/field.png")
    field.position = ORIGIN
    field.size = Vector2(320, 240)
    field.scale = Vector2.ONE * ZOOM
    field.stretch_mode = TextureRect.STRETCH_TILE
    field.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
    field.mouse_filter = Control.MOUSE_FILTER_IGNORE
    background.get_parent().add_child(field)
    background.get_parent().move_child(field, background.get_index() + 1)

func layout_screen() -> void:
    super.layout_screen()
    if store_camera != null:
        store_camera.layout()
    main.town_view.position = Vector2(160, 96)
    main.town_view.view_size = Vector2(960, 624)
    if not _map_zoom_initialized:
        main.town_view.map_tile_pixels = 24.0 # original 8-pixel tiles at 3x
        main.town_view.center_on_store()
        _map_zoom_initialized = true
    hud.hide()
    bottom_bar.hide()
    menu.hide()
    # Legacy panels still serve unreferenced acquisition/stock flows.
    if _ready_ui:
        surface.queue_redraw()

func refresh() -> void:
    if not _ready_ui:
        return
    super.refresh()
    hud.hide()
    bottom_bar.hide()
    menu.hide()
    if command_open and screen.is_empty():
        open_window("root" if main.town_view.visible else "store")
    if not screen.is_empty():
        window.visible = true # compatibility with existing touch controls
        window.modulate.a = 0.0
        window.mouse_filter = Control.MOUSE_FILTER_IGNORE
        window.position = Vector2(-5000, -5000)
    surface.queue_redraw()

func _process(delta: float) -> void:
    if _ready_ui and _process_calendar(): return
    super._process(delta)
    if not _ready_ui:
        return
    if command_open and screen.is_empty():
        open_window("root" if main.town_view.visible else "store")
    _paint_age += delta
    if _paint_age >= 0.1:
        _paint_age = 0
        surface.queue_redraw()

# Original special screens use120 draw waits, then audio idle / mask0x60.
# REMAKE_BALANCED_DEFAULT: map source waits to rendered UI updates and field
# taps to mask0x60. This presentation adapter never runs accelerated
# accelerated simulation tick. Reload restarts the source voice, keeps waits.
func _process_calendar() -> bool:
    var sim = main.simulation
    var blocked: bool = sim.source_calendar_blocked()
    for child in touch_controls.get_children():
        if child is Button:
            child.disabled=blocked and (not child.text.begins_with("○") and not child.text.begins_with("×") or int(sim.source_calendar.event.get("wait_updates",0))<120)
    if not blocked:
        _calendar_key=""
        _calendar_touches.clear()
        _calendar_mouse_down=false
        return false
    var event: Dictionary = sim.source_calendar.event
    var key := "%s:%d" % [event.kind,int(event.day)]
    if key!=_calendar_key or _calendar_notice_source!=sim.notifications:
        _calendar_key=key
        _calendar_notice_source=sim.notifications
        _pending_taps.clear()
        _cancel_staff_drag()
        SoundManager.play_source(58 if event.kind=="festival" else 59)
    notice.visible=false
    _source_notice_visible=false
    sim.advance_source_calendar_presentation(1,SoundManager.source_voice_active())
    surface.queue_redraw()
    return true

func _ack_calendar() -> bool:
    var sim = main.simulation
    if sim.source_calendar_blocked() and int(sim.source_calendar.event.wait_updates)>=120:
        SoundManager.play_source(-1)
        SoundManager.play_source(1) # Original65000 acknowledgement wrapper.
        sim.finish_source_calendar_event()
        _calendar_key=""
        _calendar_touches.clear()
        surface.queue_redraw()
    return true

func _calendar_input(event: InputEvent) -> void:
    var area := Rect2(160,0,960,720)
    if event is InputEventKey:
        if event.pressed and not event.echo and (event.is_action_pressed("ui_accept") or event.is_action_pressed("ui_cancel")):_ack_calendar()
    elif event is InputEventScreenTouch:
        if event.pressed:
            _calendar_touches[event.index]=area.has_point(event.position)
        else:
            var allowed: bool = bool(_calendar_touches.get(event.index,false)) and not event.canceled and area.has_point(event.position)
            _calendar_touches.erase(event.index)
            if allowed:_ack_calendar()
    elif event is InputEventMouseButton and event.button_index==MOUSE_BUTTON_LEFT:
        if event.device == -1:
            get_viewport().set_input_as_handled()
            return
        if event.pressed:_calendar_mouse_down=area.has_point(event.position)
        else:
            if _calendar_mouse_down and area.has_point(event.position):_ack_calendar()
            _calendar_mouse_down=false
    get_viewport().set_input_as_handled()

func _draw_calendar(event: Dictionary) -> void:
    if event.kind=="festival":
        _paper(Rect2(48,48,224,64))
        surface.draw_texture_rect(_texture("res://assets/ps1/ui/calendar_festival.png"),Rect2(48,56,32,32),false)
        _ink(Vector2(80,64),"今日は夜にお祭りがあります。")
    else:
        var variant := int(event.variant)
        surface.draw_texture_rect_region(_texture("res://assets/ps1/ui/calendar_idols.png"),Rect2(8,48,120 if variant==0 else 96,144),Rect2(0 if variant==0 else 120,0,120 if variant==0 else 96,144))
        _paper(Rect2(80,96,240,64))
        var lines := ["%5d万人目の来客をきねんして、" % int(event.units),"アイドルを一日オーナーに","よびました。"]
        var y := 112
        for text in lines:
            var line := ""
            for ch in text:
                if _text_width(line+ch)>208:
                    _ink(Vector2(96,y),line)
                    y+=12
                    line=""
                line+=ch
            if not line.is_empty():
                _ink(Vector2(96,y),line)
                y+=12

func open_window(id: String) -> void:
    if main.simulation != null and main.simulation.source_calendar_blocked(): return
    if not _ready_ui:
        return
    _cancel_staff_drag()
    if id == "stock" or id == "town":
        screen = ""
        window.modulate.a = 1.0
        window.mouse_filter = Control.MOUSE_FILTER_STOP
        super.open_window(id)
        return
    if main.selecting_site:
        return
    if id == "advertising" and not _restoring_menu:
        _ad_before = main.simulation.source_promotions.keys()
        _ad_draft = _ad_before.duplicate()
    if id == "prices" and screen not in ["stock_prices","price_confirm"] and not _restoring_menu:
        _price_before = main.simulation.source_price_settings()
        _price_draft = _price_before.duplicate()
        _price_uid = main.simulation._store_uid
        _price_name = main.simulation.store_name
    if id == "stock_prices" and not _restoring_menu:
        _price_individual_before = _price_draft.duplicate()
    if id == "renovation" and not _restoring_menu: _renovation_permits.clear()
    if id == "permits" and screen != "permit_confirm" and not _restoring_menu:
        _permit_selected.clear()
        _permit_request.clear()
    if id == "candidates" and screen != "candidates" and not _restoring_menu:
        # Sampling consumes the gameplay RNG. Do it once on entry, never
        # from the draw callback, hover, or the decision handler.
        _hiring_candidates = main.simulation.source_hiring_candidates()
        for index in 3:
            if _person_id(main.simulation.staff,index).is_empty():
                slot = index
                break
    if id == "interior" and not floor_mode.is_empty():
        screen = "interior"
    else:
        if not screen.is_empty() and screen != id:
            history.append(screen)
            _history_states.append({"page":page,"selection":selection,"choice":choice,"slot":slot,"pool":_hiring_candidates.duplicate()})
        screen = id
    command_open = false
    window_id = "interior" if id in ["interior", "fixtures", "floor_material", "close_shop"] else id
    window.visible = true
    window.modulate.a = 0.0
    window.mouse_filter = Control.MOUSE_FILTER_IGNORE
    window.position = Vector2(-5000, -5000)
    selection = 0
    choice = 0
    page = 0
    _updaters.clear()
    main.store_view.editing = window_id == "interior" and not floor_mode.is_empty()
    surface.queue_redraw()

func close_window() -> void:
    if not _ready_ui:
        return
    if not main.simulation.renovation_session.is_empty():
        open_window("renovation_finish")
        return
    if not close_hours.is_empty():
        var sim = main.simulation
        var home: int = sim.active_store
        for index in sim.store_count():
            if int(sim.store_field(index,"_store_uid")) == _close_store_uid:
                sim._switch_store(index)
                sim.try_set_business_hours(close_hours)
                sim._switch_store(home)
                break
        close_hours = ""
        _close_store_uid = -1
    _cancel_staff_drag()
    screen = ""
    history.clear()
    _history_states.clear()
    _pending_taps.clear()
    floor_mode = ""
    command_open = false
    main.store_view.editing = false
    main.store_view.selected_fixture_id = ""
    window_id = ""
    window.visible = false
    window.modulate.a = 1.0
    _updaters.clear()
    surface.queue_redraw()

func handle_command() -> void:
    if main.simulation.source_calendar_blocked(): return
    if main.selecting_site:
        return
    if not floor_mode.is_empty():
        floor_mode = ""
        open_window("interior")
    elif not screen.is_empty():
        close_window()
    else:
        open_window("root" if main.town_view.visible else "store")

func handle_cancel() -> bool:
    if main.simulation.source_calendar_blocked(): return _ack_calendar()
    if screen.is_empty():
        return false
    if screen == "stock_prices": _price_draft = _price_individual_before.duplicate()
    if screen == "interior" and floor_mode.is_empty() and not main.simulation.renovation_session.is_empty():
        open_window("renovation_finish")
        return true
    if not floor_mode.is_empty():
        floor_mode = ""
        main.store_view.selected_fixture_id = ""
        open_window("interior")
    elif not history.is_empty():
        var target: String = history.pop_back()
        var state: Dictionary = _history_states.pop_back() if not _history_states.is_empty() else {}
        screen = ""
        _restoring_menu = true
        open_window(target)
        _restoring_menu = false
        page = state.get("page",0)
        selection = state.get("selection",0)
        choice = state.get("choice",0)
        slot = state.get("slot",0)
        _hiring_candidates.assign(state.get("pool",[]))
        if screen == "candidates" and not _person_id(main.simulation.staff,slot).is_empty():
            for index in 3:
                if _person_id(main.simulation.staff,index).is_empty():
                    slot = index
                    break
        surface.queue_redraw()
    else:
        close_window()
    return true

func handle_start() -> void:
    if main.simulation.source_calendar_blocked(): return
    if not screen.is_empty():
        close_window()
    else:
        main._on_pause_pressed()
    refresh()

func handle_accept() -> bool:
    if main.simulation.source_calendar_blocked(): return _ack_calendar()
    if screen in ["candidates", "dismiss"]:
        _decide_personnel()
        return true
    if main.selecting_site and _active_action.is_valid():
        _active_action.call()
        return true
    if screen.is_empty():
        return false
    if _active_action.is_valid():
        var action := _active_action
        SoundManager.play_sfx("select")
        action.call()
        surface.queue_redraw()
    return true

func handle_shoulder(direction: int) -> bool:
    if main.simulation.source_calendar_blocked(): return true
    if not main.simulation.renovation_session.is_empty() and not screen in ["fixtures","floor_material"]: return true
    if main.selecting_site:
        if not main.site_buy_button.disabled: main._on_buy_site_pressed()
        return true
    if screen in ["fixtures", "candidates", "stock_prices", "facilities"]:
        page = maxi(0, page + direction)
        choice = 0
        surface.queue_redraw()
        return true
    if screen in ["hours", "shop", "shop_graph", "survey", "transfer", "renovation", "sell_store"]:
        if screen == "hours":
            choice = posmod(choice + direction, main.simulation.business_hours_presets().size())
        elif screen == "transfer":
            transfer_store = posmod(transfer_store + direction, main.simulation.store_count())
        elif screen == "renovation":
            choice = posmod(choice + direction, main.simulation.store_types().size())
        else:
            var count: int = main.simulation.store_count()
            if count > 1:
                var was_town: bool = main.town_view.visible
                main.select_store(posmod(main.simulation.active_store + direction, count))
                main.town_view.visible = was_town
                main.store_view.visible = not was_town
                layout_screen()
        surface.queue_redraw()
        return true
    return false

func _cancel_staff_drag() -> void:
    _staff_drag.clear()
    _staff_drag_moved = false
    _staff_drag_pointer = -2

func _staff_at(p: Vector2) -> Dictionary:
    if screen != "transfer":
        return {}
    for side in 2:
        var x := 18 if side == 0 else 250
        for i in 3:
            if Rect2(x,58+i*48,46,38).has_point(p):
                return {"side": side, "slot": i, "store": main.simulation.active_store if side == 0 else transfer_store}
    return {}

func _commit_transfer(from_store: int, from_slot: int, to_store: int, to_slot: int) -> bool:
    var changed: bool = main.simulation.try_transfer_source_staff(from_store,"staff-%d" % (from_slot+1),to_store,"staff-%d" % (to_slot+1))
    if changed:
        SoundManager.play_sfx("select")
        show_notice("異動しました")
    return changed

func _input(event: InputEvent) -> void:
    if _ready_ui and main.simulation.source_calendar_blocked():
        _calendar_input(event)
        return
    if not _ready_ui or not main.visible:
        _cancel_staff_drag()
        return
    var pointer := -2
    var pressed := false
    var released := false
    var moved := false
    var position := Vector2.ZERO
    var canceled := false
    if event is InputEventScreenTouch:
        pointer = event.index
        pressed = event.pressed
        released = not event.pressed
        canceled = event.canceled
        position = event.position
        if pressed and _native_pointer == -1:
            _native_pointer = pointer
    elif event is InputEventScreenDrag:
        pointer = event.index
        moved = true
        position = event.position
    elif event is InputEventMouseButton and event.button_index == MOUSE_BUTTON_LEFT:
        if _native_pointer != -1:
            return
        pointer = -1
        pressed = event.pressed
        released = not event.pressed
        position = event.position
    elif event is InputEventMouseMotion:
        if _native_pointer != -1:
            return
        pointer = -1
        moved = true
        position = event.position
    else:
        return
    if event is InputEventMouseButton and event.device == -1:
        return
    var p: Vector2 = (position - ORIGIN) / ZOOM
    # The rails are real GUI buttons on a higher CanvasLayer. Never consume
    # their press/release in the painted-menu input handler.
    if position.x < PLAY_LEFT or position.x >= PLAY_RIGHT:
        if released and pointer == _native_pointer: _native_pointer = -1
        if _staff_drag.is_empty():
            return
    if notice.visible:
        _cancel_staff_drag()
        if released and pointer == _native_pointer: _native_pointer = -1
        return # the notice Control owns dismissal, including native touch.
    if not _staff_drag.is_empty():
        # Consume a second finger too; it cannot select a different member.
        get_viewport().set_input_as_handled()
        if pointer != _staff_drag_pointer:
            return
        _staff_drag_position = p
        # REMAKE_BALANCED_DEFAULT: mobile drag threshold, owner-authorized.
        if moved and p.distance_to(_staff_drag.start) > 4.0:
            _staff_drag_moved = true
        if released or canceled:
            var from := _staff_drag.duplicate()
            var target := _staff_at(p)
            var should_move := _staff_drag_moved and not canceled
            _cancel_staff_drag()
            if pointer == _native_pointer: _native_pointer = -1
            if should_move and not target.is_empty():
                _commit_transfer(from.store,from.slot,target.store,target.slot)
        surface.queue_redraw()
        return
    if released:
        var pending: Dictionary = _pending_taps.get(pointer,{})
        _pending_taps.erase(pointer)
        if not pending.is_empty():
            get_viewport().set_input_as_handled()
            if not canceled and pending.screen == screen and pending.rect.has_point(p):
                SoundManager.play_sfx("select")
                pending.action.call()
                surface.queue_redraw()
        if _claimed_touches.has(pointer):
            _claimed_touches.erase(pointer)
            get_viewport().set_input_as_handled()
        if pointer == _native_pointer: _native_pointer = -1
        # TownView acts on RELEASE, so consuming only the menu's press lets
        # the same gesture select a building behind the menu.
        if not screen.is_empty() and floor_mode.is_empty():
            get_viewport().set_input_as_handled()
        return
    if not screen.is_empty() and pointer >= 0 and pointer != _native_pointer:
        get_viewport().set_input_as_handled()
        return
    if moved:
        # Hover is a mouse convenience; finger movement must not select rows.
        if pointer == -1:
            for h in hits:
                if h.rect.has_point(p):
                    selection = h.index
                    if screen in ["fixtures", "advertising", "facilities", "renovation"] and h.index < 100:
                        choice = h.index
                    surface.queue_redraw()
                    break
        if not screen.is_empty() and floor_mode.is_empty():
            get_viewport().set_input_as_handled()
        return
    if not pressed or canceled:
        return
    var member := _staff_at(p)
    if not member.is_empty():
        if member.side == 0: slot = member.slot
        else: transfer_slot = member.slot
        # Empty destinations are selectable; only occupied slots start drags.
        var roster = main.simulation.store_field(member.store,"staff")
        if not _person_id(roster,member.slot).is_empty():
            _staff_drag = member.duplicate()
            _staff_drag.start = p
            _staff_drag_pointer = pointer
            _staff_drag_position = p
        get_viewport().set_input_as_handled()
        surface.queue_redraw()
        return
    for i in range(hits.size() - 1, -1, -1):
        var h: Dictionary = hits[i]
        if h.rect.has_point(p):
            selection = h.index
            var action: Callable = h.action
            _claimed_touches[pointer] = true
            get_viewport().set_input_as_handled()
            # REMAKE_BALANCED_DEFAULT: native menu commits on release inside
            # the same item, so sliding off cancels without changing game state.
            _pending_taps[pointer] = {"screen":screen,"rect":h.rect,"action":action}
            surface.queue_redraw()
            return
    # A modal blocks the map everywhere, not only inside its painted paper.
    # Editing modes intentionally release the uncovered shop floor.
    if not screen.is_empty() and floor_mode.is_empty():
        get_viewport().set_input_as_handled()
    else:
        for rect in panel_rects:
            if rect.has_point(p):
                get_viewport().set_input_as_handled()
                return

func _fixture_action(id: String) -> void:
    if floor_mode == "sell" and not id.is_empty():
        main._on_sell_fixture_pressed()
        main.fixture_info_panel.hide()

# Drawing helpers. Original bitmap glyphs have a 12x15 image cell. ASCII
# advances eight pixels, Japanese twelve, as measured in the supplied HUD.
func _text_width(text: String) -> int:
    var width := 0
    for ch in text:
        width += 8 if ch.unicode_at(0) < 128 or ch == "¥" else 12
    return width

func _ink(at: Vector2, text: String, tint: Color = DARK) -> void:
    # Owner-authorized readable lettering. Rasterize at final phone size,
    # keeping the original 8/12-pixel advances and existing panel positions.
    surface.draw_set_transform(at, 0, Vector2.ONE / ZOOM)
    var x := 0.0
    for ch in text:
        var advance := (8 if ch.unicode_at(0) < 128 or ch == "¥" else 12) * ZOOM
        var width := readable_font.get_string_size(ch,HORIZONTAL_ALIGNMENT_LEFT,-1,36).x
        surface.draw_string(readable_font,Vector2(x+(advance-width)/2,36),ch,HORIZONTAL_ALIGNMENT_LEFT,-1,36,tint)
        x += advance
    surface.draw_set_transform(Vector2.ZERO)

func _center(y: float, text: String, left: float = 0, width: float = 320) -> void:
    _ink(Vector2(left + (width - _text_width(text)) / 2, y), text)

func _paper(rect: Rect2) -> void:
    surface.draw_rect(Rect2(rect.position + Vector2(3, 3), rect.size), Color("282923"))
    surface.draw_rect(rect, Color("9c8354"))
    surface.draw_rect(rect.grow(-1), Color("c6b77c"))
    surface.draw_texture_rect(_texture("res://assets/ps1/ui/paper.png"), rect.grow(-2), true)
    panel_rects.append(rect)

func _region(rect: Rect2, action: Callable, index: int = -1) -> void:
    if index < 0:
        index = hits.size()
    hits.append({"rect": rect, "action": action, "index": index})
    if index == selection:
        _selected_rect = rect
        _active_action = action

func _option(rect: Rect2, text: String, action: Callable, index: int = -1) -> void:
    if index < 0:
        index = hits.size()
    if index == selection:
        surface.draw_rect(rect, PINK)
    _ink(rect.position + Vector2(2, 0), text)
    _region(rect, action, index)

func _list(items: Array, rect := Rect2(45, 56, 86, 0)) -> void:
    # REMAKE_BALANCED_DEFAULT: owner-authorized phone-sized rows, same PS hierarchy.
    rect.size.y = items.size() * 20 + 6
    _paper(rect)
    for i in items.size():
        var item: Array = items[i]
        var id := str(item[1])
        _option(Rect2(rect.position + Vector2(3, 3 + i * 20), Vector2(rect.size.x - 6, 20)), str(item[0]), func(): _navigate(id), i)

func _navigate(id: String) -> void:
    match id:
        "show_store", "show_town":
            close_window()
            building_card.hide()
            main.fixture_info_panel.hide()
            customer_card.hide()
            main.town_view.visible = id == "show_town"
            main.store_view.visible = id == "show_store"
            layout_screen()
            main._refresh_ui()
        "enter":
            close_window()
            if main.town_view.visible:
                main._on_show_town_map_pressed()
            open_window("store")
            layout_screen()
        "interior":
            floor_mode = ""
            _close_target = "interior"
            open_window("close_shop" if main.simulation.is_open_now() else "interior")
        "renovation":
            _close_target = "renovation"
            open_window("close_shop" if main.simulation.is_open_now() else "renovation")
        "new_store":
            close_window()
            main.start_new_store()
        "finish": close_window()
        "move", "swap", "sell":
            floor_mode = id
            screen = "interior"
            window_id = "interior"
            main.store_view.editing = true
            main.store_view.edit_mode = "swap" if id == "swap" else "move"
            main.store_view.selected_fixture_id = ""
        _: open_window(id)

func _draw_screen(_target: Node2D) -> void:
    hits.clear()
    panel_rects.clear()
    _active_action = Callable()
    _selected_rect = Rect2()
    if main.simulation == null:
        return
    var s = main.simulation
    surface.draw_texture_rect(_texture("res://assets/ps1/ui/hud.png"), Rect2(0, 8, 160, 24), false)
    surface.draw_texture_rect(_texture("res://assets/ps1/ui/hud.png"), Rect2(160, 8, 160, 24), false)
    var snap: Dictionary = s.snapshot()
    var month: int = s.month_count+int(bool(s.source_calendar.boundary.get("closing",false)))
    var day: int = 1 if bool(s.source_calendar.boundary.get("closing",false)) else int(snap["days_completed_this_month"])+1
    _ink(Vector2(8, 16), "%02d年目%02d月%02d日[%s ] %s¥%s" % [month / 12 + 1, month % 12 + 1, day, s.weather_display_label(), s.clock_text(), main._format_integer(s.economy.cash_yen)])
    if s.source_calendar_blocked():
        _draw_calendar(s.source_calendar.event)
        return
    if main.selecting_site:
        _site_selection()
        return
    match screen:
        "rival_actions": _rival_actions()
        "rival_details": _rival_details()
        "rival_confirm": _rival_confirmation()
        "view": _list([["店内へ", "show_store"], ["町へ", "show_town"], ["全店舗一覧", "stores"]], Rect2(70,64,140,0))
        "stores": _store_overview()
        "root": _list([["店舗", "enter"], ["不動産", "realestate"], ["販促", "promotion"], ["調査", "research"], ["システム", "system"]], Rect2(45,56,70,0))
        "realestate": _list([["新装開店", "new_store"], ["店舗売却", "sell_store"]], Rect2(45,56,74,0))
        "promotion": _list([["宣伝をする", "advertising"], ["誘致をする", "facilities"]], Rect2(45,56,86,0))
        "research": _list([["店舗別詳細", "shop"], ["店舗別グラフ", "shop_graph"], ["全店収支グラフ", "results"], ["アンケート", "survey"]], Rect2(45,56,102,0))
        "store": _store_panel()
        "interior":
            if floor_mode.is_empty():
                _list([["配置", "fixtures"], ["移動", "move"], ["入れ替え", "swap"], ["売却", "sell"], ["床材", "floor_material"], ["終了", "finish"]], Rect2(192,64,118,0))
            else:
                _paper(Rect2(236,54,70,22))
                _center(58, {"move":"移動", "swap":"入れ替え", "sell":"売却", "place":"配置"}.get(floor_mode,"配置"),236,70)
        "fixtures": _fixtures()
        "floor_material": _floor_materials()
        "policy": _list([["営業時間", "hours"], ["商品価格", "prices"], ["販売許可", "permits"]], Rect2(192,64,118,0))
        "hours": _hours()
        "prices": _prices()
        "price_confirm": _price_confirmation()
        "stock_prices": _individual_prices()
        "permits": _permits()
        "permit_confirm": _permit_confirmation()
        "advertising": _advertising()
        "facilities": _facilities()
        "staff": _list([["店員の雇用", "candidates"], ["店員の解雇", "dismiss"], ["店員の異動", "transfer"]], Rect2(45,56,86,0))
        "candidates", "dismiss": _personnel()
        "dismiss_confirm": _dismiss_confirmation()
        "transfer": _transfer()
        "renovation": _renovation()
        "renovation_confirm": _renovation_confirmation()
        "renovation_finish": _renovation_finish()
        "renovation_permits": _renovation_permit_panel()
        "shop": _shop_details()
        "shop_graph", "results": _graph()
        "survey": _survey()
        "system": _system()
        "close_shop": _close_shop()
        "sell_store": _sell_store_panel()
        "sell_store_confirm": _sell_store_confirmation()
    if not _staff_drag.is_empty() and _staff_drag_moved:
        var roster = s.store_field(_staff_drag.store,"staff")
        _face(_person_id(roster,_staff_drag.slot),Rect2(_staff_drag_position-Vector2(23,19),Vector2(46,38)))
        var target := _staff_at(_staff_drag_position)
        if not target.is_empty():
            surface.draw_rect(Rect2(18 if target.side == 0 else 250,58+target.slot*48,46,38),PINK,false,1.0)
    if not _selected_rect.size.is_zero_approx() and floor_mode.is_empty():
        surface.draw_texture_rect(_texture("res://assets/ps1/ui/cursor.png"), Rect2(_selected_rect.end - Vector2(10,5), Vector2(16,16)), false)

func _money(value: int) -> String:
    return "¥" + main._format_integer(value)

func _store_panel() -> void:
    var s = main.simulation
    _paper(Rect2(192,37,118,168))
    _ink(Vector2(196,42), _company)
    _ink(Vector2(204,58), s.store_name)
    for i in 3:
        var id: String = ["tobacco","alcohol","medicine"][i]
        if s.has_permit(id):
            surface.draw_texture_rect(_texture(UI_ICON_DIR + PERMIT_ICONS.get(id,"") + ".png"), Rect2(260+i*14,56,14,14), false)
    _ink(Vector2(240,74), _money(s.store_sales_today_yen()))
    var hours: String = str(s._business_hours_preset(s.business_hours_id).get("label","24時間"))
    if _text_width(hours) > 108: hours = hours.replace("AM", "").replace("PM", "")
    _ink(Vector2(196,90), hours)
    _ink(Vector2(196,122),"評価")
    _stars(Vector2(230,122), s.star_rating)
    for i in 4:
        var target: String = ["interior","policy","staff","renovation"][i]
        _option(Rect2(195,137+i*17,112,16), ["内 装","方 針","店 員","改 築"][i],func(): _navigate(target),i)

func _stars(at: Vector2, count: int) -> void:
    for i in clampi(count,0,5):
        _ink(at + Vector2(i*12,0), "★", Color("ff2828"))

func _footer(y: float = 190) -> void:
    _region(Rect2(112,y,110,17),handle_start)
    _center(y,"終了・・・START")

func _icon(rect: Rect2, texture: Texture2D, action: Callable, index: int) -> void:
    surface.draw_rect(rect, Color("96988f"))
    surface.draw_rect(rect.grow(-1),Color("eeeecc"))
    if texture != null:
        surface.draw_texture_rect(texture,rect,false)
    _region(rect,action,index)

func _fixtures() -> void:
    var catalog: Array = main.config["fixture_catalog"].duplicate()
    var order: Array = [35,36,22,23,24]+range(22)+range(25,35)+range(37,53)
    catalog.sort_custom(func(a,b): return order.find(int(fixture_info.get(a["catalog_id"],{}).get("kind",99))) < order.find(int(fixture_info.get(b["catalog_id"],{}).get("kind",99))))
    page = clampi(page,0,maxi(0,(catalog.size()-1)/15))
    var entries: Array = catalog.slice(page*15,page*15+15)
    choice = clampi(choice,0,maxi(0,entries.size()-1))
    _paper(Rect2(44,45,230,166))
    _ink(Vector2(49,49),"設備を選択して下さい")
    if not entries.is_empty():
        var entry: Dictionary = entries[choice]
        var info: Dictionary = fixture_info.get(entry["catalog_id"],{})
        _ink(Vector2(49,65),str(info.get("label",main.tr(str(entry["catalog_id"])))))
        _ink(Vector2(201,49),"収納力 %d" % int(info.get("capacity",0)))
        _ink(Vector2(201,65),"注目度 %d" % int(info.get("attention",0)))
        _ink(Vector2(49,81),"価格" + _money(int(entry["purchase_price_yen"])))
        _ink(Vector2(154,81),"維持費 " + _money(int(info.get("hourly_cost",0) * main.simulation.open_minutes(main.simulation._business_hours_preset(main.simulation.business_hours_id)) / 60)) + "/日")
    for i in entries.size():
        var id := str(entries[i]["catalog_id"])
        var index := i
        _icon(Rect2(60+(i%5)*40,96+(i/5)*40,32,32),_atlas_icon("fixtures",int(fixture_info[id]["kind"])+1,Vector2i(32,32),8),func():
            choice = index
            floor_mode = "place"
            screen = "interior"
            window_id = "interior"
            main.store_view.edit_mode = "move"
            main.store_view.editing = true
            main.store_view.selected_fixture_id = main.NEW_FIXTURE_SELECTION_PREFIX + id, i)
    _region(Rect2(44,195,16,16),func(): handle_shoulder(-1),100)
    _region(Rect2(258,195,16,16),func(): handle_shoulder(1),101)
    _ink(Vector2(45,195),"◁")
    _ink(Vector2(259,195),"▷")

# Clean source tiles only. Codes1..4/6..9/11..14 are runtime stains,
# not selectable interior patterns. This extra entry is a phone UI control.
func _floor_materials() -> void:
    _paper(Rect2(60, 68, 200, 100))
    _ink(Vector2(69, 76), "床材を選択して下さい")
    var atlas: Texture2D = _texture("res://assets/ps1/floor_atlas.png")
    for i in 3:
        var code: int = [0, 5, 10][i]
        var picture := AtlasTexture.new()
        picture.atlas = atlas
        picture.region = Rect2(code * 16, 0, 16, 16)
        _icon(Rect2(80 + i * 64, 105, 32, 32), picture, func():
            if main.simulation.try_set_source_floor(code):
                main.store_view.queue_redraw()
                handle_cancel(), i)
        _ink(Vector2(80 + i * 64, 141), "床材%d" % (i + 1))

# REMAKE_BALANCED_DEFAULT: original3-choice branch in readable paper rows,
# with a separate mobile cost confirmation. Known inspection opens detail only.
func show_source_rival(rival_id: String) -> void:
    if main.simulation.source_calendar_blocked() or not main.simulation.renovation_session.is_empty(): return
    close_window()
    _rival_target=rival_id
    _rival_request={}
    _rival_error=""
    if rival_id.is_empty() or main.simulation._rival_index(rival_id)<0: return
    open_window("rival_details" if main.simulation.rival_investigated(rival_id) else "rival_actions")

func _rival_actions() -> void:
    var sim=main.simulation
    var index:int=sim._rival_index(_rival_target)
    _paper(Rect2(44,54,232,150))
    if index<0:
        _center(80,"店舗がありません")
        _option(Rect2(100,166,120,26),"戻る",close_window,0)
        return
    var entry:Dictionary=sim._rival_guide_entry(_rival_target)
    _center(62,str(entry.get("name","ライバル店")))
    _option(Rect2(56,88,208,26),str(rival_actions.menu[0])+" "+_money(sim.rival_investigation_cost_yen()),func():_confirm_source_rival("investigate"),0)
    var price:int=sim.rival_buyout_price_yen(_rival_target)
    _option(Rect2(56,120,208,26),str(rival_actions.menu[1])+(" "+_money(price) if sim.rival_is_buyable(_rival_target) else "（本店）"),func():_confirm_source_rival("buyout"),1)
    _option(Rect2(56,160,208,26),str(rival_actions.menu[2]),close_window,2)

func _confirm_source_rival(action: String) -> void:
    _rival_request=main.simulation.source_rival_action_quote(_rival_target,action)
    _rival_error=str(_rival_request.reason)
    open_window("rival_confirm")

func _rival_confirmation() -> void:
    _paper(Rect2(32,58,256,142))
    _center(66,str(_rival_request.get("name","ライバル店")))
    var action:String=_rival_request.get("action","")
    _center(88,"調査費 "+_money(int(_rival_request.get("cost_yen",0))) if action=="investigate" else "買収費 "+_money(int(_rival_request.get("cost_yen",0))))
    if not _rival_error.is_empty():
        var line := ""
        var y := 116
        for ch in _rival_error:
            if readable_font.get_string_size(line+ch,HORIZONTAL_ALIGNMENT_LEFT,-1,27).x/ZOOM>236:
                _ink_small(Vector2(42,y),line)
                line=""
                y+=12
            line+=ch
        if not line.is_empty():_ink_small(Vector2(42,y),line)
        _option(Rect2(98,162,124,26),"戻る",handle_cancel,0)
        return
    _center(116,"この内容でよろしいですか？")
    _option(Rect2(50,162,94,26),"いいえ",handle_cancel,0)
    _option(Rect2(176,162,94,26),"はい",_commit_source_rival,1)

func _commit_source_rival() -> void:
    var sim=main.simulation
    var action:String=_rival_request.get("action","")
    var ok:bool=sim.try_investigate_rival(_rival_target,_rival_request) if action=="investigate" else sim.try_buy_out_rival(_rival_target,_rival_request)
    if not ok:
        _rival_error="店舗の状態・資金が変わりました。選び直して下さい"
        surface.queue_redraw()
        return
    close_window()
    if action=="investigate":open_window("rival_details")
    else:
        _rival_target=""
        main.town_view.queue_redraw()
    main._refresh_ui()

func _rival_details() -> void:
    var sim=main.simulation
    _paper(Rect2(44,42,232,178))
    var index:int=sim._rival_index(_rival_target)
    if index<0 or not sim.rival_investigated(_rival_target):
        _center(70,"調査内容が更新されています")
        _option(Rect2(96,182,128,26),"戻る",close_window,0)
        return
    var entry:Dictionary=sim._rival_guide_entry(_rival_target)
    var data:Dictionary=entry.guide_data
    var child=sim._program_rival_simulation(sim._rival_stores[index])
    _center(50,str(entry.name))
    _ink(Vector2(52,74),"営業時間 "+str(data.hours))
    _ink(Vector2(52,96),"評価")
    _stars(Vector2(108,96),int(child.star_rating))
    for i in 2:
        _ink(Vector2(52,120+i*24),["人気","サービス"][i])
        _ink(Vector2(118,120+i*24),str(int(data[["popularity","service"][i]])))
        _ink(Vector2(170,120+i*24),["清掃","警備"][i])
        _ink(Vector2(236,120+i*24),str(int(data[["cleaning","security"][i]])))
    _option(Rect2(96,182,128,26),"戻る",close_window,0)

func _hours() -> void:
    var presets: Array = main.simulation.business_hours_presets()
    if presets.is_empty(): return
    choice = posmod(choice,presets.size())
    var entry: Dictionary = presets[choice]
    _paper(Rect2(44,70,230,70))
    _center(75,"営業方針を決定して下さい")
    _ink(Vector2(49,91),"営業時間")
    _option(Rect2(112,91,155,16),"◁ " + str(entry["label"]) + " ▷",func(): handle_shoulder(1),0)
    _center(107,"これでよろしいですか?")
    _option(Rect2(107,123,36,16),"はい",func():
        main.simulation.try_set_business_hours(str(entry["id"]))
        handle_cancel(),1)
    _option(Rect2(155,123,48,16),"いいえ",handle_cancel,2)

func _price_group_step(direction: int) -> void:
    var ids: Array = _price_draft.keys()
    var values: Array = ids.map(func(id):return _price_draft[id])
    var changed: Array = preload("res://scripts/domain/program_pricing.gd").step(values,direction)
    if changed.is_empty():
        show_notice("上限または下限のため変更できません")
        return
    for i in ids.size(): _price_draft[ids[i]] = changed[i]

func _prices() -> void:
    _paper(Rect2(44,46,232,164))
    _center(54,_price_name+"の商品価格")
    var total := 0
    for value in _price_draft.values(): total += int(value)
    _center(80,"平均設定値 %d%%" % (total/26))
    _option(Rect2(56,105,100,22),"全商品 −1",func():_price_group_step(-1),0)
    _option(Rect2(164,105,100,22),"全商品 ＋1",func():_price_group_step(1),1)
    _option(Rect2(56,137,208,22),"個別に設定",func():open_window("stock_prices"),2)
    _option(Rect2(56,177,80,22),"戻る",handle_cancel,3)
    _option(Rect2(150,177,114,22),"変更を確認",func():open_window("price_confirm"),4)

func _individual_prices() -> void:
    _paper(Rect2(8,40,304,184))
    _center(45,"商品価格を決定して下さい")
    var rows: Array = main.simulation.source_price_preview(_price_draft)
    page = clampi(page,0,maxi(0,(rows.size()-1)/6))
    for i in mini(6,rows.size()-page*6):
        var row: Dictionary = rows[page*6+i]
        var id: String = row.category
        var y := 68+i*20
        _ink(Vector2(16,y),main.tr(id))
        _ink(Vector2(132,y),_money(int(row.unit_yen)))
        _ink(Vector2(203,y),"%d%%" % int(row.setting))
        _option(Rect2(238,y-2,26,20),"−",func():
            if int(_price_draft[id])>0: _price_draft[id]=int(_price_draft[id])-1,i*2)
        _option(Rect2(276,y-2,26,20),"＋",func():
            if int(_price_draft[id])<100: _price_draft[id]=int(_price_draft[id])+1,i*2+1)
    _option(Rect2(16,195,52,22),"戻る",handle_cancel,20)
    _option(Rect2(84,195,30,22),"◁",func():handle_shoulder(-1),21)
    _center(198,"%d/%d" % [page+1,(rows.size()+5)/6],117,50)
    _option(Rect2(174,195,30,22),"▷",func():handle_shoulder(1),22)
    _option(Rect2(218,195,86,22),"設定して戻る",func():
        _price_individual_before = _price_draft.duplicate()
        handle_cancel(),23)

func _price_confirmation() -> void:
    _paper(Rect2(32,64,256,136))
    _center(72,"商品価格を変更しますか?")
    var changed := 0
    for id in _price_draft:
        if int(_price_draft[id])!=int(_price_before.get(id,-1)): changed += 1
    _center(104,_price_name+" 変更%d商品" % changed)
    _center(130,"確定するまで価格は変わりません")
    _option(Rect2(50,168,80,22),"戻る",handle_cancel,0)
    _option(Rect2(170,168,100,22),"変更する",func():
        if main.simulation.try_commit_source_prices(_price_draft,_price_uid,_price_before):
            close_window()
            main._refresh_ui()
        else: show_notice("店舗か設定が変わっています。開き直して下さい"),1)

func _permits() -> void:
    var sim = main.simulation
    _paper(Rect2(32,48,256,160))
    _center(54,"販売許可を申請しますか?")
    for i in 3:
        var id: String = sim.ProgramPermitsScript.IDS[i]
        var held: bool = sim.has_permit(id)
        var allowed: bool = sim._can_acquire_permit(id)
        var selected: bool = _permit_selected.has(id)
        var y := 78+i*24
        surface.draw_texture_rect(_texture(UI_ICON_DIR+PERMIT_ICONS[id]+".png"),Rect2(44,y,16,16),false)
        _ink(Vector2(64,y),sim.ProgramPermitsScript.NAMES[id])
        var text := "申請済み" if held else ("ここでは扱えません" if not allowed else ("選択 " if selected else "□ ")+_money(int(sim._permit_catalog[id]["fee_yen"])))
        _option(Rect2(112,y,164,22),text,func():
            if held: show_notice("申請済みです")
            elif not allowed: show_notice("ここでは扱えません")
            elif _permit_selected.has(id): _permit_selected.erase(id)
            else: _permit_selected.append(id),i)
    var quote: Dictionary = sim.permit_application_quote(_permit_selected)
    _ink(Vector2(44,153),"申請費用 "+_money(int(quote.total_yen)))
    _option(Rect2(44,178,80,22),"戻る",handle_cancel,3)
    _option(Rect2(148,178,128,22),"選択内容を確認",func():
        if not quote.allowed: show_notice(str(quote.reason))
        elif quote.new_permits.is_empty(): show_notice("許可を選択して下さい")
        else:
            _permit_request = {"selected":_permit_selected.duplicate(),"store_uid":quote.store_uid}
            open_window("permit_confirm"),4)

func _permit_confirmation() -> void:
    _paper(Rect2(32,56,256,140))
    _center(64,"この内容で申請しますか?")
    var sim = main.simulation
    var quote: Dictionary = sim.permit_application_quote(_permit_request.get("selected",[]))
    for i in _permit_request.get("selected",[]).size():
        var id: String = _permit_request.selected[i]
        _ink(Vector2(50,88+i*20),sim.ProgramPermitsScript.NAMES[id]+"  "+_money(int(sim._permit_catalog[id]["fee_yen"])))
    _ink(Vector2(50,150),"合計 "+_money(int(quote.total_yen)))
    _option(Rect2(50,170,80,22),"戻る",handle_cancel,0)
    _option(Rect2(170,170,100,22),"申請する",func():
        if sim.try_purchase_permits(_permit_request.get("selected",[]),int(_permit_request.get("store_uid",-1))):
            _permit_selected.clear()
            _permit_request.clear()
            handle_cancel()
            main._refresh_ui()
        else:
            show_notice(str(quote.reason) if not str(quote.reason).is_empty() else "店舗または申請内容を確認して下さい"),1)

func _advertising() -> void:
    var sim = main.simulation
    _paper(Rect2(32,44,256,164))
    _center(50,"宣伝方法（複数選択可）")
    var entries: Array = sim.config.promotions
    choice = clampi(choice,0,entries.size()-1)
    var selected: Dictionary = entries[choice]
    _ink(Vector2(48,70),main.tr(str(selected.promotion_id)))
    _ink(Vector2(180,70),_money(int(selected.cost_yen)))
    var total := 0
    for i in mini(5,entries.size()):
        var id: String = entries[i].promotion_id
        var index := i
        var rect := Rect2(52+i*44,94,32,32)
        _icon(rect,_texture(UI_ICON_DIR+str(PROMOTION_ICONS.get(id,""))+".png"),func():
            choice=index
            if _ad_draft.has(id): _ad_draft.erase(id)
            else: _ad_draft.append(id),i)
        if _ad_draft.has(id):
            surface.draw_rect(rect.grow(2),PINK,false,1.5)
            total+=int(entries[i].cost_yen)
        _ink(Vector2(60+i*44,128),"○" if _ad_draft.has(id) else "−")
    _ink(Vector2(48,146),"費用合計")
    _ink(Vector2(180,146),_money(total))
    _ink_small(Vector2(48,163),"実施時に支払・翌月も継続")
    _option(Rect2(48,181,80,22),"戻る",handle_cancel,10)
    _option(Rect2(150,181,122,22),"設定を確定",func():
        if sim.try_commit_source_promotions(_ad_draft,_ad_before):
            close_window()
            main._refresh_ui()
        else: show_notice("宣伝設定が変わっています。開き直して下さい"),11)

func _facilities() -> void:
    var entries: Array = main.simulation.inducement_facilities()
    _paper(Rect2(51,45,230,120))
    _center(50,"誘致する施設を選択して下さい")
    if entries.is_empty(): return
    page = clampi(page,0,maxi(0,(entries.size()-1)/10))
    choice = clampi(choice,0,mini(10,entries.size()-page*10)-1)
    var selected: Dictionary = entries[page*10+choice]
    _ink(Vector2(56,66),str(selected["name"]))
    _ink(Vector2(148,66),"援助額　"+_money(int(selected["aid_yen"])))
    for i in mini(10,entries.size()-page*10):
        var entry: Dictionary = entries[page*10+i]
        var id := str(entry["id"])
        var index := i
        _icon(Rect2(68+(i%5)*40,80+(i/5)*40,32,32),_texture("res://assets/town/%s.png" % entry["sprite"]),func():
            choice = index
            screen = ""
            start_inducing(id),i)
    _region(Rect2(51,145,16,16),func(): page = maxi(0,page-1),100)
    _region(Rect2(265,145,16,16),func(): page = mini((entries.size()-1)/10,page+1),101)
    _ink(Vector2(52,145),"◁")
    _ink(Vector2(266,145),"▷")

func _person_id(roster, index: int) -> String:
    var key := "staff-%d" % (index+1)
    return str(roster.members[key].candidate_id) if roster.members.has(key) else ""

func _face(id: String, rect: Rect2) -> void:
    var code := -1
    if not id.is_empty():
        var name: String = main.simulation._candidate_figures(id).get("display_name", "")
        code = int(portrait_codes.get(name,-1))
    var portrait: Texture2D = _texture("res://assets/ps1/ui/vacant.png") if code < 0 else _atlas_icon("portraits_%d" % (code/30),code%30,Vector2i(48,40),5)
    surface.draw_texture_rect(portrait,rect,false)

func _bar(at: Vector2, value: int, width: float = 40) -> void:
    surface.draw_rect(Rect2(at,Vector2(width,9)),Color("a00000"))
    for y in 9:
        surface.draw_rect(Rect2(at+Vector2(0,y),Vector2(width*clampi(value,0,100)/100.0,1)),Color(1,0.12+y*0.025,0.12+y*0.015))

func _personnel() -> void:
    var s = main.simulation
    var hiring := screen == "candidates"
    _paper(Rect2(35,38,247,198))
    _ink(Vector2(100,42),s.store_name+"の店員を"+("採用します" if hiring else "解雇して下さい"))
    for i in 3:
        var index := i
        var id := _person_id(s.staff,i)
        _face(id,Rect2(41,41+i*52,46,38))
        if i == slot:
            surface.draw_rect(Rect2(40,40+i*52,48,40),PINK,false,1)
        _region(Rect2(41,41+i*52,46,44),func(): slot = index,10+i)
        _ink_small(Vector2(42,80+i*52),("店長" if i == 0 else "店員%d" % i)+(" 空き" if id.is_empty() else ""))
    var ids: Array = _hiring_candidates if hiring else []
    var id: String = _person_id(s.staff,slot)
    if hiring:
        page = clampi(page,0,maxi(0,ids.size()-1))
        if not ids.is_empty(): id = str(ids[page])
    surface.draw_rect(Rect2(138,55,128,128),BLUE)
    if not id.is_empty():
        var e: Dictionary = s._candidate_figures(id)
        _face(id,Rect2(148,57,46,38))
        _ink(Vector2(196,57),str(e.get("display_name",id)))
        _ink(Vector2(196,73),"%d歳 %s" % [int(e.get("age_years",0)),profiles.get(e.get("display_name",""),{}).get("gender", "")])
        _ink(Vector2(196,89),"未経験" if hiring and not s._unassigned_staff.has(id) else "経験あり")
        _ink(Vector2(196,105),_money(int(e.get("salary_yen_per_day_24h",0)) if hiring else _scheduled_wage(int(s.staff.members["staff-%d" % (slot+1)].salary_yen_per_day_24h),s.business_hours_id))+"/日")
        var keys := ["stamina","academic_background","agility","sociability"]
        for i in 4:
            var value := int(e.get(keys[i],0))
            _ink(Vector2(100,123+i*16),["体力","学歴","敏捷性","社交性"][i])
            _ink(Vector2(146,123+i*16),str(value))
            _bar(Vector2(162,126+i*16),value)
        # The portrait/stat card is information; only an explicit decision
        # button or circle commits hiring/dismissal.
        var enabled: bool = not s.staff.members.has("staff-%d" % (slot+1)) if hiring else true
        if enabled:
            _option(Rect2(160,188,96,17),"採用する" if hiring else "解雇する",_decide_personnel,0)
        else:
            surface.draw_rect(Rect2(160,188,96,17),Color("b9b8ae"))
            _ink(Vector2(162,188),"空き枠なし",Color("66665f"))
            _region(Rect2(160,188,96,17),_decide_personnel,0)
    if hiring:
        _option(Rect2(95,61,18,20),"◁",func(): page = maxi(0,page-1),20)
        _option(Rect2(116,61,18,20),"▷",func(): page = mini(maxi(0,ids.size()-1),page+1),21)
    var occupied := 0
    for i in 3:
        if not _person_id(s.staff,i).is_empty(): occupied += 1
    _ink_small(Vector2(40,194),"配置%d/3人 空き%d" % [occupied,3-occupied])
    if hiring:
        _ink_small(Vector2(40,206),"解雇画面へ" if occupied == 3 else "左の空き枠を選択")
        _region(Rect2(40,204,112,13),func(): open_window("dismiss") if occupied == 3 else null,30)
        _ink_small(Vector2(96,85),"候補%d/%d" % [page+1 if not ids.is_empty() else 0,ids.size()])
    else:
        _option(Rect2(98,62,36,16),"採用へ",func(): open_window("candidates"),30)
    _footer(218)

func _ink_small(at: Vector2, text: String) -> void:
    surface.draw_set_transform(at,0,Vector2.ONE/ZOOM)
    surface.draw_string(readable_font,Vector2(0,27),text,HORIZONTAL_ALIGNMENT_LEFT,-1,27,DARK)
    surface.draw_set_transform(Vector2.ZERO)

func _decide_personnel() -> void:
    var sim = main.simulation
    var key := "staff-%d" % (slot+1)
    if screen == "candidates":
        if sim.staff.members.has(key):
            show_notice("空き枠を選んで下さい。満員なら先に店員を解雇して下さい")
            return
        var ids: Array = _hiring_candidates
        if ids.is_empty():
            show_notice("採用できる候補者がいません")
            return
        var id := str(ids[clampi(page,0,ids.size()-1)])
        var name: String = sim._candidate_figures(id).get("display_name",id)
        if sim.try_hire_candidate(key,id):
            _hiring_candidates.erase(id)
            page = clampi(page,0,maxi(0,_hiring_candidates.size()-1))
            main._refresh_hire_candidate_option()
            show_notice(name+"を採用しました")
        else:
            show_notice("採用条件を確認して下さい")
    elif screen == "dismiss":
        var id := _person_id(sim.staff,slot)
        if id.is_empty():
            show_notice("この枠には店員がいません")
            return
        _dismiss_request = {"slot":slot,"id":id,"name":str(sim._candidate_figures(id).get("display_name",id))}
        open_window("dismiss_confirm")
    surface.queue_redraw()

func _dismiss_confirmation() -> void:
    _paper(Rect2(45,64,232,124))
    _center(70,"店員の解雇")
    _center(94,str(_dismiss_request.get("name","")))
    _center(114,"この店員を解雇しますか")
    _option(Rect2(60,148,96,22),"戻る",handle_cancel,0)
    _option(Rect2(166,148,96,22),"解雇する",_confirm_dismissal,1)

func _confirm_dismissal() -> void:
    if _dismiss_request.is_empty(): return
    var sim = main.simulation
    var index: int = _dismiss_request.slot
    if _person_id(sim.staff,index) != _dismiss_request.id:
        show_notice("店員の配置が変わりました")
        handle_cancel()
        return
    if sim.try_dismiss_source_staff("staff-%d" % (index+1)):
        handle_cancel()
        slot = index
        show_notice("解雇しました。空き枠へ採用できます")
    _dismiss_request.clear()
    surface.queue_redraw()

func _transfer() -> void:
    var s = main.simulation
    _paper(Rect2(12,38,294,182))
    _center(43,"店員を異動させます")
    for side in 2:
        var index: int = s.active_store if side == 0 else transfer_store
        var roster = s.store_field(index,"staff")
        var x: int = 18 if side == 0 else 250
        if side == 0:
            _ink(Vector2(x,43),str(s.store_field(index,"store_name")))
        else:
            _option(Rect2(230,43,16,16),"◁",func():
                transfer_store = posmod(transfer_store-1,s.store_count()),20)
            _ink(Vector2(248,43),str(s.store_field(index,"store_name")))
            _option(Rect2(290,43,16,16),"▷",func():
                transfer_store = posmod(transfer_store+1,s.store_count()),21)
        for i in 3:
            var index_slot := i
            var which := side
            _face(_person_id(roster,i),Rect2(x,58+i*48,46,38))
            _region(Rect2(x,58+i*48,46,38),func():
                if which == 0: slot = index_slot
                else: transfer_slot = index_slot,side*3+i)
        var id := _person_id(roster,slot if side == 0 else transfer_slot)
        if not id.is_empty():
            var e: Dictionary = s._candidate_figures(id)
            _ink(Vector2(66 if side == 0 else 164,60),str(e.get("display_name","")))
            var keys := ["stamina","education","register_skill","replenishment_skill","security_skill","cleaning_skill","service_skill"]
            var member = roster.members["staff-%d" % ((slot if side == 0 else transfer_slot)+1)]
            for i in 7:
                var value := int(e.get(keys[i],0)) if i < 2 else int(member.get(keys[i]))
                _bar(Vector2(90 if side == 0 else 181,93+i*16),value,36)
                _ink(Vector2(74 if side == 0 else 225,90+i*16),str(value))
            _ink(Vector2(65 if side == 0 else 177,204),_money(_scheduled_wage(int(member.salary_yen_per_day_24h),str(s.store_field(index,"business_hours_id"))))+"/日")
    for i in 7: _center(90+i*16,["体力","教育","レジ","補充","警備","清掃","接客"][i])
    _option(Rect2(136,204,40,15),"決定",func():
        _commit_transfer(s.active_store,slot,transfer_store,transfer_slot),31)

func _renovation() -> void:
    var s = main.simulation
    var types: Array = _store_grid_types()
    _paper(Rect2(60,54,198,120))
    _ink(Vector2(65,59),"店舗を選んで下さい")
    if types.is_empty(): return
    choice = clampi(choice,0,types.size()-1)
    _ink(Vector2(170,75),_money(s.renovation_price_yen(str(types[choice]["id"]))))
    for i in mini(6,types.size()):
        var id := str(types[i]["id"])
        _icon(Rect2(96+(i%3)*48,91+(i/3)*42,32,32),_atlas_icon("stores",str(types[i]["icon"]).right(2).to_int()-1,Vector2i(32,32),8),func():
            var quote: Dictionary = s.renovation_quote(id)
            if quote.allowed:
                _renovation_request = quote
                open_window("renovation_confirm")
            else: show_notice(str(quote.reason)),i)

func _renovation_confirmation() -> void:
    var s = main.simulation
    var id: String = _renovation_request.get("to_type","")
    _paper(Rect2(32,64,256,136))
    _center(72,"この店舗へ改築しますか?")
    var entry: Dictionary = s.GuideStartingStoreScript.store_type_entry(s.config,id)
    _center(96,main.store_type_caption(entry))
    var permit_quote: Dictionary = s.permit_application_quote(_renovation_permits)
    var total: int = int(_renovation_request.get("total_yen",0))+int(permit_quote.total_yen)
    _center(120,"費用合計 "+_money(total))
    _option(Rect2(48,140,224,22),"販売許可を選択（%d件）" % _renovation_permits.size(),func():open_window("renovation_permits"),2)
    _option(Rect2(50,168,80,22),"戻る",handle_cancel,0)
    _option(Rect2(170,168,100,22),"改築する",func():
        if s.begin_renovation_edit(id,_renovation_permits,int(_renovation_request.get("store_uid",-1)),str(_renovation_request.get("from_type","")),close_hours):
            main.store_view.selected_fixture_id = ""
            main._store_layout_changed()
            _renovation_request.clear()
            history.clear()
            _history_states.clear()
            open_window("interior")
            main._refresh_ui()
        else:
            var quote: Dictionary = s.renovation_quote(id)
            var reason: String = str(quote.reason)
            if reason.is_empty() and not permit_quote.allowed: reason = str(permit_quote.reason)
            if reason.is_empty() and s.economy.cash_yen < total: reason = "資金が足りません"
            show_notice(reason if not reason.is_empty() else "店舗または改築内容を確認して下さい"),1)

func _renovation_permit_panel() -> void:
    var sim = main.simulation
    _paper(Rect2(32,48,256,160))
    _center(54,"販売許可を選択して下さい")
    for i in 3:
        var id: String = sim.ProgramPermitsScript.IDS[i]
        var held: bool = sim.has_permit(id)
        var allowed: bool = sim._can_acquire_permit(id)
        var selected: bool = _renovation_permits.has(id)
        var y := 78+i*24
        _ink(Vector2(44,y),sim.ProgramPermitsScript.NAMES[id])
        var text := "申請済み" if held else ("ここでは扱えません" if not allowed else ("選択 " if selected else "□ ")+_money(int(sim._permit_catalog[id]["fee_yen"])))
        _option(Rect2(112,y,164,22),text,func():
            if held or not allowed: return
            if _renovation_permits.has(id): _renovation_permits.erase(id)
            else: _renovation_permits.append(id),i)
    _center(153,"追加費用 "+_money(int(sim.permit_application_quote(_renovation_permits).total_yen)))
    _option(Rect2(48,178,224,22),"選択を終える",handle_cancel,3)

func _resume_renovation_edit() -> void:
    var sim = main.simulation
    if sim.renovation_session.is_empty(): return
    for index in sim.store_count():
        if int(sim.store_field(index,"_store_uid")) == int(sim.renovation_session.store_uid):
            main.select_store(index)
            close_hours = str(sim.renovation_session.get("restore_hours",""))
            _close_store_uid = int(sim.renovation_session.store_uid)
            _close_target = "renovation"
            open_window("interior")
            return

func _renovation_finish() -> void:
    _paper(Rect2(32,72,256,132))
    _center(80,"改築の内装を終了しますか?")
    _option(Rect2(48,110,224,22),"内装を続ける",func():
        history.clear()
        _history_states.clear()
        open_window("interior"),0)
    _option(Rect2(48,140,224,22),"改築を確定する",func(): _finish_renovation_edit(true),1)
    _option(Rect2(48,170,224,22),"改築を取り消す",func(): _finish_renovation_edit(false),2)

func _finish_renovation_edit(accept: bool) -> void:
    if not main.simulation.finish_renovation_edit(accept):
        show_notice("編集中の店舗を確認して下さい")
        return
    floor_mode = ""
    main.store_view.selected_fixture_id = ""
    main._store_layout_changed()
    history.clear()
    _history_states.clear()
    if accept: close_window()
    else: open_window("renovation")
    main._refresh_ui()

func _selector(y: float = 43) -> void:
    _ink(Vector2(204,y),main.simulation.store_name)
    _region(Rect2(185,y,16,16),func(): handle_shoulder(-1),100)
    _region(Rect2(268,y,16,16),func(): handle_shoulder(1),101)
    _ink(Vector2(186,y),"◁")
    _ink(Vector2(268,y),"▷")

func _shop_details() -> void:
    var s = main.simulation
    _paper(Rect2(180,33,102,184))
    _ink(Vector2(184,38),_company)
    _ink(Vector2(192,54),s.store_name)
    _ink(Vector2(184,70),"先月売り上げ")
    _ink(Vector2(192,86),_money(s._store_sales_last_month))
    _ink(Vector2(192,102),str(s._business_hours_preset(s.business_hours_id).get("label","24時間")))
    _ink(Vector2(184,134),"評価")
    _stars(Vector2(216,134),s.star_rating)
    var values: Dictionary = s._store_values()
    for i in 4:
        _ink(Vector2(184,150+i*16),["人気","清掃","警備","サービス"][i])
        var value := int(s.popularity) if i == 0 else int(values[["","cleaning","security","service"][i]])
        _ink(Vector2(248,150+i*16),str(value))
    _paper(Rect2(28,86,150,38))
    _ink(Vector2(32,91),"どの店舗を調査しますか?")
    _option(Rect2(34,107,132,16),"◁ "+s.store_name+" ▷",func(): handle_shoulder(1),0)

func _graph() -> void:
    var s = main.simulation
    _paper(Rect2(20,38,278,182))
    _ink(Vector2(24,43),_company)
    _selector(43)
    _ink(Vector2(24,59),"顧客独占率")
    _ink(Vector2(108,59),"%d%%" % int(s.demand.customer_share_percent))
    _ink(Vector2(169,59),"総合評価")
    _stars(Vector2(225,59),s.star_rating)
    var graph: Dictionary = s.graph_data(screen == "results")
    var figures: Array = graph.oldest_first
    var maximum: int = graph.axis_yen
    _ink(Vector2(24,75),"¥%d万" % (maximum/10000))
    _ink(Vector2(24,139),"¥0")
    _ink(Vector2(24,203),"-¥%d万" % (maximum/10000))
    var plot := Rect2(48,88,240,112)
    surface.draw_rect(plot,Color("ffffac"))
    for x in range(48,289,48):
        for y in range(88,200,5): surface.draw_line(Vector2(x,y),Vector2(x,y+2),DARK)
    for y in [116,172]:
        for x in range(48,288,5): surface.draw_line(Vector2(x,y),Vector2(x+2,y),DARK)
    surface.draw_line(Vector2(48,144),Vector2(288,144),DARK)
    if figures.is_empty(): _ink_small(Vector2(68,154),"決算後に損益履歴を表示します")
    var shown: Array = figures.slice(maxi(0,figures.size()-60))
    for i in shown.size():
        var value: int = shown[i]
        var h: float = preload("res://scripts/domain/program_graph.gd").height(value,maximum)
        surface.draw_rect(Rect2(48+i*4,144-h if value >= 0 else 144,3,h),Color("2020f6") if value>=0 else Color("ff2020"))

func _survey() -> void:
    var s = main.simulation
    _paper(Rect2(28,38,264,182))
    _ink(Vector2(56,43),_company)
    _selector(43)
    var data := {"bought":s.survey_bought,"missing":s.survey_missing}
    for col in 2:
        var x: int = 34+col*132
        surface.draw_rect(Rect2(x+10,64,96,16),PINK if col==0 else BLUE)
        _ink(Vector2(x+22,64),"買った商品" if col==0 else "欲しかった物")
        var counts: Dictionary = data["bought" if col==0 else "missing"]
        var rows: Array = preload("res://scripts/domain/program_survey.gd").rank(counts,s.config["source_catalog"]["product_ids"])
        for i in rows.size():
            _ink(Vector2(32+col*132,80+i*16),main.tr(str(rows[i].id)))
            _ink(Vector2(120+col*132,80+i*16),str(rows[i].count))
    if s.survey_legacy_totals:
        _ink_small(Vector2(34,208),"更新前の集計を含みます")

func _system() -> void:
    var bits: int = SoundManager.source_settings_bits
    _paper(Rect2(60,70,198,102))
    _option(Rect2(112,75,112,16),"データをセーブ",func(): main._on_save_pressed(),0)
    _option(Rect2(112,91,112,16),"データをロード",func():
        main._on_load_pressed()
        close_window(),1)
    _ink(Vector2(65,107),"SE (効果音)")
    _option(Rect2(177,107,16,16),"ON",func(): SoundManager.set_source_settings(bits&~1),2)
    _ink(Vector2(193,107),"/")
    _option(Rect2(201,107,24,16),"OFF",func(): SoundManager.set_source_settings(bits|1),3)
    _ink(Vector2(65,123),"BGM (音楽)")
    for i in 3:
        var value := i
        _option(Rect2(177+i*16,123,12,16),str(i+1),func():
            SoundManager.set_source_settings((bits&3)|(value<<8))
            SoundManager.play_source_bgm(int(SoundManager.source_settings()["bgm_id"])),4+i)
        if i < 2: _ink(Vector2(187+i*16,123),"/")
    _ink(Vector2(65,139),"月次報告")
    _option(Rect2(177,139,24,16),"する",func():
        SoundManager.set_source_settings(bits&~2)
        main.simulation.config["source_settings_bits"] = SoundManager.source_settings_bits,7)
    _ink(Vector2(201,139),"/")
    _option(Rect2(209,139,36,16),"しない",func():
        SoundManager.set_source_settings(bits|2)
        main.simulation.config["source_settings_bits"] = SoundManager.source_settings_bits,8)
    # Settings persist selected values independently of the current cursor.
    for r in [Rect2(201 if bits&1 else 177,107,24 if bits&1 else 16,16),Rect2(177+int(SoundManager.source_settings()["bgm_choice"])*16,123,12,16),Rect2(209 if bits&2 else 177,139,36 if bits&2 else 24,16)]:
        surface.draw_rect(r,Color(1,0.7,1,0.25))
    _footer(155)

func _close_shop() -> void:
    _paper(Rect2(60,102,198,54))
    _center(107,"開店中は改装できません")
    _center(123,"臨時休業にしますか?")
    _option(Rect2(115,139,36,16),"はい",func():
        for entry in main.simulation.business_hours_presets():
            if main.simulation.open_minutes(entry) == 0:
                if close_hours.is_empty():
                    close_hours = main.simulation.business_hours_id
                    _close_store_uid = main.simulation._store_uid
                main.simulation.try_set_business_hours(str(entry["id"]))
                open_window(_close_target)
                return
        show_notice("営業時間の設定を確認して下さい"),0)
    _option(Rect2(167,139,48,16),"いいえ",handle_cancel,1)

func _site_selection() -> void:
    # Keep the existing panels as acquisition-state sentinels for main.gd;
    # all visible controls here use the actual quote and build handlers.
    main.site_panel.position = Vector2(-5000,-5000)
    main.store_type_panel.position = Vector2(-5000,-5000)
    if main.store_type_panel.visible:
        _paper(Rect2(60,54,198,120))
        _ink(Vector2(65,59),"店舗を選んで下さい")
        var types: Array = _store_grid_types()
        for i in mini(6,types.size()):
            var entry: Dictionary = types[i]
            var id := str(entry["id"])
            var index := i
            _icon(Rect2(96+(i%3)*48,91+(i/3)*42,32,32),_atlas_icon("stores",str(entry["icon"]).right(2).to_int()-1,Vector2i(32,32),8),func():
                choice = index
                if main.simulation.store_type_is_selectable(id):
                    main._build_store(id)
                else: show_notice("この店舗はまだ選択できません"),i)
        if not types.is_empty():
            choice = clampi(choice,0,types.size()-1)
            _ink(Vector2(170,75),_money(main.simulation.store_type_price_yen(str(types[choice]["id"]))))
        return
    _paper(Rect2(60,70,198,38))
    var name := "%d号店" % (main.simulation.player_store_count+1) if main.choosing_new_store else "本店"
    _center(75,name+"の位置を決定して下さい")
    _option(Rect2(116,91,134,16),"L1・・・サイズ変更",func(): handle_shoulder(1),20)
    if main._site_origin.x >= 0:
        var quote: Dictionary = main.simulation.store_site_quote(main._site_origin)
        _paper(Rect2(60,126,198,54))
        if bool(quote["buildable"]):
            _center(131,_money(int(quote["total_yen"])))
            _option(Rect2(96,153,64,16),"ここに決定",func(): main._on_buy_site_pressed(),0)
            _option(Rect2(176,153,48,16),"いいえ",func(): main._site_origin=Vector2i(-1,-1),1)
        else:
            _center(134,"ここには出店できません")
            _option(Rect2(132,154,56,16),"終了",func(): main._site_origin=Vector2i(-1,-1),0)

func _store_grid_types() -> Array:
    var types: Array = main.simulation.store_types()
    if types.size() == 6:
        return [types[0],types[2],types[4],types[1],types[3],types[5]]
    return types

func _atlas_icon(sheet: String, index: int, cell: Vector2i, columns: int) -> Texture2D:
    var key := sheet+":"+str(index)
    if not _textures.has(key):
        var icon := AtlasTexture.new()
        icon.atlas = _texture("res://assets/ps1/ui/"+sheet+".png")
        icon.region = Rect2(Vector2((index%columns)*cell.x,(index/columns)*cell.y),Vector2(cell))
        _textures[key] = icon
    return _textures[key]

func _scheduled_wage(base: int, hours_id: String) -> int:
    return (base / 24) * (main.simulation.open_minutes(main.simulation._business_hours_preset(hours_id)) / 60)

func _store_overview() -> void:
    # Owner-authorized overview using live per-store fields, available in both views.
    var sim = main.simulation
    _paper(Rect2(8,40,304,188))
    _center(44,"全店舗の状況")
    var start := page * 3
    for row in mini(3,sim.store_count()-start):
        var index := start + row
        var y := 66 + row*44
        var sales: int = sim.store_field(index,"_store_sales_yen") - sim.store_field(index,"_store_sales_at_day_start")
        _option(Rect2(14,y,292,17),str(sim.store_field(index,"store_name")),func():
            close_window()
            main.select_store(index)
            main.town_view.hide()
            main.store_view.show()
            store_camera.reset_view()
            layout_screen(),index)
        _ink(Vector2(18,y+18),"★%d 売上%s 客%d人" % [sim.store_field(index,"star_rating"),_money(sales),sim.store_field(index,"customers").active_customers().size()])
    if page > 0:
        _option(Rect2(16,204,64,16),"前へ",func(): page-=1,100)
    if start+3 < sim.store_count():
        _option(Rect2(112,204,64,16),"次へ",func(): page+=1,101)
    _option(Rect2(236,204,64,16),"閉じる",close_window,102)

func _sell_store_panel() -> void:
    _paper(Rect2(24,42,272,172))
    _center(48,"店舗売却")
    _selector(70)
    var quote: Dictionary = main.simulation.store_sale_quote(main.simulation.active_store)
    _center(96,"評価額 "+_money(int(quote.total_yen)))
    if not quote.allowed:
        _center(120,str(quote.reason))
        _option(Rect2(100,156,120,22),"戻る",handle_cancel,0)
    else:
        _option(Rect2(38,156,100,22),"戻る",handle_cancel,0)
        _option(Rect2(164,156,112,22),"売却の確認",func():
            _sale_request=quote.duplicate()
            open_window("sell_store_confirm"),1)

func _sell_store_confirmation() -> void:
    _paper(Rect2(24,52,272,154))
    _center(58,str(_sale_request.get("name",""))+"を売却しますか")
    _center(86,_money(int(_sale_request.get("total_yen",0))))
    _center(110,"店員は未所属になり、空き地になります")
    _option(Rect2(38,154,100,22),"戻る",handle_cancel,0)
    _option(Rect2(164,154,112,22),"売却する",func():
        var sim = main.simulation
        if sim.try_sell_store(int(_sale_request.index),int(_sale_request.uid)):
            close_window()
            main._store_layout_changed()
            main.town_view.show()
            main.store_view.hide()
            main._refresh_ui()
            show_notice("店舗を売却しました")
        else:
            handle_cancel()
            show_notice("店舗の状態が変わり、売却できません"),1)
