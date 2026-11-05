#!/usr/bin/env python3
"""Replay the committed final monthly segment and capture natural rival entry/exit.

No game state or return value is supplied by this observer. The replay is not
counted again as additional natural operating updates.
"""
import hashlib
import json
import shutil
import sys
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parent
algo = Path(sys.argv[1]).resolve()
sys.path.insert(0, str(algo))
from check_machine import *
from caller_connection_harness import Memory
from unicorn import UC_HOOK_CODE
import verify_opened_snapshot_play_20261028 as play

original = play.BackgroundCategoryRunner
records = []
units = []


def capture(u, label):
    ram = bytes(u.mem_read(0, 0x200000))
    (ROOT / (label + '.ram.zlib')).write_bytes(zlib.compress(ram, 9))
    registers = list(range(UC_MIPS_REG_0, UC_MIPS_REG_31 + 1)) + [UC_MIPS_REG_HI, UC_MIPS_REG_LO, UC_MIPS_REG_PC]
    metadata = dict(label=label, ram_sha256=hashlib.sha256(ram).hexdigest(),
                    registers={str(r): u.reg_read(r) for r in registers},
                    scope='Observed original function boundary; diagnostic capture, not a normal play restart.')
    (ROOT / (label + '.json')).write_text(json.dumps(metadata, indent=2) + '\n')
    return metadata


def factory(u, *args, **kwargs):
    runner = original(u, *args, **kwargs)
    which = len(units)
    units.append(u)
    m = Memory(u)

    def observe(z, address, size, data):
        if (m.word(0x800ce610), m.word(0x800ce614), m.word(0x800ce618)) != (1, 0, 0):
            return
        assert m.word(0x800cd93c) == 17280
        label = 'rival-' + ('native' if which == 0 else 'reference')
        entry = capture(z, label + '-entry')
        row = dict(side=which, clock=17280, function=hex(address),
                   caller=hex(z.reg_read(UC_MIPS_REG_RA)), entry=entry)
        records.append(row)

        def finish():
            row['exit'] = capture(z, label + '-exit')

        runner.onreturn(z.reg_read(UC_MIPS_REG_RA), finish)

    runner.monthly_capture_hook = u.hook_add(UC_HOOK_CODE, observe, begin=0x8002a8e0, end=0x8002a8e0)
    return runner


play.BackgroundCategoryRunner = factory
name = 'TOWN0001-monthly-rival-replay-20261105-single'
try:
    row = play.compare('TOWN0001-ci-main-12-single', 200, native_music=True,
                       finance_monitor=True, event_monitor=True, refill_monitor=True,
                       customer_monitor=True, whole_town_monitor=True, staff_loop_monitor=True,
                       progress_snapshot=name, progress_file=str(ROOT / 'replay-progress.json'))
    assert len(records) == 2 and all('exit' in r for r in records)
    snapshots = algo / 'source/opened-snapshots-20261028'
    actual = zlib.decompress((snapshots / (name + '.ram.zlib')).read_bytes())
    target = zlib.decompress((snapshots / 'TOWN0001-ci-main-13-single.ram.zlib').read_bytes())
    assert actual == target
    proof = dict(all_passed=True, replay_updates=200, new_updates_counted=0,
                 final_ram_equals_committed_main13=True, final_ram_sha256=hashlib.sha256(actual).hexdigest(),
                 captures=records, play=row,
                 limits=['Observer only: no game clock, RNG, cash, staff or function-return injections.',
                         'Paired original execution/parent comparison shares native child routines and Unicorn.',
                         'Existing SDK/BIOS/GPU/SPU/IRQ boundaries remain modeled.'])
    (ROOT / 'monthly-replay.json').write_text(json.dumps(proof, separators=(',', ':')) + '\n')
    for ext in ('.json', '.ram.zlib'):
        p = snapshots / (name + ext)
        dst = ROOT / 'replay-evidence' / p.relative_to(algo)
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(p, dst)
    print(json.dumps(dict(all_passed=True, captures=len(records), final_ram_equals_main13=True)), flush=True)
finally:
    (ROOT / 'monthly-capture-status.json').write_text(json.dumps(records, indent=2) + '\n')
