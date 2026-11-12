#!/usr/bin/env python3
"""Reconcile reached monthly screen values, ledger profit and dequeued notices."""
import hashlib,json,struct,sys,zlib
from pathlib import Path
ROOT=Path(__file__).resolve().parent;algo=Path(sys.argv[1]).resolve()
def signed(v):return (v+0x80000000)%0x100000000-0x80000000
world=json.loads((ROOT/'natural-town-audit.json').read_text());assert world['all_passed'];rows=[]
proofs=[]
for p in sorted(ROOT.glob('TOWN0001-ci-main-*-single.audit.json')):
 name=json.loads(p.read_text())['output'];d=json.loads((algo/('opened-snapshot-'+name+'-verification-20261103.json')).read_text());assert d['all_passed'];proofs.append(d['cases'][0])
for worldcase in world['cases']:
 afterpath=ROOT/worldcase['input'].replace('-before.','-after.');ram=zlib.decompress(afterpath.read_bytes());assert hashlib.sha256(ram).hexdigest()==worldcase['captured_output_sha256']
 word=lambda a:struct.unpack_from('<I',ram,a)[0]
 expected=[signed(word(0xe3c28)),signed(word(0xe3c28)-word(0xe3c2c)),signed(word(0xda974)),signed(word(0xda974)-word(0xda978)),signed(word(0xe36a8)),signed(word(0xe36a8)-word(0xe36ac))]
 own_profit=0;ledgers=[]
 for slot in range(10):
  p=0x12b2f8+slot*5080
  if ram[p] and not struct.unpack_from('<H',ram,p+4)[0]&0x8000:
   ledger=list(struct.unpack_from('<5i',ram,p+0xd4c));profit=signed(ledger[4]-sum(ledger[:4]));own_profit=signed(own_profit+profit);ledgers.append(dict(slot=slot,ledger=ledger,profit=profit))
 assert expected[0]==own_profit and expected[4]==worldcase['population_after']
 screens=[s for r in proofs for s in r['monthly_screen_checks'] if s['clock']>=worldcase['clock']]
 assert screens,'Monthly result screen has not been reached in completed evidence'
 for s in screens:
  assert s['values']==expected
  nums=[q for q in s['requests'] if q['address']==0x8004e494]
  digits=[((-v if i in (0,1,3,5) and v<0 else v)&0xffffffff) for i,v in enumerate(expected)]
  assert [q['value'] for q in nums]==digits
  sign_text=[q['args'][2] for q in s['requests'] if q['address']==0x80067338]
  assert sign_text.count(0x800b956c)==sum(expected[i]<0 for i in (0,1,3,5))
  assert sign_text.count(0x800b9570)==sum(expected[i]>0 for i in (0,1,3,5))
  assert [q['slot'] for q in nums]==[0x800e4000]*4+[0x800cd938]*2
 queued=[]
 for slot in range(50):
  p=0x137970+slot*160
  if ram[p]==1:
   kind,param,sound=struct.unpack_from('<3i',ram,p+132);queued.append(dict(slot=slot,kind=kind,param=param,sound=sound,mode=ram[p+2]))
 dequeues=[c for r in proofs for c in r['event_consumer_checks'] if c['slot'] is not None and c['clock']>=worldcase['clock']]
 assert any(d['mode']==2 for d in dequeues),'No monthly result notice consumed'
 rows.append(dict(clock=worldcase['clock'],source_ram_sha256=worldcase['captured_output_sha256'],monthly_values=expected,rendered_digit_values=digits,negative_sign_labels_per_screen=sum(expected[i]<0 for i in (0,1,3,5)),own_previous_month_ledgers=ledgers,own_profit=own_profit,queued_requests=queued,dequeues=dequeues,monthly_screen_calls=len(screens),first_screen_clock=screens[0]['clock'],last_screen_clock=screens[-1]['clock']))
assert rows
(ROOT/'monthly-notices-audit.json').write_text(json.dumps(dict(all_passed=True,cases=rows,limits=['Original logical draw/number requests and consumer/model checks, not GPU rasterization or physical audio.', 'Screen call count and clock span are not real elapsed seconds.', 'This source trajectory only; no new natural updates counted by the audit.']),indent=2)+'\n')
print(json.dumps([dict(values=r['monthly_values'],screen_calls=r['monthly_screen_calls'],first_clock=r['first_screen_clock'],last_clock=r['last_screen_clock']) for r in rows]))
