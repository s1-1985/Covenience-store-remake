#!/usr/bin/env python3
"""Canonical MIPS address references and bounded pointer-use search for R04.
No execution; deliberately does not prove global nonuse or field semantics.
"""
import argparse,hashlib,json,struct,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parent
def sha(b):return hashlib.sha256(b).hexdigest()
def put(n,x):(ROOT/n).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def main():
 ap=argparse.ArgumentParser();ap.add_argument('archive',type=Path);args=ap.parse_args()
 manifest=json.loads((ROOT.parent.parent/'archives/20261103-r2/manifest.json').read_text());assert sha(args.archive.read_bytes())==manifest['sha256'];z=zipfile.ZipFile(args.archive)
 exe=z.read('algorithm-analysis/source/SLPS_007.82');assert sha(exe)=='d6a167a1c9e0fe98d7e44e12968caa489ac3eb7ed3b9e46012a188af8432b1fd'
 start=struct.unpack_from('<I',exe,0x18)[0];length=struct.unpack_from('<I',exe,0x1c)[0];data=exe[2048:2048+length];words=struct.unpack('<'+'I'*(len(data)//4),data[:len(data)//4*4])
 table=0x8009fcd8;end=table+18*20;slot=0x800cd87c
 def decode(i):
  w=words[i];return dict(pc=start+i*4,word=w,op=w>>26,rs=w>>21&31,rt=w>>16&31,rd=w>>11&31,funct=w&63,imm=w&65535,simm=struct.unpack('<h',struct.pack('<H',w&65535))[0])
 refs=[]
 for i,w in enumerate(words):
  d=decode(i)
  if d['op'] not in (9,13,0x20,0x21,0x23,0x24,0x25,0x28,0x29,0x2b):continue
  for j in range(i-1,max(-1,i-9),-1):
   p=decode(j)
   if p['op']==15 and p['rt']==d['rs']:
    address=((p['imm']<<16)|d['imm']) if d['op']==13 else ((p['imm']<<16)+d['simm'])&0xffffffff
    if table<=address<end or address==slot:
     refs.append(dict(pc=hex(d['pc']),word=hex(w),target=hex(address),target_kind='project_master' if table<=address<end else 'selected_row_pointer',operation={9:'addiu',13:'ori',0x20:'lb',0x21:'lh',0x23:'lw',0x24:'lbu',0x25:'lhu',0x28:'sb',0x29:'sh',0x2b:'sw'}[d['op']],lui_pc=hex(p['pc']),base_register=d['rs'],value_register=d['rt'],context_words=[hex(x) for x in words[j:i+1]]))
    break
 direct=[r for r in refs if r['target_kind']=='project_master'];shared=[r for r in refs if r['target_kind']=='selected_row_pointer']
 assert [r['pc'] for r in direct]==['0x80029134','0x8006a608','0x8006ae1c','0x80075420']
 assert len(shared)==17 and all(0x8006a44c<=int(r['pc'],16)<0x8006b1cc for r in shared)
 # For each canonical selected-pointer load, follow only straight-line register
 # copies and immediate offsets. Stop at control transfer; no hidden path claims.
 accesses={};escapes=[]
 for r in shared:
  if r['operation']!='lw':continue
  seed=(int(r['pc'],16)-start)//4;tags={r['value_register']:0}
  for i in range(seed+1,min(len(words),seed+65)):
   d=decode(i);op=d['op'];rs=d['rs'];rt=d['rt'];rd=d['rd'];fun=d['funct'];pc=d['pc']
   if op in (1,2,3,4,5,6,7) or op==0 and fun in (8,9):
    if op==3 and any(a in tags for a in (4,5,6,7)):escapes.append(dict(seed=r['pc'],pc=hex(pc),kind='possible_pointer_argument',tagged_args=[a for a in (4,5,6,7) if a in tags]))
    break
   if op in (0x20,0x21,0x23,0x24,0x25,0x28,0x29,0x2b):
    if rs in tags:
     key=hex(pc);accesses[key]=dict(pc=key,word=hex(d['word']),field_offset=tags[rs]+d['simm'],operation={0x20:'lb',0x21:'lh',0x23:'lw',0x24:'lbu',0x25:'lhu',0x28:'sb',0x29:'sh',0x2b:'sw'}[op])
    if op in (0x20,0x21,0x23,0x24,0x25):tags.pop(rt,None)
    elif rt in tags:escapes.append(dict(seed=r['pc'],pc=hex(pc),kind='pointer_stored',value_register=rt))
   elif op in (8,9):
    old=tags.get(rs);tags.pop(rt,None)
    if old is not None:tags[rt]=old+d['simm']
   elif op==0:
    copy=tags.get(rs) if fun in (0x21,0x25) and rt==0 else tags.get(rt) if fun in (0x21,0x25) and rs==0 else None
    if fun not in (0x10,0x11,0x12,0x13,0x18,0x19,0x1a,0x1b):tags.pop(rd,None)
    if copy is not None:tags[rd]=copy
   else:tags.pop(rt,None)
   tags.pop(0,None)
   if not tags:break
 fields=sorted({x['field_offset'] for x in accesses.values()});assert fields==[0,12] and not escapes
 literal_hits={hex(a):[hex(start+i) for i in range(0,len(data)-3,4) if struct.unpack_from('<I',data,i)[0]==a] for a in [table,slot]}
 gp=0x800cd6c4;gphits=[]
 for i,w in enumerate(words):
  d=decode(i)
  if d['rs']==28 and d['op'] in (0x20,0x21,0x23,0x24,0x25,0x28,0x29,0x2b) and (gp+d['simm'])&0xffffffff==slot:gphits.append(hex(d['pc']))
 put('project-reference-index.json',dict(exe_sha256=sha(exe),archive_sha256=manifest['sha256'],scan_payload=dict(address=hex(start),bytes=len(data),includes_data=True),table=dict(start=hex(table),end_exclusive=hex(end),stride=20),selected_row_pointer=hex(slot),canonical_table_references=direct,canonical_selected_pointer_references=shared,bounded_field_accesses=sorted(accesses.values(),key=lambda x:int(x['pc'],16)),observed_offsets_in_bounded_pointer_paths=fields,pointer_argument_or_store_leads=escapes,literal_word_references=literal_hits,gp_relative_slot_references=gphits,scope='LUI + signedlow/load/store orLUI+ORI within8instructions. Canonical candidates manually inspected inoriginal disassembly. Pointeruses limitedto64straightline instructions andstop at control transfer; notfull CFG/dataflow.'))
 prior=ROOT.parent/'20261115-town-project-data/project-master.json'
 put('unknown-field-status.json',dict(issue='R04',fields=[2,4,6,8,16],status='open',new_evidence='Canonicalwholepayloadreference inventory identifies sharedrowpointer0x800CD87C;17canonicalreferences allinsideoriginalstartmenu. Boundedfollowing of15pointerloads onlyreaches+0/+12. No newsemanticreader forfiveunknownfields found.',existing_evidence='Previousreport alreadyestablished+0kind/+12cost at selectedsites. Do notcount these again asnewmechanics.',raw_values_reference='../20261115-town-project-data/project-master.json',raw_values_reference_sha256=sha(prior.read_bytes()),limitations=['No proof of nonuse through noncanonical addressing, unaligned pointerliterals,computedaliases or overlays.','Immediateaddress candidates caninclude embeddeddata; no reachability assumption.','No field renamed from numeric similarity.'],original_cpu_calls=0,original_operating_updates=0))
 print(json.dumps(dict(canonical_table_refs=len(direct),canonical_shared_pointer_refs=len(shared),bounded_field_accesses=len(accesses),bounded_offsets=fields,literal_hits=literal_hits,gp_relative_hits=gphits,new_field_meanings=0,original_cpu_calls=0)))
if __name__=='__main__':main()
