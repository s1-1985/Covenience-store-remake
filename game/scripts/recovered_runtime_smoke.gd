extends SceneTree
const Town := preload("res://scripts/domain/program_town.gd")
const ProgramRandomScript := preload("res://scripts/domain/program_random.gd")
var failures := 0
func check(ok: bool, message: String) -> void:
    if not ok:
        failures += 1
        push_error(message)
func _initialize() -> void:
    var rng := ProgramRandomScript.new()
    check([rng.randi_range(1, 100), rng.randi_range(1, 100), rng.randi_range(1, 100)] == [1, 69, 89], "bounded draws must use the PS1 LCG, not the Godot global builtin")
    check(rng.seed == 2802067423, "LCG seed advances through range calls")
    rng.seed = 0
    check(rng.randf() == 0.0 and rng.randf() == 21468.0 / 32768.0, "float draws use the same stream")
    var data: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://data/ps1_recovered.json"))
    check("REMAKE_BALANCED_DEFAULT" in data["compatibility_boundaries"]["evidence_note"], "hybrid runtime boundaries stay explicit")
    var cases: Array = JSON.parse_string(FileAccess.get_file_as_string("res://tests/fixtures/recovered_town.json"))
    for sample in cases:
        var town := Town.new(data)
        town.seed = int(sample["seed"])
        if int(sample["level"]) != 0:
            for c in town.cells:
                c[1] = int(sample["level"])
        var actions := town.monthly(sample["stores"])
        var h := HashingContext.new()
        h.start(HashingContext.HASH_SHA256)
        h.update(town.raw_bytes())
        check(h.finish().hex_encode() == sample["sha256"], "entire source town " + str(sample["seed"]) + "/" + str(sample["level"]))
        check(town.seed == int(sample["final_seed"]), "town random state")
        check(town.population() == int(sample["population"]), "town population")
        check(JSON.stringify(actions) == JSON.stringify(sample["actions"]), "town build/removal decisions")
    print("Recovered runtime town cases: ", cases.size(), "; failures: ", failures)
    quit(1 if failures else 0)
