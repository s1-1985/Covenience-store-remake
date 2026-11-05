#!/usr/bin/env python3
"""Separate filesystem integrity from the game's original payload checksum.

Deliberate mutations are made in copies of the strict diagnostic card image.
This invokes the original checksum gate directly; it does not test UI errors.
"""
import hashlib
import json
import runpy
import struct
import sys
from pathlib import Path
from raw_card import RawCard

ROOT = Path(__file__).resolve().parent
algo = Path(sys.argv[1]).resolve()
ref = runpy.run_path(str(ROOT.parent/'20261103-native-file-recovery/native-file-analysis.py'), run_name='file_reference')
Cpu, LogicalFiles, PATH, GP, BODY = (ref[k] for k in ('Cpu', 'LogicalFiles', 'PATH', 'GP', 'BODY'))
exe = (algo/'source/SLPS_007.82').read_bytes()
assert hashlib.sha256(exe).hexdigest() == ref['EXE_SOURCE_SHA']
original = (ROOT/'fragmented-0.mcr').read_bytes()
initial = RawCard(original)
file = initial.read(PATH, 0, 114688, trace=False)
checksum_offset = 512+0x197a8
variants = [('valid', []), ('payload-bit-flip', [(512+0x3c, file[512+0x3c]^1)]),
            ('checksum-bit-flip', [(checksum_offset, file[checksum_offset]^1)])]
left = 512+0x3c
right = next(index for index in range(512, 576) if file[index] != file[left])
variants.append(('byte-swap-preserving-sum', [(left, file[right]), (right, file[left])]))
records = []
for name, changes in variants:
    card = RawCard(original)
    for offset, value in changes:
        card.write(PATH, offset, bytes([value]))
    assert card.validate() == initial.validate()
    damaged = card.read(PATH, 0, 114688, trace=False)
    cpu = Cpu(exe)
    env = LogicalFiles(cpu, {PATH: damaged})
    # Read via the original file routine; the filesystem mapping was independently
    # exercised in verify_card.py. Here isolate the original checksum predicate.
    cpu.write(0x800d6270, struct.pack('<I', 0xdeadbeef))
    for mode in (0, 1):
        assert cpu.run(0x8007ab2c, [mode], limit=1000000, stack_pointer=0x801d0000, global_pointer=GP) == 0
    assert cpu.read(BODY, 114176) == damaged[512:]
    result = cpu.run(0x8005188c, limit=15000000, stack_pointer=0x801d0000, global_pointer=GP)
    expected = 0 if name in ('valid', 'byte-swap-preserving-sum') else -1
    assert result == expected and cpu.read(0x800d6270, 4) == struct.pack('<I', 0xdeadbeef)
    if changes:
        (ROOT/('mutated-'+name+'.mcr')).write_bytes(card.image)
    records.append(dict(case=name, patches=[dict(file_offset=offset, before=file[offset], after=value) for offset, value in changes],
                        filesystem_directory_valid=True, native_checksum_return=result, expected=expected,
                        checksum_instructions=cpu.steps, rng_preserved=True,
                        image_sha256=hashlib.sha256(card.image).hexdigest(), file_sha256=hashlib.sha256(damaged).hexdigest()))
(ROOT/'checksum-results.json').write_text(json.dumps(dict(all_passed=True, cases=records,
    limits=['Controlled mutations and direct checksum-gate calls; not UI error behavior.',
            'Directory XOR validates metadata, not save body; additive checksum collisions remain possible.']), indent=2)+'\n')
print('four raw-card payload checksum diagnostics passed', flush=True)
