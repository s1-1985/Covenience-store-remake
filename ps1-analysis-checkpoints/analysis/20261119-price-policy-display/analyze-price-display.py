#!/usr/bin/env python3
"""Original price-display blocks; capture visual calls, stop before UI input.
Reuse known editor/price formulas; no gameplay or card execution.
"""
import argparse,hashlib,importlib.util,json,runpy,struct,zipfile
from pathlib import Path
from unicorn import UC_HOOK_CODE
from unicorn.mips_const import *
ROOT=Path(__file__).resolve().parent;HELPER=ROOT.parent/'20261117-festival-customer-state-data/analyze-festival-state.py'
spec=importlib.util.spec_from_file_location('machine_helper',HELPER);P=importlib.util.module_from_spec(spec);spec.loader.exec_module(P)
def sha(b):return hashlib.sha256(b).hexdigest()
def out(n,d):(ROOT/n).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
def s16(v):v&=65535;return v-65536 if v>=32768 else v
def trunc(n,d):return (abs(n)//d)*(1 if n>=0 else -1)
def rd(u,a,n):return bytes(u.mem_read(a&0x1fffffff,n))
def u32(u,a):return struct.unpack('<I',rd(u,a,4))[0]

def main(archive):
 z=zipfile.ZipFile(archive);exe=z.read('algorithm-analysis/source/SLPS_007.82');assert sha(exe)==P.EXE_SHA
 raw=lambda a,n:exe[a-0x80010000+2048:a-0x80010000+2048+n]
 defaults=[struct.unpack_from('<i',raw(0x8009cdf0+88*i,88),32)[0] for i in range(27)]
 dec=runpy.run_path(str(ROOT.parent/'20261114-staff-roster-growth-data/source-reference/psmoji.py'))['decode'];inline={}
 def text(uc,address):
  cs=[]
  while True:
   v=struct.unpack('<H',rd(uc,address+2*len(cs),2))[0];cs.append(v)
   if v==0x40ff:break
   assert len(cs)<200
  inline[hex(address)]={'codes':cs,'decoded_template':dec(cs),'sha256':sha(rd(uc,address,2*len(cs)))}
  return inline[hex(address)]['decoded_template']
 visual={0x80065974,0x80017b18,0x80067338,0x8004e494,0x80018940,0x800182d0,0x80069438}
 def run(name,entry,settings):
  u=P.machine(exe);s=P.S
  for i,v in enumerate(settings):P.put(u,s+0xc7c+4*i,v)
  # Cash26 deliberately differs, with no inventory/fixture/sale data supplied.
  P.put(u,s+0xc7c+26*4,99)
  before=rd(u,s,5080);draws=[]
  for r,v in [(UC_MIPS_REG_SP,P.SP),(UC_MIPS_REG_FP,P.SP),(UC_MIPS_REG_RA,P.STOP),(UC_MIPS_REG_A0,s+0x80000000)]:u.reg_write(r,v)
  def code(uc,pc,n,c):
   if pc==0x80041374:uc.emu_stop();return
   if pc in visual:
    a=[uc.reg_read(r) for r in [UC_MIPS_REG_A0,UC_MIPS_REG_A1,UC_MIPS_REG_A2]]
    if pc==0x80067338:draws.append({'kind':'inline','x':s16(a[0]),'y':s16(a[1]),'pointer':hex(a[2]),'text':text(uc,a[2])})
    if pc==0x8004e494:draws.append({'kind':'message','x':s16(a[0]),'y':s16(a[1]),'message':a[2],'numeric_i32':struct.unpack('<i',rd(uc,0xcd938,4))[0]})
    uc.reg_write(UC_MIPS_REG_PC,uc.reg_read(UC_MIPS_REG_RA))
  h=u.hook_add(UC_HOOK_CODE,code);u.emu_start(entry,P.STOP,count=1000000);u.hook_del(h)
  assert u.reg_read(UC_MIPS_REG_PC)==0x80041374,hex(u.reg_read(UC_MIPS_REG_PC))
  assert rd(u,s,5080)==before
  shown=s16(u32(u,0xcd83c));mean_delta=s16(u32(u,0xcd7d4));changes=[v-defaults[i] for i,v in enumerate(settings)]
  target_delta=trunc(sum(changes),26) if entry==0x80062cfc else changes[0]
  target_shown=trunc(sum(settings),26) if entry==0x80062cfc else settings[0]
  assert shown==target_shown
  if entry==0x80062cfc:assert mean_delta==target_delta
  label=next(a for a in draws if a['kind']=='inline' and a['y']==128 and a['x'] in [180,200])
  assert label['pointer']==hex(0x80099c64 if target_delta>0 else 0x80099c74 if target_delta<0 else 0x80099c6c)
  if target_delta:
   delta_number=next(a for a in draws if a['kind']=='message' and a['x']==164 and a['y']==128)
   assert delta_number['numeric_i32']==abs(target_delta)
  elif entry==0x80062cfc:assert not any(a['kind']=='message' and a['x']==164 and a['y']==128 for a in draws)
  return {'name':name,'entry':hex(entry),'settings26':settings,'cash26_setting':99,'model':{'mean_or_selected_setting':target_shown,'mean_or_selected_delta':target_delta},'displayed_setting':shown,'label':label,'draw_calls':draws,'store_record_unchanged':True,'stop':'before original input/update41374'}
 base=defaults[:26];assert min(base)>0 and base[0]+26<=100
 cases=[]
 mixed=base.copy();mixed[0]+=1;mixed[1]-=1
 one=base.copy();one[0]+=26
 fraction=base.copy();fraction[0]+=6
 for name,values in [('initial_settings',base),('mixed_changes_zero_mean',mixed),('single_product_plus26',one),('single_product_plus6_zero_delta',fraction),('all_minus1',[v-1 for v in base])]:cases.append(run(name,0x80062cfc,values))
 for delta in [-1,0,1]:
  values=base.copy();values[0]+=delta;cases.append(run('individual_first_delta'+str(delta),0x80063714,values))
 out('original-cases.json',{'cases':cases,'original_block_entries':8,'operating_updates':0,'gameplay_callee_replacements':0,'visual_callee_intercepts':[hex(a) for a in sorted(visual)],'scope':'Normal price-setting ranges injected in an otherwise zeroed diagnostic store; no original title/shop acquisition/stock/editor input/confirm/cancel loop or GPU output. The first individual item is selected by original initialization.'})
 out('inline-templates.json',{'rows':inline,'source':'Original EXE inline UTF16 glyph/control words; existing decoder reused.'})
 out('price-display-rules.json',{'editable_products':list(range(26)),'setting_field':'store+C7C+4*product','default_field':'product master9CDF0+88*product+32','group_average':'trunc(sum(settings0..25)/26)','group_delta':'trunc(sum(settings[i]-defaults[i] for i0..25)/26)','weighting':'No fixture, stock, sale quantity, revenue or cash26 weighting in this display calculation. Not the store-choice price metric.','group_label':'mean_delta==0 -> 定価, even if individual settings differ; >0 UP; <0 OFF with magnitude. Fractional mean delta truncates toward zero.','group_positions':{'mean_setting':[192,96],'delta_suffix':[200,128],'delta_magnitude':[164,128],'zero_label':[180,128]},'individual':'Selected product setting=default+temporary delta; delta is shown independently with magnitude%UP / magnitude%OFF / 定価; selected setting at[160,144], nameMSG71+id at[120,112].','comparison_to_economy':'Original UI coefficient, not sales-weighted gross margin; unit price formula already decoded elsewhere.','existing_editor_rules_reused':'26-item temporary array,0..100 boundaries,group all-or-nothing step,confirm/cancel semantics already known and not retested here.','apk_updated':False})
 spans=[('group_average',0x80062cfc,0x80062ea8),('group_display',0x80062ea8,0x800631b4),('individual_init_and_display',0x80063714,0x80063b3c)]
 out('source-provenance.json',{'exe_sha256':sha(exe),'archive_sha256':sha(archive.read_bytes()),'helper_sha256':sha(HELPER.read_bytes()),'ranges':[{'name':n,'start':hex(a),'end_exclusive':hex(b),'sha256':sha(raw(a,b-a))} for n,a,b in spans],'master_defaults27':defaults,'existing_rules':'../20261113-pricing-store-choice-data/README.md','reuse_audit_scope':'Existing pricing report, field/bridge JSON and source-reference model names. Large historical snapshot logs excluded.','paused_issues_investigated':False})
 print(json.dumps({'entries':8,'group':[{'case':c['name'],'display':c['displayed_setting'],'label':c['label']['text']} for c in cases[:5]],'individual_labels':[c['label']['text'] for c in cases[5:]]},ensure_ascii=False))
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('archive',type=Path);main(ap.parse_args().archive)
