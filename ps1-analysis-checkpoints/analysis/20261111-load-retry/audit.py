#!/usr/bin/env python3
"""Audit two actual native attempts inside one original confirmation session."""
import hashlib,json,struct,zlib
from pathlib import Path
ROOT=Path(__file__).resolve().parent
rows=[]
for case in ('repeat-corrupt','replace-with-valid'):
    f=ROOT/case;d=json.loads((f/'play-load.json').read_text());recover=case=='replace-with-valid'
    assert d['all_passed'] and d['external_card_replacement']==recover
    assert len(d['load_policy'])==2
    assert [x['result'] for x in d['load_policy']]==[-1,0 if recover else -1]
    assert [x['checksum_valid'] for x in d['load_policy']]==[False,recover]
    assert d['protected_live_fields']==[dict(regions=37,unchanged=True,return_value=x) for x in (0xffffffff,0 if recover else 0xffffffff)]
    assert len(d['decode_checks'])==int(recover)
    confirms=d['confirmation_policy'];assert [x['action'] for x in confirms]==(['attempt','attempt'] if recover else ['attempt','attempt','cancel'])
    assert confirms[0]['terminal']==False and confirms[-1]['terminal']==True
    assert sum(x['function']=='0x80051174' for x in d['native_path'])==1
    assert sum(x['function']=='0x80051524' for x in d['native_path'])==2
    reads=[x for x in d['card']['io'] if x['op']=='read' and x['requested']==128]
    assert len(reads)==1784 and [x['file_offset'] for x in reads]==list(range(512,114688,128))*2
    assert not any(x['op']=='write' for x in d['card']['io'])
    assert d['card']['open_handles']==0
    messages=[]
    for p in d['load_policy']:
        msgs=[a[2] for fn,a in p['calls'] if fn==0x8004e494]
        assert msgs[:3]==[0x1e6,0x1e2,0x1e4];messages.append(msgs[-1])
    assert messages==[0x1f2,0x1e9 if recover else 0x1f2]
    meta=json.loads(next(f.glob('TOWN0001-*.json')).read_text());ram=zlib.decompress(next(f.glob('TOWN0001-*.ram.zlib')).read_bytes())
    assert hashlib.sha256(ram).hexdigest()==meta['ram_sha256']
    clock=struct.unpack_from('<I',ram,0xcd93c)[0];assert clock==(17646 if recover else 18966)
    rows.append(dict(case=case,passed=True,attempts=2,confirmation_sessions=1,native_results=[x['result'] for x in d['load_policy']],
        preserved_live_regions_per_attempt=37,native_read_chunks=len(reads),native_decodes=len(d['decode_checks']),
        messages=messages,external_card_replacement=recover,clock_after=clock,cash_after=list(struct.unpack_from('<2i',ram,0xcd9f8)),
        original_live_clock=18960,restored_saved_clock=17640 if recover else None,ram_sha256=meta['ram_sha256'],confirmation=confirms))
(ROOT/'results.json').write_text(json.dumps(dict(all_passed=True,total=2,cases=rows,
    source_snapshot='TOWN0001-ci-main-20-single',limits=['Card replacement is a controlled modeled external event before the second attempt, not original BIOS/SIO execution.',
    'The original UI, card routines, checksum and decoder execute unchanged; the driver supplies raw input streams.',
    'The transfer map for replacement covers the final card attempt; the complete logical I/O trace covers both attempts.',
    'Paired parents share Unicorn/native child routines and existing external adapters. Diagnostic branches do not replace natural main-20.']),ensure_ascii=False,indent=2)+'\n')
print('two retry cases passed; 3568 native 128-byte reads')
