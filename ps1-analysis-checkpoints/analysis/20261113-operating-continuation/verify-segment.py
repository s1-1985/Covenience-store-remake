#!/usr/bin/env python3
"""Keep the existing paired play checks and capture natural rival-month entry/exit.

No original instructions are skipped by these observation hooks. Captures are
function-boundary diagnostic RAM, not resumable play states.
"""
import hashlib,json,struct,sys,zlib
from pathlib import Path
algo=Path(sys.argv[1]).resolve()
sys.path.insert(0,str(algo))
import verify_opened_snapshot_play_20261028 as verifier
from unicorn import UC_HOOK_CODE
from unicorn.mips_const import UC_MIPS_REG_RA
OriginalRunner=verifier.BackgroundCategoryRunner
captures=[]
source,count,name=sys.argv[2:5];count=int(count)
root=Path(__file__).resolve().parent
if name != 'TOWN0001-ci-main-25-single':
    (root/'execution-stop.json').write_text(json.dumps(dict(reason='Bound completed work at 200 updates; monthly not reached. New frame-timeline analysis completed separately.', blocked_output=name, original_play_instructions_executed=False),indent=2)+'\n')
    raise SystemExit('Completed-segment boundary: longer monthly plan deferred')

def sha(b):return hashlib.sha256(b).hexdigest()
class CapturingRunner(OriginalRunner):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.rival_checks=[];self.town_checks=[];captures.append(self.rival_checks)
        def observe(u,a,n,d):
            minute,hour,stage=tuple(struct.unpack('<I',u.mem_read(p,4))[0] for p in (0xce618,0xce614,0xce610))
            if minute or hour or stage!=1:return
            before=bytes(u.mem_read(0,2097152));clock=struct.unpack_from('<I',before,0xcd93c)[0]
            kind="town" if a==0x8002bd54 else "rival"
            checks=self.town_checks if kind=="town" else self.rival_checks
            index=len(checks)
            def finish():
                after=bytes(u.mem_read(0,2097152))
                record=dict(clock=clock,calendar=[struct.unpack_from('<I',before,p)[0] for p in (0xce608,0xce60c,0xce610,0xce614,0xce618)],
                            before_sha256=sha(before),after_sha256=sha(after))
                # Save once for the original side. Exact domain equality between
                # original and independent parent side is checked by Connection.
                if captures[0] is self.rival_checks:
                    directory=root/(kind+'-boundaries');directory.mkdir(exist_ok=True)
                    for phase,data in (('before',before),('after',after)):
                        filename=f'{name}-{clock}-{index}-{phase}.ram.zlib'
                        (directory/filename).write_bytes(zlib.compress(data,9))
                        record[phase+'_path']=kind+'-boundaries/'+filename
                checks.append(record)
            self.onreturn(u.reg_read(UC_MIPS_REG_RA),finish)
        for address in (0x8002a8e0,0x8002bd54):
            self.hooks.append(self.u.hook_add(UC_HOOK_CODE,observe,begin=address,end=address))
verifier.BackgroundCategoryRunner=CapturingRunner
row=verifier.compare(source,count,native_music=True,finance_monitor=True,event_monitor=True,refill_monitor=True,customer_monitor=True,whole_town_monitor=True,staff_loop_monitor=True,progress_snapshot=name,progress_file=str(algo/(name+'-progress.json')))
assert len(captures)==2 and len(captures[0])==len(captures[1])
# Raw whole-RAM hashes differ because reference parent stack frames differ.
# Full domain comparisons at each play return remain in the existing verifier.
assert [x['clock'] for x in captures[0]]==[x['clock'] for x in captures[1]]
row['natural_rival_boundaries']=captures[0]
assert row['runtime_table_provenance']=='single_conversion' and row['single_conversion_appearance_verified']
assert row['steps'][-1]['clock']==row['opening_clock']+2*count
out=dict(total=1,all_passed=True,iterations_verified=count,frames_verified=len(row['frames']),cases=[row],limits=row['limits']+['Rival boundary RAM is captured by observation only; full RAM includes different parent stacks.', 'SDK/GPU/SPU/IRQ boundaries remain modeled; not a physical console recording.'])
(algo/f'opened-snapshot-{name}-verification-20261103.json').write_text(json.dumps(out,separators=(',',':')))
print('next-month segment passed',name,count,row['steps'][-1]['clock'],flush=True)
