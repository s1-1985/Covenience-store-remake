#!/usr/bin/env node
// Rebuild from existing source-derived repository inputs. No emulator or external package.
import {readFileSync,writeFileSync} from 'node:fs';
import {fileURLToPath} from 'node:url';
import path from 'node:path';
function build(master, p, products) {
 const names=products.products.map(x=>x.name),s8=x=>x>127?x-256:x;
 const s16=(a,i)=>{const x=a[i]|a[i+1]<<8;return x>=32768?x-65536:x;};
 return master.rows.map(m=>{
 const area=m.footprint[0]*m.footprint[1],byProfile={},byProduct={},byMode={},slotPop=[];
 m.per_cell_mix_choices.forEach(c=>{let total=0;for(const [pid,heads] of c.profiles){
 if(pid<0||pid>=144)throw Error("Invalid profile");
 const q=p.slice(pid*24,(pid+1)*24),prod=s8(q[8]),mode=s8(q[12]);
 byProfile[pid]=(byProfile[pid]||0)+heads*area;byProduct[prod]=(byProduct[prod]||0)+heads*area;byMode[mode]=(byMode[mode]||0)+heads*area;total+=heads;}slotPop.push(total);});
 const numerator=Object.values(byProfile).reduce((a,b)=>a+b,0);
 const profiles=Object.entries(byProfile).map(([id,n])=>{const q=p.slice(Number(id)*24,(Number(id)+1)*24);return {profile:Number(id),head_weight_numerator:n,denominator:5,primary_product:s8(q[8]),product_candidates:q.slice(8,12).map(s8),arrival_mode:s8(q[12]),wallet_source:s16(q,6),patience:s8(q[17])};});
 const primary_products=Object.entries(byProduct).map(([id,n])=>({id:Number(id),name:names[id],head_weight_numerator:n,denominator:5})).sort((a,b)=>b.head_weight_numerator-a.head_weight_numerator||a.id-b.id);
 const arrival_modes=Object.entries(byMode).map(([id,n])=>({mode:Number(id),head_weight_numerator:n,denominator:5}));
 if(primary_products.reduce((a,b)=>a+b.head_weight_numerator,0)!==numerator||arrival_modes.reduce((a,b)=>a+b.head_weight_numerator,0)!==numerator)throw Error("Join mismatch");
 return {selection:m.selection,kind:m.kind,name:m.name,footprint:m.footprint,area,source_mix_slots:m.customer_mix_choices,per_cell_slot_population:slotPop,population_slot_average:{numerator,denominator:5},population_min:Math.min(...slotPop)*area,population_max:Math.max(...slotPop)*area,unique_profiles:profiles.length,profiles,primary_products,arrival_modes};
 });
}
const root=path.dirname(fileURLToPath(import.meta.url));
const master=JSON.parse(readFileSync(path.join(root,'../20261115-town-project-data/project-master.json'),'utf8'));
const p=Array.from(readFileSync(path.join(root,'../20261113-customer-data/source/shopping-profiles.bin')));
const products=JSON.parse(readFileSync(path.join(root,'../20261113-product-stock-data/product-fixture-data.json'),'utf8'));
const rows=build(master,p,products);
if(rows.length!==18||!rows.every((r,i)=>r.population_min===master.rows[i].completed_building_population_range[0]&&r.population_max===master.rows[i].completed_building_population_range[1]))throw Error('Population range mismatch');
const result={schema_version:1,source_commit:"ed3db52f2900d47b45e2401996038b6a5001192a",scope:"Completed-building source composition, before weather, season, calendar share, store choice and customer spawn. Each numerator/5 is the arithmetic mean of five catalog slots multiplied by footprint area, not actual fractional people, expected sales, a daily arrival count, or a measured RNG distribution. Duplicate slots retain multiplicity.",profile_links:rows.reduce((s,r)=>s+r.profiles.length,0),distinct_profiles:new Set(rows.flatMap(r=>r.profiles.map(p=>p.profile))).size,facilities_with_parking_mode:rows.filter(r=>r.arrival_modes.some(m=>m.mode===3)).length,rows};
writeFileSync(path.join(root,'project-customer-cohorts.json'),JSON.stringify(result,null,2)+'\n');
