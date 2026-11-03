"""Native presentation save continuation and original encoder.

With native_prompt=True, enter at6DAF0 and run original66FCC with raw input;
otherwise enter6DB00 with an explicit confirmation result. Stack/entry are
fixtures in both modes, not a natural end-of-scenario playthrough. Physical
card writing is stopped before501FC. Decline preserves the old buffer, which
need not be a valid save payload.
"""
from opened_snapshot_harness_20261029 import *
from save_codec import BASE,SIZE,encode,valid
from unicorn import UC_HOOK_CODE

def make(name='TOWN0001-music',accepted=1,native_prompt=False):
    from verify_schedule_selector_frames import seq
    unit=restore(name,{0x80066fcc:[seq([32] if accepted else [0x2000,32])+[0]*100]} if native_prompt else {})
    u,runner=unit[:2];m=Memory(u);before=m.byte(0x800cd8a8);calls=[];stop=0x800501fc if accepted==1 else 0x8006db34
    initial=m.read(BASE,SIZE)
    def expected_read(a,n):
        raw=bytearray(m.read(a,n))
        if a<=0x800cd8a8<a+n:raw[0x800cd8a8-a]=255
        return bytes(raw)
    wanted=bytes(encode(bytearray(initial),expected_read)) if accepted else initial
    def observe(z,a,n,d):
        if a==stop:z.emu_stop();return
        if a==0x8006db00:
            assert z.reg_read(UC_MIPS_REG_V0)==accepted;return
        if 0x8006db00<=z.reg_read(UC_MIPS_REG_RA)<0x8006db34:calls.append(a)
    hooks=[u.hook_add(UC_HOOK_CODE,observe,begin=a,end=a) for a in (0x80065974,0x8006b81c,stop,*([0x8006db00] if native_prompt else []))]
    u.reg_write(UC_MIPS_REG_SP,0x801ffee0);u.reg_write(UC_MIPS_REG_FP,0x801ffee0);u.reg_write(UC_MIPS_REG_V0,accepted)
    u.emu_start(0x8006daf0 if native_prompt else 0x8006db00,stop,count=20000000)
    assert u.reg_read(UC_MIPS_REG_PC)==stop
    assert calls==([0x80065974,0x8006b81c] if accepted else [])
    assert m.byte(0x800cd8a8)==(255 if accepted else before)
    actual=m.read(BASE,SIZE);assert actual==wanted
    if accepted:assert valid(actual) and actual[2]==255 and u.reg_read(UC_MIPS_REG_A0)==0
    proof=dict(accepted=accepted,native_prompt=native_prompt,frames=len(runner.frames),flag_before=before,flag_after=m.byte(0x800cd8a8),calls=calls,stop_pc=hex(stop),
               payload_sha256=hashlib.sha256(actual).hexdigest(),payload_valid=valid(actual),
               limitations=__doc__.strip())
    for h in hooks:u.hook_del(h)
    for item in unit[2:6]:item.dispose()
    runner.dispose()
    return actual,proof
if __name__=='__main__':
    rows=[make(accepted=a)[1] for a in (0,1)]
    (R/'presentation-save-payload-verification-20261030.json').write_text(json.dumps(dict(all_passed=True,evidence_only_not_case_count=True,cases=rows),indent=2))
    print('native presentation continuation + native encoder passed',flush=True)
