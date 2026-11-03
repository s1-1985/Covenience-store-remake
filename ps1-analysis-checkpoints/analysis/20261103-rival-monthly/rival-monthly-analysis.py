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



import copy,hashlib,json,sys,zlib,zipfile
ZIP_PATH=sys.argv[1] if len(sys.argv)>1 else '/workspace/scratch/03bc5bb46781/upload/Conveni-PS1-Analysis-Checkpoint-20261103-r2(1).zip'
sys.path.insert(0,ZIP_PATH+'/algorithm-analysis')
from rival_management import monthly
from town_mutation import descriptors as building_descriptors
from store_lifecycle import initialize
from recovered import rng_next

def u32(c,a):return struct.unpack("<I",c.read(a,4))[0]
def i32read(c,a):return struct.unpack("<i",c.read(a,4))[0]
def state_from(c,layouts):
    return dict(stores=[bytearray(c.read(0x8012b2f8+j*5080,5080)) for j in range(10)],
                staff=[bytearray(c.read(0x80143ff8+j*60,60)) for j in range(35)],
                town=bytearray(c.read(0x801398f0,24000)),queue=bytearray(c.read(0x80137970,8000)),
                text=c.read(0x800e4020,120),demolition_mask=bytearray(c.read(0x800cda50,3000)),
                cash=[i32read(c,0x800cd9f8+j*4) for j in range(2)],
                capital=[i32read(c,0x800d8f68+j*16) for j in range(2)],
                order=list(struct.unpack("<10i",c.read(0x800ce61c,40))),
                minute=i32read(c,0x800ce618),hour=i32read(c,0x800ce614),stage=i32read(c,0x800ce610),
                month=i32read(c,0x800ce60c),seed=u32(c,0x800d6270),
                serial=int.from_bytes(c.read(0x800cd9e2,2),"little"),
                size_control=c.read(0x800cd994,1)[0],layout_control=c.read(0x800cd8a8,1)[0],
                custom=[c.read(0x8013f6c0+j*3108,3108) for j in range(6)],
                dirty=c.read(0x801398bc,1)[0],town_dirty=c.read(0x800cd8dc,1)[0],refreshes=0)
def tables(c,z):
    return dict(table=building_descriptors(json.loads(z.read('algorithm-analysis/town-building-tables.json'))['buildings']),
                prices=[i32read(c,0x80099f10+j*196) for j in range(53)],
                products=[struct.unpack("<2i",c.read(0x8009ce08+j*88,8)) for j in range(27)],
                images=[struct.unpack("<12i",c.read(0x8009ce14+j*88,48)) for j in range(27)],
                layouts=[bytes.fromhex(x['raw_hex']) for x in json.loads(z.read('algorithm-analysis/layout-tables.json'))['layouts']],
                defaults=[i32read(c,0x8009ce10+j*88) for j in range(27)],
                dimensions=[struct.unpack("<2i",c.read(0x80099f30+j*196,8)) for j in range(53)],
                offsets=[struct.unpack("<2i",c.read(0x800997c8+j*8,8)) for j in range(3)],
                staff_types=c.read(0x800cd6f4,6))
def compare_rival(cpu,t):
    state=state_from(cpu,t['layouts'])
    expected=monthly(copy.deepcopy(state),**t)
    refresh=[]
    for address in (0x8006d758,0x8006d204,0x8006d3f8):
        cpu.hooks[address]=lambda c:c.r[2]
    def cache(c):refresh.append(1);return c.r[2]
    cpu.hooks[0x80023c20]=cache
    ret=cpu.run(0x8002a8e0,limit=15000000,stack_pointer=0x801d0000,global_pointer=0x800cd6c4)
    regions=[]
    for name,address,got in [('stores',0x8012b2f8,b''.join(expected['stores'])),
                             ('staff',0x80143ff8,b''.join(expected['staff'])),
                             ('town',0x801398f0,expected['town']),
                             ('queue',0x80137970,expected['queue']),
                             ('demolition',0x800cda50,expected['demolition_mask'])]:
        actual=cpu.read(address,len(got))
        if actual!=got:raise AssertionError((name,expected['reason'],[(i,a,b) for i,(a,b) in enumerate(zip(actual,got)) if a!=b][:8]))
        regions.append(dict(name=name,bytes=len(got),sha256=hashlib.sha256(actual).hexdigest()))
    for j in range(2):
        assert i32read(cpu,0x800cd9f8+j*4)==expected['cash'][j],('cash',j)
        assert i32read(cpu,0x800d8f68+j*16)==expected['capital'][j],('capital',j)
    assert u32(cpu,0x800d6270)==expected['seed'],'rng'
    assert int.from_bytes(cpu.read(0x800cd9e2,2),'little')==expected['serial'],'serial'
    assert cpu.read(0x801398bc,1)[0]==expected['dirty']
    assert cpu.read(0x800cd8dc,1)[0]==expected['town_dirty']
    assert len(refresh)==expected['refreshes']
    return dict(reason=expected['reason'],steps=cpu.steps,seed_before=state['seed'],seed_after=expected['seed'],
                cash_before=state['cash'],cash_after=expected['cash'],events=expected['events'],
                regions=regions,costs=expected.get('costs'),return_value=ret,hook_calls=cpu.calls)


SOURCE_RAM="algorithm-analysis/source/opened-snapshots-20261028/TOWN0001-nov3-two-own-nextday-single.ram.zlib"
NativeCpu=Cpu
class Cpu(NativeCpu):
    def __init__(self,exe):
        super().__init__(exe);self.exe=exe;self.visited={}
    def step(self):
        if self.pc not in self.visited:
            offset=self.pc-0x80010000+0x800
            if offset<0x800 or offset+4>len(self.exe):raise AssertionError("instruction outside EXE")
            actual=self.read(self.pc,4)
            if actual!=self.exe[offset:offset+4]:raise AssertionError("modified instruction "+hex(self.pc))
            self.visited[self.pc]=struct.unpack("<I",actual)[0]
        super().step()

def set32(c,a,v):c.write(a,struct.pack("<I",v&0xffffffff))
def prepare(exe,ram,controls):
    c=Cpu(exe);c.mem[:]=ram
    if controls.get("monthly",True):
        for a,v in [(0x800ce618,0),(0x800ce614,0),(0x800ce610,1),(0x800ce60c,controls.get("month",3))]:set32(c,a,v)
    for key,address in [("minute",0x800ce618),("hour",0x800ce614),("stage",0x800ce610),("seed",0x800d6270),("cash",0x800cd9fc)]:
        if key in controls:set32(c,address,controls[key])
    if controls.get("land_level") is not None:
        for j in range(3000):c.write(0x801398f0+j*8+2,bytes([controls["land_level"]]))
    rival=0x8012b2f8+5080
    if "loss" in controls:c.write(rival+0xd4c,struct.pack("<5i",100,0,0,0,0) if controls["loss"] else struct.pack("<5i",0,0,0,0,100))
    if "streak" in controls:c.write(rival+0x1184,struct.pack("<H",controls["streak"]))
    if controls.get("two_rivals"):
        c.write(0x8012b2f8+2*5080+4,struct.pack("<H",0x8002))
    if controls.get("second_closure"):
        second=0x8012b2f8+2*5080
        c.write(second+0xd4c,struct.pack("<5i",100,0,0,0,0))
        c.write(second+0x1184,struct.pack("<H",5))
    if controls.get("nine_own") or controls.get("no_slot"):
        for j in range(10):
            a=0x8012b2f8+j*5080
            if not c.read(a,1)[0]:
                c.write(a,bytes(5080));c.write(a,bytes([1]))
                c.write(a+4,struct.pack("<H",j+1))
                c.write(a+8,struct.pack("<4i",2+4*j,2,3+4*j,3))
                c.write(a+0xdd8,struct.pack("<3h",-1,-1,-1))
        c.write(0x800ce61c,struct.pack("<10i",*range(10)))
    if controls.get("rival_serial")==2:c.write(rival+4,struct.pack("<H",0x8002))
    if controls.get("no_staff"):
        for j in range(35):c.write(0x80143ff8+j*60,struct.pack("<H",0x1234))
    return c

def additions(before,c):
    stores=[];staff=[]
    for j in range(10):
        a=0x12b2f8+j*5080
        old=before[a:a+5080];new=c.read(0x80000000+a,5080)
        if old!=new:
            stores.append(dict(slot=j,active_before=old[0],active_after=new[0],
                               flags_before=struct.unpack_from("<H",old,4)[0],flags_after=struct.unpack_from("<H",new,4)[0],
                               loss_before=struct.unpack_from("<H",old,0x1184)[0],loss_after=struct.unpack_from("<H",new,0x1184)[0],
                               staff_before=list(struct.unpack_from("<3h",old,0xdd8)),staff_after=list(struct.unpack_from("<3h",new,0xdd8)),
                               rectangle_after=list(struct.unpack_from("<4i",new,8)),changed_bytes=sum(a!=b for a,b in zip(old,new))))
    for j in range(35):
        a=0x143ff8+j*60;old=before[a:a+60];new=c.read(0x80000000+a,60)
        if old!=new:staff.append(dict(index=j,before=old.hex(),after=new.hex()))
    return dict(store_changes=stores,staff_changes=staff,
                input_ram_sha256=hashlib.sha256(before).hexdigest(),output_ram_sha256=hashlib.sha256(c.mem).hexdigest(),
                unique_original_instructions=len(c.visited))

def run_suite():
    digest=hashlib.sha256()
    with open(ZIP_PATH,'rb') as source:
        for block in iter(lambda:source.read(1048576),b''):digest.update(block)
    if digest.hexdigest()!='afd46b32e0a24e3f2d75723a0c4a3fecc120d80b07993c2e73236e55cf3d54cd':raise ValueError('r2 ZIP hash mismatch')
    with zipfile.ZipFile(ZIP_PATH) as z:
        exe=z.read("algorithm-analysis/source/SLPS_007.82")
        assert hashlib.sha256(exe).hexdigest()=="d6a167a1c9e0fe98d7e44e12968caa489ac3eb7ed3b9e46012a188af8432b1fd"
        packed=z.read(SOURCE_RAM);ram=zlib.decompress(packed)
        assert len(ram)==0x200000
        cases=[];coverage={}
        def run(label,controls,cpu=None):
            c=prepare(exe,ram,controls) if cpu is None else cpu
            before=bytes(c.mem)
            result=compare_rival(c,tables(c,z))
            result.update(additions(before,c));result.update(case=label,controls=controls)
            cases.append(result);coverage.update(c.visited)
            if len(cases)%12==0:print("PROGRESS",len(cases),flush=True)
            return c,result
        run("unaltered_snapshot_time_gate",dict(monthly=False))
        for key,value in [("minute",1),("hour",1),("stage",0),("stage",2)]:
            run("time_gate_"+key+"_"+str(value),dict(seed=0,**{key:value}))
        for seed in range(16):
            run("actual_land_seed_"+str(seed),dict(seed=seed))
            run("raised_land_seed_"+str(seed),dict(seed=seed,land_level=8))
        for streak in [0,4,5,6,32767,65535]:
            for loss in [False,True]:run("loss_counter_"+str(streak)+"_"+str(loss),dict(seed=1,streak=streak,loss=loss))
        for cash in [0,58263654,58263655,58263656,153835247]:
            run("cash_boundary_"+str(cash),dict(seed=0,land_level=8,cash=cash))
        run("all_staff_unavailable",dict(seed=0,land_level=8,no_staff=True))
        run("all_store_slots_active",dict(seed=0,no_slot=True))
        run("first_rival_protected",dict(seed=1,two_rivals=True,loss=True,streak=5))
        run("only_one_closure_per_call",dict(seed=1,two_rivals=True,loss=True,streak=5,second_closure=True))
        for month in [1,2]:
            run("nine_own_month_"+str(month),dict(seed=1,nine_own=True,month=month,loss=False))
        run("nine_own_nonfirst_rival",dict(seed=1,nine_own=True,month=1,loss=False,rival_serial=2))
        c=prepare(exe,ram,dict(seed=1,loss=True,streak=0))
        chain=[]
        for month in range(3,9):
            set32(c,0x800ce60c,month)
            c,r=run("six_loss_chain_month_"+str(month),dict(carried_ram=True,month=month),c)
            chain.append(dict(month=month,reason=r["reason"],rival_active=c.read(0x8012b2f8+5080,1)[0],streak=int.from_bytes(c.read(0x8012b2f8+5080+0x1184,2),"little")))
        assert [x["rival_active"] for x in chain]==[1,1,1,1,1,0]
        c=prepare(exe,ram,dict(seed=1,loss=True,streak=0));recovery=[]
        for step,loss in enumerate([True,True,False,True]):
            c.write(0x8012b2f8+5080+0xd4c,struct.pack("<5i",100,0,0,0,0) if loss else struct.pack("<5i",0,0,0,0,100))
            c,r=run("profit_reset_chain_"+str(step),dict(carried_ram=True,loss=loss),c)
            recovery.append(int.from_bytes(c.read(0x8012b2f8+5080+0x1184,2),"little"))
        assert recovery==[1,2,0,1]
        # Recover the quoted exact cost boundary rather than assuming all fixtures cost this.
        named={c["case"]:c for c in cases}
        assert named["cash_boundary_58263654"]["reason"]=="no_cash"
        assert named["cash_boundary_58263655"]["reason"]=="opened"
        assert named["first_rival_protected"]["reason"]=="rng_gate"
        assert named["only_one_closure_per_call"]["reason"]=="closed"
        assert named["nine_own_month_1"]["reason"]=="closed"
        assert named["nine_own_month_2"]["reason"]=="rng_gate"
        assert named["nine_own_nonfirst_rival"]["reason"]=="rng_gate"
        counts={}
        for c in cases:counts[c["reason"]]=counts.get(c["reason"],0)+1
        output=dict(source_zip_sha256="afd46b32e0a24e3f2d75723a0c4a3fecc120d80b07993c2e73236e55cf3d54cd",
                    source_ram_path=SOURCE_RAM,source_ram_sha256=hashlib.sha256(ram).hexdigest(),
                    source_compressed_ram_sha256=hashlib.sha256(packed).hexdigest(),source_clock=13074,
                    instruction_entry="0x8002a8e0",all_checks_passed=True,total_cases=len(cases),counts=counts,
                    cases=cases,six_loss_chain=chain,profit_reset_chain=recovery,
                    executed_original_words=[[hex(a),hex(w)] for a,w in sorted(coverage.items())],
                    scope="Actual r2 RAM snapshot plus explicit controlled monthly inputs. Original integer instructions compared with archived independent monthly model; text assembly and cache refresh are hooked.",
                    limitations=["These are injected monthly boundaries, not natural elapsed gameplay months.",
                                 "Raised land levels, bound staff and synthetic extra stores are marked control fixtures.",
                                 "No original BIOS, GPU/SPU/IRQ or full game UI execution.",
                                 "Callback hooks preserve V0 rather than treating the monthly routine return register as a success API."])
        print("RESULT",json.dumps(output,ensure_ascii=False,separators=(",",":")),flush=True)
    return output


def capture_checkpoint(name):
    import base64
    controls_by_name={
        "closed":dict(seed=1,loss=True,streak=5),
        "opened":dict(seed=0,land_level=8,cash=153835247),
        "no_cash":dict(seed=0,land_level=8,cash=0)}
    controls=controls_by_name[name]
    with zipfile.ZipFile(ZIP_PATH) as z:
        exe=z.read("algorithm-analysis/source/SLPS_007.82")
        if hashlib.sha256(exe).hexdigest()!="d6a167a1c9e0fe98d7e44e12968caa489ac3eb7ed3b9e46012a188af8432b1fd":raise ValueError("EXE mismatch")
        ram=zlib.decompress(z.read(SOURCE_RAM))
        c=prepare(exe,ram,controls);before=bytes(c.mem)
        result=compare_rival(c,tables(c,z));result.update(additions(before,c))
        packed=zlib.compress(bytes(c.mem),9)
        return dict(kind="controlled diagnostic monthly-function endpoint; not a running-game resume snapshot",
                    name=name,controls=controls,source_ram_path=SOURCE_RAM,
                    ram_sha256=hashlib.sha256(c.mem).hexdigest(),compressed_sha256=hashlib.sha256(packed).hexdigest(),
                    compressed_bytes=len(packed),ram_zlib_base64=base64.b64encode(packed).decode(),
                    pc=hex(c.pc),npc=hex(c.npc),registers=[hex(v) for v in c.r],hi=hex(c.hi),lo=hex(c.lo),
                    comparison=result)

if __name__=="__main__":
    if len(sys.argv)==4 and sys.argv[2]=="--capture":
        print("SNAPSHOT",json.dumps(capture_checkpoint(sys.argv[3]),separators=(",",":")))
    else:
        run_suite()
