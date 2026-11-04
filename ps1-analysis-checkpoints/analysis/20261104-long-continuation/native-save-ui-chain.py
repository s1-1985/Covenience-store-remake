#!/usr/bin/env python3
"""Original encoder -> original 501FC/505A0 save UI -> native file write.

Card BIOS semantics match the integrated title test. The existing independent
505A0 policy monitor is retained, with its synthetic completions removed.
"""
import ast
import difflib
import hashlib
import json
import runpy
import struct
import sys
import types
from pathlib import Path

ROOT = Path(__file__).resolve().parent
algo = Path(sys.argv[1]).resolve()
name = sys.argv[2]
profile = sys.argv[3] if len(sys.argv) > 3 else 'low'
assert profile in ('low', 'high-mirror')
output_prefix = 'save-ui' if profile == 'low' else 'save-ui-high-mirror'
sys.path.insert(0, str(algo))
from check_machine import *
from opened_snapshot_harness_20261029 import restore
from caller_connection_harness import Memory
from save_codec import BASE, SIZE, encode, valid
from verify_schedule_selector_frames import seq
from unicorn import UC_HOOK_CODE


def sha(data):
    return hashlib.sha256(data).hexdigest()


reference = runpy.run_path(str(ROOT.parent / '20261103-native-file-recovery/native-file-analysis.py'), run_name='file_reference')
LogicalFiles, CARD_PATH = reference['LogicalFiles'], reference['PATH']
# Reuse only the adapter class definitions; never execute the other experiment's
# top-level producer or cases as a side effect of importing it.
adapter_path = ROOT / 'native-title-card-chain.py'
tree = ast.parse(adapter_path.read_text())
classes = [node for node in tree.body if isinstance(node, ast.ClassDef)]
assert [node.name for node in classes] == ['Facade', 'NativeCardBridge']
exec(compile(ast.Module(body=classes, type_ignores=[]), str(adapter_path), 'exec'), globals())

monitor_path = algo / 'source_save_write_monitor_20261031.py'
source = monitor_path.read_text()
old = '    m.byteset(0x800cd820,status);z.reg_write(UC_MIPS_REG_V0,0);z.reg_write(UC_MIPS_REG_PC,z.reg_read(UC_MIPS_REG_RA));return'
assert source.count(old) == 1
patched = source.replace(old, '    return # Native card status/write execute; no completion injection.')
patched = patched.replace('status=0 if a==0x8007b1f8 else write_status',
                          'status=expected_init_status if a==0x8007b1f8 else write_status')
patched = patched.replace('0x8007b1f8:1,0x8007adf8:1}',
                          '0x8007b1f8:1,0x8007adf8:1,0x8007b8a4:0}')
(ROOT / 'save-monitor.patch').write_text(''.join(difflib.unified_diff(
    source.splitlines(True), patched.splitlines(True), fromfile=monitor_path.name,
    tofile='observational_save_monitor.py')))
module = types.ModuleType('observational_save_monitor')
exec(compile(patched, str(monitor_path), 'exec'), module.__dict__)
original_policy = module.policy
rows = []
for mode in ('overwrite', 'create'):
    module.expected_init_status = 0 if mode == 'overwrite' else 2

    def policy(write_status):
        calls = original_policy(write_status)
        if mode == 'create':
            index = next(i for i, row in enumerate(calls) if row[0] == 0x8007b1f8) + 2
            calls[index:index] = [[0x8007b8a4, []], [0x80089ca4, [2]]]
        return calls

    module.policy = policy
    pair = []
    for which in (0, 1):
        plans = {0x800501fc: [seq([32, 64]) + [0] * 100],
                 0x800505a0: [[0] * 12 + seq([64]) + [0] * 100]}
        unit = restore(name, plans)
        u, runner = unit[:2]
        memory = Memory(u)
        wanted = bytes(encode(bytearray(memory.read(BASE, SIZE)), memory.read))
        assert valid(wanted)
        frozen = [(address, memory.read(address, size)) for address, size in (
            (0x8012b2f8, 50800), (0x80143ff8, 2100), (0x800cd9f8, 8),
            (0x800cd93c, 4))]
        rng_before = memory.word(0x800d6270)
        # Explicit diagnostic stack leaves the native create-file staging read
        # wholly inside mapped RAM. The high-stack crossing is preserved as an
        # unresolved boundary diagnostic, rather than silently synthesizing it.
        stack = 0x801d0000 if profile == 'low' else 0x801ffee0
        u.reg_write(UC_MIPS_REG_SP, stack)
        u.reg_write(UC_MIPS_REG_FP, stack)
        u.reg_write(UC_MIPS_REG_RA, 0x80001000)
        u.emu_start(0x8006b81c, 0x80001000, count=15000000)
        assert u.reg_read(UC_MIPS_REG_PC) == 0x80001000
        assert memory.read(BASE, SIZE) == wanted
        body = memory.read(BASE, 114176)
        existing = (ROOT / (name + '.card-file.bin')).read_bytes()
        assert existing[512:512 + SIZE] == wanted
        files = {CARD_PATH: existing} if mode == 'overwrite' else {}
        bridge = NativeCardBridge(u, runner, files)
        bridge.cpu.allow_ram_mirror = profile == 'high-mirror'
        header_observations = []
        def capture_header(z, pc, size, data):
            # 7BC14 allocates 8438 bytes and stages its header at FP+8228:
            # original-entry-SP - 210. This is before any header fields write.
            pointer = z.reg_read(UC_MIPS_REG_SP) - 0x210
            header_observations.append(dict(address=hex(pointer), before_hex=memory.read(pointer, 512).hex()))
        capture_hook = u.hook_add(UC_HOOK_CODE, capture_header, begin=0x8007bc14, end=0x8007bc14)
        monitor = module.SourceSaveWriteMonitor(u, runner, lambda: wanted)
        u.reg_write(UC_MIPS_REG_A0, 0)
        u.reg_write(UC_MIPS_REG_RA, 0x80001000)
        u.emu_start(0x800501fc, 0x80001000, count=100000000)
        assert u.reg_read(UC_MIPS_REG_PC) == 0x80001000
        runner.flush(0x80001000)
        assert u.reg_read(UC_MIPS_REG_V0) == 0
        assert all(memory.read(address, len(data)) == data for address, data in frozen)
        assert len(monitor.checks) == 1 and monitor.committed == wanted
        card = bytes(bridge.env.files[CARD_PATH])
        assert len(card) == 114688 and card[512:] == body
        assert not bridge.env.fds
        writes = [row for row in bridge.env.io if row['op'] == 'write' and row['requested'] == 128]
        assert len(writes) == 892
        assert [row['file_offset'] for row in writes] == list(range(512, 114688, 128))
        assert [row['function'] for row in bridge.native_calls] == ['0x8007b1f8', '0x8007adf8', '0x8007adf8']
        assert [row['status'] for row in bridge.native_calls] == [module.expected_init_status, 0, 0]
        if mode == 'create':
            assert len(header_observations) == 1
            before_header = bytes.fromhex(header_observations[0]['before_hex'])
            exe = EXE.read_bytes()
            title_offset = 0x10ce8 - 0x10000 + 2048
            title = exe[title_offset:].split(b'\0', 1)[0] + b'\0'
            prefix = bytes.fromhex('5343130e') + title
            assert len(prefix) == 13 and card[:13] == prefix
            assert card[13:96] == before_header[13:96]
            header_observations[0].update(retained_range=[13, 96], retained_bytes_sha256=sha(card[13:96]),
                                          original_title_hex=title.hex(), prefix_hex=prefix.hex())
        else:
            assert not header_observations
        out = dict(all_passed=True, mode=mode, profile=profile, stack=hex(stack), card_sha256=sha(card), payload_sha256=sha(wanted),
                   body_sha256=sha(body), monitor=monitor.checks, bridge=bridge.proof(),
                   frames=runner.frames, original_gameplay_fields_preserved=True)
        out['rng_before'] = rng_before
        out['rng_after'] = memory.word(0x800d6270)
        out['header_observations'] = header_observations
        pair.append(out)
        monitor.dispose()
        u.hook_del(capture_hook)
        for item in unit[2:6]:
            item.dispose()
        runner.dispose()
    assert pair[0] == pair[1]
    (ROOT / (output_prefix + '-' + mode + '.json')).write_text(json.dumps(pair[0], separators=(',', ':')) + '\n')
    (ROOT / (output_prefix + '-' + mode + '.card-file.bin')).write_bytes(card)
    rows.append(dict(mode=mode, all_passed=True, frames=len(pair[0]['frames']),
                     body_writes=892, payload_sha256=pair[0]['payload_sha256'],
                     card_sha256=pair[0]['card_sha256'], native_calls=pair[0]['bridge']['native_calls']))
    print('original save UI -> native card file passed', mode, flush=True)
out = dict(all_passed=True, total=len(rows), snapshot=name, profile=profile, cases=rows,
           original_monitor_sha256=sha(source.encode()), patched_monitor_sha256=sha(patched.encode()),
           adapter_sha256=sha(adapter_path.read_bytes()),
           limits=['501FC is an explicit direct UI entry after native encoder; no gameplay menu-navigation claim.',
                   'Low profile uses SP/FP=801D0000. High-mirror profile uses 801FFEE0 and explicit 2MB RAM mirrors within the first 8MB only at BIOS transfer reads.',
                   'High-mirror assumes the documented standard mirror configuration; memory-controller hardware/BIOS configuration is not restored or independently measured.',
                   'Source 505A0 call policy, rendering/resources, card status and file writes execute; only BIOS/file/event and prior SDK boundaries modeled.',
                   'Independent monitor predicts write success; exact saved file and all writes separately assert actual success.',
                   'Two identical native CPU runs establish determinism and model checks, not two independent CPU implementations.',
                   'Physical card allocation/serial transport, BIOS instructions and physical GPU/SPU/IRQ remain outside scope.'])
(ROOT / ('native-save-ui-summary.json' if profile == 'low' else 'native-save-ui-high-mirror-summary.json')).write_text(json.dumps(out, ensure_ascii=False, indent=2) + '\n')
