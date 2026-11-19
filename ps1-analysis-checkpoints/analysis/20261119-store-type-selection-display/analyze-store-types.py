#!/usr/bin/env python3
"""Original six-store selection rendering; reuse old premises_input navigation."""
import hashlib,importlib.util,json,runpy,struct,sys,zipfile
from pathlib import Path
from unicorn import UC_HOOK_CODE
from unicorn.mips_const import *
ROOT=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('helper',ROOT.parent/'20261117-festival-customer-state-data/analyze-festival-state.py');P=importlib.util.module_from_spec(spec);spec.loader.exec_module(P)
def out(n,d):(ROOT/n).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
def rd(u,a,n):return bytes(u.mem_read(a&0x1fffffff,n))
def s16(v):v&=65535;return v-65536 if v&32768 else v

def main(exefile,asmfile,archive):
 exe=Path(exefile).read_bytes();assert hashlib.sha256(exe).hexdigest()==P.EXE_SHA
 raw=lambda a,b:exe[a-0x80010000+2048:b-0x80010000+2048]
 costs=list(struct.unpack('<6i',raw(0x800109f4,0x80010a0c)));grid=list(struct.unpack('<6i',raw(0x80010a0c,0x80010a24)))
 assert grid==[1,3,5,2,4,6]
 cases=[]
 for limit,choice in ((2,0),(2,4),(6,5)):
  u=P.machine(exe);draws=[];loads=[]
  for r,v in ((UC_MIPS_REG_SP,P.SP),(UC_MIPS_REG_FP,P.SP),(UC_MIPS_REG_RA,P.STOP),(UC_MIPS_REG_A0,limit)):u.reg_write(r,v)
  P.put(u,0xcd9f8,123456789)
  visual={0x80013f7c,0x80013eac,0x80018940,0x80017b18,0x800419e0,0x8004e938,0x800157b4,0x800155d0,0x80018a5c,0x8004e494}
  def hook(uc,pc,n,c):
   if pc==0x8004420c:
    f=uc.reg_read(UC_MIPS_REG_FP);P.put(uc,f+0x48,choice//2);P.put(uc,f+0x4c,choice%2)
   if pc==0x80041374:uc.emu_stop();return
   if pc not in visual:return
   a=[uc.reg_read(r) for r in (UC_MIPS_REG_A0,UC_MIPS_REG_A1,UC_MIPS_REG_A2)]
   if pc==0x80013f7c:loads.append(a[0])
   if pc==0x8004e494:draws.append(dict(x=s16(a[0]),y=s16(a[1]),message=a[2],money=P.get(uc,0xe4000)))
   uc.reg_write(UC_MIPS_REG_PC,uc.reg_read(UC_MIPS_REG_RA))
  h=u.hook_add(UC_HOOK_CODE,hook);u.emu_start(0x80043cf4,P.STOP,count=100000);u.hook_del(h)
  assert u.reg_read(UC_MIPS_REG_PC)==0x80041374 and loads==[6]
  icons=[]
  for i in range(6):
   b=rd(u,0xdae60+36*i,36);x,y,w,hh,kind=struct.unpack_from('<5h',b,4)
   d=dict(x=x+160,y=y+112,width=w,height=hh,kind=kind,uv=list(b[14:16]),clut=list(struct.unpack_from('<2H',b,16)),rgb=list(b[20:23]))
   assert d==dict(x=96+48*(i//2),y=84+40*(i%2)-(2 if i==choice else 0),width=32,height=32,kind=13,uv=[32*i,128],clut=[0,490],rgb=[128 if i<limit else 64]*3),d
   icons.append(d)
  money=next(d for d in draws if d['message']==272);assert money['money']==costs[choice]
  assert P.get(u,0xcd9f8)==123456789
  cases.append(dict(unlock_count=limit,choice=choice,grid_row=choice%2,grid_column=choice//2,icons=icons,draws=draws,selected_cost=money,cash_unchanged=True,resource_request=loads))
 binding=json.loads((ROOT.parent/'20261117-texture-runtime-binding-data/texture-bindings.json').read_text())['rows'][6]
 z=zipfile.ZipFile(archive);old=z.read('algorithm-analysis/premises_input.py')
 out('reuse-audit.json',dict(path='algorithm-analysis/premises_input.py',sha256=hashlib.sha256(old).hexdigest(),known='GRID((1,3,5),(2,4,6)), directional movement, maximum eligibility and confirm/cancel already decoded; construction cost tiers also known.',new_scope='source display binding of visible locked icons, selected spriteY, originalSHOPTYP1icon cells, displayed price and Android differences'))
 out('original-cases.json',dict(cases=cases,original_entries=3,visual_intercepts=[hex(a) for a in sorted(visual)],original_sprite_constructor_executed=True,gpu=False,operating_updates=0,staged_selection=True,actual_input_samples=0))
 out('store-type-display.json',dict(rows=[dict(tier=i,row=i%2,column=i//2,source_image='SHOPTYP1.TIM',source_rect=[32*i,0,32,32],logical_rect=[96+48*(i//2),84+40*(i%2),32,32],displayed_cost=costs[i]) for i in range(6)],paper=[48,32,224,144],selected_y_offset=-2,unlock_rgb=dict(available=128,locked=64),selection_count=6,price_xy_rule='160+8*(11-original65820(price)),64',title_xy=[64,48],resource_binding=binding,android_updated=False))
 ranges={'selector_and_display':(0x80043cf4,0x800443d8),'price_and_grid':(0x800109f4,0x80010a24),'maximum_count_caller':(0x8006e998,0x8006e9fc)}
 out('source-provenance.json',dict(exe_sha256=P.EXE_SHA,ranges={k:dict(start=hex(a),end_exclusive=hex(b),sha256=hashlib.sha256(raw(a,b)).hexdigest()) for k,(a,b) in ranges.items()}))
 asm=Path(asmfile).read_text().splitlines();(ROOT/'store-type-display.asm').write_text('\n'.join(x.rstrip() for x in asm if any(a<=int(x[:8],16)<b for a,b in ranges.values()))+'\n')
 print('3 original six-icon displays passed; locked tier remains visible/selectable, no confirmation')
if __name__=='__main__':main(*sys.argv[1:])
