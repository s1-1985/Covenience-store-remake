#!/usr/bin/env python3
"""Audit ten integrated title/card traces against explicit response expectations."""
import collections
import hashlib
import json
from pathlib import Path

root = Path(__file__).resolve().parent
expected = {
    # Both read modes refresh card state, in addition to title's initial probe.
    'success': (0, (3, 3, 3), 'resume', 0x1e9),
    'bad_checksum': (0, (3, 3, 3), 'load_nonzero', 0x1f2),
    'init_error_2': (2, (1, 1, 1), 'load_nonzero', 0x1e1),
    'init_error_3': (3, (1, 1, 1), 'load_nonzero', 0x1f5),
    'init_error_4': (4, (30, 0, 0), 'load_nonzero', 0x1dd),
    'init_error_5': (5, (3, 0, 0), 'load_nonzero', 0x1df),
    'info_busy_twice': (0, (5, 3, 3), 'resume', 0x1e9),
    'post_busy_twice': (0, (3, 3, 5), 'resume', 0x1e9),
    'header_mutation': (0, (3, 3, 3), 'resume', 0x1e9),
    'tail_mutation': (0, (3, 3, 3), 'resume', 0x1e9),
}
rows = []
for name, (status, commands, branch, message) in expected.items():
    path = root / (name + '.json')
    data = json.loads(path.read_text())
    title, bridge = data['title'], data['bridge']
    assert data['all_passed'] and bridge['open_handles'] == 0
    assert title['branch'] == branch and message in title['message_ids']
    assert title['runtime_tables_preserved_after_resume']['both_cpus']
    assert bridge['native_calls'][0]['function'] == '0x8007b1f8'
    assert bridge['native_calls'][0]['caller'] == '0x800515d0'
    assert bridge['native_calls'][0]['status'] == status
    counts = collections.Counter(row[0] for row in bridge['commands'])
    assert tuple(counts[k] for k in ('info', 'load', 'post')) == commands
    reads = [row for row in bridge['io'] if row['op'] == 'read']
    if status == 0:
        assert len(reads) == 892
        assert [row['file_offset'] for row in reads] == list(range(512, 114688, 128))
        assert [row['caller'] for row in bridge['native_calls'][1:]] == ['0x8005163c', '0x80051654']
        assert [row['argument'] for row in bridge['native_calls'][1:]] == [0, 1]
        assert title['payload_valid'] == (name != 'bad_checksum')
    else:
        assert not reads and len(bridge['native_calls']) == 1
    rows.append(dict(case=name, passed=True, init_status=status, commands=dict(counts),
                     branch=branch, message=hex(message), file_reads=len(reads),
                     native_calls=len(bridge['native_calls']), frames=len(title['frames']),
                     sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                     resumed_clocks=[row['clock'] for row in title['resumed_play']['steps']]
                     if title['resumed_play'] else []))
assert sum(row['file_reads'] for row in rows) == 5352
out = dict(all_passed=True, total=len(rows), cases=rows, native_calls=sum(r['native_calls'] for r in rows),
           file_reads=sum(r['file_reads'] for r in rows), paired_processors_per_case=2,
           header_and_tail_scope='Header/tail mutations are accepted under the named logical BIOS model; this does not establish physical-card header acceptance.',
           development_failure='The first adapter replaced 7E57C globally and compared 120 unrelated stack-destination copies. That failed diagnostic is preserved. The final adapter leaves 7E57C executing natively; no mismatches are normalized away.')
(root / 'title-chain-coverage.json').write_text(json.dumps(out, ensure_ascii=False, indent=2) + '\n')
print(json.dumps(dict(all_passed=True, cases=len(rows), native_calls=out['native_calls'], file_reads=out['file_reads'])))
