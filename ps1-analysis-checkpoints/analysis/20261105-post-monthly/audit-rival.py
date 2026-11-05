#!/usr/bin/env python3
"""Compare the naturally reached rival boundary with strict MIPS-I and its model."""
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
reference = runpy.run_path(str(ROOT.parent / '20261103-rival-monthly/rival-monthly-analysis.py'), run_name='rival_reference')
exe = (algo / 'source/SLPS_007.82').read_bytes()


def captured(label):
    meta = json.loads((ROOT / (label + '.json')).read_text())
    ram = zlib.decompress((ROOT / (label + '.ram.zlib')).read_bytes())
    assert len(ram) == 2097152 and hashlib.sha256(ram).hexdigest() == meta['ram_sha256']
    return ram


regions = [('stores', 0x12b2f8, 50800), ('staff', 0x143ff8, 2100),
           ('town', 0x1398f0, 24000), ('queue', 0x137970, 8000),
           ('demolition_mask', 0xcda50, 3000), ('cash', 0xcd9f8, 8),
           ('capital_own', 0xd8f68, 4), ('capital_rival', 0xd8f78, 4),
           ('rng', 0xd6270, 4), ('serial', 0xcd9e2, 2),
           ('dirty', 0x1398bc, 1), ('town_dirty', 0xcd8dc, 1),
           ('text', 0xe4020, 120)]
rows = []
with zipfile.ZipFile(archive) as z:
    for side in ('native', 'reference'):
        before, after = captured('rival-' + side + '-entry'), captured('rival-' + side + '-exit')
        cpu = reference['Cpu'](exe)
        cpu.mem[:] = before
        result = reference['compare_rival'](cpu, reference['tables'](cpu, z))
        # In the naturally reached branch no abstract text/cache endpoint may
        # execute. A future opening/withdrawal branch needs additional coverage.
        assert not result['hook_calls'], ('additional boundary requires coverage', result['reason'], result['hook_calls'])
        checks = []
        for name, address, size in regions:
            actual = bytes(cpu.mem[address:address + size])
            assert actual == after[address:address + size], (side, name, result['reason'])
            checks.append(dict(region=name, bytes=size, sha256=hashlib.sha256(actual).hexdigest()))
        losses = []
        for slot in range(10):
            p = 0x12b2f8 + slot * 5080
            if not before[p] or not struct.unpack_from('<H', before, p + 4)[0] & 0x8000:
                continue
            month = list(struct.unpack_from('<5i', before, p + 0xd4c))
            profit = (month[4] - sum(month[:4]) + 0x80000000) % 0x100000000 - 0x80000000
            old, new = struct.unpack_from('<H', before, p + 0x1184)[0], struct.unpack_from('<H', after, p + 0x1184)[0]
            assert new == ((old + 1) & 65535 if profit < 0 else 0)
            losses.append(dict(slot=slot, previous_month_ledger=month, profit=profit,
                               loss_streak_before=old, loss_streak_after=new))
        rows.append(dict(side=side, all_passed=True, comparison=result, region_checks=checks,
                         loss_streaks=losses, input_ram_sha256=hashlib.sha256(before).hexdigest(),
                         output_ram_sha256=hashlib.sha256(after).hexdigest(),
                         visited_instructions=[dict(pc=hex(a),word=hex(w)) for a,w in sorted(cpu.visited.items())]))
assert rows[0]['region_checks'] == rows[1]['region_checks']
assert rows[0]['loss_streaks'] == rows[1]['loss_streaks']
assert rows[0]['comparison']['reason'] == rows[1]['comparison']['reason']
out = dict(all_passed=True, source_executable_sha256=hashlib.sha256(exe).hexdigest(),
           natural_clock=17280, cases=rows, new_natural_updates_counted=0,
           limits=['Original function entry captured during an unchanged replay of the committed main-12→main-13 trajectory.',
                   'Strict MIPS-I interpreter and independent rival-management model versus reached Unicorn output.',
                   'Relevant regions are exact; whole RAM/register equality is not claimed across different caller stacks.',
                   'Text/cache hooks are configured but asserted unreachable in this natural branch; other branches remain outside this result.',
                   'Not a physical hardware, GPU/SPU/IRQ or BIOS equivalence test.'])
(ROOT / 'rival-audit.json').write_text(json.dumps(out, indent=2) + '\n')
print(json.dumps(dict(all_passed=True, reason=rows[0]['comparison']['reason'],
                      seed_before=rows[0]['comparison']['seed_before'], seed_after=rows[0]['comparison']['seed_after'],
                      loss_streaks=rows[0]['loss_streaks'])))
