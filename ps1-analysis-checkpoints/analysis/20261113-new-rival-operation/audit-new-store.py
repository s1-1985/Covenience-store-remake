#!/usr/bin/env python3
"""Audit a naturally created rival's first operating day from paired live traces."""
import collections, hashlib, json, struct, sys, zlib
from pathlib import Path
ROOT=Path(__file__).resolve().parent
algo=Path(sys.argv[1]).resolve()
START='TOWN0001-ci-main-31-single'
EXE=algo/'source/SLPS_007.82'
exe=EXE.read_bytes()
assert hashlib.sha256(exe).hexdigest()=='d6a167a1c9e0fe98d7e44e12968caa489ac3eb7ed3b9e46012a188af8432b1fd'
def raw(a,n):return exe[a-0x80010000+2048:a-0x80010000+2048+n]
def state(name):
 p=algo/'source/opened-snapshots-20261028'/name
 meta=json.loads(p.with_suffix('.json').read_text())
 ram=zlib.decompress(Path(str(p)+'.ram.zlib').read_bytes())
 assert hashlib.sha256(ram).hexdigest()==meta['ram_sha256']
 return meta,ram
start_meta,start=state(START)
slot=3;offset=0x12b2f8+5080*slot
assert start[offset] and struct.unpack_from('<H',start,offset+4)[0]>>15==1
refs=list(struct.unpack_from('<3h',start,offset+0xdd8))
schedule=struct.unpack_from('<i',start,offset+0xc78)[0]
hours=list(raw(0x80099de5+schedule*45,24))
checks={k:[] for k in ('source_spawn_checks','customer_loop_checks','whole_staff_loop_checks','restock_checks','stock_posting_checks','midnight_finance_checks')}
segments=[];prior=start_meta;normal_clocks=[]
for index in range(32,35):
 name=f'TOWN0001-ci-main-{index:02d}-single'
 proofpath=algo/f'opened-snapshot-{name}-verification-20261103.json'
 proof=json.loads(proofpath.read_text());row=proof['cases'][0]
 assert proof['all_passed'] and row['snapshot_sha256']==prior['ram_sha256']
 meta,ram=state(name);assert meta['parent_snapshot_sha256']==prior['ram_sha256']
 assert struct.unpack_from('<3h',ram,offset+0xdd8)==tuple(refs)
 assert struct.unpack_from('<i',ram,offset+0xc78)[0]==schedule
 assert all(s['active_slots']==[0,1,2,3] for s in row['steps'])
 assert len(row['steps'])==len(row['master_reasons'])
 normal_clocks.extend(s['clock'] for s,reason in zip(row['steps'],row['master_reasons']) if reason=='normal')
 for k in checks:checks[k].extend(row[k])
 segments.append(dict(name=name,iterations=proof['iterations_verified'],clock=row['steps'][-1]['clock'],ram_sha256=meta['ram_sha256'],proof_sha256=hashlib.sha256(proofpath.read_bytes()).hexdigest()))
 prior=meta
spawn=[x for x in checks['source_spawn_checks'] if x['store_slot']==slot]
customers=[x for x in checks['customer_loop_checks'] if x['store_slot']==slot]
staff=[x for x in checks['whole_staff_loop_checks'] if x['store_slot']==slot]
assert len(spawn)==len(customers)==len(staff)==len(normal_clocks)
assert [x['clock'] for x in spawn]==[x['clock'] for x in customers]==[x['clock'] for x in staff]==normal_clocks
for x in spawn:
 # Native cache uses integer clock minutes modulo24 hours in this trajectory.
 assert (x['reason']!='not_open')==bool(hours[(x['clock']//60)%24]),('schedule gate',x)
for x in staff:
 assert [p['id'] for p in x['before']]==refs==[p['id'] for p in x['after']]
opening_trace=next(x for x in spawn if x['clock']==23460)
closing_trace=next(x for x in spawn if x['clock']==24420)
assert opening_trace['reason']!='not_open' and closing_trace['reason']=='not_open'
created=[x for x in spawn if x['reason']=='created']
sales=[x for x in customers if x['revenue_after']!=x['revenue_before']]
assert all(x['revenue_after']>=x['revenue_before'] for x in sales)
refills=[x for x in checks['restock_checks'] if x['store_slot']==slot]
postings=[x for x in checks['stock_posting_checks'] if x['store_slot']==slot]
movement=[];turns=[];energy=[];transitions=collections.Counter()
for x in staff:
 for a,b in zip(x['before'],x['after']):
  if a['position'][:2]!=b['position'][:2]:movement.append(dict(clock=x['clock'],id=a['id'],before=a['position'],after=b['position']))
  elif a['position'][2]!=b['position'][2]:turns.append(dict(clock=x['clock'],id=a['id'],before=a['position'],after=b['position']))
  if a['energy']!=b['energy']:energy.append(dict(clock=x['clock'],id=a['id'],before=a['energy'],after=b['energy']))
  if a['state']!=b['state']:transitions[f"{a['state']}->{b['state']}"]+=1
closes=checks['midnight_finance_checks'];assert len(closes)==1 and closes[0]['clock']==24480
assert slot in closes[0]['store_order']
ending=struct.unpack_from('<5i',ram,offset+0xd9c)
assert ending[4]==sum(x['revenue_after']-x['revenue_before'] for x in sales)
opening_ledger=struct.unpack_from('<5i',start,offset+0xd88)
closing_postings=[x for x in postings if x['clock']<24480]
additional_goods=sum(x['amount'] for x in closing_postings if not x['income'])
assert ending[3]==opening_ledger[3]+additional_goods
assert ending[4]==opening_ledger[4]+sum(x['amount'] for x in closing_postings if x['income'])
# At the midnight update, original finance runs before per-store work.
lastrow=json.loads((algo/'opened-snapshot-TOWN0001-ci-main-34-single-verification-20261103.json').read_text())['cases'][0]
groups=[]
for call in lastrow['master_calls']:
 if call[0]==0x8004095c:groups.append([])
 groups[-1].append(call)
assert len(groups)==len(lastrow['steps'])
midnight_index=next(j for j,x in enumerate(lastrow['steps']) if x['clock']==24480)
sequence=groups[midnight_index]
finance_index=next(j for j,c in enumerate(sequence) if c[0]==0x80029334)
new_staff_index=next(j for j,c in enumerate(sequence) if c==[0x80036ac0,[0x8012b2f8+3*5080]])
assert finance_index<new_staff_index
call_words=[]
for target in (0x80029334,0x80036ac0):
 for pc in range(0x80023438,0x80023c20,4):
  word=struct.unpack('<I',raw(pc,4))[0]
  if word>>26==3 and (((pc+4)&0xf0000000)|((word&0x3ffffff)<<2))==target:
   call_words.append(dict(pc=hex(pc),word=hex(word),target=hex(target)))
assert len(call_words)==2
next_day_postings=[x for x in postings if x['clock']>=24480 and not x['income']]
next_day_goods=sum(x['amount'] for x in next_day_postings)
current_ledger=struct.unpack_from('<5i',ram,offset+0xd88)
assert current_ledger[3]==next_day_goods and current_ledger[4]==0
closed_goods=[x for x in postings if not x['income'] and not hours[(x['clock']//60)%24]]
assert closed_goods and next_day_postings[0]['clock']==24480 and next_day_postings[0]['amount']==180
assert next_day_postings[0]['cash_before'][1]==closes[0]['cash_after'][1]
midnight_order=dict(clock=24480,finance_trace_index=finance_index,new_store_staff_trace_index=new_staff_index,
 original_jal_words=call_words,first_after_close_posting=next_day_postings[0],
 old_day_postings_use_strict_clock_less_than=24480,
 reason='Finance closes and resets day ledgers before staff work at the same clock. The180 expense at clock24480 belongs to the new day.')
assert created and movement and sales and postings
staff_summary=[]
for role,ident in enumerate(refs):
 observed=[p for x in staff for p in x['after'] if p['id']==ident]
 capability_changes=[dict(offset=hex(j),before=start[0x143ff8+ident*60+j],after=ram[0x143ff8+ident*60+j]) for j in range(0x1a,0x28) if start[0x143ff8+ident*60+j]!=ram[0x143ff8+ident*60+j]]
 staff_summary.append(dict(role_index=role,id=ident,capability_field_changes=capability_changes,state_counts=dict(collections.Counter(p['state'] for p in observed)),movement_steps=sum(x['id']==ident for x in movement),direction_changes=sum(x['id']==ident for x in turns),energy_range=[min(p['energy'] for p in observed),max(p['energy'] for p in observed)]))
report=dict(all_passed=True,slot=slot,company=1,staff_ids=refs,schedule_index=schedule,
 scheduled_open_hours=[j for j,v in enumerate(hours) if v],
 segments=segments,start_ram_sha256=start_meta['ram_sha256'],completed_iterations=prior['completed_iterations'],
 verified_loops_per_domain=len(staff),spawn_reasons=dict(collections.Counter(x['reason'] for x in spawn)),
 opening_trace=opening_trace,closing_trace=closing_trace,first_created=created[0],created_groups=len(created),created_people=sum(x['quantity'] for x in created),
 first_revenue=sales[0],sales_postings=len(sales),additional_revenue=sum(x['revenue_after']-x['revenue_before'] for x in sales),
 staff_summary=staff_summary,staff_movement_steps=len(movement),staff_direction_only_changes=len(turns),staff_state_transitions=dict(transitions),
 staff_energy_changes=len(energy),staff_effects=dict(collections.Counter(e for x in staff for e in x['effects'])),
 first_movement=movement[0],first_energy_change=energy[0] if energy else None,
 restock_checks=len(refills),stock_postings=len(postings),first_ledger_posting=postings[0],first_goods_posting=next((x for x in postings if not x['income']),None),
 midnight=closes[0],midnight_order=midnight_order,next_day_goods=next_day_goods,current_day_ledger=list(current_ledger),closed_hours_goods_amount=sum(x['amount'] for x in closed_goods),closed_hours_goods_postings=closed_goods,opening_day_ledger=list(opening_ledger),additional_goods=additional_goods,previous_day_ledger=list(ending),
 limits=['Natural trajectory without input/cash/clock/roster/RNG edits.',
 'Each paired live loop compares model bytes and original RAM; original child routines remain shared by the paired parent execution.',
 'Position changes are logical half-tile coordinates, not a rendered-pixel or real-time animation test.',
 'Unvisited restock paths are disclosed by counts; task execution is not assumed from the staff roster.',
 'Previous-day sales and goods reconcile to individual postings. Opening day-ledger goods includes38260 initial equipment already paid at the monthly birth boundary; it is not charged again by this audit.',
 'GPU/SPU/IRQ/SDK boundaries are modeled, as in the archived runner.'])
(ROOT/'new-store-audit.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:report[k] for k in ('all_passed','created_groups','created_people','additional_revenue','staff_movement_steps','restock_checks','previous_day_ledger')}))
