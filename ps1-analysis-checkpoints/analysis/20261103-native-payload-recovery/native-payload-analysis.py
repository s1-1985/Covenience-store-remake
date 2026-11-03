
"""Re-run original save-payload routines using the saved limited MIPS interpreter.

No output files are written. This is not a card-file or physical PS1 test.
Inputs are the two real payload files preserved inside the r2 archive.
"""
import argparse
import hashlib
import json
from pathlib import Path
import runpy
import struct
import zipfile

BASE=0x80187e00
CHECKSUM=0x197a8
SIZE=CHECKSUM+4
RNG=0x800d6270
FIELDS=[(0,0x800cd948,1),(1,0x800cd8a0,1),(2,0x800cd8a8,1),
(4,0x8012b2c8,40),(0x2c,0x800cd8d0,2),(0x30,0x800cd93c,4),
(0x35,0x800cd8a9,1),(0x36,0x800cd834,1),(0x37,0x800cd836,1),
(0x38,0x800cd835,1),(0x3c,0x800cd9f8,4),(0x40,0x800cd9fc,4),
(0x44,0x800cd9a8,4),(0x48,0x800cd9a0,4),(0x4c,0x80137968,0x1f58),
(0x1fa4,0x800cd98c,1),(0x1fa5,0x800cd8dc,1),(0x1fa8,0x800cd89c,4),
(0x1fac,0x801398f0,24000),(0x7d6c,0x800cd904,4),(0x7d70,0x800cd994,1),
(0x7d72,0x800cd9e0,2),(0x7d74,0x800cd9e2,2),(0x7d78,0x800e3c00,32),
(0x7d98,0x80143ff8,2100),(0x85cc,0x800e3688,10),(0x85d8,0x800cd930,4),
(0x85dc,0x800df080,32),(0x85fc,0x800da970,32),(0x861c,0x800d8f68,32),
(0x863c,0x800e36a8,240),(0x872c,0x800e3c28,240),(0x881c,0x800e43d0,60),
(0x8858,0x8012b2f8,50800),(0x14ec8,0x800cda00,4),(0x14ecc,0x800cd8b8,4),
(0x14ed0,0x8013f6c0,0x48d8)]
EXE_HASH="d6a167a1c9e0fe98d7e44e12968caa489ac3eb7ed3b9e46012a188af8432b1fd"

def sha(data):
    return hashlib.sha256(data).hexdigest()

def valid(data):
    return sum(data[:CHECKSUM])==struct.unpack_from("<I",data,CHECKSUM)[0]

def verify_codec(exe,payloads,Cpu):
    if sha(exe)!=EXE_HASH:raise ValueError("EXE mismatch")
    records=[]
    for path,payload in payloads:
        assert len(payload)==SIZE and valid(payload)
        cpu=Cpu(exe)
        for off,address,size in FIELDS:cpu.write(address,payload[off:off+size])
        cpu.write(BASE,payload)
        cpu.write(RNG,struct.pack("<I",0xdeadbeef))
        cpu.run(0x8006b81c,limit=15000000)
        encoded=cpu.read(BASE,SIZE)
        assert encoded==payload and cpu.read(RNG,4)==struct.pack("<I",0xdeadbeef)
        for off,address,size in FIELDS:assert cpu.read(address,size)==payload[off:off+size]
        encoder_steps=cpu.steps
        for off,address,size in FIELDS:cpu.write(address,bytes([0xcc])*size)
        cpu.run(0x8006bc40,limit=15000000)
        restored=[]
        for off,address,size in FIELDS:
            actual=cpu.read(address,size)
            assert actual==payload[off:off+size]
            restored.append(dict(payload_offset=off,ram=hex(address),bytes=size,sha256=sha(actual)))
        assert cpu.read(BASE,SIZE)==payload and cpu.read(RNG,4)==struct.pack("<I",0xdeadbeef)
        decoder_steps=cpu.steps
        variants=[("valid",payload)]
        for label,offset in [("data_bit_flip",0x3c),("retained_padding_bit_flip",3),("checksum_bit_flip",CHECKSUM)]:
            changed=bytearray(payload);changed[offset]^=1
            variants.append((label,bytes(changed)))
        # Preserve additive checksum without recomputing it.
        a=0x3c
        b=next(i for i in range(64) if payload[i]!=payload[a])
        swapped=bytearray(payload);swapped[a],swapped[b]=swapped[b],swapped[a]
        variants.append(("byte_swap_preserving_sum",bytes(swapped)))
        gates=[]
        for label,changed in variants:
            cpu.write(BASE,changed)
            cpu.write(RNG,struct.pack("<I",0xdeadbeef))
            got=cpu.run(0x8005188c,limit=15000000)
            expected=0 if valid(changed) else -1
            assert got==expected,(path,label,got,expected)
            assert cpu.read(BASE,SIZE)==changed and cpu.read(RNG,4)==struct.pack("<I",0xdeadbeef)
            gates.append(dict(case=label,return_value=got,steps=cpu.steps,sha256=sha(changed),
                              patches=[dict(offset=i,old=payload[i],new=changed[i]) for i in range(SIZE) if payload[i]!=changed[i]]))
        # Decode does not perform its caller's checksum validation.
        corrupt=variants[1][1]
        assert not valid(corrupt)
        cpu.write(BASE,corrupt)
        cpu.run(0x8006bc40,limit=15000000)
        for off,address,size in FIELDS:assert cpu.read(address,size)==corrupt[off:off+size]
        assert cpu.read(BASE,SIZE)==corrupt
        records.append(dict(source_path=path,source_sha256=sha(payload),source_checksum=struct.unpack_from("<I",payload,CHECKSUM)[0],
                            encoder_steps=encoder_steps,decoder_steps=decoder_steps,restored_regions=restored,
                            gate_variants=gates,invalid_checksum_decode_still_copies=True))
    return dict(scope="Original instructions executed using limited interpreter; RAM inputs reconstructed from real saved payloads, not a restored full running CPU",
                source_exe_sha256=EXE_HASH,payload_bytes=SIZE,checksum_target_bytes=CHECKSUM,
                counts=dict(payloads=len(records),encode=len(records),decode_valid=len(records),
                            gate_cases=sum(len(r["gate_variants"]) for r in records),decode_invalid=len(records)),
                rng_preserved=True,records=records,all_checks_passed=True,
                limitations=["No physical memory card, BIOS, GPU/SPU/IRQ or full title/game roundtrip.",
                             "The 37 source/destination fields are initialized from payloads or poisoned for these tests; these RAM states are controlled.",
                             "The acceptance gate checks an additive checksum; passing it does not prove semantic validity.",
                             "The invalid-checksum decoder test deliberately calls the decoder directly, bypassing the caller's rejection."])

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("zip")
    parser.add_argument("--engine",default=str(Path(__file__).resolve().parent.parent/"20261103-native-card-recovery"/"native-card-analysis.py"))
    args=parser.parse_args()
    Cpu=runpy.run_path(args.engine)["Cpu"]
    with zipfile.ZipFile(args.zip) as z:
        exe=z.read("algorithm-analysis/source/SLPS_007.82")
        names=sorted(n for n in z.namelist() if n.startswith("algorithm-analysis/source/operating-save-payloads-20261103/") and n.endswith(".payload.bin"))
        payloads=[(n,z.read(n)) for n in names]
    print(json.dumps(verify_codec(exe,payloads,Cpu),ensure_ascii=False,separators=(",",":")))

if __name__ == "__main__":
    main()
