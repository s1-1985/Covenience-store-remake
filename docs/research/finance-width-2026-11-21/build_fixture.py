"""Generate compact expected values from the PREVIOUSLY recovered Python model.
No disc/EXE/emulator access. Pass recovered.py from the archived 20261103 source.
"""
import hashlib, importlib.util, json, pathlib, sys
path=pathlib.Path(sys.argv[1]);spec=importlib.util.spec_from_file_location('original_finance',path)
model=importlib.util.module_from_spec(spec);spec.loader.exec_module(model)
fields=['maintenance_yen','wages_yen','promotion_yen','goods_yen','sales_yen']
inputs=[([100,200,300,400,2000],200000000),([0,0,0,0,0],2147483647),([0,0,0,0,1],2147483647),([0,0,0,0,-1],-2147483648),([0,0,0,0,268435456],1000),([0,0,0,0,400000000],1000),([2147483647,2147483647,0,0,0],0),([-2147483648,0,0,0,2147483647],-1),([1,-1,2147483647,-2147483648,2147483647],2147483647)]
for i in range(5):
 for value in [2147483647,-2147483648,536870912]:
  row=[0]*5;row[i]=value;inputs.append((row,200000000))
rows=[]
for values,cash in inputs:
 closed=model.month_close(values,cash,[0]*5);profit=model.ledger_profit(values)
 rows.append({'representative':dict(zip(fields,values)),'cash_before':cash,'monthly':dict(zip(fields,closed['previous_month'])),'profit':profit,'monthly_profit':model.ledger_profit(closed['previous_month']),'adjustment':model.i32(7*profit),'cash_after':closed['cash']})
out={'kind':'existing recovered-model expectations; not new original CPU execution','source_file':'ps1-analysis-checkpoints/analysis/20261103-operating-continuation/source-reference/recovered.py','archive_commit':'a1f45981ffc1479e9a8e0b4ff429d4fc4cb85ea4','source_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'original_ranges':['8001CCC0','80029918..80029D30'],'rows':rows}
pathlib.Path(sys.argv[2]).write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
print(len(rows),'model-derived cases')
