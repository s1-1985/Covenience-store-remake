extends SceneTree
const Survey=preload("res://scripts/domain/program_survey.gd")
const Sim=preload("res://scripts/vertical_slice_simulation.gd")
const Starting=preload("res://scripts/domain/guide_starting_store.gd")
func _init() -> void:
    var fixture: Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://tests/fixtures/source_survey.json"))
    fixture.cases.append_array(JSON.parse_string(FileAccess.get_file_as_string("res://tests/fixtures/source_survey_boundaries.json")).cases)
    var order: Array=[]
    for i in 27: order.append(str(i))
    for case in fixture.cases:
        for col in ["left","right"]:
            var counts: Dictionary={}
            for i in 27: counts[str(i)]=case[col+"_u32"][i]
            var rows: Array=Survey.rank(counts,order)
            var calls: Array=[]
            for call in case.captured_text_calls:
                if call.x==(32 if col=="left" else 164): calls.append(call)
            assert(rows.size()==calls.size())
            for i in rows.size():
                assert(rows[i].index==calls[i].message-71,"Original ranking/order mismatch")
    assert(Survey.rank({"0":-1,"1":4},order)[0].count==4294967295)
    var wrapped: Dictionary={"0":4294967295}
    Survey.add(wrapped,"0",1)
    assert(Survey.rank(wrapped,order).is_empty())
    var base: Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/vertical_slice.json"))
    var sim=Sim.new(Starting.apply(base))
    assert(sim.try_buy_store_site(Vector2i(26,12)))
    var expected: Dictionary={}
    var held_before_checkout:=false
    for tick in 1100:
        var before: int=sim.event_log.records.back().sequence if not sim.event_log.records.is_empty() else 0
        sim.tick()
        for event in sim.event_log.records:
            if event.sequence<=before or event.event_type!="product_picked": continue
            var product=sim.inventory.get_product(str(event.details.product_id))
            var person=sim.customers.customers[str(event.details.customer_id)]
            Survey.add(expected,product.catalog_id,person.group_size)
        for id in sim.config["source_catalog"]["product_ids"]:
            assert(int(sim.survey_bought.get(id,0))==int(expected.get(id,0)),"Picked counts must match collection events, not checkout events")
        for person in sim.customers.active_customers():
            if not person.basket.is_empty() and not held_before_checkout:
                held_before_checkout=true
                # Force one shopper to leave before payment: picked-product
                # votes must remain even when this basket never reaches checkout.
                person.basket.clear()
                person.source_state=5
                person.source_goal=Vector2i(-1,-1)
    assert(held_before_checkout and sim.economy.completed_sales>0)
    var id: String=sim.inventory.product_order[0]
    var category: String=sim.inventory.get_product(id).catalog_id
    sim.survey_missing.clear()
    sim.inventory.get_product(id).stock_units=5
    sim._record_source_survey_missing(category,2)
    assert(sim.survey_missing.is_empty(),"A route/fixture failure with stock is not a missing-product vote")
    for product in sim.inventory.products.values():
        if product.catalog_id==category: product.stock_units=0
    sim._record_source_survey_missing(category,2)
    assert(sim.survey_missing[category]==2)
    sim.economy.cash_yen=1000000000
    assert(sim.try_buy_store_site(Vector2i(3,3),"small_top"))
    sim.select_store(1)
    assert(sim.survey_bought.is_empty())
    sim._record_source_survey_pick(str(sim.inventory.product_order[0]),3)
    var branch: Dictionary=sim.survey_bought.duplicate()
    sim.select_store(0)
    assert(sim.survey_bought==expected)
    var saved: Dictionary=JSON.parse_string(JSON.stringify(sim.save_state()))
    var clone=Sim.new(Starting.apply(base))
    assert(clone.load_state(saved))
    assert(clone.survey_bought==expected and not clone.survey_legacy_totals)
    clone.select_store(1)
    assert(clone.survey_bought==branch)
    # Legacy saves keep their existing totals but explicitly label the old semantics.
    var old: Dictionary=saved.duplicate(true)
    # Save schema stores store0 at the root and additional stores as blocks.
    old["survey"].erase("source_counter_version")
    old["survey"].erase("legacy_totals")
    var migrated=Sim.new(Starting.apply(base))
    assert(migrated.load_state(old))
    assert(migrated.survey_legacy_totals and migrated.survey_bought==expected)
    migrated._for_each_store(migrated._close_store_month)
    for i in migrated.store_count():
        assert(migrated.store_field(i,"survey_bought").is_empty())
        assert(migrated.store_field(i,"survey_missing").is_empty())
        assert(not migrated.store_field(i,"survey_legacy_totals"))
    print("SOURCE_SURVEY_PASS 8 original ranking cases; u32 ties/wrap; 1100 native ticks exact picks without checkout duplication; stockout guard; two stores; save/load; legacy label; monthly reset")
    quit()
