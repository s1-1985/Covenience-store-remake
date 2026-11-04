#!/usr/bin/env python3
"""Isolated daily-close threshold probes on a copy of the saved operating RAM.

This deliberately calls 29334 again on a cloned post-close state. It is a
controlled function probe, not another natural daily close or operating day.
"""
import hashlib
import json
import struct
import sys
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parent
algo, snapshot = (Path(p).resolve() for p in sys.argv[1:3])
sys.path.insert(0, str(algo))
from check_machine import *
from source_finance_monitor_20261029 import SourceFinanceMonitor
from unicorn import UC_HOOK_CODE


class Returns:
    def __init__(self):
        self.callbacks = {}

    def onreturn(self, address, callback):
        self.callbacks.setdefault(address, []).append(callback)

    def flush(self, address):
        while self.callbacks.get(address):
            self.callbacks[address].pop()()


meta = json.loads(snapshot.with_suffix('.json').read_text())
ram = zlib.decompress(snapshot.with_suffix('.ram.zlib').read_bytes())
assert hashlib.sha256(ram).hexdigest() == meta['ram_sha256']
assert hashlib.sha256(EXE.read_bytes()).hexdigest() == meta['source_executable_sha256']
assert struct.unpack_from('<I', ram, 0xcd93c)[0] == 14400
# Ensure the diagnostic starts on an ordinary daily, rather than monthly, close.
assert struct.unpack_from('<5I', ram, 0xce608) == (1, 3, 3, 0, 0)
assert struct.unpack_from('<i', ram, 0xcd8b8)[0] == 0
cases = [
    ('baseline', {}, False),
    ('cash_below_debit', {0xcd9f8: 43471}, True),
    ('cash_equals_debit', {0xcd9f8: 43472}, False),
    ('cash_above_debit', {0xcd9f8: 43473}, False),
    ('rival_negative_cash', {0xcd9fc: 0}, False),
    ('year_98', {0xce608: 98}, False),
    ('year_99', {0xce608: 99}, True),
    ('year_100', {0xce608: 100}, True),
    ('year_signed_negative', {0xce608: 0xffffffff}, False),
    ('serial_98', {0xcd9e0: 98}, False),
    ('serial_99', {0xcd9e0: 99}, True),
    ('serial_100', {0xcd9e0: 100}, True),
    ('serial_signed_32767', {0xcd9e0: 32767}, True),
    ('serial_signed_32768', {0xcd9e0: 32768}, False),
    ('serial_signed_65535', {0xcd9e0: 65535}, False),
    ('gate_a_skips_negative_cash', {0xcd9f8: 0xffffffff, 0xce614: 1}, False),
    ('gate_b_skips_year_limit', {0xce608: 99, 0xce618: 1}, False),
]
rows = []
for name, changes, ending in cases:
    u = machine()
    u.mem_write(0, ram)
    u.reg_write(UC_MIPS_REG_SP, 0x801ff000)
    u.reg_write(UC_MIPS_REG_FP, 0x801ff000)
    u.reg_write(UC_MIPS_REG_GP, 0x800cd6c4)
    for address, value in changes.items():
        size = 2 if address == 0xcd9e0 else 4
        u.mem_write(address, value.to_bytes(size, 'little'))
    # Sentinel makes termination writes observable even when checking bad cash.
    put(u, 0xcd9b4, 7)
    before_cash = list(struct.unpack('<2i', u.mem_read(0xcd9f8, 8)))
    before_scenario = bytes(u.mem_read(0xcd948, 1))[0]
    returns = Returns()
    monitor = SourceFinanceMonitor(u, returns)
    calls = []

    def external(z, address, size, data):
        calls.append(hex(address))
        z.reg_write(UC_MIPS_REG_V0, 0)
        z.reg_write(UC_MIPS_REG_PC, z.reg_read(UC_MIPS_REG_RA))

    for address in (0x80062a4c, 0x8008eaec, 0x80041a08, 0x8006d204, 0x8006ce14, 0x8006d758):
        u.hook_add(UC_HOOK_CODE, external, begin=address, end=address)
    u.reg_write(UC_MIPS_REG_RA, 0x80001000)
    u.emu_start(0x80029334, 0x80001000, count=3000000)
    assert u.reg_read(UC_MIPS_REG_PC) == 0x80001000
    returns.flush(0x80001000)
    monitor.dispose()
    after_cash = list(struct.unpack('<2i', u.mem_read(0xcd9f8, 8)))
    final_state = get(u, 0xcd9b4)
    scenario = bytes(u.mem_read(0xcd948, 1))[0]
    gated = bool(changes.get(0xce614, 0) or changes.get(0xce618, 0))
    assert after_cash == (before_cash if gated else [before_cash[0] - 43472, before_cash[1] - 26976])
    assert final_state == (4 if ending else 7)
    assert scenario == (255 if ending else before_scenario)
    assert len(monitor.checks) == (0 if gated else 1)
    assert monitor.time_gates == int(gated)
    rows.append(dict(name=name, controlled_changes={hex(a): v for a, v in changes.items()},
                     cash_before=before_cash, cash_after=after_cash, ending=ending,
                     state_after=final_state, scenario_after=scenario, time_gated=gated,
                     finance_checks=monitor.checks, external_calls=calls,
                     final_ram_sha256=hashlib.sha256(bytes(u.mem_read(0, 0x200000))).hexdigest()))
out = dict(all_passed=True, total=len(rows), snapshot=snapshot.name,
           source_ram_sha256=meta['ram_sha256'], source_executable_sha256=meta['source_executable_sha256'],
           cases=rows, limits=[
               'Synthetic isolated re-invocations on copied post-close RAM; not natural new days.',
               'Original finance code and game children with existing independent finance monitor.',
               'Six named UI/audio/text endpoints are nonmutating zero-return hooks if reached.',
               'Both branches use the shared Unicorn execution engine; no independent CPU claim.',
               'Signed negative year/serial inputs are type-boundary diagnostics, not reachable player actions.'])
(ROOT / 'finance-boundaries.json').write_text(json.dumps(out, ensure_ascii=False, indent=2) + '\n')
print(json.dumps(dict(all_passed=True, total=len(rows))))
