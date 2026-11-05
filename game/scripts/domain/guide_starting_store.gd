class_name GuideStartingStore
extends RefCounted

# Task #89: builds the config every new game actually starts from, by laying
# vertical_slice.json's "guide_starting_store" block (the strategy guide's
# p.48 store: CONFIRMED_OFFICIAL 12x8 large floor, CONFIRMED_VISUAL fixture
# positions, PROVISIONAL product readings -- see that block's evidence_note)
# over the top-level prototype store. The top-level prototype store stays
# as-is because the automated test scenarios script exact coordinates in it.
# Returns a new dictionary; the input is not modified.
static func apply(config: Dictionary, scenario_index := 0) -> Dictionary:
    var guide: Dictionary = config["guide_starting_store"]
    var applied: Dictionary = config.duplicate(true)
    applied["scenario_id"] = str(guide["scenario_id"])
    applied["store"] = (guide["store"] as Dictionary).duplicate(true)
    applied["fixtures"] = (guide["fixtures"] as Array).duplicate(true)
    applied["products"] = (guide["products"] as Array).duplicate(true)
    applied["sample_layouts"] = [{
        "sample_id": "guide_p48_layout",
        "label": str(guide["sample_layout_label"]),
        "evidence_note": "The guide p.48 starting arrangement itself (see guide_starting_store.evidence_note), offered as a free 'restore the starting layout' sample.",
        "fixtures": (guide["fixtures"] as Array).duplicate(true),
    }]
    applied["simulation"]["checkout_fixture_id"] = str(guide["checkout_fixture_id"])


    var work: Dictionary = guide["staff_work"]
    applied["simulation"]["restock_trigger_share_of_full"] = float(work["restock_trigger_share_of_full"])
    applied["simulation"]["cleaning_task_enabled"] = bool(work["cleaning_task_enabled"])
    applied["simulation"]["stamina_enabled"] = bool(work["stamina_enabled"])
    applied["simulation"]["building_demand_enabled"] = bool(work["building_demand_enabled"])


    applied["simulation"]["edits_while_open"] = bool(work["edits_while_open"])


    var rules: Dictionary = guide.get("store_rules", {})
    applied["simulation"]["checkout_rotation_enabled"] = bool(rules.get("checkout_rotation_enabled", false))
    applied["simulation"]["customer_types_enabled"] = bool(rules.get("customer_types_enabled", false))
    applied["simulation"]["any_side_catalog_ids"] = (rules.get("any_side_catalog_ids", []) as Array).duplicate()
    applied["simulation"]["fixture_attention"] = (rules.get("fixture_attention", {}) as Dictionary).duplicate()


    applied["simulation"]["edit_front_search"] = bool(rules.get("edit_front_search", false))


    applied["simulation"]["town_growth_enabled"] = config.get("guide_town_map", {}).has("town_growth")


    var hours: Dictionary = guide["business_hours"]
    applied["simulation"]["start_minute_of_day"] = int(hours["start_minute_of_day"])
    applied["simulation"]["business_hours"] = (hours["presets"] as Array).duplicate(true)
    applied["simulation"]["business_hours_default_id"] = str(hours["default_id"])


    var rivals: Array = []
    for rival in config["guide_town_map"]["rival_stores"]:
        rivals.append({
            "id": str(rival["id"]),
            "position": (rival["position"] as Array).duplicate(),
            "permits_held": (rival["permits_held"] as Array).duplicate(),
        })
    applied["town"]["rival_stores"] = rivals
    applied["town"]["store_count_including_rivals"] = 1 + rivals.size()
    for member in applied["staff"]["members"]:
        member["start_subcell"] = (guide["staff_start_subcells"][str(member["id"])] as Array).duplicate()
    applied["customer"]["visit_plan_product_ids"] = (guide["customer_visit_plan_product_ids"] as Array).duplicate()


    applied["customer"]["max_concurrent_customers"] = int(guide["max_concurrent_customers"])
    applied["provisional_restock"]["product_id"] = str(guide["provisional_restock_product_id"])


    applied["economy"]["initial_cash_yen"] = int(config["android_preview"]["starting_cash_yen"])


    if config.has("guide_store_types"):
        var store_types: Dictionary = config["guide_store_types"]
        applied["scenario_id"] = str(store_types["scenario_id"])
        applied["store_types"] = (store_types["types"] as Array).duplicate(true)
        apply_store_type(applied, str(store_types["default_id"]))


    if not Engine.has_meta("legacy_guide_fixture"):
        var recovery: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://data/ps1_recovered.json"))
        var native = preload("res://scripts/domain/program_town.gd").new(recovery)
        applied["guide_town_map"] = native.guide_map(config["guide_town_map"])
        applied["simulation"]["program_recovery_enabled"] = true
        applied["simulation"]["step_game_minutes"] = 2
        applied["customer"]["max_concurrent_customers"] = 10
        applied["scenario_id"] = "ps1-town0001-recovered"
        applied["town"]["population"] = int(recovery["initial_population"])
        applied["town"]["rival_stores"] = [{"id": "rival-hq", "position": [43, 12], "permits_held": []}]
        applied["town"]["store_count_including_rivals"] = 2
        applied["economy"]["initial_cash_yen"] = int(recovery["initial_cash"][0])
        var interiors: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://data/ps1_interiors.json"))
        applied["fixture_catalog"].append_array(interiors["extra_fixture_catalog"])
        for index in applied["store_types"].size():
            var entry: Dictionary = applied["store_types"][index]
            entry["source_layouts"] = []
            for variant in range(1, 5):
                entry["source_layouts"].append(interiors["layouts"][index * 5 + variant])
            entry["layout"] = (entry["source_layouts"][0] as Dictionary).duplicate(true)
            var source_store: Dictionary = entry["layout"]["store"]


            entry["floor_tiles"] = [int(source_store["width_tiles"]) - (5 if index % 2 == 0 else 2), int(source_store["height_tiles"]) - (2 if index % 2 == 0 else 5)]
        applied["customer"]["visit_plan_product_ids"] = []
        apply_store_type(applied, str(config["guide_store_types"]["default_id"]))
    if not Engine.has_meta("legacy_guide_fixture"):
        preload("res://scripts/domain/source_integration.gd").apply(applied, scenario_index)
        apply_store_type(applied, str(config["guide_store_types"]["default_id"]))
    return applied


static func store_type_entry(config: Dictionary, type_id: String) -> Dictionary:
    for entry in config.get("store_types", []):
        if str(entry["id"]) == type_id:
            return entry
    return {}


static func apply_store_type(config: Dictionary, type_id: String) -> void:
    var entry := store_type_entry(config, type_id)
    assert(entry.has("layout"))
    var layout: Dictionary = entry["layout"]
    config["store_type_id"] = type_id
    config["store"] = (layout["store"] as Dictionary).duplicate(true)
    config["fixtures"] = (layout["fixtures"] as Array).duplicate(true)
    config["products"] = (layout["products"] as Array).duplicate(true)
    config["sample_layouts"] = [{
        "sample_id": "opening_layout",
        "label": str(layout["sample_layout_label"]),
        "evidence_note": "The store's own opening arrangement (see guide_store_types.evidence_note), offered as a free 'restore the starting layout' sample.",
        "fixtures": (layout["fixtures"] as Array).duplicate(true),
    }]
    config["simulation"]["checkout_fixture_id"] = str(layout["checkout_fixture_id"])
    for member in config["staff"]["members"]:
        member["start_subcell"] = (layout["staff_start_subcells"][str(member["id"])] as Array).duplicate()
    # REMAKE_BALANCED_DEFAULT: p.48's customer cap scaled by floor area.
    config["customer"]["max_concurrent_customers"] = int(layout["max_concurrent_customers"])
    if bool(config["simulation"].get("program_recovery_enabled", false)):
        config["customer"]["max_concurrent_customers"] = {"small": 10, "medium": 15, "large": 20}.get(str(config["store"]["size_tier"]), 10)
    config["provisional_restock"]["product_id"] = str(layout["provisional_restock_product_id"])
