extends SceneTree
const Sim=preload("res://scripts/vertical_slice_simulation.gd")
const Start=preload("res://scripts/domain/guide_starting_store.gd")
const Calendar=preload("res://scripts/domain/program_calendar.gd")
const RNG=preload("res://scripts/domain/program_random.gd")
var base:Dictionary
func native():return Sim.new(Start.apply(base))
func _initialize() -> void:
    base=JSON.parse_string(FileAccess.get_file_as_string("res://data/vertical_slice.json"))
    var fixture:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://tests/fixtures/source_calendar.json"))
    for row in fixture.arrivals:
        var actual:Dictionary=Calendar.arrival(int(row.before),int(row.heads),int(row.pending_before))
        assert(int(actual.total)==int(row.total) and int(actual.pending)==int(row.pending_after))
    for row in fixture.popularity:
        assert(Calendar.celebration_popularity(int(row.popularity),bool(row.active),int(row.owner))==int(row.after))
    for row in fixture.displays:
        var entries:Array=[]
        for i in 4:entries.append({"active":bool(row.active[i]),"owner":int(row.owners[i]),"entered":int(row.counts[i])})
        assert(Calendar.display_total(entries)==int(row.total))
    assert(Calendar.midnight_kind(8,4,1)=="festival")
    assert(Calendar.midnight_kind(8,3,1)=="celebration")
    assert(Calendar.midnight_kind(8,3,0x80000000)=="")
    var s=native()
    s.economy.cash_yen=1000000000
    assert(s.try_buy_store_site(Vector2i(26,12)))
    assert(s.try_buy_store_site(Vector2i(3,3),"small_top"))
    s.select_store(1);s.try_set_business_hours("closed");s._store_visitor_heads=3
    s.select_store(0);s.try_set_business_hours("closed");s._store_visitor_heads=9999
    s._chain_visitors_total=9999
    # The actual native admission caller crosses without landing on10000.
    var row:Dictionary=s._program_demand.rows[0]
    s._start_program_customer(row,3)
    assert(s._chain_visitors_total==10002 and int(s.source_calendar.pending)==1)
    s._observe_chain_visitor_milestone(20000)
    assert(s._chain_visitors_total==30002 and int(s.source_calendar.pending)==3)
    var actor_before:Dictionary=s._source_runtime_snapshot()
    s.minute_of_day=1438;s._days_completed_this_month=0
    var expected=RNG.new();expected.seed=s._program_rng.seed
    var variant:int=expected.randi()%2
    s._advance_minute_of_day()
    assert(s.source_calendar_blocked() and s.source_calendar.event.kind=="celebration")
    assert(int(s.source_calendar.event.units)==1,"Display is current own store sum, not global quotient3")
    assert(int(s.source_calendar.event.variant)==variant and s._program_rng.seed==expected.seed)
    assert(int(s.source_calendar.pending)==0 and s.popularity!=100)
    assert(JSON.stringify(s._source_runtime_snapshot())==JSON.stringify(actor_before))
    var frozen:String=JSON.stringify(s.save_state())
    for i in 64:s.tick()
    assert(JSON.stringify(s.save_state())==frozen,"16x debt must not move the game behind presentation")
    assert(not s.finish_source_calendar_event())
    assert(not s.advance_source_calendar_presentation(119,false) and s.popularity!=100)
    assert(not s.advance_source_calendar_presentation(1,true) and s.popularity!=100)
    var saved:Dictionary=JSON.parse_string(JSON.stringify(s.save_state()))
    assert(Calendar.valid(saved.source_calendar))
    var clone=native();assert(clone.load_state(saved))
    assert(clone.source_calendar_blocked() and int(clone.source_calendar.event.wait_updates)==120)
    var rating:int=s.internal_rating_value
    var cash:int=s.economy.cash_yen
    assert(s.advance_source_calendar_presentation(0,false) and clone.advance_source_calendar_presentation(0,false))
    assert(s.popularity==100 and int(s.store_field(1,"popularity"))==100)
    for rival in s._rival_stores:assert(s._program_rival_simulation(rival).popularity==100)
    assert(s.internal_rating_value==rating and s.economy.cash_yen==cash)
    assert(comparable(s)==comparable(clone),"Mid-event load must resume the same effects/allocation/RNG")
    assert(not s.finish_source_calendar_event())
    # Festival priority preserves pending and consumes no celebration variant.
    var festival=native();festival.economy.cash_yen=1000000000
    assert(festival.try_buy_store_site(Vector2i(26,12)))
    festival.try_set_business_hours("closed");festival._store_visitor_heads=20000
    festival.month_count=7;festival._days_completed_this_month=2;festival.minute_of_day=1438
    festival.source_calendar.pending=2
    var seed:int=festival._program_rng.seed
    festival._advance_minute_of_day()
    assert(festival.source_calendar.event.kind=="festival" and festival._program_rng.seed==seed)
    assert(int(festival.source_calendar.pending)==2 and int(festival.source_calendar.festival)==0)
    var festival_pop:int=festival.popularity
    assert(festival.advance_source_calendar_presentation(120,false))
    assert(festival.popularity==festival_pop and int(festival.source_calendar.pending)==2 and int(festival.source_calendar.festival)==1)
    # Next midnight is also month end. Donation/ratings before event, finance after.
    festival.economy.cash_yen=1600000000;festival._rival_cash_yen=0
    festival.minute_of_day=1438
    var closes:int=festival.economy.month_end_records.size()
    festival._advance_minute_of_day()
    assert(festival.source_calendar.event.kind=="celebration" and int(festival.source_calendar.pending)==0)
    assert(festival.economy.cash_yen==1000000000 and festival.economy.month_end_records.size()==closes)
    assert(festival.month_count==7 and bool(festival.source_calendar.boundary.closing))
    var midmonth:Dictionary=JSON.parse_string(JSON.stringify(festival.save_state()))
    var resumed=native();assert(resumed.load_state(midmonth))
    assert(resumed.advance_source_calendar_presentation(120,false) and festival.advance_source_calendar_presentation(120,false))
    assert(festival.month_count==8 and festival.economy.month_end_records.size()==closes+1 and festival.popularity==100)
    assert(comparable(resumed)==comparable(festival))
    assert(festival.economy.expense_records.filter(func(e):return e.expense_type=="company_donation").size()==1)
    # Original early screen return still performs the parent's popularity writes.
    var early=native();assert(early.try_buy_store_site(Vector2i(26,12)))
    early.try_set_business_hours("closed");early._store_visitor_heads=9999;early.source_calendar.pending=1
    early.minute_of_day=1438;early._advance_minute_of_day()
    assert(not early.source_calendar_blocked() and early.popularity==100 and int(early.source_calendar.pending)==0)
    # The global arrival counter uses unsigned32; an overflow does not catch up.
    early._chain_visitors_total=0xfffffffe;early.source_calendar.pending=17
    early._observe_chain_visitor_milestone(3)
    assert(early._chain_visitors_total==1 and int(early.source_calendar.pending)==17)
    var legacy:Dictionary=saved.duplicate(true);legacy.erase("source_calendar")
    legacy.chain_visitor_milestone.events=[{"threshold_visitors":10000,"fired":true},{"threshold_visitors":20000,"fired":false}]
    assert(clone.load_state(legacy) and int(clone.source_calendar.pending)==2 and not clone.source_calendar_blocked())
    var bad:Dictionary=midmonth.duplicate(true);bad.source_calendar.boundary.statement.adjustment_yen="bad"
    assert(not resumed.load_state(bad))
    bad=midmonth.duplicate(true);bad.source_calendar.event.wait_updates=121
    assert(not resumed.load_state(bad))
    print("CALENDAR_PASS 14 original excerpts, native arrival crossing/coalescing/wrap, separate display count, midnight festival priority, one RNG draw, paused actors, OR popularity, no cash reward, before-finance continuation and mid-event JSON replay")
    quit()

# Old runtime restore materializes absent cleanliness defaults. Compare full
# saved state semantically, including those documented0/-1 defaults, not JSON
# spellings of equivalent integer/floating-point values after parsing.
func comparable(sim) -> Dictionary:
    var data:Dictionary=JSON.parse_string(JSON.stringify(sim.save_state()))
    fill_defaults(data)
    return data
func fill_defaults(value: Variant) -> void:
    if value is Dictionary:
        if value.get("source_store_config") is Dictionary:
            var config:Dictionary=value.source_store_config
            if not config.has("source_previous_cleanliness"):config.source_previous_cleanliness=0.0
            if not config.has("source_floor_clock"):config.source_floor_clock=-1.0
        for child in value.values():fill_defaults(child)
    elif value is Array:
        for child in value:fill_defaults(child)
