#!/usr/bin/env python3
"""Read-only verification of the 2026-10-15 native PNG staging; no file writes."""
import argparse, hashlib, json, pathlib, struct, sys, zlib
def git_blob_sha(data):
    return hashlib.sha1(b"blob "+str(len(data)).encode()+b"\0"+data).hexdigest()
def png_header(data):
    if data[:8] != b"\x89PNG\r\n\x1a\n": raise ValueError("bad PNG signature")
    if data[12:16] != b"IHDR" or len(data)<33: raise ValueError("missing IHDR")
    if struct.unpack(">I",data[8:12])[0]!=13: raise ValueError("invalid IHDR length")
    if zlib.crc32(data[12:29])&0xffffffff != struct.unpack(">I",data[29:33])[0]: raise ValueError("IHDR CRC mismatch")
    w,h,depth,ctype=struct.unpack(">IIBB",data[16:26])
    if (w,h,depth,ctype)!=(64,64,8,6): raise ValueError(f"unexpected PNG: {(w,h,depth,ctype)}")
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--repo-root",type=pathlib.Path,default=pathlib.Path("."))
    p.add_argument("--manifest",type=pathlib.Path,default=pathlib.Path("chatgpt_map_assets/generated/native_copies_2026-10-15/manifest.json"))
    a=p.parse_args()
    root=a.repo_root.resolve()
    manifest=json.loads((root/a.manifest).read_text(encoding="utf-8"))
    bad=[]
    for r in manifest["assets"]:
        src=root/r["source_path"]; dst=root/r["isolated_path"]
        try:
            if src.is_symlink() or dst.is_symlink(): raise ValueError("symlink forbidden")
            s=src.read_bytes(); d=dst.read_bytes()
            if s!=d: raise ValueError("source and isolated copy differ")
            if git_blob_sha(d)!=r["git_blob_sha"]: raise ValueError("git blob SHA mismatch")
            png_header(d)
            print("PASS",r["asset_id"])
        except Exception as e: bad.append((r["asset_id"],str(e))); print("FAIL",r["asset_id"],str(e))
    print(json.dumps({"checked":len(manifest["assets"]),"passed":len(manifest["assets"])-len(bad),"failed":bad,"seam_verified":False},ensure_ascii=False))
    return int(bool(bad))
if __name__=="__main__": sys.exit(main())
