extends CanvasLayer
# Mobile presentation only. Original simulation never reads these controls.
# REMAKE_BALANCED_DEFAULT: rail positions, zoom, and portable button actions.
var main
var ui
var speed_label: Button
var pause_label: Button

func setup(owner_main, owner_ui) -> void:
    main = owner_main
    ui = owner_ui
    layer = 8
    for x in [0.0, 1120.0]:
        var rail := ColorRect.new()
        rail.position = Vector2(x, 0)
        rail.size = Vector2(160, 720)
        rail.color = Color("101715")
        rail.mouse_filter = Control.MOUSE_FILTER_STOP
        add_child(rail)
    _button("L1\n回転／縮小", Vector2(16, 110), func(): _shoulder(-1))
    _button("L2\n前の店", Vector2(16, 190), func(): _store(-1))
    _button("R1\n回転／拡大", Vector2(1136, 110), func(): _shoulder(1))
    _button("R2\n次の店", Vector2(1136, 190), func(): _store(1))
    _button("□\nコマンド", Vector2(16, 310), func():
        if main.selecting_site:
            return
        if ui.window.visible:
            ui.close_window()
        ui.command_open = not ui.command_open
        ui.refresh())
    _button("△\n町／店内", Vector2(16, 390), func():
        if main.selecting_site:
            return
        ui.close_window()
        ui.command_open = false
        main._on_show_town_map_pressed()
        ui.layout_screen()
        main._refresh_ui())
    _button("○\n決定", Vector2(1136, 310), _accept)
    _button("×\n取消", Vector2(1136, 390), _cancel)
    _button("SELECT\nシステム", Vector2(16, 620), func(): ui.toggle_window("system"))
    pause_label = _button("START\n停止／終了", Vector2(1136, 620), func():
        if ui.window.visible:
            ui.close_window()
        else:
            main._on_pause_pressed()
        ui.refresh())
    speed_label = _button("×1\n速度", Vector2(16, 16), func():
        main.speed = {1:2, 2:4, 4:8, 8:1}.get(main.speed, 1)
        speed_label.text = "×%d\n速度" % main.speed
        ui.refresh())
    var help := Label.new()
    help.position = Vector2(16, 490)
    help.size = Vector2(128, 100)
    help.text = "直接タップ\nドラッグ移動\n２本指で拡縮"
    help.add_theme_font_size_override("font_size", 15)
    help.add_theme_color_override("font_color", Color("b4c9bf"))
    add_child(help)

func _button(text: String, at: Vector2, action: Callable) -> Button:
    var button := Button.new()
    button.text = text
    button.position = at
    button.size = Vector2(128, 64)
    button.add_theme_font_size_override("font_size", 17)
    button.theme = ui.theme
    button.pressed.connect(action)
    add_child(button)
    return button

func _cancel() -> void:
    ui.command_open = false
    if ui.window.visible:
        ui.close_window()
    elif main.site_cancel_button != null and main.site_cancel_button.visible and not main.site_cancel_button.disabled:
        main.site_cancel_button.pressed.emit()
    elif main.fixture_info_panel != null and main.fixture_info_panel.visible:
        main.fixture_info_panel.hide()
    main.store_view.selected_fixture_id = ""
    ui.refresh()

func _accept() -> void:
    if main.site_buy_button != null and main.site_buy_button.is_visible_in_tree() and not main.site_buy_button.disabled:
        main.site_buy_button.pressed.emit()
        return
    if main.store_type_build_button != null and main.store_type_build_button.is_visible_in_tree() and not main.store_type_build_button.disabled:
        main.store_type_build_button.pressed.emit()
        return
    var focused: Control = get_viewport().gui_get_focus_owner()
    if focused is BaseButton and focused.get_parent() != self and not focused.disabled:
        focused.pressed.emit()

func _shoulder(direction: int) -> void:
    if ui.window_id == "interior":
        if direction == 1:
            main._on_rotate_fixture_pressed()
        else:
            # Same source-supported clockwise action, three turns for left.
            for i in range(3):
                main._on_rotate_fixture_pressed()
    elif main.town_view.visible:
        main.town_view.touch_zoom(1.25 if direction > 0 else 0.8)
    else:
        var factor := 1.15 if direction > 0 else 1.0 / 1.15
        main.store_view.scale = (main.store_view.scale * factor).clamp(Vector2(0.2, 0.2), Vector2(2, 2))

func _store(direction: int) -> void:
    if main.selecting_site:
        return
    var sim = main.simulation
    var count: int = sim._stores.size()
    if count <= 1:
        ui.toggle_window("stores")
        return
    ui.close_window()
    if not ui.window_id.is_empty():
        return
    var target: int = posmod(int(sim.active_store) + direction, count)
    main.select_store(target)
    ui.layout_screen()
