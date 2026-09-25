class_name GuideStartingStore
extends RefCounted

# Task #89: builds the config every new game actually starts from, by laying
# vertical_slice.json's "guide_starting_store" block (the strategy guide's
# p.48 store: CONFIRMED_OFFICIAL 12x8 large floor, CONFIRMED_VISUAL fixture
# positions, PROVISIONAL product readings -- see that block's evidence_note)
# over the top-level prototype store. The top-level prototype store stays
# as-is because the automated test scenarios script exact coordinates in it.
# Returns a new dictionary; the input is not modified.
static func apply(config: Dictionary) -> Dictionary:
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
    # Task #97 (REMAKE_BALANCED_DEFAULT, see staff_work.evidence_note):
    # staff refill shelves once they visibly go down, and clean.
    var work: Dictionary = guide["staff_work"]
    applied["simulation"]["restock_trigger_share_of_full"] = float(work["restock_trigger_share_of_full"])
    applied["simulation"]["cleaning_task_enabled"] = bool(work["cleaning_task_enabled"])
    applied["simulation"]["stamina_enabled"] = bool(work["stamina_enabled"])
    applied["simulation"]["building_demand_enabled"] = bool(work["building_demand_enabled"])
    # Task #98: the rival's 本店 and 2号店 on the town map (see
    # guide_town_map.rival_stores: CONFIRMED_OFFICIAL that they exist,
    # REMAKE_BALANCED_DEFAULT where they stand).
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
    # REMAKE_BALANCED_DEFAULT cap anchored to a CONFIRMED_VISUAL count (see
    # max_concurrent_customers_evidence_note in the guide block).
    applied["customer"]["max_concurrent_customers"] = int(guide["max_concurrent_customers"])
    applied["provisional_restock"]["product_id"] = str(guide["provisional_restock_product_id"])
    # CONFIRMED_COMMUNITY beginner starting cash (android_preview's own
    # anchor, docs/research/ui-consistency-audit-2026-09-05.md), and
    # CONFIRMED_VISUAL since task #90: the guide p.11 beginner-map screenshot
    # reads 1年目1月1日 00:00 ¥200,000,000 (assets/raw/conveni_guide_town_v1).
    # A furnished
    # large store's daily upkeep would bankrupt the prototype's 1,000 yen at
    # the first day boundary.
    applied["economy"]["initial_cash_yen"] = int(config["android_preview"]["starting_cash_yen"])
    return applied
