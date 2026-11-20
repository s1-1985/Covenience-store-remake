extends SceneTree
const Sim = preload("res://scripts/vertical_slice_simulation.gd")
const Start = preload("res://scripts/domain/guide_starting_store.gd")
const Permits = preload("res://scripts/domain/program_permits.gd")
func _initialize() -> void:
    var fixture: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://tests/fixtures/source_permits.json"))
    for case in fixture.query_cases:
        var cells: Array = []
        for i in 3000: cells.append([0,0,0,0,0,0])
        for point in case.points: cells[int(point[1])*60+int(point[0])][4]=int(point[2])
        var r: Array = case.rect
        assert(Permits.restricted(cells,Rect2i(int(r[0]),int(r[1]),int(r[2])-int(r[0])+1,int(r[3])-int(r[1])+1),str(case.permit_id))==bool(case.restricted),str(case.name))
    var base: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://data/vertical_slice.json"))
    var s = Sim.new(Start.apply(base))
    s.economy.cash_yen=1000000000
    assert(s.try_buy_store_site(Vector2i(26,12)))
    assert(s.try_buy_store_site(Vector2i(20,12),"small_top"))
    s.select_store(0)
    var order: Array = Permits.IDS.duplicate()
    for i in 3: assert(int(s._permit_catalog[order[i]].fee_yen)==int(fixture.fees[i]))
    var quote: Dictionary = s.permit_application_quote(order)
    assert(quote.allowed and quote.total_yen==20000000)
    var count: int = s.economy.expense_records.size()
    s.economy.cash_yen=19999999
    assert(not s.try_purchase_permits(order))
    assert(s._permits_held.is_empty() and s.economy.expense_records.size()==count)
    s.economy.cash_yen=20000000
    assert(s.try_purchase_permits(order,int(quote.store_uid)))
    assert(s.economy.cash_yen==0 and s.economy.expense_records.size()==count+3)
    for id in order: assert(s.has_permit(id))
    assert(not s.try_purchase_permits(order) and s.economy.cash_yen==0)
    assert(s.permit_application_quote(order).total_yen==0)
    s.select_store(1)
    assert(not s._can_acquire_permit("tobacco"),"One overlapping corner of actual branch footprint is restricted by own chain")
    assert(not s.store_site_quote(Vector2i(20,12)).permits_available.tobacco)
    s.economy.cash_yen=1000000000
    count=s.economy.expense_records.size()
    assert(not s.try_purchase_permits(["tobacco"]))
    assert(s._permits_held.is_empty() and s.economy.expense_records.size()==count)
    var cash: int = s.economy.cash_yen
    assert(not s.try_purchase_permits(["alcohol"],int(quote.store_uid)))
    assert(s.economy.cash_yen==cash)
    var saved: Dictionary = JSON.parse_string(JSON.stringify(s.save_state()))
    var clone = Sim.new(Start.apply(base))
    assert(clone.load_state(saved))
    assert(not clone._can_acquire_permit("tobacco"))
    clone.select_store(0)
    assert(clone.has_permit("tobacco") and clone.permit_application_quote(order).allowed)
    clone.select_store(1)
    assert(clone.try_set_business_hours("closed"))
    assert(clone.try_sell_store(1))
    # Remaining store's existing permissions stay held even though its own
    # map overlay necessarily contains restriction bits.
    assert(clone.permit_application_quote(order).allowed)
    assert(clone.permit_application_quote(order).total_yen==0)
    var other=Sim.new(Start.apply(base))
    other.economy.cash_yen=1000000000
    assert(other.try_buy_store_site(Vector2i(26,12)))
    assert(other.try_buy_store_site(Vector2i(20,12),"small_top"))
    other.select_store(1)
    assert(not other._can_acquire_permit("tobacco"),"Initial rival overlay must also restrict issuance")
    # Isolate the own-chain geometry from the recovered rival at (14,10).
    other._rival_stores.clear()
    assert(other.try_purchase_permits(["tobacco","tobacco"]))
    var branch_uid: int=other._store_uid
    other.select_store(0)
    var old_count: int=other.economy.expense_records.size()
    var old_cash: int=other.economy.cash_yen
    # An available alcohol request must not be partially charged when the
    # same batch also contains restricted tobacco.
    assert(other._can_acquire_permit("alcohol"))
    assert(not other.try_purchase_permits(["alcohol","tobacco"]))
    assert(other._permits_held.is_empty() and other.economy.cash_yen==old_cash and other.economy.expense_records.size()==old_count)
    other.select_store(1)
    assert(other.try_set_business_hours("closed"))
    assert(other.try_sell_store(1,branch_uid))
    assert(other._can_acquire_permit("tobacco"),"Sold branch overlay must disappear")
    assert(other.try_purchase_permit("tobacco"))
    # Legacy synthetic point scenarios retain their isolated guide fixture.
    var legacy=Sim.new(base)
    assert(int(legacy._permit_catalog.tobacco.fee_yen)==7000000)
    print("PERMIT_PASS 18 original queries, source fees, exact cash, atomic rollback, own-chain rectangle, stable UID, existing flags, save and sale")
    quit()
