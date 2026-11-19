extends Control
# CONFIRMED_BINARY: 80057BD4, 80058388, 80058AEC, 80059254.
# Original art/palette/coordinates; readable text and direct taps authorized
# by the owner. Original startup movie/scenario dialogs are separate work.
const FONT = preload("res://fonts/ConveniJP.ttf")
const TITLE = preload("res://assets/ps1/ui/titl0.png")
const MENU = preload("res://assets/ps1/ui/titl1.png")
const FIELD = preload("res://assets/ps1/ui/field.png")
const CURSOR = preload("res://assets/ps1/ui/cursor.png")
var owner_menu
var surface: Node2D
var phase := "intro"
var tick := 0
var selected := 0
var y := -267
var bounce_mode := 0
var bounce_count := 1
var velocity := 1
var heights: Array[int] = [16,16,16,16,16,16,16,16,16,16]
var strips := 0
var scroll := Vector2i.ZERO
var elapsed := 0.0
var message := ""

func setup(menu) -> void:
    owner_menu = menu
    position = Vector2(160,0)
    size = Vector2(960,720)
    clip_contents = true
    mouse_filter = Control.MOUSE_FILTER_STOP
    focus_mode = Control.FOCUS_ALL
    grab_focus()
    surface = Node2D.new()
    surface.scale = Vector2.ONE*3
    surface.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
    surface.draw.connect(_paint)
    add_child(surface)

func _process(delta: float) -> void:
    if not visible: return
    elapsed += delta
    while elapsed >= 1.0/60.0:
        elapsed -= 1.0/60.0
        step_title()
    surface.queue_redraw()

func step_title() -> void:
    match phase:
        "intro":
            if tick in [33,81,111]:
                bounce_mode = 1
                bounce_count -= 10
            if bounce_count == 0:
                bounce_mode = 0
                bounce_count = 1
            y += velocity if bounce_mode == 0 else -velocity
            bounce_count += 1 if bounce_mode == 0 else -1
            velocity = int(bounce_count*2/6.0)
            tick += 1
            if tick == 125:
                phase = "start"
        "start", "hide":
            scroll += Vector2i(-1,1)
            if phase == "hide":
                for i in strips:
                    heights[i] = maxi(0,heights[i]-1)
                strips = mini(10,strips+1)
                if heights[9] == 0:
                    phase = "reveal"
                    strips = 0
        "reveal":
            scroll += Vector2i(1,-1)
            for i in strips:
                var index := 9-i
                heights[index] = mini(16,heights[index]+1)
            strips = mini(10,strips+1)
            if heights[0] == 16:
                phase = "menu"

func accept() -> void:
    if phase == "start":
        phase = "hide"
        SoundManager.play_sfx("select")
        SoundManager.play_source_bgm(1)
    elif phase == "menu":
        SoundManager.play_sfx("select")
        if selected == 0:
            owner_menu.show_scenarios()
        elif owner_menu._save_service.save_exists():
            owner_menu._on_continue_pressed()
            message = owner_menu.status_label.text
        else:
            message = "セーブデータがありません"
    surface.queue_redraw()

func cancel() -> void:
    if phase != "menu":return
    phase = "intro"
    tick = 0
    y = -267
    bounce_mode = 0
    bounce_count = 1
    velocity = 1
    heights.fill(16)
    strips = 0
    message = ""
    SoundManager.play_source_bgm(0)

func _gui_input(event: InputEvent) -> void:
    if event is InputEventKey and event.pressed and not event.echo:
        if event.is_action("ui_cancel"): cancel()
        elif event.is_action("ui_up"): selected = 0
        elif event.is_action("ui_down"): selected = 1
        elif event.is_action("ui_accept") or event.keycode == KEY_ENTER: accept()
        accept_event()
    var pressed := false
    var at := Vector2.ZERO
    if event is InputEventScreenTouch:
        pressed = event.pressed and not event.canceled
        at = event.position/3
    elif event is InputEventMouseButton:
        pressed = event.pressed and event.button_index == MOUSE_BUTTON_LEFT
        at = event.position/3
    if not pressed:return
    accept_event()
    if phase == "start":
        accept()
    elif phase == "menu":
        for i in 2:
            if Rect2(48,74+i*16,224,16).has_point(at):
                selected = i
                accept()
                return

func _text(at: Vector2, text: String, size_px := 36, color := Color("49483f")) -> void:
    surface.draw_set_transform(at,0,Vector2.ONE/3)
    surface.draw_string(FONT,Vector2(0,size_px),text,HORIZONTAL_ALIGNMENT_LEFT,-1,size_px,color)
    surface.draw_set_transform(Vector2.ZERO)

func _paint() -> void:
    # KABEE.BGD is a 20x16 repeat of the original 4x4 KYOU field tiles.
    for row in range(-1,5):
        for col in range(-1,6):
            surface.draw_texture(FIELD,Vector2(col*64+posmod(scroll.x,64),row*64+posmod(scroll.y,64)))
    if phase in ["intro","start","hide"]:
        for i in 10:
            var h: int = heights[i]
            if h > 0:
                surface.draw_texture_rect_region(TITLE,Rect2(32,y+120+i*16,256,h),Rect2(0,i*16,256,h))
        if phase in ["start","hide"]:
            _text(Vector2(112,178),"Push Start",27,Color.WHITE)
            surface.draw_texture_rect_region(MENU,Rect2(64,194,184,16),Rect2(0,0,184,16))
            surface.draw_texture_rect_region(MENU,Rect2(64,208,112,16),Rect2(0,16,112,16))
    else:
        for i in 10:
            var h: int = heights[i]
            if h > 0:
                surface.draw_texture_rect_region(MENU,Rect2(32,24+i*16,256,h),Rect2(0,32+i*16,256,h))
        if phase == "menu":
            surface.draw_rect(Rect2(48,74+selected*16,224,16),Color("f4b9f5"))
            _text(Vector2(124,74),"はじめから")
            _text(Vector2(124,90),"つづきから")
            surface.draw_texture(CURSOR,Vector2(186,86+selected*16))
            if not message.is_empty(): _text(Vector2(48,168),message,27)
