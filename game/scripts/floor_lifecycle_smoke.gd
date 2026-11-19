extends SceneTree
const Sim = preload("res://scripts/vertical_slice_simulation.gd")
const Starting = preload("res://scripts/domain/guide_starting_store.gd")
const Customer = preload("res://scripts/domain/customer_state.gd")
const People = preload("res://scripts/domain/program_people.gd")

func stains(s) -> int:
    var count := 0
    for row in s.config["store"]["source_floor"]:
        for cell in row:
            count += int(int(cell) >= 0 and int(cell) < 15 and int(cell) % 5 != 0)
    return count

func _init() -> void:
    var base: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://data/vertical_slice.json"))
    var s = Sim.new(Starting.apply(base))
    assert(s.try_buy_store_site(Vector2i(26,12)))
    var rows: Array = s.config["store"]["source_floor"]
    var spots: Array[Vector2i] = []
    for y in rows.size():
        for x in rows[y].size():
            if int(rows[y][x]) >= 0 and int(rows[y][x]) < 15 and s.layout.is_walkable(Vector2i(x*2,y*2)):
                spots.append(Vector2i(x*2,y*2))
    assert(spots.size() > 3)
    var exterior: Array = []
    for y in rows.size():
        for x in rows[y].size():
            if int(rows[y][x]) >= 16:
                exterior.append([y,x,int(rows[y][x])])
    for bad in [1,4,6,9,11,14,15,-1,16]:
        var before := JSON.stringify(rows)
        assert(not s.try_set_source_floor(bad))
        assert(JSON.stringify(rows) == before)
    s.customers.customers.clear()
    var c = Customer.new({"id":"floor-regression"})
    c.source_native = true
    c.source_state = 2
    c.phase = "shopping"
    s.customers.customers[c.customer_id] = c
    for p in s.staff.all_staff():
        p.cleaning_skill = 0
    assert(s.source_cleaning_score() == 0)
    s.day_count = 0
    for material in [0,5,10]:
        assert(s.try_set_source_floor(material))
        assert(stains(s) == 0)
        # Legacy save value100 must not suppress future hourly dirt forever.
        s.config["store"]["source_previous_cleanliness"] = 100
        s.config["store"]["source_floor_clock"] = -1
        for hour in 3:
            c.position = spots[hour]
            s.minute_of_day = (hour+1)*60
            s._step_source_floor_wear()
            assert(stains(s) == hour+1)
            var code := int(rows[c.position.y/2][c.position.x/2])
            assert(code >= material+1 and code <= material+4)
            # Repeated updates at the same clock cannot add extra stains.
            c.position = spots[3]
            s._step_source_floor_wear()
            assert(stains(s) == hour+1)
        # Real staff clean action: reach dirty floor, wait for source RNG success.
        var cleaner = s.staff.all_staff()[0]
        for other in s.staff.all_staff():
            People.enter_rest(s, other, 0)
        cleaner.cleaning_skill = 100
        cleaner.source_state = 4
        cleaner.state = "cleaning"
        cleaner.position = spots[0]
        cleaner.source_goal = spots[0]
        cleaner.source_direction = 0
        cleaner.source_goal_direction = 0
        cleaner.stamina = cleaner.stamina_max
        c.phase = "done"
        for attempt in 100:
            People.employee(s,cleaner,0)
            if int(rows[spots[0].y/2][spots[0].x/2]) == material:
                break
        assert(int(rows[spots[0].y/2][spots[0].x/2]) == material)
        assert(stains(s) == 2)
        cleaner.cleaning_skill = 0
        c.phase = "shopping"
    for item in exterior:
        assert(int(rows[item[0]][item[1]]) == item[2])
    # Native score100 prevents stains; do not force dirt just to make it visible.
    assert(s.try_set_source_floor(0))
    for p in s.staff.all_staff(): p.cleaning_skill = 100
    assert(s.source_cleaning_score() == 100)
    c.position = spots[0]
    s.minute_of_day = 300
    s._step_source_floor_wear()
    assert(stains(s) == 0)
    # No customers inside means no new stain, even when staff score is zero.
    for p in s.staff.all_staff(): p.cleaning_skill = 0
    c.position = Vector2i(-1,-1)
    s.minute_of_day = 360
    s._step_source_floor_wear()
    assert(stains(s) == 0)
    c.position = spots[0]
    s.minute_of_day = 420
    s._step_source_floor_wear()
    assert(stains(s) == 1)
    var snapshot: Dictionary = JSON.parse_string(JSON.stringify(s.save_state()))
    var clone = Sim.new(Starting.apply(base))
    assert(clone.load_state(snapshot))
    var restored: Array = clone.config["store"]["source_floor"]
    for y in rows.size():
        for x in rows[y].size():
            assert(int(restored[y][x]) == int(rows[y][x]))
    clone.customers.customers[c.customer_id].position = spots[1]
    clone.minute_of_day = 480
    clone._step_source_floor_wear()
    assert(stains(clone) == 2)
    print("FLOOR_LIFECYCLE_PASS 3 materials; hourly wear after legacy100; source staff cleaning; score100/offmap guard; save/reload continues wear")
    quit(0)
