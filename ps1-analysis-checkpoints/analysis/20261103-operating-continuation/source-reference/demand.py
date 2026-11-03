from recovered import rng_next,truncdiv,i32
from extended import seasonal_gate

def select_store(profile,x,y,stores,order,schedules,ranges,seed,low=0,high=110):
 stores=[dict(s) for s in stores];candidates=[]
 for k in order:
  if k==-1:break
  s=stores[k];seed,r=rng_next(seed)
  if r%100+1>s['rating']+20:continue
  if schedules[s['schedule']][profile[2]]==0:continue
  if profile[12]==3 and s['capacity']<=0:continue
  stock=s['stock'][profile[8]]
  if stock<=0:continue
  x0,y0,x1,y1=s['rect'];dist=max(x0-x,x-x1)+max(y0-y,y-y1);s['distance']=dist
  if dist>ranges[profile[12]]:continue
  candidates.append((k,stock,s['rating']))
 if not candidates:return -1,stores,seed
 ranked=[]
 for k,stock,rating in candidates:
  s=stores[k];s['distance']=0 if high==low else 100-truncdiv(i32((s['distance']-low)*100),high-low)
  score=i32(s['price']*profile[14]+s['distance']*profile[15]+s['security']*profile[16]);ranked.append((score,stock,rating,k))
 # Strict greater on each key: complete ties keep first candidate in list order.
 best=max(range(len(ranked)),key=lambda j:ranked[j][:3])
 return ranked[best][3],stores,seed

def weather_value(month,thresholds,seed):
 seed,r=rng_next(seed);roll=r%100+1;row=thresholds[month-1]
 if roll<=row[0]:return 0,seed
 seed,r=rng_next(seed)
 if roll<=row[1]:return r%19+1,seed
 if roll<=row[2]:return r%20+20,seed
 if roll<=row[3]:return r%20+40,seed
 return r%20+60,seed

def replenish_demand(town,groups,profiles,stores,order,schedules,ranges,month,stage,bypass,thresholds,calendar,seasons,seed):
 weather,seed=weather_value(month,thresholds,seed);table=calendar[month*4+stage-1];demand=[[0]*144 for _ in range(10)]
 for y,row in enumerate(town):
  for x,group in enumerate(row):
   if group==-1:continue
   for pid,qty in groups[group]:
    if pid==-1:continue
    p=profiles[pid]
    if not bypass:
     if p[13]+20<weather:continue
     product=p[8];ret,seed=seasonal_gate(product,seasons[product] if 0<=product<27 else 0,month,seed)
     if ret==2:continue
     seed,r=rng_next(seed)
     if r%100+1>p[21+table]:continue
    dest,stores,seed=select_store(p,x,y,stores,order,schedules,ranges,seed)
    if dest!=-1:demand[dest][pid]=(demand[dest][pid]+qty)&65535
 totals=[sum(v if v<32768 else v-65536 for v in row) if s['active'] else s['old_total'] for s,row in zip(stores,demand)]
 return demand,totals,weather,stores,seed
