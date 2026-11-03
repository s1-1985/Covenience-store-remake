#!/usr/bin/env python3
"""Differentially check saved controlled inputs with two separate MIPS engines."""
import hashlib,json,runpy,struct,sys
from pathlib import Path
from unicorn import Uc,UC_ARCH_MIPS,UC_MODE_MIPS32,UC_MODE_LITTLE_ENDIAN,UC_HOOK_CODE
from unicorn import mips_const as reg
import zipfile,zlib

def sha(b):return hashlib.sha256(b).hexdigest()
def main():
    root=Path(__file__).resolve().parent;balance=root.parent/"20261103-town-balance"
    previous=sys.argv[:];sys.argv=[str(balance/"balance-analysis.py"),sys.argv[1]]
    try:module=runpy.run_path(str(balance/"balance-analysis.py"),run_name="engine_crosscheck_model")
    finally:sys.argv=previous
    with zipfile.ZipFile(sys.argv[1]) as archive:
        exe=archive.read("algorithm-analysis/source/SLPS_007.82");ram=zlib.decompress(archive.read(module["SOURCE_RAM"]))
    rows=[]
    for proof_path in sorted((balance/"results").glob("*.json")):
        proof=json.loads(proof_path.read_text());assert proof["all_checks_passed"]
        controls=proof["controls"];c=module["BaseCpu"](exe);c.mem[:]=ram
        c.write(module["SEED"],struct.pack("<I",controls["seed"]&0xffffffff))
        for j in range(3000):
            a=module["TOWN"]+j*8
            if "level" in controls:c.write(a+2,bytes([controls["level"]]))
            if c.read(a+4,1)[0] in controls["empty_categories"]:c.write(a+6,b"\xff\xff")
        whole=bool(controls.get("whole"))
        if whole:
            for a,v in ((0x800ce618,0),(0x800ce614,0),(0x800ce610,1)):c.write(a,struct.pack("<I",v))
            entry,stop=0x8002bd54,0x80000080
            fp=0
        else:
            entry,stop=0x8002d1cc,0x8002d770;fp=0x801d0000-0xc48;c.write(fp,bytes(0xc48))
        c.r=[0]*32;c.r[28]=0x800cd6c4;c.r[29]=0x801d0000 if whole else fp;c.r[30]=fp;c.r[31]=0x80000080
        c.pc=entry;c.npc=entry+4;c.pending_load=None;c.steps=0
        initial=bytes(c.mem);u=Uc(UC_ARCH_MIPS,UC_MODE_MIPS32|UC_MODE_LITTLE_ENDIAN);u.mem_map(0,0x200000);u.mem_write(0,initial)
        for i in range(32):u.reg_write(getattr(reg,"UC_MIPS_REG_"+str(i)),c.r[i])
        u.reg_write(reg.UC_MIPS_REG_HI,0);u.reg_write(reg.UC_MIPS_REG_LO,0)
        def text_hook(z,a,n,d):z.reg_write(reg.UC_MIPS_REG_PC,z.reg_read(reg.UC_MIPS_REG_RA))
        if whole:
            for a in (0x8006d204,0x8006d3f8):u.hook_add(UC_HOOK_CODE,text_hook,begin=a,end=a)
        while c.pc!=stop:
            if c.steps>=30000000:raise TimeoutError(hex(c.pc))
            if whole and c.pc in (0x8006d204,0x8006d3f8):
                assert c.pending_load is None;c.pc=c.r[31];c.npc=c.pc+4;c.steps+=1
            else:c.step()
        u.emu_start(entry,stop,count=30000000);assert u.reg_read(reg.UC_MIPS_REG_PC)==stop
        actual=bytes(u.mem_read(0,0x200000));expected=bytes(c.mem)
        differences=[i for i in range(32) if u.reg_read(getattr(reg,"UC_MIPS_REG_"+str(i)))!=c.r[i]]
        assert actual==expected,(proof["case"],"RAM",[(hex(i),a,b) for i,(a,b) in enumerate(zip(actual,expected)) if a!=b][:10])
        assert not differences,(proof["case"],"registers",differences)
        assert u.reg_read(reg.UC_MIPS_REG_HI)==c.hi and u.reg_read(reg.UC_MIPS_REG_LO)==c.lo
        assert sha(expected)==proof["output_ram_sha256"]
        rows.append(dict(case=proof["case"],seed=controls["seed"],mode=proof["mode"],passed=True,
                         input_ram_sha256=sha(initial),output_ram_sha256=sha(actual),limited_engine_steps=c.steps,
                         full_ram_bytes_compared=len(actual),gpr_registers_compared=32,hi_lo_compared=True,
                         existing_model_proof=str(proof_path.relative_to(root.parent)),existing_proof_sha256=sha(proof_path.read_bytes())))
        print("Two engines agree: "+proof["case"]+" seed "+str(controls["seed"]),flush=True)
    assert len(rows)==33
    out=dict(all_passed=True,total_cases=len(rows),unicorn_version=__import__("unicorn").__version__,cases=rows,
             source_exe_sha256=sha(exe),limits=["Same explicitly controlled input in both MIPS engines; no added natural gameplay cases.",
             "Full 2 MiB RAM, all 32 GPRs and HI/LO compared after each original routine/slice.",
             "The two documented text endpoints are skipped on whole-function cases, preserving V0 in both engines.",
             "Instruction-step counts are not physical PS1 timing or GPU/SPU/IRQ proof."])
    (root/"mips-engine-crosscheck.json").write_text(json.dumps(out,indent=2)+"\n")
if __name__=="__main__":main()
