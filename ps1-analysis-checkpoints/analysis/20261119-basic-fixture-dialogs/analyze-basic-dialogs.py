#!/usr/bin/env python3
"""Known two/four-choice rules joined to original display, not new navigation mechanics."""
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
 regs=list(struct.unpack('<4i',raw(0x800b9910,0x800b9920)));rooms=list(struct.unpack('<2i',raw(0x800cd760,0x800cd768)))
 assert regs==[38,39,41,42] and rooms==[48,49]
 master=[struct.unpack('<49i',raw(0x80099f0c+196*k,0x80099f0c+196*(k+1))) for k in range(53)]
 decode=runpy.run_path(str(ROOT.parent/'20261114-staff-roster-growth-data/source-reference/psmoji.py'))['decode'];texts={}
 def text(u,p):
  cs=[]
  for i in range(200):
   v=struct.unpack('<H',rd(u,p+2*i,2))[0];cs.append(v)
   if v==0x40ff:break
  else:raise AssertionError('text terminator')
  texts[hex(p)]=dict(codes=cs,decoded=decode(cs));return texts[hex(p)]['decoded']
 cases=[]
 for typ,choice in [('room',0),('room',1),('register',0),('register',3)]:
  u=P.machine(exe);draws=[];icons=[];cursors=[];polls=0
  P.put(u,0xcd9f8,123456789);before=rd(u,P.S,5080)
  for r,v in ((UC_MIPS_REG_SP,P.SP),(UC_MIPS_REG_FP,P.SP),(UC_MIPS_REG_RA,P.STOP),(UC_MIPS_REG_A0,P.S|0x80000000),(UC_MIPS_REG_A1,1)):u.reg_write(r,v)
  visual={0x80065974,0x80017b18,0x80067338,0x8004e494,0x8004e938,0x80018940,0x800419e0,0x800157b4,0x800155d0}
  def hook(uc,pc,n,c):
   nonlocal polls
   if pc==0x80069684 and typ=='register':P.put(uc,uc.reg_read(UC_MIPS_REG_FP)+0x1c,choice)
   if pc==0x80041374:
    if typ=='room' and choice==1 and polls==0:
     polls+=1;draws.clear();P.put(uc,0xcda0c,0x2000);P.put(uc,0xcda28,0);uc.reg_write(UC_MIPS_REG_PC,uc.reg_read(UC_MIPS_REG_RA));return
    uc.emu_stop();return
   if pc==0x80041630 and typ=='register':
    a=[uc.reg_read(r) for r in (UC_MIPS_REG_A0,UC_MIPS_REG_A1,UC_MIPS_REG_A2,UC_MIPS_REG_A3)];b=rd(uc,uc.reg_read(UC_MIPS_REG_SP)+0x10,24)
    icons.append(dict(x=s16(a[2])+160,y=s16(a[2]>>16)+112,kind=int.from_bytes(b[:2],'little'),uv=list(b[2:4]),rgb=list(b[8:11]),width=a[3]&65535,height=(a[3]>>16)&65535));uc.reg_write(UC_MIPS_REG_PC,uc.reg_read(UC_MIPS_REG_RA));return
   if pc not in visual:return
   a=[uc.reg_read(r) for r in (UC_MIPS_REG_A0,UC_MIPS_REG_A1,UC_MIPS_REG_A2)]
   if pc==0x80067338:draws.append(dict(kind='inline',x=s16(a[0]),y=s16(a[1]),text=text(uc,a[2])))
   elif pc==0x8004e494:draws.append(dict(kind='message',x=s16(a[0]),y=s16(a[1]),message=a[2],variable0=P.get(uc,0xcd938),money0=P.get(uc,0xe4000),money1=P.get(uc,0xe4004)))
   elif pc==0x8004e938:cursors.append([s16(a[0]),s16(a[1])])
   uc.reg_write(UC_MIPS_REG_PC,uc.reg_read(UC_MIPS_REG_RA))
  h=u.hook_add(UC_HOOK_CODE,hook);u.emu_start(0x8004594c if typ=='room' else 0x8006966c,P.STOP,count=250000);u.hook_del(h)
  assert u.reg_read(UC_MIPS_REG_PC)==0x80041374
  k=rooms[choice] if typ=='room' else regs[choice];m=master[k]
  cost=next(d for d in draws if d['kind']=='message' and d['message']==28);rate=next(d for d in draws if d['kind']=='message' and d['message']==296)
  assert cost['money1']==m[1] and rate['money0']==m[2]*24
  if typ=='register':
   att=next(d for d in draws if d['kind']=='message' and d['message']==368);assert att['variable0']==m[3]
   assert len(icons)==4
   for i,d in enumerate(icons):
    code=master[regs[i]][20];assert d==dict(x=80+40*i,y=88,kind=25,uv=[32*(code%8),32*(code//8)],rgb=[128]*3,width=32,height=32)
   assert cursors==[[103+40*choice,111]]
  else:
   # Original41630 actually executes for room icons, including default RGB and fixed slots0/1.
   for i in range(2):
    b=rd(u,0xdae60+36*i,36);x,y,w,hh,kind=struct.unpack_from('<5h',b,4)
    icons.append(dict(x=x+160,y=y+112,width=w,height=hh,kind=kind,uv=list(b[14:16]),rgb=list(b[20:23])))
    assert icons[-1]==dict(x=112+40*i,y=110 if choice==i else 112,width=32,height=32,kind=25,uv=[96+32*i,192],rgb=[128]*3),icons[-1]
   assert struct.unpack('<H',rd(u,0xdae3c,2))[0]==(40 if choice else 0) # cursor helper intercepted: original movement delta still executes
  assert rd(u,P.S,5080)==before and P.get(u,0xcd9f8)==123456789
  cases.append(dict(dialog=typ,choice=choice,fixture=k,price=m[1],maintenance_24h=m[2]*24,attention=m[4],display_calls=draws,icons=icons,cursor_requests=cursors,input_samples_supplied=polls,store_cash_unchanged=True))
 z=zipfile.ZipFile(archive)
 out('reuse-audit.json',dict(known=[dict(path=n,sha256=hashlib.sha256(z.read(n)).hexdigest()) for n in ['algorithm-analysis/basic_fixture_choices.py','algorithm-analysis/category_parent_control.py']],scope='Two/four choice, selection-before/after-confirm differences and cancel rules are already known; no new discovery or retest of acceptance/cancel.'))
 out('original-cases.json',dict(cases=cases,original_entries=4,preparatory_entries=7,synthetic_input_samples=1,operating_updates=0,gpu=False,room_icon_record_constructor_executed=True,register_record_constructor_intercepted=True))
 rows=[dict(dialog=typ,choice=i,fixture=k,price=master[k][1],maintenance_24h=24*master[k][2],attention=master[k][4],capacity_known=master[k][3],icon=master[k][20]) for typ,ks in [('room',rooms),('register',regs)] for i,k in enumerate(ks)]
 out('dialog-rules.json',dict(rows=rows,room=dict(paper=[64,48,192,112],price_y=80,maintenance_y=96,icons=[[112,112,32,32],[152,112,32,32]],selected_icon_y=110,unselected_icon_y=112),register=dict(paper=[40,24,240,112],price_y=72,maintenance_y=72,parcel_form_capacity_xy=[172,56],icons=[[80+40*i,88,32,32] for i in range(4)],cursor_rule=[103,111,40]),semantics='UI display bindings of known separate selectors; no charges or placement here',android_updated=False))
 out('inline-texts.json',texts)
 ranges={'room_dialog':(0x8004594c,0x80045ffc),'register_dialog':(0x8006966c,0x80069bbc),'register_map':(0x800b9910,0x800b9920),'room_map':(0x800cd760,0x800cd768),'placement_map_reader':(0x80076bd4,0x80076d1c)}
 out('source-provenance.json',dict(exe_sha256=P.EXE_SHA,ranges={k:dict(start=hex(a),end_exclusive=hex(b),sha256=hashlib.sha256(raw(a,b)).hexdigest()) for k,(a,b) in ranges.items()}))
 asm=Path(asmfile).read_text().splitlines();(ROOT/'basic-dialogs.asm').write_text('\n'.join(x.rstrip() for x in asm if any(a<=int(x[:8],16)<b for a,b in ranges.values()))+'\n')
 print('4 bounded dialog displays passed; room second choice uses1 supplied right-input sample')
if __name__=='__main__':main(*sys.argv[1:])
