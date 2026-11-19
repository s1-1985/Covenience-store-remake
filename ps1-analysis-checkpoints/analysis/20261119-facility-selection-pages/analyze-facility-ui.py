#!/usr/bin/env python3
"""Original facility page display and isolated cross-page input fragments."""
import hashlib,importlib.util,json,runpy,struct,sys
from pathlib import Path
from unicorn import UC_HOOK_CODE
from unicorn.mips_const import *
ROOT=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('helper',ROOT.parent/'20261117-festival-customer-state-data/analyze-festival-state.py');P=importlib.util.module_from_spec(spec);spec.loader.exec_module(P)
def out(n,d):(ROOT/n).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
def rd(u,a,n):return bytes(u.mem_read(a&0x1fffffff,n))
def s16(v):v&=65535;return v-65536 if v&32768 else v

def main(exefile,asmfile):
 exe=Path(exefile).read_bytes();assert hashlib.sha256(exe).hexdigest()==P.EXE_SHA
 raw=lambda a,b:exe[a-0x80010000+2048:b-0x80010000+2048]
 mapping=list(struct.unpack('<18i',raw(0x80010bb8,0x80010c00)));messages=list(struct.unpack('<18i',raw(0x800b94f8,0x800b9540)))
 master=json.loads((ROOT.parent/'20261115-town-project-data/project-master.json').read_text())['rows']
 decode=runpy.run_path(str(ROOT.parent/'20261114-staff-roster-growth-data/source-reference/psmoji.py'))['decode'];texts={}
 def text(u,p):
  codes=[]
  for i in range(200):
   v=struct.unpack('<H',rd(u,p+2*i,2))[0];codes.append(v)
   if v==0x40ff:break
  else:raise AssertionError('text terminator')
  texts[hex(p)]=dict(codes=codes,decoded=decode(codes));return texts[hex(p)]['decoded']
 cases=[]
 for page,slot in ((0,0),(1,7)):
  u=P.machine(exe);f=P.SP;cols=5 if page==0 else 4
  for r,v in ((UC_MIPS_REG_SP,f),(UC_MIPS_REG_FP,f)):u.reg_write(r,v)
  u.mem_write((f+0x18)&0x1fffffff,raw(0x80010bb8,0x80010c00));u.mem_write((f+0x60)&0x1fffffff,raw(0x80010c00,0x80010c0a))
  P.put(u,f+0x80,page);P.put(u,f+0x84,slot);P.put(u,0xcd9f8,123456789);draws=[];icons=[];cursor=[]
  intercept={0x80065974,0x80017b18,0x80067338,0x8004e494,0x80018940,0x80041630,0x8004e938}
  def hook(uc,pc,n,c):
   if pc==0x80041374:uc.emu_stop();return
   if pc not in intercept:return
   a=[uc.reg_read(r) for r in (UC_MIPS_REG_A0,UC_MIPS_REG_A1,UC_MIPS_REG_A2,UC_MIPS_REG_A3)]
   if pc==0x80067338:draws.append(dict(kind='inline',x=s16(a[0]),y=s16(a[1]),text=text(uc,a[2])))
   elif pc==0x8004e494:draws.append(dict(kind='message',x=s16(a[0]),y=s16(a[1]),message=a[2],value=P.get(uc,0xe4000)))
   elif pc==0x80041630:
    b=rd(uc,uc.reg_read(UC_MIPS_REG_SP)+0x10,24)
    icons.append(dict(x=s16(a[2])+160,y=s16(a[2]>>16)+112,width=a[3]&65535,height=(a[3]>>16)&65535,kind=int.from_bytes(b[:2],'little'),uv=list(b[2:4]),clut=list(struct.unpack_from('<2H',b,4)),rgb=list(b[8:11])))
   elif pc==0x8004e938:cursor.append([s16(a[0]),s16(a[1])])
   uc.reg_write(UC_MIPS_REG_PC,uc.reg_read(UC_MIPS_REG_RA))
  h=u.hook_add(UC_HOOK_CODE,hook);u.emu_start(0x8006a5bc,P.STOP,count=200000);u.hook_del(h)
  assert u.reg_read(UC_MIPS_REG_PC)==0x80041374
  assert len(icons)==(10 if page==0 else 8)
  for i,d in enumerate(icons):
   code=mapping[page*10+i]
   assert d==dict(x=68+40*(i%cols),y=72+40*(i//cols),width=32,height=32,kind=13,uv=[32*(code%8),128+32*(code//8)],clut=[0,490],rgb=[128]*3),d
  chosen=page*10+slot;cost=next(d for d in draws if d['kind']=='message' and d['message']==272)
  assert cost['value']==master[chosen]['base_cost']
  name=next(d for d in draws if d['kind']=='message' and d['x']==56 and d['y']==56)
  assert name['message']==messages[chosen]
  assert cursor==[[91+40*(slot%cols),95+40*(slot//cols)]]
  assert P.get(u,0xcd9f8)==123456789
  cases.append(dict(page=page,slot=slot,selection=chosen,columns=cols,cost=cost,name_message=name['message'],draws=draws,icons=icons,cursor=cursor,cash_unchanged=True))
 nav=[]
 for page,slot,dirs,expected in ((0,4,0x2000,(1,0)),(0,9,0x2000,(1,4)),(1,0,0x8000,(0,4)),(1,4,0x8000,(0,9))):
  u=P.machine(exe);f=P.SP;u.reg_write(UC_MIPS_REG_SP,f);u.reg_write(UC_MIPS_REG_FP,f)
  for a,v in ((f+0x80,page),(f+0x84,slot),(f+0x8c,5 if page==0 else 4),(0xcda0c,dirs)):P.put(u,a,v)
  def stop(uc,pc,n,c):
   if pc==0x8006ad60:uc.emu_stop()
  h=u.hook_add(UC_HOOK_CODE,stop);u.emu_start(0x8006ab68,P.STOP,count=10000);u.hook_del(h)
  actual=(P.get(u,f+0x80),P.get(u,f+0x84));assert actual==expected and u.reg_read(UC_MIPS_REG_PC)==0x8006ad60
  nav.append(dict(before=[page,slot],direction_mask=hex(dirs),after=list(actual),stop='before cancel/confirm at6AD60'))
 rows=[]
 for i,m in enumerate(master):
  page=i//10;slot=i%10;cols=5 if page==0 else 4;code=mapping[i]
  rows.append(dict(selection=i,name=m['name'],page=page,slot=slot,columns=cols,name_message=messages[i],base_cost_known=m['base_cost'],icon_code=code,source_image='BUILDIN1.TIM',source_rect=[32*(code%8),32*(code//8),32,32],logical_rect=[68+40*(slot%cols),72+40*(slot//cols),32,32]))
 ranges={'selection_init_tables':(0x80010bb8,0x80010c0a),'display_and_input':(0x8006a5bc,0x8006ad60),'facility_icon':(0x8006b620,0x8006b780),'message_table':(0x800b94f8,0x800b9540)}
 out('original-cases.json',dict(display=cases,cross_page=nav,original_entries=6,gpu=False,operating_updates=0,staged_frame=True,visual_intercepts=[hex(x) for x in sorted(intercept)]))
 out('facility-ui-map.json',dict(rows=rows,page_sizes=[10,8],page_columns=[5,4],cursor_rule='91+40*(slot%columns),95+40*(slot//columns)',paper=[40,24,256,144],title_xy=[72,40],name_xy=[56,56],aid_xy=[148,56],cost_alignment='184+8*(11-original65820(value)),56',shared_icons=[dict(selections=[4,5],code=18),dict(selections=[9,10,11],code=8)],cross_page=nav,original_image_binding='20261117-texture-runtime-binding-data/texture-bindings.json row17',android_update=False))
 out('inline-texts.json',texts)
 out('source-provenance.json',dict(exe_sha256=P.EXE_SHA,ranges={k:dict(start=hex(a),end_exclusive=hex(b),sha256=hashlib.sha256(raw(a,b)).hexdigest()) for k,(a,b) in ranges.items()},known_reused=['18 project definitions/base cost/building size','BUILDIN1 texture upload and palette','project initialization/completion untouched']))
 asm=Path(asmfile).read_text().splitlines();(ROOT/'facility-ui.asm').write_text('\n'.join(x.rstrip() for x in asm if any(a<=int(x[:8],16)<b for a,b in ranges.values()))+'\n')
 print('2 original page displays and4 cross-page input fragments passed; no placement/payment/completion')
if __name__=='__main__':main(*sys.argv[1:])
