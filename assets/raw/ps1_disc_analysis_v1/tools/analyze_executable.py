from pathlib import Path
import struct,re,json,collections
from capstone import Cs,CS_ARCH_MIPS,CS_MODE_MIPS32,CS_MODE_LITTLE_ENDIAN
BASE=Path(__file__).resolve().parents[1];b=(BASE/'files/SLPS_007.82').read_bytes();base=struct.unpack_from('<I',b,24)[0]
md=Cs(CS_ARCH_MIPS,CS_MODE_MIPS32|CS_MODE_LITTLE_ENDIAN);md.skipdata=True
ins=list(md.disasm_lite(b[0x800:],base));targets=collections.Counter()
for addr,size,mn,ops in ins:
 if mn=='jal':targets[ops]+=1
(BASE/'executable-summary.json').write_text(json.dumps(dict(entry=hex(struct.unpack_from('<I',b,16)[0]),load=hex(base),payload_size=struct.unpack_from('<I',b,28)[0],file_to_ram='RAM = 0x80010000 + file_offset - 0x800',warning='Linear disassembly includes data. Function targets are candidates, not identified algorithms.',jal_targets=targets),indent=2))
with (BASE/'executable-reference-hits.txt').open('w') as f:
 for i,(addr,sz,mn,ops) in enumerate(ins):
  if mn in ('addiu','slti','sltiu','ori') and ops.endswith(', 0xbb8'):
   f.write('\nCANDIDATE constant 3000; semantics unconfirmed\n')
   for a,s,m,o in ins[max(0,i-10):i+11]:f.write(f'{a:08x} file+{a-base+0x800:06x} {m:8} {o}\n')
paths=[]
for m in re.finditer(rb'\\[A-Z0-9_\\.]+;1',b):paths.append(dict(offset=hex(m.start()),ram=hex(base+m.start()-0x800),path=m.group().decode()))
(BASE/'executable-paths.json').write_text(json.dumps(paths,indent=2));print('3000 references', (BASE/'executable-reference-hits.txt').read_text()[:7000])
