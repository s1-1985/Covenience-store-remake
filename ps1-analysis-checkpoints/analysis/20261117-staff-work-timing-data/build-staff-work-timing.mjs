export function buildTiming(roster) {
  const phase = (ability, parity, slot) => Array.from({length:150}, (_,n)=>n).filter(n => {
    const clock = 2*n + parity;
    return ((clock >>> 1) % 3) === slot && clock % 100 >= 100 - ability;
  });
  const profiles = roster.shared_initial_profiles.map(p => ({
    id:p.id, name:p.name, customer_service:p.initial_attributes.customer_service,
    parity_cases:[0,1].map(parity=>({parity, slots:[0,1,2].map(slot=>{
      const update_indices=phase(p.initial_attributes.customer_service, parity, slot);
      return {slot, rest_reconsiderations:50, cleaning_time_gate_passes:update_indices.length, update_indices};
    })}))
  }));
  const initial_assignments = roster.maps.flatMap(m=>m.active_stores.flatMap(s=>s.staff_ids.map((id,slot)=>({id,slot})).filter(x=>x.id>=0).map(({id,slot})=>({
    map:m.map, physical_store_slot:s.physical_slot, staff_slot:slot, staff_id:id,
    name:profiles[id].name, customer_service:profiles[id].customer_service,
    initial_task:m.staff_states.find(x=>x.id===id).task,
    even_clock_cleaning_windows:profiles[id].parity_cases[0].slots[slot].update_indices,
    odd_clock_cleaning_windows:profiles[id].parity_cases[1].slots[slot].update_indices
  }))));
  return {
    schema_version:1,
    scope:"Conditional clock gates for fully recovered task0 staff reconsidering work; earlier checkout/refill choices must fail before cleaning is tried.",
    clock_step:2, block_updates:150, clock_residue_period:300,
    index_convention:"n=0..149, clock=2*n+parity; these are phase positions, not elapsed times since rest/full recovery.",
    wrap_scope:"No uint32 overflow within block; retain saved clock phase and parity in native implementation.",
    abilities: {field:"signed runtime staff+0x20", original_name:"接客", minimum:Math.min(...profiles.map(p=>p.customer_service)), maximum:Math.max(...profiles.map(p=>p.customer_service)), odd_profile_count:profiles.filter(p=>p.customer_service%2).length},
    counts:{profiles:profiles.length, initial_stores:roster.maps.reduce((n,m)=>n+m.active_stores.length,0), initial_assignments:initial_assignments.length},
    formulas:{rest:"((clock>>>1)%3)==staff_slot", cleaning:"(clock>>>0)%100>=100-customer_service", even_count:"floor(customer_service/2) per50 reconsiderations", odd_count:"ceil(customer_service/2) per50 reconsiderations"},
    profiles, initial_assignments,
    limitations:["No task success rate, probability or real seconds is inferred.","Target availability, fatigue/recovery, earlier tasks, path and fixture conditions remain required.","This package establishes the original cleaning time gate; it does not newly establish the checkout helper internal time gate.","Odd parity is a conditional case, not a claim about the default new-game clock."]
  };
}

import {readFileSync,writeFileSync} from 'node:fs';
import {fileURLToPath} from 'node:url';
import {dirname,resolve} from 'node:path';
const here=dirname(fileURLToPath(import.meta.url));
const roster=JSON.parse(readFileSync(resolve(here,'../20261114-staff-roster-growth-data/staff-roster-data.json'),'utf8'));
const asm=readFileSync(resolve(here,'staff-work-readers.asm'),'utf8');
for(const word of ['80036f44: 42100300','80036f74: 05004310','80039638: 20004380','800396e0: 2a104300','80037378: 03000324']) {
  if(!asm.includes(word)) throw new Error('Original instruction evidence changed: '+word);
}
const caller=readFileSync(resolve(here,'../20261117-project-sound-stack-data/source/caller_prefix.bin'));
if(caller.subarray(0x1c,0x20).toString('hex')!=='02004324') throw new Error('Clock increment changed');
const result=buildTiming(roster);
for(const p of result.profiles) for(const c of p.parity_cases) for(const s of c.slots)
  if(s.cleaning_time_gate_passes!==Math.floor((p.customer_service+c.parity)/2)) throw new Error('Phase count mismatch');
writeFileSync(resolve(here,'staff-work-timing.json'),JSON.stringify(result,null,2)+'\n');
const rows=['id,name,customer_service,even_passes_per_50,odd_passes_per_50',...result.profiles.map(p=>[p.id,p.name,p.customer_service,p.parity_cases[0].slots[0].cleaning_time_gate_passes,p.parity_cases[1].slots[0].cleaning_time_gate_passes].join(','))];
writeFileSync(resolve(here,'staff-work-timing.csv'),rows.join('\n')+'\n');
