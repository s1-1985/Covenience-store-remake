extends SceneTree
const Sim = preload("res://scripts/vertical_slice_simulation.gd")
const Starting = preload("res://scripts/domain/guide_starting_store.gd")
const People = preload("res://scripts/domain/program_people.gd")
const Customer = preload("res://scripts/domain/customer_state.gd")
func _init() -> void:
    var base: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://data/vertical_slice.json"))
    var s = Sim.new(Starting.apply(base))
    assert(s.try_buy_store_site(Vector2i(26, 12)))
    assert(People.clock(s) == 0)
    var workers = s.staff.all_staff()
    for i in workers.size():
        People.enter_rest(s, workers[i], i)
    var c = Customer.new({"id": "response-regression"})
    c.source_native = true
    c.source_state = 3
    c.phase = "waiting_checkout"
    c.position = s.layout.entry
    c.basket.append({"product_id": str(s.inventory.products.keys()[0]), "quantity": 1, "unit_price_yen": 100})
    s.customers.customers[c.customer_id] = c
    assert(People.target(s, c, "checkout"))
    c.position = c.source_goal
    c.source_direction = c.source_goal_direction
    c.route.clear()
    assert(People.unattended_checkout(s))
    var p = workers[0]
    assert(p.service_skill < 100) # original clock gate is closed at clock 0
    People.employee(s, p, 0)
    assert(p.source_state == 1)
    assert(not People.unattended_checkout(s)) # no duplicate dispatch
    for task in [2, 4]:
        People.enter_rest(s, p, 0)
        assert(People.target(s, p, "checkout"))
        p.source_state = task
        p.stamina = p.stamina_max
        People.employee(s, p, 0)
        assert(p.source_state == 1) # refill and cleaning yield to the register
    People.enter_rest(s, p, 0)
    p.stamina = p.stamina_max - 1
    People.employee(s, p, 0)
    assert(p.source_state == 0) # recovery is still required
    # Legacy absolute deadlines migrate once, including first-day negative times.
    c.source_deadline = -1320
    var old: Dictionary = s._source_runtime_snapshot()
    old.erase("clock_epoch")
    old["floor_clock"] = -1438
    s._restore_source_runtime(old)
    assert(s.customers.customers[c.customer_id].source_deadline == 120)
    assert(s.config["store"]["source_floor_clock"] == 2)
    var current: Dictionary = s._source_runtime_snapshot()
    s._restore_source_runtime(current)
    assert(s.customers.customers[c.customer_id].source_deadline == 120)
    assert(s.config["store"]["source_floor_clock"] == 2)
    s.day_count = 1
    s.minute_of_day = 2
    assert(People.clock(s) == 1442)
    print("STAFF_RESPONSE_PASS first-day clock + waiting checkout priority + refill/clean interruption + recovery + one-time legacy clock migration")
    quit()
