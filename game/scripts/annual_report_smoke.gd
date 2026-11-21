extends SceneTree
const Sim=preload("res://scripts/vertical_slice_simulation.gd")
const Start=preload("res://scripts/domain/guide_starting_store.gd")
const Annual=preload("res://scripts/domain/program_annual.gd")
const Progress=preload("res://scripts/domain/program_progression.gd")
func setup():
    var base:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/vertical_slice.json"))
    var s=Sim.new(Start.apply(base));s.economy.cash_yen=1000000000
    assert(s.try_buy_store_site(Vector2i(26,12)))
    assert(s.try_buy_store_site(Vector2i(3,3),"small_top"))
    s._for_each_store(func():s.try_set_business_hours("closed"))
    s.notifications.reset()
    return s
func _initialize() -> void:
    var fixture:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://tests/fixtures/source_annual.json"))
    for row in fixture.additions:assert(Annual.add_sales(int(row.current),int(row.monthly))==int(row.expected))
    for row in fixture.rollovers:
        var result:Array=Annual.rollover(int(row.current),row.previous)
        assert(result.size()==row.expected.size())
        for i in result.size():assert(int(result[i])==int(row.expected[i]))
    for row in fixture.evaluations:
        var entries:Array=[]
        for i in int(row.count):entries.append({"annual_sales":int(row.sales),"rating":int(row.rating)})
        var result:Dictionary=Progress.owner_rating(entries,int(row.visitors),int(row.population))
        assert(result.total==int(row.total) and result.annual_sales==int(row["values"][2]))
        for i in 5:assert(int(result.parts[i])==int(row.parts[i]))
    assert(Annual.add_sales(2147483647,1)==-2147483648 and Annual.add_sales(-2147483648,-1)==2147483647)
    var s=setup();s.month_count=11;s._days_completed_this_month=3;s.minute_of_day=1438
    s._chain_visitors_total=50000
    s.select_store(0);s._annual_sales_yen=100000000;s._source_annual_sales_history=[80,70,60];s._store_sales_yen=12500000
    s.select_store(1);s._annual_sales_yen=300000000;s._source_annual_sales_history=[180,170,160];s._store_sales_yen=25000000
    var viewed:int=s.active_store
    var monthly:int=s.economy.month_end_records.size()
    s._record_event("manager_report",{"text":"先の通知"})
    s._advance_minute_of_day()
    assert(s.month_count==12 and s.economy.month_end_records.size()==monthly+1 and s.active_store==viewed)
    assert(s._source_annual_sales_history==[500000000,180,170] and s._annual_sales_yen==0)
    assert(s.store_field(0,"_source_annual_sales_history")==[200000000,80,70])
    assert(s.last_owner_review.is_empty(),"Assessment waits for notification consumption")
    var modes:Array=[]
    for slot in 50:
        if s.notifications.queue[slot*160]!=0:modes.append(int(s.notifications.queue[slot*160+2]))
    assert(modes.slice(-2)==[2,3] and modes[0]==1,"Earlier notices then monthly then annual")
    var payload:Dictionary=JSON.parse_string(JSON.stringify(s.save_state()))
    var clone=setup();assert(clone.load_state(payload))
    var salary:int=clone.staff.checkout_staff().salary_yen_per_day_24h
    var seed:int=clone._program_rng.seed
    clone._annual_review();assert(clone._program_rng.seed==seed and clone.staff.checkout_staff().salary_yen_per_day_24h==salary)
    # Inputs change while reports wait: sold store excluded, current-year sales
    # ignored, live population/rating/visitors read at actual annual dispatch.
    assert(clone.try_sell_store(1))
    clone.select_store(0);clone._annual_sales_yen=1700000000;clone.internal_rating_value=70
    clone.town.population=14000;clone._chain_visitors_total=100000
    var annual:Dictionary={}
    for i in 50:
        var record:Dictionary=clone.consume_source_notice()
        if record.is_empty():break
        if int(record.mode)==3:annual=record;break
        clone.notifications.display(0,0)
    assert(not annual.is_empty())
    var n=clone.notifications
    assert(n.word(0x800e3ba8)==1 and n.word(0x800e3bb0)==200000000)
    assert(n.word(0x800e3bac)==100000 and n.word(0x800e3bb4)==14000 and n.word(0x800e3bb8)==70)
    assert(clone.last_owner_review.annual_sales==200000000 and clone.last_owner_review.mean_rating==70)
    var active_payload:Dictionary=JSON.parse_string(JSON.stringify(clone.save_state()))
    var active_clone=setup();assert(active_clone.load_state(active_payload))
    assert(JSON.parse_string(JSON.stringify(active_clone.notifications.current))==JSON.parse_string(JSON.stringify(clone.notifications.current)) and JSON.parse_string(JSON.stringify(active_clone.last_owner_review))==JSON.parse_string(JSON.stringify(clone.last_owner_review)))
    # Next years retain three previous revenues, once-only rollover survives JSON.
    clone.notifications.reset();clone.month_count=24;clone._annual_sales_yen=12;clone._annual_review(false)
    assert(clone._source_annual_sales_history==[12,200000000,80])
    clone.month_count=36;clone._annual_sales_yen=13;clone._annual_review(false)
    assert(clone._source_annual_sales_history==[13,12,200000000])
    var bad:Dictionary=payload.duplicate(true);bad.branches[0].store_sales.source_annual_sales_history=["bad"]
    assert(not clone.load_state(bad))
    bad=payload.duplicate(true);bad.source_annual_rollover_year=1.5;assert(not clone.load_state(bad))
    # Old queued aggregate remains usable without inventing per-store ledgers.
    var legacy:Dictionary=payload.duplicate(true)
    legacy.erase("source_annual_rollover_year")
    legacy.store_sales.erase("source_annual_sales_history")
    for block in legacy.branches:block.store_sales.erase("source_annual_sales_history")
    for context in legacy.source_notifications.contexts.values():
        if context.event_type=="owner_review":context.details={"annual_sales":700000000,"mean_rating":90,"parts":[4,4,20,4,20]}
    var old=setup();assert(old.load_state(legacy) and old._source_annual_sales_history.is_empty())
    for i in 50:
        var record:Dictionary=old.consume_source_notice()
        if record.is_empty():break
        if int(record.mode)==3:break
        old.notifications.display(0,0)
    assert(old.notifications.word(0x800e3bb0)==700000000)
    # Controlled eight-active-store input to the real consumer: score and
    # ending must depend on live rating, not the earlier reservation.
    var goal=setup();goal.config.source_scenario_index=2;goal.source_progress.mode=2;goal.source_progress.flags=3
    goal.month_count=12;goal._chain_visitors_total=500000;goal.town.population=20000
    goal._for_each_store(func():goal._source_annual_sales_history=[80000000];goal.internal_rating_value=90)
    for i in 6:goal._stores.append(goal._capture_store().duplicate())
    goal._record_event("owner_review",{"year":1})
    goal._for_each_store(func():goal.internal_rating_value=70)
    assert(goal.source_progress.pending==-1)
    goal.consume_source_notice();assert(goal.last_owner_review.total==92 and goal.source_progress.pending==-1)
    goal.notifications.reset();goal._for_each_store(func():goal.internal_rating_value=90)
    goal._record_event("owner_review",{"year":1})
    assert(goal.source_progress.pending==-1)
    goal.consume_source_notice();assert(goal.last_owner_review.total==100 and goal.source_progress.pending==2)
    # A celebration interrupts year-end before finance. JSON continuation
    # must roll once and enqueue one annual report after returning.
    var interrupted=setup();interrupted.month_count=11;interrupted._days_completed_this_month=3;interrupted.minute_of_day=1438
    interrupted.select_store(0);interrupted._annual_sales_yen=42;interrupted._store_visitor_heads=10000
    interrupted.source_calendar.pending=1
    interrupted._advance_minute_of_day()
    assert(interrupted.source_calendar_blocked() and interrupted.month_count==11 and interrupted._source_annual_sales_history.is_empty())
    var mid:Dictionary=JSON.parse_string(JSON.stringify(interrupted.save_state()))
    var resumed=setup();assert(resumed.load_state(mid))
    assert(resumed.advance_source_calendar_presentation(120,false))
    assert(resumed.month_count==12 and resumed.store_field(0,"_source_annual_sales_history")==[42])
    var annual_count:=0
    for slot in 50:
        if resumed.notifications.queue[slot*160] and resumed.notifications.queue[slot*160+2]==3:annual_count+=1
    assert(annual_count==1 and not resumed.finish_source_calendar_event())
    print("ANNUAL_REPORT_PASS 55 original excerpts, actual December/January ledger rollover and ordered reports, live sold-store/rating/population/visitors assessment, three histories, JSON and legacy")
    quit()
