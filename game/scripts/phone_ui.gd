extends Node

# Task #110: the phone screen (Android). Platform presentation only; every
# action goes through the same simulation calls as the desktop panel.
#
# What is taken from the original (docs/research/official-ui-state-
# reconstruction-2026-09-05.md, CONFIRMED_VISUAL Console Archives
# screenshots, and the gameplay-video frame
# assets/raw/conveni_additional_assets_v1/reference/video_900s.png):
# - the store or town stays on screen and the commands open as windows
#   laid over it, never as separate full-screen pages;
# - one light band across the top with 年目/月/日 [天候] 時刻 ¥所持金;
# - a status bar along the bottom of the store with the store name, the
#   tobacco/alcohol/medicine marks and a yen figure;
# - the green background with the game's name repeated across it;
# - the command names 内装 (配置/移動/入れ替え/売却/終了), 店員, 営業方針,
#   販促 (宣伝), 調査 (docs/research/menu-hierarchy-evidence-2026-09-05.md);
# - the 宣伝 choices as a row of five pictures with their monthly cost.
# REMAKE_BALANCED_DEFAULT (this project's own, for touch screens): the
# command column on the right, large buttons instead of a cursor, the
# pause/speed buttons, picture grids instead of drop-down lists, the colours,
# the bottom bar's figure being today's sales (what the original's yen
# figure means is not known), the short notices for events, and that the
# layout can only be changed while the 内装 window is open.

const HUD_HEIGHT := 60.0
const BOTTOM_HEIGHT := 56.0
const MENU_LEFT := 1030.0
const MENU_WIDTH := 238.0
const PLAY_RIGHT := 1020.0
const SCREEN := Vector2(1280, 720)
const WINDOW_MIN_LEFT := 430.0

const BAND := Color("d7e9d2")
const BAND_TEXT := Color("26332a")
const FIELD := Color("2f7d68")
const FIELD_TEXT := Color("4f9f86")
const PAPER := Color("fbf6e6")
const PAPER_TEXT := Color("2b2620")
const INK_SOFT := Color("6b6152")
const FRAME := Color("5b4a35")
const TITLE_PINK := Color("e889a6")
const BUTTON := Color("2f8a73")
const BUTTON_HOVER := Color("37a086")
const BUTTON_PRESSED := Color("1f6b58")
const BUTTON_OFF := Color("b9b2a2")
const CHOSEN := Color("e889a6")
const GAUGE_BACK := Color("d9d2c0")
const GAUGE_GOOD := Color("3aa56b")
const GAUGE_LOW := Color("d9534f")

const PROMOTION_ICONS := {
    "direct_mail": "advertising_direct_mail",
    "newspaper": "advertising_newspaper",
    "airship": "advertising_airship",
    "radio": "advertising_radio",
    "tv": "advertising_television",
}
const PERMIT_ICONS := {"tobacco": "status_tobacco", "alcohol": "status_alcohol", "medicine": "status_medicine"}
const UI_ICON_DIR := "res://assets/ui/"
const STAFF_STATE_TEXT := {
    "idle": "待機中", "checkout": "レジ中", "to_restock": "補充へ", "restocking": "補充中",
    "to_clean": "掃除へ", "cleaning": "掃除中",
}
const EVENT_NOTICES := [
    "store_built", "facility_built", "inducement_started", "town_building_built", "rival_withdrew", "rival_opened", "rival_bought_out", "month_end_settlement",
    "checkout_anger_triggered", "staff_exhausted", "promotion_fired", "chain_expanded",
]

var main
var theme: Theme
var hud: PanelContainer
var pause_button: Button
var speed_button: Button
var bottom_bar: PanelContainer
var store_name_label: Label
var permit_marks: Dictionary = {}
var sales_label: Label
var ticker_label: Label
var menu: VBoxContainer
var menu_buttons: Dictionary = {}
var town_button: Button
var window: PanelContainer
var window_title: Label
var window_body: VBoxContainer
var window_scroll: ScrollContainer
var window_id := ""
var notice: PanelContainer
var customer_card: PanelContainer
var customer_card_label: Label
var customer_eject_button: Button
var customer_id := ""
# Task #111: choosing where to induce a facility on the town map.
var inducing_id := ""
var inducing_origin := Vector2i(-1, -1)
var induce_panel: PanelContainer
var induce_label: Label
var induce_button: Button
# Task #112: a tapped building on the town map.
var building_card: PanelContainer
var building_card_label: Label
var notice_label: Label
var _notice_left := 0.0
var _updaters: Array[Callable] = []
var _heard_sequence := 0
var _last_message := ""
var _day_seen := -1
var _revenue_at_day_start := 0
var _textures: Dictionary = {}


func setup(owner_main) -> void:
    main = owner_main
    theme = make_theme()
    _heard_sequence = main._latest_event_sequence()
    _last_message = main.layout_edit_label.text
    _build_background()
    _build_hud()
    _build_bottom_bar()
    _build_menu()
    _build_window()
    _build_notice()
    _build_customer_card()
    main.store_view.customer_tapped.connect(show_customer)
    _build_induce_panel()
    main.town_view.site_tapped.connect(_on_induce_tapped)
    _build_building_card()
    main.town_view.map_tapped.connect(_on_map_building_tapped)
    for panel in [main.site_panel, main.store_type_panel, main.rival_panel, main.fixture_info_panel]:
        if panel != null:
            panel.theme = theme
    main.get_node("Title").visible = false
    layout_screen()
    set_process(true)


# --- look ---

static func _box(color: Color, border := Color.TRANSPARENT, radius := 10, border_width := 0) -> StyleBoxFlat:
    var box := StyleBoxFlat.new()
    box.bg_color = color
    box.set_corner_radius_all(radius)
    if border_width > 0:
        box.border_color = border
        box.set_border_width_all(border_width)
    box.content_margin_left = 14
    box.content_margin_right = 14
    box.content_margin_top = 8
    box.content_margin_bottom = 8
    return box


static func make_theme() -> Theme:
    var made := Theme.new()
    made.default_font_size = 24
    made.set_stylebox("normal", "Button", _box(BUTTON))
    made.set_stylebox("hover", "Button", _box(BUTTON_HOVER))
    made.set_stylebox("pressed", "Button", _box(CHOSEN))
    made.set_stylebox("hover_pressed", "Button", _box(CHOSEN))
    made.set_stylebox("disabled", "Button", _box(BUTTON_OFF))
    made.set_stylebox("focus", "Button", StyleBoxEmpty.new())
    for state in ["font_color", "font_hover_color", "font_pressed_color", "font_hover_pressed_color", "font_focus_color"]:
        made.set_color(state, "Button", Color.WHITE)
    made.set_color("font_disabled_color", "Button", Color("f4f0e6"))
    made.set_font_size("font_size", "Button", 24)
    made.set_stylebox("panel", "PanelContainer", _box(PAPER, FRAME, 14, 3))
    made.set_color("font_color", "Label", PAPER_TEXT)
    made.set_font_size("font_size", "Label", 22)
    made.set_stylebox("normal", "OptionButton", _box(BUTTON))
    made.set_color("font_color", "OptionButton", Color.WHITE)
    made.set_constant("separation", "VBoxContainer", 10)
    made.set_constant("separation", "HBoxContainer", 10)
    made.set_constant("h_separation", "GridContainer", 10)
    made.set_constant("v_separation", "GridContainer", 10)
    return made


func _texture(path: String) -> Texture2D:
    if not _textures.has(path):
        _textures[path] = load(path) as Texture2D if ResourceLoader.exists(path) else null
    return _textures[path]


# The field behind the store: green, with the game's name written across it
# in rows, like the original's backdrop (video_900s.png).
func _build_background() -> void:
    var background: ColorRect = main.get_node("Background")
    add_field(background)


# Shared with the title screen (main_menu.gd).
static func add_field(background: CanvasItem) -> void:
    background.set("color", FIELD)
    var pattern := Node2D.new()
    pattern.name = "FieldPattern"
    pattern.draw.connect(func():
        var font: Font = ThemeDB.fallback_font
        for row in range(-1, 9):
            for column in range(-1, 7):
                var at := Vector2(column * 230 + (row % 2) * 115, row * 96)
                pattern.draw_set_transform(at, -0.35, Vector2.ONE)
                pattern.draw_string(font, Vector2.ZERO, "ザ・コンビニ", HORIZONTAL_ALIGNMENT_LEFT, -1, 40, FIELD_TEXT)
        pattern.draw_set_transform(Vector2.ZERO, 0.0, Vector2.ONE))
    background.get_parent().add_child(pattern)
    background.get_parent().move_child(pattern, background.get_index() + 1)


# --- the band across the top ---

func _build_hud() -> void:
    hud = main.get_node("UI/TopBar")
    var band := _box(BAND, Color("9fb99a"), 0, 0)
    band.content_margin_left = 20
    band.content_margin_right = 12
    hud.add_theme_stylebox_override("panel", band)
    hud.offset_left = 0
    hud.offset_top = 0
    hud.offset_right = SCREEN.x
    hud.offset_bottom = HUD_HEIGHT
    var row: HBoxContainer = hud.get_node("Margin/HBox")
    row.add_theme_constant_override("separation", 22)
    (hud.get_node("Margin") as MarginContainer).add_theme_constant_override("margin_top", 0)
    (hud.get_node("Margin") as MarginContainer).add_theme_constant_override("margin_bottom", 0)
    for label in row.get_children():
        if label is Label:
            label.add_theme_color_override("font_color", BAND_TEXT)
            label.add_theme_font_size_override("font_size", 26)
            label.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
    (row.get_node("CashValue") as Label).add_theme_color_override("font_color", Color("7a4b00"))
    row.get_node("StoreNameValue").visible = false
    pause_button = _small_button("‖", "PhonePause")
    pause_button.pressed.connect(func():
        main._on_pause_pressed()
        refresh())
    row.add_child(pause_button)
    speed_button = _small_button("×1", "PhoneSpeed")
    speed_button.pressed.connect(func():
        main.speed = {1: 2, 2: 4, 4: 1}[main.speed]
        refresh())
    row.add_child(speed_button)


func _small_button(text: String, node_name: String) -> Button:
    var button := Button.new()
    button.name = node_name
    button.text = text
    button.theme = theme
    button.custom_minimum_size = Vector2(76, 50)
    button.add_theme_font_size_override("font_size", 26)
    return button


# --- the status bar under the store ---

func _build_bottom_bar() -> void:
    bottom_bar = PanelContainer.new()
    bottom_bar.name = "PhoneStatusBar"
    var bar := _box(Color(BAND, 0.92), Color.TRANSPARENT, 0, 0)
    bar.content_margin_top = 4
    bar.content_margin_bottom = 4
    bottom_bar.add_theme_stylebox_override("panel", bar)
    bottom_bar.theme = theme
    var row := HBoxContainer.new()
    row.add_theme_constant_override("separation", 16)
    bottom_bar.add_child(row)
    store_name_label = _label("本店", 24, BAND_TEXT)
    row.add_child(store_name_label)
    for permit_id in ["tobacco", "alcohol", "medicine"]:
        var mark := TextureRect.new()
        mark.texture = _texture(UI_ICON_DIR + PERMIT_ICONS[permit_id] + ".png")
        mark.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
        mark.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
        mark.custom_minimum_size = Vector2(40, 40)
        mark.tooltip_text = main.tr(permit_id)
        permit_marks[permit_id] = mark
        row.add_child(mark)
    ticker_label = _label("", 20, INK_SOFT)
    ticker_label.size_flags_horizontal = Control.SIZE_EXPAND_FILL
    ticker_label.clip_text = true
    ticker_label.text_overrun_behavior = TextServer.OVERRUN_TRIM_ELLIPSIS
    row.add_child(ticker_label)
    sales_label = _label("", 24, Color("7a4b00"))
    row.add_child(sales_label)
    main.get_node("UI").add_child(bottom_bar)
    bottom_bar.position = Vector2(0, SCREEN.y - BOTTOM_HEIGHT)
    bottom_bar.size = Vector2(PLAY_RIGHT, BOTTOM_HEIGHT)


func _label(text: String, size: int, color: Color = PAPER_TEXT) -> Label:
    var label := Label.new()
    label.text = text
    label.add_theme_font_size_override("font_size", size)
    label.add_theme_color_override("font_color", color)
    label.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
    return label


# --- the command column ---

const COMMANDS := [
    ["interior", "内装", "res://assets/menu_icons/fixtures/small_ambient_shelf.png"],
    ["staff", "店員", "res://assets/menu_icons/staff/staff_001.png"],
    ["policy", "営業方針", "res://assets/menu_icons/products/cash.png"],
    ["promotion", "販促", "res://assets/ui/advertising_television.png"],
    ["research", "調査", "res://assets/menu_icons/products/books.png"],
]


func _build_menu() -> void:
    menu = VBoxContainer.new()
    menu.name = "PhoneMenu"
    menu.theme = theme
    menu.add_theme_constant_override("separation", 8)
    main.get_node("UI").add_child(menu)
    menu.position = Vector2(MENU_LEFT, HUD_HEIGHT + 10)
    menu.size = Vector2(MENU_WIDTH, SCREEN.y - HUD_HEIGHT - 20)
    for command in COMMANDS:
        var button := _menu_button(str(command[1]), str(command[2]))
        button.name = "Menu_" + str(command[0])
        var window_name := str(command[0])
        button.pressed.connect(func(): toggle_window(window_name))
        menu_buttons[window_name] = button
        menu.add_child(button)
    town_button = _menu_button("町マップ", "res://assets/menu_icons/store_types/store_type_01.png")
    town_button.name = "Menu_town"
    town_button.pressed.connect(func():
        close_window()
        building_card.visible = false
        if not inducing_id.is_empty():
            stop_inducing()
        main.store_view.selected_fixture_id = ""
        main._on_show_town_map_pressed()
        layout_screen()
        main._refresh_ui())
    menu.add_child(town_button)
    var system := _menu_button("システム", "")
    system.name = "Menu_system"
    system.pressed.connect(func(): toggle_window("system"))
    menu_buttons["system"] = system
    menu.add_child(system)


func _menu_button(text: String, icon_path: String) -> Button:
    var button := Button.new()
    button.text = text
    button.toggle_mode = false
    button.custom_minimum_size = Vector2(MENU_WIDTH, 76)
    button.alignment = HORIZONTAL_ALIGNMENT_LEFT
    button.add_theme_font_size_override("font_size", 28)
    if not icon_path.is_empty():
        button.icon = _texture(icon_path)
        button.expand_icon = false
        button.add_theme_constant_override("icon_max_width", 52)
    return button


# --- windows laid over the store ---

func _build_window() -> void:
    window = PanelContainer.new()
    window.name = "PhoneWindow"
    window.theme = theme
    window.visible = false
    window.clip_contents = true
    var column := VBoxContainer.new()
    window.add_child(column)
    var title_row := HBoxContainer.new()
    column.add_child(title_row)
    var title_band := PanelContainer.new()
    title_band.add_theme_stylebox_override("panel", _box(TITLE_PINK, Color.TRANSPARENT, 8, 0))
    title_band.size_flags_horizontal = Control.SIZE_EXPAND_FILL
    title_row.add_child(title_band)
    window_title = _label("", 28, Color.WHITE)
    title_band.add_child(window_title)
    var close := Button.new()
    close.name = "PhoneWindowClose"
    close.text = "×"
    close.custom_minimum_size = Vector2(64, 56)
    close.add_theme_font_size_override("font_size", 32)
    close.pressed.connect(close_window)
    title_row.add_child(close)
    var scroll := ScrollContainer.new()
    window_scroll = scroll
    scroll.name = "Scroll"
    scroll.size_flags_vertical = Control.SIZE_EXPAND_FILL
    scroll.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
    column.add_child(scroll)
    window_body = VBoxContainer.new()
    window_body.size_flags_horizontal = Control.SIZE_EXPAND_FILL
    window_body.add_theme_constant_override("separation", 12)
    scroll.add_child(window_body)
    main.get_node("UI").add_child(window)


func _clear_body() -> void:
    for child in window_body.get_children():
        window_body.remove_child(child)
        child.queue_free()


func toggle_window(id: String) -> void:
    if window_id == id:
        close_window()
    else:
        open_window(id)


func open_window(id: String) -> void:
    if main.selecting_site:
        return
    close_window()
    window_id = id
    _updaters.clear()
    _clear_body()
    match id:
        "interior":
            window_title.text = "内装"
            _fill_interior()
        "staff":
            window_title.text = "店員"
            _fill_staff()
        "policy":
            window_title.text = "営業方針"
            _fill_policy()
        "promotion":
            window_title.text = "販促"
            _fill_promotion()
        "research":
            window_title.text = "調査"
            _fill_research()
        "system":
            window_title.text = "システム"
            _fill_system()
        "stock":
            window_title.text = "商品を並べる"
            _fill_stock()
    window.visible = true
    window_scroll.scroll_vertical = 0
    for key in menu_buttons:
        (menu_buttons[key] as Button).add_theme_stylebox_override("normal", _box(CHOSEN if key == id else BUTTON))
    # Only the 内装 window edits the layout (see the file header).
    main.store_view.editing = id == "interior"
    if id != "interior":
        main.store_view.edit_mode = "move"
    layout_screen()
    refresh()


func close_window() -> void:
    if window_id.is_empty():
        return
    if window_id == "interior":
        main.store_view.selected_fixture_id = ""
    window_id = ""
    _updaters.clear()
    window.visible = false
    main.store_view.editing = false
    for key in menu_buttons:
        (menu_buttons[key] as Button).remove_theme_stylebox_override("normal")
    layout_screen()
    main._refresh_ui()


# Where everything goes: the store fills the space left of the command
# column, and moves to the left edge while a window is open beside it.
func layout_screen() -> void:
    var area := Rect2(0, HUD_HEIGHT, PLAY_RIGHT, SCREEN.y - HUD_HEIGHT - BOTTOM_HEIGHT)
    var store: Dictionary = main.config["store"]
    var tile_pixels: float = main.store_view.SUBCELL_PIXELS * int(store["subcells_per_tile"])
    var natural := Vector2(int(store["width_tiles"]), int(store["height_tiles"])) * tile_pixels
    var fit := minf(1.0, minf((area.size.x - 32) / natural.x, (area.size.y - 16) / natural.y))
    main.store_view.scale = Vector2(fit, fit)
    var shown := natural * fit
    var top := area.position.y + (area.size.y - shown.y) / 2.0
    if window.visible and main.store_view.visible:
        main.store_view.position = Vector2(16, top)
    else:
        main.store_view.position = Vector2((area.size.x - shown.x) / 2.0, top)
    main.town_view.position = area.position
    main.town_view.view_size = area.size
    var left := WINDOW_MIN_LEFT
    if main.store_view.visible:
        left = clampf(16 + shown.x + 16, WINDOW_MIN_LEFT, 640)
    window.position = Vector2(left, HUD_HEIGHT + 8)
    window.size = Vector2(PLAY_RIGHT - left - 8, SCREEN.y - HUD_HEIGHT - BOTTOM_HEIGHT - 16)
    bottom_bar.visible = main.store_view.visible
    if main.site_panel != null:
        main.site_panel.position = Vector2(8, SCREEN.y - 150)
        main.site_panel.size = Vector2(PLAY_RIGHT - 16, 140)
    if main.rival_panel != null:
        main.rival_panel.position = Vector2(8, SCREEN.y - 170)
        main.rival_panel.size = Vector2(PLAY_RIGHT - 16, 160)
    if main.fixture_info_panel != null:
        main.fixture_info_panel.position = Vector2(PLAY_RIGHT - 470, SCREEN.y - BOTTOM_HEIGHT - 250)
        main.fixture_info_panel.size = Vector2(460, 0)
    if main.store_type_panel != null:
        main.store_type_panel.position = area.position + (area.size - main.store_type_panel.size) / 2.0
    main.town_view.queue_redraw()


# --- keeping everything current ---

func refresh() -> void:
    var simulation = main.simulation
    if simulation == null:
        return
    pause_button.text = "▶" if main.paused else "‖"
    speed_button.text = "×%d" % main.speed
    if _day_seen != simulation.day_count or _day_seen < 0:
        _day_seen = simulation.day_count
        _revenue_at_day_start = simulation.economy.recorded_revenue_yen()
    sales_label.text = "本日の売上 ¥%s" % main._format_integer(simulation.economy.recorded_revenue_yen() - _revenue_at_day_start)
    for permit_id in permit_marks:
        (permit_marks[permit_id] as TextureRect).modulate = Color.WHITE if simulation.has_permit(permit_id) else Color(1, 1, 1, 0.22)
    ticker_label.text = main.tr(str(simulation.last_event))
    # What the last action did (a refusal, a hire...) pops up as a notice.
    if main.layout_edit_label.text != _last_message:
        _last_message = main.layout_edit_label.text
        if not _last_message.is_empty() and _last_message != main.tr("Deselected"):
            show_notice(_last_message, 2.5)
    town_button.text = "店内へ" if main.town_view.visible else "町マップ"
    menu.visible = not main.selecting_site
    bottom_bar.visible = main.store_view.visible and not main.selecting_site
    if main.selecting_site and window.visible:
        close_window()
    for updater in _updaters:
        updater.call()
    _refresh_customer_card()
    _show_event_notices()


func _process(delta: float) -> void:
    if notice.visible:
        _notice_left -= delta
        if _notice_left <= 0.0:
            notice.visible = false


# --- 誘致: choosing the place on the town map ---
# The 援助額 and the place price are shown together and paid when the
# player confirms (the videos show the 援助額 taken when place selection
# starts and given back on cancel, so the total paid is the same).

func _build_induce_panel() -> void:
    induce_panel = PanelContainer.new()
    induce_panel.name = "PhoneInducePanel"
    induce_panel.theme = theme
    induce_panel.visible = false
    var column := VBoxContainer.new()
    induce_panel.add_child(column)
    induce_label = _label("", 22)
    induce_label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
    induce_label.size_flags_horizontal = Control.SIZE_EXPAND_FILL
    column.add_child(induce_label)
    var row := HBoxContainer.new()
    row.alignment = BoxContainer.ALIGNMENT_END
    column.add_child(row)
    induce_button = Button.new()
    induce_button.name = "PhoneInduceConfirm"
    induce_button.text = "誘致する"
    induce_button.custom_minimum_size = Vector2(180, 60)
    induce_button.pressed.connect(_confirm_inducing)
    row.add_child(induce_button)
    var cancel := Button.new()
    cancel.name = "PhoneInduceCancel"
    cancel.text = "やめる"
    cancel.custom_minimum_size = Vector2(140, 60)
    cancel.pressed.connect(stop_inducing)
    row.add_child(cancel)
    main.get_node("UI").add_child(induce_panel)


func start_inducing(facility_id: String) -> void:
    var facility: Dictionary = main.simulation._inducement_facility(facility_id)
    close_window()
    inducing_id = facility_id
    inducing_origin = Vector2i(-1, -1)
    if not main.town_view.visible:
        main._on_show_town_map_pressed()
    main.town_view.selecting_site = true
    main.town_view.site_cursor_size = Vector2i(int(facility["size"][0]), int(facility["size"][1]))
    main.town_view.show_site_cursor(Vector2i(-1, -1), false)
    induce_label.text = "%s（%d×%dマス）を建てる場所を地図でタップ\n援助額 ¥%s" % [
        facility["name"], int(facility["size"][0]), int(facility["size"][1]), main._format_integer(int(facility["aid_yen"])),
    ]
    induce_button.disabled = true
    induce_panel.visible = true
    induce_panel.position = Vector2(8, SCREEN.y - 150)
    induce_panel.size = Vector2(PLAY_RIGHT - 16, 140)
    layout_screen()
    main._refresh_ui()


func stop_inducing() -> void:
    inducing_id = ""
    induce_panel.visible = false
    main.town_view.selecting_site = main.selecting_site
    main.town_view.site_cursor_size = Vector2i(2, 2)
    main.town_view.show_site_cursor(Vector2i(-1, -1), false)
    main._refresh_ui()


func _on_induce_tapped(origin: Vector2i) -> void:
    if inducing_id.is_empty():
        return
    inducing_origin = origin
    var facility: Dictionary = main.simulation._inducement_facility(inducing_id)
    var quote: Dictionary = main.simulation.inducement_quote(inducing_id, origin)
    var ok: bool = bool(quote["placeable"])
    main.town_view.show_site_cursor(origin, ok)
    if not ok:
        induce_label.text = "%s　誘致不可能（%s）" % [facility["name"], {
            "not_buildable_ground": "道路・線路・地図の外にかかる",
            "store_in_the_way": "コンビニにかかる",
            "one_at_a_time": "誘致中の施設がある",
        }.get(str(quote["reason"]), str(quote["reason"]))]
        induce_button.disabled = true
        SoundManager.play_sfx(str(main.config["sound"]["refused_sfx"]))
        return
    var taken: Array = quote["taken_buildings"]
    induce_label.text = "%s　誘致可能\n援助額 ¥%s ＋ 場所代 ¥%s ＝ ¥%s%s" % [
        facility["name"], main._format_integer(int(quote["aid_yen"])), main._format_integer(int(quote["place_yen"])),
        main._format_integer(int(quote["total_yen"])),
        "　（建物%d軒を巻き込みます）" % taken.size() if not taken.is_empty() else "",
    ]
    induce_button.disabled = main.simulation.economy.cash_yen < int(quote["total_yen"])


func _confirm_inducing() -> void:
    if inducing_id.is_empty() or inducing_origin.x < 0:
        return
    if not main.simulation.try_induce(inducing_id, inducing_origin):
        show_notice("ここには誘致できません")
        return
    stop_inducing()


# --- a tapped building on the town map ---
# CONFIRMED_COMMUNITY (docs/research/ui-menu-evidence-2026-09-05.md section
# 6, a PS screenshot): the original shows a building's name and its 買い物
# 人口 when the cursor is on it. Shown here: the name, its DATA4 wanted items
# and hours (CONFIRMED_OFFICIAL), the 買い物人口 only where the guide gives it
# (the 誘致 facilities), and whether it is in the store's 16x16 area.

func _build_building_card() -> void:
    building_card = PanelContainer.new()
    building_card.name = "PhoneBuildingCard"
    building_card.theme = theme
    building_card.visible = false
    var row := HBoxContainer.new()
    building_card.add_child(row)
    building_card_label = _label("", 22)
    building_card_label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
    building_card_label.size_flags_horizontal = Control.SIZE_EXPAND_FILL
    row.add_child(building_card_label)
    var close := Button.new()
    close.name = "PhoneBuildingClose"
    close.text = "閉じる"
    close.custom_minimum_size = Vector2(110, 60)
    close.pressed.connect(func(): building_card.visible = false)
    row.add_child(close)
    main.get_node("UI").add_child(building_card)


func _on_map_building_tapped(tile: Vector2i) -> void:
    building_card.visible = false
    var simulation = main.simulation
    if simulation.store_site == null or not simulation.rival_at(tile).is_empty():
        return
    var index: int = simulation.store_site.building_at(tile, simulation.bought_buildings())
    if index < 0:
        return
    var profile: Dictionary = simulation.store_site.building_profile(index)
    var sprite := str(simulation.store_site.buildings[index]["sprite"])
    var wanted: Array[String] = []
    for category in profile.get("wanted", []):
        wanted.append(main.tr(str(category)))
    var lines: Array[String] = [str(profile.get("name", sprite))]
    for facility in simulation.inducement_facilities():
        if str(facility["sprite"]) == sprite and facility.get("shopping_population") != null:
            lines[0] += "　買い物人口 %d人" % int(facility["shopping_population"])
    lines.append("欲しい品物：" + ("、".join(wanted) if not wanted.is_empty() else "なし"))
    var hours := "深夜も客がいる" if bool(profile.get("overnight", false)) else "朝から夜だけ客がいる"
    if simulation.has_store_site():
        hours += "　" + ("お店の商圏内" if simulation.store_site.in_catchment(simulation.store_site_origin, tile) else "お店の商圏外")
    lines.append(hours)
    building_card_label.text = "\n".join(lines)
    building_card.visible = true
    building_card.size = Vector2(PLAY_RIGHT - 16, 0)
    building_card.reset_size()
    building_card.size.x = PLAY_RIGHT - 16
    building_card.position = Vector2(8, SCREEN.y - building_card.size.y - 8)


# --- a tapped customer: what they are buying, and つまみだす ---
# CONFIRMED_COMMUNITY (SS play record, docs/research/menu-customer-screen-
# and-source-conflicts-2026-09-05.md section 2): a customer can be selected
# to see their information and be thrown out (つまみだす); the guide (p.35)
# advises doing it to angry-looking customers in the checkout queue, which
# is where this client allows it (try_eject_customer).

func _build_customer_card() -> void:
    customer_card = PanelContainer.new()
    customer_card.name = "PhoneCustomerCard"
    customer_card.theme = theme
    customer_card.visible = false
    var row := HBoxContainer.new()
    customer_card.add_child(row)
    customer_card_label = _label("", 22)
    customer_card_label.size_flags_horizontal = Control.SIZE_EXPAND_FILL
    customer_card_label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
    row.add_child(customer_card_label)
    customer_eject_button = Button.new()
    customer_eject_button.name = "PhoneEjectButton"
    customer_eject_button.text = "つまみだす"
    customer_eject_button.custom_minimum_size = Vector2(150, 60)
    customer_eject_button.pressed.connect(func():
        if main.simulation.try_eject_customer(customer_id):
            show_notice("お客さんをつまみだした")
        show_customer(""))
    row.add_child(customer_eject_button)
    var close := Button.new()
    close.text = "閉じる"
    close.custom_minimum_size = Vector2(110, 60)
    close.pressed.connect(func(): show_customer(""))
    row.add_child(close)
    main.get_node("UI").add_child(customer_card)


func show_customer(id: String) -> void:
    customer_id = id
    if not id.is_empty():
        main.store_view.selected_fixture_id = ""
    _refresh_customer_card()
    main._refresh_ui()


func _refresh_customer_card() -> void:
    var customer = null
    if not customer_id.is_empty() and main.simulation.customers.customers.has(customer_id):
        customer = main.simulation.customers.customer(customer_id)
    if customer == null or customer.phase == "done" or not main.store_view.visible:
        customer_id = ""
        customer_card.visible = false
        return
    var items: Array[String] = []
    for line in customer.basket:
        var product = main.simulation.inventory.get_product(str(line["product_id"]))
        items.append(main.tr(product.catalog_id) if product != null else str(line["product_id"]))
    customer_card_label.text = "お客さん（%s）\nかご：%s　¥%s" % [
        main.tr(customer.phase), "、".join(items) if not items.is_empty() else "なし",
        main._format_integer(customer.basket_total_yen()),
    ]
    customer_eject_button.disabled = not customer.phase in ["waiting_checkout", "checkout"]
    customer_card.visible = true
    customer_card.size = Vector2(560, 0)
    customer_card.reset_size()
    customer_card.size.x = 560
    var store_width: float = main.simulation.layout.width_subcells * main.store_view.SUBCELL_PIXELS * main.store_view.scale.x
    customer_card.position = Vector2(
        clampf(main.store_view.position.x + (store_width - 560.0) / 2.0, 8.0, PLAY_RIGHT - 568.0),
        SCREEN.y - BOTTOM_HEIGHT - customer_card.size.y - 8
    )


# --- short notices for what just happened ---

func _build_notice() -> void:
    notice = PanelContainer.new()
    notice.name = "PhoneNotice"
    notice.theme = theme
    notice.add_theme_stylebox_override("panel", _box(Color(PAPER, 0.96), FRAME, 12, 3))
    notice.visible = false
    notice.mouse_filter = Control.MOUSE_FILTER_IGNORE
    notice_label = _label("", 26)
    notice_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
    notice.add_child(notice_label)
    main.get_node("UI").add_child(notice)


func show_notice(text: String, seconds := 3.5) -> void:
    notice_label.text = text
    notice.visible = true
    notice.size = Vector2.ZERO
    notice.reset_size()
    # Centred over the store (or the town map), just above the status bar.
    var middle: float = PLAY_RIGHT / 2.0
    if main.store_view.visible:
        var store_width: float = main.simulation.layout.width_subcells * main.store_view.SUBCELL_PIXELS * main.store_view.scale.x
        middle = main.store_view.position.x + store_width / 2.0
    notice.position = Vector2(
        clampf(middle - notice.size.x / 2.0, 8.0, PLAY_RIGHT - notice.size.x - 8.0),
        SCREEN.y - BOTTOM_HEIGHT - notice.size.y - 12
    )
    _notice_left = seconds


func _show_event_notices() -> void:
    var records: Array = main.simulation.event_log.records
    if records.is_empty():
        return
    var newest := int(records[-1]["sequence"])
    if newest < _heard_sequence:
        _heard_sequence = 0
    var shown := ""
    for record in records:
        if int(record["sequence"]) <= _heard_sequence:
            continue
        var event_type := str(record["event_type"])
        if EVENT_NOTICES.has(event_type):
            shown = _notice_text(event_type, record.get("details", {}))
    _heard_sequence = newest
    if not shown.is_empty():
        show_notice(shown)


func _notice_text(event_type: String, details: Dictionary) -> String:
    match event_type:
        "month_end_settlement":
            # Like the original's monthly report (収支, 町人口 and its change,
            # CONFIRMED_VISUAL video V03).
            var result := int(details.get("month_result_yen", 0))
            var text := "%d月の収支　%s¥%s" % [
                (int(details.get("month_number", 1)) - 1) % 12 + 1,
                "+" if result >= 0 else "-", main._format_integer(absi(result)),
            ]
            var records: Array = main.simulation.economy.month_end_records
            if details.has("town_population"):
                var people := int(details["town_population"])
                text += "\n町人口 %s人" % main._format_integer(people)
                if records.size() >= 2 and (records[-2]["details"] as Dictionary).has("town_population"):
                    var change := people - int(records[-2]["details"]["town_population"])
                    text += "（%s%d人）" % ["+" if change >= 0 else "", change]
            return text
        "town_building_built":
            var milestone: Dictionary = main.simulation._town_milestone(str(details.get("milestone_id", "")))
            if str(details.get("milestone_id", "")) == "metropolitan_office":
                return "人口が%s人を超え、都庁が建ちました！　初級マップクリア" % main._format_integer(int(milestone.get("population", 0)))
            return "人口が%s人を超え、%sが建ちました" % [
                main._format_integer(int(milestone.get("population", 0))), str(milestone.get("name", "")),
            ]
        "rival_withdrew":
            return "%s が撤退しました" % _rival_name(str(details.get("rival_id", "")))
        "rival_opened":
            return "%s が新しく出店しました" % _rival_name(str(details.get("rival_id", "")))
        "checkout_anger_triggered":
            return "レジが遅くてお客さんが怒った！"
        "staff_exhausted":
            return "%s が疲れて休憩に入った" % _staff_name(str(details.get("staff_id", "")))
        "inducement_started":
            return "%s の誘致を始めました（完成まで約1か月）" % _facility_name(str(details.get("facility_id", "")))
        "facility_built":
            return "%s が完成しました" % _facility_name(str(details.get("facility_id", "")))
    return main.tr(event_type.replace("_", " "))


func _facility_name(facility_id: String) -> String:
    return str(main.simulation._inducement_facility(facility_id).get("name", facility_id))


func _rival_name(rival_id: String) -> String:
    return str(main.simulation._rival_guide_entry(rival_id).get("name", "ライバル店"))


func _staff_name(staff_id: String) -> String:
    var member = main.simulation.staff.members.get(staff_id)
    return staff_id if member == null else str(member.display_name)


# --- window contents ---

func _section(text: String) -> void:
    var label := _label(text, 22, INK_SOFT)
    window_body.add_child(label)


func _text(text: String, size := 22) -> Label:
    var label := _label(text, size)
    label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
    label.size_flags_horizontal = Control.SIZE_EXPAND_FILL
    window_body.add_child(label)
    return label


func _button(text: String, action: Callable, parent: Control = null) -> Button:
    var button := Button.new()
    button.text = text
    button.custom_minimum_size = Vector2(0, 64)
    button.size_flags_horizontal = Control.SIZE_EXPAND_FILL
    button.pressed.connect(func():
        action.call()
        main._refresh_ui())
    (parent if parent != null else window_body).add_child(button)
    return button


func _row() -> HBoxContainer:
    var row := HBoxContainer.new()
    window_body.add_child(row)
    return row


func _picture_button(texture: Texture2D, caption: String, action: Callable, parent: Control) -> Button:
    var button := Button.new()
    button.icon = texture
    button.expand_icon = true
    button.text = caption
    button.icon_alignment = HORIZONTAL_ALIGNMENT_CENTER
    button.vertical_icon_alignment = VERTICAL_ALIGNMENT_TOP
    button.custom_minimum_size = Vector2(0, 128)
    button.size_flags_horizontal = Control.SIZE_EXPAND_FILL
    button.clip_text = true
    button.text_overrun_behavior = TextServer.OVERRUN_TRIM_ELLIPSIS
    button.add_theme_font_size_override("font_size", 18)
    button.pressed.connect(func():
        action.call()
        main._refresh_ui())
    parent.add_child(button)
    return button


func _gauge(value: int, maximum: int, width := 160.0) -> Control:
    var gauge := Control.new()
    gauge.custom_minimum_size = Vector2(width, 16)
    gauge.set_meta("value", value)
    gauge.set_meta("maximum", maximum)
    gauge.draw.connect(func():
        var shown_max: int = maxi(1, int(gauge.get_meta("maximum")))
        var share := clampf(float(gauge.get_meta("value")) / shown_max, 0.0, 1.0)
        gauge.draw_rect(Rect2(Vector2.ZERO, gauge.size), GAUGE_BACK)
        gauge.draw_rect(Rect2(Vector2.ZERO, Vector2(gauge.size.x * share, gauge.size.y)), GAUGE_GOOD if share > 0.3 else GAUGE_LOW))
    return gauge


# 内装: the original's 配置/移動/入れ替え/売却/終了 (終了 = the × button),
# plus 回転 and restoring the opening layout.
func _fill_interior() -> void:
    var help := _text("")
    _updaters.append(func():
        var selected: String = main.store_view.selected_fixture()
        if selected.begins_with(main.NEW_FIXTURE_SELECTION_PREFIX):
            help.text = "空いているマスをタップして置く"
        elif selected.is_empty():
            help.text = "動かしたい設備をタップ" if main.store_view.edit_mode == "move" else "入れ替える設備を2つ続けてタップ"
        else:
            help.text = "%s を選択中　置きたいマスをタップ" % main._fixture_label(selected)
            if main.store_view.edit_mode == "swap":
                help.text = "%s を選択中　入れ替える相手をタップ" % main._fixture_label(selected))
    var modes := _row()
    var move := _button("移動", func():
        main.store_view.edit_mode = "move"
        main.store_view.selected_fixture_id = "", modes)
    var swap := _button("入れ替え", func():
        main.store_view.edit_mode = "swap"
        main.store_view.selected_fixture_id = "", modes)
    _updaters.append(func():
        move.add_theme_stylebox_override("normal", _box(CHOSEN if main.store_view.edit_mode == "move" else BUTTON))
        swap.add_theme_stylebox_override("normal", _box(CHOSEN if main.store_view.edit_mode == "swap" else BUTTON)))
    var actions := _row()
    var rotate := _button("回転", main._on_rotate_fixture_pressed, actions)
    var sell := _button("売却", main._on_sell_fixture_pressed, actions)
    _updaters.append(func():
        var selected: String = main.store_view.selected_fixture()
        var has_fixture: bool = not selected.is_empty() and not selected.begins_with(main.NEW_FIXTURE_SELECTION_PREFIX)
        rotate.disabled = not has_fixture
        sell.disabled = not has_fixture)
    _section("配置（買って置く）")
    var grid := GridContainer.new()
    grid.columns = 3
    window_body.add_child(grid)
    for entry in main.config["fixture_catalog"]:
        if str(entry.get("placement", "")) == "outdoor":
            continue
        var catalog_id := str(entry["catalog_id"])
        var price := int(entry["purchase_price_yen"])
        var button := _picture_button(
            main._menu_icon("fixtures", catalog_id),
            "%s\n¥%s" % [main.tr(catalog_id), main._format_integer(price)],
            func():
                main.store_view.edit_mode = "move"
                main.store_view.selected_fixture_id = main.NEW_FIXTURE_SELECTION_PREFIX + catalog_id,
            grid
        )
        var permit := str(entry.get("required_permit_id", ""))
        _updaters.append(func():
            button.disabled = main.simulation.economy.cash_yen < price or (not permit.is_empty() and not main.simulation.has_permit(permit)))
    _section("見本")
    _button("開店時の配置に戻す", main._on_load_sample_layout_pressed)


func _fill_staff() -> void:
    var simulation = main.simulation
    for staff_member in simulation.staff.all_staff():
        var staff_id := str(staff_member.staff_id)
        var card := PanelContainer.new()
        card.add_theme_stylebox_override("panel", _box(Color("f1ead4"), Color("cbbf9f"), 10, 2))
        window_body.add_child(card)
        var row := HBoxContainer.new()
        card.add_child(row)
        var face := TextureRect.new()
        face.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
        face.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
        face.custom_minimum_size = Vector2(72, 72)
        row.add_child(face)
        var info := VBoxContainer.new()
        info.size_flags_horizontal = Control.SIZE_EXPAND_FILL
        info.add_theme_constant_override("separation", 4)
        row.add_child(info)
        var name_label := _label("", 22)
        name_label.clip_text = true
        name_label.text_overrun_behavior = TextServer.OVERRUN_TRIM_ELLIPSIS
        info.add_child(name_label)
        var stamina_row := HBoxContainer.new()
        info.add_child(stamina_row)
        stamina_row.add_child(_label("体力", 18, INK_SOFT))
        var gauge := _gauge(0, 1, 120.0)
        stamina_row.add_child(gauge)
        var stamina_label := _label("", 18, INK_SOFT)
        stamina_row.add_child(stamina_label)
        var skills := _label("", 18, INK_SOFT)
        skills.clip_text = true
        info.add_child(skills)
        var replace := Button.new()
        replace.text = "交代"
        replace.custom_minimum_size = Vector2(96, 64)
        replace.pressed.connect(func(): _fill_candidates(staff_id))
        row.add_child(replace)
        _updaters.append(func():
            var member = main.simulation.staff.members[staff_id]
            face.texture = main._menu_icon("staff", main.store_view._staff_sprite_id_for_candidate(member.candidate_id))
            var role := "店員"
            if staff_id == str(main.config["staff"].get("manager_staff_id", "")):
                role = "店長"
            elif staff_id == main.simulation.staff.checkout_staff_id:
                role = "レジ係"
            var doing := str(STAFF_STATE_TEXT.get(member.state, member.state))
            if member.rest_phase == "resting":
                doing = "休憩中"
            name_label.text = "%s（%s）%s" % [member.display_name, role, doing]
            gauge.set_meta("value", member.stamina)
            gauge.set_meta("maximum", member.stamina_max)
            gauge.queue_redraw()
            stamina_label.text = "%d/%d" % [member.stamina, member.stamina_max]
            skills.text = "レジ%d 接客%d 補充%d 清掃%d 警備%d" % [
                member.register_skill, member.service_skill, member.replenishment_skill,
                member.cleaning_skill, member.security_skill,
            ])


# Hiring into one post: every candidate not already working elsewhere,
# with the résumé bands the original shows before hiring (体力/学歴/敏捷性/
# 社交性 as 普通/高い, task #56) and the daily wage.
func _fill_candidates(staff_id: String) -> void:
    _updaters.clear()
    _clear_body()
    var member = main.simulation.staff.members[staff_id]
    window_title.text = "%s と交代する人" % member.display_name
    _button("もどる", func(): open_window("staff"))
    var employed: Array[String] = []
    for other in main.simulation.staff.all_staff():
        if other.staff_id != staff_id:
            employed.append(other.candidate_id)
    for entry in main.config["staff_candidates"]:
        var candidate_id := str(entry["candidate_id"])
        if candidate_id in employed or candidate_id == member.candidate_id:
            continue
        var row := _row()
        var face := TextureRect.new()
        face.texture = main._menu_icon("staff", main.store_view._staff_sprite_id_for_candidate(candidate_id))
        face.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
        face.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
        face.custom_minimum_size = Vector2(64, 64)
        row.add_child(face)
        var text := _label("%s　日給¥%s\n体力%s 学歴%s 敏捷性%s 社交性%s" % [
            entry["display_name"], main._format_integer(int(entry["salary_yen_per_day_24h"])),
            main._resume_stat_band(int(entry["stamina"])), main._resume_stat_band(int(entry["academic_background"])),
            main._resume_stat_band(int(entry["agility"])), main._resume_stat_band(int(entry["sociability"])),
        ], 18)
        text.size_flags_horizontal = Control.SIZE_EXPAND_FILL
        row.add_child(text)
        var hire := Button.new()
        hire.text = "雇う"
        hire.custom_minimum_size = Vector2(96, 64)
        hire.pressed.connect(func():
            if main.simulation.try_hire_candidate(staff_id, candidate_id):
                main._refresh_hire_candidate_option()
                show_notice("%s を雇いました" % entry["display_name"])
                open_window("staff")
            else:
                show_notice("今は雇えません"))
        row.add_child(hire)


func _fill_policy() -> void:
    var simulation = main.simulation
    _section("商品の値段（定価から）")
    var price_row := _row()
    var price_label := _label("", 30)
    price_label.custom_minimum_size = Vector2(130, 0)
    price_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
    _button("－5%", func(): main.simulation.try_set_price_policy(main.simulation.price_change_pct - 5), price_row)
    price_row.add_child(price_label)
    _button("＋5%", func(): main.simulation.try_set_price_policy(main.simulation.price_change_pct + 5), price_row)
    _button("定価", func(): main.simulation.try_set_price_policy(0), price_row)
    _updaters.append(func():
        var pct: int = main.simulation.price_change_pct
        price_label.text = "定価" if pct == 0 else "%+d%%" % pct)
    _section("営業時間")
    var hours := GridContainer.new()
    hours.columns = 2
    window_body.add_child(hours)
    for preset in simulation.business_hours_presets():
        var preset_id := str(preset["id"])
        var button := _button(str(preset["label"]), func():
            main.simulation.try_set_business_hours(preset_id)
            main._select_current_business_hours(), hours)
        button.add_theme_font_size_override("font_size", 20)
        _updaters.append(func():
            button.add_theme_stylebox_override("normal", _box(CHOSEN if main.simulation.business_hours_id == preset_id else BUTTON)))
    _section("販売許可")
    for entry in main.config["permits"]:
        var permit_id := str(entry["permit_id"])
        var fee := int(entry["fee_yen"])
        var row := _row()
        var mark := TextureRect.new()
        mark.texture = _texture(UI_ICON_DIR + PERMIT_ICONS.get(permit_id, "") + ".png")
        mark.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
        mark.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
        mark.custom_minimum_size = Vector2(48, 48)
        row.add_child(mark)
        var text := _label("%s　¥%s" % [main.tr(permit_id), main._format_integer(fee)], 22)
        text.size_flags_horizontal = Control.SIZE_EXPAND_FILL
        row.add_child(text)
        var button := Button.new()
        button.custom_minimum_size = Vector2(150, 60)
        button.pressed.connect(func():
            if not main.simulation.try_purchase_permit(permit_id):
                show_notice("この場所では取れないか、お金が足りません")
            main._refresh_ui())
        row.add_child(button)
        _updaters.append(func():
            var held: bool = main.simulation.has_permit(permit_id)
            button.text = "取得済み" if held else "申請"
            button.disabled = held or main.simulation.economy.cash_yen < fee)


func _fill_promotion() -> void:
    _section("宣伝（人気が上がる）")
    var grid := GridContainer.new()
    grid.columns = 3
    window_body.add_child(grid)
    for entry in main.config["promotions"]:
        var promotion_id := str(entry["promotion_id"])
        var cost := int(entry["cost_yen"])
        var button := _picture_button(
            _texture(UI_ICON_DIR + str(PROMOTION_ICONS.get(promotion_id, "")) + ".png"),
            "%s\n¥%s" % [main.tr(promotion_id), main._format_integer(cost)],
            func():
                if main.simulation.try_purchase_promotion(promotion_id):
                    show_notice("%s を出しました" % main.tr(promotion_id))
                else:
                    show_notice("今月はもう出したか、お金が足りません"),
            grid
        )
        _updaters.append(func(): button.disabled = main.simulation.economy.cash_yen < cost)
    _section("誘致（町に施設を建ててもらう）")
    var induce_state := _text("")
    _updaters.append(func():
        var pending: Dictionary = main.simulation.pending_inducement
        induce_state.text = (
            "%s を工事中。完成するまで次の誘致はできません" % _facility_name(str(pending["facility_id"]))
            if not pending.is_empty() else "施設を選んで、町の地図で場所を決めます"
        ))
    var facilities := GridContainer.new()
    facilities.columns = 3
    window_body.add_child(facilities)
    for facility in main.simulation.inducement_facilities():
        var facility_id := str(facility["id"])
        var aid := int(facility["aid_yen"])
        var button := _picture_button(
            _texture("res://assets/town/%s.png" % facility["sprite"]),
            "%s\n援助¥%s" % [facility["name"], main._format_integer(aid)],
            func(): start_inducing(facility_id),
            facilities
        )
        button.name = "Induce_" + facility_id
        _updaters.append(func():
            button.disabled = not main.simulation.pending_inducement.is_empty() or main.simulation.economy.cash_yen < aid)
    _section("新しい店を出す")
    var expand := _button("", main._on_expand_chain_pressed)
    _updaters.append(func():
        expand.text = "チェーンを広げる ¥%s（今%d店）" % [
            main._format_integer(main.simulation.chain_expansion_cost_yen()), main.simulation.player_store_count,
        ]
        expand.disabled = main.simulation.town_is_full() or main.simulation.economy.cash_yen < main.simulation.chain_expansion_cost_yen())
    var full := _text("")
    _updaters.append(func(): full.text = "町の店はライバル込みで10店まで" if main.simulation.town_is_full() else "")


func _fill_research() -> void:
    # Task #114: the beginner map's goal, 都庁を誘致する.
    if not main.simulation._town_growth().is_empty():
        _section("目標")
        var goal := _text("")
        _updaters.append(func():
            var target := 0
            for milestone in main.simulation._town_growth()["milestones"]:
                if str(milestone["id"]) == str(main.simulation._town_growth()["clear_milestone"]):
                    target = int(milestone["population"])
            goal.text = "都庁を誘致する（町人口%s人で建つ）\n今の町人口 %s人" % [
                main._format_integer(target), main._format_integer(main.simulation.town.population),
            ]
            if main.simulation.clear_condition_met:
                goal.text += "　クリア！")
    _section("店の成績")
    var results := _text("")
    _updaters.append(func():
        var simulation = main.simulation
        var snapshot: Dictionary = simulation.snapshot()
        var month_sales: int = simulation.economy.recorded_revenue_yen() - simulation._revenue_at_month_start
        var lines: Array[String] = [
            "今月の売上　¥%s" % main._format_integer(month_sales),
            "来店　%d人（会計まで %d人）" % [int(snapshot["started_visits"]), int(snapshot["completed_visits"])],
            "評価　%s　人気度 %d" % [main._star_rank_text(int(snapshot["star_rating"])), int(snapshot["popularity"])],
            "商品在庫　%d個" % int(snapshot["stock_units"]),
        ]
        if not simulation.economy.month_end_records.is_empty():
            var last: Dictionary = simulation.economy.month_end_records[-1]["details"]
            lines.append("先月の収支　¥%s" % main._format_integer(int(last.get("month_result_yen", 0))))
        results.text = "\n".join(lines))
    # Task #113: 調査 → 収支グラフ (the command exists, docs/research/menu-
    # hierarchy-evidence-2026-09-05.md section 3; its drawing is this
    # project's own): the last 12 months' sales and 収支 as bars.
    _section("収支グラフ（月ごと・売上と収支）")
    var graph := Control.new()
    graph.name = "ResultsGraph"
    graph.custom_minimum_size = Vector2(0, 170)
    graph.draw.connect(func(): _draw_results_graph(graph))
    window_body.add_child(graph)
    _updaters.append(func(): graph.queue_redraw())
    _section("アンケート")
    var survey := _text("")
    _updaters.append(func(): survey.text = main.survey_label.text)
    _section("町")
    var town := _text("")
    _updaters.append(func(): town.text = main.town_label.text)
    _section("最近の出来事")
    var events := _text("", 20)
    _updaters.append(func():
        var records: Array = main.simulation.event_log.records
        var shown: Array[String] = []
        var index := records.size() - 1
        while index >= 0 and shown.size() < 6:
            var record: Dictionary = records[index]
            var event_type := str(record["event_type"])
            if not event_type in ["customer_reached_product", "product_picked", "customer_queued_for_checkout", "restock_started"]:
                shown.append("%02d:%02d %s" % [
                    int(record["minute_of_day"]) / 60, int(record["minute_of_day"]) % 60,
                    main.tr(event_type.replace("_", " ")),
                ])
            index -= 1
        events.text = "\n".join(shown))


const GRAPH_SALES := Color("3a7fc1")
const GRAPH_PROFIT := Color("3aa56b")
const GRAPH_LOSS := Color("d9534f")


func _draw_results_graph(graph: Control) -> void:
    var records: Array = main.simulation.economy.month_end_records
    var font: Font = ThemeDB.fallback_font
    var area := Rect2(Vector2(8, 8), graph.size - Vector2(16, 34))
    graph.draw_rect(Rect2(Vector2.ZERO, graph.size), Color("f1ead4"))
    if records.is_empty():
        graph.draw_string(font, Vector2(16, graph.size.y / 2.0), "最初の月末から表示されます", HORIZONTAL_ALIGNMENT_LEFT, -1, 20, INK_SOFT)
        return
    var shown: Array = records.slice(maxi(0, records.size() - 12))
    var biggest := 1.0
    for record in shown:
        var details: Dictionary = record["details"]
        biggest = maxf(biggest, absf(float(details.get("month_sales_yen", 0))))
        biggest = maxf(biggest, absf(float(details.get("month_result_yen", 0))))
    var zero_y := area.position.y + area.size.y * 0.7
    var up := area.size.y * 0.7
    var down := area.size.y * 0.3
    graph.draw_line(Vector2(area.position.x, zero_y), Vector2(area.end.x, zero_y), INK_SOFT, 1.0)
    var slot := area.size.x / 12.0
    for i in shown.size():
        var details: Dictionary = shown[i]["details"]
        var x := area.position.x + slot * i + 4
        var sales := float(details.get("month_sales_yen", 0))
        var result := float(details.get("month_result_yen", 0))
        var sales_height := up * sales / biggest
        graph.draw_rect(Rect2(x, zero_y - sales_height, slot * 0.4, sales_height), GRAPH_SALES)
        var result_height := (up if result >= 0 else down) * absf(result) / biggest
        var result_top := zero_y - result_height if result >= 0 else zero_y
        graph.draw_rect(Rect2(x + slot * 0.42, result_top, slot * 0.4, result_height), GRAPH_PROFIT if result >= 0 else GRAPH_LOSS)
        var month := (int(details.get("month_number", i + 1)) - 1) % 12 + 1
        graph.draw_string(font, Vector2(x, graph.size.y - 6), "%d月" % month, HORIZONTAL_ALIGNMENT_LEFT, -1, 14, PAPER_TEXT)
    graph.draw_string(font, Vector2(area.end.x - 150, 22), "■売上", HORIZONTAL_ALIGNMENT_LEFT, -1, 16, GRAPH_SALES)
    graph.draw_string(font, Vector2(area.end.x - 80, 22), "■収支", HORIZONTAL_ALIGNMENT_LEFT, -1, 16, GRAPH_PROFIT)


func _fill_system() -> void:
    _button("セーブ", func():
        main._on_save_pressed()
        show_notice("セーブしました" if main.layout_edit_label.text == main.tr("Game saved") else "セーブできませんでした"))
    _button("ロード", func():
        main._on_load_pressed()
        show_notice(main.layout_edit_label.text)
        close_window())
    var sound := _button("", func(): main.sound_toggle_button.pressed.emit())
    _updaters.append(func(): sound.text = main.sound_toggle_button.text)
    _button("タイトルへ", main._on_quit_to_menu_pressed)


# Stocking an empty shelf: the products it can hold, as pictures (the
# original picks products from a grid of category icons,
# docs/research/ui-menu-evidence-2026-09-05.md section 5).
var stock_fixture_id := ""


func _fill_stock() -> void:
    var fixture: Dictionary = main.simulation.layout.fixtures_by_id.get(stock_fixture_id, {})
    var catalog: Dictionary = {}
    for entry in main.config["fixture_catalog"]:
        if str(entry["catalog_id"]) == str(fixture.get("catalog_id", "")):
            catalog = entry
    _text("%s に並べる商品" % main._fixture_label(stock_fixture_id))
    var grid := GridContainer.new()
    grid.columns = 3
    window_body.add_child(grid)
    for entry in main.config["product_catalog"]:
        var catalog_id := str(entry["catalog_id"])
        if not (catalog.get("compatible_product_categories", []) as Array).has(catalog_id):
            continue
        var permit := str(entry.get("required_permit_id", ""))
        var button := _picture_button(
            main._menu_icon("products", catalog_id),
            "%s\n仕入れ¥%s" % [main.tr(catalog_id), main._format_integer(int(entry["restock_unit_cost_yen"]))],
            func():
                var instance_id := "product-purchase-%d" % main._next_product_purchase_sequence
                main._next_product_purchase_sequence += 1
                if main.simulation.try_procure_product(catalog_id, instance_id, stock_fixture_id):
                    show_notice("%s を並べました" % main.tr(catalog_id))
                    close_window()
                else:
                    show_notice("並べられません（許可かお金が足りません）"),
            grid
        )
        _updaters.append(func(): button.disabled = not permit.is_empty() and not main.simulation.has_permit(permit))


func open_stock_window(fixture_id: String) -> void:
    stock_fixture_id = fixture_id
    open_window("stock")
