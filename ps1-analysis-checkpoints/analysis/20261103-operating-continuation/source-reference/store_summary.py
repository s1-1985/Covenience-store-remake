# Legacy identifiers security/security_norm in this module refer to store summary +0C/+0A4 SERVICE, not +08 security. See RARE-STORE-EVENT.md.
from staff_work import scan_store

def truncdiv(a,b):return (abs(a)//abs(b))*(-1 if (a<0)!=(b<0) else 1)
def store_summaries(stores,fixtures,images,costs):
 count=total=capacity=0;out=[]
 for store in stores:
  if not store['active']:out.append(None);continue
  skills=store['skills'];security=truncdiv(sum(skills),len(skills)) if skills else 0
  coords,stock,(count,total,capacity,security)=scan_store(store['width'],store['height'],store['words'],fixtures,images,costs,store['prices'],store['prior'],(count,total,capacity,security))
  if count>0:total=truncdiv(total,count)
  out.append(dict(coords=coords,stock=stock,price=total,capacity=capacity,security=min(security,100)))
 active=[o for o in out if o]
 if active:
  pmin=min(10000,min(o['price'] for o in active));pmax=max(-10000,max(o['price'] for o in active));smin=min(10000,min(o['security'] for o in active));smax=max(-10000,max(o['security'] for o in active))
  for o in active:
   o['price_norm']=100 if pmin==pmax else 100-truncdiv((o['price']-pmin)*100,pmax-pmin)
   o['security_norm']=100 if smin==smax else truncdiv((o['security']-smin)*100,smax-smin)
 return out
