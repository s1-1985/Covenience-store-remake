#!/usr/bin/env python3
"""Verify original actor record construction on unmodified natural play RAM."""
import hashlib
import json
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
ALGO = Path(sys.argv[1]).resolve()
sys.path.insert(0, str(ALGO))
from check_machine import UC_MIPS_REG_A0, UC_MIPS_REG_RA, EXE
from caller_connection_harness import Memory
from interior_display import overlay_staff_records
from unicorn import UC_HOOK_CODE
import verify_opened_snapshot_play_20261028 as play


class DisplayMonitor:
    def __init__(self, u, runner):
        self.rows = []
        self.pending = 0

        def observe(z, address, size, data):
            m = Memory(z)
            pointer = z.reg_read(UC_MIPS_REG_A0)
            store = m.read(pointer, 5080)
            staff = m.read(0x80143ff8, 2100)
            prior = m.read(0x800da990, 1152)
            expected, count = overlay_staff_records(prior, store, staff)
            clock = m.word(0x800cd93c)
            width, height = struct.unpack_from('<2i', store, 68)
            actors = []
            for y in range(height):
                for x in range(width):
                    word = struct.unpack_from('<I', store, 264 + y * 112 + x * 4)[0]
                    code = (word >> 12) & 1023
                    if word & 1023 or not 640 <= code < 820:
                        continue
                    shift = x + 1 < width and struct.unpack_from('<I', store, 268 + y * 112 + x * 4)[0] & 1023 != 0
                    actors.append(dict(source='grid', cell=[x, y], image=code,
                                       pixel=[x * 8 - 8 * int(shift) - 160, (y - 1) * 8 - 90],
                                       uv=[((code - 640) & 15) * 16, (code - 640) & 240],
                                       right_fixture_shift=bool(shift)))
            refs = struct.unpack_from('<3h', store, 0xdd8)
            personnel = []
            customers = []
            capacity = (10, 10, 15, 15, 20, 20)[struct.unpack_from('<i', store, 0xc70)[0]]
            for index in range(capacity):
                offset = 0xf04 + index * 32
                state = store[offset]
                if not state:
                    continue
                x, y, direction = struct.unpack_from('<3b', store, offset + 12)
                customers.append(dict(id=index, state=state, cell=[x, y], direction=direction,
                                      appearance=struct.unpack_from('<b', store, offset + 31)[0]))
            for slot in (2, 1, 0):
                index = refs[slot]
                if index == -1:
                    continue
                offset = index * 60
                appearance = struct.unpack_from('<h', staff, offset + 6)[0]
                state, x, y, direction = struct.unpack_from('<4b', staff, offset + 40)
                personnel.append(dict(slot=slot, id=index, state=state, cell=[x, y], direction=direction,
                                      appearance=appearance, appended=state == 0 and x != -1 and y != -1))
                if state == 0 and x != -1 and y != -1:
                    code = appearance * 4
                    actors.append(dict(source='resting_staff', id=index, cell=[x, y], image=code + 640,
                                       pixel=[x * 8 + 8 - 160, y * 8 - 90],
                                       uv=[(code & 15) * 16, code & 240]))
            assert len(actors) == count <= 32
            self.pending += 1

            def finish():
                actual = m.read(0x800da990, 1152)
                assert actual == expected
                assert struct.unpack('<H', m.read(0x800cda2c, 2))[0] == count
                assert m.read(pointer, 5080) == store and m.read(0x80143ff8, 2100) == staff
                records = []
                for index, actor in enumerate(actors):
                    record = actual[index * 36:(index + 1) * 36]
                    assert list(struct.unpack_from('<2h', record, 4)) == actor['pixel']
                    assert list(record[14:16]) == actor['uv']
                    records.append(record.hex())
                self.rows.append(dict(clock=clock, store_slot=(pointer - 0x8012b2f8) // 5080,
                                      actors=actors, personnel=personnel, customers=customers, count=count,
                                      records_hex=records, record_pool_sha256=hashlib.sha256(actual).hexdigest()))
                self.pending -= 1

            runner.onreturn(z.reg_read(UC_MIPS_REG_RA), finish)

        self.hook = u.hook_add(UC_HOOK_CODE, observe, begin=0x80056a3c, end=0x80056a3c)
        self.u = u

    def dispose(self):
        assert self.pending == 0
        self.u.hook_del(self.hook)


Base = play.Connection
monitors = []


class Connection(Base):
    def after_opening(self, units, runners, resources, voices):
        for u, runner in zip(units, runners):
            monitors.append(DisplayMonitor(u, runner))
        try:
            return super().after_opening(units, runners, resources, voices)
        finally:
            for monitor in monitors:
                monitor.dispose()


play.Connection = Connection
name = 'TOWN0001-ci-main-20-single'
case = sys.argv[2] if len(sys.argv) > 2 else 'second-store'
assert case in ('first-store', 'second-store')
count = 48 if case == 'first-store' else 64
if len(sys.argv) > 3:
    count = int(sys.argv[3])
assert count > 0
actions = {0: 16, 2: 32} if case == 'first-store' else {0: 16, 2: 0x4000, 4: 32}
proof = play.compare(name, count, actions=actions, native_music=True, finance_monitor=True, event_monitor=True,
                     refill_monitor=True, customer_monitor=True, whole_town_monitor=True,
                     staff_loop_monitor=True)
assert monitors[0].rows == monitors[1].rows and monitors[0].rows
exe = EXE.read_bytes()
directions = list(struct.unpack_from('<4i', exe, 0x8009940c - 0x80010000 + 2048))
result = dict(all_passed=True, snapshot=name, case=case, iterations=count, diagnostic_only=True,
              source_executable_sha256=hashlib.sha256(exe).hexdigest(),
              actions=actions, direction_image_offsets=directions, display_checks=len(monitors[0].rows),
              cases=monitors[0].rows,
              limits=['Unmodified main-20 natural play, original 56A3C and 18940 executed.',
                      'Complete 1152-byte CPU record pool, count and source state checked.',
                      'Parent comparison shares native children; SDK/GPU/SPU/IRQ boundaries modeled.',
                      'CPU coordinates and texture UVs, no GPU rasterization or measured display cadence.',
                      'Diagnostic branch does not replace the natural continuation checkpoint.'])
ROOT.mkdir(exist_ok=True)
(ROOT / (case + '-results.json')).write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
(ROOT / (case + '-play-proof.json')).write_text(json.dumps(proof, separators=(',', ':')) + '\n')
print(json.dumps({key: result[key] for key in ('all_passed', 'iterations', 'display_checks', 'direction_image_offsets')}))
