#!/usr/bin/env python3
"""Verify base64 Git readback records supplied as a JSON array on stdin."""
import sys,json,base64,hashlib,zlib,struct
records=json.loads(sys.stdin.buffer.read())
rows=[];buffers={}
for row in records:
 b=base64.b64decode(row["content"],validate=True)
 assert len(b)==row["bytes"] and hashlib.sha256(b).hexdigest()==row["sha256"]
 name=row["path"].split("/")[-1];buffers[name]=b
 record=dict(path=row["path"],bytes=len(b),sha256=hashlib.sha256(b).hexdigest(),matched=True)
 if name.endswith(".ram.zlib"):
  ram=zlib.decompress(b)
  assert len(ram)==2097152 and hashlib.sha256(ram).hexdigest()==row["expected_ram_sha256"]
  record.update(ram_sha256=row["expected_ram_sha256"],clock=struct.unpack_from("<I",ram,0xcd93c)[0],cash=list(struct.unpack_from("<2i",ram,0xcd9f8)))
 rows.append(record)
for name,b in buffers.items():
 if name.endswith(".card-file.bin"):
  payload=buffers[name.replace(".card-file.bin",".payload.bin")]
  assert b[:4]==bytes.fromhex("5343130e") and b[512:512+104364]==payload
  assert sum(payload[:104360])&0xffffffff==struct.unpack_from("<I",payload,104360)[0]
print(json.dumps(dict(all_passed=True,binary_files_verified=len(rows),results=rows,logical_file_payloads_and_checksums_match=True)))