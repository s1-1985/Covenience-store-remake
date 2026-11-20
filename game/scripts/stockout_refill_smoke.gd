extends SceneTree
const Sim=preload("res://scripts/vertical_slice_simulation.gd")
const Start=preload("res://scripts/domain/guide_starting_store.gd")
const Rules=preload("res://scripts/domain/program_rules.gd")
const RNG=preload("res://scripts/domain/program_random.gd")
const People=preload("res://scripts/domain/program_people.gd")
const Customer=preload("res://scripts/domain/customer_state.gd")
func setup():
    var base:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/vertical_slice.json"))
    var s=Sim.new(Start.apply(base));s.economy.cash_yen=1000000000
    assert(s.try_buy_store_site(Vector2i(26,12)))
    return s
func events(s,kind:String) -> int:
    return s.event_log.snapshot().filter(func(e):return str(e.event_type)==kind).size()
func _initialize() -> void:
    var fixture:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://tests/fixtures/source_stockout_refill.json"))
    var s=setup();var id:String=s.inventory.product_order[0]
    var product=s.inventory.get_product(id)
    for row in fixture.acquisitions:
        product.stock_units=int(row.stock);s._notice_counts.sold_out=int(row.counter)
        var seed:int=s._program_rng.seed;var cash:int=s.economy.cash_yen
        var line:Dictionary=s._take_source_product("missing" if bool(row.mismatch) else id,int(row.heads))
        assert(line.is_empty()==bool(row.failed) and product.stock_units==int(row.stock_after))
        assert(s._notice_counts.sold_out==int(row.counter_after) and s.economy.cash_yen==cash and s._program_rng.seed==seed)
        assert(s.survey_missing.is_empty(),"Failed item calls are distinct from unmet-demand heads")
    for row in fixture.refills:
        var rng=RNG.new();rng.seed=int(row.seed)
        var amount:int=Rules.refill_amount(int(row.ability),rng)
        assert(mini(40-int(row.stock),amount)==int(row.stock_after)-int(row.stock) and rng.seed==int(row.seed_after))
        product.stock_units=int(row.stock);product.initial_stock_units=40;product.restock_unit_cost_yen=360
        var person=s.staff.members["staff-2"]
        person.replenishment_skill=int(row.ability);person.restock_target_product_id=id
        s._program_rng.seed=int(row.seed)
        var before:int=events(s,"source_restock_completed");var cash:int=s.economy.cash_yen
        s._complete_restock(person)
        assert(product.stock_units==int(row.stock_after) and cash-s.economy.cash_yen==int(row.cost))
        assert(events(s,"source_restock_completed")==before+int(int(row.status)==0))
        if int(row.status)==1:
            assert(person.restock_target_product_id==id and s._program_rng.seed==int(row.seed_after))
    # Actual purchase path: one failed group acquisition, not group-size count.
    s=setup();id=s.inventory.product_order[0];product=s.inventory.get_product(id)
    var f:Dictionary=s.layout.fixtures_by_id[product.fixture_id]
    var p=Customer.new({"id":"stockout"});p.source_native=true;p.source_state=2;p.phase="shopping"
    p.source_wanted=product.catalog_id;p.group_size=3;p.budget_left=9999;p.visit={"quickness":100,"manners":0}
    p.position=s._vec2i_from_array(f.origin_subcell)+Vector2i(0,2);p.source_goal=p.position;p.source_direction=0;p.source_goal_direction=0
    product.stock_units=2;s._notice_counts.sold_out=0
    People.customer(s,p)
    assert(s._notice_counts.sold_out==1 and product.stock_units==2 and p.budget_left==9999 and s.survey_missing.is_empty(),str([s._notice_counts.sold_out,product.stock_units,p.budget_left,s.survey_missing,f,p.position,p.source_wanted]))
    assert(not s._source_try_theft(p,id) and s._notice_counts.sold_out==2 and product.stock_units==2)
    # Stockout observations, unlike demand survey, persist per owned store.
    var first:int=s._notice_counts.sold_out
    assert(s.try_buy_store_site(Vector2i(3,3),"small_top"))
    s.select_store(1)
    assert(s._notice_counts.sold_out==0)
    s._take_source_product("missing",5)
    assert(s._notice_counts.sold_out==1)
    s.select_store(0);assert(s._notice_counts.sold_out==first)
    var clone=setup();assert(clone.load_state(JSON.parse_string(JSON.stringify(s.save_state()))))
    assert(clone._notice_counts.sold_out==first)
    clone.select_store(1);assert(clone._notice_counts.sold_out==1)
    s.minute_of_day=1
    for i in 20:s._take_source_product("missing",5)
    var reports:int=events(s,"manager_report")
    s._step_manager_reports()
    assert(events(s,"manager_report")==reports+1 and s._notice_counts.sold_out==0)
    assert(int(s.config.sound.source_event_sounds.source_restock_completed)==int(fixture.completion_sound))
    print("STOCKOUT_REFILL_PASS 55 original acquisitions/30 refills; one-call counters, floors, full-only completion, real purchase/theft callers, per-store JSON")
    quit()
