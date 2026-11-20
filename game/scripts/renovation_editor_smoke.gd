extends SceneTree
const Sim=preload("res://scripts/vertical_slice_simulation.gd")
const Start=preload("res://scripts/domain/guide_starting_store.gd")
func buy(s,id:String) -> void:
    var reasons:Dictionary={}
    for y in s.layout.height_subcells:
        for x in s.layout.width_subcells:
            if s.try_purchase_fixture_at("small_ambient_shelf",id,Vector2i(x,y)):return
            reasons[s.edit_refusal]=int(reasons.get(s.edit_refusal,0))+1
    print("EDITOR_REFUSAL ",reasons)
    assert(false,"Actual editor purchase needs a free spot")
func _initialize() -> void:
    var base:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/vertical_slice.json"))
    var s=Sim.new(Start.apply(base))
    s.economy.cash_yen=1000000000
    assert(s.try_buy_store_site(Vector2i(26,12)))
    assert(s.try_buy_store_site(Vector2i(3,3),"small_top"))
    assert(s.select_store(1))
    s.try_set_business_hours("closed")
    assert(s.try_purchase_permit("alcohol"))
    var root_fixtures:String=JSON.stringify(s.store_field(0,"layout").fixture_snapshot())
    var cash:int=s.economy.cash_yen
    var original:String=s.store_type_id
    var uid:int=s._store_uid
    s.economy._settled_customer_ids["historical-id"]=true
    assert(s.begin_renovation_edit("medium_top",["tobacco","alcohol"],uid,original))
    assert(s.economy.cash_yen==cash-15000000 and s.has_permit("tobacco"))
    var after:int=s.economy.cash_yen
    var count:int=s.economy.expense_records.size()
    var footprint:String=JSON.stringify(s.layout.fixture_snapshot())
    assert(not s.select_store(0) and not s.try_sell_store(1))
    assert(not s.begin_renovation_edit("medium_top"))
    var minute:int=s.minute_of_day
    s.tick();s.step();assert(not s.tick_idle_for_demand())
    assert(s.minute_of_day==minute)
    buy(s,"editor-keep")
    assert(s.economy.cash_yen<after and s.layout.fixtures_by_id.has("editor-keep"))
    assert(s.try_set_source_floor(5))
    var saved:Dictionary=JSON.parse_string(JSON.stringify(s.save_state()))
    var clone=Sim.new(Start.apply(base))
    assert(clone.load_state(saved))
    assert(not clone.renovation_session.is_empty() and clone.select_store(1))
    assert(clone.finish_renovation_edit(true))
    assert(clone.economy.cash_yen==after and clone.economy.expense_records.size()==count)
    assert(clone.layout.fixtures_by_id.has("editor-keep") and clone._permits_held.has("tobacco"))
    assert(clone.economy._settled_customer_ids.has("historical-id"))
    assert(not clone.finish_renovation_edit(true))
    assert(JSON.stringify(clone.store_field(0,"layout").fixture_snapshot())==root_fixtures)
    # Same saved editing state, opposite outcome: undo edit, reverse fees,
    # remove new permit, keep the chosen size and enable a fresh attempt.
    var cancel=Sim.new(Start.apply(base))
    assert(cancel.load_state(saved) and cancel.select_store(1))
    assert(cancel.finish_renovation_edit(false))
    assert(cancel.economy.cash_yen==cash and cancel.store_type_id=="medium_top")
    assert(not cancel.has_permit("tobacco") and cancel.has_permit("alcohol") and not cancel.layout.fixtures_by_id.has("editor-keep"))
    assert(JSON.stringify(cancel.layout.fixture_snapshot())==footprint)
    assert(cancel.economy.expense_records.size()==count+2)
    assert(int(cancel.economy.expense_records[-2].amount_yen)==-12000000)
    assert(int(cancel.economy.expense_records[-1].amount_yen)==-3000000)
    assert(int(cancel.economy.expense_records[-1].store_uid)==uid)
    assert(cancel.begin_renovation_edit("medium_top"))
    var paid:int=cancel.economy.cash_yen
    assert(cancel.try_sell_fixture(str(cancel.layout.fixtures[-1].id)))
    assert(cancel.economy.cash_yen>=paid)
    assert(cancel.finish_renovation_edit(true) and cancel.economy.cash_yen==paid)
    var valid:Dictionary=JSON.parse_string(JSON.stringify(cancel.save_state()))
    var bad:Dictionary=valid.duplicate(true);bad.renovation_session=[]
    assert(not Sim.new(Start.apply(base)).load_state(bad))
    var final=Sim.new(Start.apply(base))
    assert(final.load_state(valid) and final.renovation_session.is_empty())
    print("RENOVATION_EDITOR_PASS actual purchase/sale/floor edits, commit/cancel finance, selected-size retention, permit refund, branch isolation, paused ticks, pending JSON and retry")
    quit()
