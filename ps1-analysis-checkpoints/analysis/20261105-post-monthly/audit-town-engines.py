#!/usr/bin/env python3
"""Execute natural post-rival town input in strict MIPS-I, without SDK hooks."""
import hashlib
import json
import runpy
import struct
import sys
import zipfile
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parent
algo = Path(sys.argv[1]).resolve()
archive = Path(sys.argv[2]).resolve()
sys.path.insert(0, str(algo))
from town_monthly import monthly, population
from town_mutation import descriptors
from source_town_monthly_monitor_20261102 import FIELDS, BYTE

reference = runpy.run_path(str(ROOT.parent / '20261103-rival-monthly/rival-monthly-analysis.py'), run_name='town_integer_engine')
exe = (algo / 'source/SLPS_007.82').read_bytes()
before = zlib.decompress((ROOT / 'rival-native-exit.ram.zlib').read_bytes())
meta = json.loads((ROOT / 'rival-native-exit.json').read_text())
assert len(before) == 2097152 and hashlib.sha256(before).hexdigest() == meta['ram_sha256']
read = lambda address, size: before[address & 0x1fffffff:(address & 0x1fffffff) + size]
word = lambda address: struct.unpack('<I', read(address, 4))[0]
state = {k:read(a, 1)[0] if k in BYTE else word(a) for k,a in FIELDS.items()}
state['history'] = list(struct.unpack('<60I', read(0x800e36a8, 240)))
assert (state['month'],state['stage'],state['hour'],state['subhour']) == (4,1,0,0)
groups = [list(zip(*[iter(struct.unpack('<10h', read(0x8009ff1c + n * 20, 20)))] * 2)) for n in range(144)]
table = descriptors(json.loads((algo / 'town-building-tables.json').read_text())['buildings'])
stores = []
for n in range(10):
    s = read(0x8012b2f8 + n * 5080, 5080)
    stores.append(dict(active=s[0],rect=list(struct.unpack_from('<4i',s,8)),
                       value=struct.unpack_from('<i',s,0xd5c)[0],c74=s[0xc74],c75=s[0xc75],c76=s[0xc76]))
order = []
for n in struct.unpack('<10i', read(0x800ce61c,40)):
    if n == -1:
        break
    order.append(n)
town = bytearray(read(0x801398f0,24000))
expected, events, actions = monthly(town,table,groups,stores,order,state)
assert events == [] and actions == [('build',13,4,45)]
cpu = reference['Cpu'](exe)
cpu.mem[:] = before
cpu.run(0x8002bd54, limit=30000000, stack_pointer=0x801d0000, global_pointer=0x800cd6c4)
assert not cpu.calls and not cpu.hooks
assert cpu.read(0x801398f0,24000) == town
for key,address in FIELDS.items():
    actual = cpu.read(address,1)[0] if key in BYTE else struct.unpack('<I',cpu.read(address,4))[0]
    assert actual == expected[key], (key,actual,expected[key])
assert list(struct.unpack('<60I',cpu.read(0x800e36a8,240))) == expected['history']
for address,size in ((0x8012b2f8,50800),(0x80143ff8,2100),(0x80137970,8000),(0x800e4020,120)):
    assert cpu.read(address,size) == read(address,size)
native = json.loads((ROOT / 'monthly-replay.json').read_text())['play']['whole_monthly_town_checks'][-1]
assert native['seed_before'] == state['seed'] and native['seed_after'] == expected['seed']
assert native['town_sha256'] == hashlib.sha256(town).hexdigest()
assert native['queue_sha256'] == hashlib.sha256(cpu.read(0x80137970,8000)).hexdigest()
assert native['population_before'] == population(read(0x801398f0,24000),0,groups)
assert native['population_after'] == population(town,0,groups)
assert native['actions'] == [list(x) for x in actions]
assert native['tier_after'] == expected['tier'] and native['pending_after'] == expected['progress_counter'] and native['flags_after'] == expected['progress_flags']
packed = zlib.compress(bytes(cpu.mem),9)
(ROOT / 'strict-town-output.ram.zlib').write_bytes(packed)
out = dict(all_passed=True, input_kind='Natural rival return data, immediately before the original caller invokes town monthly processing.',
           input_ram_sha256=meta['ram_sha256'], source_executable_sha256=hashlib.sha256(exe).hexdigest(),
           output_ram_sha256=hashlib.sha256(cpu.mem).hexdigest(), instructions=cpu.steps,
           visited_instructions=[dict(pc=hex(a),word=hex(w)) for a,w in sorted(cpu.visited.items())],
           external_hook_calls=cpu.calls, town_sha256=hashlib.sha256(town).hexdigest(),
           seed_before=state['seed'], seed_after=expected['seed'], actions=[list(x) for x in actions],
           population_before=native['population_before'], population_after=native['population_after'],
           matched_original_unicorn_return=native, model_state=expected,
           new_natural_updates_counted=0,
           limits=['Function input data is captured at preceding rival return; this is a separate diagnostic invocation, not a continuous hardware CPU run.',
                   'Strict interpreter executes original town and child instructions with no external function hooks in this branch.',
                   'Town bytes, globals, history and unchanged stores/staff/queue/text are verified; whole caller-stack RAM and registers are not compared.',
                   'Diagnostic output RAM is not a normal-play restart; main-15 remains the natural trajectory.'])
(ROOT / 'town-engine-audit.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(dict(all_passed=True,instructions=cpu.steps,population_after=out['population_after'],actions=out['actions'])))
