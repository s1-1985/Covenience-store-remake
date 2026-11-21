extends SceneTree

const Sim = preload("res://scripts/vertical_slice_simulation.gd")
const Start = preload("res://scripts/domain/guide_starting_store.gd")
const People = preload("res://scripts/domain/program_people.gd")
const RNG = preload("res://scripts/domain/program_random.gd")
const Rules = preload("res://scripts/domain/program_rules.gd")

func setup():
    var base: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://data/vertical_slice.json"))
    var s = Sim.new(Start.apply(base))
    assert(s.try_buy_store_site(Vector2i(26, 12)))
    return s

func check_collision(s, boosted: bool) -> void:
    var p = s.staff.members[str(s.config.staff.manager_staff_id)]
    var base_agility: int = s._staff_candidate_catalog[p.candidate_id].agility
    assert(base_agility < 100)
    var blocker = null
    for worker in s.staff.all_staff():
        worker.position = Vector2i(-1, -1)
        if worker != p:
            blocker = worker
    assert(blocker != null)
    s.customers.customers.clear()
    var start := Vector2i(-1, -1)
    for y in range(1, s.layout.height_subcells - 1):
        for x in range(1, s.layout.width_subcells - 2):
            var cell := Vector2i(x, y)
            if s.layout.is_walkable(cell) and s.layout.is_walkable(cell + Vector2i.RIGHT) and s.layout.is_walkable(cell + Vector2i.RIGHT * 2) and s.layout.is_walkable(cell + Vector2i.UP) and s.layout.is_walkable(cell + Vector2i.DOWN):
                start = cell
                break
        if start.x >= 0:
            break
    assert(start.x >= 0)
    p.position = start
    p.source_state = 3
    p.stamina = p.stamina_max
    p.source_goal = start + Vector2i.RIGHT * 2
    p.route.assign([start + Vector2i.RIGHT, p.source_goal])
    blocker.position = start + Vector2i.RIGHT
    # Find a collision roll that fails at the initial trait but succeeds at 100.
    # Include the preceding working-energy roll, preserving the actual call order.
    var seed := -1
    for value in range(1, 10000):
        var rng = RNG.new()
        rng.seed = value
        Rules.working_energy(p.stamina, rng)
        if rng.randi() % 100 + 1 > base_agility:
            seed = value
            break
    assert(seed >= 0)
    s._program_rng.seed = seed
    People.employee(s, p, int(p.staff_id.get_slice("-", 1)) - 1)
    assert((p.position != start) == boosted, "Collision avoidance must use the current trait")
    assert(p.source_goal == Vector2i(-1, -1))

func check_prototype_recovery(s) -> void:
    var p = s.staff.members[str(s.config.staff.manager_staff_id)]
    var base_agility: int = s._staff_candidate_catalog[p.candidate_id].agility
    var seed := -1
    for value in range(1, 10000):
        var rng := RandomNumberGenerator.new()
        rng.seed = value
        var roll := rng.randf()
        if roll >= 0.9 * float(base_agility) / 100.0 and roll < 0.9:
            seed = value
            break
    assert(seed >= 0)
    var native_town = s.program_town
    s.program_town = null
    s._stamina_enabled = true
    s._stamina_rng = RandomNumberGenerator.new()
    var raised: Dictionary = s._candidate_raises[p.candidate_id]
    s._candidate_raises.erase(p.candidate_id)
    p.stamina = 0
    s._stamina_rng.seed = seed
    s._recover_stamina(p)
    assert(p.stamina == 1)
    s._candidate_raises[p.candidate_id] = raised
    p.stamina = 0
    s._stamina_rng.seed = seed
    s._recover_stamina(p)
    assert(p.stamina == 2, "Prototype recovery must use the current trait too")
    s.program_town = native_town

func _initialize() -> void:
    var s = setup()
    var p = s.staff.members[str(s.config.staff.manager_staff_id)]
    var initial: int = s._staff_candidate_catalog[p.candidate_id].agility
    check_collision(s, false)
    # The award helper is the existing source-backed entry to shared base traits.
    s._raise_manager(["agility"], 100)
    assert(s._candidate_figures(p.candidate_id).agility == 100)
    assert(s._staff_candidate_catalog[p.candidate_id].agility == initial)
    var saved: Dictionary = JSON.parse_string(JSON.stringify(s.save_state()))
    var clone = setup()
    assert(clone.load_state(saved))
    assert(clone._candidate_figures(p.candidate_id).agility == 100)
    check_collision(s, true)
    check_collision(clone, true)
    check_prototype_recovery(s)
    print("LIVE_STAFF_TRAITS_PASS current collision ability, immutable initial table, JSON continuation, prototype recovery")
    quit()
