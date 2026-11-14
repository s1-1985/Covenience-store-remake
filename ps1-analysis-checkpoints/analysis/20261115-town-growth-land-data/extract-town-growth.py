#!/usr/bin/env python3
"""Extract monthly town-growth source parameters and initial influence maps."""
import argparse,collections,hashlib,json,runpy,struct
from pathlib import Path
from capstone import Cs,CS_ARCH_MIPS,CS_MODE_MIPS32,CS_MODE_LITTLE_ENDIAN
ROOT=Path(__file__).resolve().parent
DISC_SHA='8d8eda789c5a2fe892a4722719b0466dd7d126eed6cd99ad05a807d81b57d1c1'
EXE_SHA='d6a167a1c9e0fe98d7e44e12968caa489ac3eb7ed3b9e46012a188af8432b1fd'
MAPS=['TOWN0001','TOWN0002','TOWN0003','TOWNPS']
def sha(b):return hashlib.sha256(b).hexdigest()
def i32(v):return (v+2**31)%2**32-2**31
def s8(v):return (v+128)%256-128
def trunc(a,b):return (-1 if (a<0)!=(b<0) else 1)*(abs(a)//abs(b))
def write(n,x):(ROOT/n).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')

def baseline(sales,population,reference):
    total=0
    for value in sales:total=i32(total+value)
    average=trunc(total,population) if population>0 else total
    if average<=0:average=reference
    result=trunc(i32(i32(average-reference)*10),average) if average>=reference else -trunc(i32(i32(reference-average)*100),reference)
    return s8(result),average

def source_influence(town,base):
    grid=[base]*3000;roads=[];stations=[];categories=[struct.unpack_from('<b',town,k*8+4)[0] for k in range(3000)]
    for y in range(50):
        for x in range(60):
            tile=struct.unpack_from('<h',town,(y*60+x)*8)[0]
            if tile in (70,72):
                stations.append([x,y,tile])
                for yy in range(max(0,y-8),min(49,y+8)+1):
                    for xx in range(max(0,x-8),min(59,x+8)+1):
                        k=yy*60+xx;grid[k]=s8(min(100,grid[k]+30))
            if 50<=tile<=52:
                roads.append([x,y,tile])
                # Native BE0/BE0 loop is one vertical position, not y-3..y+3.
                targets=[(x,max(0,y-3))]+[(xx,y) for xx in range(max(0,x-3),min(59,x+3)+1)]
                for xx,yy in targets:
                    k=yy*60+xx
                    if categories[k]!=1:grid[k]=s8(min(100,grid[k]+10))
    return grid,roads,stations

def main():
    ap=argparse.ArgumentParser();ap.add_argument('disc',type=Path);args=ap.parse_args()
    raw=args.disc.read_bytes();assert sha(raw)==DISC_SHA
    iso=runpy.run_path(str(ROOT.parent/'20261113-disc-data-extraction/extract-disc-data.py'))['iso']
    rows,read=iso(raw);files={r['path']:r for r in rows}
    def payload(p):r=files[p];return read(r['lba'],r['bytes'])
    exe=payload('/SLPS_007.82');assert sha(exe)==EXE_SHA
    def at(a,n):return exe[a-0x80010000+2048:a-0x80010000+2048+n]
    groups=[list(zip(*[iter(struct.unpack('<10h',at(0x8009ff1c+j*20,20)))]*2)) for j in range(137)]
    # 137 rows end exactly at the following144-record shopping-profile table.
    assert 0x8009ff1c+137*20==0x800a09d0
    buildings=json.loads((ROOT.parent/'20261114-land-construction-cost-data/building-demolition-master.json').read_text())['rows'][:72]
    assert [buildings[j]['tile_lower'] for j in (14,16,20,21)]==[50,52,70,72]
    categories={c:[d['id'] for d in buildings if d['category']==c] for c in range(11)}
    catalog=[]
    for j in sorted(set(range(18,50))|set(categories[5])|set(categories[8])):
        d=buildings[j];b=at(0x8009d738+j*56,56)
        catalog.append(dict(id=j,name=d['name'],category=d['category'],footprint=[d['width'],d['height']],tiles=[d['tile_lower'],d['tile_upper']],
            customer_mix_choices=list(struct.unpack_from('<5h',b,42)),notification_event=struct.unpack_from('<h',b,52)[0]))
    write('growth-building-choices.json',dict(lookup_rows=72,categories=categories,buildings=catalog,
        housing=dict(level_8_to_14=list(range(43,49)),level_15_up=list(range(43,50)),rule='43 + RNG%(6 if level<15 else7), no category-wide random substitution.'),
        company=dict(category=4,target='residential population'),retail=dict(category=5,target='trunc(residential population/4)'),
        public_facilities=dict(population_5000_to_7999=dict(categories=[8],radius=100),population_8000_to_19999=dict(categories=[6,7,8],radius=50),
            population_20000_up=dict(categories=[6,7,8],radius=30),
            selection='At >=8000 choose category6+RNG%3 then choose a row uniformly by RNG%category_row_count. Preserve category-first selection; row probabilities differ between categories.'),
        administration=dict(tier1=22,tier2=23,tier3=23,tier4=24)))
    worlds=[];blob=bytearray();curves=[]
    for name in MAPS:
        data=payload('/DAT/'+name+'.BIN');town=data[17:24017];reference,divisor=struct.unpack_from('<2i',data,9)
        pop=collections.Counter();group_refs=collections.Counter()
        for k in range(3000):
            category=struct.unpack_from('<b',town,k*8+4)[0];mix=struct.unpack_from('<h',town,k*8+6)[0]
            if mix==-1:continue
            assert 0<=mix<137;group_refs[mix]+=1
            # Native population accepts any pid except-1, including pid144.
            pop[category]=i32(pop[category]+sum(count for pid,count in groups[mix] if pid!=-1))
        stores=[]
        for slot in range(10):
            s=data[25907+slot*5080:25907+(slot+1)*5080]
            if s[0]:stores.append(dict(slot=slot,previous_month_sales_D5C=struct.unpack_from('<i',s,0xd5c)[0],rect=list(struct.unpack_from('<4i',s,8))))
        sales=[s['previous_month_sales_D5C'] for s in stores];assert all(v==0 for v in sales)
        base,average=baseline(sales,pop[3],reference);assert base==0
        grid,roads,stations=source_influence(town,base);offset=len(blob);blob.extend(bytes(v&255 for v in grid))
        admin=next(([k%60,k//60] for k in range(3000) if struct.unpack_from('<b',town,k*8+4)[0]==9),None)
        hist=dict(sorted(collections.Counter(grid).items()));land=dict(sorted(collections.Counter(struct.unpack_from('<b',town,k*8+2)[0] for k in range(3000)).items()))
        worlds.append(dict(map=name,source_town_sha256=sha(data),sales_per_resident_reference=reference,store_sales_influence_divisor=divisor,
            population_by_category=dict(sorted(pop.items())),total_population=sum(pop.values()),residential_population=pop[3],
            source_stores=stores,source_base_influence=base,source_average_after_fallback=average,roads=len(roads),station_origins=stations,
            first_administrative_cell=admin,land_coefficient_histogram=land,influence_histogram=hist,
            positive_influence_cells=sum(v>0 for v in grid),influence_file_offset=offset,
            active_customer_mix_count=len(group_refs),
            neutral_average_at_reference_total_sales=reference*pop[3],
            growth_first_positive_average=(10*reference+8)//9,
            development_balance_targets=dict(company=pop[3],retail=trunc(pop[3],4)),
            initial_public_facility_population_gate=sum(pop.values())>=5000))
        values=sorted(set([0,1,reference//4,reference//2,reference*9//10,reference,(10*reference+8)//9,reference*2,reference*10]))
        curves.append(dict(map=name,reference=reference,residential_population=pop[3],scenarios=[dict(
            input_average=v,total_sales=v*pop[3],effective_average=baseline([v*pop[3]],pop[3],reference)[1],
            base_influence=baseline([v*pop[3]],pop[3],reference)[0]) for v in values],
            note='Constructed source-arithmetic inputs, not observed store earnings. Zero/nonpositive mean falls back to source reference and yields0.'))
    (ROOT/'initial-influence.i8').write_bytes(blob)
    write('initial-town-growth-inputs.json',dict(source_disc_sha256=DISC_SHA,source_exe_sha256=EXE_SHA,worlds=worlds,
        binary=dict(path='initial-influence.i8',map_order=MAPS,bytes_per_map=3000,dimensions=[60,50],format='signed int8,row-major'),
        scope='Influence computed on raw initial source town/store records. All source D5C values0, so no store influence/RNG is needed for these specific files. This is not the real first-month input after player opening and a month of trading. No level changes, RNG calls or building placement executed.'))
    write('source-sales-response-examples.json',curves)
    residues=[]
    for g in range(-128,128):
        threshold=min(100,abs(g));success=327*threshold+min(threshold,68)
        residues.append(dict(influence=g,rng_draws=0 if g==0 else 1,
            matching_outputs=success if g else 0,total_outputs=32768,
            change=0 if g==0 else 1 if g>0 else -1,
            level_guard='level<25' if g>0 else 'level>=2' if g<0 else 'no change'))
    write('land-level-transition-rules.json',dict(source_cell_byte=2,land_price_per_level=1000000,initial_level=5,
        normal_bounds=[1,25],rules=residues,
        interpretation='Counts enumerate the32768 possible15-bit RNG outputs. They are not independent per-cell outcome probabilities for a fixed seed; modulo100 is slightly biased.',
        housing_action_residues=dict(test='RNG%100+1<3',matching_outputs=656,total_outputs=32768),
        minimum_draw_order='Row-major cells: if influence nonzero draw once before level bound check; then if resulting level<4 draw residential-removal gate; reread level; if level>=8 draw housing-build gate and on pass draw housing index. Placement/demolition consumes additional RNG per affected cell.'))
    tiers=[dict(population_lower=0,population_upper=4999,tier=0,station_target=0,administration=None),
        dict(population_lower=5000,population_upper=7999,tier=1,station_target=1,administration=22),
        dict(population_lower=8000,population_upper=15999,tier=2,station_target=2,administration=23),
        dict(population_lower=16000,population_upper=19999,tier=3,station_target=3,administration=23),
        dict(population_lower=20000,population_upper=None,tier=4,station_target=4,administration=24)]
    write('monthly-development-rules.json',dict(run_gate=dict(day=1,hour=0,subhour=0,reader='2BD84..2BDC8'),
        parent_order=['275F8','29020','29334 daily/monthly finance','2A8E0','2BD54 town growth'],
        sales='D5C is prior-month revenue after financial monthly rollup. Original29334 runs first and stores month revenue multiplied by8; do not multiply by8 a second time in growth.',
        land='Update each signed cell+2 by at most1; then test local building removal/placement on the resulting level. New/removed buildings retain this land value.',
        housing_removal=dict(level_below=4,random_residue_percent=2,category=3),
        housing_build=dict(level_at_least=8,random_residue_percent=2,large_residence_at_level=15,feasibility_required=True),
        balance='Recompute residential population after local cell actions. For company then retail scan from random x/y with wrapped row-major coordinates, max one mutation each. Negative target difference: remove matching category only at level<3; positive difference: try category-chosen building at level>=9. Stop after success; infeasible candidates do not guarantee construction.',
        public='At totalpopulation>=5000 choose one category/row, random-origin wrapped scan; candidate level>=5, feasibility0, no same building within population-based radius. At mostone public building here; no direct company cash debit in2BD54.',
        town_tiers=tiers,
        station='Count only tile70/72 anchors from current scan. Initial threshold11; update it to greater level of eligible rail sites with no station within40, then subtract1. If station_count<tier, try one small station20 using this threshold, feasibility and radius40.',
        administrative='Only when new tier exceeds stored CD98C, update CD98C, choose22 at1,23 at2/3,24 at4, and place at first row-major category9 cell. Do not silently replace(-1,-1) with a guessed origin in malformed states. Source initial maps all supply an administrative cell. Mode0+building24 sets progress flag bit1 and counter0 instead of normal notice.',
        finish='Population history60 words shifts once and new population goes at head. Months6/12 queue a notice. Rebuild map masks1F8BC only after all building actions; dirtyCD8DC=0.',
        feasibility='Respect mutable current town flags during sequential placements; do not evaluate all intended buildings against a frozen initial map.'))
    write('android-town-growth-bridge.json',dict(schema_version=1,
        baseline='Sum ordered stores D5C with signed32 wrapping. Divide by population(category3) ifpositive. Nonpositive mean falls back to map reference. If mean>=reference use trunc((mean-reference)*10/mean), else -trunc((reference-mean)*100/reference), then signed byte.',
        roads='Every tile50..52: +10 at(x,max(0,y-3)), then at all(x-3..x+3,y), clipped. Skip category1 target cells, cap each addition at100. Original vertical loop ends at BE0, not BE8. Keep this asymmetry.',
        stations='Every tile70 or72 origin adds30 to inclusive square radius8, clipped, cap100. One influence per station anchor, not one per every station tile.',
        stores='Process CE61C order until-1. Strength=signed8(min(100,trunc(D5C/map_divisor))). Skip nonpositive strength. Expand store rectangle by12; inner rectangle expansion7 always receives strength, outer ring receives only when RNG&3==0. Ring consumes a draw per candidate; cap additions100. Do not apply store influence to the raw source map dump when all source D5C0.',
        thresholds='Land1..25 normal range, at mostone step per update; housing gates4/8/15; company and retail build9/removebelow3; publicbuild5; populationtiers5000/8000/16000/20000. Keep population and shopping-profile validity separate.',
        sequencing='Monthly finance precedes growth. In growth, grid inputs are read before local level/building updates; later balance/public/administrative population is recomputed after preceding mutations. Preserve order, target predicates, and RNG call order.',
        native='These extracted values/rules are inputs to native Android logic. No PS emulator/BIOS/original EXE runtime needed. No APK change in this extraction.'))
    (ROOT/'source').mkdir(exist_ok=True);ranges=[];asm=[];md=Cs(CS_ARCH_MIPS,CS_MODE_MIPS32|CS_MODE_LITTLE_ENDIAN)
    for name,a,end in [('monthly_growth',0x8002bd54,0x8002e138),('finance_before_growth',0x80023490,0x800234b8),
        ('population_reader',0x80020498,0x800206ac),('building_choice',0x80020364,0x80020498),
        ('land_price',0x8001dfd0,0x8001e1a8),('rng',0x8007e648,0x8007e690)]:
        b=at(a,end-a);(ROOT/'source'/f'{name}.bin').write_bytes(b);ranges.append(dict(name=name,address=hex(a),bytes=len(b),sha256=sha(b)))
        asm.append(f'\n# {name} {a:#x}..{end:#x}');asm.extend(f'{i.address:08x}: {i.bytes.hex()} {i.mnemonic} {i.op_str}' for i in md.disasm(b,a))
    (ROOT/'growth-readers.asm').write_text('\n'.join(asm)+'\n');write('source-ranges.json',ranges)
    write('source-dependencies.json',dict(town_cells='../20261114-security-theft-data/source/town-cells.bin',
        building_master='../20261114-land-construction-cost-data/source/building-descriptors.bin',
        population_mixes='../20261113-customer-data/source/customer-mixes.bin',
        note='Reuses source bytes. Extractor rereads disc; no full EXE/RAM duplication.'))
    write('summary.json',dict(maps=4,source_cells=12000,building_lookup_rows=72,customer_mix_rows=137,influence_values=256,
        population={w['map']:w['total_population'] for w in worlds},references={w['map']:w['sales_per_resident_reference'] for w in worlds},
        source_influence_histograms={w['map']:w['influence_histogram'] for w in worlds},positive_influence_cells={w['map']:w['positive_influence_cells'] for w in worlds},
        original_cpu_updates=0,known_before='Town growth/monthly isolated rules and whole source interpreter existed. New extraction binds actual four map economic parameters/category populations and road coordinates to initial influence maps, 72-row building choice sets,137 population mixes, land-price byte, calendar/finance ordering and native Android rules.',
        limits='Initial-source influence only; not an actual first-month run, future outcome prediction or native Android/APK update.'))
    print((ROOT/'summary.json').read_text())
if __name__=='__main__':main()
