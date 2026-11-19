#!/usr/bin/env python3
"""Bind known equipment navigation/master to original bounded display output."""
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
 order=list(struct.unpack('<39i',raw(0x800b9920,0x800b99bc)))
 master=[struct.unpack('<49i',raw(0x80099f0c+196*k,0x80099f0c+196*(k+1))) for k in range(53)]
 labels=json.loads((ROOT.parent/'20261113-product-stock-data/fixture-labels.json').read_text())['labels']
 decode=runpy.run_path(str(ROOT.parent/'20261114-staff-roster-growth-data/source-reference/psmoji.py'))['decode'];texts={}
 def text(u,p):
  cs=[]
  for i in range(200):
   v=struct.unpack('<H',rd(u,p+2*i,2))[0];cs.append(v)
   if v==0x40ff:break
  else:raise AssertionError('text terminator')
  texts[hex(p)]=dict(codes=cs,decoded=decode(cs));return texts[hex(p)]['decoded']
 cases=[]
 for name,page,slot,permit,schedule in [('copy_short_hours',0,0,1,1),('tobacco_no_permit',1,10,0,2),('tobacco_permitted',1,10,1,2),('tower_closed',2,8,1,6)]:
  u=P.machine(exe);f=P.SP;cols=3 if page==2 else 5
  for r,v in ((UC_MIPS_REG_SP,f),(UC_MIPS_REG_FP,f)):u.reg_write(r,v)
  u.mem_write((f+0x38)&0x1fffffff,raw(0x80010bac,0x80010bb6))
  for a,v in ((f+0x10,1),(f+0x1c,page),(f+0x20,slot),(f+0x50,P.S|0x80000000),(P.S+0xc78,schedule),(0xcd9f8,123456789)):P.put(u,a,v)
  u.mem_write(P.S+0xc74,bytes([permit]));before=rd(u,P.S,5080);draws=[];icons=[];cursor=[]
  intercept={0x80065974,0x80017b18,0x80067338,0x8004e494,0x80041630,0x8004e938}
  def hook(uc,pc,n,c):
   if pc==0x80041374:uc.emu_stop();return
   if pc not in intercept:return
   a=[uc.reg_read(r) for r in (UC_MIPS_REG_A0,UC_MIPS_REG_A1,UC_MIPS_REG_A2,UC_MIPS_REG_A3)]
   if pc==0x80067338:draws.append(dict(kind='inline',x=s16(a[0]),y=s16(a[1]),text=text(uc,a[2])))
   elif pc==0x8004e494:draws.append(dict(kind='message',x=s16(a[0]),y=s16(a[1]),message=a[2],variable0=P.get(uc,0xcd938),money_slots=[P.get(uc,0xe4000),P.get(uc,0xe4004)]))
   elif pc==0x80041630:
    b=rd(uc,uc.reg_read(UC_MIPS_REG_SP)+0x10,24)
    icons.append(dict(x=s16(a[2])+160,y=s16(a[2]>>16)+112,width=a[3]&65535,height=(a[3]>>16)&65535,kind=int.from_bytes(b[:2],'little'),uv=list(b[2:4]),clut=list(struct.unpack_from('<2H',b,4)),rgb=list(b[8:11])))
   elif pc==0x8004e938:cursor.append([s16(a[0]),s16(a[1])])
   uc.reg_write(UC_MIPS_REG_PC,uc.reg_read(UC_MIPS_REG_RA))
  h=u.hook_add(UC_HOOK_CODE,hook);u.emu_start(0x80067cf0,P.STOP,count=150000);u.hook_del(h)
  assert u.reg_read(UC_MIPS_REG_PC)==0x80041374
  assert len(icons)==(9 if page==2 else 15)
  for i,d in enumerate(icons):
   k=order[page*15+i];code=master[k][20];rgb=64 if k in (27,28) and not permit else 128
   assert d==dict(x=60+40*(i%cols),y=88+40*(i//cols),width=32,height=32,kind=25,uv=[32*(code%8),32*(code//8)],clut=[0,491],rgb=[rgb]*3),d
  k=order[page*15+slot];m=master[k]
  heading=next(d for d in draws if d['kind']=='message' and d['x']==48 and d['y']==56);assert heading['message']==387+k
  rate=next(d for d in draws if d['kind']=='message' and d['message']==296);assert rate['money_slots'][0]==m[2]*24
  purchase=next(d for d in draws if d['kind']=='message' and d['message']==28);assert purchase['money_slots'][1]==m[1]
  cap=next(d for d in draws if d['kind']=='message' and d['x']==240 and d['y']==40);att=next(d for d in draws if d['kind']=='message' and d['x']==240 and d['y']==56)
  assert cap['variable0']==m[3] and att['variable0']==m[4]
  assert cursor==[[83+40*(slot%cols),111+40*(slot//cols)]]
  assert rd(u,P.S,5080)==before and P.get(u,0xcd9f8)==123456789
  cases.append(dict(name=name,page=page,slot=slot,fixture=k,schedule=schedule,tobacco_permit=permit,maintenance_display=m[2]*24,purchase_display=m[1],capacity=m[3],attention=m[4],icons=icons,cursor=cursor,draws=draws,store_and_cash_unchanged=True))
 rows=[]
 for j,k in enumerate(order):
  page=j//15;slot=j%15;c=3 if page==2 else 5;m=master[k];code=m[20]
  rows.append(dict(selection=j,page=page,slot=slot,columns=c,fixture=k,label=labels[k]['name'],message=387+k,purchase=m[1],maintenance_display_24h=m[2]*24,capacity=m[3],attention=m[4],icon_code=code,icon_uv=[32*(code%8),32*(code//8)],logical_rect=[60+40*(slot%c),88+40*(slot//c),32,32],requires_tobacco_permit=k in (27,28)))
 z=zipfile.ZipFile(archive);old=z.read('algorithm-analysis/equipment_choice.py')
 out('reuse-audit.json',dict(archive_equipment_choice=dict(path='algorithm-analysis/equipment_choice.py',sha256=hashlib.sha256(old).hexdigest(),known='39choice order/navigation page0/1fivecolumns page2three; permit27/28 and confirm/cancel already decoded.'),reused=['53fixture master and MSG labels','hourly maintenance rates and real daily billing mode','source image/page/renderer conventions'],new_scope='existing selector/master -> actual display calls and Android differences; no claim of newly discovered navigation mechanic'))
 out('original-cases.json',dict(cases=cases,original_entries=4,visual_intercepts=[hex(a) for a in sorted(intercept)],gpu=False,operating_updates=0,staged_frame=True))
 out('equipment-ui-map.json',dict(rows=rows,page_sizes=[15,15,9],page_columns=[5,5,3],paper=[32,24,256,192],maintenance_display='master hourly*24 independent of selected business schedule',real_daily_billing='separate existing mode0 rule',excluded_from_this_menu=[k for k in range(53) if k not in order],selection_index_is_not_fixture_id=True,android_update=False))
 out('inline-texts.json',texts)
 ranges={'catalog_display':(0x80067cf0,0x80068338),'icon_helper':(0x800687c4,0x80068978),'order':(0x800b9920,0x800b99bc),'paper':(0x80010bac,0x80010bb6)}
 out('source-provenance.json',dict(exe_sha256=P.EXE_SHA,ranges={k:dict(start=hex(a),end_exclusive=hex(b),sha256=hashlib.sha256(raw(a,b)).hexdigest()) for k,(a,b) in ranges.items()}))
 asm=Path(asmfile).read_text().splitlines();(ROOT/'equipment-display.asm').write_text('\n'.join(x.rstrip() for x in asm if any(a<=int(x[:8],16)<b for a,b in ranges.values()))+'\n')
 print('4 bounded original equipment displays passed; store/cash unchanged, no input/placement/update')
if __name__=='__main__':main(*sys.argv[1:])
