#!/usr/bin/env python3
"""Link source acquisition/sale prices, inspection UI and ownership resets to11 stores."""
import argparse,hashlib,json,runpy,struct
from pathlib import Path
ROOT=Path(__file__).resolve().parent
DISC_SHA='8d8eda789c5a2fe892a4722719b0466dd7d126eed6cd99ad05a807d81b57d1c1'
EXE_SHA='d6a167a1c9e0fe98d7e44e12968caa489ac3eb7ed3b9e46012a188af8432b1fd'
def sha(b):return hashlib.sha256(b).hexdigest()
def put(n,x):(ROOT/n).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def i32(v):return (v+2**31)%2**32-2**31
def main():
 ap=argparse.ArgumentParser();ap.add_argument('disc',type=Path);a=ap.parse_args();raw=a.disc.read_bytes();assert sha(raw)==DISC_SHA
 iso=runpy.run_path(str(ROOT.parent/'20261113-disc-data-extraction/extract-disc-data.py'))['iso'];rows,read=iso(raw);files={r['path']:r for r in rows}
 def payload(p):r=files[p];return read(r['lba'],r['bytes'])
 exe=payload('/SLPS_007.82');assert sha(exe)==EXE_SHA
 def at(a,n):return exe[a-0x80010000+2048:a-0x80010000+2048+n]
 fee=(struct.unpack('<I',at(0x80060fe4,4))[0]&65535)<<16|(struct.unpack('<I',at(0x80060fe8,4))[0]&65535);assert fee==500000
 assert struct.unpack('<I',at(0x80061030,4))[0]==0x00021840 # sll v1,v0,1 -> twice asset sum
 avs=json.loads((ROOT.parent/'20261115-rival-management-data/initial-withdrawal-values.json').read_text());assets={(x['map'],x['slot']):x for x in avs}
 source_worlds={x['map']:x for x in json.loads((ROOT.parent/'20261115-rival-management-data/initial-rival-inputs.json').read_text())}
 allquotes=[];stafflinks=[];worlds=[]
 for name in ('TOWN0001','TOWN0002','TOWN0003','TOWNPS'):
  data=payload('/DAT/'+name+'.BIN');assert sha(data)==source_worlds[name]['source_town_sha256'];cash=list(struct.unpack_from('<2i',data,1));town=data[17:24017];stores=[]
  for slot in range(10):
   b=data[25907+slot*5080:25907+(slot+1)*5080]
   if not b[0]:continue
   asset=assets[(name,slot)];rect=list(struct.unpack_from('<4i',b,8));assert rect==asset['rect'];l,t,r,bot=rect
   land=sum(struct.unpack_from('<b',town,(y*60+x)*8+2)[0]*1000000 for y in range(t,bot+1) for x in range(l,r+1));assert land==asset['land_refund']
   fl=struct.unpack_from('<H',b,4)[0];low=fl&255;inspection=0 if b[2]==1 else fee;price=i32(i32(land+asset['premises_refund'])*2);ids=list(struct.unpack_from('<3h',b,0xdd8));guard=low==1
   quote=dict(map=name,slot=slot,flags=fl,owner_bit15=fl>>15,serial_low8=low,rect=rect,inspection_flag=b[2],inspection_quote=inspection,land_value=land,
     premises_components={k:asset[k] for k in ('equipment','inventory','premises_refund')},base_asset=land+asset['premises_refund'],acquisition_price=price,sale_or_withdrawal_asset_value=land+asset['premises_refund'],
     original_main_store_acquisition_guard=guard,initial_cash_covers_acquisition=cash[0]>=price,initial_cash_covers_inspection=cash[0]>=inspection,
     minimum_cash_direct_acquisition=None if guard else price,staff_ids=ids,normal_sale_open_flag_C77=b[0xc77],note='All these original stores are rivals. Price/sale values are valuation inputs; not valid direct player sale states or fully initialized normal acquisition states.')
   allquotes.append(quote);stores.append(slot)
   for position,sid in enumerate(ids):
    if sid==-1:continue
    person=data[24017+sid*54:24017+(sid+1)*54];owner=struct.unpack_from('<H',person)[0]
    stafflinks.append(dict(map=name,store_slot=slot,store_flags=fl,position=position,person_id=sid,source_owner=owner,
      on_acquisition='Owner u16 changes to new player store serial; person skills/wage/energy not reset by binding mode1.',
      on_sale='Owner u16 becomes0; runtime byte+0x19 copies+0x18; store reference becomes-1 before store initialization.',acquisition_allowed_by_initial_main_guard=not guard))
  worlds.append(dict(map=name,source_town_sha256=sha(data),source_cash=cash,source_rival_slots=stores,initial_acquisition_candidates=sum(not q['original_main_store_acquisition_guard'] for q in allquotes if q['map']==name)))
 put('initial-store-quotes.json',allquotes);put('initial-staff-transfer-links.json',stafflinks);put('source-map-inputs.json',worlds)
 controls=[]
 for known in (0,1):
  for low in (1,2):
   controls.append(dict(inspection_flag=known,serial_low8=low,fee_display=0 if known==1 else fee,
    ui_path='Detailed report only;4D6EC returns default2 after acknowledgement' if known==1 else 'Unknown-store three-choice menu: investigate0,buy1,no-op2',
    acquisition_parent_first_choice_guard=low==1,note='Native UI child routing and parent guards both matter. Do not invent second-menu choices after investigation.'))
 put('inspection-state-routing.json',controls)
 resets=[dict(offset='0x'+format(a,'x'),bytes=n,value='zero') for a,n in [(0xce8,80),(0xd38,80),(0xd88,80),(0x1184,2),(0x1188,4),(0x118c,4),(0x1190,1),(0x1194,4),(0x1198,0x144),(0x12e1,4)]]
 resets.append(dict(offset='0x12e8',bytes=240,value='60 signed32 entries0x80000000'))
 put('ownership-field-policy.json',dict(acquisition=dict(store_flags='Replace u16+4 with incremented player serial0x800cd9e0; ownership bit15 becomes0 in normal serial domain.',staff='All nonnegative references among+DD8/+DDA/+DDC retain identity and rebind owner to new flags.',reset_by_binding_mode1=resets,
   retained_by_binding=['store geometry+8..+0x17','interior dimensions/floor/fixture/stock data','C68 evaluation,C6C popularity','C70 tier','C74..C76 permits','C78 opening schedule','C7C..CE4 product settings','DD8..DDC staff references'],
   caveat='List covers binding child only, before native town reactivation/cache refresh. Derived cache bytes may be overwritten by following helpers; no full post-gameplay byte identity claim.'),
 sale=dict(unbind='Release staff ownership and set store staff references-1 before closure.',town='Source close clears original rectangle corners through kind12 placement, initializes store and rebuilds town masks.',store_reset='Initialize5080-byte record: inactive, evaluation10,popularity20,3 staff refs-1,profit history sentinels; copy selected defaults from first-store template as original mode0.',retained='No promise that prior store interior survives sale.')))
 dec=runpy.run_path(str(ROOT.parent/'20261114-staff-roster-growth-data/source-reference/psmoji.py'))['decode'];msg_path=next(p for p in files if p.endswith('/MSG00.OBJ'));msg=payload(msg_path)
 def stream(b,off):
  cs=[]
  for k in range(200):
   c=struct.unpack_from('<H',b,off+2*k)[0];cs.append(c)
   if c==0x40ff:return cs
  raise AssertionError('no terminator')
 texts=[]
 for index in (298,299,300,301,497):
  off=struct.unpack_from('<I',msg,index*4)[0];cs=stream(msg,off);texts.append(dict(source=msg_path,index=index,offset=off,codes=cs,text=dec(cs)))
 for a in (0x80099ba0,0x80099bb8,0x800b9688):
  cs=stream(exe,a-0x80010000+2048);texts.append(dict(source='/SLPS_007.82',address=hex(a),codes=cs,text=dec(cs)))
 put('transaction-texts.json',dict(labels=texts,control_note='4004 consumes following variable index; its argument0 is not literal price0. Existing PSMOJI transcription reused. Old helper result label lease is not evidence of rental: native labels say investigation/acquisition.'))
 ranges=[('acquisition_parent',0x80060e70,0x800612cc),('survey_ui_route',0x8004d6ec,0x8004d8c8),('acquisition_menu',0x8004dfac,0x8004e494),('binding_reset',0x8001b320,0x8001b678),('reactivation',0x8001baac,0x8001bb80),('sale_parent',0x80061cdc,0x8006215c),('sale_confirm',0x8006215c,0x80062484)]
 rs=[]
 for n,a,b in ranges:
  v=at(a,b-a);(ROOT/f'source/{n}.bin').write_bytes(v);rs.append(dict(file=f'source/{n}.bin',start=hex(a),end_exclusive=hex(b),sha256=sha(v)))
 put('source-ranges.json',dict(disc_sha256=DISC_SHA,exe_sha256=EXE_SHA,message_sha256=sha(msg),ranges=rs))
 put('summary.json',dict(source_maps=4,source_stores=len(allquotes),initial_acquisition_candidates=sum(not q['original_main_store_acquisition_guard'] for q in allquotes),source_staff_references=len(stafflinks),inspection_fee=fee,price_multiplier=2,original_cpu_updates=0,
 known_before='Acquisition parent/child and natural controlled UI branches existed. New data extraction connects11 source asset prices to7 guarded acquisition candidates, source staff ownership links, native investigation labels/state routing, sale guards and explicit ledger/history reset spans. No new acquisition gameplay runs.'))
 print('Extracted11 store quotes,7 acquisition candidates,',len(stafflinks),'staff references and source field policies.')
if __name__=='__main__':main()
