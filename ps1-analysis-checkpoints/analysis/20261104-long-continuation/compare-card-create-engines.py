"""Attach a strict-MIPS vs Unicorn whole-card-create comparison at native entry.

Only used with the low-stack profile, so both engines use strict 2MB RAM.
No RAM-mirror implementation or hardware startup configuration is shared here.
"""
import hashlib
import runpy
import json
import zlib
from pathlib import Path
from unicorn import UC_HOOK_CODE
from unicorn.mips_const import UC_MIPS_REG_0, UC_MIPS_REG_31, UC_MIPS_REG_HI, UC_MIPS_REG_LO, UC_MIPS_REG_SP, UC_MIPS_REG_RA


def attach(u, runner, bridge, exe, output):
    path = Path(__file__).resolve().parent.parent / '20261103-native-file-recovery/native-file-analysis.py'
    module = runpy.run_path(str(path), run_name='create_engine_reference')
    def entry(z, address, size, data):
        ram = bytes(z.mem_read(0, 2097152))
        cpu = module['Cpu'](exe)
        cpu.mem[:] = ram
        env = module['LogicalFiles'](cpu, bridge.env.files)
        env.next_fd = bridge.env.next_fd
        assert not bridge.env.fds
        assert bytes(cpu.mem) == ram
        # Both engines execute the ordinary MIPS memcpy leaf, not a Python copy.
        del cpu.hooks[0x8007e57c]
        # The archived Unicorn VSync adapter runs the original input callback.
        # Predict its five input words with the prior independent model rather
        # than treating wait as a nonmutating return or copying native results.
        from input_control import interrupt, GP
        def wait_with_input(c):
            addresses = (GP + 4, GP + 8, 0x800cd9d8, 0x800cd7e0, 0x801398b8)
            state = {a: int.from_bytes(c.read(a, 4), 'little') for a in addresses}
            interrupt(state, state[0x800cd9d8])
            for a, value in state.items():
                c.write(a, value.to_bytes(4, 'little'))
            return 0
        cpu.hooks[0x80089ca4] = wait_with_input
        cpu.r = [z.reg_read(k) for k in range(UC_MIPS_REG_0, UC_MIPS_REG_31 + 1)]
        cpu.hi, cpu.lo = z.reg_read(UC_MIPS_REG_HI), z.reg_read(UC_MIPS_REG_LO)
        cpu.pc, cpu.npc = address, address + 4
        cpu.pending_load = None
        return_pc = z.reg_read(UC_MIPS_REG_RA)
        io_start = len(bridge.env.io)
        while cpu.pc != return_pc:
            assert cpu.steps < 1000000
            if cpu.pc in cpu.hooks:
                assert cpu.pending_load is None
                cpu.r[2] = cpu.hooks[cpu.pc](cpu) & 0xffffffff
                cpu.pc, cpu.npc = cpu.r[31], (cpu.r[31] + 4) & 0xffffffff
                cpu.steps += 1
            else:
                cpu.step()
        def finish():
            actual = bytes(z.mem_read(0, 2097152))
            if actual != bytes(cpu.mem):
                root = Path(__file__).resolve().parent
                changes = [dict(address=hex(i), native=x, strict=y) for i, (x, y) in enumerate(zip(actual, cpu.mem)) if x != y]
                (root / 'create-engine-mismatch.json').write_text(json.dumps(dict(total=len(changes), changes=changes,
                    native_registers=[z.reg_read(k) for k in range(UC_MIPS_REG_0, UC_MIPS_REG_31 + 1)],
                    strict_registers=cpu.r, io_equal=bridge.env.io[io_start:]==env.io), indent=2)+'\n')
                (root / 'create-engine-input.ram.zlib').write_bytes(zlib.compress(ram,9))
                (root / 'create-engine-native.ram.zlib').write_bytes(zlib.compress(actual,9))
                (root / 'create-engine-strict.ram.zlib').write_bytes(zlib.compress(bytes(cpu.mem),9))
            assert actual == bytes(cpu.mem), 'whole create RAM mismatch'
            assert cpu.r == [z.reg_read(k) for k in range(UC_MIPS_REG_0, UC_MIPS_REG_31 + 1)], 'whole create register mismatch'
            assert (cpu.hi, cpu.lo) == (z.reg_read(UC_MIPS_REG_HI), z.reg_read(UC_MIPS_REG_LO))
            assert bridge.env.files == env.files and bridge.env.io[io_start:] == env.io
            output.append(dict(all_passed=True, function=hex(address), stack=hex(cpu.r[29]),
                               strict_mips_instructions=cpu.steps, full_ram_bytes=2097152,
                               input_ram_sha256=hashlib.sha256(ram).hexdigest(),
                               output_ram_sha256=hashlib.sha256(actual).hexdigest(),
                               all_32_registers_equal=True, hi_lo_equal=True,
                               sdk_wait_scope='Existing independent five-word input callback model; native side runs original1310C through archived VSync adapter.',
                               entire_file_bytes_equal=True, io_events_equal=len(env.io)))
        runner.onreturn(return_pc, finish)
    return u.hook_add(UC_HOOK_CODE, entry, begin=0x8007b8a4, end=0x8007b8a4)
