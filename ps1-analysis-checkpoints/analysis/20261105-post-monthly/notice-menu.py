#!/usr/bin/env python3
"""Observe an original menu-button request while a naturally queued notice is active."""
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
from verify_schedule_selector_frames import seq
from unicorn import UC_HOOK_CODE
import verify_opened_snapshot_play_20261028 as play

active_name = 'TOWN0001-notice-active-20261105-single'
first = play.compare('TOWN0001-ci-main-13-single', 1, native_music=True,
                     finance_monitor=True, event_monitor=True, refill_monitor=True,
                     customer_monitor=True, whole_town_monitor=True, staff_loop_monitor=True,
                     progress_snapshot=active_name, progress_file=str(ROOT / 'notice-entry-progress.json'))
snapshots = algo / 'source/opened-snapshots-20261028'
active_ram = zlib.decompress((snapshots / (active_name + '.ram.zlib')).read_bytes())
assert int.from_bytes(active_ram[0x1398b4:0x1398b8], 'little') == 1
assert int.from_bytes(active_ram[0xe3be4:0xe3be8], 'little') == 3
prior = json.loads((ROOT / 'evidence/opened-snapshot-TOWN0001-ci-main-14-single-verification-20261103.json').read_text())
assert first['steps'][0]['regions'] == prior['cases'][0]['steps'][0]['regions']
original = play.BackgroundCategoryRunner
observations = []


def factory(u, *args, **kwargs):
    runner = original(u, *args, **kwargs)
    calls = []
    observations.append(calls)
    m = Memory(u)

    def observe(z, address, size, data):
        calls.append(dict(function=hex(address), clock=m.word(0x800cd93c),
                          notice_active=m.word(0x801398b4), notice_kind=m.word(0x800e3be4)))

    runner.notice_menu_hooks = [u.hook_add(UC_HOOK_CODE, observe, begin=a, end=a)
                               for a in (0x8005fe54, 0x80062484, 0x800501fc)]
    return runner


play.BackgroundCategoryRunner = factory
output = 'TOWN0001-notice-menu-20261105-single'
second = play.compare(active_name, 4, actions={0:128}, native_music=True,
                      input_plans={0x8004e578:[seq([64]) + [0] * 150]},
                      finance_monitor=True, event_monitor=True, refill_monitor=True,
                      customer_monitor=True, whole_town_monitor=True, staff_loop_monitor=True,
                      progress_snapshot=output, progress_file=str(ROOT / 'notice-menu-progress.json'))
assert len(observations) == 2 and observations[0] == observations[1]
out = dict(all_passed=True, source_snapshot='TOWN0001-ci-main-13-single',
           active_snapshot_ram_sha256=hashlib.sha256(active_ram).hexdigest(),
           initial_notice_active=1, initial_notice_kind=3, supplied_raw_action=128,
           menu_reached=any(r['function'] == '0x8005fe54' for r in observations[0]),
           native_calls=observations[0], entry_play=first, request_play=second,
           new_natural_updates_counted=0,
           limits=['One replayed update creates the notice-active state without changing flags or timers.',
                   'Raw controller request at original SDK frame boundary, with cancel inputs available if a menu opens.',
                   'Paired parent/original comparison shares native children; existing SDK/GPU/SPU/IRQ adapters remain modeled.',
                   'This is one timed notice in town view, not all notification kinds or UI views.'])
(ROOT / 'notice-menu.json').write_text(json.dumps(out, separators=(',', ':')) + '\n')
for name in (active_name, output):
    for ext in ('.json', '.ram.zlib'):
        p = snapshots / (name + ext)
        dst = ROOT / 'notice-evidence' / p.relative_to(algo)
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(p, dst)
print(json.dumps(dict(all_passed=True, menu_reached=out['menu_reached'], calls=out['native_calls'])))
