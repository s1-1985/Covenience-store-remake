#!/usr/bin/env python3
"""Static PS1 restocking and stock-acquisition contracts, with named capacities.
No original game CPU runs or long simulated operating sessions.
"""
import argparse,hashlib,json,runpy,struct
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
    prior=json.loads((ROOT.parent/'20261113-product-stock-data/product-fixture-data.json').read_text());labels={r['id']:r['name'] for r in prior['fixtures']}
    fixtures=[]
    for i in range(53):
        a=0x80099f0c+i*196;words=list(struct.unpack('<49i',at(a,196)));allowed=words[21:48];allowed=allowed[:next((j for j,v in enumerate(allowed) if v==-1),len(allowed))]
        if not allowed:continue
        capacity=words[3];assert 0<capacity<=127
        rows=[]
        for selection_skill in [0,25,50,75,100]:
            threshold=selection_skill*2//3;max_qty=((threshold+1)*capacity-1)//100
            rows.append(dict(selection_skill_byte20=selection_skill,open_or_closing_threshold_percent=threshold,max_existing_quantity_eligible=max_qty))
        fixtures.append(dict(id=i,name=labels[i],capacity=capacity,size=words[9:11],category=words[0]&255,allowed_products=allowed,open_threshold_examples=rows,closed_or_opening_max_existing_quantity=capacity-1))
    abilities=[dict(refill_skill_byte1f=i,request_quantity_on_success=i//10+1,success_gate=f'roll1..100<={i}',reservation_exclusion_raw_threshold=2*i,reservation_exclusion_effective_cutoff=min(100,2*i)) for i in range(101)]
    js('restocking-capacity-masters.json',dict(source_disc_sha256=DISC_SHA,source_exe_sha256=EXE_SHA,fixtures=fixtures,skill_rules=abilities,label_dependency='../20261113-product-stock-data/product-fixture-data.json; numeric fields reread from disc',note='Fixture rows cover those with allowed-product lists, not parking/rest facilities. Capacity is one fixture total, not per rendered tile.'))
    js('android-restocking-stockout-bridge.json',dict(schema_version=1,source_exe_sha256=EXE_SHA,staff_field_roles={'0x20':'target-selection threshold input; distinct from actual refill skill; no new semantic label assigned','0x1f':'actual refill success and quantity; also another refilling employee reservation exclusion','0x28':'task state;2 means refill','0x2c..0x2e':'goal x,y,direction'},target_selection=dict(function='0x80038d6c',store_state='store+C77:0closed,1open,2closing,3opening',threshold='trunc(2*staff_byte20/3) for states1/2; otherwise99',predicate='Anchor bit31 set, kind<53, nonzero product image; trunc(quantity*100/capacity)<=threshold',routing='Mark usable fixture sides, then route search selects reachable target by source distance/frontier order; it does not sort eligible fixtures by remaining quantity.',image_zero='No product image means not a candidate. Quantity0 with a retained image remains a candidate.',reservation='For each other staff on task2: draw roll, exclude their target sides if roll<=2*their refill skill1f and target is valid. This is probabilistic, not an unconditional lock.'),work_priority='If energy<=0 choose rest; otherwise eligible cashier target before refill, then cleaning, then rest. This is task-choice order, not a continuous preemption rule.',refill_action=dict(function='0x8003b278',success='One roll1..100 must be<=signed staff_byte1f; otherwise return1 without inventory or money mutation.',request='trunc(refill skill/10)+1',applied='min(request, capacity-current quantity)',unit_cost='trunc(base_price*cost_percent/100)',cash='Applied quantity*unit_cost added to store+D94, subtracted from owning side cash. No balance refusal appears in this local caller.',continuation='Return1 means failed attempt or not-yet-full shelf; parent keeps target. Return0 means full; parent clears target, applies growth and sound0x800. Return2 error also clears target.',threshold_scope='Threshold is for choosing a new target. It is not the final desired stock level; retained job refills toward full capacity.'),acquisition=dict(function='0x8003b420 ->800209f8',request='Current customer group quantity byte+1e, as one all-or-nothing subtraction.',failure='No matching product/anchor or insufficient total quantity -> no stock decrement; caller increments store+12e2 by1 if signed counter<127; returns failure1.',count_unit='One failed acquisition call, not number of people or missing units.'),unmet_product_demand=dict(function='purchase_control800340fc',condition='Destination search failed, current product!=-1 and product stock summary==0.',write='store+119c+12*product += group quantity',scope='Separate from acquisition failure+12e2. No new outside-store rerouting behavior is inferred.'),advice=dict(counter='signed store+12e2',threshold='trunc((100-manager leadership1d)/4)+5; trigger uses counter>threshold',examples=[{'leadership':100,'threshold':5,'first_trigger_count':6},{'leadership':0,'threshold':30,'first_trigger_count':31}],counter_resets='Existing four-hour/advice/rare-reset rules in3B570; see floor-cleaning report.')))
    # Source-arithmetic example, no CPU simulation. Attribute20 selects; attribute1f acts.
    capacity=40;selection_skill=100;refill_skill=100;quantity=26;unit_cost=55;steps=[]
    while quantity<capacity:
        before=quantity;applied=min(refill_skill//10+1,capacity-quantity);quantity+=applied
        steps.append(dict(before=before,requested=11,added=applied,after=quantity,cost=unit_cost*applied,inventory_return=0 if quantity==capacity else 1))
    assert steps==[dict(before=26,requested=11,added=11,after=37,cost=605,inventory_return=1),dict(before=37,requested=11,added=3,after=40,cost=165,inventory_return=0)]
    assert next(f for f in fixtures if f['id']==13)['capacity']==40 and 0 in next(f for f in fixtures if f['id']==13)['allowed_products']
    js('source-derived-examples.json',dict(scope='Arithmetic examples from source formulas; no captured gameplay run.',target_boundary=dict(capacity=40,selection_skill_byte20=100,threshold=66,quantity26_percent=65,quantity26_eligible=True,quantity27_percent=67,quantity27_eligible=False),refill_to_full=dict(fixture_id=13,fixture_name=labels[13],product_id=0,initial=26,capacity=40,refill_skill=100,unit_cost=55,steps=steps),group_stock_failure=dict(available=2,requested_group_quantity=3,result_stock=2,acquisition_counter_increment=1,partial_purchase=False),leadership_warning=dict(leadership=100,threshold=5,at5=False,at6=True)))
    spans=[('fixture_master',0x80099f0c,53*196,False),('product_master',0x8009cdf0,27*88,False),('refill_target_selection',0x80038d6c,0x80039428-0x80038d6c,True),('refill_caller',0x8003b278,0x8003b420-0x8003b278,True),('acquisition_caller',0x8003b420,0x8003b570-0x8003b420,True),('inventory_update',0x800209f8,0x80021f20-0x800209f8,True),('staff_refill_parent_excerpt',0x80037428,0x80037734-0x80037428,True),('unmet_demand_excerpt',0x800343b4,0x800344e8-0x800343b4,True),('advice_threshold_excerpt',0x8003b570,0x8003b9f0-0x8003b570,True)]
    (ROOT/'source').mkdir(exist_ok=True);md=Cs(CS_ARCH_MIPS,CS_MODE_MIPS32|CS_MODE_LITTLE_ENDIAN);asm=[];manifest=[]
    for name,a,n,is_code in spans:
        b=at(a,n);(ROOT/'source'/f'{name}.bin').write_bytes(b);manifest.append(dict(name=name,address=hex(a),bytes=n,sha256=sha(b)))
        if is_code:
            asm.append(f'\n# {name} {a:#x} bytes={n}');asm.extend(f'{x.address:08x}: {x.bytes.hex()} {x.mnemonic} {x.op_str}' for x in md.disasm(b,a))
    (ROOT/'restocking-readers.asm').write_text('\n'.join(asm)+'\n');js('source-ranges.json',manifest)
    js('summary.json',dict(stock_fixtures=len(fixtures),unique_capacities=sorted({f['capacity'] for f in fixtures}),skill_inputs=101,new_work='Connect source capacity tables to separate target-selection and execution skill fields, threshold-vs-full refill continuation, reservation behavior, and two distinct stock-out counters.',existing_work='Independent inventory, staff target and purchase models existed earlier; this work extracts the named master contract and cross-function meaning.',original_cpu_updates=0))
    print(json.dumps(dict(stock_fixtures=len(fixtures),capacities=sorted({f['capacity'] for f in fixtures}),refill_example=steps)))
if __name__=='__main__':main()
