#!/usr/bin/env python3
"""Execute the captured rival manager including original text/cache children."""
import hashlib,importlib.util,json,sys,zlib
from pathlib import Path
ROOT=Path(__file__).resolve().parent;algo=Path(sys.argv[1]).resolve();sys.path.insert(0,str(algo))
spec=importlib.util.spec_from_file_location('strict_full_rival',ROOT.parent/'20261103-rival-monthly/rival-monthly-analysis.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
exe=(algo/'source/SLPS_007.82').read_bytes();policy=json.loads((ROOT/'natural-rival-audit.json').read_text());assert policy['all_passed'];rows=[]
for r in policy['cases']:
 p=ROOT/r['input'];before=zlib.decompress(p.read_bytes());after=zlib.decompress(p.with_name(p.name.replace('-before.','-after.')).read_bytes());assert hashlib.sha256(before).hexdigest()==r['input_sha256']
 from importlib.machinery import SourceFileLoader
 unaligned=SourceFileLoader('strict_unaligned',str(ROOT/'strict-unaligned.py')).load_module()
 cpu=unaligned.extend(m.Cpu)(exe);cpu.mem[:]=before;cpu.run(0x8002a8e0,limit=30000000,stack_pointer=0x801d0000,global_pointer=0x800cd6c4)
 assert not cpu.hooks and not cpu.calls
 if bytes(cpu.mem[:0x1c0000])!=after[:0x1c0000]:
  from itertools import islice
  raise AssertionError(('Full rival non-stack RAM mismatch',list(islice(((hex(i),a,b) for i,(a,b) in enumerate(zip(cpu.mem[:0x1c0000],after[:0x1c0000])) if a!=b),20))))
 out=ROOT/('strict-rival-'+str(r['clock'])+'-diagnostic.ram.zlib');out.write_bytes(zlib.compress(bytes(cpu.mem),9))
 rows.append(dict(clock=r['clock'],reason=r['reason'],instructions=cpu.steps,input_ram_sha256=r['input_sha256'],native_output_sha256=hashlib.sha256(after).hexdigest(),strict_output_sha256=hashlib.sha256(cpu.mem).hexdigest(),output_path=out.name,matched_non_stack_ram_bytes=0x1c0000,external_hook_calls=cpu.calls,visited_instructions=[dict(pc=hex(a),word=hex(w)) for a,w in sorted(cpu.visited.items())]))
assert rows
(ROOT/'strict-rival-full-audit.json').write_text(json.dumps(dict(all_passed=True,cases=rows,source_executable_sha256=hashlib.sha256(exe).hexdigest(),limits=['Natural rival-entry input; separate diagnostic invocation, no natural updates added.', 'Original text assembly and cache refresh children execute with no external hooks in this captured branch.', 'RAM below 0x1c0000 compared in full; different caller/interpreter stacks excluded.', 'Two original-code engines do not replace the separate independent rival-policy model comparison.']),indent=2)+'\n');print(json.dumps([dict(clock=r['clock'],reason=r['reason'],instructions=r['instructions'],matched_bytes=r['matched_non_stack_ram_bytes']) for r in rows]))
