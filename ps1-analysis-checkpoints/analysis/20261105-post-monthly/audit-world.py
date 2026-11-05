#!/usr/bin/env python3
"""Audit naturally reached monthly map/population/history changes from raw RAM."""
import collections
import hashlib
import json
import struct
import sys
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parent
algo = Path(sys.argv[1]).resolve()
previous = ROOT.parent / '20261105-resumed-daily-close'
snapshots = previous / 'evidence/source/opened-snapshots-20261028'


def snapshot(name):
    meta = json.loads((snapshots / (name + '.json')).read_text())
    ram = zlib.decompress((snapshots / (name + '.ram.zlib')).read_bytes())
    assert len(ram) == 2097152 and hashlib.sha256(ram).hexdigest() == meta['ram_sha256']
    return meta, ram


opening, before = snapshot('TOWN0001-ci-main-12-single')
closing, after = snapshot('TOWN0001-ci-main-13-single')
town_start = 0x1398f0
old, new = before[town_start:town_start + 24000], after[town_start:town_start + 24000]
groups_before = before[0x9ff1c:0x9ff1c + 144 * 20]
assert groups_before == after[0x9ff1c:0x9ff1c + 144 * 20]
groups = [list(zip(*[iter(struct.unpack_from('<10h', groups_before, n * 20))] * 2)) for n in range(144)]


def population(town):
    result = 0
    for n in range(3000):
        group = struct.unpack_from('<h', town, n * 8 + 6)[0]
        if group != -1:
            assert 0 <= group < len(groups)
            result += sum(count for person, count in groups[group] if person != -1)
    return result


changes = []
counts = collections.Counter()
for n in range(3000):
    a, b = old[n * 8:n * 8 + 8], new[n * 8:n * 8 + 8]
    if a == b:
        continue
    fields = []
    for label, lo, hi in [('tile_id', 0, 2), ('level', 2, 3), ('attribute', 3, 4),
                          ('category', 4, 5), ('flags', 5, 6), ('population_group', 6, 8)]:
        if a[lo:hi] != b[lo:hi]:
            counts[label] += 1
            fields.append(label)
    changes.append(dict(x=n % 60, y=n // 60, before_hex=a.hex(), after_hex=b.hex(), fields=fields))
proof = json.loads((previous / 'evidence/opened-snapshot-TOWN0001-ci-main-13-single-verification-20261103.json').read_text())
assert proof['all_passed']
town_checks = proof['cases'][0]['whole_monthly_town_checks']
assert len(town_checks) == 200
old_hash, new_hash = hashlib.sha256(old).hexdigest(), hashlib.sha256(new).hexdigest()
assert all(c['town_sha256'] == old_hash and not c['actions'] for c in town_checks[:-1])
assert town_checks[-1]['town_sha256'] == new_hash
assert town_checks[-1]['calendar'] == [4, 1, 0, 0]
assert town_checks[-1]['actions'] == [['build', 13, 4, 45]]
assert population(old) == town_checks[-1]['population_before'] == 2179
assert population(new) == town_checks[-1]['population_after'] == 2183
history_before = struct.unpack_from('<60i', before, 0xe36a8)
history_after = struct.unpack_from('<60i', after, 0xe36a8)
assert list(history_after) == [population(new)] + list(history_before[:59])
tile_changes = [r for r in changes if 'tile_id' in r['fields']]
assert len(tile_changes) == 1 and (tile_changes[0]['x'], tile_changes[0]['y']) == (13, 4)
buildings = json.loads((algo / 'town-building-tables.json').read_text())['buildings']
building = buildings[45]
new_cell = bytes.fromhex(tile_changes[0]['after_hex'])
assert building['lower'] <= struct.unpack_from('<h', new_cell)[0] <= building['upper']
new_group = struct.unpack_from('<h', new_cell, 6)[0]
assert sum(n for p, n in groups[new_group] if p != -1) == 4
stores = []
for slot in range(10):
    p = 0x12b2f8 + 5080 * slot
    if not before[p]:
        continue
    a, b = struct.unpack_from('<H', before, p + 0x1184)[0], struct.unpack_from('<H', after, p + 0x1184)[0]
    stores.append(dict(slot=slot, owner=struct.unpack_from('<H', after, p + 4)[0] >> 15,
                       loss_streak_before=a, loss_streak_after=b,
                       previous_month_ledger=list(struct.unpack_from('<5i', after, p + 0xd4c))))
out = dict(all_passed=True, source_ram_sha256=opening['ram_sha256'], final_ram_sha256=closing['ram_sha256'],
           population_before=population(old), population_after=population(new),
           changed_cells=len(changes), changed_fields=dict(counts), changes=changes,
           new_building=dict(x=13, y=4, id=45, name=building['name'], population_group=new_group, added_population=4),
           population_history_shift_verified=True, stores=stores,
           scope='Raw RAM census and map delta, linked to the existing naturally reached whole monthly-town comparison. Not new natural updates or a rendered-screen test.')
(ROOT / 'world-audit.json').write_text(json.dumps(out, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({k: out[k] for k in ('all_passed', 'population_before', 'population_after', 'changed_cells', 'changed_fields')}, ensure_ascii=False))
