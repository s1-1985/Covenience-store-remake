#!/usr/bin/env node
// Static code/data recovery only; does not execute PS instructions.
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

const root=path.dirname(fileURLToPath(import.meta.url)),analysis=path.dirname(root);
const ram=inflateSync(readFileSync(path.join(analysis,'20261105-post-monthly/rival-native-exit.ram.zlib')));
if(ram.length!==2097152||createHash('sha256').update(ram).digest('hex')!=='ddfd28dc6538fd13e7cda761c85943ad0ffe50b950d3019de9f24af9e9dd0238')throw Error('Source RAM mismatch');
const completion=readFileSync(path.join(analysis,'20261115-town-project-data/source/completion.bin'));
if(!ram.subarray(0x29020,0x29020+completion.length).equals(completion))throw Error('Original completion mismatch');
const ranges=[
  {
    "name": "caller_prefix",
    "start": "0x80023438",
    "end_exclusive": "0x800234a8",
    "offset": 144440,
    "bytes": 112
  },
  {
    "name": "metric_prologue",
    "start": "0x80023c20",
    "end_exclusive": "0x80023c40",
    "offset": 146464,
    "bytes": 32
  },
  {
    "name": "metric_store_loop",
    "start": "0x80023ce4",
    "end_exclusive": "0x80023da4",
    "offset": 146660,
    "bytes": 192
  },
  {
    "name": "metric_height_write",
    "start": "0x80023f20",
    "end_exclusive": "0x80023f48",
    "offset": 147232,
    "bytes": 40
  },
  {
    "name": "metric_loop_end",
    "start": "0x80024630",
    "end_exclusive": "0x8002464c",
    "offset": 149040,
    "bytes": 28
  },
  {
    "name": "queue_prologue",
    "start": "0x8003ef44",
    "end_exclusive": "0x8003ef68",
    "offset": 257860,
    "bytes": 36
  },
  {
    "name": "annual_alias_writes",
    "start": "0x8003f7fc",
    "end_exclusive": "0x8003f934",
    "offset": 260092,
    "bytes": 312
  },
  {
    "name": "preceding_handler",
    "start": "0x800275f8",
    "end_exclusive": "0x80029020",
    "offset": 161272,
    "bytes": 6696
  },
  {
    "name": "completion",
    "start": "0x80029020",
    "end_exclusive": "0x80029334",
    "offset": 167968,
    "bytes": 788
  }
];
mkdirSync(path.join(root,'source'),{recursive:true});
for(const r of ranges)writeFileSync(path.join(root,'source',r.name+'.bin'),ram.subarray(r.offset,r.offset+r.bytes));
const aliases=JSON.parse(readFileSync(path.join(root,'stack-aliases.json'),'utf8'));
for(const f of aliases.frames){const a=parseInt(f.function,16)&0x1fffffff,size=-(ram.readInt32LE(a)<<16>>16);if(size!==f.frame_size||f.local_offset-size!==-36)throw Error('Frame alias mismatch');}
const calls=[];for(let a=0x10000;a<0x98000;a+=4)if(ram.readUInt32LE(a)===(0x0c000000|((0x80029020>>>2)&0x3ffffff)))calls.push('0x'+(a+0x80000000).toString(16));
if(JSON.stringify(calls)!==JSON.stringify(['0x80023498']))throw Error('Direct caller mismatch');
const bytes=Array.from(ram),prior=dis(bytes,0x800275f8,0x80029020);
const directStores=prior.filter(x=>/^(sw|sh|sb) .*, .*\(\$fp\)/.test(x.text));
if(directStores.some(x=>x.text.includes('0x3c($fp)')))throw Error('New direct writer');
let asm=ranges.filter(r=>r.name!=='preceding_handler').map(r=>'# '+r.name+'\n'+dis(bytes,parseInt(r.start,16),parseInt(r.end_exclusive,16)).map(l=>l.asm).join('\n')).join('\n\n');
asm+='\n\n# preceding handler prologue and direct fp-relative stores only; full bytes retained in source/preceding_handler.bin\n'+dis(bytes,0x800275f8,0x80027610).map(x=>x.asm).join('\n')+'\n'+directStores.map(x=>'0x'+x.address.toString(16)+': '+x.text).join('\n')+'\n';
writeFileSync(path.join(root,'sound-readers.asm'),asm);
const initial=readFileSync(path.join(analysis,'20261114-parking-arrival-data/source/initial-active-stores.bin'));
const index=JSON.parse(readFileSync(path.join(analysis,'20261114-parking-arrival-data/initial-store-ranges.json'),'utf8'));
const stores=index.stores.map(s=>({map:s.map,physical_slot:s.physical_slot,width:initial.readInt32LE(s.packed_offset+0x44),height:initial.readInt32LE(s.packed_offset+0x48)}));
const saved=JSON.parse(readFileSync(path.join(root,'initial-store-height-links.json'),'utf8'));
if(JSON.stringify(stores)!==JSON.stringify(saved.stores))throw Error('Initial store mismatch');
for(const m of saved.maps){const group=stores.filter(x=>x.map===m.map).sort((a,b)=>a.physical_slot-b.physical_slot),last=group[group.length-1];if(last.height!==m.height_written_by_metric||last.physical_slot!==m.last_active_physical_slot)throw Error('Last store mismatch');}
