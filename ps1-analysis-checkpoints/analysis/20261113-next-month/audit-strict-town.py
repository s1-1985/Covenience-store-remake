#!/usr/bin/env python3
"""Execute captured natural town input with the strict MIPS-I interpreter."""
import hashlib,importlib.util,json,sys,zlib
from pathlib import Path
ROOT=Path(__file__).resolve().parent;algo=Path(sys.argv[1]).resolve();sys.path.insert(0,str(algo))
spec=importlib.util.spec_from_file_location('strict_engine',ROOT.parent/'20261103-rival-monthly/rival-monthly-analysis.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
exe=(algo/'source/SLPS_007.82').read_bytes();model=json.loads((ROOT/'natural-town-audit.json').read_text());assert model['all_passed']
rows=[]
for r in model['cases']:
 before=zlib.decompress((ROOT/r['input']).read_bytes());after=zlib.decompress((ROOT/r['input'].replace('-before.','-after.')).read_bytes())
 assert hashlib.sha256(before).hexdigest()==r['input_ram_sha256'] and hashlib.sha256(after).hexdigest()==r['captured_output_sha256']
 cpu=m.Cpu(exe);cpu.mem[:]=before
 cpu.run(0x8002bd54,limit=30000000,stack_pointer=0x801d0000,global_pointer=0x800cd6c4)
 assert not cpu.calls and not cpu.hooks
 assert cpu.read(0x801398f0,24000)==after[0x1398f0:0x1398f0+24000]
 assert bytes(cpu.mem[:0x1c0000])==after[:0x1c0000],'Non-stack prefix mismatch'
 packed=zlib.compress(bytes(cpu.mem),9);target=ROOT/('strict-town-'+str(r['clock'])+'-diagnostic.ram.zlib');target.write_bytes(packed)
 rows.append(dict(clock=r['clock'],input_ram_sha256=r['input_ram_sha256'],captured_native_output_sha256=r['captured_output_sha256'],strict_output_sha256=hashlib.sha256(cpu.mem).hexdigest(),output_path=target.name,instructions=cpu.steps,visited_instructions=[dict(pc=hex(a),word=hex(w)) for a,w in sorted(cpu.visited.items())],external_hook_calls=cpu.calls,matched_non_stack_ram_bytes=0x1c0000,town_sha256=r['town_sha256'],population_before=r['population_before'],population_after=r['population_after'],actions=r['actions'],events=r['events']))
assert rows
(ROOT/'strict-town-audit.json').write_text(json.dumps(dict(all_passed=True,cases=rows,source_executable_sha256=hashlib.sha256(exe).hexdigest(),limits=['Natural function-entry data; separate diagnostic invocation, no new natural updates counted.', 'Strict MIPS-I original instructions and children, no external hooks in these captured branches.', 'RAM below 0x1c0000 compared in full; distinct caller/interpreter stacks are excluded.', 'Diagnostic CPU output is not the normal-play resume point; GPU pixels/physical timing/audio are outside this check.']),indent=2)+'\n')
print(json.dumps([dict(clock=r['clock'],instructions=r['instructions'],matched_non_stack_ram_bytes=r['matched_non_stack_ram_bytes'],actions=r['actions']) for r in rows]))
