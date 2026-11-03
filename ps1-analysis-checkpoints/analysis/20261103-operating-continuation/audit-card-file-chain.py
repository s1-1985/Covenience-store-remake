#!/usr/bin/env python3
"""Original encode -> logical card file -> read -> decode and title boundary handoff."""
import hashlib,json,runpy,struct,sys,zlib
from pathlib import Path

def sha(b):return hashlib.sha256(b).hexdigest()
def main():
    algo=Path(sys.argv[1]).resolve();names=sys.argv[2:];assert names
    root=Path(__file__).resolve().parent
    module=runpy.run_path(str(root.parent/"20261103-native-file-recovery/native-file-analysis.py"),run_name="card_chain_reference")
    sys.path.insert(0,str(algo))
    from check_machine import machine,EXE
    from unicorn.mips_const import UC_MIPS_REG_SP,UC_MIPS_REG_FP,UC_MIPS_REG_GP,UC_MIPS_REG_RA,UC_MIPS_REG_PC
    from save_codec import BASE,SIZE,FIELDS,encode,valid
    import verify_title_native_load_20261029 as title
    dest=algo/"source/card-file-chain-20261103-ci";dest.mkdir(exist_ok=True)
    exe=EXE.read_bytes();files={};rows=[]
    for number,name in enumerate(names):
        snapshots=algo/"source/opened-snapshots-20261028"
        meta=json.loads((snapshots/(name+".json")).read_text());ram=zlib.decompress((snapshots/(name+".ram.zlib")).read_bytes())
        assert sha(ram)==meta["ram_sha256"]
        read=lambda address,size:ram[address&0x1fffffff:(address&0x1fffffff)+size]
        expected=bytes(encode(bytearray(read(BASE,SIZE)),read))
        unit=machine();unit.mem_write(0,ram)
        for register,value in ((UC_MIPS_REG_SP,0x801d0000),(UC_MIPS_REG_FP,0x801d0000),
                               (UC_MIPS_REG_GP,0x800cd6c4),(UC_MIPS_REG_RA,0x80000080)):unit.reg_write(register,value)
        unit.emu_start(0x8006b81c,0x80000080,count=15000000);assert unit.reg_read(UC_MIPS_REG_PC)==0x80000080
        body=bytes(unit.mem_read(BASE&0x1fffffff,114176));assert body[:SIZE]==expected and valid(expected)
        c=module["Cpu"](exe);c.mem[:]=bytes(unit.mem_read(0,0x200000));env=module["LogicalFiles"](c,files)
        assert c.read(0x800cd768,4)==struct.pack("<I",BASE)
        seed=c.read(0x800d6270,4);calls=[]
        for function in (0x8007adf8,0x8007ab2c):
            if function==0x8007ab2c:c.write(BASE,b"\xcc"*114176)
            for mode in (0,1):
                result=c.run(function,[mode],limit=1000000,stack_pointer=0x801d0000,global_pointer=0x800cd6c4)
                assert result==0
                calls.append(dict(function=hex(function),mode=mode,return_value=result,steps=c.steps))
        assert c.read(BASE,114176)==body and c.read(0x800d6270,4)==seed
        saved=bytes(env.files[module["PATH"]]);assert saved[512:]==body and len(saved)==114688
        if rows:assert saved[:512]==previous_header
        previous_header=saved[:512];files=env.files
        payload=c.read(BASE,SIZE);assert payload==expected and valid(payload)
        # Corrupt only the documented decode destinations, leaving payload intact.
        for offset,address,size in FIELDS:c.write(address,b"\xcc"*size)
        result=c.run(0x8006bc40,[],limit=1000000,stack_pointer=0x801d0000,global_pointer=0x800cd6c4)
        assert all(c.read(address,size)==payload[offset:offset+size] for offset,address,size in FIELDS)
        assert c.read(0x800d6270,4)==seed
        title.payload=lambda requested,payload=payload,name=name: payload if requested==name else (_ for _ in ()).throw(AssertionError(requested))
        loaded=title.compare("success",name,audit_runtime_tables=True)
        assert loaded["payload_sha256"]==sha(payload) and loaded["payload_valid"]
        assert loaded["runtime_tables_preserved_after_resume"]["both_cpus"]
        native_file=name+".card-file.bin";payload_file=name+".payload.bin";trace_file=name+".io.json";title_file=name+".title.json"
        (dest/native_file).write_bytes(saved);(dest/payload_file).write_bytes(payload)
        (dest/trace_file).write_text(json.dumps(env.io,separators=(",",":"))+"\n")
        (dest/title_file).write_text(json.dumps(loaded,separators=(",",":"))+"\n")
        writes=[r for r in env.io if r["op"]=="write" and r["requested"]==128]
        reads=[r for r in env.io if r["op"]=="read" and r["requested"]==128]
        for transfers in (writes,reads):
            assert len(transfers)==892 and [r["file_offset"] for r in transfers]==list(range(512,114688,128))
            assert all(r["requested"]==r["result"]==128 for r in transfers)
        rows.append(dict(snapshot=name,source_ram_sha256=meta["ram_sha256"],clock=struct.unpack_from("<I",ram,0xcd93c)[0],
                         passed=True,operation="create" if number==0 else "overwrite",calls=calls,
                         native_file=native_file,file_sha256=sha(saved),payload_file=payload_file,payload_sha256=sha(payload),
                         body_sha256=sha(body),tail_sha256=sha(body[SIZE:]),tail_origin="original encoder CPU RAM; no synthetic tail pattern",
                         header_sha256=sha(saved[:512]),body_writes=len(writes),body_reads=len(reads),
                         decoded_regions=len(FIELDS),rng_preserved=True,title_frames=len(loaded["frames"]),title_proof=title_file,
                         runtime_tables=loaded["runtime_tables_preserved_after_resume"]))
        print("Original encoded card file and title handoff passed "+name,flush=True)
    output=dict(all_passed=True,total=len(rows),cases=rows,source_exe_sha256=sha(exe),
                limits=["CPU snapshot -> original encoder -> original logical file writer/reader -> original decoder; original game fields are not synthesized.",
                        "BIOS file/event boundaries are a logical model. Physical allocation and serial card transport are outside proof.",
                        "Decoded destinations are deliberately corrupted in this diagnostic before original decode; this is not part of the natural gameplay trajectory.",
                        "The exact file-read payload is handed to the pre-existing title read boundary. This does not prove a continuous title-to-card-driver native call stack.",
                        "Original title/load/play resources and runtime table audit execute as in the unchanged archived harness."])
    (dest/"summary.json").write_text(json.dumps(output,ensure_ascii=False,indent=2)+"\n")
if __name__=="__main__":main()
