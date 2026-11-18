extends "res://scripts/phone_ui.gd"
# CONFIRMED_VISUAL: owner's 26 screenshots, 2026-11-18. Coordinates are
# native 320x240; only the two external touch rails are remake presentation.
const ORIGIN := Vector2(160, 0)
const ZOOM := 3.0
const PINK := Color("f4b9f5")
const BLUE := Color("80ddf2")
const DARK := Color("49483f")
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
var selection := 0
var choice := 0
var page := 0
var slot := 0
var person_index := 0
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

func setup(owner_main) -> void:
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
    _ready_ui = true
    main.store_view.fixture_selected.connect(_fixture_action)
    refresh()

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
    var store: Dictionary = main.config["store"]
    var tile: float = main.store_view.SUBCELL_PIXELS * int(store["subcells_per_tile"])
    var natural := Vector2(int(store["width_tiles"]), int(store["height_tiles"])) * tile
    var lot: float = main.store_view.lot_pixel_height()
    natural.y += lot
    var fit := minf(1.0, minf(960.0 / natural.x, 624.0 / natural.y))
    main.store_view.scale = Vector2.ONE * fit
    main.store_view.position = Vector2(160, 96 + lot * fit)
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
    super._process(delta)
    if not _ready_ui:
        return
    if command_open and screen.is_empty():
        open_window("root" if main.town_view.visible else "store")
    _paint_age += delta
    if _paint_age >= 0.1:
        _paint_age = 0
        surface.queue_redraw()

func open_window(id: String) -> void:
    if not _ready_ui:
        return
    if id == "stock" or id == "town":
        screen = ""
        window.modulate.a = 1.0
        window.mouse_filter = Control.MOUSE_FILTER_STOP
        super.open_window(id)
        return
    if main.selecting_site:
        return
    if id == "interior" and not floor_mode.is_empty():
        screen = "interior"
    else:
        if not screen.is_empty() and screen != id:
            history.append(screen)
        screen = id
    command_open = false
    window_id = "interior" if id in ["interior", "fixtures", "close_shop"] else id
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
    if not close_hours.is_empty():
        main.simulation.try_set_business_hours(close_hours)
        close_hours = ""
    screen = ""
    history.clear()
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
    if screen.is_empty():
        return false
    if not floor_mode.is_empty():
        floor_mode = ""
        main.store_view.selected_fixture_id = ""
        open_window("interior")
    elif not history.is_empty():
        var target: String = history.pop_back()
        screen = ""
        open_window(target)
    else:
        close_window()
    return true

func handle_start() -> void:
    if not screen.is_empty():
        close_window()
    else:
        main._on_pause_pressed()
    refresh()

func handle_accept() -> bool:
    if main.selecting_site and _active_action.is_valid():
        _active_action.call()
        return true
    if screen.is_empty():
        return false
    if _active_action.is_valid():
        var action := _active_action
        action.call()
        surface.queue_redraw()
    return true

func handle_shoulder(direction: int) -> bool:
    if main.selecting_site:
        if not main.site_buy_button.disabled: main._on_buy_site_pressed()
        return true
    if screen in ["fixtures", "candidates", "stock_prices", "facilities"]:
        page = maxi(0, page + direction)
        choice = 0
        surface.queue_redraw()
        return true
    if screen in ["hours", "shop", "shop_graph", "survey", "transfer", "renovation"]:
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

func _input(event: InputEvent) -> void:
    if not _ready_ui or not main.visible:
        return
    if event is InputEventMouseMotion:
        var p: Vector2 = (event.position - ORIGIN) / ZOOM
        for h in hits:
            if h.rect.has_point(p):
                selection = h.index
                if screen in ["fixtures", "advertising", "facilities", "renovation"] and h.index < 100:
                    choice = h.index
                _cursor = p
                surface.queue_redraw()
                return
    if not (event is InputEventMouseButton and event.button_index == MOUSE_BUTTON_LEFT and event.pressed):
        return
    var p: Vector2 = (event.position - ORIGIN) / ZOOM
    # Notices/acquisition dialogs retain their own input handlers.
    if notice.visible:
        return
    for i in range(hits.size() - 1, -1, -1):
        var h: Dictionary = hits[i]
        if h.rect.has_point(p):
            selection = h.index
            var action: Callable = h.action
            get_viewport().set_input_as_handled()
            action.call()
            surface.queue_redraw()
            return
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

func _ink(at: Vector2, text: String, tint: Color = Color.WHITE) -> void:
    var x := at.x
    text = text.replace("［", "[").replace("］", "]").replace("･･･", "・・・").replace("～", "~").replace("○", "O").replace("％", "%")
    for ch in text:
        var code := int(glyphs.get(ch, -1))
        if code >= 0:
            var k: int = code % 336
            surface.draw_texture_rect_region(font_pages[code / 336], Rect2(x, at.y, 12, 15), Rect2((k % 21) * 12, (k / 21) * 16, 12, 15), tint)
        elif ch != " ":
            surface.draw_string(load("res://fonts/ConveniJP.ttf"), Vector2(x, at.y + 12), ch, HORIZONTAL_ALIGNMENT_LEFT, -1, 12, DARK)
        x += 8 if ch.unicode_at(0) < 128 or ch == "¥" else 12

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
    rect.size.y = items.size() * 16 + 6
    _paper(rect)
    for i in items.size():
        var item: Array = items[i]
        var id := str(item[1])
        _option(Rect2(rect.position + Vector2(3, 3 + i * 16), Vector2(rect.size.x - 6, 16)), str(item[0]), func(): _navigate(id), i)

func _navigate(id: String) -> void:
    match id:
        "enter":
            close_window()
            if main.town_view.visible:
                main._on_show_town_map_pressed()
            open_window("store")
            layout_screen()
        "interior":
            floor_mode = ""
            open_window("close_shop" if main.simulation.is_open_now() else "interior")
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
    _ink(Vector2(8, 16), "%02d年目%02d月%02d日[%s ] %s¥%s" % [s.month_count / 12 + 1, s.month_count % 12 + 1, int(snap["days_completed_this_month"]) + 1, s.weather_display_label(), s.clock_text(), main._format_integer(s.economy.cash_yen)])
    if main.selecting_site:
        _site_selection()
        return
    match screen:
        "root": _list([["店舗", "enter"], ["不動産", "realestate"], ["販促", "promotion"], ["調査", "research"], ["システム", "system"]], Rect2(45,56,70,0))
        "realestate": _list([["新装開店", "new_store"], ["店舗売却", "sell_store"]], Rect2(45,56,74,0))
        "promotion": _list([["宣伝をする", "advertising"], ["誘致をする", "facilities"]], Rect2(45,56,86,0))
        "research": _list([["店舗別詳細", "shop"], ["店舗別グラフ", "shop_graph"], ["全店収支グラフ", "results"], ["アンケート", "survey"]], Rect2(45,56,102,0))
        "store": _store_panel()
        "interior":
            if floor_mode.is_empty():
                _list([["配置", "fixtures"], ["移動", "move"], ["入れ替え", "swap"], ["売却", "sell"], ["終了", "finish"]], Rect2(192,64,118,0))
            else:
                _paper(Rect2(236,54,70,22))
                _center(58, {"move":"移動", "swap":"入れ替え", "sell":"売却", "place":"配置"}.get(floor_mode,"配置"),236,70)
        "fixtures": _fixtures()
        "policy": _list([["営業時間", "hours"], ["商品価格", "prices"], ["販売許可", "permits"]], Rect2(192,64,118,0))
        "hours": _hours()
        "prices": _prices()
        "stock_prices": _individual_prices()
        "permits": _permits()
        "advertising": _advertising()
        "facilities": _facilities()
        "staff": _list([["店員の雇用", "candidates"], ["店員の解雇", "dismiss"], ["店員の異動", "transfer"]], Rect2(45,56,86,0))
        "candidates", "dismiss": _personnel()
        "transfer": _transfer()
        "renovation": _renovation()
        "shop": _shop_details()
        "shop_graph", "results": _graph()
        "survey": _survey()
        "system": _system()
        "close_shop": _close_shop()
        "sell_store":
            _paper(Rect2(60,80,198,70))
            _center(88,"店舗売却")
            _center(108,"本店は売却できません" if s.active_store == 0 else "店舗売却は未実装です")
            _option(Rect2(132,128,56,16),"終了",close_window)
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

func _prices() -> void:
    _paper(Rect2(75,86,166,102))
    _ink(Vector2(80,91),"商品価格を決定して下さい")
    _ink(Vector2(80,107),"全商品平均利益率")
    var s = main.simulation
    var margin := 0
    # REMAKE_BALANCED_DEFAULT: portfolio margin is derived from the actual
    # catalog below, never copied as the screenshot's fixed 40 percent.
    var sale := 0.0
    var cost := 0.0
    for entry in main.config["product_catalog"]:
        sale += s._apply_price_policy(int(entry.get("sale_price_yen",0)),str(entry["catalog_id"]))
        cost += int(entry.get("purchase_price_yen",entry.get("cost_price_yen",entry.get("restock_unit_cost_yen",0))))
    if sale > 0: margin = roundi((sale-cost)*100/sale)
    _ink(Vector2(200,107),"%d%%" % margin)
    _option(Rect2(80,137,64,16),"全体に設定",func():
        s.try_set_price_policy(s.price_change_pct + 5 if s.price_change_pct < 50 else -50),0)
    _option(Rect2(156,137,78,16),"◁ %s ▷" % ("定価" if s.price_change_pct == 0 else "%+d%%" % s.price_change_pct),func():
        s.try_set_price_policy(s.price_change_pct - 5 if s.price_change_pct > -50 else 50),1)
    _option(Rect2(80,153,76,16),"個別に設定",func(): open_window("stock_prices"),2)
    _footer(170)

func _individual_prices() -> void:
    _paper(Rect2(44,46,230,166))
    _center(51,"商品価格を決定して下さい")
    var entries: Array = main.config["product_catalog"]
    page = clampi(page,0,maxi(0,(entries.size()-1)/7))
    for i in mini(7,entries.size()-page*7):
        var entry: Dictionary = entries[page*7+i]
        var id := str(entry["catalog_id"])
        _ink(Vector2(50,73+i*16),main.tr(id))
        _option(Rect2(170,73+i*16,95,16),"◁ 設定%d ▷" % main.simulation.source_price_setting(id),func():
            main.simulation.try_set_product_price(id,(main.simulation.source_price_setting(id)+1)%11),i)
    _footer(193)

func _permits() -> void:
    _paper(Rect2(44,70,230,86))
    _center(75,"販売許可を申請しますか?")
    var entries: Array = main.config["permits"]
    for i in mini(3,entries.size()):
        var entry: Dictionary = entries[i]
        var id := str(entry["permit_id"])
        var held: bool = main.simulation.has_permit(id)
        surface.draw_texture_rect(_texture(UI_ICON_DIR+PERMIT_ICONS.get(id,"")+".png"),Rect2(50,91+i*16,14,14),false)
        _ink(Vector2(72,91+i*16),main.tr(id))
        _option(Rect2(130,91+i*16,132,16),"申請済み" if held else "申請 "+_money(int(entry["fee_yen"])),func():
            if not held and not main.simulation.try_purchase_permit(id):
                show_notice("申請条件か資金を確認して下さい"),i)
    _footer(139)

func _advertising() -> void:
    _paper(Rect2(51,45,230,120))
    _center(50,"宣伝方法を選択して下さい(複数選択可)")
    var entries: Array = main.config["promotions"]
    choice = clampi(choice,0,entries.size()-1)
    var e: Dictionary = entries[choice]
    _ink(Vector2(72,66), main.tr(str(e["promotion_id"])))
    _ink(Vector2(176,66), _money(int(e["cost_yen"]))+"/月")
    var total := 0
    for id in main.simulation._promotions_used_this_month:
        for entry in entries:
            if entry["promotion_id"] == id: total += int(entry["cost_yen"])
    _ink(Vector2(72,82),"費用合計")
    _ink(Vector2(176,82),_money(total)+"/月")
    for i in mini(5,entries.size()):
        var id := str(entries[i]["promotion_id"])
        var index := i
        _icon(Rect2(68+i*40,96,32,32),_texture(UI_ICON_DIR+str(PROMOTION_ICONS.get(id,""))+".png"),func():
            choice = index
            if not main.simulation.try_purchase_promotion(id): show_notice("今月は申請済みか資金が足りません"),i)
    _footer(143)

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
    _paper(Rect2(35,38,247,166))
    _ink(Vector2(100,42),s.store_name+"の店員を"+("採用します" if hiring else "解雇して下さい"))
    for i in 3:
        var index := i
        var id := _person_id(s.staff,i)
        _face(id,Rect2(41,41+i*52,46,38))
        _region(Rect2(41,41+i*52,46,44),func(): slot = index,10+i)
        if i == 0: _ink(Vector2(52,81),"店長")
    var ids: Array = s.source_hiring_candidates() if hiring else []
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
        _ink(Vector2(196,89),"未経験" if hiring else "経験あり")
        _ink(Vector2(196,105),_money(int(e.get("salary_yen_per_day_24h",0)) if hiring else _scheduled_wage(int(s.staff.members["staff-%d" % (slot+1)].salary_yen_per_day_24h),s.business_hours_id))+"/日")
        var keys := ["stamina","academic_background","agility","sociability"]
        for i in 4:
            var value := int(e.get(keys[i],0))
            _ink(Vector2(100,123+i*16),["体力","学歴","敏捷性","社交性"][i])
            _ink(Vector2(146,123+i*16),str(value))
            _bar(Vector2(162,126+i*16),value)
        var candidate := id
        _region(Rect2(138,55,128,128),func():
            if hiring:
                if s.try_hire_candidate("staff-%d" % (slot+1),candidate):
                    main._refresh_hire_candidate_option()
                    show_notice("採用しました")
                else: show_notice("採用条件を確認して下さい")
            else:
                if s.try_dismiss_source_staff("staff-%d" % (slot+1)): show_notice("解雇しました"),0)
    _option(Rect2(95,61,18,16),"◁",func(): page = maxi(0,page-1),20)
    _option(Rect2(116,61,18,16),"▷",func(): page = mini(maxi(0,ids.size()-1),page+1),21)
    _footer(188)

func _transfer() -> void:
    var s = main.simulation
    _paper(Rect2(12,38,294,182))
    _center(43,"店員を異動させます")
    for side in 2:
        var index: int = s.active_store if side == 0 else transfer_store
        var roster = s.store_field(index,"staff")
        var x: int = 18 if side == 0 else 250
        _option(Rect2(x,43,62,16),"◁ %s ▷" % s.store_field(index,"store_name"),func():
            transfer_store = posmod(transfer_store+1,s.store_count()),20+side)
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
    _region(Rect2(135,188,40,28),func():
        if s.try_transfer_source_staff(s.active_store,"staff-%d"%(slot+1),transfer_store,"staff-%d"%(transfer_slot+1)):
            show_notice("異動しました"),30)
    _option(Rect2(136,204,40,15),"決定",func():
        s.try_transfer_source_staff(s.active_store,"staff-%d"%(slot+1),transfer_store,"staff-%d"%(transfer_slot+1)),31)

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
            if s.can_renovate_to(id):
                close_window()
                main.renovate_store(id)
            else: show_notice("この店舗へは改築できません"),i)

func _selector(y: float = 43) -> void:
    _ink(Vector2(204,y),main.simulation.store_name)
    _region(Rect2(185,y,16,16),func(): handle_shoulder(-1),100)
    _region(Rect2(234,y,16,16),func(): handle_shoulder(1),101)
    _ink(Vector2(186,y),"◁")
    _ink(Vector2(234,y),"▷")

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
    var records: Array = s.economy.month_end_records
    var figures: Array[int] = []
    for record in records:
        var d: Dictionary = record.get("details",{})
        # Only chain records exist currently: never present them as an
        # individual store's history. Store graph uses current store sales.
        if screen == "results": figures.append(int(d.get("month_result_yen",0)))
    if screen == "shop_graph":
        figures.append(s._store_sales_last_month)
        figures.append(s._store_sales_yen-s._store_sales_at_month_start)
    var maximum := 4000000
    for value in figures: maximum = maxi(maximum,ceili(absf(value)/1000000.0)*1000000)
    _ink(Vector2(24,75),"¥%d万" % (maximum/10000))
    _ink(Vector2(24,139),"¥0")
    _ink(Vector2(24,203),"-¥%d万" % (maximum/10000))
    var plot := Rect2(48,88,240,112)
    surface.draw_rect(plot,Color("fcfba4"))
    for x in range(48,289,48):
        for y in range(88,200,5): surface.draw_line(Vector2(x,y),Vector2(x,y+2),DARK)
    for y in [116,172]:
        for x in range(48,288,5): surface.draw_line(Vector2(x,y),Vector2(x+2,y),DARK)
    surface.draw_line(Vector2(48,144),Vector2(288,144),DARK)
    var shown: Array = figures.slice(maxi(0,figures.size()-60))
    for i in shown.size():
        var value: int = shown[i]
        var h: float = absf(value)*56.0/maximum
        surface.draw_rect(Rect2(48+i*4,144-h if value >= 0 else 144,3,h),Color.BLUE if value>=0 else Color.RED)

func _survey() -> void:
    var s = main.simulation
    _paper(Rect2(28,54,264,166))
    _ink(Vector2(56,59),_company)
    _selector(59)
    var data := {"bought":s.survey_bought,"missing":s.survey_missing}
    for col in 2:
        var x: int = 34+col*132
        surface.draw_rect(Rect2(x+10,72,96,16),PINK if col==0 else BLUE)
        _ink(Vector2(x+22,72),"買った商品" if col==0 else "欲しかった物")
        var counts: Dictionary = data["bought" if col==0 else "missing"]
        var keys: Array = counts.keys()
        keys.sort_custom(func(a,b): return int(counts[a]) > int(counts[b]))
        for i in mini(8,keys.size()):
            _ink(Vector2(x,91+i*16),main.tr(str(keys[i])))
            _ink(Vector2(x+96,91+i*16),str(counts[keys[i]]))

func _system() -> void:
    var bits: int = SoundManager.source_settings_bits
    _paper(Rect2(60,70,198,102))
    _option(Rect2(112,75,112,16),"データをセーブ",func(): main._on_save_pressed(),0)
    _option(Rect2(112,91,112,16),"データをロード",func():
        main._on_load_pressed()
        close_window(),1)
    _ink(Vector2(65,107),"SE (効果音)")
    _option(Rect2(177,107,16,16),"ON",func(): SoundManager.set_source_settings(bits|1),2)
    _ink(Vector2(193,107),"/")
    _option(Rect2(201,107,24,16),"OFF",func(): SoundManager.set_source_settings(bits&~1),3)
    _ink(Vector2(65,123),"BGM (音楽)")
    for i in 3:
        var value := i
        _option(Rect2(177+i*16,123,12,16),str(i+1),func():
            SoundManager.set_source_settings((bits&3)|(value<<8))
            SoundManager.play_source_bgm(int(SoundManager.source_settings()["bgm_id"])),4+i)
        if i < 2: _ink(Vector2(187+i*16,123),"/")
    _ink(Vector2(65,139),"月次報告")
    _option(Rect2(177,139,24,16),"する",func():
        SoundManager.set_source_settings(bits|2)
        main.simulation.config["source_settings_bits"] = SoundManager.source_settings_bits,7)
    _ink(Vector2(201,139),"/")
    _option(Rect2(209,139,36,16),"しない",func():
        SoundManager.set_source_settings(bits&~2)
        main.simulation.config["source_settings_bits"] = SoundManager.source_settings_bits,8)
    # Settings persist selected values independently of the current cursor.
    for r in [Rect2(177 if bits&1 else 201,107,16 if bits&1 else 24,16),Rect2(177+int(SoundManager.source_settings()["bgm_choice"])*16,123,12,16),Rect2(177 if bits&2 else 209,139,24 if bits&2 else 36,16)]:
        surface.draw_rect(r,Color(1,0.7,1,0.25))
    _footer(155)

func _close_shop() -> void:
    _paper(Rect2(60,102,198,54))
    _center(107,"開店中は改装できません")
    _center(123,"臨時休業にしますか?")
    _option(Rect2(115,139,36,16),"はい",func():
        for entry in main.simulation.business_hours_presets():
            if main.simulation.open_minutes(entry) == 0:
                close_hours = main.simulation.business_hours_id
                main.simulation.try_set_business_hours(str(entry["id"]))
                open_window("interior")
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
