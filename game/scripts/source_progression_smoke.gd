extends SceneTree
const P := preload("res://scripts/domain/program_progression.gd")
const Sim := preload("res://scripts/vertical_slice_simulation.gd")
const Starting := preload("res://scripts/domain/guide_starting_store.gd")

func _initialize() -> void:
    var cases: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://tests/fixtures/source_progression.json"))
    for row in cases["stores"]:
        var result := P.store_milestone(row["stores"], int(row["mode"]), int(row["flags"]), int(row["pending"]))
        assert(JSON.parse_string(JSON.stringify(result)) == row["result"])
    for row in cases["terminal"]:
        var result := P.terminal_guard(int(row["cash"]), int(row["year"]), int(row["serial"]), 2, -1)
        assert(JSON.parse_string(JSON.stringify(result)) == row["result"])
    for i in 256:
        assert(P.menu_limit(i) == int(cases["menu"][i]))
    for i in 5:
        assert(JSON.parse_string(JSON.stringify(P.presentation_plan(i))) == cases["presentation"][i])
    var base: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://data/vertical_slice.json"))
    var sim = Sim.new(Starting.apply(base))
    assert(sim.try_buy_store_site(Vector2i(26, 12)))
    sim.source_progress["flags"] = 5
    sim.source_progress["mode"] = 1
    # Controlled ten-active-store fixture for the actual ownership caller.
    var context: Dictionary = sim._capture_store()
    for i in 9:
        sim._stores.append(context.duplicate())
    sim._source_store_milestone()
    assert(sim.source_progress["pending"] == 1 and sim.source_progress["flags"] == 7)
    var minute: int = sim.minute_of_day
    sim.tick()
    sim.step()
    assert(not sim.tick_idle_for_demand())
    assert(sim.minute_of_day == minute)
    sim._stores.resize(1)
    sim.source_progress["pending"] = -1
    sim.source_progress["mode"] = 0
    sim.source_progress["flags"] = 0
    sim.program_town.tier = 4
    sim._grow_town_at_month_end()
    assert(sim.source_progress["pending"] == 0 and sim.source_progress["flags"] == 1)
    sim.source_progress["pending"] = -1
    sim.source_progress["flags"] = 3
    sim.source_progress["mode"] = 2
    sim.config["source_scenario_index"] = 2
    sim._chain_visitors_total = 500000
    sim._annual_sales_yen = 600000000
    sim.internal_rating_value = 90
    sim.town.population = 20000
    for i in 9:
        sim._stores.append(sim._capture_store().duplicate())
    sim.month_count = 12
    sim.notifications.reset()
    sim._annual_review()
    assert(sim.source_progress["pending"] == -1)
    sim.consume_source_notice()
    assert(sim.source_progress["pending"] == 2 and sim.source_progress["flags"] == 7)
    sim._stores.resize(1)
    sim.source_progress["pending"] = -1
    sim.economy.cash_yen = -1
    sim.minute_of_day = 10
    sim._evaluate_terminal_state()
    assert(sim.source_progress["pending"] == -1)
    sim.minute_of_day = 0
    sim._evaluate_terminal_state()
    assert(sim.source_progress["pending"] == 4 and sim.source_progress["mode"] == 255)
    assert(sim.source_progress["flags"] == 7)
    print("SOURCE_PROGRESSION_PASS 198 store + 45 terminal + 256 menu + 5 presentation, caller flags and time gate")
    quit()
