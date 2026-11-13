#!/usr/bin/env python3
"""Static actor-render contract and source-derived geometry examples.
Does not run the PS CPU, simulate business days, or manufacture walk frames.
"""
import argparse, hashlib, json, runpy, struct
from pathlib import Path
from capstone import Cs,CS_ARCH_MIPS,CS_MODE_MIPS32,CS_MODE_LITTLE_ENDIAN
ROOT=Path(__file__).resolve().parent
DISC_SHA='8d8eda789c5a2fe892a4722719b0466dd7d126eed6cd99ad05a807d81b57d1c1'
EXE_SHA='d6a167a1c9e0fe98d7e44e12968caa489ac3eb7ed3b9e46012a188af8432b1fd'
def sha(b):return hashlib.sha256(b).hexdigest()
def js(name,data):(ROOT/name).write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
def main():
    ap=argparse.ArgumentParser();ap.add_argument('disc',type=Path);args=ap.parse_args();raw=args.disc.read_bytes();assert sha(raw)==DISC_SHA
    lib=runpy.run_path(str(ROOT.parent/'20261113-disc-data-extraction/extract-disc-data.py'));files,read=lib['iso'](raw);row=next(r for r in files if r['path']=='/SLPS_007.82');exe=read(row['lba'],row['bytes']);assert sha(exe)==EXE_SHA
    def at(a,n):return exe[a-0x80010000+2048:a-0x80010000+2048+n]
    md=Cs(CS_ARCH_MIPS,CS_MODE_MIPS32|CS_MODE_LITTLE_ENDIAN)
    spans=[('input_interrupt',0x8001310c,0x800131d0),('interior_record_init',0x80013448,0x80013ddc),('input_edge_update',0x80013ddc,0x80013e5c),('frame_draw',0x80018a5c,0x80019460),('interior_refresh',0x80041218,0x80041268),('actor_records',0x80056a3c,0x80056ff0),('sprite_packet',0x80084830,0x800849ac),('vsync',0x80089ca4,0x80089dec),('play_tail',0x8005d4b0,0x8005d5a4),('staff_walk_commit',0x80037734,0x80037f44),('customer_position_commit',0x80032c68,0x800330b0)]
    (ROOT/'source').mkdir(exist_ok=True);ranges=[];assembly=[];calls={};instructions={}
    for name,a,end in spans:
        b=at(a,end-a);(ROOT/'source'/f'{name}.bin').write_bytes(b);ranges.append(dict(name=name,address=hex(a),bytes=len(b),sha256=sha(b)));ins=list(md.disasm(b,a));instructions[name]=ins
        assembly.append(f'\n# {name} {a:#x}..{end:#x}')
        assembly.extend(f'{x.address:08x}: {x.bytes.hex()} {x.mnemonic} {x.op_str}' for x in ins)
        calls[name]=[dict(site=hex(x.address),opcode=x.mnemonic,target=x.op_str) for x in ins if x.mnemonic in ('jal','jalr')]
    (ROOT/'actor-readers.asm').write_text('\n'.join(assembly)+'\n');js('source-ranges.json',ranges);js('direct-calls.json',calls)
    # Native84830 sets t3=a0 once. Enumerate direct loads from that record base.
    loads=[]
    for x in instructions['sprite_packet']:
        w=struct.unpack('<I',x.bytes)[0];op=w>>26;base=(w>>21)&31
        if op in (0x20,0x21,0x23,0x24,0x25) and base==11:
            off=struct.unpack('<h',x.bytes[:2])[0];loads.append(dict(site=hex(x.address),offset=off,bytes={0x20:1,0x21:2,0x23:4,0x24:1,0x25:2}[op],instruction=x.mnemonic+' '+x.op_str))
    assert sorted({r['offset'] for r in loads})==[0,4,6,8,10,12,14,15,16,18,20,21,22]
    covered={i for r in loads for i in range(r['offset'],r['offset']+r['bytes'])};assert not covered.intersection(range(24,36))
    js('packet-record-accesses.json',dict(record_bytes=36,record_base_register='t3, assigned from a0 at entry',loads=loads,unused_trailing_bytes=list(range(24,36)),conclusion='This packet function does not read the record transform/scale tail and does not interpolate XY or animate UV. Global draw origin is added directly. Scope is84830, not every renderer in the executable.'))
    dirs=[list(struct.unpack('<2i',at(0x8009941c+j*8,8))) for j in range(4)];di=list(struct.unpack('<4i',at(0x8009940c,16)));assert di==[1,0,2,3]
    def project(x,y,rest=False,right_fixture=False,origin=(160,120)):
        rx=x*8-160+(8 if rest else -8 if right_fixture else 0)
        ry=(y-1)*8-90+(8 if rest else 0)
        return dict(record_xy=[rx,ry],packet_xy=[rx+origin[0],ry+origin[1]])
    examples=[dict(name='ordinary_grid_actor',grid=[4,3],**project(4,3)),dict(name='right_neighbor_has_fixture_low10',grid=[4,3],**project(4,3,right_fixture=True)),dict(name='resting_staff_separate_record',grid=[4,3],**project(4,3,rest=True))]
    # Empty-route example: source's end-of-segment facing update, no RNG/obstacles.
    x,y,d=4,3,3;route=[0xc1,0x02]+[255]*8;path=[];appearance=38
    for tick in range(4):
        path.append(dict(tick=tick,grid=[x,y],direction=d,image_code=appearance*4+di[d]+640,route=list(route),**project(x,y)))
        if route[0]==255:continue
        direction=route[0]>>6;dx,dy=dirs[direction];x+=dx;y+=dy;d=direction;route[0]-=1
        if route[0]&63==0:
            route=route[1:]+[255]
            if route[0]!=255:d=route[0]>>6
    assert [r['image_code'] for r in path]==[795,793,793,793]
    js('geometry-examples.json',dict(scope='Source-derived arithmetic examples, not captured gameplay frames.',draw_origin=[160,120],position_cases=examples,route_turn_case=path,turn_note='On the final rightward step, the actor already faces the next segment(up); there is no additional turn-only sample in this unobstructed route case.'))
    bridge=dict(schema_version=1,source_disc_sha256=DISC_SHA,source_exe_sha256=EXE_SHA,normal_interior_scope=['customer position commit','staff position commit','56A3C actor record builder','18A5C actor group dispatch','84830 packet builder'],actor_record=dict(base='0x800da990',count='0x800cda2c',stride=36,initialized_slots=33,width=16,height=16,page=5,clut=[0,493]),directions=dirs,direction_image_offsets=di,grid_image='appearance*4+direction_offset+640',rest_image='appearance*4+640; fixed down-facing source image, no direction lookup',grid_actor_gate='word low10==0 and640<=((word>>12)&1023)<820',grid_record_xy=['8*x-160-(8 if right neighbor within width has nonzero low10 else0)','8*(y-1)-90'],rest_actor_gate='assigned staff slot, staff state byte+40==0, x!=-1,y!=-1',rest_record_xy=['8*x+8-160','8*(y-1)+8-90'],record_build_order='grid row-major top-to-bottom/left-to-right, then resting staff slot2,1,0',packet_cpu_order='actor records last-to-first at OT depth9',ot_link_order='head insertion reconstructs actor record order0..n-1 in this OT bucket',packet_record_unused_tail=[24,36],interpolation='None in these normal actor image/coordinate expressions or84830 packet emission. Global draw origin remains an input.',timing=dict(frame_vsync_site='0x800193b8: call89ca4 with a0=0',normal_tail=['3FF00 ancillary updates','18A5C draw and input snapshot update','if cd9cc==0: second18A5C','if branch taken and cd7f4==0:23438 simulation update'],input_state='13DDC updates current/previous logical input and rising edges; cd9cc is the previous snapshot after that helper',rule='Holding nonzero logical input across first draw prevents this tail from entering simulation-update branch. If input changes during second draw, that gate is not rechecked before23438.',wall_clock='Two draw calls in the uncomplicated tail are not a measured fixed frame rate. Extra UI/audio draws and waits exist; do not assign a global pixels-per-second constant from this alone.'),limitations=['No original game CPU execution or new game-state trace in this work.','No claim that every UI, cutscene, customer variant or hardware path has no animation.','Original TIM only supplies four direction tiles per identified appearance; synthesized footstep frames would be remake additions.'])
    js('android-actor-render-bridge.json',bridge)
    js('summary.json',dict(new_work=['Enumerated exact record bytes read by native84830: trailing transform fields+24..35 are unused in this path.','Connected normal interior render stages and distinguished fixed down-facing rest record from active direction lookup.','Made end-of-route-segment facing change and input-gated simulation timing explicit for the native port.'],existing_work=['176 appearance direction frames and previous actor coordinate formulas were already extracted.'],scope='Normal interior render data contract; not a global no-animation proof.',original_cpu_updates=0))
    print(json.dumps(dict(source_spans=len(spans),packet_record_loads=len(loads),geometry_examples=len(examples),route_images=[r['image_code'] for r in path])))
if __name__=='__main__':main()
