extends SceneTree
const Sim := preload("res://scripts/vertical_slice_simulation.gd")
const G := preload("res://scripts/domain/guide_starting_store.gd")
func _init() -> void:
    var fresh: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://data/vertical_slice.json"))
    var sim = Sim.new(G.apply(fresh))
    sim.try_buy_store_site(Vector2i(13, 21), "small_top")
    var last_visits := 0
    for month in 12:
        for day in 4:
            for m in 1440:
                sim.tick()
        var rec: Dictionary = sim.economy.month_end_records[-1]["details"] if not sim.economy.month_end_records.is_empty() else {}
        var snap: Dictionary = sim.snapshot()
        var stuck := []
        for member in sim.staff.all_staff():
            stuck.append("%s:%s/%s st%d" % [member.staff_id, member.state, member.rest_phase, member.stamina])
        print("m%02d cash=%d result=%s sales=%s visits=%d stock=%d star=%d pop=%d anger=%d rivals=%d over=%s %s" % [
            month + 1, sim.economy.cash_yen, rec.get("month_result_yen"), rec.get("month_sales_yen"),
            int(snap["completed_visits"]) - last_visits, sim.inventory.total_stock_units(), sim.star_rating, sim.popularity,
            sim.event_log.count_type("checkout_anger_triggered"), sim._rival_stores.size(), sim.is_game_over, stuck])
        last_visits = int(snap["completed_visits"])
    quit(0)
