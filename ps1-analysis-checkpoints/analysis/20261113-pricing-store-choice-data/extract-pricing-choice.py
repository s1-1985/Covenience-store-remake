#!/usr/bin/env python3
"""Static source data: price-setting domains and named customer store-choice weights.
No PS CPU execution, random test farm or simulated business continuation.
"""
import argparse,collections,hashlib,json,runpy,struct
from pathlib import Path
from capstone import Cs,CS_ARCH_MIPS,CS_MODE_MIPS32,CS_MODE_LITTLE_ENDIAN
ROOT=Path(__file__).resolve().parent
DISC_SHA='8d8eda789c5a2fe892a4722719b0466dd7d126eed6cd99ad05a807d81b57d1c1'
EXE_SHA='d6a167a1c9e0fe98d7e44e12968caa489ac3eb7ed3b9e46012a188af8432b1fd'
def sha(b):return hashlib.sha256(b).hexdigest()
def js(name,data):(ROOT/name).write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
def main():
    ap=argparse.ArgumentParser();ap.add_argument('disc',type=Path);args=ap.parse_args();raw=args.disc.read_bytes();assert sha(raw)==DISC_SHA
    lib=runpy.run_path(str(ROOT.parent/'20261113-disc-data-extraction/extract-disc-data.py'));files,read=lib['iso'](raw);r=next(r for r in files if r['path']=='/SLPS_007.82');exe=read(r['lba'],r['bytes']);assert sha(exe)==EXE_SHA
    def at(a,n):return exe[a-0x80010000+2048:a-0x80010000+2048+n]
    products=[]
    for i in range(27):
        a=0x8009cdf0+i*88;b=at(a,88);base,factor,initial=struct.unpack_from('<3i',b,24)
        price=lambda setting:base*(factor+setting)//100
        products.append(dict(id=i,address=hex(a),name=b[:24].split(b'\0')[0].decode('shift_jis'),base_price=base,cost_percent=factor,initial_setting=initial,editable_in_individual_menu=i<26,procurement_unit_cost=base*factor//100,initial_selling_price=price(initial),selling_price_at_setting0=price(0),selling_price_at_setting100=price(100),price_at_initial_minus1=price(initial-1) if initial else None,price_at_initial_plus1=price(initial+1) if initial<100 else None))
    assert all(p['initial_selling_price']==p['base_price'] for p in products)
    ranges=list(struct.unpack('<4i',at(0x80099570,16)));assert ranges==[20,40,60,70]
    # Prior decoded labels are reused; all numerical selection fields are reread here.
    old=json.loads((ROOT.parent/'20261113-customer-data/customer-data.json').read_text());labels={p['id']:p['group_label'] for p in old['profiles']}
    profiles=[];modes=collections.Counter();weight_sums=collections.Counter()
    for i in range(144):
        a=0x800a09d0+i*24;b=at(a,24);hour=struct.unpack_from('<b',b,2)[0];mode=struct.unpack_from('<b',b,12)[0];ids=list(struct.unpack_from('<4b',b,8));weights=list(struct.unpack_from('<3b',b,14));modes[mode]+=1;weight_sums[sum(weights)]+=1
        profiles.append(dict(id=i,address=hex(a),label=labels[i],arrival_hour=hour,arrival_mode=mode,max_source_distance=ranges[mode],parking_required=mode==3,primary_product=ids[0],product_ids=ids,weight_price=weights[0],weight_distance=weights[1],weight_service=weights[2],weight_sum=sum(weights),initial_wallet=struct.unpack_from('<h',b,6)[0]))
    js('pricing-choice-masters.json',dict(schema_version=1,source_disc_sha256=DISC_SHA,source_exe_sha256=EXE_SHA,products=products,customer_profiles=profiles,arrival_ranges=ranges,arrival_mode_counts=dict(sorted(modes.items())),weight_sum_counts=dict(sorted(weight_sums.items())),labels_dependency='../20261113-customer-data/customer-data.json; numerical values freshly read from disc',weight_note='Raw coefficients, not percentages constrained to total100. Transport labels for modes0..2 are not assigned by this report.'))
    # The existing source model keeps these three accumulators across physical slots.
    # This example is arithmetic, not a captured gameplay trace.
    count=running=parking=0;carry=[]
    for slot,new_parking in [(0,2),(1,0)]:
        count+=2;running+=200;running//=count;parking+=new_parking
        carry.append(dict(physical_slot=slot,identical_fixture_price_factors=[100,100],own_parking=new_parking,accumulated_fixture_count=count,stored_price_factor=running,stored_parking_capacity=parking))
    assert [s['stored_price_factor'] for s in carry]==[100,75]
    js('source-derived-examples.json',dict(scope='Arithmetic examples from raw tables/source expressions, not real gameplay observations.',price_step_examples=[p for p in products if p['id'] in (0,3)],physical_slot_carryover=carry,price_normalization_for_two_example_stores=[0,100],tie_break=dict(order=[4,1],same_score=True,same_primary_stock=True,same_rating=True,selected=4),budget_note='Initial wallet is not used in26A64 store ranking. It is checked in the later purchase branch.'))
    bridge=dict(schema_version=1,source_exe_sha256=EXE_SHA,pricing=dict(setting_field='store+C7C+4*product',unit_formula='trunc_toward_zero(base_price*(cost_percent+setting)/100)',purchase_cast='Purchase control narrows computed unit price to signed16 before wallet comparison; ordinary UI values remain in range.',editable_products=list(range(26)),readonly_product26='Cash; no ordinary individual-menu entry.',individual_editor='Temporary26-value delta array. Commit writes all26; cancel does not write them back. Direction edits stop at setting0/100.',group_editor='Raise all26 by1 only if none is>=100; lower all26 by1 only if none is<=0. Do not clamp each item independently.',meaning='Setting1 step changes coefficient by1 percentage point of source base price, not1 monetary unit and not1% of procurement cost.'),store_metrics=dict(price_raw='Summary+00: running average of cost_percent+setting for every anchored fixture with a recognized product image, exceptcash26; quantity0 does not itself exclude an image.',price_normalized='Summary+9C:100-trunc((price_raw-min)*100/(max-min)),or100 when equal.',service_raw='Summary+0C, normalized at+A4. Not security at+08. Earlier helper variables namedsecurity in this path refer to service.',distance='max(left-x,x-right)+max(top-y,y-bottom)',distance_normalized='Summary+A0:100-trunc((distance-low)*100/(high-low)),or0 if equal; source initializes low0/high110.',carryover='Native23C20 clears stack+48(count),+4C(parking),+50(price accumulator) before physical-store loop0..9 only. Later active stores inherit all three; price accumulator has already been divided for prior store. Preserve as a source quirk rather than silently resetting per store.'),candidate_gates=['One RNG for rating gate per store in order; continue only if rand()%100+1<=store rating+20.','Schedule must be open at profile signed byte+2 arrival hour.','Arrival mode3 requires summary parking capacity>0.','Primary product profile+8 stock must be>0. Other stock cannot substitute.','Computed source distance must be<=arrival_ranges[mode].'],ranking='price_norm*profile+14 + distance_norm*profile+15 + service_norm*profile+16; highest score wins.',ties=['more primary-product stock','higher store rating','first in supplied store order'],wallet='Not part of candidate ranking; later purchase control compares per-person current wallet against unit price.',limits=['This report links existing algorithms to complete named master data and exact source fields; it does not claim each formula is newly discovered.','Store-order/carryover behavior is from the original code, not a desired economic design.','No approximation of these weights as independent percentages or new probabilistic model.'])
    js('android-pricing-choice-bridge.json',bridge)
    spans=[('product_master',0x8009cdf0,27*88,False),('customer_profiles',0x800a09d0,144*24,False),('arrival_ranges',0x80099570,16,False),('store_metric_builder',0x80023c20,0x800248b0-0x80023c20,True),('store_selector',0x80026a64,0x80027328-0x80026a64,True),('individual_price_editor',0x80063714,0x80063e44-0x80063714,True),('group_price_step_excerpt',0x80063208,0x480,True),('purchase_unit_price_excerpt',0x8003473c,0x80034800-0x8003473c,True)]
    md=Cs(CS_ARCH_MIPS,CS_MODE_MIPS32|CS_MODE_LITTLE_ENDIAN);asm=[];manifest=[];zero_sites=[];service_reads=[];(ROOT/'source').mkdir(exist_ok=True)
    for name,a,n,code in spans:
        b=at(a,n);(ROOT/'source'/f'{name}.bin').write_bytes(b);manifest.append(dict(name=name,address=hex(a),bytes=n,sha256=sha(b)))
        if not code:continue
        asm.append(f'\n# {name} {a:#x} bytes={n}')
        for x in md.disasm(b,a):
            asm.append(f'{x.address:08x}: {x.bytes.hex()} {x.mnemonic} {x.op_str}')
            w=struct.unpack('<I',x.bytes)[0]
            if name=='store_metric_builder' and w>>26==43 and (w>>21)&31==30 and (w>>16)&31==0 and (w&65535) in (0x48,0x4c,0x50):zero_sites.append(dict(address=hex(x.address),stack_offset=w&65535))
            if name=='store_selector' and w>>26==35 and w&65535==0xa4:service_reads.append(dict(address=hex(x.address),instruction=x.mnemonic+' '+x.op_str))
    assert len(zero_sites)==3 and len(service_reads)==1
    js('source-field-evidence.json',dict(carryover_accumulator_zero_sites=zero_sites,normalized_service_read=service_reads,reference='See full store_metric_builder/store_selector instructions and physical-slot loop boundaries in pricing-readers.asm.'))
    (ROOT/'pricing-readers.asm').write_text('\n'.join(asm)+'\n');js('source-ranges.json',manifest)
    js('summary.json',dict(products=27,editable_products=26,profiles=144,arrival_mode_counts=dict(sorted(modes.items())),arrival_ranges=ranges,weight_sum_min=min(weight_sums),weight_sum_max=max(weight_sums),new_work='Connect raw price settings to currency prices, all144 named profile weights/ranges, and normalized service rather than security. Document physical-slot carryover with exact zero/store sites and a concrete identical-shop example.',known_before='Core selector and metric-builder formulas already existed in independently reconstructed models.',original_cpu_updates=0))
    print(json.dumps(dict(products=27,profiles=144,ranges=ranges,carryover_price_example=[s['stored_price_factor'] for s in carry],service_read=service_reads),ensure_ascii=False))
if __name__=='__main__':main()
