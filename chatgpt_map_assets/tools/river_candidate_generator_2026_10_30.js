"use strict";
// Reproduce candidate river T and pond-headwater PNGs, read-only inputs.
// node river_candidate_generator_2026_10_30.js CROSS NS EW POND_S NEW_OUTPUT_DIR
const fs=require("node:fs"),path=require("node:path"),crypto=require("node:crypto");
require("./png64_rotate_2026_10_16.js");
const C=globalThis.MapPngCodec,args=process.argv.slice(2);
if(args.length!==5)throw Error("usage: node script.js CROSS NS EW POND_S NEW_OUTPUT_DIR");
const out=path.resolve(args[4]);
if(fs.existsSync(out))throw Error("refusing existing output: "+out);
const names=["cross","ns","ew","pond"];
const src=Object.fromEntries(names.map((k,i)=>[k,C.decode(C.b64dec(fs.readFileSync(args[i]).toString("base64")))]));
const p={};
for(const id of ["nes","new","nsw","esw"]){
 const a=new Uint8Array(src.cross.pix);
 for(let y=0;y<64;y++)for(let x=0;x<64;x++){
  const replace=id==="nes"?x<32:id==="nsw"?x>=32:id==="new"?y>=32:y<32;
  if(replace){const z=(y*64+x)*4,s=(id==="nes"||id==="nsw")?src.ns:src.ew;a.set(s.pix.subarray(z,z+4),z);}
 }
 p[id]=a;
}
p.s=src.pond.pix;p.w=C.rotate(src.pond.pix,1);
p.n=C.rotate(src.pond.pix,2);p.e=C.rotate(src.pond.pix,3);
fs.mkdirSync(out,{recursive:true});
const masks={n:1,e:2,s:4,w:8,nes:7,new:11,nsw:13,esw:14},records=[];
for(const id of ["n","e","s","w","nes","new","nsw","esw"]){
 const bytes=C.encode(id.length===1?src.pond:src.cross,p[id]),d=C.decode(bytes);
 if(!d.pix.every((v,i)=>v===p[id][i]))throw Error("PNG roundtrip failed "+id);
 const name="river_"+id+".png";
 fs.writeFileSync(path.join(out,name),Buffer.from(bytes),{flag:"wx"});
 records.push({asset_id:"river_"+id,direction_bits_nesw:masks[id],path:name,sha256:crypto.createHash("sha256").update(bytes).digest("hex"),status:"CANDIDATE_NOT_ACCEPTED"});
}
fs.writeFileSync(path.join(out,"manifest.json"),JSON.stringify({status:"CANDIDATE_NOT_ACCEPTED",assets:records},null,2),{flag:"wx"});
console.log("8 candidate PNGs written; original-game and Godot acceptance not performed.");
