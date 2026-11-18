#!/usr/bin/env python3
"""Original survey ranking leaf with text calls captured, not GPU rendering."""
import argparse,hashlib,importlib.util,json,struct,zipfile
from pathlib import Path
from unicorn import UC_HOOK_CODE
from unicorn.mips_const import *
ROOT=Path(__file__).resolve().parent
HELPER=ROOT.parent/'20261117-festival-customer-state-data/analyze-festival-state.py'
sp=importlib.util.spec_from_file_location('machine_helper',HELPER);P=importlib.util.module_from_spec(sp);sp.loader.exec_module(P)
def sha(b):return hashlib.sha256(b).hexdigest()
def save(n,d):(ROOT/n).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
def ranked(values):return sorted(range(27),key=lambda i:(-values[i],i))[:8]
def model(values,column):
 ids=ranked(values);names=[];numbers=[]
 for row,i in enumerate(ids):
  if values[i]:
   names.append({'x':32 if column==0 else 164,'y':80+16*row,'message':71+i})
   numbers.append({'x':120 if column==0 else 252,'y':80+16*row,'message':369,'value_u32':values[i]})
 return ids,names+numbers

def main(archive):
 z=zipfile.ZipFile(archive);exe=z.read('algorithm-analysis/source/SLPS_007.82');assert sha(exe)==P.EXE_SHA
 inputs=[]
 left=[0]*27;right=[0]*27
 # Example counts patterned on the supplied survey screenshot; IDs are test inputs.
 for i,v in [(6,62),(10,38),(7,22),(18,17),(22,16),(3,15),(25,13),(23,12)]:left[i]=v
 inputs.append(('eight_left_empty_right',left,right))
 left=[0]*27;right=[0]*27
 for i in [1,3,5,7,9,11,13,15,17]:left[i]=10
 for i,v in [(0,2),(2,5),(4,5),(26,1)]:right[i]=v
 inputs.append(('ties_cutoff_and_independent_right',left,right))
 inputs.append(('all_zero',[0]*27,[0]*27));cases=[]
 for name,left,right in inputs:
  u=P.machine(exe)
  # Third counter must not affect survey ranking or rendering.
  for i,(a,b) in enumerate(zip(left,right)):u.mem_write(P.S+0x1198+12*i,struct.pack('<III',a,b,1000000+i))
  u.reg_write(UC_MIPS_REG_A0,P.S+0x80000000);draws=[];ranks={}
  def code(uc,pc,n,c):
   if pc in [0x800472d0,0x800476c4]:
    fp=uc.reg_read(UC_MIPS_REG_FP)&0x1fffffff;ranks['left' if pc==0x800472d0 else 'right']=list(struct.unpack('<8I',uc.mem_read(fp+0x20,32)))
   if pc==0x8004e494:
    x=uc.reg_read(UC_MIPS_REG_A0);y=uc.reg_read(UC_MIPS_REG_A1);msg=uc.reg_read(UC_MIPS_REG_A2)
    d={'x':x,'y':y,'message':msg}
    if msg==369:d['value_u32']=struct.unpack('<I',uc.mem_read(0xcd938,4))[0]
    draws.append(d);uc.reg_write(UC_MIPS_REG_PC,uc.reg_read(UC_MIPS_REG_RA))
  h=u.hook_add(UC_HOOK_CODE,code);before=bytes(u.mem_read(P.S,5080));P.call(u,0x800470e4);u.hook_del(h)
  il,dl=model(left,0);ir,dr=model(right,1)
  assert ranks=={'left':il,'right':ir} and draws==dl+dr,(name,ranks,draws)
  assert bytes(u.mem_read(P.S,5080))==before
  cases.append({'case':name,'left_u32':left,'right_u32':right,'source_selected_indices':ranks,'captured_text_calls':draws,'store_record_unchanged':True})
 save('original-cases.json',{'source_leaf':'0x800470e4','cases':cases,'original_function_entries':3,'text_renderer_replacements_per_case':1,'replacement_scope':'4E494 text renderer captured and returned; source ranking, memset and caller argument construction run unchanged. No actual glyph/GPU output or complete menu loop.','gameplay_function_replacements':0,'operating_updates':0})
 rules={'products':27,'rows_per_column':8,'left':{'title':'買った商品','base_offset':'0x1198'},'right':{'title':'欲しかった物','base_offset':'0x119c'},'counter_stride':12,'counter_compare':'unsigned32 strict greater; descending; ties lower product ID first','zero':'Selected ranks may contain zero values but emit neither label nor number; no placeholder or percent. Both columns independent.','messages':{'product_name':'71+product_id (existing source label mapping reused)','count':369},'positions':{'left_name_x':32,'left_count_x':120,'right_name_x':164,'right_count_x':252,'first_y':80,'row_step_y':16},'scope':'Original logical coordinates, not screenshot pixels or phone pixels. Counts, not sales money or share percentages.','third_counter_11a0':'Not read by this survey leaf; do not substitute its values.','lifetime':'Existing main-update rule clears1198/119c for27 products at month-stage1/hour0/minute0; month-to-date, not all-time. Third counter is not cleared by that loop.','store_navigation':{'source':'46E1C..46EC4','next_mask':'0x2000','previous_mask':'0x8000','wrap':'next from last ->0, previous from0 -> count-1','order':'original1BD78 owner-store list, existing helper reused; not all rival stores'},'source_leaf':'0x800470e4..0x800478f8','new_vs_reused':'New read-side top8/ties/independent zero filtering and placement; known monthly reset, counters and product labels reused.','apk_updated':False}
 save('survey-rules.json',rules)
 spans=[('survey_wrapper',0x80046a84,0x80046f0c),('rank_and_draw',0x800470e4,0x800478f8),('monthly_counter_reset',0x8002359c,0x80023670),('wanted_counter_update',0x8003444c,0x800344d0),('purchase_counter_update',0x80034a5c,0x80034ae8),('research_menu_branch',0x800628f8,0x80062938)]
 save('source-provenance.json',{'exe_sha256':sha(exe),'archive_sha256':sha(archive.read_bytes()),'helper_sha256':sha(HELPER.read_bytes()),'ranges':[{'name':n,'start':hex(a),'end_exclusive':hex(b),'sha256':sha(exe[a-0x80010000+2048:b-0x80010000+2048])} for n,a,b in spans],'reused':['../20261116-inspection-lifetime-data/README.md','../20261117-product-menu-source-data/product-labels.json','../20261103-operating-continuation/source-reference/main_update_control.py'],'reuse_audit_scope':'Existing Markdown/Python and small JSON plus recovered source-reference. Large historical CPU snapshot JSON excluded; no claim of exhaustive archive discovery.'})
 print(json.dumps({'original_leaf_calls':3,'all_model_matches':True,'cases':[c['case'] for c in cases],'gameplay_calls':0}))
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('archive',type=Path);main(ap.parse_args().archive)
