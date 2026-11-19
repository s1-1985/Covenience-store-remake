extends Node
# REMAKE_BALANCED_DEFAULT: owner-requested mobile camera; no simulation effects.
const AREA := Rect2(160,96,960,624)
var main
var ui
var _identity := ""
var _points: Dictionary = {}
var _start := Vector2.ZERO
var _moved := false
var _pinched := false
var _last_finger_ms := -1000
var _clip: Control
func setup(owner_main, owner_ui) -> void:
    main = owner_main
    ui = owner_ui
    _clip = Control.new()
    _clip.name = "StoreCameraClip"
    _clip.position = AREA.position
    _clip.size = AREA.size
    _clip.clip_contents = true
    _clip.mouse_filter = Control.MOUSE_FILTER_IGNORE
    main.add_child(_clip)
    main.move_child(_clip, main.store_view.get_index())
    main.store_view.reparent(_clip)
    reset_view()
func content_rect() -> Rect2:
    var store: Dictionary = main.config["store"]
    var tile: float = main.store_view.SUBCELL_PIXELS * int(store["subcells_per_tile"])
    var lot: float = main.store_view.lot_pixel_height()
    return Rect2(0,-lot,int(store["width_tiles"])*tile,int(store["height_tiles"])*tile+lot)
func layout() -> void:
    var key := str(main.simulation.viewed_store)+str(main.config["store"])
    if key != _identity:
        _identity = key
        reset_view()
    else:
        _clamp()
func reset_view() -> void:
    var rect := content_rect()
    var fit := minf(1.0,minf(AREA.size.x/rect.size.x,AREA.size.y/rect.size.y))
    main.store_view.scale = Vector2.ONE*fit
    main.store_view.global_position = AREA.get_center()-rect.get_center()*fit
    _points.clear()
    _clamp()
func _clamp() -> void:
    var rect := content_rect()
    var scaled: Vector2 = rect.size*main.store_view.scale
    var top: Vector2 = main.store_view.global_position+rect.position*main.store_view.scale
    for axis in 2:
        if scaled[axis] <= AREA.size[axis]:
            top[axis] = AREA.position[axis]+(AREA.size[axis]-scaled[axis])/2
        else:
            top[axis] = clampf(top[axis],AREA.end[axis]-scaled[axis],AREA.position[axis])
    main.store_view.global_position = top-rect.position*main.store_view.scale
func zoom_at(factor: float, anchor: Vector2) -> void:
    var view = main.store_view
    var local: Vector2 = view.to_local(anchor)
    var rect := content_rect()
    var fit := minf(1.0,minf(AREA.size.x/rect.size.x,AREA.size.y/rect.size.y))
    view.scale = Vector2.ONE*clampf(view.scale.x*factor,fit*0.5,fit*5)
    view.global_position = anchor-local*view.scale
    _clamp()
func _input(event: InputEvent) -> void:
    if not main.store_view.visible or main.selecting_site or not ui.screen.is_empty() or ui.notice.visible:
        _points.clear()
        return
    if event is InputEventMouseButton and Time.get_ticks_msec()-_last_finger_ms < 500:
        if AREA.has_point(event.position): get_viewport().set_input_as_handled()
        return
    if event is InputEventMagnifyGesture and AREA.has_point(event.position):
        zoom_at(event.factor,event.position)
        get_viewport().set_input_as_handled()
        return
    if event is InputEventScreenTouch:
        if event.pressed:
            if not AREA.has_point(event.position): return
            for card in [main.fixture_info_panel,ui.customer_card,ui.building_card]:
                if card.visible and card.get_global_rect().has_point(event.position): return
            _last_finger_ms = Time.get_ticks_msec()
            if _points.is_empty():
                _start = event.position
                _moved = false
                _pinched = false
            _points[event.index] = event.position
            if _points.size()>1: _pinched = true
        elif _points.has(event.index):
            _last_finger_ms = Time.get_ticks_msec()
            _points.erase(event.index)
            if _points.is_empty() and not _moved and not _pinched and not event.canceled:
                var tap := InputEventScreenTouch.new()
                tap.position = event.position
                tap.pressed = true
                main.store_view._unhandled_input(tap)
        else: return
        get_viewport().set_input_as_handled()
    elif event is InputEventScreenDrag and _points.has(event.index):
        var before := _points.values()
        var previous: Vector2 = _points[event.index]
        _points[event.index] = event.position
        if _points.size()==2:
            var after := _points.values()
            var distance: float = before[0].distance_to(before[1])
            if distance>1:
                zoom_at(after[0].distance_to(after[1])/distance,(before[0]+before[1])/2)
            main.store_view.global_position += (after[0]+after[1]-before[0]-before[1])/2
            _pinched = true
            _clamp()
        elif not _pinched and (_moved or event.position.distance_to(_start)>8):
            main.store_view.global_position += event.position-previous
            _moved = true
            _clamp()
        get_viewport().set_input_as_handled()
