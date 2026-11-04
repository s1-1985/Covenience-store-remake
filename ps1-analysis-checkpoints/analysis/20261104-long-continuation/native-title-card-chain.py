#!/usr/bin/env python3
"""Run title load through original card status and file routines, down to BIOS hooks.

The r2 title harness is loaded as a separate module with one exact, recorded
replacement: remove the synthetic status/payload/return at 7B1F8 and 7AB2C.
The archived source is never rewritten. LogicalFiles' existing BIOS semantics
are shared through a Unicorn memory/register facade.
"""
import difflib
import hashlib
import json
import runpy
import struct
import sys
import types
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parent
algo = Path(sys.argv[1]).resolve()
snapshot = sys.argv[2]
scenarios = sys.argv[3:] or ['success', 'bad_checksum', 'init_error_2']
sys.path.insert(0, str(algo))
from check_machine import *
from caller_connection_harness import Memory
from save_codec import BASE, SIZE, valid
from unicorn import UC_HOOK_CODE

reference_path = ROOT.parent / '20261103-native-file-recovery/native-file-analysis.py'
reference = runpy.run_path(str(reference_path), run_name='native_file_reference')
Cpu, LogicalFiles, CARD_PATH = (reference[k] for k in ('Cpu', 'LogicalFiles', 'PATH'))


def sha(data):
    return hashlib.sha256(data).hexdigest()


class Facade:
    def __init__(self, u):
        self.u, self.hooks = u, {}

    @property
    def r(self):
        return [self.u.reg_read(k) for k in range(UC_MIPS_REG_0, UC_MIPS_REG_31 + 1)]

    def read(self, address, size):
        try:
            return bytes(self.u.mem_read(address & 0x1fffffff, size))
        except Exception as error:
            raise RuntimeError('card BIOS read address=' + hex(address) + ' size=' + str(size)) from error

    def write(self, address, data):
        self.u.mem_write(address & 0x1fffffff, bytes(data))

    def cstring(self, address, limit=1024):
        for size in range(limit):
            if self.read(address + size, 1) == b'\0':
                return self.read(address, size)
        raise ValueError('unterminated BIOS path')


class NativeCardBridge:
    def __init__(self, u, runner, files, responses=None):
        self.u, self.runner = u, runner
        self.cpu = Facade(u)
        self.env = LogicalFiles(self.cpu, files)
        for name, values in (responses or {}).items():
            self.env.responses[name] = list(values)
        self.hooks, self.native_calls, self.bios_calls = [], [], []
        for address, function in self.cpu.hooks.items():
            # The runner owns VSync. 7E57C is an ordinary MIPS byte-copy leaf,
            # so execute it natively rather than abstracting unrelated copies.
            if address in (0x80089ca4, 0x8007e57c):
                continue

            def endpoint(z, pc, size, data, function=function):
                args = self.cpu.r[4:8]
                result = function(self.cpu)
                self.bios_calls.append(dict(pc=hex(pc), args=args, result=result))
                z.reg_write(UC_MIPS_REG_V0, result & 0xffffffff)
                z.reg_write(UC_MIPS_REG_PC, z.reg_read(UC_MIPS_REG_RA))

            self.hooks.append(u.hook_add(UC_HOOK_CODE, endpoint, begin=address, end=address))
        for address in (0x8007b1f8, 0x8007ab2c, 0x8007adf8):
            def observe(z, pc, size, data):
                rec = dict(function=hex(pc), argument=z.reg_read(UC_MIPS_REG_A0),
                           caller=hex(z.reg_read(UC_MIPS_REG_RA)), bios_before=len(self.bios_calls))
                self.native_calls.append(rec)

                def finish():
                    rec.update(result=z.reg_read(UC_MIPS_REG_V0),
                               status=self.cpu.read(0x800cd820, 1)[0], bios_after=len(self.bios_calls),
                               payload_sha256=sha(self.cpu.read(BASE, SIZE)),
                               body_sha256=sha(self.cpu.read(BASE, 114176)))

                runner.onreturn(z.reg_read(UC_MIPS_REG_RA), finish)

            self.hooks.append(u.hook_add(UC_HOOK_CODE, observe, begin=address, end=address))

    def proof(self):
        return dict(native_calls=self.native_calls, bios_calls=self.bios_calls,
                    io=self.env.io, commands=self.env.commands, patterns=self.env.patterns,
                    open_handles=len(self.env.fds), files={k.decode(): sha(v) for k, v in self.env.files.items()})


def produce():
    folder = algo / 'source/opened-snapshots-20261028'
    meta = json.loads((folder / (snapshot + '.json')).read_text())
    ram = zlib.decompress((folder / (snapshot + '.ram.zlib')).read_bytes())
    assert sha(ram) == meta['ram_sha256']
    exe = EXE.read_bytes()
    assert sha(exe) == meta['source_executable_sha256']
    u = machine()
    u.mem_write(0, ram)
    u.reg_write(UC_MIPS_REG_SP, 0x801d0000)
    u.reg_write(UC_MIPS_REG_FP, 0x801d0000)
    u.reg_write(UC_MIPS_REG_RA, 0x80001000)
    u.emu_start(0x8006b81c, 0x80001000, count=15000000)
    assert u.reg_read(UC_MIPS_REG_PC) == 0x80001000
    body = bytes(u.mem_read(BASE & 0x1fffffff, 114176))
    assert valid(body[:SIZE])
    cpu = Cpu(exe)
    cpu.mem[:] = bytes(u.mem_read(0, 2097152))
    env = LogicalFiles(cpu, {})
    for mode in (0, 1):
        assert cpu.run(0x8007adf8, [mode], limit=1000000,
                       stack_pointer=0x801d0000, global_pointer=0x800cd6c4) == 0
    card = bytes(env.files[CARD_PATH])
    assert len(card) == 114688 and card[512:] == body
    (ROOT / (snapshot + '.card-file.bin')).write_bytes(card)
    (ROOT / 'producer-io.json').write_text(json.dumps(env.io, separators=(',', ':')) + '\n')
    return card, dict(snapshot=snapshot, source_ram_sha256=sha(ram), source_executable_sha256=sha(exe),
                      card_sha256=sha(card), payload_sha256=sha(body[:SIZE]),
                      tail_sha256=sha(body[SIZE:]), tail_origin='original encoder CPU RAM',
                      writer='original 7ADF8 modes0/1 in strict MIPS interpreter',
                      code_reference_sha256=sha(reference_path.read_bytes()))


old = """                arg=z.reg_read(UC_MIPS_REG_A0);cards[which].append([a,arg]);m.byteset(0x800cd820,(0 if scenario=='init_retry' and attempt_count[0]>1 else init_status) if a==0x8007b1f8 else read_status)
                if a==0x8007ab2c and arg==1 and not read_status:m.write(BASE,supplied)
                z.reg_write(UC_MIPS_REG_V0,0);z.reg_write(UC_MIPS_REG_PC,z.reg_read(UC_MIPS_REG_RA));return"""
new = """                arg=z.reg_read(UC_MIPS_REG_A0);cards[which].append([a,arg])
                # Native 7B1F8 / 7AB2C execute unchanged to named BIOS boundaries.
                return"""
source_path = algo / 'verify_title_native_load_20261029.py'
source = source_path.read_text()
assert source.count(old) == 1
patched = source.replace(old, new)
(ROOT / 'title-driver.patch').write_text(''.join(difflib.unified_diff(
    source.splitlines(True), patched.splitlines(True), fromfile=source_path.name,
    tofile='title_native_file_chain.py')))
module = types.ModuleType('title_native_file_chain')
module.__file__ = str(source_path)
exec(compile(patched, str(source_path), 'exec'), module.__dict__)
base_restore = module.restore
card, producer = produce()
rows = []
for scenario in scenarios:
    assert scenario in ('success', 'bad_checksum', 'init_error_2', 'init_error_3',
                        'init_error_4', 'init_error_5', 'info_busy_twice', 'post_busy_twice',
                        'header_mutation', 'tail_mutation')
    title_scenario = 'success' if scenario in ('info_busy_twice', 'post_busy_twice',
                                               'header_mutation', 'tail_mutation') else scenario
    responses = {'init_error_3': {'post': [3]}, 'init_error_4': {'info': [2]},
                 'init_error_5': {'info': [1]}, 'info_busy_twice': {'info': [2, 2, 0]},
                 'post_busy_twice': {'post': [2, 2, 0]}}.get(scenario, {})
    bridges = []
    supplied_file = bytearray(card)
    if scenario == 'bad_checksum':
        supplied_file[512 + 0x3c] ^= 1
    if scenario == 'header_mutation':
        supplied_file[:512] = bytes(512)
    if scenario == 'tail_mutation':
        supplied_file[512 + SIZE:] = b'\xa5' * (114176 - SIZE)
    files = {} if scenario == 'init_error_2' else {CARD_PATH: supplied_file}

    def restore(name, plans):
        unit = base_restore(name, plans)
        bridges.append(NativeCardBridge(unit[0], unit[1], files, responses))
        return unit

    module.restore = restore
    try:
        title = module.compare(title_scenario, snapshot, audit_runtime_tables=True)
        paired = [bridge.proof() for bridge in bridges]
        assert paired[0] == paired[1]
        for bridge in bridges:
            assert not bridge.env.fds
            assert all('result' in row for row in bridge.native_calls)
        if not scenario.startswith('init_error_'):
            reads = [r for r in paired[0]['io'] if r['op'] == 'read']
            assert len(reads) == 892
            assert [r['file_offset'] for r in reads] == list(range(512, 114688, 128))
            assert all(r['result'] == 128 for r in reads)
            assert len(paired[0]['native_calls']) == 3
            assert paired[0]['native_calls'][-1]['body_sha256'] == sha(supplied_file[512:])
        else:
            assert len(paired[0]['native_calls']) == 1
            assert paired[0]['native_calls'][0]['status'] == int(scenario.rsplit('_', 1)[1])
        title['limits'] = [v for v in title['limits'] if not v.startswith('Card7B1F8/')]
        title['limits'].append('7B1F8 and 7AB2C execute original routines; only the listed BIOS/file/event endpoints are modeled. Physical card transport/BIOS instructions are not executed.')
        row = dict(all_passed=True, scenario=scenario, title=title, bridge=paired[0],
                   supplied_card_sha256=sha(supplied_file) if files else None,
                   supplied_header_sha256=sha(supplied_file[:512]) if files else None,
                   supplied_tail_sha256=sha(supplied_file[512 + SIZE:]) if files else None,
                   response_configuration=responses)
        (ROOT / (scenario + '.json')).write_text(json.dumps(row, separators=(',', ':')) + '\n')
        rows.append(dict(scenario=scenario, all_passed=True, branch=title['branch'],
                         title_states=title['title_states'], frames=len(title['frames']),
                         card_calls=paired[0]['native_calls'], bios_calls=len(paired[0]['bios_calls']),
                         file_read_count=sum(r['op'] == 'read' for r in paired[0]['io']),
                         message_ids=title['message_ids']))
        print('native title/card chain passed', scenario, flush=True)
    except Exception:
        (ROOT / (scenario + '.failure.json')).write_text(json.dumps([b.proof() for b in bridges], separators=(',', ':')) + '\n')
        raise
out = dict(all_passed=True, total=len(rows), producer=producer, cases=rows,
           original_title_driver_sha256=sha(source.encode()), patched_title_driver_sha256=sha(patched.encode()),
           limits=['Title state1 is an explicit CPU fixture; no game-exit-to-title claim.',
                   'Original file writer creates the input; original title calls status, read, checksum, decode and resumes.',
                   'Existing paired parent/frame/resource models share original children, logical BIOS semantics, and Unicorn.',
                   'Physical card allocation/serial protocol, BIOS execution and physical GPU/SPU/IRQ remain outside scope.',
                   'Corrupted checksum and empty card are controlled diagnostics, not natural game histories.'])
(ROOT / 'native-title-card-summary.json').write_text(json.dumps(out, ensure_ascii=False, indent=2) + '\n')
