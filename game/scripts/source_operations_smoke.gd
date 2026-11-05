extends SceneTree
const Sim = preload("res://scripts/vertical_slice_simulation.gd")
const Starting = preload("res://scripts/domain/guide_starting_store.gd")
const Ops = preload("res://scripts/domain/program_operations.gd")
const RNG = preload("res://scripts/domain/program_random.gd")
func _initialize() -> void:
    var rng = RNG.new()
    rng.seed = 1
    var cases: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://tests/fixtures/source_operations.json"))
    for case in cases["floor_cases"]:
        var positions: Array = []
        for point in case["positions"]:
            positions.append(Vector2i(int(point[0]), int(point[1])))
        rng.seed = int(case["seed"])
        var floor_rows: Array = case["rows"].duplicate(true)
        assert(Ops.wear(floor_rows, int(case["previous"]), positions, rng) == int(case["percentage"]))
        assert(JSON.stringify(floor_rows) == JSON.stringify(case["after"]), "reference floor case")
        assert(rng.seed == int(case["final_seed"]))
    for case in cases["pool_cases"]:
        rng.seed = int(case["seed"])
        assert(Ops.sample_candidates(case["free"], rng) == case["chosen"])
        assert(rng.seed == int(case["final_seed"]))
    var rows: Array = [[0, 5, 10, 15, 16, 255]]
    assert(Ops.cleanliness(rows) == 100)
    var old_seed: int = rng.seed
    assert(Ops.wear(rows, 0, [Vector2i(0, 0)], rng) == 100)
    assert(rows[0][0] >= 1 and rows[0][0] <= 4)
    assert(rows[0][4] == 16 and rows[0][5] == 255)
    assert(rng.seed != old_seed)
    old_seed = rng.seed
    assert(Ops.wear(rows, 100, [Vector2i(0, 0)], rng) == 75)
    assert(rng.seed == old_seed)
    var selected = Ops.sample_candidates(["a", "b", "c", "d"], rng)
    assert(selected.size() == 4 and selected.has("a") and selected.has("d"))
    var base: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://data/vertical_slice.json"))
    var sim = Sim.new(Starting.apply(base))
    assert(sim.try_buy_store_site(Vector2i(26, 12)))
    var candidates = sim.source_hiring_candidates()
    assert(candidates.size() == 10)
    for id in candidates:
        for person in sim.staff.all_staff():
            assert(person.candidate_id != id)
    var initial: String = sim.staff.members["staff-1"].candidate_id
    assert(sim.try_dismiss_source_staff("staff-1"))
    assert(sim.source_management_has_vacancy())
    var minute: int = sim.minute_of_day
    sim.step()
    assert(sim.minute_of_day == minute)
    assert(sim.try_hire_candidate("staff-1", candidates[0]))
    assert(not sim.source_management_has_vacancy())
    assert(not sim.try_hire_candidate("staff-1", initial))
    assert(sim.try_transfer_source_staff(0, "staff-1", 0, "staff-2"))
    var saved: Dictionary = JSON.parse_string(JSON.stringify(sim.save_state()))
    var clone = Sim.new(Starting.apply(base))
    assert(clone.load_state(saved))
    assert(clone.staff.members["staff-1"].candidate_id == sim.staff.members["staff-1"].candidate_id)
    assert(clone.staff.members["staff-2"].candidate_id == sim.staff.members["staff-2"].candidate_id)
    assert(clone.source_cleanliness() == sim.source_cleanliness())
    print("Source operations: floor wear, RNG, candidate pool, dismissal, manager guard, transfer and JSON save passed")
    quit(0)
