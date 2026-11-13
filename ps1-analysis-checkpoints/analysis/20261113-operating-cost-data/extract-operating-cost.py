#!/usr/bin/env python3
"""Read all source opening schedules and name all53 fixture hourly rates.
Static disc parsing and instruction decoding only, no original CPU execution.
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
    schedules=[]
    for i in range(7):
        a=0x80099dd0+i*45;b=at(a,45);flags=list(b[21:45]);assert all(v in (0,1) for v in flags)
        schedules.append(dict(id=i,address=hex(a),name=b[:21].split(b'\0')[0].decode('shift_jis'),hour_flags=flags,open_hours=[h for h,v in enumerate(flags) if v],hours_per_day=sum(v!=0 for v in flags),temporary_closed=i==6))
    assert [s['hours_per_day'] for s in schedules]==[24,8,16,16,16,16,0]
    label_path=ROOT.parent/'20261113-product-stock-data/fixture-labels.json';labels={r['id']:r['name'] for r in json.loads(label_path.read_text())['labels']}
    fixtures=[]
    for i in range(53):
        a=0x80099f0c+i*196;flags,price,rate=struct.unpack('<3i',at(a,12))
        fixtures.append(dict(id=i,address=hex(a),name=labels[i],category=flags&255,raw_purchase_price=price,hourly_operating_rate=rate,cost_per_schedule=[rate*s['hours_per_day'] for s in schedules],cost_fixed24_mode=rate*24))
    assert fixtures[50]['hourly_operating_rate']==0 and fixtures[52]['hourly_operating_rate']==200
    js('schedule-fixture-costs.json',dict(schema_version=1,source_disc_sha256=DISC_SHA,source_exe_sha256=EXE_SHA,schedule_schema={'base':'0x80099dd0','count':7,'stride':45,'name':'Shift-JIS[21]','flags':'u8[24] at+21'},fixture_rate_schema={'base':'0x80099f0c','count':53,'stride':196,'hourly_rate_offset':8},label_dependency='../20261113-product-stock-data/fixture-labels.json',schedules=schedules,fixtures=fixtures,unit_note='Values are source internal monetary amounts. No additional x1000 conversion or purchase-price display unit is inferred by this extractor.'))
    js('android-operating-cost-bridge.json',dict(schema_version=1,source_exe_sha256=EXE_SHA,mode_rule='mode0 uses count of nonzero flags of current schedule; any nonzero mode uses24 hours.',schedule6='Temporary closure is a real seventh data row with zero hourly flags; normal operation-menu code can assign index6.',equipment='Sum rate*hours for each grid anchor(bit31 set) whose fixture id=(word>>12)&1023 is<53. Count once per anchor; do not multiply by footprint or remaining stock.',staff='For each assigned ref!=-1: read signed i32 wage base at staff+12. Slot0 applies trunc_toward_zero(wage*130/100) before multiplying by hours; slots1/2 use wage as-is.',staff_scope='No actual-worktime, task, rest or energy filter in these cost helpers.',daily_debit='At native296F0..297A4 write equipment cost to store+D88 and staff cost to+D8C, then debit these plus existing+D90 from owning side cash. This report does not assign a new label or recalculation formula to+D90.',side='(u16(store+4)>>15)&1 chooses cash side.',arithmetic='Source uses signed32 operations and truncation toward zero; examples here use normal nonnegative amounts.',currency='Preserve source amounts; purchase display units and other monetary conversions are outside this report.'))
    js('derived-cost-examples.json',dict(scope='Source-table arithmetic, not a gameplay or billing trace.',fixture7=dict(name=fixtures[7]['name'],rate=30,schedule1_hours=8,daily_schedule1=240,daily_schedule0=720),manager_rounding=dict(wage_base=99,hours=8,manager_hourly=128,manager_daily=1024,ordinary_daily=792,formula='trunc(99*130/100)*8; not trunc(99*130*8/100)'),temporary_closed=dict(schedule=6,hours=0,equipment=0,staff=0,other_costs='Existing+D90 is still part of the separate daily debit.')))
    (ROOT/'source').mkdir(exist_ok=True);ranges=[];asm=[];md=Cs(CS_ARCH_MIPS,CS_MODE_MIPS32|CS_MODE_LITTLE_ENDIAN)
    spans=[('opening_schedules',0x80099dd0,315,False),('fixture_master',0x80099f0c,53*196,False),('operating_cost_helpers',0x8001d8ac,0x8001de5c-0x8001d8ac,True),('daily_expense_debit',0x800296f0,0x800297a4-0x800296f0,True)]
    for name,a,n,is_code in spans:
        b=at(a,n);(ROOT/'source'/f'{name}.bin').write_bytes(b);ranges.append(dict(name=name,address=hex(a),bytes=n,sha256=sha(b)))
        if is_code:
            asm.append(f'\n# {name} {a:#x} bytes={n}');asm.extend(f'{x.address:08x}: {x.bytes.hex()} {x.mnemonic} {x.op_str}' for x in md.disasm(b,a))
    (ROOT/'cost-readers.asm').write_text('\n'.join(asm)+'\n');js('source-ranges.json',ranges)
    js('summary.json',dict(schedules=7,normal_schedules=6,temporary_closed=6,fixtures=53,new_work='Identify complete45-byte opening schedule rows including Shift-JIS labels and temporary closure; map named fixture hourly-rate field+8 and schedule-specific daily values; preserve manager rounding order.',existing_work='Isolated operating-cost helper formulas were reconstructed earlier.',original_cpu_updates=0))
    print(json.dumps(dict(schedules=[dict(id=s['id'],name=s['name'],hours=s['hours_per_day']) for s in schedules],fixtures=53),ensure_ascii=False))
if __name__=='__main__':main()
