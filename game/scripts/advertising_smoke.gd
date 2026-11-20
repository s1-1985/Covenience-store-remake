extends SceneTree
const Sim=preload("res://scripts/vertical_slice_simulation.gd")
const Start=preload("res://scripts/domain/guide_starting_store.gd")
const Ads=preload("res://scripts/domain/program_advertising.gd")
func _initialize() -> void:
    var base:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/vertical_slice.json"))
    var evidence:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://tests/fixtures/source_advertising.json"))
    for master in evidence.masters:
        var entry:Dictionary=base.promotions[int(master.index)]
        assert(int(entry.cost_yen)==int(master.cost_yen) and int(entry.popularity_gain)==int(master.gain))
        assert(int(entry.trigger_day)==int(master.period) and int(entry.trigger_hour)==int(master.hour))
    for case in evidence.cases:
        var entry:Dictionary=base.promotions[int(case.index)]
        var result:Dictionary=Ads.plan(base.promotions,[entry.promotion_id],int(entry.trigger_day),int(entry.trigger_hour),0,int(case.cash_before))
        assert(result.actions.size()==1 and bool(result.actions[0].fired)==bool(case.fired))
        assert(int(result.cash_yen)==int(case.cash_after))
        assert(result.enabled.has(entry.promotion_id)==bool(case.flag))
        assert(Ads.plan(base.promotions,[entry.promotion_id],int(entry.trigger_day),int(entry.trigger_hour),1,int(case.cash_before)).actions.is_empty())
    var s=Sim.new(Start.apply(base))
    s.economy.cash_yen=1000000000
    assert(s.try_buy_store_site(Vector2i(26,12)))
    assert(s.try_buy_store_site(Vector2i(3,3),"small_top"))
    s.select_store(1);s.popularity=70
    s.try_set_business_hours("closed")
    s.select_store(0);s.popularity=20
    s.try_set_business_hours("closed")
    s.notifications.reset()
    s._days_completed_this_month=1
    s.minute_of_day=599
    assert(s.try_commit_source_promotions(["direct_mail"]))
    var seed:int=s._program_rng.seed
    s.economy.cash_yen=500000
    var cash:int=s.economy.cash_yen
    var count:int=s.economy.expense_records.size()
    var operating:int=s.month_operating_statement().month_result_yen
    var oneoff:int=s.month_operating_statement().one_off_yen
    s.minute_of_day=598
    s._advance_minute_of_day()
    assert(s.minute_of_day==600 and s.economy.cash_yen==cash-100000)
    assert(s.economy.expense_records.size()==count+1 and int(s.economy.expense_records[-1].store_uid)==0)
    assert(s.economy.expense_records[-1].expense_type=="company_advertising")
    assert(s.popularity==32 and int(s.store_field(1,"popularity"))==82)
    assert(s.month_operating_statement().month_result_yen==operating)
    assert(s.month_operating_statement().one_off_yen==oneoff+100000)
    assert(s._program_rng.seed==seed and s.source_promotions.has("direct_mail"))
    s._fire_source_promotions()
    assert(s.economy.cash_yen==cash-100000,"Same hour cannot double-post")
    var notice:Dictionary=s.consume_source_notice()
    assert(notice.kind==4 and notice.parameter==0 and notice.context.details.company_wide)
    var saved:Dictionary=JSON.parse_string(JSON.stringify(s.save_state()))
    var clone=Sim.new(Start.apply(base))
    assert(clone.load_state(saved))
    clone._fire_source_promotions()
    assert(clone.economy.expense_records.size()==count+1)
    clone.month_count+=1
    clone._fire_source_promotions()
    assert(not clone.source_promotions.has("direct_mail") and clone.economy.cash_yen==400000)
    clone.economy.cash_yen=1000000000
    clone.month_count+=1
    clone._fire_source_promotions()
    assert(clone.economy.expense_records.size()==count+1,"Cash recovery must not reactivate a cancelled flag")
    assert(clone.try_commit_source_promotions(["direct_mail"]))
    clone.minute_of_day=601
    clone._fire_source_promotions()
    assert(clone.economy.expense_records.size()==count+1,"Past deadline is not caught up")
    var legacy:Dictionary=saved.duplicate(true)
    legacy.erase("source_promotions")
    legacy.erase("source_advertising_last_clock")
    legacy.promotions_used_this_month=["tv"]
    legacy.branches[0].scheduled_promotions=[{"promotion_id":"direct_mail","trigger_day":2,"trigger_hour":10}]
    var migrated=Sim.new(Start.apply(base))
    assert(migrated.load_state(legacy))
    assert(migrated.source_promotions.size()==2 and migrated.source_promotions.has("tv") and migrated.source_promotions.has("direct_mail"))
    assert(migrated.store_field(1,"_scheduled_promotions").is_empty())
    # Actual representative-month boundaries: no monthly flag reset.
    var recurring=Sim.new(Start.apply(base))
    recurring.economy.cash_yen=1000000000
    assert(recurring.try_buy_store_site(Vector2i(26,12)))
    recurring.try_set_business_hours("closed")
    assert(recurring.try_commit_source_promotions(["direct_mail"]))
    for i in 5760:recurring._advance_minute_of_day()
    var ads:Array=recurring.economy.expense_records.filter(func(row):return row.expense_type=="company_advertising")
    assert(ads.size()==2 and recurring.source_promotions.has("direct_mail"))
    assert(not recurring.try_commit_source_promotions([],[]),"Stale empty draft must not clear a newer setting")
    print("ADVERTISING_PASS 10 original cash gates, company-wide closed-store effect, one payment, capital classification, notice4, save, no duplicate/catchup/reactivation, legacy migration and two real month rollovers")
    quit()
