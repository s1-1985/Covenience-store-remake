#!/usr/bin/env python3
"""Compare both original save modes under strict-low-stack and mirrored-high-stack fixtures."""
import hashlib
import json
from pathlib import Path

root = Path(__file__).resolve().parent
rows = []
for mode in ('overwrite', 'create'):
    a = json.loads((root / ('save-ui-' + mode + '.json')).read_text())
    b = json.loads((root / ('save-ui-high-mirror-' + mode + '.json')).read_text())
    low = (root / ('save-ui-' + mode + '.card-file.bin')).read_bytes()
    high = (root / ('save-ui-high-mirror-' + mode + '.card-file.bin')).read_bytes()
    assert a['all_passed'] and b['all_passed']
    assert len(low) == len(high) == 114688 and low[512:] == high[512:]
    assert a['rng_before'] == b['rng_before'] and a['rng_after'] == b['rng_after']
    assert a['rng_before'] != a['rng_after']
    assert a['profile'] == 'low' and b['profile'] == 'high-mirror'
    changes = [i for i, (x, y) in enumerate(zip(low, high)) if x != y]
    for item in (a, b):
        writes = [r for r in item['bridge']['io'] if r['op'] == 'write' and r['requested'] == 128]
        assert len(writes) == 892
        assert item['bridge']['open_handles'] == 0 and item['original_gameplay_fields_preserved']
        if mode == 'create':
            header = item['header_observations'][0]
            actual = low if item is a else high
            prior = bytes.fromhex(header['before_hex'])
            assert actual[13:96] == prior[13:96]
            assert actual[:13].hex() == header['prefix_hex']
    if mode == 'overwrite':
        assert not changes and not b['bridge']['ram_mirror_reads']
    else:
        assert changes == list(range(13, 96))
        assert len(b['bridge']['ram_mirror_reads']) == 1
        request = b['bridge']['ram_mirror_reads'][0]
        assert request['address'] == '0x801f7a20' and request['bytes'] == 114688
        assert request['chunks'] == [dict(physical_ram='0x1f7a20', bytes=34272), dict(physical_ram='0x0', bytes=80416)]
    rows.append(dict(mode=mode, all_passed=True, changed_file_offsets=changes,
                     body_equal=True, body_sha256=hashlib.sha256(low[512:]).hexdigest(),
                     low_card_sha256=hashlib.sha256(low).hexdigest(), high_card_sha256=hashlib.sha256(high).hexdigest(),
                     body_writes_per_profile=892, high_mirror_reads=b['bridge']['ram_mirror_reads'],
                     rng_before=a['rng_before'], rng_after=a['rng_after']))
created = json.loads((root / 'save-ui-high-mirror-create.json').read_text())
loaded = json.loads((root / 'save_ui_created.json').read_text())
producer = json.loads((root / 'title-save-ui-created-summary.json').read_text())['producer']
assert created['card_sha256'] == loaded['supplied_card_sha256'] == producer['external_card_sha256']
assert created['payload_sha256'] == loaded['title']['payload_sha256']
assert loaded['title']['branch'] == 'resume' and loaded['title']['runtime_tables_preserved_after_resume']['both_cpus']
connection = dict(all_passed=True, created_file='save-ui-high-mirror-create.card-file.bin',
                  card_sha256=created['card_sha256'], payload_sha256=created['payload_sha256'],
                  load_proof='save_ui_created.json', resumed_clocks=[r['clock'] for r in loaded['title']['resumed_play']['steps']],
                  scope='The exact UI-created logical file is handed to a separate title fixture. Not a continuous save-UI-to-title navigation call stack.')
out = dict(all_passed=True, modes=2, profiles_per_mode=2, body_writes=3568, cases=rows, created_file_title_connection=connection,
           header_provenance='Original 7BC14 writes SC/flags/blocks plus the nul-terminated title and icon/palette data. In these fixtures file offsets13..95 retain the pre-entry stack bytes, independently captured before the function ran.',
           limits=['83 differences are observed for the chosen two stack fixtures, not a universal count across all saves.',
                   'Create-file header is not normalized or replaced by the overwrite fixture.',
                   'High-stack BIOS transfer assumes documented standard 2MB-in-8MB mirroring; the physical controller is not emulated.',
                   'Preserved gameplay regions exclude RNG, which naturally advances during UI and is recorded separately.'])
(root / 'save-ui-coverage.json').write_text(json.dumps(out, ensure_ascii=False, indent=2) + '\n')
print(json.dumps(dict(all_passed=True, modes=2, profiles=2, body_writes=3568)))
