"""Continue source-created24h/manager branch, no clock/roster/cash/seed edits."""
from verify_opened_snapshot_play_20261028 import compare,R
import json,sys
source,count,name=sys.argv[1:4];count=int(count)
assert len(sys.argv) in (4,5) and (len(sys.argv)==4 or sys.argv[4]=='no-staff')
# Segments01/02 predate the live staff adapter. Preserve their exact scope on replay.
live_staff=len(sys.argv)==4
row=compare(source,count,native_music=True,finance_monitor=True,event_monitor=True,refill_monitor=True,customer_monitor=True,whole_town_monitor=True,staff_loop_monitor=live_staff,progress_snapshot=name,progress_file=str(R/(name+'-progress.json')))
assert row['runtime_table_provenance']=='single_conversion' and row['single_conversion_appearance_verified']
assert row['steps'][-1]['clock']==row['opening_clock']+2*count
out=dict(total=1,all_passed=True,iterations_verified=count,frames_verified=len(row['frames']),cases=[row],limits=row['limits']+['This branch starts at a prior source-created24h or manager-transfer UI state. No gameplay clock/owner/staff/cash/RNG injection after restore.', 'Branch roots have different elapsed clocks, UI history and RNG states. Observed revenues are examples, not a matched causal estimate of manager transfer.'])
(R/f'opened-snapshot-{name}-verification-20261103.json').write_text(json.dumps(out,separators=(',',':')))
print('operating branch passed',name,count,len(row['frames']),row['steps'][-1]['clock'],row['steps'][-1]['cash'],flush=True)
