extends SceneTree
const Starting := preload("res://scripts/domain/guide_starting_store.gd")
const Sim := preload("res://scripts/vertical_slice_simulation.gd")

func _initialize() -> void:
    var base: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://data/vertical_slice.json"))
    var source: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://data/ps1_integration.json"))
    assert(source["layouts"].size() == 30)
    assert("REMAKE_BALANCED_DEFAULT" in str(source["evidence_note"]))
    var checked := 0
    for type_index in 6:
        for variant in 4:
            var config := Starting.apply(base)
            var entry: Dictionary = config["store_types"][type_index]
            entry["layout"] = (entry["source_layouts"][variant] as Dictionary).duplicate(true)
            Starting.apply_store_type(config, str(entry["id"]))
            var sim = Sim.new(config)
            assert(not sim.has_outdoor_lot(), "source grid already includes exterior")
            var original: Dictionary = source["layouts"][type_index * 5 + variant + 1]
            assert(sim.layout.width_subcells == int(original["store"]["width_tiles"]) * 2)
            assert(sim.layout.height_subcells == int(original["store"]["height_tiles"]) * 2)
            for cell in original["store"]["blocked_subcells"]:
                assert(not sim.layout.is_walkable(Vector2i(int(cell[0]), int(cell[1]))))
            assert(sim._required_routes_are_reachable())
            var fee: int = sim.store_type_price_yen(str(entry["id"]))
            assert(fee == int(entry["construction_price_yen"]) + int(original["source_equipment_yen"]) + int(original["source_goods_yen"]))
            var cash: int = sim.economy.cash_yen
            var land: int = sim.store_site_quote(Vector2i(26,12))["total_yen"]
            # All six types may be inspected/renovated, but only small stores
            # may be bought initially, matching the existing source gate.
            if type_index < 2:
                assert(sim.try_buy_store_site(Vector2i(26,12), str(entry["id"])))
                assert(sim.economy.cash_yen == cash - land - fee)
                for tick in 2000:
                    sim.tick()
                assert(sim._store_sales_yen > 0, "customers must buy in every small source sample")
            var serialized: Dictionary = JSON.parse_string(JSON.stringify(sim.save_state()))
            var clone = Sim.new(config)
            assert(clone.load_state(serialized))
            assert(clone.config["store"]["source_floor"] == sim.config["store"]["source_floor"])
            assert(clone.inventory.total_stock_units() == sim.inventory.total_stock_units())
            for cell in original["store"]["blocked_subcells"]:
                assert(not clone.layout.is_walkable(Vector2i(int(cell[0]), int(cell[1]))))
            checked += 1
    print("Source interiors: %d layouts, original walls, routes, opening fees, purchases and JSON reload passed" % checked)
    quit(0)
