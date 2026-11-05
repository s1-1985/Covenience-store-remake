"""Restore our own 0.3.0 native release after an ephemeral workspace reset.
Run GDRE Tools v2.7.4 --recover=APK --scripts-only for baseline and release,
then pass: source_apk baseline_apk recovered_source_dir recovered_baseline_dir.
Unchanged scripts/functions keep their original source and comments.
"""
from pathlib import Path
import hashlib,json,re,shutil,sys,zipfile
root=Path(__file__).resolve().parents[1]
apk,oldapk,newdir,olddir=map(Path,sys.argv[1:])
assert hashlib.sha256(apk.read_bytes()).hexdigest()=='55e186fdeb4be2b2c9a3f2953f2ddcea687a9687a8331374b217bf0cfaa57743'
def chunks(text):
 matches=list(re.finditer(r'^(?:static )?func (\w+)\(',text,re.M))
 prefix=text[:matches[0].start()] if matches else text
 return prefix,{m.group(1):text[m.start():matches[i+1].start() if i+1<len(matches) else len(text)] for i,m in enumerate(matches)}
def norm(text):return '\n'.join(l.rstrip() for l in text.expandtabs(4).splitlines() if l.strip())
def style(text):
 text=text.expandtabs(4)
 text=re.sub(r': =', ':=', text)
 text=re.sub(r'(?<! ):=', ' :=', text)
 text=re.sub(r':=(?! )', ':= ', text)
 text=re.sub(r'\n{4,}', '\n\n\n', text)
 text=re.sub(r'-> void :', '-> void:', text)
 return '\n'.join(line.rstrip() for line in text.splitlines()) + '\n'
changed=[];unchanged=[];retained=0
with zipfile.ZipFile(apk) as new,zipfile.ZipFile(oldapk) as old:
 oldnames=set(old.namelist())
 for entry in new.namelist():
  if entry.startswith('assets/scripts/') and entry.endswith('.gdc'):
   rel=Path(entry.removeprefix('assets/')).with_suffix('.gd');dest=root/'game'/rel
   if entry in oldnames and new.read(entry)==old.read(entry):unchanged.append(str(rel));continue
   n=(newdir/rel).read_text();parts=[]
   if dest.exists() and (olddir/rel).exists():
    op,of=chunks(dest.read_text());bp,bf=chunks((olddir/rel).read_text());np,nf=chunks(n)
    parts.append(op if norm(np)==norm(bp) else style(np))
    for name,code in nf.items():
     if name in bf and name in of and norm(code)==norm(bf[name]):parts.append(of[name]);retained+=1
     else:parts.append(style(code))
   else:parts=[style(n)]
   dest.parent.mkdir(parents=True,exist_ok=True);dest.write_text(''.join(parts));changed.append(str(rel))
  elif entry.startswith('assets/data/') and entry.endswith('.json') or entry=='assets/locale/ja.po':
   dest=root/'game'/entry.removeprefix('assets/');dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(new.read(entry))
for i in range(3):
 shutil.copy2(root/f'assets/raw/ps1_disc_analysis_v1/images/TIM0_SYOP_S0{i}.png',root/f'game/assets/ps1/shop_page_{i}.png')
manifest=dict(apk_sha256=hashlib.sha256(apk.read_bytes()).hexdigest(),release='0.3.0-analysis-integration',recovery_tool='GDRE Tools v2.7.4',changed_scripts=changed,unchanged_scripts=unchanged,original_function_blocks_retained=retained,notes='Original feature commits and comments in changed functions were lost with the workspace. Runtime code was recovered from our signed APK; no additional game rules were invented. Recovered scripts are validated separately before push.')
(root/'docs/handoff/2026-11-05-v03-recovery.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(manifest,ensure_ascii=False,indent=2))
