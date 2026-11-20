extends SceneTree
const Sim=preload("res://scripts/vertical_slice_simulation.gd")
const Start=preload("res://scripts/domain/guide_starting_store.gd")
const Rule=preload("res://scripts/domain/program_donations.gd")

func _initialize() -> void:
    var base:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/vertical_slice.json"))
    var fixture:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://tests/fixtures/source_donations.json"))
    for case in fixture.cases:
        var amount:int=Rule.amount(int(case.cash_before),int(case.period),int(case.hour),0)
        assert(amount==int(case.paid) and int(case.cash_before)-amount==int(case.cash_after))
        for i in fixture.stores.size():
            var row:Dictionary=fixture.stores[i]
            assert(Rule.next_rating(int(row.rating),bool(row.active),int(row.company),int(case.company),amount>0)==int(case.ratings[i]))
        assert(Rule.amount(int(case.cash_before),int(case.period),int(case.hour),1)==0)
    var s=Sim.new(Start.apply(base))
    s.economy.cash_yen=1000000000
    assert(s.try_buy_store_site(Vector2i(26,12)))
    assert(s.try_buy_store_site(Vector2i(3,3),"small_top"))
    s.select_store(1);s.internal_rating_value=99;s.popularity=55;s.try_set_business_hours("closed")
    s.select_store(0);s.internal_rating_value=39;s.popularity=41;s.try_set_business_hours("closed")
    s.economy.cash_yen=1600000000
    s._rival_cash_yen=1500000001
    for rival in s._rival_stores:
        var child=s._program_rival_simulation(rival)
        child.internal_rating_value=19;child.star_rating=0;child.popularity=64
    var seed:int=s._program_rng.seed
    s.notifications.reset()
    s.minute_of_day=0;s._days_completed_this_month=4
    var before:int=s.economy.expense_records.size()
    var uid:int=s.economy.current_store_uid
    var operating:int=s.month_operating_statement().month_result_yen
    var special:int=s.month_operating_statement().one_off_yen
    s._apply_source_donations()
    assert(s.economy.cash_yen==1000000000 and s._rival_cash_yen==1000000000)
    assert(s.internal_rating_value==44 and s.star_rating==2 and s.popularity==41)
    assert(int(s.store_field(1,"internal_rating_value"))==100 and int(s.store_field(1,"popularity"))==55)
    assert(s.economy.expense_records.size()==before+1 and s.economy.current_store_uid==uid)
    var fee:Dictionary=s.economy.expense_records[-1]
    assert(fee.expense_type=="company_donation" and int(fee.amount_yen)==600000000 and int(fee.store_uid)==0)
    assert(s.month_operating_statement().month_result_yen==operating and s.month_operating_statement().one_off_yen==special+600000000)
    assert(s.rival_donation_records.size()==1 and int(s.rival_donation_records[0].amount_yen)==500000001)
    for rival in s._rival_stores:
        var child=s._program_rival_simulation(rival)
        assert(child.internal_rating_value==24 and child.star_rating==1 and child.popularity==64)
        child.economy.cash_yen=2000000000
        child._days_completed_this_month=4;child.minute_of_day=0
        child._apply_source_donations()
        assert(child.economy.cash_yen==2000000000,"Company child must not repeat shared donations")
    assert(s._program_rng.seed==seed)
    var notice:Dictionary=s.consume_source_notice()
    assert(notice.kind==0 and notice.parameter==0 and notice.sounds==[29] and notice.mode==1)
    assert(notice.context.event_type=="company_donation" and notice.context.details.company_wide)
    s.economy.cash_yen=2000000000
    s._rival_cash_yen=2000000000
    s._apply_source_donations()
    assert(s.economy.cash_yen==2000000000 and s._rival_cash_yen==2000000000,"Same month cannot repeat")
    var saved:Dictionary=JSON.parse_string(JSON.stringify(s.save_state()))
    var clone=Sim.new(Start.apply(base))
    assert(clone.load_state(saved))
    clone._apply_source_donations()
    assert(clone.economy.cash_yen==2000000000 and clone.rival_donation_records.size()==1)
    clone.month_count+=1
    clone._apply_source_donations()
    assert(clone.economy.cash_yen==1000000000 and clone.rival_donation_records.size()==2)
    var bad:Dictionary=saved.duplicate(true)
    bad.rival_donation_records=[{"month":1,"amount_yen":"x","cash_after_yen":1000000000}]
    assert(not clone.load_state(bad))
    var legacy:Dictionary=saved.duplicate(true)
    legacy.erase("source_donation_last_month");legacy.erase("rival_donation_records")
    assert(clone.load_state(legacy) and clone.rival_donation_records.is_empty())
    # Actual day/month boundary includes donation before the closing ledger.
    var clocked=Sim.new(Start.apply(base))
    clocked.economy.cash_yen=1000000000
    assert(clocked.try_buy_store_site(Vector2i(26,12)))
    clocked.try_set_business_hours("closed")
    clocked.economy.cash_yen=1600000000
    clocked._rival_cash_yen=0
    clocked.minute_of_day=1438;clocked._days_completed_this_month=2
    clocked._advance_minute_of_day()
    assert(clocked.economy.cash_yen==1600000000,"Ordinary midnight must not donate")
    clocked.minute_of_day=1438;clocked._days_completed_this_month=3
    clocked._advance_minute_of_day()
    assert(clocked.month_count==1 and clocked.economy.cash_yen==1000000000)
    assert(int(clocked.economy.month_end_records[-1].details.one_off_yen)>=600000000)
    assert(clocked.economy.expense_records.filter(func(row):return row.expense_type=="company_donation").size()==1)
    clocked._apply_source_donations()
    assert(clocked.economy.expense_records.filter(func(row):return row.expense_type=="company_donation").size()==1)
    # Strict threshold and both company's independence on next month.
    clocked.month_count+=1
    clocked.economy.cash_yen=1500000000;clocked._rival_cash_yen=1500000001
    clocked._apply_source_donations()
    assert(clocked.economy.cash_yen==1500000000 and clocked._rival_cash_yen==1000000000)
    # Inject a period1 00:00 ad only to verify relative dispatch order.
    # The real five source media have no hour0 record.
    var ordered=Sim.new(Start.apply(base))
    ordered.economy.cash_yen=1000000000
    assert(ordered.try_buy_store_site(Vector2i(26,12)))
    ordered.try_set_business_hours("closed")
    ordered.config.promotions[0].trigger_day=1;ordered.config.promotions[0].trigger_hour=0
    assert(ordered.try_commit_source_promotions(["direct_mail"]))
    ordered.economy.cash_yen=1500100001;ordered._rival_cash_yen=0
    ordered.minute_of_day=1438;ordered._days_completed_this_month=3
    ordered._advance_minute_of_day()
    var payments:Array=ordered.economy.expense_records.filter(func(row):return row.expense_type in ["company_advertising","company_donation"])
    assert(payments.size()==2 and payments[0].expense_type=="company_advertising" and int(payments[1].amount_yen)==500000001)
    assert(ordered.economy.cash_yen==1000000000)
    print("DONATIONS_PASS 36 original conditions, evaluation not popularity, two closed shops, both companies, single company capital payment, no child duplication, real month boundary, notice, RNG and JSON")
    quit()
