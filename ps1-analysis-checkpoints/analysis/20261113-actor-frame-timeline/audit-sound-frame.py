#!/usr/bin/env python3
"""Connect the extra source frame to the original sound wrapper's native call order."""
import hashlib,json,struct,sys,zlib
from pathlib import Path
root=Path(__file__).resolve().parent;algo=Path(sys.argv[1]).resolve()
audit=json.loads((root/'audit.json').read_text())
proof=json.loads(zlib.decompress((root/'second-store-play-proof.json.zlib').read_bytes()))
exe=(algo/'source/SLPS_007.82').read_bytes()
sha=hashlib.sha256(exe).hexdigest();assert sha=='d6a167a1c9e0fe98d7e44e12968caa489ac3eb7ed3b9e46012a188af8432b1fd'
start,end=0x80064fc0,0x80064fe8
words=list(struct.unpack('<10I',exe[start-0x80010000+2048:end-0x80010000+2048]))
for offset,target in ((0,0x80064550),(8,0x80018a5c),(32,0x80064740)):
 word=words[offset//4];assert word>>26==3 and ((start+offset+4)&0xf0000000)|((word&0x3ffffff)<<2)==target
assert audit['stale_records']==[dict(clock=20580,record_clock=20578,caller='0x80064fd0',construction=9)]
assert len(proof['voice_starts'])==1 and proof['voice_starts'][0][0]==22
result=dict(all_passed=True,source_executable_sha256=sha,
 source_words={hex(start+i*4):hex(w) for i,w in enumerate(words)},
 original_call_order=['80064550: stop prior voice state','80018A5C: draw current record pool','80064740: start requested voice'],
 observed_extra_frame=audit['stale_records'][0],observed_voice_index=22,
 limits=['Source wrapper call order and observed branch; not a recording of the spoken phrase or actual playback latency.',
 'One stored voice start and one wrapper frame in this branch; does not imply every sound adds a frame.',
 'Original source texture/record remains valid while logical state has advanced; no interpolation is implied.'])
(root/'sound-frame-audit.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
