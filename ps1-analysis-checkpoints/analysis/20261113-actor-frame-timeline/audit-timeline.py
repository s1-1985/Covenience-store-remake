#!/usr/bin/env python3
"""Audit each observed frame against its preceding original actor construction."""
import collections,hashlib,json,zlib
from pathlib import Path
ROOT=Path(__file__).resolve().parent
src=ROOT/'second-store-results.json'
raw=src.read_bytes() if src.exists() else zlib.decompress(Path(str(src)+'.zlib').read_bytes())
d=json.loads(raw);rows=d['cases'];frames=[f for f in d['frames'] if f['mask']&512]
assert d['all_passed'] and frames
by=collections.defaultdict(list)
for f in frames:
 k=f['display_constructions'];assert 1<=k<=len(rows)
 row=rows[k-1]
 expected=''.join(row['records_hex'])
 assert f['count']==row['count'] and f['records_hex']==expected
 by[k].append(f)
assert all(len({f['records_sha256'] for f in group})==1 for group in by.values())
move=[];unchanged=[];poses={}
for ordinal,row in enumerate(rows,1):
 for p in row['personnel']:
  if p['state']==0:
   matches=[a for a in row['actors'] if a['source']=='resting_staff' and a['id']==p['id']]
  else:
   image=640+p['appearance']*4+d['direction_image_offsets'][p['direction']]
   matches=[a for a in row['actors'] if a['source']=='grid' and a['cell']==p['cell'] and a['image']==image]
  assert len(matches)==1,(ordinal,p,matches)
  a=matches[0];pose=(tuple(p['cell']),p['direction'],p['state'],p['appearance'])
  old=poses.get(p['id'])
  if old:
   if old['pose']==pose:
    assert old['uv']==a['uv'] and old['pixel']==a['pixel']
    unchanged.append(dict(person=p['id'],before=old['ordinal'],after=ordinal))
   if old['pose'][0]!=pose[0]:
    move.append(dict(person=p['id'],before=old['ordinal'],after=ordinal,cell_before=old['pose'][0],cell_after=p['cell'],pixel_before=old['pixel'],pixel_after=a['pixel'],direction=p['direction'],uv=a['uv']))
  poses[p['id']]=dict(ordinal=ordinal,pose=pose,pixel=a['pixel'],uv=a['uv'])
assert move and unchanged
sameclock=collections.defaultdict(list)
for f in frames:sameclock[f['clock']].append(f)
result=dict(all_passed=True,source_sha256=hashlib.sha256(raw).hexdigest(),diagnostic_iterations=d['iterations'],
 original_actor_constructions=len(rows),total_frames=len(d['frames']),actor_frames=len(frames),
 observed_construction_groups=len(by),same_construction_repeated_frames=sum(len(fs)-1 for fs in by.values()),
 unchanged_pose_transitions=len(unchanged),staff_cell_transitions=len(move),movements=move,
 frame_record_clock_deltas=dict(collections.Counter(str(f['clock']-rows[f['display_constructions']-1]['clock']) for f in frames)),
 frame_callers=dict(collections.Counter(f['caller'] for f in frames)),
 stale_records=[dict(clock=f['clock'],record_clock=rows[f['display_constructions']-1]['clock'],caller=f['caller'],construction=f['display_constructions']) for f in frames if f['clock']!=rows[f['display_constructions']-1]['clock']],
 same_clock_with_different_records=[dict(clock=c,frames=len(fs),constructions=sorted({f['display_constructions'] for f in fs})) for c,fs in sameclock.items() if len({f['records_sha256'] for f in fs})>1],
 limits=['CPU frame-dispatch calls, not measured real display frames or wall time.',
 'Frame counter is zero under this SDK boundary; do not infer PAL/NTSC/Hz or speed.',
 'Observed original actor records match the latest logical cell/pose; no intermediate coordinate or footstep texture was observed in this branch.',
 'Fixed pose alone does not prove absence of all animation in other routines, actors, or scenes.',
 'Diagnostic input branch; excluded from natural continuation update totals.'])
(ROOT/'audit.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items() if k not in ('movements','limits')}))
