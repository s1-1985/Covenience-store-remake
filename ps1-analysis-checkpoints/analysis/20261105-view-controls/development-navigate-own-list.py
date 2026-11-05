#!/usr/bin/env python3
"""Drive the original town/list/interior controls from the latest real play state."""
import hashlib
import json
import shutil
import sys
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parent
algo = Path(sys.argv[1]).resolve()
case = sys.argv[2]
assert case in ('own', 'rival')
folder = ROOT / case
folder.mkdir(exist_ok=True)
sys.path.insert(0, str(algo))
from check_machine import *
from caller_connection_harness import Memory
from unicorn import UC_HOOK_CODE
import verify_opened_snapshot_play_20261028 as play

original = play.BackgroundCategoryRunner
observations = []


def factory(u, *args, **kwargs):
    runner = original(u, *args, **kwargs)
    m = Memory(u)
    calls = []
    observations.append(calls)

    def observe(z, address, size, data):
        item = dict(function=hex(address), clock=m.word(0x800cd93c), view=m.word(0x800cd97c),
                    selected=m.word(0x8013796c), list_row=int.from_bytes(m.read(0x800cd99c,2),'little'),
                    processed_input=m.word(0x800cd884))
        if address == 0x80062a4c:
            item['requested_view'] = z.reg_read(UC_MIPS_REG_A0)
            item['requested_slot'] = z.reg_read(UC_MIPS_REG_A1)
        calls.append(item)

    runner.view_control_hooks = [u.hook_add(UC_HOOK_CODE, observe, begin=a, end=a)
                                 for a in (0x8005fe54,0x8005f500,0x80062a4c,0x80060418)]
    return runner


play.BackgroundCategoryRunner = factory
actions = {0:16,2:0x4000,4:32,6:128} if case == 'own' else {0:16,2:0x4000,4:0x4000,6:32,8:128}
count = 10 if case == 'own' else 12
name = 'TOWN0001-view-' + case + '-20261105-single'
try:
    row = play.compare('TOWN0001-ci-main-15-single', count, actions=actions, operation=True, native_music=True,
                       finance_monitor=True,event_monitor=True,refill_monitor=True,
                       customer_monitor=True,whole_town_monitor=True,staff_loop_monitor=True,
                       operation_parent_monitor=True,progress_snapshot=name,
                       progress_file=str(folder/'progress.json'))
    assert len(observations) == 2 and observations[0] == observations[1]
    meta_path = algo/'source/opened-snapshots-20261028'/(name+'.json')
    ram_path = meta_path.with_name(name+'.ram.zlib')
    ram = zlib.decompress(ram_path.read_bytes())
    meta = json.loads(meta_path.read_text())
    assert hashlib.sha256(ram).hexdigest() == meta['ram_sha256']
    selected = int.from_bytes(ram[0x13796c:0x137970],'little')
    flags = None if selected >= 10 else int.from_bytes(ram[0x12b2f8+selected*5080+4:0x12b2f8+selected*5080+6],'little')
    out = dict(all_passed=True,case=case,actions=actions,play=row,calls=observations[0],
               final_selected=selected,final_store_flags=flags,
               final_view=int.from_bytes(ram[0xcd97c:0xcd980],'little'),
               new_natural_updates_counted=0,
               limits=['Original raw-controller input streams at the archived SDK frame boundaries.',
                       'No cursor/selection/view/owner/clock/RNG injection; operation menus receive cancel-only input.',
                       'Paired parent and reached models share original child routines and Unicorn.',
                       'Graphics/audio/IRQ SDK boundaries remain modeled; no physical-screen claim.'])
    (folder/'result.json').write_text(json.dumps(out,separators=(',',':'))+'\n')
    for p in (meta_path,ram_path):
        dst=folder/'evidence'/p.relative_to(algo);dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dst)
    print(json.dumps(dict(all_passed=True,case=case,final_view=out['final_view'],selected=selected,flags=flags)),flush=True)
finally:
    (folder/'call-trace.json').write_text(json.dumps(observations,indent=2)+'\n')
