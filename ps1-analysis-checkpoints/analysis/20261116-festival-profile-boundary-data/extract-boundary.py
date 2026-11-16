#!/usr/bin/env python3
"""Extract static festival/profile144 boundary operands; no CPU simulation."""
import argparse,hashlib,json,runpy,struct
from pathlib import Path
R=Path(__file__).resolve().parent
DISC_SHA='8d8eda789c5a2fe892a4722719b0466dd7d126eed6cd99ad05a807d81b57d1c1'
EXE_SHA='d6a167a1c9e0fe98d7e44e12968caa489ac3eb7ed3b9e46012a188af8432b1fd'
def sha(b):return hashlib.sha256(b).hexdigest()
def put(n,v):(R/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def main():
 ap=argparse.ArgumentParser();ap.add_argument('disc',type=Path);args=ap.parse_args();raw=args.disc.read_bytes();assert sha(raw)==DISC_SHA
 entries,read=runpy.run_path(str(R.parent/'20261113-disc-data-extraction/extract-disc-data.py'))['iso'](raw);fs={x['path']:x for x in entries}
 def payload(n):v=fs[n];return read(v['lba'],v['bytes'])
 exe=payload('/SLPS_007.82');assert sha(exe)==EXE_SHA
 def at(a,n):return exe[a-0x80010000+2048:a-0x80010000+2048+n]
 profile_addr=0x800a09d0+144*24;p=at(profile_addr,24);signed=list(struct.unpack('24b',p));assert signed[2]==-126 and signed[8]==-111 and signed[12]==0 and signed[14:17]==[0,0,0]
 put('adjacent-text-operands.json',dict(address=hex(profile_addr),raw_hex=p.hex(),signed_bytes=signed,prior_decoding='赤い女子大生',is_valid_profile=False,valid_profile_count=144,schedule_subscript=signed[2],primary_product_subscript=signed[8],arrival_mode=signed[12],score_weights=signed[14:17],source_range_for_mode0=struct.unpack('<i',at(0x80099570,4))[0],scope='Existing adjacent-string identification reused; operands are conditional misreads, not a valid person or observed customer.'))
 schedules=[]
 for j in range(7):
  a=0x80099de5+j*45+signed[2];v=struct.unpack('b',at(a,1))[0];schedules.append(dict(schedule=j,address=hex(a),signed_byte=v,passes_nonzero_schedule_check=v!=0,within_selected_schedule_row=False))
 assert [x['schedule'] for x in schedules if x['passes_nonzero_schedule_check']]==[0,3,5]
 put('schedule-aliases.json',dict(formula='0x80099de5 + 45*store.C78 + signed(profile[2])',rows=schedules,meaning='Original26c34 tests nonzero, including negative values. These are out-of-row reads, not opening-hour flags for profile144.'))
 aliases=[]
 for j in range(10):
  a=0x800ce65c+j*168+44+signed[8]*4
  desc=('pre-summary global data; meaning not established' if j<2 else 'store-order[0] at0x800ce61c' if j==2 else f'summary[{j-3}].stock[15]')
  aliases.append(dict(store_slot=j,address=hex(a),relative_to_own_summary=44+signed[8]*4,aliases=desc))
 assert aliases[2]['address']=='0x800ce61c'
 put('stock-aliases.json',dict(formula='0x800ce65c + 168*store_slot + 0x2c + 4*(-111)',required='signed32 value >0 at26cf0',rows=aliases,scope='Address alias only. Values depend on live globals/summary. No assertion that an initial or natural play store passes.'))
 worlds=[]
 for name in ('TOWN0001','TOWN0002','TOWN0003','TOWNPS'):
  b=payload('/DAT/'+name+'.BIN');stores=[]
  for j in range(10):
   s=b[25907+j*5080:25907+(j+1)*5080]
   if not s[0]:continue
   schedule=struct.unpack_from('<i',s,0xc78)[0];stores.append(dict(slot=j,schedule=schedule,profile144_schedule_byte=schedules[schedule]['signed_byte'],profile144_rejected_at_schedule=schedules[schedule]['signed_byte']==0))
  worlds.append(dict(map=name,town_sha256=sha(b),stores=stores))
 assert sum(len(w['stores']) for w in worlds)==11 and all(s['profile144_rejected_at_schedule'] for w in worlds for s in w['stores'])
 put('initial-store-boundary.json',worlds)
 rules=dict(demand_write=dict(instruction='0x80026868',base='0x8013c0dc + 5080*store_slot',relative_to_store='0xDE4 + 2*profile_id',profile144_offset=0xde4+2*144,alias='store+0xF04: first customer state byte and next byte',condition='Only if selector26a64 returns a store, not merely if festival bypass is nonzero',operation='unsigned16(old_alias + mix_head_count), low16 stored',scope='Conditional static write alias; natural runtime corruption or crash not observed'),demand_total=dict(loop_guard='0x80026958',profiles='0..143',includes144=False),spawn=dict(wrap_guard='0x80031B50..0x80031B5C',modulus=144,profile_write='0x80031E78',profiles='0..143',profile144_selected=False,scope='The regular spawn selector cannot assign profile144. A conditional write toF04 could still affect an existing/stale slot; this is not proof of no indirect effects.'),normal_gate=dict(seasonal='negative primary product returns2 at80027344..8002736c',bypass='nonzeroCDA00 skips weather/season/share at80026600'),android=dict(population='Preserve source mix136 heads, including the one invalid-profile head',demand='Validate0<=profile<144 before any table or store access, in all event branches',customer='Do not invent a145th shopper or reinterpret adjacent string as wallet/items',memory_alias='Do not reproduce unsafe cross-record writes as a gameplay feature'),remaining='Live selector operands and indirect first-slot effects under a naturally reached festival with eligible altered schedules are not established; R02 remains open but narrowed.')
 assert rules['demand_write']['profile144_offset']==0xf04
 put('boundary-rules.json',rules)
 blocks=[('adjacent_text',profile_addr,24),('schedule_alias_window',0x80099d67,271),('arrival_ranges',0x80099570,16),('festival_demand_gate_write',0x800265d0,0x8002686c-0x800265d0),('demand_total_loop',0x8002694c,0x80026a30-0x8002694c),('store_selector_gates',0x80026a64,0x80026e78-0x80026a64),('spawn_wrap',0x80031ac8,0x80031be4-0x80031ac8),('spawn_slot_assignment',0x80031e3c,0x80031e7c-0x80031e3c)]
 ranges=[]
 for n,a,size in blocks:
  b=at(a,size);(R/'source'/f'{n}.bin').write_bytes(b);ranges.append(dict(file=f'source/{n}.bin',address=hex(a),bytes=size,sha256=sha(b)))
 put('source-ranges.json',dict(disc_sha256=DISC_SHA,exe_sha256=EXE_SHA,ranges=ranges))
 put('summary.json',dict(date_jst='2026-11-16',valid_profiles=144,invalid_profile_id=144,source_maps=4,source_initial_stores=11,initial_stores_rejected_by_schedule=11,schedule_choices=7,conditional_schedule_pass_choices=[0,3,5],stock_alias_rows=10,regular_spawn_max_profile=143,demand144_conditional_store_offset='0xF04',original_cpu_updates=0,status='R02 open; static downstream boundary and source initial-store rejection established',known_before='Mix136/profile144 adjacent string, normal seasonal rejection and festival bypass were known. New joins: seven schedule aliases, ten summary aliases,11 source schedules, conditional first-slot write and regular spawn exclusion.'))
 print('Extracted seven schedule aliases, ten summary aliases, eleven initial-store rejects and spawn/write boundary.')
if __name__=='__main__':main()
