#!/usr/bin/env python3
"""Extract original project master and site costs from the hash-verified PS1 disc.
No CPU emulation or gameplay progression. Source cells remain separate from derived data.
"""
import argparse, collections, hashlib, json, runpy, struct, zlib
from pathlib import Path
ROOT=Path(__file__).resolve().parent
DISC_SHA='8d8eda789c5a2fe892a4722719b0466dd7d126eed6cd99ad05a807d81b57d1c1'
EXE_SHA='d6a167a1c9e0fe98d7e44e12968caa489ac3eb7ed3b9e46012a188af8432b1fd'
MAPS=['TOWN0001','TOWN0002','TOWN0003','TOWNPS']
def sha(b):return hashlib.sha256(b).hexdigest()
def i32(x):return (x+2**31)%2**32-2**31
def trunc(x,n):return (1 if x>=0 else -1)*(abs(x)//n)
def save(n,x):(ROOT/n).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def main():
    ap=argparse.ArgumentParser();ap.add_argument('disc',type=Path);args=ap.parse_args()
    raw=args.disc.read_bytes();assert sha(raw)==DISC_SHA
    iso=runpy.run_path(str(ROOT.parent/'20261113-disc-data-extraction/extract-disc-data.py'))['iso']
    entries,read=iso(raw);files={r['path']:r for r in entries}
    def payload(p):r=files[p];return read(r['lba'],r['bytes'])
    exe=payload('/SLPS_007.82');assert sha(exe)==EXE_SHA
    def at(a,n):return exe[a-0x80010000+2048:a-0x80010000+2048+n]
    buildings=[]
    for j in range(72):
        b=at(0x8009d738+j*56,56);w,h,lo,hi=struct.unpack_from('<4i',b,24);c,attr=struct.unpack_from('<2b',b,40)
        buildings.append(dict(id=j,name=b[:24].split(b'\0')[0].decode('shift_jis'),width=w,height=h,lower=lo,upper=hi,category=c,attribute=attr,
                              groups=list(struct.unpack_from('<5h',b,42)),event=struct.unpack_from('<h',b,52)[0]))
    # Native 20238 lookup: only first 72 rows, fallback row0.
    lookup={t:d for d in reversed(buildings) for t in range(d['lower'],d['upper']+1)}
    master=at(0x8009fcd8,360);(ROOT/'source/project-master.bin').write_bytes(master)
    projects=[]
    mixes=[list(zip(*[iter(struct.unpack('<10h',at(0x8009ff1c+j*20,20)))]*2)) for j in range(137)]
    for j in range(18):
        b=master[j*20:(j+1)*20];kind=struct.unpack_from('<h',b)[0];d=buildings[kind]
        base=0
        for k in range(d['width']*d['height']):base=i32(base+i32(d['attribute']*1000000))
        base=trunc(base,10)
        projects.append(dict(selection=j,kind=kind,name=d['name'],footprint=[d['width'],d['height']],category=d['category'],attribute=d['attribute'],base_cost=base,
            tile_range=[d['lower'],d['upper']],customer_mix_choices=d['groups'],notification_event=d['event'],completion_name_message=98+struct.unpack('<h',at(0x80098768+kind*2,2))[0],
            raw_hex=b.hex(),unassigned_fields={'i16_at_2':struct.unpack_from('<h',b,2)[0],'i16_at_4':struct.unpack_from('<h',b,4)[0],
                'i16_at_6':struct.unpack_from('<h',b,6)[0],'i32_at_8':struct.unpack_from('<i',b,8)[0],'i32_at_16':struct.unpack_from('<i',b,16)[0]},mutable_cost_at_12=struct.unpack_from('<i',b,12)[0]))
    for p in projects:
        choices=[]
        for m in p['customer_mix_choices']:
            pairs=[] if m==-1 else mixes[m]
            choices.append(dict(mix=m,profiles=[[pid,n] for pid,n in pairs if pid!=-1],population=sum(n for pid,n in pairs if pid!=-1)))
        area=p['footprint'][0]*p['footprint'][1];values=[c['population'] for c in choices]
        p['per_cell_mix_choices']=choices
        p['completed_building_population_range']=[area*min(values),area*max(values)]
        p['population_scope']='Native customer-profile population over all footprint cells, not exclusively residential residents. Each written cell chooses one of five entries with RNG%5; duplicate entries retain their weights.'
    save('project-master.json',dict(address='0x8009fcd8',stride=20,rows=projects,unknown='Fields +2,+4,+6,+8,+16 are retained without assigning meaning. +8 is not used as construction time or base cost by the recovered project path.'))
    allcosts=bytearray();worlds=[];totals=collections.Counter();outside_examples=[]
    for name in MAPS:
        data=payload('/DAT/'+name+'.BIN');town=data[17:24017];tiles=list(struct.unpack_from('<h',town,k*8)[0] for k in range(3000))
        cats=list(struct.unpack_from('<b',town,k*8+4)[0] for k in range(3000));land=list(struct.unpack_from('<b',town,k*8+2)[0] for k in range(3000))
        # Source load rebuilds mask16 from positive town category. Store overlays add only bits1,2,4,8.
        flags=[0 if c<=0 else (16 if c in (3,4,5) else 24) for c in cats]
        rows=[]
        for p in projects:
            w,h=p['footprint'];kind=p['kind'];grid=[-1]*3000;count=0;bounds=3000-(61-w)*(51-h);blocked=0;examples={};hist=collections.Counter();outside_count=0
            for y in range(51-h):
                for x in range(61-w):
                    cells=[yy*60+xx for yy in range(y,y+h) for xx in range(x,x+w)]
                    def reject(k):
                        if not flags[k]&16:return False
                        if kind==49:return not buildings[43]['lower']<=tiles[k]<=buildings[48]['upper']
                        if 3<=p['category']<=5:return True
                        return not 3<=cats[k]<=5
                    if any(reject(k) for k in cells):blocked+=1;continue
                    lv=0
                    for k in cells:lv=i32(lv+i32(land[k]*1000000))
                    demolition=0;covered=set();builds=[];outside=set()
                    for k in cells:
                        if k in covered:continue
                        yy,xx=divmod(k,60);d=lookup.get(tiles[k],buildings[0]);dw,dh=d['width'],d['height']
                        demolition=i32(demolition+i32(dw*dh*d['attribute']*1000000))
                        delta=tiles[k]-d['lower'];left=xx-(delta-trunc(delta,dw)*dw)
                        top=yy-trunc(tiles[yy*60+left]-d['lower'],dw)
                        affected={ay*60+ax for ay in range(top,top+dh) for ax in range(left,left+dw)}
                        assert all(0<=a<3000 for a in affected)
                        covered.update(affected)
                        if d['category']>0:
                            builds.append([d['id'],left,top]);outside.update(affected-set(cells))
                    site=trunc(i32(lv+demolition),10);fee=i32(p['base_cost']+site);grid[y*60+x]=fee;count+=1;hist[fee]+=1
                    ex=dict(origin=[x,y],rect=[x,y,x+w-1,y+h-1],base_cost=p['base_cost'],land=lv,full_demolition=demolition,site_surcharge=site,total_charge=fee,minimum_cash_to_confirm=fee+1)
                    if 'cheapest' not in examples or fee<examples['cheapest']['total_charge']:examples['cheapest']=ex
                    if 'most_expensive' not in examples or fee>examples['most_expensive']['total_charge']:examples['most_expensive']=ex
                    if outside:
                        outside_count+=1
                        if len(outside_examples)<12 and not any(e['map']==name and e['selection']==p['selection'] for e in outside_examples):
                            outside_examples.append(dict(map=name,selection=p['selection'],name=p['name'],**ex,removed_buildings=builds,outside_selected_rect=[[k%60,k//60] for k in sorted(outside)],
                                effect='Mode0 demolition clears entire old positive-category footprints, including these cells outside the selected rectangle. They are not reserved as project land.'))
            assert count+blocked+bounds==3000
            encoded=struct.pack('<3000i',*grid);offset=len(allcosts);allcosts.extend(encoded)
            rows.append(dict(selection=p['selection'],name=p['name'],candidate_origins=3000,out_of_bounds=bounds,blocked=blocked,allowed=count,
                sites_removing_cells_outside_rect=outside_count,cost_grid_offset=offset,cost_grid_bytes=len(encoded),cost_grid_sha256=sha(encoded),
                cost_histogram={str(k):v for k,v in sorted(hist.items())},examples=examples))
            totals.update(allowed=count,blocked=blocked,out_of_bounds=bounds)
        worlds.append(dict(map=name,source_town_sha256=sha(data),projects=rows))
    (ROOT/'project-cost-grids.i32.zlib').write_bytes(zlib.compress(allcosts,9))
    save('map-project-costs.json',dict(context='Static original maps after mask rebuild, before any player project or town growth; excludes cash/active-project gating.',
        grid=dict(file='project-cost-grids.i32.zlib',compression='zlib',decompressed_bytes=len(allcosts),sha256=sha(allcosts),ordering='map order, selection0..17, y*60+x; signed little-endian i32; -1 invalid; otherwise full fee, not just site surcharge',maps=MAPS),maps=worlds))
    save('whole-building-removal-examples.json',outside_examples)
    ranges=[('gate',0x800643f8,0x8006443c),('menu_start',0x8006a44c,0x8006b1cc),('site_confirm',0x8006b520,0x8006b620),('quote',0x800752c4,0x80075514),('completion',0x80029020,0x80029334)]
    sources=[]
    for n,a,b in ranges:
        v=at(a,b-a);(ROOT/f'source/{n}.bin').write_bytes(v);sources.append(dict(file=f'source/{n}.bin',start=hex(a),end_exclusive=hex(b),sha256=sha(v)))
    save('source-ranges.json',dict(disc_sha256=DISC_SHA,exe_sha256=EXE_SHA,ranges=sources))
    summary=dict(project_types=18,maps=4,candidate_origins=216000,**dict(totals),base_cost_min=min(p['base_cost'] for p in projects),base_cost_max=max(p['base_cost'] for p in projects),
        construction_midnight_ticks=[4,8],original_cpu_updates=0,grid_bytes=len(allcosts),grid_compressed_bytes=(ROOT/'project-cost-grids.i32.zlib').stat().st_size,
        known_before='Isolated quote/start/completion rules and helpers existed. Newly extracted all18 master rows and linked native building descriptors to 4 maps, 216000 origins, site costs, completion names/events, and whole-building spillover examples.')
    save('summary.json',summary);print(json.dumps(summary,ensure_ascii=False))
if __name__=='__main__':main()
