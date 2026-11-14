#!/usr/bin/env python3
"""Recover caller-specific financial effects from source, not gameplay runs."""
import argparse,hashlib,json,runpy,struct
from pathlib import Path
from capstone import Cs,CS_ARCH_MIPS,CS_MODE_MIPS32,CS_MODE_LITTLE_ENDIAN
ROOT=Path(__file__).resolve().parent
DISC_SHA='8d8eda789c5a2fe892a4722719b0466dd7d126eed6cd99ad05a807d81b57d1c1'
EXE_SHA='d6a167a1c9e0fe98d7e44e12968caa489ac3eb7ed3b9e46012a188af8432b1fd'
def sha(b):return hashlib.sha256(b).hexdigest()
def i32(v):return (v+2**31)%2**32-2**31
def write(n,x):(ROOT/n).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')

def main():
    ap=argparse.ArgumentParser();ap.add_argument('disc',type=Path);args=ap.parse_args()
    disc=args.disc.read_bytes();assert sha(disc)==DISC_SHA
    iso=runpy.run_path(str(ROOT.parent/'20261113-disc-data-extraction/extract-disc-data.py'))['iso']
    rows,read=iso(disc);files={r['path']:r for r in rows}
    def payload(p):r=files[p];return read(r['lba'],r['bytes'])
    exe=payload('/SLPS_007.82');assert sha(exe)==EXE_SHA
    def at(a,n):return exe[a-0x80010000+2048:a-0x80010000+2048+n]
    md=Cs(CS_ARCH_MIPS,CS_MODE_MIPS32|CS_MODE_LITTLE_ENDIAN)
    spans=[('operation_menu',0x80060418,0x80060b90),('first_opening_interior',0x8005dd04,0x8005de1c),
        ('new_branch_interior',0x80061508,0x80061630),('remodel_controller',0x80063e44,0x800640e4),
        ('cursor_only',0x80065ff4,0x80066070),('stock_and_capital_post',0x8001ca7c,0x8001ccc0),
        ('close_capital_history',0x8002a47c,0x8002a7e4),('close_exit_conditions',0x8002a864,0x8002a8e0)]
    (ROOT/'source').mkdir(exist_ok=True);asm=[];ranges=[];call_sites={}
    for name,a,end in spans:
        b=at(a,end-a);ins=list(md.disasm(b,a));(ROOT/'source'/f'{name}.bin').write_bytes(b)
        calls=[dict(address=hex(i.address),target=i.op_str) for i in ins if i.mnemonic=='jal'];call_sites[name]=calls
        ranges.append(dict(name=name,address=hex(a),bytes=len(b),sha256=sha(b)))
        asm.append(f'\n# {name} {a:#x}..{end:#x}');asm.extend(f'{i.address:08x}: {i.bytes.hex()} {i.mnemonic} {i.op_str}' for i in ins)
    assert [r['target'] for r in call_sites['cursor_only']]==[]
    assert sum(c['target']=='0x8001cbc4' for c in call_sites['remodel_controller'])==4
    assert not any(c['target']=='0x8001ca7c' for c in call_sites['remodel_controller'])
    (ROOT/'accounting-readers.asm').write_text('\n'.join(asm)+'\n');write('source-ranges.json',ranges);write('source-call-sites.json',call_sites)
    routes=[dict(id='direct_existing',menu_index=0,parent='0x80060418',editor_call='0x80060abc',editor_argument=1,
        initial_editor_state=7,restore_primary_cash=False,restore_primary_capital=False,success_post_stock=False,success_post_equipment=False,
        meaning='Keeps actual cash changes made during individual editor operations. No extra1CA7C/1CBC4 after return in60418. No whole-store restore in this caller.'),
        dict(id='remodel_existing',menu_index=3,parent='0x80063e44',editor_call='0x80063fc4',editor_argument=0,
        initial_editor_state=1,restore_primary_cash=True,restore_primary_capital=True,success_post_stock=False,success_post_equipment=False,
        meaning='Pays confirmed size/permit fees through1CBC4 before editor. After editor restores primary cash/capital; accepted interior values/layout retained, editor equipment/stock costs not reposted.65FF4 only initializes cursor variables.'),
        dict(id='first_opening',parent='new-game opening',editor_call='0x8005dd2c',editor_argument='local continuation flag; initially0',
        restore_primary_cash=True,restore_primary_capital=True,success_post_stock=True,success_post_equipment=True,
        meaning='Restores provisional primary cash/capital then posts stockCD8E0 to1CA7C(mode0) and equipmentCD978 to1CBC4. Cancel reverses land/demolition/size/permit fees.'),
        dict(id='later_opening',parent='0x800612cc',editor_call='0x80061530',editor_argument='local continuation flag; initially0',
        restore_primary_cash=True,restore_primary_capital=True,success_post_stock=True,success_post_equipment=True,
        meaning='Same stock/equipment posting distinction as first opening. Cancel reverses the four previously posted premises fees.')]
    write('caller-accounting-routes.json',dict(routes=routes,scope='Route names describe observed behavior, not newly transcribed UI labels. Normal own-company routes. Primary cash/capital backups are hard-coded, not automatically selected by the store owner flag. Do not apply this as a rival editor policy.'))
    fields=[dict(name='cash',address='0x800cd9f8',stride=4,company_slots=2,rule='cash[owner] for1CA7C/1CBC4; direct editor leaves use primary cash'),
        dict(name='editor_equipment',address='0x800cd978',rule='Working cost reset by75514, not itself a company historical ledger'),
        dict(name='editor_stock',address='0x800cd8e0',rule='Working procurement cost reset by75514, not itself store D94'),
        dict(name='store_daily_stock_expense',store_offset='0xd94',rule='1CA7C mode0 adds amount here and subtracts owner cash; mode!=0 instead adds D98 and owner cash'),
        dict(name='store_daily_revenue',store_offset='0xd98',rule='1CA7C nonzero mode credits this field and owner cash'),
        dict(name='company_capital_history_today',address='0x800d8f68',company_stride=16,history_words=4,rule='1CBC4 adds signed amount and subtracts owner cash. Null store explicitly targets company1.'),
        dict(name='company_capital_history_month',address='0x800da970',company_stride=16,history_words=4),
        dict(name='company_capital_history_year',address='0x800df080',company_stride=16,history_words=4)]
    write('financial-field-map.json',dict(fields=fields,
        capital_label_scope='Descriptive name for the amount maintained by1CBC4, not newly decoded UI wording.',
        rollover='Native2A464 onward adds daily current amount into monthly current, shifts daily4 words and zeros current. Stage1 adds monthly into annual current then shifts monthly; stage1+month1 shifts annual. Stores live only own/rival side0/1; no times8 multiplier on this company capital series.',
        negative_cash='At daily-close end2A868, signed primary cash<0 branches to2A8B0, setsCD9B4=4 andCD948=0xff. Year/serial>=99 share the exit target. Zero cash alone does not take the negative branch. This is a post-close condition, not an immediate editor affordability check.',
        save_layout=dict(daily=dict(offset='0x861c',bytes=32),monthly=dict(offset='0x85fc',bytes=32),yearly=dict(offset='0x85dc',bytes=32),
            evidence='Native save6BB04..6BB24,6BAE0..6BB00,6BABC..6BADC and inverse load6BEDC..6BF44; these offsets are within decoded save payload, not raw memory-card block offsets.')))
    # Actual original store inputs; no invented own-company stores or RAM.
    master=json.loads((ROOT.parent/'20261114-interior-transactions-data/fixture-transaction-master.json').read_text())
    fixtures=master['fixture_rows'];products=master['product_rows']
    def product(im):return next((p for p in products if any(v//3==im//3 for v in p['runtime_images'])),products[0])
    originals=[]
    for name in ['TOWN0001','TOWN0002','TOWN0003','TOWNPS']:
        b=payload('/DAT/'+name+'.BIN')
        for slot in range(10):
            store=b[25907+slot*5080:25907+(slot+1)*5080]
            if not store[0]:continue
            w,h=struct.unpack_from('<2i',store,0x44);assets=[]
            for y in range(h):
                for x in range(w):
                    v=struct.unpack_from('<I',store,0x108+y*112+x*4)[0];kind=v>>12&1023
                    if not v&0x80000000 or kind>=53:continue
                    sv=struct.unpack_from('<I',store,0x178+y*112+x*4)[0];im=sv>>12&1023;qty=sv>>24&127
                    p=product(im) if im else None;cost=0 if p is None else p['procurement_unit']*qty
                    assets.append(dict(x=x,y=y,fixture=kind,equipment=fixtures[kind]['purchase_price'],stock_product=None if p is None else p['id'],
                        stock_quantity=qty,stock_cost=cost,ordinary_removal_allowed=fixtures[kind]['regular_removal_allowed']))
            originals.append(dict(map=name,slot=slot,owner=struct.unpack_from('<H',store,4)[0]>>15,source_store_sha256=sha(store),
                tier=struct.unpack_from('<i',store,0xc70)[0],stored_D94=struct.unpack_from('<i',store,0xd94)[0],stored_D98=struct.unpack_from('<i',store,0xd98)[0],
                equipment_value=sum(a['equipment'] for a in assets),stock_asset_value=sum(a['stock_cost'] for a in assets),anchors=assets))
    assert len(originals)==11 and all(r['owner']==1 for r in originals)
    write('initial-store-assets-and-ledgers.json',dict(stores=originals,
        scope='All11 source active stores are rival company1. Their asset values and stored D94/D98 are real input evidence; this file does not claim own-company editor actions were performed on those stores. Asset stock value is not automatically daily procurement expense.'))
    prefabs=json.loads((ROOT.parent/'20261114-interior-transactions-data/built-in-prefab-opening-costs.json').read_text())['rows']
    examples=[]
    for q in prefabs:
        e=q['equipment'];s=q['stock'];fee=q['construction_fee'];start=200000000
        examples.append(dict(tier=q['tier'],source_layout=q['built_in_prefab_layout'],equipment=e,stock=s,size_fee=fee,
            direct_buy_equivalent=dict(cash_delta=i32(-e-s),stock_expense_post_delta=0,capital_post_delta=0,
                scope='Sum of eligible individual purchase leaf effects only; not a claim existing-editor arg1 loads this prefab, and required facility changes have separate paths.'),
            new_opening_interior_commit=dict(cash_delta=i32(-e-s),stock_expense_post_delta=s,capital_post_delta=e),
            existing_remodel_accept=dict(starting_cash=start,cash_after_size_fee=start-fee,editor_temporary_cash=start-fee-e-s,
                cash_after_parent_restore=start-fee,capital_post_delta=fee,stock_expense_post_delta=0,
                note='Source-only arithmetic with no new permits and enough funds. Layout retained but no extra equipment/stock repost in63E44.'),
            existing_remodel_cancel=dict(cash_after_editor_restore=start-fee,cash_after_refund=start,net_capital_post_delta=0,
                store_snapshot='5080 bytes captured AFTER new size/permit selection; restoring it retains selected C70. Restore saved original3 permit flags separately. Retry premises stage.')))
    write('source-derived-caller-examples.json',dict(method='Source arithmetic on actual six selected prefab cost rows, no CPU execution or observed playthrough.',rows=examples))
    size_changes=[dict(old_tier=old,new_tier=new,confirmed_construction_fee=(new//2+1)*6000000,
        old_building_refund_in_this_path=0,
        editor_cancel_then_snapshot_restore_C70=new,
        source_note='6DD18mode1 calls1DE5C(mode1) with newly storedC70; no old-tier subtraction.63E44 snapshot after premises confirmation.')
        for old in range(6) for new in range(6)]
    write('existing-store-size-fees.json',dict(rows=size_changes,
        scope='36 source arithmetic transitions. Full selected-tier fee includes same-size and downsizing; not difference between old/new fees. Selector availability, cash checks and successful confirmation still required. Cancellation snapshot C70 result is source field order, not a gameplay run.'))
    # One concrete purchase / same-item reverse / change credit from real masters.
    f=fixtures[0];p=products[f['source_default_product']];stock=f['capacity']*p['procurement_unit']
    write('source-derived-single-operation.json',dict(fixture=dict(id=0,label=f['label'],price=f['purchase_price']),
        product=dict(id=p['id'],name=p['name'],quantity=f['capacity'],unit=p['procurement_unit']),
        buy=dict(cash_delta=-f['purchase_price']-stock,editor_equipment_delta=f['purchase_price'],editor_stock_delta=stock,store_D94_post_delta=0,company_capital_post_delta=0),
        remove_same_full_item=dict(cash_delta=f['purchase_price']+stock,editor_equipment_delta=-f['purchase_price'],editor_stock_delta=-stock,store_D94_post_delta=0,company_capital_post_delta=0),
        scope='Specific76474/773BC cash/cost effects. They do not invoke1CA7C/1CBC4. Numeric example follows source price units, not a real-world price estimate.'))
    bridge=dict(schema_version=1,
        entrypoint='Preserve distinct workflows.60418 menu0->75514(arg1) is direct editor; menu3->63E44->6DD18(mode1)->75514(arg0) is whole remodel. New-store calls at5DD2C/61530 have separate accounting.',
        direct='Existing direct editor starts at state7 and keeps individual changes in cash. No parent cash backup/restore, stock1CA7C or capital1CBC4. Its counters are not automatic financial-history postings.',
        remodel='After premises confirmation post sizeCD8D8 and permitCD998 using1CBC4. Snapshot cash/capital and5080 store bytes. After editor restore cash/capital unconditionally. Success retains layout, calls65FF4 cursor initialization only and refresh; do not add a missing new-store equipment/stock posting as an assumed original rule.',
        cancel='If editor returns-1, reverse size and permit signed amounts with1CBC4; restore post-premises5080 store snapshot and original3 permits; retry from premises. This does not restore all bytes from before premises selection or whole-world/external staff state.',
        new_store='On success restore provisional cash/capital then post CD8E0 to1CA7C(mode0),CD978 to1CBC4. On cancellation reverse four premises amounts. Do not charge provisional and final debits twice.',
        routing='1CA7C/1CBC4 derive owner from store flags bit15.1CBC4 null-store fallback targets company1. Editors and saved backups discussed here use primary cash/record explicitly. Do not make arbitrary rival-editor guarantees.',
        histories='Keep1CBC4 company series separate from store D94/D98, and preserve daily/monthly/yearly histories. Persist exact decoded save offsets with the rest of save state.',
        negative='No new immediate editor cash guard inferred. The identified daily-close negative primary cash condition enters state4 withreasonFF; complete UI outcome and timing outside this condition are not executed here.',
        scope='Native implementation specification, no emulator/BIOS/EXE runtime dependency. This package does not change native Android code/APK.')
    write('android-remodel-accounting-bridge.json',bridge)
    # Include original persistence reader/writer slices for the newly mapped fields.
    extra=[]
    for name,a,end in [('save_financial_series',0x8006babc,0x8006bb28),('load_financial_series',0x8006bedc,0x8006bf48)]:
        b=at(a,end-a);(ROOT/'source'/f'{name}.bin').write_bytes(b);extra.append(dict(name=name,address=hex(a),bytes=len(b),sha256=sha(b)))
    write('source-ranges.json',ranges+extra)
    write('source-dependencies.json',dict(original_stores='../20261114-parking-arrival-data/source/initial-active-stores.bin',
        fixture_product_costs='../20261114-interior-transactions-data/fixture-transaction-master.json',prefab_costs='../20261114-interior-transactions-data/built-in-prefab-opening-costs.json',
        size_fee_reader='../20261114-land-construction-cost-data/source/premises_value.bin',size_dialog='../20261114-land-construction-cost-data/source/size_ui.bin',
        note='Reuses original evidence; source disc reread, no new RAM/emulator dumps.'))
    write('summary.json',dict(caller_routes=4,original_active_store_records=11,prefab_caller_examples=6,size_fee_transitions=36,
        stored_asset_value_by_map={name:dict(equipment=sum(r['equipment_value'] for r in originals if r['map']==name),stock=sum(r['stock_asset_value'] for r in originals if r['map']==name)) for name in ['TOWN0001','TOWN0002','TOWN0003','TOWNPS']},
        persistence_series=3,original_cpu_updates=0,
        known_before='Four isolated75514 caller slices and63E44 controller already recovered. New work connects source operation menu, distinct confirmed/provisional postings, real11 source-store asset values, six real prefab totals,3 persisted history series and post-close cash exit condition.',
        limits='Source data/control extraction, not a new gameplay run. Do not call preserved original accounting asymmetry a fixed bug. Native Android/APK not updated.'))
    print((ROOT/'summary.json').read_text())
if __name__=='__main__':main()
