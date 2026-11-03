"""Wholeoriginal play loop body, explicit child endpoints, independent controller."""
from check_machine import *
from caller_connection_harness import Memory
from mainplay_iteration import iteration,S
from recovered import i32
from unicorn import UC_HOOK_CODE
import itertools,json,hashlib
R=Path(__file__).resolve().parent
CALLS={0x80065974:0,0x80065b9c:1,0x8006dbf0:0,0x80066234:0,0x80018940:2,0x8004ea68:0,0x80066070:1,0x8004a27c:1,0x80041218:1,0x80065000:0,0x80065040:0,0x800650c0:0,0x8005fe54:0,0x80062a4c:2,0x80020238:2,0x80060d6c:0,0x8004d104:4,0x800656f8:0,0x80041a08:0,0x80018a5c:0,0x8005f500:0,0x80060418:0,0x80066818:3,0x8003ff00:0,0x80023438:0,0x80013ddc:0,0x8006d8ec:1,0x80065a1c:0}
RAWS=(0,0x80,0x10,0x20,0x40,0x800,0xc,0xfff)
def compare(view,raw,case):
 u=machine();m=Memory(u);u.reg_write(UC_MIPS_REG_FP,0x801effa0);u.reg_write(UC_MIPS_REG_SP,0x801effa0)
 for a,v in ((0x8013796c,case%10 if view==2 else -1),(0x800cd97c,view),(0x800cd884,raw),(0x800cd850,0x9000),(0x800cd7f4,case%3),(0x800cd9a4,case%2),(0x800cd9cc,0),(0x800cd7e0,123),(0x800cd9d8,456),(0x801398b4,case%2)):put(u,a,v)
 m.write(0x800cda42,struct.pack('<2h',10,10 if case%2 else 25));m.write(0x800cd7d0,struct.pack('<2h',-123,32767));m.write(0x800cd7d8,struct.pack('<h',5))
 for j in range(10):
  m.byteset(S+j*5080,int(j in(0,4,9)));m.write(S+j*5080+8,struct.pack('<4i',10,10,12,12) if j==4 else struct.pack('<4i',30,30,32,32))
 v=machine();v.mem_write(0,bytes(u.mem_read(0,0x200000)));traces=[[],[]];ticks=[0,0]
 def effect(z,a,args,which):
  if a==0x80020238:return (-1,0,2,3,8,9,10,2147483647)[case%8]
  if a==0x80018a5c:put(z,0x800cd9cc,case%4 if ticks[which]==0 else 0);ticks[which]+=1
  if a==0x80062a4c:put(z,0x800cd97c,args[0]);put(z,0x8013796c,args[1] if args[0]==2 else -1)
  if a==0x8003ff00 and case%5==4:put(z,0x800cd9b4,77)
  if a==0x80023438:put(z,0x800cd7e0,7 if case%2 else 0)
  if a==0x80060418 and case%3==2:put(z,0x800cd884,0x60)
  return 0
 def hook(z,a,n,d):
  args=[z.reg_read(reg) for reg in (UC_MIPS_REG_A0,UC_MIPS_REG_A1,UC_MIPS_REG_A2,UC_MIPS_REG_A3)[:CALLS[a]]];traces[0].append([a,args]);z.reg_write(UC_MIPS_REG_V0,effect(z,a,args,0)&0xffffffff);z.reg_write(UC_MIPS_REG_PC,z.reg_read(UC_MIPS_REG_RA))
 for a in CALLS:u.hook_add(UC_HOOK_CODE,hook,begin=a,end=a)
 for a in (0x8005d5a4,0x8005d5ac):u.hook_add(UC_HOOK_CODE,lambda z,a,n,d:z.emu_stop(),begin=a,end=a)
 u.emu_start(0x8005ce34,0x80001000,count=100000)
 def call(a,*args):traces[1].append([a,[x&0xffffffff for x in args]]);return effect(v,a,args,1)
 #65974 isfirstchild atloopentry; kept separately since modelstarts aftercounterreset.
 call(0x80065974);end=iteration(Memory(v),call)
 assert traces[0]==traces[1] and u.reg_read(UC_MIPS_REG_PC)==(0x8005d5ac if end=='exit' else 0x8005d5a4),(view,raw,case,traces,end,hex(u.reg_read(UC_MIPS_REG_PC)))
 hashes=[]
 for a,n in ((0x800cd700,0x380),(S,50800),(0x8013796c,4),(0x801398b4,4)):
  data=m.read(a,n);assert data==Memory(v).read(a,n);hashes.append(hashlib.sha256(data).hexdigest())
 return [view,raw,case,end,traces[0],hashes]
if __name__=='__main__':
 rows=[compare(*a) for a in itertools.product((0,1,2,9),RAWS,range(16))]
 out=dict(total=len(rows),all_passed=True,cases=rows,limits=['Original5CE34..5D5A4/5D5AC wholeloopbody vs independent control; everychild explicitoutcomecontract, no renderer/UI/simulation implementationclaim here','512conditions:4views x8buttonmasks x16tile/input/pause/modal/exit scripts; selectedstoreblock recalculatespointerbeforeoperation,reads CD884 again afterward, refreshes cachedstore evenifselectioncleared','Townclick checks activephysicalstores0..9 in order andinclusive coordinatebounds; no matchingstore leavesviewunchanged. Tile<3 storelookup,3..8 projectdialog,>=9 tileinfo; negative tile belongs<3 branch','First18A5C heldinput CD9CC==0 gates secondframe/update; pausezero required, dirtyCD7E0 copiedto rawsample before13DDC; exitCD9B4 handledbefore repeat; modal masks bothCD884/CD850 withF00C','Controlledchild mutations ofCD884/exit arestressscripts,notobserved actualmenu output. Whole5CD60 entryprologue/notalllivechildren/normalboot/hardware remain'])
 (R/'mainplay-iteration-control-verification.json').write_text(json.dumps(out,separators=(',',':')));print(json.dumps({'total':len(rows),'all_passed':True}))
