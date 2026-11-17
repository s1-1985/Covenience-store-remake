#!/usr/bin/env python3
"""Audit prior-art overlap and perform a bounded static lead search for R07.
No emulation, source execution or semantic nonuse claim.
"""
import argparse,hashlib,json,re,struct,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parent
ANALYSIS=ROOT.parent
def sha(b):return hashlib.sha256(b).hexdigest()
def put(n,x):(ROOT/n).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def main():
 ap=argparse.ArgumentParser();ap.add_argument('archive',type=Path);ap.add_argument('disassembly',type=Path);args=ap.parse_args()
 expected=json.loads((ANALYSIS.parent/'archives/20261103-r2/manifest.json').read_text())['sha256'];assert sha(args.archive.read_bytes())==expected;z=zipfile.ZipFile(args.archive)
 exe=z.read('algorithm-analysis/source/SLPS_007.82');assert sha(exe)=='d6a167a1c9e0fe98d7e44e12968caa489ac3eb7ed3b9e46012a188af8432b1fd'
 checks=[]
 for report,path,member in [
  ('20261117-hud-source-data','source-reference/hud_display.py','algorithm-analysis/hud_display.py'),
  ('20261117-hud-source-data','source-reference/text_controls.py','algorithm-analysis/text_controls.py'),
  ('20261117-product-menu-source-data','source-reference/interior_submenu.py','algorithm-analysis/interior_submenu.py')]:
  a=(ANALYSIS/report/path).read_bytes();b=z.read(member);assert a==b;checks.append(dict(report=report,local_path=path,previous_archive_member=member,identical=True,bytes=len(a),sha256=sha(a)))
 a=(ANALYSIS/'20261117-permit-dialog-source-data/source/permit_dialog.bin').read_bytes();b=(ANALYSIS/'20261114-permit-siting-data/source/permit_dialog.bin').read_bytes();assert a==b
 checks.append(dict(report='20261117-permit-dialog-source-data',local_path='source/permit_dialog.bin',previous_repo_path='20261114-permit-siting-data/source/permit_dialog.bin',identical=True,bytes=len(a),sha256=sha(a)))
 rows=[dict(report='20261117-hud-source-data',known=['HUDconstructor4095C','calendar19EB4..1A098','numerictext expansion','weather message selection'],prior=['r2:hud_display.py','r2:text_controls.py','20261116-weather-demand-data'],added='Messages/font/background crop binding and explicit UI input recipes.',classification='source_binding_of_known_rules',new_gameplay_mechanic_established=False),
 dict(report='20261117-product-menu-source-data',known=['27product master records','53fixture choice lists','submenu imageformula/specialcases','permissiongates/navigation'],prior=['20261113-product-stock-data','20261114-permit-siting-data','r2:interior_submenu.py'],added='27menu-image crops,message-name comparison and172choice layout records.',classification='source_binding_of_known_rules',new_gameplay_mechanic_established=False),
 dict(report='20261117-permit-dialog-source-data',known=['permit acquisition/costs','existingpermission preservation','originaldialog code'],prior=['20261114-permit-siting-data','r2:premises_all_control.py'],added='Originaldialog text/display state andfivecontrol crops; reacquisitionreport link.',classification='source_binding_of_known_rules',new_gameplay_mechanic_established=False)]
 put('audit.json',dict(date_jst='2026-11-17',scope='Three most recent user-facing reports only; not exhaustive deduplication of the whole repository.',archive_sha256=expected,exact_duplicate_examples=checks,report_comparisons=rows,assessment='Real additional source bindings, but underlying mechanics already decoded. Choosing them instead of unresolved mechanics was a prioritization error. Do not report them as new mechanics or resolved open issues.',tracked_open_before=6,tracked_open_after=6))
 # Lead-generation scan only. A nearby staff-root constant is not pointer provenance.
 lines=args.disassembly.read_text().splitlines();roots=[];candidates=[];near=[]
 pattern=re.compile(r'^([0-9a-f]{8}): (lw|sw) (\$\w+), 0x10\((\$\w+)\)$')
 for i,line in enumerate(lines):
  if 'addiu' in line and '0x3ff8' in line:roots.append(i)
  m=pattern.match(line)
  if not m or m[4] in ('$fp','$sp'):continue
  pc=int(m[1],16);word=struct.unpack_from('<I',exe,pc-0x80010000+2048)[0]
  assert word>>26 in (0x23,0x2b) and word&65535==16
  item=dict(pc=hex(pc),instruction=line.split(': ',1)[1],raw_word=hex(word));candidates.append(item)
  if any(i-250<=j<i for j in roots):near.append(item)
 assert [x['pc'] for x in near]==['0x80036c6c','0x80037064']
 # Both stores are to store working-summary base800CECEC+2948*currentStore,+16.
 rejected=[]
 for pc,start in [(0x80036c6c,0x80036bf0),(0x80037064,0x80036fe0)]:
  context=[x for x in lines if x[:8].isalnum() and start<=int(x[:8],16)<pc+4]
  code=exe[start-0x80010000+2048:pc+4-0x80010000+2048]
  rejected.append(dict(pc=hex(pc),classification='not_staff_word16',reason='Base registerv0 is rebuilt from0x800CECEC plus2948*currentStore before thisstore. It writes working-summary+16, notstaff-record+16.',context=context,source_start=hex(start),source_end_exclusive=hex(pc+4),source_sha256=sha(code)))
 put('staff-word16-leads.json',dict(issue='R07',method='Lexical scan for non-stack lw/sw offset16, with staff-base lowpart3FF8 appearing within preceding250disassembly lines; manual base-register checks for two leads. Raw instruction words checked against original EXE.',disassembly_sha256=sha(args.disassembly.read_bytes()),candidate_count=len(candidates),staff_base_lowpart_occurrences=len(roots),nearby_leads=near,rejected_leads=rejected,result='No new semantic read/update path established. R07 remainsopen.',limitations=['Heuristic lead generation only, not complete pointer/dataflow analysis.','Offset+16 may be reached via other offsets, passed pointers, aliases or byte operations.','The disassembly may contain embedded data; candidates are not asserted reachable code.','No universal unused-field claim; no cooldown/availability interpretation for69120.'],original_cpu_calls=0))
 print(json.dumps(dict(audited_reports=3,exact_duplicate_examples=len(checks),word16_candidates=len(candidates),nearby_leads=len(near),new_mechanics_established=0,original_cpu_calls=0)))
if __name__=='__main__':main()
