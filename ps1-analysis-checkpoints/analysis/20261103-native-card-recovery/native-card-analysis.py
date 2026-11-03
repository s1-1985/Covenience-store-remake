"""Small strict MIPS-I integer interpreter for recovered card routines.

Not a PS1 emulator: no IRQ/GPU/SPU/BIOS execution. Branch and load delays are
explicit. Unimplemented opcodes raise; external boundaries require named hooks.
"""
import struct

MASK = 0xffffffff
def signed(v):
    return v if v < 0x80000000 else v - 0x100000000

class Cpu:
    def __init__(self, exe):
        if exe[:8] != b"PS-X EXE":
            raise ValueError("not PS-X EXE")
        self.mem = bytearray(0x200000)
        address, length = struct.unpack_from("<II", exe, 0x18)
        self.write(address, exe[0x800:0x800+length])
        self.r = [0]*32
        self.hi = self.lo = 0
        self.pc = 0
        self.npc = 4
        self.pending_load = None
        self.hooks = {}
        self.calls = []
        self.steps = 0

    def physical(self, address, size):
        address &= MASK
        p = address & 0x1fffffff
        if p + size > len(self.mem):
            raise ValueError("unmapped memory " + hex(address))
        return p

    def read(self, address, size):
        p = self.physical(address, size)
        return bytes(self.mem[p:p+size])

    def write(self, address, data):
        p = self.physical(address, len(data))
        self.mem[p:p+len(data)] = data

    def cstring(self, address, limit=1024):
        out = bytearray()
        for i in range(limit):
            v = self.read(address+i, 1)[0]
            if v == 0:
                return bytes(out)
            out.append(v)
        raise ValueError("unterminated string")

    def run(self, address, args=(), limit=200000):
        self.r = [0]*32
        self.r[29] = 0x801f0000
        self.r[31] = 0x80000080
        for i, value in enumerate(args):
            self.r[4+i] = value & MASK
        self.pc, self.npc = address, address+4
        self.pending_load = None
        self.calls, self.steps = [], 0
        self.hi = self.lo = 0
        while self.pc != 0x80000080:
            if self.steps >= limit:
                raise TimeoutError("instruction limit at " + hex(self.pc))
            if self.pc in self.hooks:
                if self.pending_load is not None:
                    raise AssertionError("pending load at abstract boundary")
                self.calls.append((self.pc, list(self.r[4:8])))
                self.r[2] = self.hooks[self.pc](self) & MASK
                self.pc, self.npc = self.r[31], (self.r[31]+4)&MASK
                self.steps += 1
                continue
            self.step()
        return signed(self.r[2])

    def step(self):
        pc = self.pc
        w = struct.unpack("<I", self.read(pc,4))[0]
        op, rs, rt, rd, sh, fn = w>>26,(w>>21)&31,(w>>16)&31,(w>>11)&31,(w>>6)&31,w&63
        u = w & 65535
        imm = u if u < 32768 else u-65536
        a,b = self.r[rs],self.r[rt]
        next_pc = (self.npc+4)&MASK
        writes = {}
        load = None
        def put(reg,value):
            if reg:
                writes[reg] = value & MASK
        if op == 0:
            if fn == 0: put(rd,b<<sh)
            elif fn == 2: put(rd,b>>sh)
            elif fn == 3: put(rd,signed(b)>>sh)
            elif fn == 4: put(rd,b<<(a&31))
            elif fn == 6: put(rd,b>>(a&31))
            elif fn == 7: put(rd,signed(b)>>(a&31))
            elif fn == 8: next_pc = a
            elif fn == 9: put(rd,pc+8); next_pc = a
            elif fn == 16: put(rd,self.hi)
            elif fn == 18: put(rd,self.lo)
            elif fn in (24,25):
                value = (signed(a)*signed(b) if fn==24 else a*b) & ((1<<64)-1)
                self.lo,self.hi = value&MASK,value>>32
            elif fn in (26,27):
                aa,bb = (signed(a),signed(b)) if fn==26 else (a,b)
                if bb == 0:
                    self.lo = (1 if fn==26 and aa<0 else MASK)
                    self.hi = a
                else:
                    q = abs(aa)//abs(bb)
                    if (aa<0) != (bb<0): q = -q
                    self.lo,self.hi = q&MASK,(aa-q*bb)&MASK
            elif fn in (32,33):
                value=signed(a)+signed(b)
                if fn==32 and not -0x80000000<=value<=0x7fffffff: raise OverflowError('ADD')
                put(rd,a+b)
            elif fn in (34,35):
                value=signed(a)-signed(b)
                if fn==34 and not -0x80000000<=value<=0x7fffffff: raise OverflowError('SUB')
                put(rd,a-b)
            elif fn == 36: put(rd,a&b)
            elif fn == 37: put(rd,a|b)
            elif fn == 38: put(rd,a^b)
            elif fn == 39: put(rd,~(a|b))
            elif fn == 42: put(rd,int(signed(a)<signed(b)))
            elif fn == 43: put(rd,int(a<b))
            else: raise NotImplementedError((hex(pc),hex(w)))
        elif op in (2,3):
            if op==3: put(31,pc+8)
            next_pc=((pc+4)&0xf0000000)|((w&0x3ffffff)<<2)
        elif op in (4,5,6,7,1):
            condition = (a==b if op==4 else a!=b if op==5 else
                         signed(a)<=0 if op==6 else signed(a)>0 if op==7 else
                         signed(a)<0 if rt==0 else signed(a)>=0 if rt==1 else None)
            if condition is None: raise NotImplementedError((hex(pc),hex(w)))
            if condition: next_pc=(pc+4+4*imm)&MASK
        elif op in (8,9):
            if op==8 and not -0x80000000<=signed(a)+imm<=0x7fffffff: raise OverflowError('ADDI')
            put(rt,a+imm)
        elif op==10: put(rt,int(signed(a)<imm))
        elif op==11: put(rt,int(a<(imm&MASK)))
        elif op==12: put(rt,a&u)
        elif op==13: put(rt,a|u)
        elif op==14: put(rt,a^u)
        elif op==15: put(rt,u<<16)
        elif op in (32,33,35,36,37):
            size={32:1,33:2,35:4,36:1,37:2}[op]
            addr=(a+imm)&MASK
            if addr%size: raise ValueError("unaligned load")
            v=int.from_bytes(self.read(addr,size),"little")
            if op in (32,33) and v>>(size*8-1): v-=1<<(size*8)
            load=(rt,v&MASK)
        elif op in (40,41,43):
            size={40:1,41:2,43:4}[op]
            addr=(a+imm)&MASK
            if addr%size: raise ValueError("unaligned store")
            self.write(addr,(b&((1<<(size*8))-1)).to_bytes(size,"little"))
        else: raise NotImplementedError((hex(pc),hex(w)))
        if self.pending_load:
            reg,value=self.pending_load
            if reg and reg not in writes:
                self.r[reg]=value
        for reg,value in writes.items():
            self.r[reg]=value
        self.r[0]=0
        self.pending_load=load
        self.pc,self.npc=self.npc,next_pc
        self.steps+=1


class CardEnvironment:
    HANDLE_ADDRS = ([0x800cd908,0x800cd90c,0x800cd910,0x800cd914],
                    [0x800cd918,0x800cd91c,0x800cd920,0x800cd928])
    def __init__(self, cpu, entries, info=None, load=None, post=None):
        self.cpu=cpu;self.entries=entries;self.cursor=0;self.events={}
        self.commands=[];self.patterns=[];self.test_calls=0
        self.responses={"info":list([0] if info is None else info),
                        "load":list([0] if load is None else load),
                        "post":list([0] if post is None else post)}
        self.handles=[]
        for group,addresses in enumerate(self.HANDLE_ADDRS):
            current=[]
            for index,address in enumerate(addresses):
                handle=0xf1000000+group*4+index
                cpu.write(address,struct.pack("<I",handle));self.events[handle]=False
                current.append(handle)
            self.handles.append(current)
        cpu.hooks={0x8007e4ac:self.test_event,
                   0x8007e6cc:lambda c:self.command("info",0),
                   0x8007e6dc:lambda c:self.command("post",0),
                   0x8007e70c:lambda c:self.command("load",1),
                   0x8007e54c:self.firstfile,0x8007e55c:self.nextfile}

    def command(self,name,group):
        queue=self.responses[name]
        response=queue.pop(0) if len(queue)>1 else queue[0]
        self.commands.append((name,response))
        if response is not None:self.events[self.handles[group][response]]=True
        return 1

    def test_event(self,c):
        handle=c.r[4];self.test_calls+=1
        if handle not in self.events:raise ValueError("unknown event handle "+hex(handle))
        result=int(self.events[handle]);self.events[handle]=False
        return result

    def put_entry(self,c,address,index):
        if index>=len(self.entries):return 0
        name,size=self.entries[index];entry=bytearray(40)
        entry[:min(len(name),20)]=name[:20]
        struct.pack_into("<I",entry,24,size&0xffffffff)
        c.write(address,entry);return address

    def firstfile(self,c):
        self.patterns.append(c.cstring(c.r[4]).decode("ascii"))
        self.cursor=0
        return self.put_entry(c,c.r[5],0)

    def nextfile(self,c):
        self.cursor+=1
        return self.put_entry(c,c.r[4],self.cursor)


import hashlib
import json
import itertools
import argparse
import zipfile

EXE_SHA256="d6a167a1c9e0fe98d7e44e12968caa489ac3eb7ed3b9e46012a188af8432b1fd"
NAME=b"BISLPS-00782CONV"+bytes(1)

def interpreter_sanity(exe):
    c=Cpu(exe)
    # lw then dependent move must see OLD value; next move sees loaded value.
    # The taken branch executes its delay slot and skips the following word.
    words=[0x24020007,0x8c830000,0x00602821,0x00603021,
           0x10000002,0x24070009,0x24070063,0x03e00008,0]
    c.write(0x80001000,b"".join(struct.pack("<I",w) for w in words))
    c.write(0x80100000,struct.pack("<I",0x12345678))
    assert c.run(0x80001000,[0x80100000])==7
    assert c.r[5]==0 and c.r[6]==0x12345678 and c.r[7]==9
    c.write(0xa0100000,b"ABCD")
    assert c.read(0x80100000,4)==b"ABCD"
    return dict(load_delay=True,branch_delay=True,kseg_ram_alias=True)

def expected_blocks(size):
    value=signed((size-1)&MASK)
    if value<0:value=signed((value+8191)&MASK)
    return (value>>13)+1

def expected_status(entries,mode):
    total=0
    for name,size in entries:
        total=signed((total+expected_blocks(size))&MASK)
        padded=name[:20]+bytes(max(0,17-len(name)))
        if padded[:17]==NAME:
            return 0
    return 2 if (mode&255)!=0 or total<2 else 1

def main_suite(exe):
    if hashlib.sha256(exe).hexdigest()!=EXE_SHA256:
        raise ValueError("source EXE SHA-256 mismatch")
    sanity=interpreter_sanity(exe)
    c=Cpu(exe);c.write(0x80100100,NAME)
    leaf=[]
    for offset in range(17):
        for value in range(256):
            if value==NAME[offset]:continue
            changed=bytearray(NAME);changed[offset]=value
            c.write(0x80100000,changed)
            got=c.run(0x8007b7c0,[0x80100000,0x80100100])
            assert got==1,(offset,value,got)
            leaf.append([offset,value,got,c.steps])
    extra=[]
    for tail in [bytes(32),bytes([255])*32,b"arbitrary suffix"]:
        c.write(0x80100000,NAME+tail)
        got=c.run(0x8007b7c0,[0x80100000,0x80100100])
        assert got==0;extra.append(dict(kind="bytes_after_17_ignored",tail_hex=tail.hex(),result=got))
    for value in [1,65,255]:
        forged=NAME[:16]+bytes([value])
        c.write(0x80100000,forged);c.write(0x80100100,forged)
        got=c.run(0x8007b7c0,[0x80100000,0x80100100])
        assert got==1;extra.append(dict(kind="equal_but_non_nul_at_16",value=value,result=got))
    statuses=[]
    scenarios=[("empty",[]),("one_other_block",[(b"OTHER",8192)]),
               ("two_other_blocks",[(b"OTHER",16384)]),
               ("wrong_name_14_blocks",[(b"TOWN0001",114688)]),
               ("correct_name_14_blocks",[(NAME,114688)]),
               ("correct_plus_one_before",[(b"OTHER",8192),(NAME,114688)]),
               ("correct_plus_one_after",[(NAME,114688),(b"OTHER",8192)])]
    for count in range(3,16):
        scenarios.append(("other_files_"+str(count),[(("OTHER"+str(i)).encode(),8192) for i in range(count)]))
    for label,entries in scenarios:
        for mode in [0,1]:
            cpu=Cpu(exe);env=CardEnvironment(cpu,entries)
            got=cpu.run(0x8007b1f8,[mode])
            expected=expected_status(entries,mode)
            assert got==expected and cpu.read(0x800cd820,1)[0]==got,(label,got,expected)
            assert env.patterns==["bu00:*"]
            statuses.append(dict(case=label,mode=mode,result=got,steps=cpu.steps,
                                 commands=env.commands,entries=[dict(name=n.hex(),size=s) for n,s in entries]))
    diagnostics=[]
    for size in [0,1,8191,8192,8193,16384,114688,122880,0x7fffffff,0x80000000,0xffffffff]:
        for mode in [0,1,255,256,257]:
            entries=[(b"OTHER",size)]
            cpu=Cpu(exe);env=CardEnvironment(cpu,entries)
            got=cpu.run(0x8007b1f8,[mode])
            assert got==expected_status(entries,mode)
            diagnostics.append(dict(size_u32=size,mode=mode,source_blocks=expected_blocks(size),result=got,
                                    scope="artificial boundary input, not all are valid card metadata"))
    triples=[]
    for info,load,post in itertools.product(range(4),repeat=3):
        cpu=Cpu(exe);env=CardEnvironment(cpu,[],info=[info],load=[load],post=[post])
        got=cpu.run(0x8007b1f8,[0])
        # Independent state-machine prediction for constant responses.
        if info==1: expected=5;counts=dict(info=3,load=0,post=0)
        elif info==2:expected=4;counts=dict(info=30,load=0,post=0)
        else:
            expected={0:2,1:5,2:4,3:3}[post]
            outer=10 if post==2 else 1
            counts=dict(info=outer,load=outer,post=outer*(3 if post in (1,2) else 1))
        actual={n:sum(1 for op,_ in env.commands if op==n) for n in counts}
        assert got==expected and actual==counts,(info,load,post,got,actual,counts)
        triples.append(dict(info=info,load=load,post=post,result=got,commands=actual,steps=cpu.steps))
    recoveries=[]
    for label,config,expected_counts in [
        ("info_busy_twice_then_success",dict(info=[2,2,0]),dict(info=3,load=1,post=1)),
        ("post_busy_twice_then_success",dict(post=[2,2,0]),dict(info=1,load=1,post=3)),
        ("post_busy_three_then_next_outer_success",dict(post=[2,2,2,0]),dict(info=2,load=2,post=4))]:
        cpu=Cpu(exe);env=CardEnvironment(cpu,[],**config)
        got=cpu.run(0x8007b1f8,[0])
        actual={n:sum(1 for op,_ in env.commands if op==n) for n in expected_counts}
        assert got==2 and actual==expected_counts
        recoveries.append(dict(case=label,result=got,commands=env.commands,steps=cpu.steps))
    stalls=[]
    for stage in ["info","load","post"]:
        cpu=Cpu(exe);env=CardEnvironment(cpu,[],**{stage:[None]})
        try:cpu.run(0x8007b1f8,[0],limit=20000)
        except TimeoutError:pass
        else:raise AssertionError("missing event unexpectedly returned")
        stalls.append(dict(stage=stage,outcome="instruction_limit",steps=cpu.steps,commands=env.commands))
    evidence=[]
    for start,end in [(0x8007b1f8,0x8007b45c),(0x8007b7c0,0x8007b8a4),
                      (0x8007b920,0x8007bc14),(0x8007c110,0x8007c3a8)]:
        data=exe[start-0x80010000+0x800:end-0x80010000+0x800]
        evidence.append(dict(start=hex(start),end_exclusive=hex(end),sha256=hashlib.sha256(data).hexdigest(),words_le=[hex(w[0]) for w in struct.iter_unpack("<I",data)]))
    return dict(source_exe_sha256=EXE_SHA256,scope="original integer instruction execution in a new limited interpreter with controlled BIOS boundary hooks; not physical PS1 or BIOS emulation",
                interpreter_sanity=sanity,filename_mutations=leaf,filename_extra=extra,normal_directory_cases=statuses,
                artificial_boundary_cases=diagnostics,event_triples=triples,retry_recoveries=recoveries,missing_event_stalls=stalls,
                counts=dict(filename_mutations=len(leaf),filename_extra=len(extra),normal_directory=len(statuses),
                            artificial_boundaries=len(diagnostics),event_triples=len(triples),retry_recoveries=len(recoveries),stalls=len(stalls)),
                evidence=evidence,all_checks_passed=True)

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("source",help="r2 ZIP or extracted SLPS_007.82")
    args=parser.parse_args()
    if zipfile.is_zipfile(args.source):
        with zipfile.ZipFile(args.source) as z:exe=z.read("algorithm-analysis/source/SLPS_007.82")
    else:
        with open(args.source,"rb") as f:exe=f.read()
    print(json.dumps(main_suite(exe),ensure_ascii=False,separators=(",",":")))

if __name__=="__main__":
    main()
