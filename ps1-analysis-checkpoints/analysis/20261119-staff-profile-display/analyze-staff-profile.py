#!/usr/bin/env python3
"""Bound original shared hiring/transfer profile reader, capturing visual calls only."""
import hashlib, importlib.util, json, struct, sys, runpy
from pathlib import Path
from unicorn import UC_HOOK_CODE
from unicorn.mips_const import *
ROOT = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('helper', ROOT.parent/'20261117-festival-customer-state-data/analyze-festival-state.py')
P = importlib.util.module_from_spec(spec); spec.loader.exec_module(P)
def out(n,v): (ROOT/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def main(exefile,asmfile):
 exe=Path(exefile).read_bytes(); assert hashlib.sha256(exe).hexdigest()==P.EXE_SHA
 dec=runpy.run_path(str(ROOT.parent/'20261114-staff-roster-growth-data/source-reference/psmoji.py'))['decode']
 cases=[]
 for name,wage,hours,experience in [('hiring_24h_new',280,24,0),('transfer_12h_experienced',280,12,1),('five_digit_wage',420,24,2)]:
  u=P.machine(exe); staff=0x143ff8; person=4; a=staff+person*60
  record=bytearray(60);record[3]=31;record[4]=1
  struct.pack_into('<h',record,8,4);struct.pack_into('<i',record,12,wage);struct.pack_into('<i',record,20,experience)
  # Maximum/current energy intentionally differ, as do hidden/current work skills.
  for offset,value in {24:100,25:51,26:61,27:73,28:88,29:42,30:9,31:10,32:11,33:12,34:13}.items():record[offset]=value
  u.mem_write(a,bytes(record)); text=[]; bars=[]; faces=[]; direct=[]
  def hook(uc,pc,n,c):
   args=[uc.reg_read(r) for r in (UC_MIPS_REG_A0,UC_MIPS_REG_A1,UC_MIPS_REG_A2,UC_MIPS_REG_A3)]
   if pc==0x8004e494:
    text.append(dict(x=args[0],y=args[1],message=args[2],integer=P.get(uc,0xcd938),money=P.get(uc,0xe4000)))
   elif pc==0x80067338:
    codes=[]
    for i in range(80):
     code=struct.unpack('<H',uc.mem_read((args[2]&0x1fffffff)+2*i,2))[0];codes.append(code)
     if code==0x40ff:break
    direct.append(dict(x=args[0],y=args[1],pointer=hex(args[2]),text=dec(codes),codes=codes))
   elif pc==0x800675dc: faces.append(args)
   elif pc==0x800182d0:
    bars.append(dict(x=args[0]&65535,y=args[0]>>16,width=args[1]&65535,height=args[1]>>16,style=args[3]))
    uc.reg_write(UC_MIPS_REG_V0,1)
   elif pc==0x80018940: pass
   else:return
   uc.reg_write(UC_MIPS_REG_PC,uc.reg_read(UC_MIPS_REG_RA))
  h=u.hook_add(UC_HOOK_CODE,hook)
  for r,v in zip((UC_MIPS_REG_A0,UC_MIPS_REG_A1,UC_MIPS_REG_A2,UC_MIPS_REG_A3),(146,48,person,hours)):u.reg_write(r,v)
  P.call(u,0x800703e4);u.hook_del(h)
  assert bytes(u.mem_read(a,60))==bytes(record)
  amount=next(x for x in text if x['message']==296)
  assert amount['money']==wage*hours and amount['x']==(186 if wage*hours>=10000 else 194)
  assert [d['integer'] for d in text if d['message']==369]==[51,42,73,88]
  assert [(b['width'],b['style']) for b in bars[:-1]]==[(24,3),(48,4),(20,3),(35,3),(42,3)]
  assert [(b['x'],b['y'],b['height']) for b in bars[:-1]]==[(162,112,16),(162,112,16),(162,128,16),(162,144,16),(162,160,16)]
  assert faces==[[146,48,4,0xffffff80]]
  assert direct[0]['text']==('経験なし' if experience==0 else '経験あり'), direct
  cases.append(dict(name=name,wage_base=wage,hours_argument=hours,experience=experience,drawn_text=text,direct_text=direct,rectangles=bars,portraits=faces,staff_record_unchanged=True))
 out('original-cases.json',dict(cases=cases,original_top_level_entries=3,preparation_entries=2,operating_updates=0,visual_functions_intercepted=['4E494','67338','675DC','182D0','18940'],native_float_conversion_and_multiplication_executed=True,scope='Controlled profile record and arguments; no natural UI/GPU/payroll/hiring commit.'))
 spans={'profile_reader':(0x800703e4,0x80070f48),'hiring_caller':(0x8006efcc,0x8006f020),'transfer_caller':(0x80071b38,0x80071b84),'labels':(0x800b9670,0x800b96b0)}
 raw=lambda a,b:exe[a-0x80010000+2048:b-0x80010000+2048]
 out('source-provenance.json',dict(exe_sha256=P.EXE_SHA,ranges={k:dict(start=hex(a),end_exclusive=hex(b),sha256=hashlib.sha256(raw(a,b)).hexdigest()) for k,(a,b) in spans.items()}))
 asm=Path(asmfile).read_text().splitlines();(ROOT/'profile-reader.asm').write_text('\n'.join(x.rstrip() for x in asm if any(a<=int(x[:8],16)<b for a,b in spans.values()))+'\n')
 print('3 original profile entries passed; original floating arithmetic executed; staff unchanged')
if __name__=='__main__':main(*sys.argv[1:])
