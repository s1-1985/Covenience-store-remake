"""Full original item-acquisition/refill calls, plus completion-flag excerpt.
Usage: python probe_stock.py EXE OUT.json. Unicorn research dependency only.
"""
from pathlib import Path
import hashlib,json,struct,sys
from unicorn import Uc,UC_ARCH_MIPS,UC_MODE_MIPS32,UC_MODE_LITTLE_ENDIAN
from unicorn.mips_const import UC_MIPS_REG_SP,UC_MIPS_REG_FP,UC_MIPS_REG_RA,UC_MIPS_REG_PC,UC_MIPS_REG_A0,UC_MIPS_REG_A1,UC_MIPS_REG_V0
exe=Path(sys.argv[1]).read_bytes();sha=hashlib.sha256(exe).hexdigest();assert sha=='d6a167a1c9e0fe98d7e44e12968caa489ac3eb7ed3b9e46012a188af8432b1fd'
repo=Path(__file__).resolve().parents[3];data=json.loads((repo/'game/data/ps1_integration.json').read_text())
f=next(f for f in data['layouts'][1]['fixtures'] if f['source_kind']==0)
category=data['product_ids'].index('retort_food');STORE=0x12b2f8;PERSON=0x160000;STOP=0x80001000
anchor=STORE+0x108+2*112+2*4;stock_address=anchor+112
# Synthetic stock uses the EXE's pre-texture-binding image ID. Disc-layout
# image IDs are already rebound and cannot be mixed with the untouched master.
image=struct.unpack_from('<i',exe,0x8009cdf0-0x80010000+2048+category*88+44)[0]

def put(u,a,fmt,*v):u.mem_write(a,struct.pack(fmt,*v))
def get(u,a,fmt):return struct.unpack(fmt,u.mem_read(a,struct.calcsize(fmt)))[0]
def machine(stock,counter=0):
 u=Uc(UC_ARCH_MIPS,UC_MODE_MIPS32|UC_MODE_LITTLE_ENDIAN);u.mem_map(0,0x200000);u.mem_write(0x10000,exe[2048:])
 for r,v in [(UC_MIPS_REG_SP,0x801f0000),(UC_MIPS_REG_FP,0x801f0000),(UC_MIPS_REG_RA,STOP)]:u.reg_write(r,v)
 put(u,STORE+4,'<H',1);put(u,STORE+68,'<ii',20,20)
 put(u,anchor,'<I',f['source_word']);put(u,stock_address,'<I',(f['source_stock_word']&0xc00fff)|(image<<12)|(stock<<24))
 put(u,STORE+0x12e2,'<b',counter);put(u,0xcd9f8,'<i',10000000);put(u,0xd6270,'<I',12345)
 return u

def acquire(stock,heads,counter,mismatch=False):
 u=machine(stock,counter);p=bytearray(32);p[1]=category+1 if mismatch else category;p[12:15]=bytes([2,3,0]);p[30]=heads;u.mem_write(PERSON,bytes(p))
 u.reg_write(UC_MIPS_REG_A0,STORE|0x80000000);u.reg_write(UC_MIPS_REG_A1,PERSON|0x80000000)
 u.emu_start(0x8003b420,STOP,count=100000);assert u.reg_read(UC_MIPS_REG_PC)==STOP
 result=dict(stock=stock,heads=heads,counter=counter,mismatch=mismatch,failed=bool(u.reg_read(UC_MIPS_REG_V0)),stock_after=(get(u,stock_address,'<I')>>24)&127,counter_after=get(u,STORE+0x12e2,'<b'))
 assert result['failed']==(mismatch or stock<heads),result
 assert result['stock_after']==(stock if result['failed'] else stock-heads),result
 assert result['counter_after']==(min(127,counter+1) if result['failed'] else counter),result
 assert get(u,0xcd9f8,'<i')==10000000 and get(u,0xd6270,'<I')==12345
 return result
acquisitions=[acquire(s,h,c) for s in [0,1,2,3,5,40] for h in [1,3,5] for c in [0,126,127]]
acquisitions.append(acquire(40,3,126,True))

def refill(stock,ability,seed):
 u=machine(stock);put(u,0xd6270,'<I',seed);p=bytearray(60);p[31]=ability;p[41:44]=bytes([2,3,0]);u.mem_write(PERSON,bytes(p))
 u.reg_write(UC_MIPS_REG_A0,STORE|0x80000000);u.reg_write(UC_MIPS_REG_A1,PERSON|0x80000000)
 u.emu_start(0x8003b278,STOP,count=100000);assert u.reg_read(UC_MIPS_REG_PC)==STOP
 result=dict(stock=stock,ability=ability,seed=seed,status=u.reg_read(UC_MIPS_REG_V0),stock_after=(get(u,stock_address,'<I')>>24)&127,cash_after=get(u,0xcd9f8,'<i'),cost=get(u,STORE+0xd94,'<i'),seed_after=get(u,0xd6270,'<I'))
 next_seed=(seed*1103515245+12345)&0xffffffff;roll=((next_seed>>16)&32767)%100+1
 amount=min(40-stock,ability//10+1) if roll<=ability else 0
 assert result['stock_after']==stock+amount and result['cost']==amount*360,result
 assert result['cash_after']==10000000-amount*360 and result['seed_after']==next_seed,result
 assert result['status']==(0 if roll<=ability and stock+amount==40 else 1),result
 return result
refills=[refill(stock,ability,seed) for stock in [0,26,37,39,40] for ability in [0,25,100] for seed in [0,1]]
flags=[]
for status in [0,1,2]:
 u=machine(40);put(u,0xcd790,'<H',0);u.reg_write(UC_MIPS_REG_V0,status)
 stop=0x80037528 if status==0 else (0x80037560 if status==1 else 0x8003753c)
 u.emu_start(0x800374ec,stop,count=1000)
 flag=get(u,0xcd790,'<H');assert flag==(2048 if status==0 else 0)
 flags.append(dict(status=status,flag=flag))
# Original bit11 dispatch entry is VOS24.
tones=list(struct.unpack_from('<16i',exe,0x8009947c-0x80010000+2048));assert tones[11]==24
Path(sys.argv[2]).write_text(json.dumps(dict(exe_sha256=sha,category='retort_food',capacity=40,unit_cost=360,acquisitions=acquisitions,refills=refills,completion_flags=flags,completion_sound=tones[11],original_calls=len(acquisitions)+len(refills)+len(flags),callee_replacements=0,scope='Full original acquisition and refill calls with real inventory/payment/RNG; parent flag excerpt stops before growth; no full operating loop'),separators=(',',':'))+'\n')
print('STOCK_SOURCE_PASS',len(acquisitions),'acquisitions,',len(refills),'refills, 3 completion excerpts')
