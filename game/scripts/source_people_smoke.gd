extends SceneTree
const Sim = preload("res://scripts/vertical_slice_simulation.gd")
const Starting = preload("res://scripts/domain/guide_starting_store.gd")
const People = preload("res://scripts/domain/program_people.gd")
func _init() -> void:
    var base: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://data/vertical_slice.json"))
    var sim = Sim.new(Starting.apply(base))
    assert(sim.try_buy_store_site(Vector2i(26, 12)))
    for i in 1000:
        sim.tick()
    print("PEOPLE sales=", sim.economy.completed_sales)
    for p in sim.staff.all_staff():
        print("STAFF ", p.staff_id, " ", p.source_state, " ", p.position, " -> ", p.source_goal, " e=", p.stamina)
    for p in sim.customers.active_customers():
        print("CUSTOMER ", p.source_state, " ", p.position, " -> ", p.source_goal, " basket=", p.basket.size())
    assert(sim.economy.completed_sales > 0)
    var data: Dictionary = JSON.parse_string(JSON.stringify(sim.save_state()))
    var clone = Sim.new(Starting.apply(base))
    assert(clone.load_state(data))
    assert(clone._program_rng.seed == sim._program_rng.seed)
    assert(JSON.stringify(clone._source_runtime_snapshot()) == JSON.stringify(sim._source_runtime_snapshot()))
    for i in 40:
        sim.tick()
        clone.tick()
    assert(clone._program_rng.seed == sim._program_rng.seed)
    assert(JSON.stringify(clone._source_runtime_snapshot()) == JSON.stringify(sim._source_runtime_snapshot()))
    print("SOURCE_PEOPLE_PASS native sales + mid-action JSON deterministic continuation")
    quit()
