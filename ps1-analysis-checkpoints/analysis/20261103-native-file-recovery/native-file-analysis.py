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

    def run(self, address, args=(), limit=200000, stack_pointer=0x801f0000, global_pointer=0):
        self.r = [0]*32
        self.r[29] = stack_pointer
        self.r[28] = global_pointer
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


class LogicalFiles(CardEnvironment):
    def __init__(self,cpu,files):
        self.files={name:bytearray(value) for name,value in files.items()}
        self.fds={};self.next_fd=3;self.io=[]
        entries=[(name.split(b":",1)[1],len(data)) for name,data in self.files.items()]
        super().__init__(cpu,entries)
        cpu.hooks.update({0x8007e4ec:self.open_file,0x8007e4fc:self.seek_file,
                          0x8007e50c:self.read_file,0x8007e51c:self.write_file,
                          0x8007e52c:self.close_file,0x80089ca4:lambda c:0,
                          0x8007e57c:self.memcpy,
                          0x8007e53c:self.aux})
    def open_file(self,c):
        name=c.cstring(c.r[4]);flags=c.r[5]
        self.io.append(dict(op="open",name=name.decode("ascii"),flags=flags))
        if flags&0x200:
            if name in self.files:return -1
            blocks=flags>>16
            self.files[name]=bytearray(blocks*8192)
            self.entries.append((name.split(b":",1)[1],blocks*8192))
        if name not in self.files:return -1
        fd=self.next_fd;self.next_fd+=1;self.fds[fd]=[name,0]
        return fd
    def seek_file(self,c):
        fd,offset,whence=c.r[4:7]
        if fd not in self.fds:return -1
        name,pos=self.fds[fd];offset=signed(offset)
        new=offset if whence==0 else pos+offset if whence==1 else len(self.files[name])+offset
        if new<0:return -1
        self.fds[fd][1]=new
        self.io.append(dict(op="seek",fd=fd,offset=offset,whence=whence,result=new))
        return new
    def read_file(self,c):
        fd,address,size=c.r[4:7]
        if fd not in self.fds:return -1
        name,pos=self.fds[fd];data=bytes(self.files[name][pos:pos+size])
        c.write(address,data);self.fds[fd][1]+=len(data)
        self.io.append(dict(op="read",fd=fd,file_offset=pos,ram=address,requested=size,result=len(data)))
        return len(data)
    def write_file(self,c):
        fd,address,size=c.r[4:7]
        if fd not in self.fds:return -1
        name,pos=self.fds[fd]
        if pos+size>len(self.files[name]):return -1
        data=c.read(address,size)
        self.files[name][pos:pos+size]=data;self.fds[fd][1]+=size
        self.io.append(dict(op="write",fd=fd,file_offset=pos,ram=address,requested=size,result=size))
        return size
    def close_file(self,c):
        fd=c.r[4];self.io.append(dict(op="close",fd=fd))
        if fd not in self.fds:return -1
        del self.fds[fd];return fd
    def memcpy(self,c):
        dst,src,size=c.r[4:7];c.write(dst,c.read(src,size));return dst
    def aux(self,c):
        self.io.append(dict(op="aux_7e53c",args=list(c.r[4:7])));return 0


import argparse
import base64
import hashlib
import json
import zlib
import zipfile

ZIP_SOURCE_SHA="afd46b32e0a24e3f2d75723a0c4a3fecc120d80b07993c2e73236e55cf3d54cd"
EXE_SOURCE_SHA="d6a167a1c9e0fe98d7e44e12968caa489ac3eb7ed3b9e46012a188af8432b1fd"
GP=0x800cd6c4
BODY=0x80187e00
PATH=b"bu00:BISLPS-00782CONV"

def sha(data):
    return hashlib.sha256(data).hexdigest()

def file_suite(exe,payloads):
    assert sha(exe)==EXE_SOURCE_SHA
    records=[]
    for case_index,(source,payload) in enumerate(payloads):
        cpu=Cpu(exe)
        assert struct.unpack("<I",cpu.read(GP+0xa4,4))[0]==BODY
        cpu.write(0x801b0000,bytes([0xa6+case_index])*0x40000)
        cpu.write(0x800d6270,struct.pack("<I",0xdeadbeef))
        env=LogicalFiles(cpu,{})
        previous_header=None
        phases=[]
        for phase_index in range(2):
            current_path,current_payload=payloads[(case_index+phase_index)%len(payloads)]
            tail=bytes([0xa5 if phase_index==0 else 0x5a])*9812
            body=current_payload+tail
            cpu.write(BODY,body)
            log_start=len(env.io)
            calls=[]
            for mode in [0,1]:
                result=cpu.run(0x8007adf8,[mode],limit=1000000,
                               stack_pointer=0x801d0000,global_pointer=GP)
                assert result==0
                calls.append(dict(function="7ADF8",mode=mode,return_value=result,steps=cpu.steps))
            saved=bytes(env.files[PATH])
            assert len(saved)==114688 and saved[:4]==bytes.fromhex("53 43 13 0e")
            assert saved[512:]==body
            header=saved[:512]
            if previous_header is not None:assert header==previous_header
            previous_header=header
            cpu.write(BODY,bytes([0xcc])*114176)
            for mode in [0,1]:
                result=cpu.run(0x8007ab2c,[mode],limit=1000000,
                               stack_pointer=0x801d0000,global_pointer=GP)
                assert result==0
                calls.append(dict(function="7AB2C",mode=mode,return_value=result,steps=cpu.steps))
            assert cpu.read(BODY,114176)==body
            assert cpu.read(0x800d6270,4)==struct.pack("<I",0xdeadbeef)
            io=env.io[log_start:]
            opens=[x for x in io if x["op"]=="open"]
            create=[x for x in opens if x["flags"]&0x200]
            assert len(create)==(1 if phase_index==0 else 0)
            if create:assert create[0]["flags"]==0xe0200
            writes=[x for x in io if x["op"]=="write" and x["requested"]==128]
            reads=[x for x in io if x["op"]=="read" and x["requested"]==128]
            for transfers in [writes,reads]:
                assert len(transfers)==892
                assert [x["file_offset"] for x in transfers]==list(range(512,114688,128))
                assert all(x["requested"]==x["result"]==128 for x in transfers)
                assert [x["ram"] for x in transfers]==list(range(BODY,BODY+114176,128))
            trace=json.dumps(io,separators=(",",":")).encode()
            phases.append(dict(kind="create" if phase_index==0 else "overwrite",
                               payload_source=current_path,payload_sha256=sha(current_payload),
                               tail_byte=tail[0],calls=calls,header_sha256=sha(header),
                               retained_header_padding_hex=header[13:96].hex(),
                               logical_file_sha256=sha(saved),logical_file_bytes=len(saved),
                               file_base64=base64.b64encode(saved).decode(),
                               trace_events=len(io),trace_sha256=sha(trace),
                               trace_zlib_base64=base64.b64encode(zlib.compress(trace,9)).decode(),
                               body_writes=len(writes),body_reads=len(reads),create_flags=[x["flags"] for x in create],
                               rng_preserved=True,header_preserved_on_overwrite=phase_index==1))
        records.append(dict(case_index=case_index,initial_payload_source=source,phases=phases))
    return dict(scope="Original file routines plus controlled logical BIOS file/event boundaries; not physical card allocation or communication",
                source_exe_sha256=EXE_SOURCE_SHA,source_zip_sha256=ZIP_SOURCE_SHA,
                stack_pointer="0x801d0000",global_pointer=hex(GP),buffer_pointer_cell=hex(GP+0xa4),
                buffer_pointer_initial_value=hex(BODY),
                counts=dict(source_payloads=len(payloads),create=len(payloads),overwrite=len(payloads),
                            source_calls=sum(len(p["calls"]) for r in records for p in r["phases"])),
                setup_audit=dict(initial_failed_probe="GP was left zero; original writer consequently read buffer pointer at physical 0xA4 and transferred from RAM zero instead of the save buffer.",
                                 correction="Set GP to 0x800CD6C4, as in the archived connected harnesses. Original EXE cell 0x800CD768 already contains 0x80187E00; no pointer patch is needed.",
                                 classification="test harness setup defect, not a game defect"),
                records=records,all_checks_passed=True)

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("zip")
    args=parser.parse_args()
    with zipfile.ZipFile(args.zip) as z:
        exe=z.read("algorithm-analysis/source/SLPS_007.82")
        names=sorted(n for n in z.namelist() if n.startswith("algorithm-analysis/source/operating-save-payloads-20261103/") and n.endswith(".payload.bin"))
        payloads=[(n,z.read(n)) for n in names]
    print(json.dumps(file_suite(exe,payloads),ensure_ascii=False,separators=(",",":")))

if __name__ == "__main__":
    main()
