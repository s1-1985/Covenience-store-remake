#!/usr/bin/env python3
"""Replay captured natural monthly rival entry with strict MIPS-I and independent policy.
No clock, RNG, store, roster, or cash injection. Text/cache boundaries retain the
previous diagnostic policy; compare these separately from gameplay domains.
"""
import hashlib, importlib.util, json, struct, sys, zlib
from pathlib import Path
ROOT=Path(__file__).resolve().parent
algo=Path(sys.argv[1]).resolve()
sys.path.insert(0,str(algo))
spec=importlib.util.spec_from_file_location('strict_rival',ROOT.parent/'20261103-rival-monthly/rival-monthly-analysis.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
class Files:
 def read(self,name):return (algo/Path(name).relative_to('algorithm-analysis')).read_bytes()
exe=(algo/'source/SLPS_007.82').read_bytes()
rows=[]
for p in sorted((ROOT/'rival-boundaries').glob('*-before.ram.zlib')):
 before=zlib.decompress(p.read_bytes());after=zlib.decompress(p.with_name(p.name.replace('-before.','-after.')).read_bytes())
 cpu=m.Cpu(exe);cpu.mem[:]=before
 result=m.compare_rival(cpu,m.tables(cpu,Files()))
 regions=[]
 for name,a,n in [('stores',0x12b2f8,50800),('staff',0x143ff8,2100),('town',0x1398f0,24000),('demolition',0xcda50,3000),('cash',0xcd9f8,8),('capital',0xd8f68,32),('rng',0xd6270,4),('serial',0xcd9e2,2),('dirty',0x1398bc,1),('town_dirty',0xcd8dc,1)]:
  got=bytes(cpu.mem[a:a+n]);expected=after[a:a+n]
  assert got==expected,(name,[(i,x,y) for i,(x,y) in enumerate(zip(got,expected)) if x!=y][:8])
  regions.append(dict(name=name,bytes=n,sha256=hashlib.sha256(got).hexdigest()))
 # No notification means there is no text generation discrepancy to exclude.
 for name,a,n in [('queue',0x137970,8000),('text',0xe4020,120),('text_position',0xcd8c8,4)]:
  same=bytes(cpu.mem[a:a+n])==after[a:a+n]
  if not result['events']:assert same,name
  regions.append(dict(name=name,bytes=n,equal=same))
 prefix_equal=bytes(cpu.mem[:0x1c0000])==after[:0x1c0000]
 if not result['events']:assert prefix_equal,'Non-stack RAM mismatch without notification/cache refresh'
 result.update(non_stack_ram_prefix_bytes=0x1c0000,non_stack_ram_prefix_equal=prefix_equal,input=str(p.relative_to(ROOT)),clock=struct.unpack_from('<I',before,0xcd93c)[0],natural_domains=regions,
               input_sha256=hashlib.sha256(before).hexdigest(),captured_output_sha256=hashlib.sha256(after).hexdigest(),
               source_instructions={hex(k):hex(v) for k,v in sorted(cpu.visited.items())},changes=m.additions(before,cpu))
 rows.append(result)
assert rows,'No natural rival boundary captured'
(ROOT/'natural-rival-audit.json').write_text(json.dumps(dict(all_passed=True,cases=rows,source_executable_sha256=hashlib.sha256(exe).hexdigest(),limits=['Strict integer interpreter and independent rival policy; text generation and cache rebuild external.', 'No notification requires equality of queue/text as well; notifications would be reported separately.']),indent=2)+'\n')
print(json.dumps([dict(reason=r['reason'],clock=r['clock'],steps=r['steps'],events=r['events']) for r in rows]))
