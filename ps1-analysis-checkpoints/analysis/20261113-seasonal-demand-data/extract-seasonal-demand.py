#!/usr/bin/env python3
"""Extract seasonal/customer eligibility data from the PS1 disc, without emulation."""
import argparse, hashlib, json, runpy, struct
from pathlib import Path
from capstone import Cs, CS_ARCH_MIPS, CS_MODE_MIPS32, CS_MODE_LITTLE_ENDIAN
ROOT=Path(__file__).resolve().parent
DISC_SHA='8d8eda789c5a2fe892a4722719b0466dd7d126eed6cd99ad05a807d81b57d1c1'
EXE_SHA='d6a167a1c9e0fe98d7e44e12968caa489ac3eb7ed3b9e46012a188af8432b1fd'
def sha(b):return hashlib.sha256(b).hexdigest()
def js(name,data):(ROOT/name).write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
def regime(season,month):
    preferred={1:(6,7,8),2:(12,1,2)}.get(season,())
    opposite={1:(12,1,2),2:(6,7,8)}.get(season,())
    return 'preferred' if month in preferred else 'opposite' if month in opposite else 'neutral'
def main():
    ap=argparse.ArgumentParser();ap.add_argument('disc',type=Path);args=ap.parse_args()
    disc=args.disc.read_bytes();assert sha(disc)==DISC_SHA
    lib=runpy.run_path(str(ROOT.parent/'20261113-disc-data-extraction/extract-disc-data.py'))
    files,read=lib['iso'](disc);r=next(r for r in files if r['path']=='/SLPS_007.82');exe=read(r['lba'],r['bytes']);assert sha(exe)==EXE_SHA
    def at(a,n):return exe[a-0x80010000+2048:a-0x80010000+2048+n]
    products=[]
    for i in range(27):
        b=at(0x8009cdf0+i*88,88)
        products.append(dict(id=i,name=b[:24].split(b'\0')[0].decode('shift_jis'),season_code=struct.unpack_from('<i',b,84)[0],primary_profile_ids=[],extra_slots=[]))
    profiles=[]
    for i in range(144):
        b=at(0x800a09d0+i*24,24);ids=list(struct.unpack_from('<4b',b,8));importance,focus,weekday,holiday=[struct.unpack_from('<b',b,k)[0] for k in [13,20,21,22]]
        profiles.append(dict(id=i,product_ids=ids,shopping_importance=importance,focus_threshold=focus,weekday_threshold=weekday,holiday_threshold=holiday,weather_max_accepted=importance+20))
        for slot,p in enumerate(ids):
            if p==-1:continue
            assert 0<=p<27
            if slot==0:products[p]['primary_profile_ids'].append(i)
            else:products[p]['extra_slots'].append(dict(profile=i,slot=slot))
    assert all(not products[i]['primary_profile_ids'] for i in [1,18,25,26])
    assert not products[26]['extra_slots']
    months=[]
    for month in range(1,13):
        thresholds=list(struct.unpack('<4i',at(0x800994b0+(month-1)*16,16)))
        days=list(struct.unpack('<4b',at(0x80099d88+(month-1)*4,4)))
        months.append(dict(month=month,weather_thresholds=thresholds,calendar_profile_share_selector=days,product_regimes=[regime(p['season_code'],month) for p in products]))
    blocked=[]
    for r in profiles:
        for slot,p in enumerate(r['product_ids'][1:],1):
            if p>=0 and r['focus_threshold']>=100 and products[p]['season_code']==0:
                blocked.append(dict(profile=r['id'],slot=slot,product=p,reason='Season0 always returns0; focus100 rejects every roll1..100 in the normal extra-candidate selection path.'))
    assert [(r['profile'],r['slot'],r['product']) for r in blocked]==[(108,2,24),(109,2,24)]
    js('extra-candidate-exclusions.json',dict(scope='Ordinary in-store extra-candidate selection using unmodified source profiles. This does not prove global unreachability under edits or other callers.',entries=blocked))
    # Each rule is per newly selected EXTRA candidate, conditional on reaching it.
    # No estimated purchase rate or independent-RNG probability multiplication.
    rules={
      'preferred':{'season_return':1,'season_rng_calls':0,'focus_rng_calls':0,'selection':'continue'},
      'neutral':{'season_return':0,'season_rng_calls':0,'focus_rng_calls':1,'selection':'skip if rand()%100+1 <= signed_profile_byte20; otherwise continue'},
      'opposite':{'season_return':'2 if season roll<=90, otherwise0','season_rng_calls':1,'focus_rng_calls':'1 only if season roll>90','selection':'skip on seasonal rejection, else apply the neutral focus gate'}
    }
    js('android-seasonal-demand-bridge.json',dict(schema_version=1,source_disc_sha256=DISC_SHA,source_exe_sha256=EXE_SHA,products=products,profiles=profiles,months=months,extra_candidate_rules=rules,primary_entry_rule='Entry initializes current product directly from profile+8. The in-store seasonal/focus gate is bypassed while that product is already assigned.',arrival_rule='Unless bypass flag is set: reject when profile+13+20 < weather; seasonal gate primary product and reject only return2; then apply selected weekday/holiday share roll.',cash_rule='No ordinary profile product slot references26. Cash is excluded from the store price-average accumulator. Customer withdrawal/fees are not established.',rng_rule='LCG seed=(seed*1103515245+12345)&0xffffffff; rand=(seed>>16)&32767. Preserve conditional call order and modulo100.'))
    md=Cs(CS_ARCH_MIPS,CS_MODE_MIPS32|CS_MODE_LITTLE_ENDIAN);manifest=[];asm=[];(ROOT/'source').mkdir(exist_ok=True)
    slices=[('product-master',0x8009cdf0,27*88,False),('shopping-profiles',0x800a09d0,144*24,False),('weather-thresholds',0x800994b0,192,False),('calendar-share-selectors',0x80099d88,48,False),('seasonal_gate',0x80027328,0x2d0,True),('demand_selection_chain',0x8002619c,0x80027328-0x8002619c,True),('purchase_control',0x800340fc,0x80035128-0x800340fc,True),('entry_initialization',0x800319ac,0x80031be4-0x800319ac,True),('cash_average_exclusion',0x80023f48,0x80024490-0x80023f48,True),('cash_fixture_immediate_class',0x800360a0,0xc0,True)]
    for name,a,n,is_code in slices:
        b=at(a,n);(ROOT/'source'/f'{name}.bin').write_bytes(b);manifest.append(dict(name=name,address=hex(a),bytes=n,sha256=sha(b)))
        if is_code:
            asm.append(f'\n# {name} {a:#x} bytes={n} sha256={sha(b)}')
            asm.extend(f'{x.address:08x}: {x.bytes.hex()} {x.mnemonic} {x.op_str}' for x in md.disasm(b,a))
    # Direct jal cross-references. This is a direct-call scan, not a whole-program proof.
    target=0x0c000000|((0x80027328>>2)&0x3ffffff)
    calls=[hex(0x80010000+o-2048) for o in range(2048,min(len(exe),2048+0x70000),4) if struct.unpack_from('<I',exe,o)[0]==target]
    assert calls==['0x80026680','0x80034268']
    (ROOT/'demand-readers.asm').write_text('\n'.join(asm)+'\n')
    js('source-ranges.json',dict(ranges=manifest,direct_season_gate_calls=calls,scan_start='0x80010000',scan_bytes='0x70000',scan_limit='Only direct jal instructions; indirect calls are not excluded.'))
    seasonal=[dict(id=p['id'],name=p['name'],season_code=p['season_code'],primary_profiles=len(p['primary_profile_ids']),extra_slots=len(p['extra_slots'])) for p in products if p['season_code']]
    js('summary.json',dict(seasonal_products=seasonal,extra_only_products=[dict(id=i,name=products[i]['name']) for i in [1,18,25]],extra_candidate_exclusions=blocked,cash_profile_slots=0,season_direct_call_sites=calls,new_contribution='Connect existing seasonal formula to named customer products, primary-vs-extra initialization and conditional RNG call order; identify two event-product slots rejected unconditionally by normal extra selection; extract month weather/calendar data as a native port contract.',not_claimed='The seasonal formula was already present in earlier recovered models. Actual cash withdrawal behavior remains unresolved.'))
    print(json.dumps(dict(seasonal_products=seasonal,direct_calls=calls),ensure_ascii=False))
if __name__=='__main__':main()
