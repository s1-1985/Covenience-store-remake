"""Independent source-model ending/flag fixtures; no CPU required."""
import itertools
import json
from pathlib import Path
import sys
sys.path.insert(0,sys.argv[1])
from progression import store_milestone,terminal_guard,menu_limit,presentation_plan
root=Path(__file__).resolve().parents[2]
stores=[]
for n,mode,flags in itertools.product(range(11),(0,1,2,3,255,257),(0,5,255)):
    rows=[dict(active=1,flags=0 if j<n else 0x8000)for j in range(10)]
    if flags==5:
        for row in rows[n:]:row['active']=0
    result=store_milestone(rows,mode,flags,-1)
    stores.append(dict(stores=rows,mode=mode,flags=flags,pending=-1,result=dict(zip(('count','flags','pending','notify'),result))))
terminal=[]
for cash,year,serial in itertools.product((-1,0,0x7fffffff),(-1,98,99),(-1,98,99,32768,65535)):
    mode,pending=terminal_guard(cash,year,serial,2,-1)
    terminal.append(dict(cash=cash,year=year,serial=serial,result=dict(mode=mode,pending=pending)))
data=dict(source='analysis 2c00ba53 / progression.py',stores=stores,terminal=terminal,
          menu=[menu_limit(i)for i in range(256)],presentation=[presentation_plan(i)for i in range(5)])
(root/'game/tests/fixtures/source_progression.json').write_text(json.dumps(data,separators=(',',':'))+'\n')
print('Exported',len(stores),len(terminal),256,5)
