#!/usr/bin/env python3
"""Original bounded display blocks with controlled focus and selection; no ordinary UI replay."""
import hashlib,importlib.util,json,runpy,struct,sys
from pathlib import Path
from unicorn import UC_HOOK_CODE
from unicorn.mips_const import *
ROOT=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('helper',ROOT.parent/'20261117-festival-customer-state-data/analyze-festival-state.py');P=importlib.util.module_from_spec(spec);spec.loader.exec_module(P)
def out(n,x):(ROOT/n).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def rd(u,a,n):return bytes(u.mem_read(a&0x1fffffff,n))
def s16(v):v&=65535;return v-65536 if v&32768 else v

def main(exefile,asmfile):
 exe=Path(exefile).read_bytes();assert hashlib.sha256(exe).hexdigest()==P.EXE_SHA
 raw=lambda a,b:exe[a-0x80010000+2048:b-0x80010000+2048]
 decode=runpy.run_path(str(ROOT.parent/'20261114-staff-roster-growth-data/source-reference/psmoji.py'))['decode'];strings={}
 def text(u,a):
  cs=[]
  for i in range(200):
   v=struct.unpack('<H',rd(u,a+2*i,2))[0];cs.append(v)
   if v==0x40ff:break
  else:raise AssertionError('unterminated text')
  strings[hex(a)]=dict(codes=cs,decoded=decode(cs));return strings[hex(a)]['decoded']
 costs=[struct.unpack('<i',raw(0x8009fe58+44*i,0x8009fe5c+44*i))[0] for i in range(5)]
 cases=[]
 for name,flags,focus in [('none_focus_DM',[0]*5,0),('DM_newspaper_focus_inactive_TV',[1,1,0,0,0],4),('all_focus_airship',[1]*5,2)]:
  u=P.machine(exe);f=P.SP;draws=[];icons=[];cursors=[]
  u.reg_write(UC_MIPS_REG_SP,f);u.reg_write(UC_MIPS_REG_FP,f)
  P.put(u,f+0x20,focus);u.mem_write((f+0x30)&0x1fffffff,bytes(flags))
  # Distinct live settings prove this block reads the staged editor copy.
  u.mem_write(0xe3688,b'\x00\x01\x00\x01\x00');live=rd(u,0xe3688,5)
  intercept={0x80065974,0x80017b18,0x80067338,0x8004e494,0x80018940,0x80041630,0x8004e938}
  def hook(uc,pc,n,c):
   if pc==0x80041374:uc.emu_stop();return
   if pc not in intercept:return
   a=[uc.reg_read(r) for r in (UC_MIPS_REG_A0,UC_MIPS_REG_A1,UC_MIPS_REG_A2,UC_MIPS_REG_A3)]
   if pc==0x80067338:draws.append(dict(kind='inline',x=s16(a[0]),y=s16(a[1]),pointer=hex(a[2]),text=text(uc,a[2])))
   elif pc==0x8004e494:draws.append(dict(kind='message',x=s16(a[0]),y=s16(a[1]),message=a[2],value=struct.unpack('<i',rd(uc,0xe4000,4))[0]))
   elif pc==0x80041630:
    sp=uc.reg_read(UC_MIPS_REG_SP);b=rd(uc,sp+0x10,24)
    icons.append(dict(x=s16(a[2])+160,y=s16(a[2]>>16)+112,width=a[3]&65535,height=(a[3]>>16)&65535,kind=int.from_bytes(b[:2],'little'),uv=list(b[2:4]),clut=list(struct.unpack_from('<2H',b,4)),rgb=list(b[8:11])))
   elif pc==0x8004e938:cursors.append([s16(a[0]),s16(a[1])])
   uc.reg_write(UC_MIPS_REG_PC,uc.reg_read(UC_MIPS_REG_RA))
  h=u.hook_add(UC_HOOK_CODE,hook);u.emu_start(0x80069d30,P.STOP,count=100000);u.hook_del(h)
  assert u.reg_read(UC_MIPS_REG_PC)==0x80041374
  total=P.get(u,(f+0x24)&0x1fffffff);assert total==sum(c for c,b in zip(costs,flags) if b==1)
  assert len(icons)==5
  for i,d in enumerate(icons):
   assert d==dict(x=68+40*i,y=88,width=32,height=32,kind=29,uv=[224,96+32*i],clut=[0,495],rgb=[128 if flags[i]==1 else 64]*3),d
  money=[d for d in draws if d['kind']=='message' and d['message']==272]
  assert [(d['y'],d['value']) for d in money]==[(56,costs[focus]),(72,total)]
  assert cursors==[[95+40*focus,117]],cursors
  assert rd(u,0xe3688,5)==live
  cases.append(dict(name=name,staged_flags=flags,focus=focus,focused_cost=costs[focus],displayed_total=total,live_flags_unchanged=list(live),icons=icons,cursor_anchor=cursors[0],draws=draws))
 ranges={'display':(0x80069d30,0x8006a110),'icon_record':(0x8006a304,0x8006a44c),'cursor_adjust':(0x8005fdd4,0x8005fe54),'input_and_writeback_known':(0x8006a110,0x8006a304),'inline_texts':(0x800b9360,0x800b9484)}
 out('original-cases.json',dict(display_cases=cases,original_entries=3,actual_gpu=False,operating_updates=0,stop='before41374',intercepted_children=[hex(x) for x in sorted(intercept)]))
 out('inline-texts.json',strings)
 out('source-provenance.json',dict(exe_sha256=P.EXE_SHA,ranges={k:dict(start=hex(a),end_exclusive=hex(b),sha256=hashlib.sha256(raw(a,b)).hexdigest()) for k,(a,b) in ranges.items()}))
 out('android-bridge.json',dict(focus_independent_of_staged_selection=True,selected_rgb=[128]*3,unselected_rgb=[64]*3,focused_cost_xy=[None,56],selected_total_xy=[None,72],money_alignment='x=152+8*(11-original65820(value))',icons=[dict(id=i,rect=[68+40*i,88,32,32],source_image='PS_CM1.TIM',source_rect=[224,32*i,32,32]) for i in range(5)],cursor_anchor_rule=[95,117,40],known_reused=['44byte master/costs','five persistent selected bytes, commit/cancel and no immediate payment','PS_CM1 pixels,kind29 UV/CLUT binding'],new_binding=['independent focus cost/name and selected total','selection RGB128/64 independent of focus','original icon and cursor display coordinates'],android_diff=dict(commit='22ba479999c4e025727806454b9858364ca145cc',path='game/scripts/ps1_ui.gd',function='_advertising',findings=['tap immediately calls try_purchase_promotion','total reads promotions_used_this_month','icons y96 instead of original88','paper51,45,230,120 instead of40,24,256,144']),apk_updated=False))
 asm=Path(asmfile).read_text().splitlines();(ROOT/'advertising-display.asm').write_text('\n'.join(line.rstrip() for line in asm if any(a<=int(line[:8],16)<b for a,b in ranges.values()))+'\n')
 print('3 bounded original display cases passed; focused cost, total, five icon records and cursor agree')
if __name__=='__main__':main(*sys.argv[1:])
