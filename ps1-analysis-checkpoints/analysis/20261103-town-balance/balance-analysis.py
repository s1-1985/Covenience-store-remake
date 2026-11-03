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



import base64,collections,copy,hashlib,json,sys,zlib,zipfile
ZIP_PATH=sys.argv[1]
sys.path.insert(0,ZIP_PATH+"/algorithm-analysis")
import town_growth as growth
import town_mutation as mutation
from recovered import rng_next,i32

TOWN=0x801398f0
SEED=0x800d6270
STORE=0x8012b2f8
SOURCE_RAM="algorithm-analysis/source/opened-snapshots-20261028/TOWN0001-nov3-two-own-nextday-single.ram.zlib"

def word(c,a):return struct.unpack("<I",c.read(a,4))[0]
def sword(c,a):return struct.unpack("<i",c.read(a,4))[0]
def h(c):return hashlib.sha256(c).hexdigest()
def world(c):return bytearray(c.read(TOWN,24000))
def ordered_stores(c):
    out=[]
    for j in struct.unpack("<10i",c.read(0x800ce61c,40)):
        if j==-1:break
        a=STORE+j*5080
        out.append(dict(rect=list(struct.unpack("<4i",c.read(a+8,16))),value=sword(c,a+0xd5c)))
    return out
def all_stores(c):
    out=[]
    for j in range(10):
        a=STORE+j*5080
        out.append(dict(active=c.read(a,1)[0],rect=list(struct.unpack("<4i",c.read(a+8,16))),
                        c74=c.read(a+0xc74,1)[0],c75=c.read(a+0xc75,1)[0],c76=c.read(a+0xc76,1)[0]))
    return out
def population(c,category):
    town=world(c);total=0
    for index in range(3000):
        a=index*8;group=struct.unpack_from("<h",town,a+6)[0]
        if group==-1 or category and town[a+4]!=category:continue
        for j in range(5):
            kind,value=struct.unpack("<2h",c.read(0x8009ff1c+group*20+j*4,4))
            if kind!=-1:total=i32(total+value)
    return total
def action_model(town,x,y,table,seed):
    calls=[];index=(y*60+x)*8
    level=growth.s8(town[index+2]);tile=struct.unpack_from("<h",town,index)[0]
    if level<4:
        seed,r=rng_next(seed)
        if r%100+1<3:
            calls.append(["lookup"])
            if table[growth.building_kind(tile,table)]["category"]==3:
                calls.append(["demolish",0]);seed=mutation.demolish(town,x,y,0,table,seed)
                level=growth.s8(town[index+2])
    if level>=8:
        seed,r=rng_next(seed)
        if r%100+1<3:
            seed,r=rng_next(seed);kind=43+r%(6 if level<15 else 7)
            calls.append(["feasibility",kind])
            if mutation.feasibility(town,x,y,kind,table)==0:
                calls.append(["place",kind,0]);seed=mutation.place(town,x,y,kind,0,table,seed)
    return town,seed,calls

BaseCpu=Cpu
class TownCpu(BaseCpu):
    def __init__(self,exe,table):
        super().__init__(exe)
        self.exe=exe;self.table=table;self.pending=[];self.phase=None;self.trace=[]
        self.counts=collections.Counter();self.visited={};self.base_population=None
        self.direct_calls=[];self.phase_counts=collections.Counter();self.phase_source_kinds=collections.Counter()
    def grid(self,fp):
        return list(struct.unpack("<3000b",self.read(fp+24,3000)))
    def validate_end(self,item):
        name,ret,expected,args=item
        if name in ("rng","population","kind","nearby","feasibility","choose"):
            value,seed=expected
            assert i32(self.r[2])==value,(name,hex(self.pc),i32(self.r[2]),value,args)
            if seed is not None:assert word(self,SEED)==seed,(name,"seed")
            if name=="population" and ret==0x8002bddc:self.base_population=value
        else:
            town,seed=expected
            assert world(self)==town,(name,"town",args)
            assert word(self,SEED)==seed,(name,"seed",args)
        self.counts[name]+=1
        self.trace.append(["helper",name,hex(ret),args,i32(self.r[2]),word(self,SEED)])
    def helper_entry(self):
        if self.pc not in (0x8007e648,0x80020498,0x80020238,0x80020364,0x8001e8cc,0x8001ff38,0x8001f4b4,0x8001f1c0,0x8001f8bc):return
        pc=self.pc;args=list(self.r[4:8]);seed=word(self,SEED);ret=self.r[31];expected=None;name=None
        if pc==0x8007e648:
            name="rng";ns,value=rng_next(seed);expected=(value,ns)
        elif pc==0x80020498:name="population";expected=(population(self,i32(args[0])),seed)
        elif pc==0x80020238:
            name="kind";tile=mutation.tile(world(self),i32(args[0]),i32(args[1]));expected=(growth.building_kind(tile,self.table),seed)
        elif pc==0x80020364:
            name="choose";kind,ns=growth.choose_kind(i32(args[0]),self.table,seed);expected=(kind,ns)
        elif pc==0x8001e8cc:
            name="feasibility";expected=(mutation.feasibility(world(self),i32(args[0]),i32(args[1]),i32(args[2]),self.table),seed)
        elif pc==0x8001ff38:
            name="nearby";expected=(mutation.nearby(world(self),i32(args[0]),i32(args[1]),i32(args[2]),i32(args[3]),self.table),seed)
        elif pc==0x8001f4b4:
            name="demolish";town=world(self);ns=mutation.demolish(town,i32(args[0]),i32(args[1]),i32(args[2]),self.table,seed);expected=(town,ns)
        elif pc==0x8001f1c0:
            name="place";town=world(self);ns=mutation.place(town,i32(args[0]),i32(args[1]),i32(args[2]),i32(args[3]),self.table,seed);expected=(town,ns)
        elif pc==0x8001f8bc:
            name="flags";town=world(self);mutation.rebuild_flags(town,all_stores(self));expected=(town,seed)
        if name:
            if self.phase and self.phase["name"]=="action" and 0x8002cf7c<=ret<=0x8002d194:
                if name=="kind":self.direct_calls.append(["lookup"])
                elif name=="demolish":self.direct_calls.append(["demolish",i32(args[2])])
                elif name=="feasibility":self.direct_calls.append(["feasibility",i32(args[2])])
                elif name=="place":self.direct_calls.append(["place",i32(args[2]),i32(args[3])])
            self.pending.append((name,ret,expected,args))
    def phase_entry(self):
        if self.pc not in (0x8002c034,0x8002c1b8,0x8002c48c,0x8002c89c,0x8002cdac,0x8002cf7c,0x8002d1cc):return
        pc=self.pc;fp=self.r[30];x=sword(self,fp+0xbec);y=sword(self,fp+0xbf0)
        if pc==0x8002c034:
            expected=growth.base_influence([s["value"] for s in ordered_stores(self)],self.base_population,sword(self,0x800cd9a8))
            assert self.grid(fp)==[expected]*3000,("base",expected,self.grid(fp)[:5])
            self.phase_counts["base"]+=1;self.trace.append(["base",expected,self.base_population])
        elif pc==0x8002c1b8:
            self.phase_source_kinds[("square",growth.building_kind(mutation.tile(world(self),x,y),self.table))]+=1
            self.phase=dict(name="square",fp=fp,grid=growth.square_influence(self.grid(fp),x,y),xy=[x,y],seed=word(self,SEED))
        elif pc==0x8002c48c:
            self.phase_source_kinds[("asymmetric",growth.building_kind(mutation.tile(world(self),x,y),self.table))]+=1
            current=world(self)
            categories=[growth.s8(current[j*8+4]) for j in range(3000)]
            self.phase=dict(name="asymmetric",fp=fp,grid=growth.asymmetric_influence(self.grid(fp),categories,x,y),xy=[x,y],seed=word(self,SEED))
        elif pc==0x8002c89c:
            grid,seed=growth.store_influence(self.grid(fp),ordered_stores(self),sword(self,0x800cd9a0),word(self,SEED))
            self.phase=dict(name="stores",fp=fp,grid=grid,seed=seed,xy=[x,y])
        elif pc==0x8002cdac:
            level=growth.s8(world(self)[(y*60+x)*8+2]);influence=self.grid(fp)[y*60+x]
            after,seed=growth.change_level(level,influence,word(self,SEED))
            self.phase=dict(name="level",xy=[x,y],level=after,seed=seed,before=level,influence=influence)
        elif pc==0x8002d1cc:
            town,seed,details=balance_model(self,world(self),self.table,word(self,SEED))
            self.phase=dict(name="balance",town=town,seed=seed,xy=[-1,-1],details=details)
        elif pc==0x8002cf7c:
            town,seed,calls=action_model(world(self),x,y,self.table,word(self,SEED))
            self.phase=dict(name="action",xy=[x,y],town=town,seed=seed,calls=calls)
            self.direct_calls=[]
    def phase_exit(self):
        pc=self.pc;p=self.phase
        if not p:return
        end={"square":0x8002c444,"asymmetric":0x8002c864,"stores":0x8002cd6c,"level":0x8002cf7c,"action":0x8002d194,"balance":0x8002d770}[p["name"]]
        if pc!=end:return
        if "grid" in p:assert self.grid(p["fp"])==p["grid"],(p["name"],"grid")
        elif p["name"]=="level":
            x,y=p["xy"];assert growth.s8(world(self)[(y*60+x)*8+2])==p["level"],("level",x,y)
        elif p["name"]=="balance":
            assert world(self)==p["town"],("balance","town",p["details"])
            self.balance_details=p["details"]
        elif p["name"]=="action":
            assert world(self)==p["town"],("action","town",p["xy"],self.direct_calls,p["calls"])
            assert self.direct_calls==p["calls"],("action","calls",p["xy"],self.direct_calls,p["calls"])
        assert word(self,SEED)==p["seed"],(p["name"],"seed",p["xy"])
        self.phase_counts[p["name"]]+=1
        self.trace.append(["phase",p["name"],p["xy"],p.get("before"),p.get("influence"),p.get("level"),p["seed"],p.get("calls")])
        self.phase=None
    def step(self):
        if self.pending and self.pc==self.pending[-1][1]:self.validate_end(self.pending.pop())
        self.phase_exit()
        self.phase_entry()
        self.helper_entry()
        if self.pc not in self.visited:
            offset=self.pc-0x80010000+0x800
            assert 0x800<=offset<=len(self.exe)-4,("outside",hex(self.pc))
            actual=self.read(self.pc,4);assert actual==self.exe[offset:offset+4],("modified",hex(self.pc))
            self.visited[self.pc]=struct.unpack("<I",actual)[0]
        super().step()



def population_in(c,town,category):
    total=0
    for index in range(3000):
        a=index*8;group=struct.unpack_from("<h",town,a+6)[0]
        if group==-1 or category and town[a+4]!=category:continue
        for j in range(5):
            kind,value=struct.unpack("<2h",c.read(0x8009ff1c+group*20+j*4,4))
            if kind!=-1:total=i32(total+value)
    return total

def scan_balance(town,table,seed,category,difference):
    seed,r=rng_next(seed);start_x=r%60
    seed,r=rng_next(seed);start_y=r%50
    draws=2;considered=0
    for dy in range(50):
        y=(start_y+dy)%50
        for dx in range(60):
            x=(start_x+dx)%60;index=(y*60+x)*8
            level=growth.s8(town[index+2]);considered+=1
            if difference<0 and level<3:
                kind=growth.building_kind(struct.unpack_from("<h",town,index)[0],table)
                if table[kind]["category"]==category:
                    seed=mutation.demolish(town,x,y,0,table,seed)
                    return town,seed,dict(category=category,difference=difference,action="demolish",kind=kind,x=x,y=y,start=[start_x,start_y],cells_considered=considered,parent_rng_draws=draws)
            elif difference>0 and level>=9:
                kind,seed=growth.choose_kind(category,table,seed);draws+=1
                if mutation.feasibility(town,x,y,kind,table)==0:
                    seed=mutation.place(town,x,y,kind,0,table,seed)
                    return town,seed,dict(category=category,difference=difference,action="place",kind=kind,x=x,y=y,start=[start_x,start_y],cells_considered=considered,parent_rng_draws=draws)
    return town,seed,dict(category=category,difference=difference,action="none",start=[start_x,start_y],cells_considered=considered,parent_rng_draws=draws)

def balance_model(c,town,table,seed):
    home=population_in(c,town,3);office=population_in(c,town,4)
    town,seed,office_action=scan_balance(town,table,seed,4,i32(home-office))
    commercial=population_in(c,town,5)
    quarter=(-1 if home<0 else 1)*(abs(home)//4)
    town,seed,commercial_action=scan_balance(town,table,seed,5,i32(quarter-commercial))
    return town,seed,dict(home_population_cached=home,office_population=office,commercial_population=commercial,
                         home_quarter_truncated=quarter,office=office_action,commercial=commercial_action)


ZIP_SHA="afd46b32e0a24e3f2d75723a0c4a3fecc120d80b07993c2e73236e55cf3d54cd"
EXE_SHA="d6a167a1c9e0fe98d7e44e12968caa489ac3eb7ed3b9e46012a188af8432b1fd"
CASES={
 "company_remove_2":dict(level=2,empty_categories=[3],expected=["demolish","demolish"]),
 "company_keep_3":dict(level=3,empty_categories=[3],expected=["none","none"]),
 "company_noadd_8":dict(level=8,empty_categories=[],expected=["none","none"]),
 "company_add_9":dict(level=9,empty_categories=[],expected=["place","none"]),
 "all_balance_zero":dict(level=9,empty_categories=[3,4,5],expected=["none","none"]),
 "commercial_add_9":dict(level=9,empty_categories=[5],expected=["place","place"]),
 "commercial_noadd_8":dict(level=8,empty_categories=[5],expected=["none","none"]),
 "commercial_remove_2":dict(level=2,empty_categories=[],expected=["none","demolish"]),
 "commercial_keep_3":dict(level=3,empty_categories=[],expected=["none","none"]),
 "whole_base":dict(whole=True,empty_categories=[]),
 "whole_level0":dict(whole=True,level=0,empty_categories=[]),
 "whole_level15":dict(whole=True,level=15,empty_categories=[]),
 "whole_company_surplus":dict(whole=True,level=0,empty_categories=[3]),
 "whole_commercial_shortage":dict(whole=True,level=15,empty_categories=[5]),
 "whole_zero":dict(whole=True,level=4,empty_categories=[3,4,5])
}

def run_balance_case(name,seed):
    digest=hashlib.sha256()
    with open(ZIP_PATH,"rb") as source:
        for block in iter(lambda:source.read(1048576),b""):digest.update(block)
    assert digest.hexdigest()==ZIP_SHA
    with zipfile.ZipFile(ZIP_PATH) as z:
        exe=z.read("algorithm-analysis/source/SLPS_007.82");assert h(exe)==EXE_SHA
        ram=zlib.decompress(z.read(SOURCE_RAM))
        table=mutation.descriptors(json.loads(z.read("algorithm-analysis/town-building-tables.json"))["buildings"])
    controls=copy.deepcopy(CASES[name]);controls["seed"]=seed
    c=TownCpu(exe,table);c.mem[:]=ram
    c.write(SEED,struct.pack("<I",seed&0xffffffff))
    for j in range(3000):
        a=TOWN+j*8
        if "level" in controls:c.write(a+2,bytes([controls["level"]]))
        if c.read(a+4,1)[0] in controls["empty_categories"]:c.write(a+6,b"\xff\xff")
    if controls.get("whole"):
        for a,v in [(0x800ce618,0),(0x800ce614,0),(0x800ce610,1)]:c.write(a,struct.pack("<I",v))
        for a in (0x8006d204,0x8006d3f8):c.hooks[a]=lambda c:c.r[2]
    before=bytes(c.mem);start=bytes(world(c))
    if controls.get("whole"):
        c.run(0x8002bd54,limit=30000000,stack_pointer=0x801d0000,global_pointer=0x800cd6c4)
    else:
        # Controlled parent slice: no claim of natural caller arrival.
        fp=0x801d0000-0xc48
        c.write(fp,bytes(0xc48))
        c.r=[0]*32;c.r[28]=0x800cd6c4;c.r[29]=fp;c.r[30]=fp;c.r[31]=0x80000080
        c.pc=0x8002d1cc;c.npc=c.pc+4;c.pending_load=None;c.steps=0
        while c.pc!=0x8002d770:
            if c.steps>=15000000:raise TimeoutError("balance slice")
            c.step()
        c.phase_exit()
    assert not c.pending and c.phase is None and c.phase_counts["balance"]==1
    details=c.balance_details
    actual_actions=[details["office"]["action"],details["commercial"]["action"]]
    if "expected" in controls:assert actual_actions==controls["expected"],(name,seed,actual_actions)
    end=bytes(world(c))
    changes=[dict(x=j%60,y=j//60,before_hex=start[j*8:j*8+8].hex(),after_hex=end[j*8:j*8+8].hex())
             for j in range(3000) if start[j*8:j*8+8]!=end[j*8:j*8+8]]
    trace=json.dumps(c.trace,separators=(",",":")).encode()
    return dict(case=name,mode="whole_function_arrival" if controls.get("whole") else "controlled_parent_slice",
                controls=controls,all_checks_passed=True,source_zip_sha256=ZIP_SHA,source_exe_sha256=EXE_SHA,
                source_ram_path=SOURCE_RAM,input_ram_sha256=h(before),output_ram_sha256=h(c.mem),
                steps=c.steps,phase_counts=dict(c.phase_counts),helper_counts=dict(c.counts),details=details,
                seed_after=word(c,SEED),changes=changes,trace_events=len(c.trace),trace_sha256=h(trace),
                trace_zlib_base64=base64.b64encode(zlib.compress(trace,9)).decode(),
                executed_original_words=[[hex(a),hex(w)] for a,w in sorted(c.visited.items())],
                limitations=["Controlled slice cases explicitly set FP/SP at 8002D1CC and stop at 8002D770.",
                             "Whole cases enter 8002BD54, with explicit monthly/level/group controls.",
                             "No full game, physical BIOS, GPU/SPU/IRQ or natural elapsed-month claim."])

if __name__=="__main__":
    name=sys.argv[2] if len(sys.argv)>2 else "company_add_9"
    seed=int(sys.argv[3],0) if len(sys.argv)>3 else 1
    print(json.dumps(run_balance_case(name,seed),ensure_ascii=False,separators=(",",":")))
