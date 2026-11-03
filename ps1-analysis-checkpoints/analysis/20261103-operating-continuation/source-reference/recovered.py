"""Recovered formulas from SLPS_007.82. Names grounded by original UI labels.
These are isolated rules, not a full game simulation. Signed inputs are 32-bit.
"""
VISITOR_LIMITS=(50000,100000,200000,400000,500000)
SALES_LIMITS=(100000000,200000000,300000000,400000000,600000000)
POPULATION_LIMITS=(3000,8000,14000,18000,20000)
RATING_LIMITS=(10,30,50,70,90)
RATING_TABLES={
 'price_good':[99,95,90,85,80,70], 'price_bad':[100]*6,
 'service_good':[50,60,70,80,90,100], 'service_bad':[30,40,50,60,70,80],
 'security_good':[70,75,80,85,90,100], 'security_bad':[50,55,60,65,70,80],
 'cleanliness_good':[80,85,90,95,100,100], 'cleanliness_bad':[75,80,85,90,95,100],
 'sales_good':[3000000,5000000,7000000,9000000,10000000,15000000],
 'sales_bad':[500000,1000000,1500000,2000000,2500000,3000000]}
def i32(x):return (x+0x80000000)%0x100000000-0x80000000
def truncdiv(a,b):return (-1 if (a<0)!=(b<0) else 1)*(abs(a)//abs(b))
def score_bands(x,bands):return 4*sum(x>=v for v in bands)
def owner_rating(stores,visitors,population):
 selected=[s for s in stores[:10] if s['active'] and not s['flags']&0x8000]
 if not selected:raise ZeroDivisionError('Original slice divides by selected store count; caller invariants not recovered')
 sales=0;rating=0
 for s in selected:
  v=s['annual_sales'];n=i32(sales+v)
  sales=0x7fffffff if sales>0 and v>0 and n<0 else n
  rating=i32(rating+s['rating'])
 mean=truncdiv(rating,len(selected))
 parts=[2*len(selected),score_bands(visitors&0xffffffff,VISITOR_LIMITS),score_bands(sales,SALES_LIMITS),score_bands(population,POPULATION_LIMITS),score_bands(mean,RATING_LIMITS)]
 raw=sum(parts);return dict(parts=parts,total=100 if raw>=96 else raw,raw=raw,stores=len(selected),annual_sales=sales,mean_rating=mean)
def store_rating_core(rating,price,service,security,cleanliness,sales):
 """Core 0x800282FC..0x80028A98, after possible 0x118C penalty.
 sales is unscaled within-month accumulator +0xD48, read before midnight close.
 price etc are internal metrics, not prices in yen or proven percentages.
 """
 tier=max(0,min(5,truncdiv(rating,20)));good=0;penalties=0;mask=0
 for i,(key,x) in enumerate([('price',price),('service',service),('security',security),('cleanliness',cleanliness),('sales',sales)]):
  g=RATING_TABLES[key+'_good'][tier];d=RATING_TABLES[key+'_bad'][tier]
  passes=x<=g if key=='price' else x>=g
  bad=x>d if key=='price' else x<d
  good+=passes;penalties+=bad
  if not passes:mask|=1<<i
 result=max(5,min(100,rating-penalties+(5 if good>=3 else 0)))
 return dict(tier=tier,good=good,penalties=penalties,failure_mask=mask,rating=result)
def rng_next(seed):
 seed=(seed*1103515245+12345)&0xffffffff
 return seed,(seed>>16)&0x7fff

def ledger_profit(fields):
 """fields = four expense accumulators followed by revenue; no tax inference."""
 return i32(fields[4]-sum(fields[:4]))
def month_close(fields,cash,annual):
 """Monthly adjustment, 0x80029918..0x80029D30; values before adjustment."""
 scaled=[i32(v*8) for v in fields]
 cash=i32(cash+7*ledger_profit(fields))
 annual=[i32(a+b) for a,b in zip(annual,scaled)]
 return dict(cash=cash,previous_month=scaled,current_month=[0]*5,annual=annual)


def purchase_price(base,factor,setting):
 """Customer path stores computed price as signed 16-bit, 0x8003473C..34800."""
 value=truncdiv(i32(base*i32(factor+setting)),100)
 return (value+32768)%65536-32768

def purchase_gate(wallet,price,seed,threshold):
 """Conditional on reaching 0x80034920; earlier product-specific gates excluded."""
 if wallet<price:return 'insufficient_money',seed
 seed,value=rng_next(seed)
 return ('try_inventory' if value%100+1<=threshold else 'wait'),seed

def theft_security_gate(mode,security,customer_trait):
 """Only underfunded branch; stock removal must still succeed."""
 return mode==0 and security<100-customer_trait

def stock_display_level(remaining,capacity):
 """Level index used for three consecutive shelf graphics."""
 third=truncdiv(capacity,3)
 return 2 if remaining<=third else (1 if remaining<=2*third else 0)
