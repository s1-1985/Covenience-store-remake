"""Read the archived operating_costs.py model; no CPU/disc analysis."""
import hashlib,importlib.util,json,pathlib,struct,sys
p=pathlib.Path(sys.argv[1]);sys.path.insert(0,str(p.parent));spec=importlib.util.spec_from_file_location('old_costs',p);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
rows=[]
for hours in [0,8,24]:
 for wages in [[500,600,700],[2147483647,1,1],[536870912,536870912,536870912],[-2147483648,-1,100]]:
  store=bytearray(5080);struct.pack_into('<3h',store,0xdd8,0,1,2)
  staff=[]
  for v in wages:
   person=bytearray(40);struct.pack_into('<i',person,12,v);staff.append(person)
  schedules=[[1]*hours+[0]*(24-hours)]
  costs=[m.staff_cost(store,person,i,0,schedules) for i,person in enumerate(staff)]
  rows.append({'hours':hours,'wages':wages,'per_staff':costs,'total':m.staff_total(store,staff,0,schedules)})
equipment=[]
for hours in [0,8,24]:
 for rates in [[100,200],[2147483647,1],[536870912,536870912]]:
  store=bytearray(5080);struct.pack_into('<ii',store,0x44,3,1)
  for i,kind in enumerate([0,1,53]):struct.pack_into('<I',store,0x108+i*4,0x80000000 | kind<<12)
  schedules=[[1]*hours+[0]*(24-hours)];full=rates+[0]*51
  equipment.append({'hours':hours,'rates':rates,'kinds':[0,1,53],'total':m.equipment_cost(store,0,schedules,full)})
x={'kind':'previously recovered Python model, not new original CPU execution','archive_commit':'a1f45981ffc1479e9a8e0b4ff429d4fc4cb85ea4','source_file':'ps1-analysis-checkpoints/analysis/20261103-operating-continuation/source-reference/operating_costs.py','source_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'staff':rows,'equipment':equipment}
pathlib.Path(sys.argv[2]).write_text(json.dumps(x,indent=2)+'\n');print(len(rows)+len(equipment),'model-derived cases')
