#!/usr/bin/env python3
"""Link original finance -> rival -> town -> demand at a natural month boundary."""
import hashlib,json,struct,sys,zlib
from pathlib import Path
ROOT=Path(__file__).resolve().parent;algo=Path(sys.argv[1]).resolve()
exe=(algo/'source/SLPS_007.82').read_bytes()
def sha(b):return hashlib.sha256(b).hexdigest()
def unpack_ram(rel):return zlib.decompress((ROOT/rel).read_bytes())
def callword(pc,target):
 w=struct.unpack_from('<I',exe,pc-0x80010000+2048)[0]
 assert w>>26==3 and (((pc+4)&0xf0000000)|((w&0x3ffffff)<<2))==target
 return dict(pc=hex(pc),word=hex(w),target=hex(target))
words=[callword(*x) for x in ((0x800234a0,0x80029334),(0x800234a8,0x8002a8e0),(0x800234b0,0x8002bd54),(0x800234e0,0x8002619c))]
rows=[]
for auditpath in sorted(ROOT.glob('TOWN0001-ci-main-*-single.audit.json')):
 segment=json.loads(auditpath.read_text());name=segment['output']
 proofpath=algo/('opened-snapshot-'+name+'-verification-20261103.json')
 if not proofpath.exists():continue
 proof=json.loads(proofpath.read_text());assert proof['all_passed'];r=proof['cases'][0]
 for rv in r['natural_rival_boundaries']:
  clock=rv['clock'];tw=next(x for x in r['natural_town_boundaries'] if x['clock']==clock)
  fin=next(x for x in r['midnight_finance_checks'] if x['clock']==clock)
  assert fin['calendar'][2:]==[1,0,0]
  rb,ra,tb=unpack_ram(rv['before_path']),unpack_ram(rv['after_path']),unpack_ram(tw['before_path'])
  assert sha(rb)==rv['before_sha256'] and sha(ra)==rv['after_sha256'] and sha(tb)==tw['before_sha256']
  assert list(struct.unpack_from('<2I',rb,0xcd9f8))==fin['cash_after']
  assert sha(rb[0x12b2f8:0x12b2f8+50800])==fin['stores_sha256']
  assert sha(rb[0x143ff8:0x143ff8+2100])==fin['staff_sha256']
  assert sha(rb[0xe4020:0xe4020+120])==fin['notification_text_sha256']
  assert ra[:0x1c0000]==tb[:0x1c0000]
  lifecycle=r['lifecycle_checks'];assert lifecycle[0]==lifecycle[1]
  demand=[x for x in lifecycle[0] if x[0]==0x8002619c];assert len(demand)==1
  rows.append(dict(clock=clock,segment=name,source_call_words=words,finance_cash_after=fin['cash_after'],finance_stores_sha256=fin['stores_sha256'],finance_staff_sha256=fin['staff_sha256'],rival_input_sha256=rv['before_sha256'],rival_output_sha256=rv['after_sha256'],town_input_sha256=tw['before_sha256'],rival_to_town_equal_ram_bytes=0x1c0000,demand_check=demand[0]))
assert rows,'No completed natural monthly handoff found'
(ROOT/'monthly-handoff-audit.json').write_text(json.dumps(dict(all_passed=True,source_executable_sha256=sha(exe),cases=rows,limits=['Natural boundary captures and original source call order; distinct parent/callee stacks are excluded.', 'Finance and demand result checks use existing independent models; no new natural updates counted by this audit.']),indent=2)+'\n')
print(json.dumps([dict(clock=r['clock'],finance_cash_after=r['finance_cash_after'],rival_to_town_equal_ram_bytes=r['rival_to_town_equal_ram_bytes']) for r in rows]))
