extends SceneTree
const Sim = preload("res://scripts/vertical_slice_simulation.gd")
const Starting = preload("res://scripts/domain/guide_starting_store.gd")
const Progression = preload("res://scripts/domain/program_progression.gd")

func _initialize() -> void:
    var base: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://data/vertical_slice.json"))
    var source: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://data/ps1_integration.json"))
    assert(source["layouts"].size() == 30)
    assert(source["product_ids"].size() == 27)
    var counts = [2, 3, 1, 5]
    for index in 4:
        var config = Starting.apply(base.duplicate(true), index)
        var sim = Sim.new(config)
        assert(sim._rival_stores.size() == counts[index])
        assert(sim.program_town.cells.size() == 3000)
        assert(sim.town.population == int(source["scenarios"][index]["population"]))
        assert(config["economy"]["initial_cash_yen"] == source["scenarios"][index]["initial_cash"][0])
        assert(config["ps1_program_tables"]["staff_candidates"].size() == 35)
        var saved = JSON.parse_string(JSON.stringify(sim.save_state()))
        var clone = Sim.new(config)
        assert(clone.load_state(saved))
        assert(clone.program_town.raw_bytes() == sim.program_town.raw_bytes())
        assert(clone._rival_stores.size() == counts[index])
    var review = Progression.owner_rating([{"annual_sales": 600000000, "rating": 90}], 500000, 20000)
    assert(review["total"] == 82)
    var stores: Array = []
    for i in 8:
        stores.append({"annual_sales": 100000000, "rating": 90})
    assert(Progression.owner_rating(stores, 500000, 20000)["total"] == 100)
    print("Analysis integration: four scenarios, eleven rivals, staff, catalog, JSON reload and owner scores passed")
    quit(0)
