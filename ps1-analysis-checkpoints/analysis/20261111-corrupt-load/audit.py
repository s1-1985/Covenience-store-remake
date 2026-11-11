#!/usr/bin/env python3
"""Audit full native UI/file results separately from native parent comparison."""
import hashlib,json,struct,zlib
from pathlib import Path
ROOT=Path(__file__).resolve().parent
rows=[]
for case in ('payload-bit-flip','checksum-bit-flip','byte-swap-preserving-sum'):
    folder=ROOT/case
    d=json.loads((folder/'play-load.json').read_text())
    accepted=case=='byte-swap-preserving-sum'
    assert d['all_passed'] and d['checksum_accepted']==accepted
    assert len(d['load_policy'])==1 and d['load_policy'][0]['result']==(0 if accepted else -1)
    assert d['protected_live_fields']==[dict(regions=37,unchanged=True,return_value=0 if accepted else 0xffffffff)]
    assert len(d['decode_checks'])==int(accepted)
    assert len(d['confirmation_policy'])==(1 if accepted else 2)
    assert d['confirmation_policy'][0]['attempt']==(0 if accepted else -1)
    assert d['confirmation_policy'][-1]['terminal']
    if not accepted: assert d['confirmation_policy'][-1]['action']=='cancel'
    reads=[x for x in d['card']['io'] if x['op']=='read' and x['requested']==128]
    assert len(reads)==892 and [x['file_offset'] for x in reads]==list(range(512,114688,128))
    assert not any(x['op']=='write' for x in d['card']['io'])
    calls=d['load_policy'][0]['calls']
    messages=[args[2] for fn,args in calls if fn==0x8004e494]
    assert messages==[0x1e6,0x1e2,0x1e4,0x1e9 if accepted else 0x1f2]
    card=(folder/'operating-menu-save.card-file.bin').read_bytes()
    assert len(card)==114688
    meta=json.loads(next(folder.glob('TOWN0001-*.json')).read_text())
    ram=zlib.decompress(next(folder.glob('TOWN0001-*.ram.zlib')).read_bytes())
    assert len(ram)==2097152 and hashlib.sha256(ram).hexdigest()==meta['ram_sha256']
    clock=struct.unpack_from('<I',ram,0xcd93c)[0]
    cash=struct.unpack_from('<2i',ram,0xcd9f8)
    assert clock==(17646 if accepted else 17766)
    assert cash[0]==(99005440 if accepted else 99005641)
    assert struct.unpack_from('<I',ram,0xcd97c)[0]==0
    rows.append(dict(case=case,passed=True,checksum_accepted=accepted,
        read_chunks=len(reads),native_decoder_calls=len(d['decode_checks']),
        attempt_preserved_live_regions=37,confirmation=d['confirmation_policy'],
        message_ids=messages,final_clock=clock,final_cash=list(cash),
        final_ram_sha256=meta['ram_sha256'],input_file_sha256=hashlib.sha256(card).hexdigest()))
out=dict(all_passed=True,total=len(rows),source_snapshot='TOWN0001-ci-main-17-single',
    cases=rows,scope='Actual operating menu -> original card reader -> original checksum -> retry/cancel or native decoder -> operating loop.',
    limits=['Controlled copies of previously committed raw-card inputs; no natural-corruption frequency claim.',
            'Unicorn, original child functions and BIOS/file/SDK adapters are shared by the paired parent comparison.',
            '37 live ranges are unchanged across the attempt function only; normal simulation resumes afterwards.',
            'Accepted collision proves these bytes reach the decoder; it does not prove all malformed payloads are safe.',
            'No physical BIOS/SIO or device/GPU/audio validation. Branch results do not replace the natural main trajectory.'])
(ROOT/'results.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(dict(all_passed=True,total=len(rows),native_read_chunks=sum(x['read_chunks'] for x in rows))))
