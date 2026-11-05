class_name SourceIntegration
extends RefCounted


static func apply(config: Dictionary, index: int) -> void:
    config["simulation"]["source_full_people"] = true
    var tables: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://data/ps1_integration.json"))
    config["source_catalog"] = {"product_ids": tables["product_ids"], "product_images": tables["product_images"]}
    var source: Dictionary = tables["scenarios"][clampi(index, 0, 3)]
    config["source_scenario_index"] = index
    config["source_scenario"] = source.duplicate(true)
    config["scenario_id"] = "ps1-%s-recovered" % str(source["id"])
    config["economy"]["initial_cash_yen"] = int(source["initial_cash"][0])
    config["town"]["population"] = int(source["population"])
    config["town"]["rival_stores"] = source["rivals"].duplicate(true)
    config["town"]["store_count_including_rivals"] = 1 + source["rivals"].size()
    var recovery: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://data/ps1_recovered.json"))
    recovery["town_cells"] = source["town_cells"]
    config["guide_town_map"] = preload("res://scripts/domain/program_town.gd").new(recovery).guide_map(config["guide_town_map"])
    config["guide_town_map"]["rival_stores"] = source["rivals"].duplicate(true)
    for rival in config["guide_town_map"]["rival_stores"]:
        rival["name"] = "ライバル本店" if int(rival["serial"]) == 1 else "ライバル%d号店" % int(rival["serial"])
        rival["role"] = "head" if int(rival["serial"]) == 1 else "branch"
        rival["sprite"] = "map_red_hq"
        rival["buyable"] = int(rival["serial"]) != 1
    config["ps1_program_tables"]["staff_candidates"] = source["staff_candidates"].duplicate(true)
    config["staff"]["manager_staff_id"] = "staff-1"
    var used := {}
    for member in config["staff"]["members"]:
        var id := str(member["candidate_id"])
        if int(source["staff_candidates"][id].get("owner_flags", 0)) != 0 or used.has(id):
            for candidate_id in source["staff_order"]:
                if int(source["staff_candidates"][candidate_id].get("owner_flags", 0)) == 0 and not used.has(candidate_id):
                    id = str(candidate_id)
                    break
        member["candidate_id"] = id
        used[id] = true
    for type_index in config["store_types"].size():
        var entry: Dictionary = config["store_types"][type_index]
        entry["source_empty_layout"] = tables["layouts"][type_index * 5]
        entry["source_layouts"] = tables["layouts"].slice(type_index * 5 + 1, type_index * 5 + 5)
        entry["layout"] = entry["source_layouts"][0].duplicate(true)
    var products: Array = tables["product_ids"]
    for fixture in config["fixture_catalog"]:
        var id := str(fixture["catalog_id"])
        if not recovery["fixture_kind"].has(id):
            continue
        var descriptor: Array = recovery["fixture_records"][int(recovery["fixture_kind"][id])]
        fixture["purchase_price_yen"] = int(descriptor[1])
        fixture["capacity"] = int(descriptor[3])
        if int(descriptor[0]) & 255 == 10:
            fixture["parking_capacity"] = int(descriptor[3])
        fixture["compatible_product_categories"] = []
        for product_index in descriptor.slice(21, 33):
            if int(product_index) < 0:
                break
            fixture["compatible_product_categories"].append(products[int(product_index)])
    config["product_catalog"].append({"catalog_id": "source_special", "sale_price_yen": 0, "restock_unit_cost_yen": 0, "initial_stock_units": 50, "evidence_note": "CONFIRMED_BINARY: source category26 base0, descriptor43 capacity50. No invented demand."})
