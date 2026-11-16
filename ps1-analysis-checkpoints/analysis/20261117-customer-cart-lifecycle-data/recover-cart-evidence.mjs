#!/usr/bin/env node
// Recover static source bytes and conditional catalog arithmetic. No CPU emulation.
import {readFileSync,writeFileSync,mkdirSync} from 'node:fs';
import {inflateSync} from 'node:zlib';
import {createHash} from 'node:crypto';
import {fileURLToPath} from 'node:url';
import path from 'node:path';
function dis(ram,lo,hi){
 const rn=["zero","at","v0","v1","a0","a1","a2","a3","t0","t1","t2","t3","t4","t5","t6","t7","s0","s1","s2","s3","s4","s5","s6","s7","t8","t9","k0","k1","gp","sp","fp","ra"],reg=i=>"$"+rn[i],hex=x=>"0x"+(x>>>0).toString(16),si=x=>x<0?"-"+hex(-x):hex(x),out=[];
 for(let addr=lo;addr<hi;addr+=4){let i=addr&0x1fffffff,w=(ram[i]|ram[i+1]<<8|ram[i+2]<<16|ram[i+3]<<24)>>>0,op=w>>>26,rs=w>>>21&31,rt=w>>>16&31,rd=w>>>11&31,imm=w<<16>>16,u=w&65535,fn=w&63,sh=w>>>6&31,t;
 const mem={32:"lb",33:"lh",35:"lw",36:"lbu",37:"lhu",40:"sb",41:"sh",43:"sw",34:"lwl",38:"lwr",42:"swl",46:"swr"};
 if(mem[op])t=`${mem[op]} ${reg(rt)}, ${si(imm)}(${reg(rs)})`;
 else if(op===15)t=`lui ${reg(rt)}, ${hex(u)}`;
 else if([8,9,10,11,12,13,14].includes(op))t=`${{8:"addi",9:"addiu",10:"slti",11:"sltiu",12:"andi",13:"ori",14:"xori"}[op]} ${reg(rt)}, ${reg(rs)}, ${op<12?si(imm):hex(u)}`;
 else if(op===2||op===3)t=`${op===3?"jal":"j"} ${hex(((addr+4)&0xf0000000)|((w&0x3ffffff)<<2))}`;
 else if([4,5,6,7,1].includes(op))t=`${{4:"beq",5:"bne",6:"blez",7:"bgtz",1:rt===0?"bltz":"bgez"}[op]} ${reg(rs)}${op===4||op===5?", "+reg(rt):""}, ${hex(addr+4+imm*4)}`;
 else if(op===0){if(!w)t="nop";else if([0,2,3].includes(fn))t=`${{0:"sll",2:"srl",3:"sra"}[fn]} ${reg(rd)}, ${reg(rt)}, ${sh}`;
 else if(fn===8)t=`jr ${reg(rs)}`;else if([16,18].includes(fn))t=`${fn===16?"mfhi":"mflo"} ${reg(rd)}`;
 else if([24,26].includes(fn))t=`${fn===24?"mult":"div"} ${reg(rs)}, ${reg(rt)}`;
 else t=`${{32:"add",33:"addu",34:"sub",35:"subu",36:"and",37:"or",38:"xor",42:"slt",43:"sltu"}[fn]||"fn"+fn} ${reg(rd)}, ${reg(rs)}, ${reg(rt)}`;}
 else t="op"+op+" "+hex(w);
 out.push({address:addr,word:w,asm:hex(addr)+": "+ram.slice(i,i+4).map(x=>x.toString(16).padStart(2,"0")).join("")+" "+t,text:t});}
 return out;
}
function scanConditional(profiles, master) {
 const s8=x=>x>=128?x-256:x;
 const ordinary=product=>master.products[product].allowed_fixture_ids.filter(fid=>![2,3,5].includes(master.fixtures[fid].flags&255));
 const out=[];
 for(let id=0;id<144;id++){
  const q=profiles.slice(id*24,(id+1)*24),initial=q[6]|q[7]<<8,threshold=100-s8(q[19]);let wallet=initial,basket=0,prior=[];
  for(let slot=0;slot<4;slot++){
   const item=s8(q[8+slot]);if(item<0||item>=27)continue;
   const fixtures=ordinary(item);if(!fixtures.length)break;const price=master.products[item].base_price;
   if(price>wallet){if(basket>0&&threshold>0)out.push({profile:id,initial_wallet:initial,prior_items:prior,unsettled_per_person:basket,remaining_wallet:wallet,next_slot:slot,next_product:item,next_name:master.products[item].name,next_price:price,next_ordinary_fixture:fixtures[0],security_must_be_below:threshold});break;}
   prior.push({slot,product:item,name:master.products[item].name,price,ordinary_fixture:fixtures[0]});wallet-=price;basket+=price;
  }
 }
 return out;
}
const root=path.dirname(fileURLToPath(import.meta.url)),analysis=path.dirname(root);
const ram=inflateSync(readFileSync(path.join(analysis,'20261105-post-monthly/rival-native-exit.ram.zlib')));
if(ram.length!==2097152||createHash('sha256').update(ram).digest('hex')!=='ddfd28dc6538fd13e7cda761c85943ad0ffe50b950d3019de9f24af9e9dd0238')throw Error('RAM source mismatch');
const comparePaths=["20261114-checkout-waiting-data/checkout-readers.asm","20261113-seasonal-demand-data/demand-readers.asm","20261113-actor-render-data/actor-readers.asm"];
for(const name of comparePaths){
 let count=0;
 for(const line of readFileSync(path.join(analysis,name),'utf8').split('\n')){
  const m=line.match(/^([0-9a-f]{8}): ([0-9a-f]{8}) /);if(!m)continue;
  const address=parseInt(m[1],16)&0x1fffffff;
  if(ram.subarray(address,address+4).toString('hex')!==m[2])throw Error('Code mismatch '+m[1]);count++;
 }
 if(!count)throw Error('Empty original disassembly '+name);
}
const ranges=[
  {
    "name": "exit_control",
    "address": "0x80035770",
    "end_exclusive": "0x80035d58",
    "ram_offset": 218992,
    "bytes": 1512
  },
  {
    "name": "customer_dispatch",
    "address": "0x80032814",
    "end_exclusive": "0x80032c68",
    "ram_offset": 206868,
    "bytes": 1108
  },
  {
    "name": "destination_control",
    "address": "0x80036160",
    "end_exclusive": "0x80036ac0",
    "ram_offset": 221536,
    "bytes": 2400
  },
  {
    "name": "state_jump_table",
    "address": "0x80010918",
    "end_exclusive": "0x8001092c",
    "ram_offset": 67864,
    "bytes": 20
  },
  {
    "name": "purchase_posting_theft",
    "address": "0x800349d0",
    "end_exclusive": "0x80034ccc",
    "ram_offset": 215504,
    "bytes": 764
  },
  {
    "name": "entry_money_reset",
    "address": "0x80032a70",
    "end_exclusive": "0x80032ab4",
    "ram_offset": 207472,
    "bytes": 68
  },
  {
    "name": "normal_checkout_posting",
    "address": "0x800352d4",
    "end_exclusive": "0x8003533c",
    "ram_offset": 217812,
    "bytes": 104
  },
  {
    "name": "wait_posting",
    "address": "0x80035e4c",
    "end_exclusive": "0x80035ec0",
    "ram_offset": 220748,
    "bytes": 116
  }
];
mkdirSync(path.join(root,'source'),{recursive:true});
for(const r of ranges)writeFileSync(path.join(root,'source',r.name+'.bin'),ram.subarray(r.ram_offset,r.ram_offset+r.bytes));
const ramArray=Array.from(ram);
const asm=ranges.filter(r=>r.name!=='state_jump_table').map(r=>'# '+r.name+'\n'+dis(ramArray,parseInt(r.address,16),parseInt(r.end_exclusive,16)).map(x=>x.asm).join('\n')).join('\n\n')+'\n';
writeFileSync(path.join(root,'cart-lifecycle-readers.asm'),asm);
const profiles=Array.from(readFileSync(path.join(analysis,'20261113-customer-data/source/shopping-profiles.bin')));
const master=JSON.parse(readFileSync(path.join(analysis,'20261113-product-stock-data/product-fixture-data.json'),'utf8'));
const rows=scanConditional(profiles,master);if(rows.length!==32)throw Error('Candidate count mismatch');
writeFileSync(path.join(root,'conditional-profile-paths.json'),JSON.stringify({source_commit:"f5ae66462883e515ec6a6de88925c80a303659c6",conditions:"For each profile, read product slots0..3 in catalog order, skip-1; choose an allowed non-immediate fixture for every prefix item; use unchanged initial prices; assume every prefix item was actually taken with all calendar/random/reachability/stock gates passed. Stop at first insufficient-wallet item. Require existing cart>0, a non-immediate fixture, and positive theft security threshold. Does not claim all possible theft cases or natural replay.",rows},null,2)+'\n');
