#!/usr/bin/env python3
"""Verify every compressed trace, data patch, original retry word, and expected diagnostic outcome."""
import base64,hashlib,json,runpy,struct,sys,zlib,zipfile
from pathlib import Path

def sha(b):return hashlib.sha256(b).hexdigest()
def verify(archive_path,texts,reference):
    m={"__name__":"native_file_reference"};exec(compile(reference,"native-file-analysis.py","exec"),m)
    with zipfile.ZipFile(archive_path) as archive:
        exe=archive.read("algorithm-analysis/source/SLPS_007.82")
        name=sorted(n for n in archive.namelist() if n.startswith("algorithm-analysis/source/operating-save-payloads-20261103/") and n.endswith(".payload.bin"))[0]
        payload=archive.read(name)
    assert sha(exe)=="d6a167a1c9e0fe98d7e44e12968caa489ac3eb7ed3b9e46012a188af8432b1fd"
    assert sha(payload)=="e6a7a7a16b914d65598fd252e7c65ff5bc0658d80ba8e6c4d0564d01b7e6bd7a"
    body=payload+b"\xa5"*9812
    c=m["Cpu"](exe);env=m["LogicalFiles"](c,{});c.write(m["BODY"],body)
    for mode in (0,1):assert c.run(0x8007adf8,[mode],limit=1000000,stack_pointer=0x801d0000,global_pointer=m["GP"])==0
    initial=bytes(env.files[m["PATH"]])
    cases=0;traces=0;patches=0;full_files=0
    for group,pattern,count in (("source",False,16),("pattern",True,8),("last",True,16)):
        records=json.loads(zlib.decompress(base64.b64decode(texts[group+".evidence.json.zlib.b64"])))
        assert len(records)==count
        for row in records:
            cases+=1
            trace=zlib.decompress(base64.b64decode(row["trace_zlib_base64"]))
            assert sha(trace)==row["trace_sha256"] and len(json.loads(trace))==row["io_count"];traces+=1
            start,end=(0,89600) if row["mode"]==0 else (89600,114176)
            wanted=body if row["operation"]=="read" else bytes((j*73+19)&255 for j in range(len(body))) if pattern else bytes(v^255 for v in body)
            wanted_range=wanted[start:end];actual=bytearray(wanted_range)
            assert sha(wanted_range)==row["expected_data_sha256"]
            for patch in row["output_patches"]:
                assert start<=patch["offset"]<end
                actual[patch["offset"]-start]=patch["value"];patches+=1
            assert sha(actual)==row["data_sha256"] and (bytes(actual)==wanted_range)==row["matches_requested_data"]
            if "full_file_sha256" in row:
                wanted_file=bytearray(initial)
                if row["operation"]=="write":wanted_file[512+start:512+end]=wanted_range
                assert sha(wanted_file)==row["expected_full_file_sha256"]
                actual_file=bytearray(wanted_file)
                if row["operation"]=="write":
                    for patch in row["output_patches"]:actual_file[512+patch["offset"]]=patch["value"]
                for patch in row["outside_mode_patches"]:actual_file[patch["file_offset"]]=patch["value"]
                assert sha(actual_file)==row["full_file_sha256"];full_files+=1
            if group=="last":
                expected_timeout=row["mode"]==1 and row["injected_result"]==127
                assert (row["return_value"] is None)==expected_timeout
                assert row["state"]==("instruction_budget_exhausted" if expected_timeout else "returned")
            else:assert row["return_value"]==0
    endpoints=json.loads(zlib.decompress(base64.b64decode(texts["endpoint.evidence.json.zlib.b64"])))
    assert len(endpoints)==24
    for row in endpoints:
        cases+=1;trace=zlib.decompress(base64.b64decode(row["trace_zlib_base64"]));assert sha(trace)==row["trace_sha256"];traces+=1
        timeout=row["frequency"]=="persistent" and row["endpoint"]!="close"
        assert row["state"]==("instruction_budget_exhausted" if timeout else "returned")
        if row["endpoint"]=="close":assert row["calls"]==1 and row["return_value"]==0 and len(row["open_handles"])==1
    persistent=json.loads(texts["persistent-results.json"])
    assert len(persistent)==8
    for row in persistent:
        cases+=1;assert row["state"]=="instruction_budget_exhausted" and row["steps"]==200000 and row["return_value"] is None
    words=json.loads(texts["retry-loop-words.json"])
    assert words["source_exe_sha256"]==sha(exe)
    for loop in words["loops"]:
        raw=b""
        for address,word in loop["original_words"]:
            offset=int(address,16)-0x80010000+0x800;value=exe[offset:offset+4]
            assert struct.unpack("<I",value)[0]==int(word,16);raw+=value
        assert sha(raw)==loop["bytes_sha256"] and loop["compare_word"]=="0x14430003"
    assert cases==72 and traces==64 and full_files==16
    return dict(all_evidence_consistent=True,diagnostic_inputs=cases,full_io_traces_verified=traces,
                data_patch_bytes_verified=patches,whole_files_reconstructed=full_files,original_retry_loops_verified=4,
                source_payload=name,source_payload_sha256=sha(payload),
                scope="Evidence integrity and exact reconstruction, not a claim that all native I/O requests succeeded or that physical card behavior was reproduced.")
def main():
    root=Path(__file__).resolve().parent
    names=["source.evidence.json.zlib.b64","pattern.evidence.json.zlib.b64","last.evidence.json.zlib.b64",
           "endpoint.evidence.json.zlib.b64","persistent-results.json","retry-loop-words.json"]
    result=verify(sys.argv[1],{n:(root/n).read_text() for n in names},
                  (root.parent/"20261103-native-file-recovery/native-file-analysis.py").read_text())
    print(json.dumps(result,ensure_ascii=False,separators=(",",":")))
if __name__=="__main__":main()
