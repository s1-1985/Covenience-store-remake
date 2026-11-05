#!/usr/bin/env python3
"""Original MIPS file routines against a documented raw-card layout model.

Run: python verify_card.py /path/to/restored/algorithm-analysis
No game/UI/BIOS state is patched to simulate successful native completion.
These are direct function diagnostics, not continuous UI or real hardware tests.
"""
import hashlib
import json
import runpy
import struct
import sys
import zlib
from pathlib import Path
from raw_card import RawCard, CardFiles, BLOCK, FRAME, frame_checksum

ROOT = Path(__file__).resolve().parent
algo = Path(sys.argv[1]).resolve()
sys.path.insert(0, str(algo))
from save_codec import BASE, SIZE, FIELDS, encode, valid

ref = runpy.run_path(str(ROOT.parent/'20261103-native-file-recovery/native-file-analysis.py'), run_name='native_reference')
Cpu, LogicalFiles, PATH, GP = (ref[k] for k in ('Cpu', 'LogicalFiles', 'PATH', 'GP'))
exe = (algo/'source/SLPS_007.82').read_bytes()
sha = lambda data: hashlib.sha256(bytes(data)).hexdigest()
assert sha(exe) == ref['EXE_SOURCE_SHA']


class RawFiles(LogicalFiles):
    def __init__(self, cpu, card):
        initial = {path: card.read(path, 0, item['size'], trace=False) for path, item in card.validate().items()}
        super().__init__(cpu, initial)
        self.files = CardFiles(card)


def call(cpu, address, mode):
    value = cpu.run(address, [mode], limit=2000000, stack_pointer=0x801d0000, global_pointer=GP)
    assert value == 0
    return dict(function=hex(address), mode=mode, return_value=value, instructions=cpu.steps)


def model_checks():
    records = []
    def rejects(name, operation):
        try:
            operation()
        except ValueError as error:
            records.append(dict(case=name, rejected=True, reason=str(error)))
        else:
            raise AssertionError(name)
    def fixed_frame(image, block):
        image[block*FRAME+127] = frame_checksum(image[block*FRAME:(block+1)*FRAME])
    card = RawCard()
    assert len(card.image) == 131072 and len(card.validate()) == 0
    card.create(b'bu00:ONE', b'1'*BLOCK)
    assert card.validate()[b'bu00:ONE']['blocks'] == [1]
    card.create(b'bu00:MULTI', b'2'*(14*BLOCK))
    assert card.read(b'bu00:MULTI', 0, 14*BLOCK) == b'2'*(14*BLOCK)
    rejects('full card', lambda: card.create(b'bu00:FULL', bytes(BLOCK)))
    rejects('duplicate name', lambda: card.create(b'bu00:ONE', bytes(BLOCK)))
    rejects('unaligned size', lambda: RawCard().create(b'bu00:BAD', b'x'))
    rejects('long filename', lambda: RawCard().create(b'bu00:'+b'X'*21, bytes(BLOCK)))
    rejects('short image', lambda: RawCard(bytes(131071)))
    image = bytearray(card.image); image[127] ^= 1
    rejects('header XOR', lambda: RawCard(image))
    image = bytearray(card.image); image[2*FRAME+127] ^= 1
    rejects('directory XOR', lambda: RawCard(image))
    image = bytearray(card.image); struct.pack_into('<H', image, 2*FRAME+8, 1); fixed_frame(image, 2)
    rejects('cycle with valid XOR', lambda: RawCard(image))
    image = bytearray(card.image); struct.pack_into('<H', image, 2*FRAME+8, 15); fixed_frame(image, 2)
    rejects('out-of-range link with valid XOR', lambda: RawCard(image))
    image = bytearray(card.image); struct.pack_into('<I', image, 2*FRAME+4, BLOCK); fixed_frame(image, 2)
    rejects('size mismatch with valid XOR', lambda: RawCard(image))
    image = bytearray(card.image); struct.pack_into('<I', image, 3*FRAME, 0x53); fixed_frame(image, 3)
    rejects('wrong continuation state', lambda: RawCard(image))
    image = bytearray(RawCard().image); struct.pack_into('<I', image, FRAME, 0x52); fixed_frame(image, 1)
    rejects('orphan active block', lambda: RawCard(image))
    image = bytearray(RawCard().image); struct.pack_into('<I', image, FRAME, 0xa1); fixed_frame(image, 1)
    rejects('deleted block unsupported', lambda: RawCard(image))
    image = bytearray(RawCard().image); struct.pack_into('<I', image, 16*FRAME, 0); fixed_frame(image, 16)
    rejects('bad sector remap unsupported', lambda: RawCard(image))
    boundary = RawCard(allocation_order=[15, 1]+list(range(2, 15)))
    boundary.create(b'bu00:CROSS', bytes(2*BLOCK))
    before = bytes(boundary.image)
    boundary.write(b'bu00:CROSS', BLOCK-3, b'ABCDEFG')
    assert boundary.read(b'bu00:CROSS', BLOCK-3, 7) == b'ABCDEFG'
    assert boundary.transfers[-1]['segments'] == [dict(logical=8189, physical=131069, block=15, size=3), dict(logical=8192, physical=8192, block=1, size=4)]
    touched = set(range(131069, 131072)) | set(range(8192, 8196))
    assert all(a == b for index, (a, b) in enumerate(zip(before, boundary.image)) if index not in touched)
    return dict(all_passed=True, rejection_cases=records, full_capacity_files=card.validate().__len__(), crossing_segments=boundary.transfers[-1]['segments'])


snapshot = 'TOWN0001-ci-main-16-single'
snapdir = algo/'source/opened-snapshots-20261028'
meta = json.loads((snapdir/(snapshot+'.json')).read_text())
ram = zlib.decompress((snapdir/(snapshot+'.ram.zlib')).read_bytes())
assert len(ram) == 2097152 and sha(ram) == meta['ram_sha256']
encoder = Cpu(exe); encoder.mem[:] = ram
expected = bytes(encode(bytearray(encoder.read(BASE, SIZE)), encoder.read))
encoder_result = encoder.run(0x8006b81c, limit=15000000, stack_pointer=0x801d0000, global_pointer=GP)
assert encoder.read(BASE, SIZE) == expected and valid(expected)
native_body = encoder.read(BASE, 114176)
(ROOT/'main-16-native-encoded-body.bin').write_bytes(native_body)
previous = (ROOT.parent/'20261105-view-controls/operating-menu-save.card-file.bin').read_bytes()
assert len(previous) == 114688 and valid(previous[512:512+SIZE])
bodies = [('main-16', native_body), ('operating-menu-previous', previous[512:])]
orders = {'contiguous': list(range(1, 16)), 'fragmented': [15, 1, 14, 2, 13, 3, 12, 4, 11, 5, 10, 6, 9, 7, 8]}
records = []
for layout, order in orders.items():
    card = RawCard(allocation_order=order)
    cpu = Cpu(exe); env = RawFiles(cpu, card)
    control = Cpu(exe); baseline = LogicalFiles(control, {})
    # Same explicit writer scratch initialization as the prior native-file suite.
    for machine in (cpu, control):
        machine.write(0x801b0000, b'\xa6'*0x40000)
        machine.write(0x800d6270, struct.pack('<I', 0xdeadbeef))
    phases = []
    for phase, (source, body) in enumerate(bodies):
        io_start, map_start = len(env.io), len(card.transfers)
        before = bytes(card.image)
        before_header = bytes(env.files[PATH])[:512] if phase else None
        calls = []
        for machine in (cpu, control):
            machine.write(BASE, body)
            for mode in (0, 1):
                record = call(machine, 0x8007adf8, mode)
                if machine is cpu: calls.append(record)
        saved = bytes(env.files[PATH])
        assert saved == bytes(baseline.files[PATH]) and saved[512:] == body
        assert saved[:4] == b'SC\x13\x0e'
        if phase:
            assert saved[:512] == before_header and bytes(card.image[:BLOCK]) == before[:BLOCK]
        entry = card.validate()[PATH]
        assert entry['blocks'] == order[:14] and entry['size'] == 114688
        free = order[14]
        assert bytes(card.image[free*BLOCK:(free+1)*BLOCK]) == before[free*BLOCK:(free+1)*BLOCK]
        (ROOT/(layout+'-'+str(phase)+'.mcr')).write_bytes(card.image)
        (ROOT/(layout+'-'+str(phase)+'.card-file.bin')).write_bytes(saved)
        # Reparse only raw image bytes; no old directory object or buffer survives.
        reopened = RawCard(bytes(card.image))
        reader = Cpu(exe); read_env = RawFiles(reader, reopened)
        reader.write(BASE, b'\xcc'*114176)
        for mode in (0, 1): calls.append(call(reader, 0x8007ab2c, mode))
        assert reader.read(BASE, 114176) == body
        payload = reader.read(BASE, SIZE)
        assert valid(payload)
        reader.run(0x8006bc40, limit=15000000, stack_pointer=0x801d0000, global_pointer=GP)
        assert all(reader.read(address, length) == payload[offset:offset+length] for offset, address, length in FIELDS)
        assert not env.fds and not read_env.fds and env.io == baseline.io
        writes = [r for r in env.io[io_start:] if r['op'] == 'write' and r['requested'] == 128]
        reads = [r for r in read_env.io if r['op'] == 'read' and r['requested'] == 128]
        for transfers in (writes, reads):
            assert len(transfers) == 892
            assert [r['file_offset'] for r in transfers] == list(range(512, 114688, 128))
            assert all(r['requested'] == r['result'] == 128 for r in transfers)
        mapped_reads = [r for r in reopened.transfers if r['op'] == 'read' and r['size'] == 128]
        assert len(mapped_reads) == 892
        assert {r['segments'][0]['block'] for r in mapped_reads} == set(order[:14])
        trace = dict(writer=env.io[io_start:], reader=read_env.io, raw_writer=card.transfers[map_start:], raw_reader=reopened.transfers)
        trace_path = ROOT/(layout+'-'+str(phase)+'.trace.json.zlib')
        trace_path.write_bytes(zlib.compress(json.dumps(trace, separators=(',', ':')).encode(), 9))
        phases.append(dict(kind='create' if phase == 0 else 'overwrite', source=source, calls=calls,
                           blocks=entry['blocks'], free_block=free, body_bytes=len(body), body_sha256=sha(body),
                           file_sha256=sha(saved), image_sha256=sha(card.image), write_transfers=len(writes),
                           read_transfers=len(reads), decoded_regions=len(FIELDS), logical_baseline_equal=True,
                           directory_unchanged_on_overwrite=bool(phase), trace=trace_path.name))
    records.append(dict(layout=layout, phases=phases))
for phase in range(2):
    assert records[0]['phases'][phase]['file_sha256'] == records[1]['phases'][phase]['file_sha256']
    assert records[0]['phases'][phase]['image_sha256'] != records[1]['phases'][phase]['image_sha256']
result = dict(all_passed=True, source_exe_sha256=sha(exe), source_snapshot=snapshot,
              source_ram_sha256=sha(ram), native_encoder_return=encoder_result,
              model_checks=model_checks(), records=records,
              limits=['Direct native function diagnostics with controlled BIOS events/file hooks.',
                      'Filesystem mapping is a documented model, not independent BIOS or SIO execution.',
                      'Model rejection tests do not establish original BIOS recovery/error behavior.',
                      'Deleted-file recovery, bad-sector remaps, physical timing and hardware remain unverified.',
                      'Experimental direct calls do not advance or replace natural main-16.'])
(ROOT/'results.json').write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n')
print(json.dumps(dict(all_passed=True, layouts=len(records), phases=4, body_writes=3568, body_reads=3568, decoded_regions_per_load=37)))
