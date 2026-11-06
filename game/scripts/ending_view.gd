extends Control
signal finished(save_requested: bool)

# Original constructor positions, artwork and credit timing; no original CPU.
# REMAKE_BALANCED_DEFAULT: until original ending voices are connected, the
# next button supplies the audio-finished boundary after fixed scene frames.
const Progression := preload("res://scripts/domain/program_progression.gd")
var tables: Dictionary
var ending := -1
var stage := "scene"
var frame := 0
var fraction := 0.0
var textures := {}
var next_button: Button
var save_yes: Button
var save_no: Button
var status: Label

func setup(value: int) -> void:
    ending = value
    tables = JSON.parse_string(FileAccess.get_file_as_string("res://data/source_endings.json"))
    set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
    mouse_filter = Control.MOUSE_FILTER_STOP
    texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
    next_button = Button.new()
    next_button.name = "EndingNext"
    next_button.text = "次へ"
    next_button.position = Vector2(1128, 620)
    next_button.size = Vector2(144, 76)
    next_button.pressed.connect(advance)
    add_child(next_button)
    save_yes = Button.new()
    save_yes.name = "EndingSaveYes"
    save_yes.text = "保存する"
    save_yes.position = Vector2(350, 400)
    save_yes.size = Vector2(260, 80)
    save_yes.pressed.connect(func(): finished.emit(true))
    add_child(save_yes)
    save_no = Button.new()
    save_no.name = "EndingSaveNo"
    save_no.text = "保存せずに戻る"
    save_no.position = Vector2(670, 400)
    save_no.size = Vector2(260, 80)
    save_no.pressed.connect(func(): finished.emit(false))
    add_child(save_no)
    status = Label.new()
    status.position = Vector2(180, 290)
    status.size = Vector2(920, 100)
    status.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
    status.add_theme_font_size_override("font_size", 32)
    add_child(status)
    _update_controls()

func _process(delta: float) -> void:
    fraction += delta * 60.0
    var count := int(fraction)
    fraction -= count
    advance_frames(count)

func advance_frames(count: int) -> void:
    frame += maxi(0, count)
    _update_controls()
    queue_redraw()

func _update_controls() -> void:
    if next_button == null:
        return
    next_button.visible = stage != "save"
    save_yes.visible = stage == "save"
    save_no.visible = stage == "save"
    status.visible = stage == "save"
    next_button.disabled = (stage == "scene" and frame < (389 if Progression.presentation_plan(ending)["scene"] in [1, 2] else 5)) or (stage == "credits" and frame < 7120)
    status.text = "クリア結果を保存しますか？" if stage == "save" else ""

func show_save_error() -> void:
    status.text = "保存できませんでした。もう一度選択してください。"

func advance() -> void:
    if next_button.disabled:
        return
    if stage == "scene":
        if not bool(Progression.presentation_plan(ending)["extra_flow"]):
            finished.emit(false)
            return
        stage = "credits"
        frame = 0
    elif stage == "credits":
        stage = "save"
    _update_controls()
    queue_redraw()

func _texture(name: String) -> Texture2D:
    if not textures.has(name):
        textures[name] = load("res://assets/ending/" + name)
    return textures[name]

func _sprite(entry: Dictionary, shift: int = 0, cycle: int = -1) -> void:
    var name := str(entry["image"])
    if entry.has("palettes") and cycle >= 0:
        name = str(entry["palettes"][cycle % 2])
    draw_texture(_texture(name), Vector2(int(entry["x"]) + 160, int(entry["y"]) + 120 - shift))

func _draw() -> void:
    draw_rect(Rect2(Vector2.ZERO, size), Color.BLACK)
    if tables.is_empty() or stage == "save":
        return
    var scale_factor := minf(size.x / 320.0, size.y / 240.0)
    draw_set_transform((size - Vector2(320, 240) * scale_factor) / 2.0, 0.0, Vector2.ONE * scale_factor)
    if stage == "scene":
        var scene: int = Progression.presentation_plan(ending)["scene"]
        var entries: Array = tables["scenes"][str(scene)]
        var cycle := clampi((frame - 5) / 6, 0, 64)
        if frame >= 4:
            # Original ordering table paints higher sprite slots first.
            for i in range(entries.size() - 1, -1, -1):
                _sprite(entries[i], cycle if scene in [1, 2] and int(entries[i]["slot"]) == 1 else 0, cycle - 1 if scene in [1, 2] else -1)
        var x: int = [96, 80, 64, 96][scene]
        var y: int = 198 if frame >= 4 else 64 if scene in [2, 3] else 96
        var windows: Array = tables["windows"][str(scene)]
        if not windows.is_empty():
            var window: Dictionary = windows[-1] if frame >= 4 else windows[0]
            var rectangle := Rect2(int(window["x"]), int(window["y"]), int(window["width"]) * 16, int(window["height"]) * 16)
            # REMAKE_BALANCED_DEFAULT: retain source window geometry; the
            # original window texture/shadow renderer is not yet ported.
            draw_rect(rectangle, Color("f8f4df"))
            draw_rect(rectangle, Color("85745d"), false, 1.0)
        draw_texture(_texture("message_%d.png" % (472 + scene)), Vector2(x, y))
    elif stage == "credits":
        for entry in tables["scenes"]["credits"]:
            _sprite(entry)
        var index := 0
        var page := mini(frame / 350, 20)
        var offset := frame % 350
        var atlas := _texture("credits.png")
        if page < 20:
            for p in page:
                index += int(tables["credits_page_lines"][p])
            var lines := int(tables["credits_page_lines"][page])
            for line in lines:
                draw_texture_rect_region(atlas, Rect2(10, 224 + 16 * line - mini(offset, 164), 384, 16), Rect2(0, (index + line) * 16, 384, 16))
        else:
            var shift := mini(frame - 7000, 120)
            for line in 2:
                draw_texture_rect_region(atlas, Rect2(16, 224 + 16 * line - shift, 384, 16), Rect2(0, (100 + line) * 16, 384, 16))
    draw_set_transform(Vector2.ZERO)
