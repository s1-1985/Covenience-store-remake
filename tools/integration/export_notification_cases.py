"""Export independent recovered-model fixtures; original EXE is not needed.

Usage: python tools/integration/export_notification_cases.py ALGORITHM_ANALYSIS
Source: analysis 2c00ba53, event_queue.py and notification_display.py.
"""
import hashlib
import json
from pathlib import Path
import random
import sys

sys.path.insert(0, sys.argv[1])
from event_queue import reserve, consume, reset
from notification_display import control

root = Path(__file__).resolve().parents[2]
rng = random.Random(20261106)
cases = []
addresses = [0x801398b0, 0x801398b4, 0x801398b8, 0x800e3be4,
             0x800e3be8, 0x800cd7ec, 0x800e3c28, 0x800e3c2c,
             0x800da974, 0x800da978, 0x800e36a8, 0x800e36ac,
             0x800cd930, 0x800cd948, 0x800cd8a0, 0x800cd9b4]
for case in range(96):
    queue = bytearray((i * 7 + case) & 255 for i in range(8000))
    occupied = [slot for slot in range(50) if case % 8 == 0 or slot % 5 == 0]
    for slot in range(50):
        queue[slot * 160] = int(slot in occupied)
    kind = [-1, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 99][case % 12]
    mode = [1, 2, 3, 5, -1, 261, 0, 4][case // 12]
    sound = [-2, -1, 28, 100, 101, 119, 110, 102][case % 8]
    body = bytes((i + case * 3) & 255 for i in range(120))
    args = [kind, case - 40, sound, mode, case + 200]
    slot = reserve(queue, *args, body)
    reserve_hash = hashlib.sha256(queue).hexdigest()
    # Remove pre-existing notices so consuming tests the newly reserved one.
    for j in occupied:
        queue[j * 160] = 0
    state = {a: rng.getrandbits(32) for a in addresses}
    state[0x801398b4] = 0 if case % 3 else 2
    state[0x800cd948] = case % 4
    state[0x800e3c28] = 0x80000000 if case % 5 == 0 else rng.getrandbits(32)
    state[0x800e36a8] = 0x80000000 if case % 7 == 0 else 20000
    state[0x800e36ac] = 0
    before = state.copy()
    old_text = bytes([17] * 120)
    stores = [dict(active=1, flags=0, annual_sales=70000000, rating=90)] * (1 + case % 10)
    clock = [0, 5759, 5760, 11520, 69120][case % 5]
    text, sounds, consumed = consume(queue, state, old_text, clock, stores, 20000)
    cases.append(dict(case=case, occupied=occupied, args=args, slot=slot,
        reserve_sha256=reserve_hash, clock=clock, initial_state=before,
        stores=stores, state=state, consumed=consumed, sounds=sounds,
        queue_sha256=hashlib.sha256(queue).hexdigest(), text=list(text)))
display_cases = []
import itertools
for active, kind, mode, audio, view in itertools.product(
        [0, 1, 2, 0xffffffff], [0, 3, 7, 8], [-1, 1, 2, 3, 5],
        [(0, 0), (0, 1), (1, 1), (0, 0x80000000)], [0, 1]):
    x, y = (32760, 65530) if len(display_cases) % 2 else (56, 104)
    args = [active, 240, *audio, kind, mode, view, x, y]
    after_active, timer, outcome, calls = control(*args)
    display_cases.append(dict(args=args, active=after_active, timer=timer,
                              outcome=outcome, calls=calls))
output = dict(source="analysis 2c00ba53: event_queue.py / notification_display.py",
              cases=cases, display_cases=display_cases)
(root / 'game/tests/fixtures/source_notifications.json').write_text(
    json.dumps(output, separators=(',', ':')) + '\n')
print(f'Exported {len(cases)} reservation/consume and {len(display_cases)} display cases')
