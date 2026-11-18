#!/usr/bin/env python3
"""Targeted original graph prefix/scale and buffer-boundary observations.
Usage: PYTHONPATH=... python analyze-graphs.py SOURCE.zip
No gameplay, graphics driver, file card or callee substitution is involved.
"""
import hashlib,json,struct,sys,zipfile
from pathlib import Path
from collections import Counter
from unicorn import Uc,UC_ARCH_MIPS,UC_MODE_MIPS32,UC_MODE_LITTLE_ENDIAN
from unicorn.mips_const import UC_MIPS_REG_SP,UC_MIPS_REG_FP,UC_MIPS_REG_RA,UC_MIPS_REG_A0,UC_MIPS_REG_PC,UC_MIPS_REG_V0
from PIL import Image
ROOT=Path(__file__).resolve().parent
EXE_SHA='d6a167a1c9e0fe98d7e44e12968caa489ac3eb7ed3b9e46012a188af8432b1fd'
STORE=0x8012b2f8;PROFIT=0x800e3c28;COUNT=0x800e43d0;AVG=0x800d6018;SCALE=0x800e4000;PIX=0x80187e00
MISSING=-2147483648

def physical(a):return a&0x1fffffff
def put(u,a,v):u.mem_write(physical(a),struct.pack('<I',v&0xffffffff))
def get(u,a):return struct.unpack('<i',u.mem_read(physical(a),4))[0]
def dump(name,x):(ROOT/name).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def truncdiv(a,b):return (-1 if a*b<0 else 1)*(abs(a)//abs(b))
def model(history,chain,counts):
    valid=[]
    for value,total,n in zip(history,chain,counts):
        if n<=0 or total==MISSING or value==MISSING:break
        valid.append((value,truncdiv(total,n)))
    maximum=max([1]+[abs(v) for pair in valid for v in pair])
    axis=max(1000000,((maximum+999999)//1000000)*1000000)
    return {'valid':len(valid),'averages':[v[1] for v in valid],'axis_yen':axis,'scale_units_10000yen':axis//10000,'oldest_first':[v[0] for v in reversed(valid)]}

def main(archive):
    z=zipfile.ZipFile(archive);exe=z.read('algorithm-analysis/source/SLPS_007.82');assert hashlib.sha256(exe).hexdigest()==EXE_SHA
    def fresh(history,chain,counts):
        u=Uc(UC_ARCH_MIPS,UC_MODE_MIPS32|UC_MODE_LITTLE_ENDIAN);u.mem_map(0,0x200000);u.mem_write(0x10000,exe[2048:])
        for i in range(60):put(u,STORE+0x12e8+4*i,MISSING);put(u,PROFIT+4*i,MISSING)
        for i,v in enumerate(history):put(u,STORE+0x12e8+4*i,v)
        for i,v in enumerate(chain):put(u,PROFIT+4*i,v)
        u.mem_write(physical(COUNT),bytes((n&255) for n in counts))
        return u
    def run(u,entry,stop):
        for r,v in [(UC_MIPS_REG_SP,0x801f0000),(UC_MIPS_REG_FP,0x801f0000),(UC_MIPS_REG_RA,0x80001000),(UC_MIPS_REG_A0,STORE)]:u.reg_write(r,v)
        u.emu_start(entry,stop,count=12000000)
        assert u.reg_read(UC_MIPS_REG_PC)in (stop,stop-4),(hex(u.reg_read(UC_MIPS_REG_PC)),hex(stop),get(u,SCALE))
    cases=[('chain_average_drives_scale',[4000000,-10000,MISSING],[10000000,-3,0],[2,2,0]),('first_store_sentinel_stops_later_history',[1000000,MISSING,9000000],[1000000,1000000,20000000],[1,1,1]),('million_rounding_boundary',[1000001],[0],[1]),('zero_history_is_valid',[0],[0],[1])]
    results=[]
    for name,history,chain,counts in cases:
        u=fresh(history,chain,counts);run(u,0x80048728,0x80048a60)
        expected=model(history,chain,counts)
        observed={'scale_units_10000yen':get(u,SCALE),'negative_scale':get(u,SCALE+4),'zero_axis':get(u,SCALE+8),'averages':[get(u,AVG+4*i) for i in range(expected['valid'])]}
        assert observed['scale_units_10000yen']==expected['scale_units_10000yen'] and observed['averages']==expected['averages']
        assert observed['negative_scale']==-observed['scale_units_10000yen'] and observed['zero_axis']==0
        results.append(dict(name=name,history=history,chain=chain,counts=counts,model=expected,original=observed))
    # One actual bitmap-render call covers chronological order and both signs.
    u=fresh([1000000,-1000000],[0,0],[1,1]);put(u,SCALE,100)
    u.mem_write(physical(PIX)-240,bytes([170])*240);u.mem_write(physical(PIX)+240*112,bytes([170])*240)
    run(u,0x80047c00,0x80001000)
    pix=bytes(u.mem_read(physical(PIX),240*112));before=bytes(u.mem_read(physical(PIX)-240,240));after=bytes(u.mem_read(physical(PIX)+240*112,240))
    assert before[4:8]==bytes([3,3,3,4]) and after[:4]==bytes([2,2,2,4])
    assert pix[57*240:57*240+4]==bytes([2,2,2,4]) and pix[4:8]==bytes([3,3,3,4])
    plot={'history_newest_first':[1000000,-1000000],'plot_size':[240,112],'return_v0':u.reg_read(UC_MIPS_REG_V0),'first_bar_x':0,'first_bar_history_index':1,'second_bar_x':4,'second_bar_history_index':0,'before_buffer_changed_offsets':[i-240 for i,v in enumerate(before) if v!=170],'after_buffer_changed_offsets':[i for i,v in enumerate(after) if v!=170],'blue_palette_index':3,'red_palette_index':2,'grid_palette_index':4,'pixel_counts':dict(Counter(pix)),'source_pixel_sha256':hashlib.sha256(pix).hexdigest()}
    palette=struct.unpack_from('<6H',exe,0x80010a30-0x80010000+2048)
    colors=[tuple(((v>>s)&31)*255//31 for s in (0,5,10)) for v in palette]
    image=Image.new('RGB',(240,112));image.putdata([colors[n] for n in pix]);image.save(ROOT/'original-graph-bounded.png')
    spans=[('store_graph',0x800478f8,0x80048b80),('chain_graph',0x80048b80,0x8004965c),('chain_scale',0x8004965c,0x800498c8),('graph_palette',0x80010a30,0x80010a3c),('finance_history',0x80029d60,0x80029e20),('chain_history',0x8002a250,0x8002a300)]
    # Compact primary evidence: original ranges, address-anchored words, hashes.
    evidence=[]
    for name,a,b in spans:
        raw=exe[a-0x80010000+2048:b-0x80010000+2048]
        evidence.append({'name':name,'start':hex(a),'end_exclusive':hex(b),'sha256':hashlib.sha256(raw).hexdigest(),'words_le':raw.hex()})
    dump('original-cases.json',dict(scale_cases=results,plot=plot,successful_original_entries=5,operating_updates=0,scope='Controlled graph arrays; scale stops before text calls, plot is original leaf. Not a natural UI/save/finance playthrough.'))
    dump('source-ranges.json',dict(source='algorithm-analysis/source/SLPS_007.82',sha256=EXE_SHA,ranges=evidence))
    print(json.dumps({'scale_cases':len(results),'plot_entries':1,'axis_yen':[x['model']['axis_yen'] for x in results],'before_offsets':plot['before_buffer_changed_offsets'],'after_offsets':plot['after_buffer_changed_offsets']}))
if __name__=='__main__': main(Path(sys.argv[1]))
