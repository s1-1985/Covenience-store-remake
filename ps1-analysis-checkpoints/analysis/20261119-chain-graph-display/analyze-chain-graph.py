#!/usr/bin/env python3
"""Original chain header/current-store aggregation and two history bitmaps."""
import hashlib,importlib.util,json,struct,sys
from pathlib import Path
from unicorn import UC_HOOK_CODE
from unicorn.mips_const import *
ROOT=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('helper',ROOT.parent/'20261117-festival-customer-state-data/analyze-festival-state.py');P=importlib.util.module_from_spec(spec);spec.loader.exec_module(P)
MISSING=-2147483648;PIX=0x187e00

def out(n,d):(ROOT/n).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
def rd(u,a,n):return bytes(u.mem_read(a&0x1fffffff,n))
def main(exefile,asmfile):
 exe=Path(exefile).read_bytes();assert hashlib.sha256(exe).hexdigest()==P.EXE_SHA
 raw=lambda a,b:exe[a-0x80010000+2048:b-0x80010000+2048]
 headers=[]
 for name,ratings in [('trunc_each_store_first',[39,99]),('all_five_stars',[100,100])]:
  u=P.machine(exe)
  # Only first150 cells have mix0 (two profiles of one each); remaining2850 are explicitly absent.
  town=bytearray(24000)
  for i in range(3000):struct.pack_into('<h',town,8*i+6,0 if i<150 else -1)
  u.mem_write(0x1398f0,bytes(town))
  for slot,number,rating,demand,rival in [(0,1,ratings[0],100,False),(3,2,ratings[1],50,False),(5,3,100,999,True)]:
   a=P.S+5080*slot;u.mem_write(a,b'\1');u.mem_write(a+4,struct.pack('<H',number|(0x8000 if rival else 0)));P.put(u,a+0xc68,rating);P.put(u,a+0xde0,demand)
  before=rd(u,P.S,50800);draws=[]
  def hook(uc,pc,n,c):
   if pc==0x8004e494:
    draws.append(dict(x=uc.reg_read(UC_MIPS_REG_A0),y=uc.reg_read(UC_MIPS_REG_A1),message=uc.reg_read(UC_MIPS_REG_A2),value=P.get(uc,0xcd938),stars=struct.unpack('<h',rd(uc,0xcd8e6,2))[0]));uc.reg_write(UC_MIPS_REG_PC,uc.reg_read(UC_MIPS_REG_RA))
  h=u.hook_add(UC_HOOK_CODE,hook);P.call(u,0x800498c8);u.hook_del(h)
  share=next(d for d in draws if d['message']==461);stars=next(d for d in draws if d['message']==462)
  assert share['value']==50 and stars['stars']==sum(v//20 for v in ratings)//2
  assert rd(u,P.S,50800)==before
  headers.append(dict(name=name,ratings=ratings,own_slots=[0,3],rival_slot_excluded=5,total_own_demand=150,town_population=300,share=share,aggregate_stars=stars,store_records_unchanged=True))
 plots=[]
 for name,values,counts in [('positive_negative_zero',[500000,-500000,0],[2,2,2]),('stop_at_history_gap',[400000,MISSING,9000000],[1,1,1])]:
  u=P.machine(exe)
  for i in range(60):P.put(u,0xe3c28+4*i,MISSING)
  for i,v in enumerate(values):P.put(u,0xe3c28+4*i,v)
  u.mem_write(0xe43d0,bytes(counts))
  # Store-specific history deliberately missing; chain graph does not consult it.
  for i in range(60):P.put(u,P.S+0x12e8+4*i,MISSING)
  for r,v in ((UC_MIPS_REG_SP,P.SP),(UC_MIPS_REG_FP,P.SP),(UC_MIPS_REG_RA,P.STOP)):u.reg_write(r,v)
  def stop(uc,pc,n,c):
   if pc==0x80049844:uc.emu_stop()
  h=u.hook_add(UC_HOOK_CODE,stop);u.emu_start(0x8004965c,P.STOP,count=100000);u.hook_del(h);assert u.reg_read(UC_MIPS_REG_PC)==0x80049844
  axis=P.get(u,0xe4000);assert axis==100
  u.mem_write(PIX-240,b'\xaa'*240);u.mem_write(PIX+240*112,b'\xaa'*240);P.call(u,0x80048cf8)
  pix=rd(u,PIX,240*112)
  assert rd(u,PIX-240,240)==b'\xaa'*240 and rd(u,PIX+240*112,240)==b'\xaa'*240
  if name=='positive_negative_zero':
   assert pix[55*240:55*240+4]==bytes([3,3,3,4])
   assert pix[57*240+4:57*240+8]==bytes([2,2,2,4])
   assert pix[27*240+8:27*240+12]==bytes([3,3,3,4])
   expected_order=[0,-500000,500000]
  else:
   assert pix[33*240:33*240+4]==bytes([3,3,3,4]);expected_order=[400000]
  plots.append(dict(name=name,history_newest_first=values,counts=counts,scale_units_10000=axis,oldest_first_valid=expected_order,bitmap_sha256=hashlib.sha256(pix).hexdigest(),guard_bytes_unchanged=True,return_value=u.reg_read(UC_MIPS_REG_V0)))
  if name=='positive_negative_zero':
   # Exact source-palette bitmap reference, no generated illustration or game screenshot.
   from PIL import Image
   pal=struct.unpack('<6H',raw(0x80010a30,0x80010a3c));colors=[tuple(((v>>s)&31)*255//31 for s in (0,5,10)) for v in pal]
   im=Image.new('RGB',(240,112));im.putdata([colors[i] for i in pix]);im.save(ROOT/'chain-bitmap-reference.png')
 out('original-cases.json',dict(header_cases=headers,plot_cases=plots,original_entries=6,preparation_entries=6,breakdown=dict(header=2,scale=2,bitmap=2),operating_updates=0,header_text_renderer_intercepted=True,native_list_and_population_helpers_executed=True,scope='Controlled current-store/town/history inputs; no natural play/GPU/text glyphs.'))
 out('display-rules.json',dict(header=dict(share='trunc(100*sum(current own store+DE0)/current town profile population)',stars='trunc(sum(trunc(each current own ratingC68/20))/number of own stores)',share_message=461,stars_message=462,historical=False),bitmap=dict(source='E3C28 chain monthly net, not store sales or per-store average',prefix='Stop at first nonpositive signed store-count byte or missing chain-net sentinel; max60',order='oldest valid first',size=[240,112],bar_width=4,zero='original draws1pixel atrow55 using palette3',native_clipping_scope='Nonmax samples only; known exact-axis overflow not retested'),reused=['monthly accounting/save layout','prior graph report scale/prefix/bar conventions'],new_scope='native full-chain bitmap counterpart and current-chain header binding',apk_updated=False))
 spans={'chain_scale':(0x8004965c,0x80049844),'chain_header':(0x800498c8,0x80049b44),'chain_bitmap':(0x80048cf8,0x8004965c),'chain_ui':(0x80048b80,0x80048cf8)}
 out('source-provenance.json',dict(exe_sha256=P.EXE_SHA,ranges={k:dict(start=hex(a),end_exclusive=hex(b),sha256=hashlib.sha256(raw(a,b)).hexdigest()) for k,(a,b) in spans.items()}))
 asm=Path(asmfile).read_text().splitlines();(ROOT/'chain-readers.asm').write_text('\n'.join(x.rstrip() for x in asm if any(a<=int(x[:8],16)<b for a,b in spans.values()))+'\n')
 print('2 current-chain headers and2 scale/bitmap pairs passed; original top-level entries6')
if __name__=='__main__':main(*sys.argv[1:])
