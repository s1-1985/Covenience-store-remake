extends SceneTree
const Sim=preload("res://scripts/vertical_slice_simulation.gd")
const Start=preload("res://scripts/domain/guide_starting_store.gd")
const Ads=preload("res://scripts/domain/program_advertising.gd")
const RNG=preload("res://scripts/domain/program_random.gd")
func _initialize() -> void:
    var base:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/vertical_slice.json"))
    var evidence:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://tests/fixtures/source_rival_advertising.json"))
    for row in evidence.selection:
        var rng=RNG.new();rng.seed=int(row.seed)
        var selected:Array=Ads.rival_selection(base.promotions,int(row.cash),int(row.control),rng)
        var expected:Array=[]
        for index in row.enabled:expected.append(str(base.promotions[int(index)].promotion_id))
        assert(selected==expected and rng.seed==int(row.seed_after))
    for row in evidence.payments:
        var entry:Dictionary=base.promotions[int(row.index)]
        var actions:Array=Ads.rival_actions(base.promotions,[str(entry.promotion_id)],int(entry.trigger_day),int(entry.trigger_hour))
        assert(actions.size()==1 and int(actions[0].gain)==int(row.gain) and int(actions[0].cost_yen)==int(entry.cost_yen))
    var s=Sim.new(Start.apply(base));assert(s._rival_stores.size()>0)
    s.economy.cash_yen=1000000000;assert(s.try_buy_store_site(Vector2i(26,12)))
    s.config["source_scenario"]["mode"]=3
    s._rival_cash_yen=50000000
    s.source_rival_promotions=["direct_mail"]
    var home:int=s.active_store;var own_cash:int=s.economy.cash_yen;var own_pop:int=s.popularity
    var seed:int=s._program_rng.seed
    s.minute_of_day=0;s._days_completed_this_month=0
    s._fire_source_promotions()
    assert(s.source_rival_promotions==["tv"] and s._rival_cash_yen==50000000)
    var after:int=s._program_rng.seed;assert(after!=seed)
    s._fire_source_promotions();assert(s._program_rng.seed==after)
    # Selection persists and triggering does not recheck funds or draw RNG.
    for rival in s._rival_stores:
        var child=s._program_rival_simulation(rival)
        child.popularity=20;child.try_set_business_hours("closed")
    var first=s._program_rival_simulation(s._rival_stores[0])
    var expense_count:int=first.economy.expense_records.size()
    var saved:Dictionary=JSON.parse_string(JSON.stringify(s.save_state()))
    var clone=Sim.new(Start.apply(base));assert(clone.load_state(saved))
    assert(clone.source_rival_promotions==["tv"])
    clone._rival_cash_yen=0;clone.minute_of_day=19*60
    clone.notifications.reset();clone._fire_source_promotions()
    assert(clone._rival_cash_yen==-5000000 and clone.economy.cash_yen==own_cash and clone.popularity==own_pop)
    assert(clone.active_store==home and clone._program_rng.seed==after)
    for rival in clone._rival_stores:assert(clone._program_rival_simulation(rival).popularity==100)
    var payer=clone._program_rival_simulation(clone._rival_stores[0])
    assert(payer.economy.expense_records.size()==expense_count+1 and payer.economy.expense_records[-1].amount_yen==5000000 and payer.economy.expense_records[-1].store_uid==0)
    var notice:Dictionary=clone.consume_source_notice()
    assert(notice.kind==4 and notice.parameter==4 and notice.sounds==[29] and not str(notice.context.details.rival_id).is_empty())
    clone._fire_source_promotions();assert(clone._rival_cash_yen==-5000000)
    # Child must never select or execute a second company campaign.
    payer.minute_of_day=0;payer._days_completed_this_month=0
    payer._source_advertising_last_clock="";payer.source_promotions={"tv":true}
    var before_cash:int=payer.economy.cash_yen;var before_seed:int=clone._program_rng.seed
    payer._fire_source_promotions()
    assert(payer.economy.cash_yen==before_cash and clone._program_rng.seed==before_seed)
    # Old saves do not guess a campaign already chosen in a past month.
    saved.erase("source_rival_promotions")
    var legacy=Sim.new(Start.apply(base));assert(legacy.load_state(saved) and legacy.source_rival_promotions.is_empty())
    var invalid:Dictionary=saved.duplicate(true);invalid.source_rival_promotions=["unknown"]
    assert(not legacy.load_state(invalid))
    # Hour/period/minute gates retain old flags and seed.
    for row in evidence.gates:
        var gated=Sim.new(Start.apply(base));gated.source_rival_promotions=["direct_mail"]
        gated.minute_of_day=int(row.hour)*60+int(row.minute);gated._days_completed_this_month=int(row.period)-1
        var before:int=gated._program_rng.seed
        gated._fire_source_promotions()
        assert(gated._program_rng.seed==before and gated.source_rival_promotions==["direct_mail"])
    # Actual initial advancement and full month rollover choose once each.
    var recurring=Sim.new(Start.apply(base));recurring.config["source_scenario"]["mode"]=3
    recurring._rival_cash_yen=50000000
    recurring.minute_of_day=0
    recurring._advance_minute_of_day()
    assert(recurring.source_rival_promotions==["tv"])
    for i in 2879:recurring._advance_minute_of_day()
    assert(recurring.month_count==1 and recurring.minute_of_day==0)
    var ads_count:=0
    for child in recurring._rival_simulations.values():
        for record in child.economy.expense_records:
            if record.expense_type=="company_advertising":ads_count+=1
    assert(ads_count==1,"First month triggers one company payment, not one per store")
    var rollover_seed:int=recurring._program_rng.seed
    recurring._fire_source_promotions();assert(recurring._program_rng.seed==rollover_seed)
    # No surviving rival: no payment or notification.
    s._rival_stores.clear();s.notifications.reset();s.minute_of_day=19*60
    s._fire_source_promotions();assert(s._rival_cash_yen==50000000 and s.notifications.contexts.is_empty())
    print("RIVAL_ADVERTISING_PASS 233 original excerpts; native company selection/payment, no repeated cash gate, closed-store popularity, one notice, JSON, child guard, legacy and timing gates")
    quit()
