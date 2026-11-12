#!/usr/bin/env python3
"""Compare merge opcodes and both pair orders against byte formulas and Unicorn."""
import hashlib,importlib.util,json,random,struct,sys
from pathlib import Path
from unicorn import Uc,UC_ARCH_MIPS,UC_MODE_MIPS32,UC_MODE_LITTLE_ENDIAN
from unicorn.mips_const import UC_MIPS_REG_A0,UC_MIPS_REG_A1,UC_MIPS_REG_RA,UC_MIPS_REG_V0
ROOT=Path(__file__).resolve().parent;algo=Path(sys.argv[1]).resolve();sys.path.insert(0,str(algo))
def mod(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
base=mod('merge_base',ROOT.parent/'20261103-rival-monthly/rival-monthly-analysis.py');extra=mod('merge_ops',ROOT/'strict-unaligned.py');Cpu=extra.extend(base.Cpu)
rand=random.Random(0x4d495053);cases=[]
def instruction(op,imm):return op<<26|4<<21|8<<16|(imm&65535)
def run(label,ops,offset,value,data,expected_value,expected_data):
 words=[(5<<21)|(8<<11)|0x21]+ops+[0,(8<<21)|(2<<11)|0x21,0x03e00008,0]
 code=struct.pack('<'+'I'*len(words),*words);header=bytearray(0x800);header[:8]=b'PS-X EXE';struct.pack_into('<II',header,0x18,0x80010000,len(code));exe=bytes(header)+code
 cpu=Cpu(exe);cpu.write(0x80020000,data);ret=cpu.run(0x80010000,args=(0x80020000+offset,value));got=cpu.read(0x80020000,len(data))
 u=Uc(UC_ARCH_MIPS,UC_MODE_MIPS32|UC_MODE_LITTLE_ENDIAN);u.mem_map(0,0x200000);u.mem_write(0x10000,code);u.mem_write(0x20000,data);u.reg_write(UC_MIPS_REG_A0,0x80020000+offset);u.reg_write(UC_MIPS_REG_A1,value);u.reg_write(UC_MIPS_REG_RA,0x80001000);u.emu_start(0x80010000,0x80001000,count=100)
 assert ret&0xffffffff==expected_value==u.reg_read(UC_MIPS_REG_V0),(label,offset,hex(ret&0xffffffff),hex(expected_value))
 assert got==expected_data==bytes(u.mem_read(0x20000,len(data))),(label,offset)
 cases.append(dict(kind=label,offset=offset,input_value=value,data_hex=data.hex(),expected_value=expected_value,expected_data_hex=expected_data.hex()))
for n in range(24):
 for k in range(4):
  data=rand.randbytes(12);v=rand.getrandbits(32);mem=int.from_bytes(data[:4],'little')
  for op,label in ((34,'LWL'),(38,'LWR')):
   expected=bytearray(v.to_bytes(4,'little'))
   if op==34:expected[3-k:]=data[:k+1]
   else:expected[:4-k]=data[k:4]
   run(label,[instruction(op,0)],k,v,data,int.from_bytes(expected,'little'),data)
  for op,label in ((42,'SWL'),(46,'SWR')):
   expected=bytearray(data);vb=v.to_bytes(4,'little')
   if op==42:expected[:k+1]=vb[3-k:]
   else:expected[k:4]=vb[:4-k]
   run(label,[instruction(op,0)],k,v,data,v,bytes(expected))
  for reverse in (False,True):
   ops=[instruction(34,3),instruction(38,0)];ops=ops[::-1] if reverse else ops
   run('load_pair_reverse' if reverse else 'load_pair',ops,k,v,data,int.from_bytes(data[k:k+4],'little'),data)
   ops=[instruction(42,3),instruction(46,0)];ops=ops[::-1] if reverse else ops
   expected=bytearray(data);expected[k:k+4]=v.to_bytes(4,'little')
   run('store_pair_reverse' if reverse else 'store_pair',ops,k,v,data,v,bytes(expected))
out=dict(all_passed=True,seed=0x4d495053,cases=len(cases),kinds=sorted({r['kind'] for r in cases}),coverage='24 random byte patterns x 4 alignments x 8 merge operations/pair orders; byte-slice formulas and Unicorn agree.',extension_sha256=hashlib.sha256((ROOT/'strict-unaligned.py').read_bytes()).hexdigest(),limits=['Final load values checked after an explicit delay slot; merge-pair forwarding exercised in both orders.', 'Only these opcodes/pairs; not a full R3000A hardware or timing validation.'],evidence=cases)
(ROOT/'unaligned-verification.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({k:v for k,v in out.items() if k!='evidence'}))
