extends SceneTree
const Sim=preload("res://scripts/vertical_slice_simulation.gd")
const Start=preload("res://scripts/domain/guide_starting_store.gd")
const Pricing=preload("res://scripts/domain/program_pricing.gd")
func _initialize() -> void:
    var evidence:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://tests/fixtures/source_pricing.json"))
    for case in evidence.group_cases:
        var after:Array=Pricing.step(case.values,int(case.delta))
        assert(after.is_empty()==not bool(case.allowed))
        if case.allowed:
            for i in 26:assert(int(after[i])==int(case.after[i]))
    for product in evidence.products:
        for i in 3:
            assert(Pricing.unit(int(product.base),int(product.cost),int([0,product.default,100][i]))==int(product.units[i]))
    var base:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/vertical_slice.json"))
    var s=Sim.new(Start.apply(base))
    s.economy.cash_yen=1000000000
    assert(s.try_buy_store_site(Vector2i(26,12)))
    var initial:Dictionary=s.source_price_settings()
    assert(initial.size()==26 and not initial.has(str(s._recovery.product_ids[26])))
    var draft:Dictionary=initial.duplicate()
    var id:String=s._recovery.product_ids[0]
    var cash:int=s.economy.cash_yen
    var seed:int=s._program_rng.seed
    var count:int=s.event_log.records.size()
    draft[id]=101
    assert(not s.try_commit_source_prices(draft))
    draft[id]=-1
    assert(not s.try_commit_source_prices(draft))
    draft[id]=0.5
    assert(not s.try_commit_source_prices(draft))
    assert(s.source_price_settings()==initial and s.event_log.records.size()==count)
    draft=initial.duplicate()
    draft.erase(id)
    assert(not s.try_commit_source_prices(draft))
    draft=initial.duplicate()
    draft[id]=int(initial[id])+1
    assert(not s.try_commit_source_prices(draft,s._store_uid+1,initial))
    assert(s.try_commit_source_prices(draft,s._store_uid,initial))
    assert(s._program_rng.seed==seed and s.economy.cash_yen==cash)
    assert(s.source_price_setting(id)==int(initial[id])+1 and s.event_log.records.size()==count+1)
    assert(not s.try_commit_source_prices(initial,s._store_uid,initial),"Stale preview must not overwrite a newer value")
    count=s.event_log.records.size()
    assert(s.try_commit_source_prices(draft) and s.event_log.records.size()==count)
    var saved:Dictionary=JSON.parse_string(JSON.stringify(s.save_state()))
    var clone=Sim.new(Start.apply(base))
    assert(clone.load_state(saved) and clone.source_price_settings()==draft)
    assert(s.try_buy_store_site(Vector2i(3,3),"small_top") and s.select_store(1))
    assert(s.source_price_settings()==initial)
    assert(s.try_set_product_price(id,100))
    var state:Dictionary=s.source_price_settings()
    assert(not s.try_set_price_policy(s.price_change_pct+1) and s.source_price_settings()==state)
    assert(s.select_store(0) and s.source_price_settings()==draft)
    # Actual native pickup baskets must use the edited coefficient.
    var live=Sim.new(Start.apply(base))
    assert(live.try_buy_store_site(Vector2i(26,12)))
    var live_settings:Dictionary=live.source_price_settings()
    for category in live_settings:live_settings[category]=int(live_settings[category])+1
    assert(live.try_commit_source_prices(live_settings))
    var units:Dictionary={}
    for row in live.source_price_preview(live_settings):units[row.category]=int(row.unit_yen)
    var checked:=0
    for tick in 1100:
        live.tick()
        for customer in live.customers.active_customers():
            for line in customer.basket:
                var product=live.inventory.get_product(str(line.product_id))
                assert(int(line.unit_price_yen)==int(units[product.catalog_id]))
                checked+=1
    assert(checked>0 and live.economy.completed_sales>0)
    print("PRICING_PASS 8 original group boundaries, 78 table-derived prices, atomic validation, stale guards, limits, save, branch isolation and real pickup prices")
    quit()
