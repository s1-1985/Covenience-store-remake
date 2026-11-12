#!/usr/bin/env python3
"""Feed naturally observed person records through the original frame renderer.

This is a rendering diagnostic: gameplay is not replayed here. Only the actor
group is enabled, and SDK synchronization/submission endpoints use the archived
runner contracts. The original dispatcher and sprite packet builder execute.
"""
import hashlib,json,struct,sys,zlib
from pathlib import Path
ROOT=Path(__file__).resolve().parent
ALGO=Path(sys.argv[1]).resolve();sys.path.insert(0,str(ALGO))
from check_machine import machine,put,get,EXE,UC_MIPS_REG_RA,UC_MIPS_REG_PC
from category_background_frame_harness import BackgroundCategoryRunner
from render_control import packet,dispatch

def sha(b):return hashlib.sha256(b).hexdigest()
rows=[];sources=[]
for case in ('first-store','second-store'):
    path=ROOT.parent/'20261112-actor-display'/(case+'-results.json')
    evidence=json.loads(path.read_text());assert evidence['all_passed']
    assert sha(EXE.read_bytes())==evidence['source_executable_sha256']
    sources.append(dict(path=str(path.relative_to(ROOT.parent)),sha256=sha(path.read_bytes())))
    for index,row in enumerate(evidence['cases']):
        records=[bytes.fromhex(x) for x in row['records_hex']]
        assert len(records)==row['count'] and len(records)<=32
        for buffer in (0,1):
            u=machine();table=0x80160000;buf=0x800e4540+buffer*144000
            runner=BackgroundCategoryRunner(u,buffer,{},table_address=table)
            # Source CPU records are unchanged; this diagnostic supplies actor-only
            # display enable, draw offsets and an empty OT according to the runner.
            u.mem_write(0xda990,b''.join(records)+bytes(1152-36*len(records)))
            u.mem_write(0xcda2c,struct.pack('<H',len(records)))
            put(u,0x800cd9dc,0x200)
            before=bytes(u.mem_read(0xda990,1152))
            u.reg_write(UC_MIPS_REG_RA,0x80001000)
            u.emu_start(0x80018a5c,0x80001000,count=1000000)
            assert u.reg_read(UC_MIPS_REG_PC)==0x80001000
            assert len(runner.frames)==1 and bytes(u.mem_read(0xda990,1152))==before
            native=bytes(u.mem_read(buf&0x1fffffff,24*len(records)))
            linked=0xffffff;expected=bytearray();packets=[]
            order=dispatch(0x200,buffer,{0x800cda2c:len(records)},4096)
            assert [x[1] for x in order]==[0x800da990+36*j for j in range(len(records)-1,-1,-1)]
            for record_index in range(len(records)-1,-1,-1):
                part=packet(records[record_index],160,120,linked);assert part and len(part)==24
                expected.extend(part)
                linked=(buf+len(expected)-24)&0xffffff
                tag,drawmode,color,xy,uv,wh=struct.unpack('<6I',part)
                x,y=xy&65535,xy>>16
                x=x if x<32768 else x-65536;y=y if y<32768 else y-65536
                actor=row['actors'][record_index]
                assert [x,y]==[actor['pixel'][0]+160,actor['pixel'][1]+120]
                assert [uv&255,(uv>>8)&255]==actor['uv']
                assert [wh&65535,wh>>16]==[16,16]
                packets.append(dict(source_record=record_index,source_actor=actor,xy=[x,y],uv=actor['uv'],packet_hex=part.hex()))
            assert native==expected and get(u,0x800e3bf8)==buf+len(native)
            assert get(u,table+9*4)==linked
            assert bytes(u.mem_read(buf+len(native)&0x1fffffff,16))==bytes(16)
            rows.append(dict(case=case,source_index=index,clock=row['clock'],buffer=buffer,depth=9,draw_order=[p['source_record'] for p in packets],
                             source_records_sha256=sha(before),packet_stream_sha256=sha(native),packet_stream_hex=native.hex(),packets=packets))
            runner.dispose()
output=dict(all_passed=True,source_executable_sha256=sha(EXE.read_bytes()),source_files=sources,frames=len(rows),
            packets=sum(len(r['packets']) for r in rows),cases=rows,
            limits=['Actor records are committed natural-play observations; frame inputs are isolated diagnostic inputs.',
                    'Original 18A5C dispatcher and 84830 packet builder, with SDK sync/submission boundaries supplied by archived runner.',
                    'No GPU rasterization, physical display timing, VRAM texture decoding or measured walking animation cadence.',
                    'The two OT buffers use the same runner-supplied logical offset (160,120); physical alternating display offsets are outside this diagnostic.'])
(ROOT/'results.json.zlib').write_bytes(zlib.compress((json.dumps(output,ensure_ascii=False,indent=2)+'\n').encode(),9))
(ROOT/'summary.json').write_text(json.dumps({k:v for k,v in output.items() if k!='cases'},ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:output[k] for k in ('all_passed','frames','packets')}))
