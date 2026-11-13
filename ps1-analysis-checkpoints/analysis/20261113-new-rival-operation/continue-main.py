#!/usr/bin/env python3
"""Continue main-31 through a newly created rival store's first daily close.

Arguments: unchanged extracted algorithm-analysis directory. Its source folder
must include the preceding committed main-31 snapshot. Every segment is saved
immediately so an interruption retains a complete restart and cash proof.
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
algo = Path(sys.argv[1]).resolve()
snapshots = algo / 'source/opened-snapshots-20261028'
rows = []


def sha(data):
    return hashlib.sha256(data).hexdigest()


def snapshot(name):
    meta = json.loads((snapshots / (name + '.json')).read_text())
    ram = zlib.decompress((snapshots / (name + '.ram.zlib')).read_bytes())
    assert len(ram) == 2097152 and sha(ram) == meta['ram_sha256']
    return meta, ram


def signed(value):
    return (value + 0x80000000) % 0x100000000 - 0x80000000


for index in range(32, 35):
    source = f'TOWN0001-ci-main-{index - 1:02d}-single'
    output = f'TOWN0001-ci-main-{index:02d}-single'
    count = 200
    proof_path = algo / ('opened-snapshot-' + output + '-verification-20261103.json')
    if not proof_path.exists():
        with (ROOT / (output + '.log')).open('w') as log:
            subprocess.run([sys.executable, str(ROOT / 'verify-segment.py'), str(algo),
                            source, str(count), output], cwd=algo, stdout=log,
                           stderr=subprocess.STDOUT, check=True, timeout=1200)
    proof = json.loads(proof_path.read_text())
    assert proof['all_passed'] and proof['iterations_verified'] == count
    row = proof['cases'][0]
    opening_meta, before = snapshot(source)
    final_meta, after = snapshot(output)
    assert row['snapshot'] == source and len(row['steps']) == count
    assert row['snapshot_sha256'] == opening_meta['ram_sha256'] == final_meta['parent_snapshot_sha256']
    assert final_meta['completed_iterations'] == opening_meta['completed_iterations'] + count
    clock = struct.unpack_from('<I', before, 0xcd93c)[0]
    assert row['opening_clock'] == clock and row['steps'][-1]['clock'] == clock + 2 * count
    assert row['runtime_table_provenance'] == 'single_conversion' and row['single_conversion_appearance_verified']
    closes = row['midnight_finance_checks']
    assert len(closes) <= 1
    cash = list(struct.unpack_from('<2i', before, 0xcd9f8))
    cash_before = cash[:]
    deltas = collections.defaultdict(lambda: [0, 0])
    write_count = 0
    for event in row['accounting_write_trace']:
        address = int(event['address'], 16)
        if address not in (0xcd9f8, 0xcd9fc):
            continue
        side = (address - 0xcd9f8) // 4
        assert event['size'] == 4 and signed(event['before']) == cash[side]
        deltas[event['pc']][side] += signed(event['after'] - event['before'])
        cash[side] = signed(event['after'])
        write_count += 1
    assert cash == list(struct.unpack_from('<2i', after, 0xcd9f8))
    ledger_cash = cash_before[:]
    rival_transitions = []
    rival_inputs, rival_outputs = [], []
    for capture in row.get('natural_rival_boundaries', []):
        rb = zlib.decompress((ROOT / capture['before_path']).read_bytes())
        ra = zlib.decompress((ROOT / capture['after_path']).read_bytes())
        assert sha(rb) == capture['before_sha256'] and sha(ra) == capture['after_sha256']
        bc = list(struct.unpack_from('<2i', rb, 0xcd9f8)); ac = list(struct.unpack_from('<2i', ra, 0xcd9f8))
        delta = [signed(b-a) for a,b in zip(bc,ac)]
        policy = json.loads((ROOT/'natural-rival-audit.json').read_text())
        assert policy['all_passed']
        independent = next(c for c in policy['cases'] if c['clock']==capture['clock'] and c['input_sha256']==capture['before_sha256'])
        expected_delta = [signed(b-a) for a,b in zip(independent['cash_before'],independent['cash_after'])]
        assert bc==independent['cash_before'] and ac==independent['cash_after'] and delta==expected_delta
        if independent['reason']=='opened':assert delta==[0,-sum(independent['costs'])]
        delta = expected_delta
        ledger_cash = [signed(a+b) for a,b in zip(ledger_cash,delta)]
        rival_transitions.append(dict(clock=capture['clock'],cash_before=bc,cash_after=ac,cash_delta=delta))
        rival_inputs.append(rb); rival_outputs.append(ra)
    stores = []
    for slot in range(10):
        offset = 0x12b2f8 + slot * 5080
        if not before[offset] and not after[offset]:
            continue
        birth = next((b for b in rival_outputs if b[offset]), None) if not before[offset] else None
        terminal = after
        if before[offset] and not after[offset]:
            terminal = next(b for b in rival_inputs if b[offset])
        if birth is not None:
            # The original rival manager already charged all opening costs,
            # including the initial equipment day-ledger posting. Count only
            # subsequent ordinary sales/goods from this birth boundary onward.
            opening = list(struct.unpack_from('<5i', birth, offset + 0xd88))
            current = list(struct.unpack_from('<5i', after, offset + 0xd88))
            closed = [0] * 5
            side = struct.unpack_from('<H', birth, offset + 4)[0] >> 15
        else:
            assert before[offset] and (terminal[offset])
            assert before[offset+4:offset+6] == terminal[offset+4:offset+6]
            side = struct.unpack_from('<H', before, offset + 4)[0] >> 15
            opening = list(struct.unpack_from('<5i', before, offset + 0xd88))
            current = list(struct.unpack_from('<5i', terminal, offset + 0xd88))
            closed = list(struct.unpack_from('<5i', terminal, offset + 0xd9c)) if closes else [0] * 5
        sales = signed(closed[4] + current[4] - opening[4])
        goods = signed(closed[3] + current[3] - opening[3])
        expense = sum(closed[:3]); monthly_adjustment = 0; monthly_source = None
        if birth is None and closes and closes[0]['calendar'][2] == 1:
            monthly_open = struct.unpack_from('<5i', before, offset + 0xd38)
            monthly_source = [signed(a+b) for a,b in zip(monthly_open,closed)]
            monthly_adjustment = signed(7 * signed(monthly_source[4]-sum(monthly_source[:4])))
            assert list(struct.unpack_from('<5i',terminal,offset+0xd4c)) == [signed(v*8) for v in monthly_source]
            assert list(struct.unpack_from('<5i',terminal,offset+0xd38)) == [0] * 5
        ledger_cash[side] = signed(ledger_cash[side]+sales-goods-expense+monthly_adjustment)
        stores.append(dict(slot=slot,company=side,active_before=bool(before[offset]),active_after=bool(after[offset]),
            opening_ledger=opening,closing_ledger=current,previous_day_ledger=closed,additional_sales=sales,
            additional_goods=goods,daily_expense=expense,monthly_source_ledger=monthly_source,
            monthly_adjustment=monthly_adjustment,new_store_opening_costs_accounted_at_rival_boundary=birth is not None))
    assert ledger_cash == cash, ('cash from ordinary ledgers plus rival transitions',ledger_cash,cash)
    assert len(row['steps']) == len(row['master_reasons'])
    expected_loops = sum(len(step['active_slots']) for step,reason in zip(row['steps'],row['master_reasons']) if reason == 'normal')
    assert len(row['whole_staff_loop_checks']) == expected_loops
    assert len(row['customer_loop_checks']) == expected_loops
    files = []
    for path in (proof_path, algo / (output + '-progress.json'),
                 snapshots / (output + '.json'), snapshots / (output + '.ram.zlib')):
        target = ROOT / 'evidence' / path.relative_to(algo)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, target)
        files.append(dict(path=str(target.relative_to(ROOT)), bytes=target.stat().st_size,
                          sha256=sha(target.read_bytes())))
    item = dict(output=output, source=source, passed=True, updates=count,
                clock_before=clock, clock_after=clock + 2 * count,
                completed_iterations=final_meta['completed_iterations'],
                source_ram_sha256=opening_meta['ram_sha256'], final_ram_sha256=final_meta['ram_sha256'],
                cash_before=cash_before, cash_after=cash, cash_from_ledgers=ledger_cash,
                cash_write_count=write_count, cash_delta_by_pc=dict(deltas), stores=stores,
                rival_cash_transitions=rival_transitions, daily_close_checks=closes, staff_checks=len(row['whole_staff_loop_checks']),
                customer_checks=len(row['customer_loop_checks']), frames=proof['frames_verified'], files=files)
    rows.append(item)
    (ROOT / (output + '.audit.json')).write_text(json.dumps(item, ensure_ascii=False, indent=2) + '\n')
    status = dict(all_passed=len(rows) == 3, completed_segments=len(rows), planned_segments=3,
                  total_updates=sum(r['updates'] for r in rows), cases=rows,
                  limits=['Natural single-conversion main trajectory, no cash/clock/roster/RNG edits.',
                          'Independent parent and reached monitors with original shared child routines.',
                          'SDK/GPU/SPU/IRQ boundaries are modeled as in the archived runner.',
                          'All commits should preserve each final proof and its CPU restart; partial progress is not a completed segment.'])
    (ROOT / 'long-continuation-status.json').write_text(json.dumps(status, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({k: item[k] for k in ('output', 'updates', 'clock_after', 'cash_after')}), flush=True)
assert rows[-1]['clock_after'] == 24560
