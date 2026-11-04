#!/usr/bin/env python3
"""Continue 120 native updates, audit cash independently, preserve new evidence.

Arguments: extracted algorithm-analysis directory, prior operating-continuation
directory. Requires the unchanged r2 archive and its checked-in later snapshots.
An existing final proof is audited and captured; delete scratch output to replay.
"""
import collections
import hashlib
import json
import shutil
import struct
import subprocess
import sys
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parent
algo, prior = (Path(p).resolve() for p in sys.argv[1:3])
source = 'TOWN0001-ci-main-04-single'
name = 'TOWN0001-ci-main-05-single'
count = 120
snapshots = algo / 'source/opened-snapshots-20261028'
for old in sorted((prior / 'runs').glob('*/generated/source/opened-snapshots-20261028/*')):
    target = snapshots / old.name
    if target.exists():
        assert target.read_bytes() == old.read_bytes(), old.name
    else:
        shutil.copy2(old, target)

def sha(data):
    return hashlib.sha256(data).hexdigest()

def load_snapshot(snapshot):
    meta = json.loads((snapshots / (snapshot + '.json')).read_text())
    ram = zlib.decompress((snapshots / (snapshot + '.ram.zlib')).read_bytes())
    assert len(ram) == 2097152 and sha(ram) == meta['ram_sha256']
    return meta, ram

proof_path = algo / ('opened-snapshot-' + name + '-verification-20261103.json')
log_path = ROOT / 'operating.log'
if not proof_path.exists():
    with log_path.open('w') as log:
        subprocess.run([sys.executable, 'verify_operating_branch_segment_20261103.py',
                        source, str(count), name], cwd=algo, stdout=log,
                       stderr=subprocess.STDOUT, check=True, timeout=1200)
proof = json.loads(proof_path.read_text())
assert proof['all_passed'] and proof['iterations_verified'] == count
row = proof['cases'][0]
assert row['snapshot'] == source and len(row['steps']) == count
before_meta, before = load_snapshot(source)
after_meta, after = load_snapshot(name)
assert row['snapshot_sha256'] == before_meta['ram_sha256'] == after_meta['parent_snapshot_sha256']
assert after_meta['completed_iterations'] == before_meta['completed_iterations'] + count
assert row['opening_clock'] == 14400 and row['steps'][-1]['clock'] == 14640
assert row['runtime_table_provenance'] == 'single_conversion'
assert row['single_conversion_appearance_verified']
assert not row['midnight_finance_checks'], 'No new daily close expected in this interval'
cash_before = list(struct.unpack_from('<2i', before, 0xcd9f8))
cash = cash_before[:]
writes = collections.Counter()
write_deltas = collections.defaultdict(lambda: [0, 0])
for event in row['accounting_write_trace']:
    addr = int(event['address'], 16)
    if addr not in (0xcd9f8, 0xcd9fc):
        continue
    side = (addr - 0xcd9f8) // 4
    signed = lambda value: (value + 0x80000000) % 0x100000000 - 0x80000000
    assert event['size'] == 4 and signed(event['before']) == cash[side]
    cash[side] = signed(event['after'])
    writes[event['pc']] += 1
    write_deltas[event['pc']][side] += signed(event['after'] - event['before'])
cash_after = list(struct.unpack_from('<2i', after, 0xcd9f8))
assert cash == cash_after
ledger_cash = cash_before[:]
stores = []
for slot in range(10):
    off = 0x12b2f8 + slot * 5080
    assert before[off] == after[off] and before[off + 4:off + 6] == after[off + 4:off + 6]
    if not before[off]:
        continue
    side = struct.unpack_from('<H', before, off + 4)[0] >> 15
    a = list(struct.unpack_from('<5i', before, off + 0xd88))
    b = list(struct.unpack_from('<5i', after, off + 0xd88))
    # No daily rollover: prior-day history must not be shifted/debited again.
    assert before[off + 0xd9c:off + 0xdd8] == after[off + 0xd9c:off + 0xdd8]
    assert a[:3] == b[:3] == [0, 0, 0]
    sales, goods = b[4] - a[4], b[3] - a[3]
    ledger_cash[side] += sales - goods
    stores.append(dict(slot=slot, company=side, opening_ledger=a, closing_ledger=b,
                       additional_sales=sales, additional_goods=goods,
                       daily_cost_reposted=False, prior_day_history_preserved=True))
assert ledger_cash == cash_after
assert len(row['whole_staff_loop_checks']) == len(stores) * count
assert len(row['customer_loop_checks']) == len(stores) * count
effects = collections.Counter()
for check in row['whole_staff_loop_checks']:
    effects.update(check['effects'])
roundtrip_path = algo / ('title-native-load-roundtrip-' + name + '-verification-20261030.json')
if not roundtrip_path.exists():
    with (ROOT / 'roundtrip.log').open('w') as log:
        subprocess.run([sys.executable, 'verify_single_roundtrip_20261030.py', name],
                       cwd=algo, stdout=log, stderr=subprocess.STDOUT, check=True, timeout=600)
roundtrip = json.loads(roundtrip_path.read_text())
assert roundtrip['all_passed']
loaded = roundtrip['cases'][0]
assert loaded['payload_valid'] and loaded['runtime_table_provenance'] == 'single_conversion'
assert loaded['runtime_tables_preserved_after_resume']['both_cpus']
assert loaded['resumed_play']['opening_clock'] == 14640
assert loaded['resumed_play']['opening_cash'] == cash_after[0]
captured = []
for path in [proof_path, algo / (name + '-progress.json'), roundtrip_path,
             snapshots / (name + '.json'), snapshots / (name + '.ram.zlib')]:
    dest = ROOT / 'evidence' / path.relative_to(algo)
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(path, dest)
    captured.append(dict(path=str(dest.relative_to(ROOT)), bytes=dest.stat().st_size,
                         sha256=sha(dest.read_bytes())))
import unicorn, capstone, PIL
result = dict(all_passed=True, source=source, output=name, updates=count,
              source_ram_sha256=before_meta['ram_sha256'], final_ram_sha256=after_meta['ram_sha256'],
              completed_iterations=after_meta['completed_iterations'], clock_before=14400, clock_after=14640,
              cash_before=cash_before, cash_after=cash_after, cash_from_ledgers=ledger_cash,
              cash_write_count=dict(writes), cash_delta_by_pc=dict(write_deltas), stores=stores,
              daily_close_count=0, staff_checks=len(row['whole_staff_loop_checks']),
              customer_checks=len(row['customer_loop_checks']), staff_effects=dict(effects),
              restock_checks=len(row['restock_checks']), stock_postings=len(row['stock_posting_checks']),
              frames_verified=proof['frames_verified'],
              roundtrip=dict(all_passed=True, payload_sha256=loaded['payload_sha256'],
                             resumed_clocks=[step['clock'] for step in loaded['resumed_play']['steps']],
                             runtime_tables=loaded['runtime_tables_preserved_after_resume']),
              runtime=dict(python=sys.version, unicorn=unicorn.__version__,
                           capstone=capstone.__version__, pillow=PIL.__version__), files=captured,
              limits=['120 new natural updates; threshold probes and load-resume steps counted separately.',
                      'No clock, cash, roster or RNG edits in this natural continuation.',
                      'Native and independent parent/control models share original child routines and Unicorn.',
                      'Title load uses the previously documented card-completion adapter; not physical card I/O.',
                      'Past physical VRAM/SPU/IRQ state is not restored.'])
(ROOT / 'continuation-audit.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({k: result[k] for k in ('all_passed', 'updates', 'clock_after', 'cash_after', 'staff_checks')}))
