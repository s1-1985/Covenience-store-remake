"""8002BD54 orchestration; notifications emitted as event requests, text rendering external."""
from town_growth import *
from town_mutation import *

def population(town,category,groups):
 total=0
 for k in range(3000):
  group=struct.unpack_from('<h',town,k*8+6)[0]
  if group==-1 or (category and s8(town[k*8+4])!=category):continue
  for pid,n in groups[group]:
   if pid!=-1:total=i32(total+((n+32768)%65536-32768))
 return total

def monthly(town,table,groups,stores,order,state,notify_text=None):
 state=dict(state);state['history']=state['history'].copy();seed=state['seed'];events=[];actions=[]
 if state['subhour']!=0 or state['hour']!=0 or state['stage']!=1:return state,events,actions
 def draw():
  nonlocal seed
  seed,r=rng_next(seed);return r
 def choose(c):
  nonlocal seed
  kind,seed=choose_kind(c,table,seed);return kind
 def build(x,y,kind):
  nonlocal seed
  seed=place(town,x,y,kind,0,table,seed);actions.append(('build',x,y,kind))
 def remove(x,y):
  nonlocal seed
  seed=demolish(town,x,y,0,table,seed);actions.append(('remove',x,y))
 def notify(kind):
  if notify_text is not None:notify_text(kind,state['tier'])
  event_id=struct.unpack_from('<h',bytes.fromhex(table[kind]['raw_hex']),52)[0]
  events.append((2,event_id,30,1,0))
 def scan():
  x0,y0=draw()%60,draw()%50
  for dy in range(50):
   for dx in range(60):yield (x0+dx)%60,(y0+dy)%50
 def level(x,y):return s8(town[(y*60+x)*8+2])
 def pop(c):return population(town,c,groups)
 grid=[base_influence([stores[i]['value'] for i in order],pop(3),state['reference'])]*3000
 categories=[s8(town[k*8+4]) for k in range(3000)]
 administrative=(-1,-1);station_count=0;maximum=11
 for y in range(50):
  for x in range(60):
   k=y*60+x
   if administrative==(-1,-1) and categories[k]==9:administrative=(x,y)
   if level(x,y)>maximum and feasibility(town,x,y,20,table)==0 and nearby(town,x,y,20,40,table)==0:maximum=level(x,y)
   tid=tile(town,x,y)
   if tid in (table[20]['lower'],table[21]['lower']):station_count+=1;grid=square_influence(grid,x,y)
   if table[14]['lower']<=tid<=table[16]['upper']:grid=asymmetric_influence(grid,categories,x,y)
 maximum-=1
 grid,seed=store_influence(grid,[stores[i] for i in order],state['divisor'],seed)
 for y in range(50):
  for x in range(60):
   k=y*60+x;lv,seed=change_level(level(x,y),grid[k],seed);town[k*8+2]=lv&255
   if lv<4 and draw()%100+1<3:
    if table[building_kind(tile(town,x,y),table)]['category']==3:remove(x,y)
   lv=level(x,y)
   if lv>=8 and draw()%100+1<3:
    kind=43+draw()%(6 if lv<15 else 7)
    if feasibility(town,x,y,kind,table)==0:build(x,y,kind)
 residential=pop(3)
 for category,target in ((4,residential),(5,truncdiv(residential,4))):
  difference=i32(target-pop(category))
  for x,y in scan():
   lv=level(x,y)
   if difference<0 and lv<3 and table[building_kind(tile(town,x,y),table)]['category']==category:remove(x,y);break
   if difference>0 and lv>=9:
    kind=choose(category)
    if feasibility(town,x,y,kind,table)==0:build(x,y,kind);break
 p=pop(0)
 if p>=5000:
  radius=30 if p>=20000 else 50 if p>=8000 else 100
  kind=choose(6+draw()%3 if p>=8000 else 8)
  for x,y in scan():
   if level(x,y)>=5 and feasibility(town,x,y,kind,table)==0 and nearby(town,x,y,kind,radius,table)==0:build(x,y,kind);notify(kind);break
 p=pop(0);tier=4 if p>=20000 else 3 if p>=16000 else 2 if p>=8000 else 1 if p>=5000 else 0
 if station_count<tier:
  for x,y in scan():
   if level(x,y)>=maximum and feasibility(town,x,y,20,table)==0 and nearby(town,x,y,20,40,table)==0:build(x,y,20);notify(20);break
 if state['tier']<tier:
  state['tier']=tier
  if tier>0:
   kind=22 if tier==1 else 23 if tier<4 else 24
   build(*administrative,kind)
   if state['mode']==0 and kind==24:state['progress_flags']|=1;state['progress_counter']=0
   else:notify(kind)
 state['history']=[pop(0)]+state['history'][:59]
 if state['month'] in (6,12):
  if notify_text is not None:notify_text(None,state['month'])
  events.append((0,0,100,1,0))
 rebuild_flags(town,stores);state['dirty']=0;state['seed']=seed
 return state,events,actions
