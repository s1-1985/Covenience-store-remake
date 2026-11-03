#!/usr/bin/env python3
"""Independently reconcile continuation cash writes, ledgers and checkpoint ancestry."""
from pathlib import Path
import collections,hashlib,json,struct,sys,zipfile,zlib

def i32(n):return (n+0x80000000)%0x100000000-0x80000000
def sha(b):return hashlib.sha256(b).hexdigest()
def main():
    root=Path(__file__).resolve().parent
    saved={}
    for p in sorted((root/"runs").glob("*/generated/source/opened-snapshots-20261028/*")):
        if p.name in saved:assert p.read_bytes()==saved[p.name]
        saved[p.name]=p.read_bytes()
    with zipfile.ZipFile(sys.argv[1]) as archive:
        def snapshot(name):
            prefix="algorithm-analysis/source/opened-snapshots-20261028/"
            a=name+".json";b=name+".ram.zlib"
            meta=json.loads(saved[a] if a in saved else archive.read(prefix+a))
            ram=zlib.decompress(saved[b] if b in saved else archive.read(prefix+b))
            assert sha(ram)==meta["ram_sha256"]
            return meta,ram
        rows=[]
        for p in sorted((root/"runs").glob("*/generated/opened-snapshot-TOWN0001-ci-*-verification-20261103.json")):
            proof=json.loads(p.read_text());assert proof["all_passed"]
            c=proof["cases"][0];name=p.name[len("opened-snapshot-"):-len("-verification-20261103.json")]
            im,before=snapshot(c["snapshot"]);fm,after=snapshot(name)
            assert c["snapshot_sha256"]==im["ram_sha256"]==fm["parent_snapshot_sha256"]
            count=proof["iterations_verified"]
            assert fm["completed_iterations"]==im["completed_iterations"]+count
            assert len(c["steps"])==count
            assert c["steps"][-1]["clock"]==c["opening_clock"]+2*count
            assert c["runtime_table_provenance"]=="single_conversion" and c["single_conversion_appearance_verified"]
            cash=list(struct.unpack_from("<2i",before,0xcd9f8));opening_cash=cash[:]
            writes=0;pcs=collections.defaultdict(lambda:[0,0])
            for r in c["accounting_write_trace"]:
                address=int(r["address"],16)
                if address not in (0xcd9f8,0xcd9fc):continue
                side=(address-0xcd9f8)//4
                assert r["size"]==4 and i32(r["before"])==cash[side]
                pcs[r["pc"]][side]+=i32(r["after"]-r["before"]);cash[side]=i32(r["after"]);writes+=1
            final_cash=list(struct.unpack_from("<2i",after,0xcd9f8));assert cash==final_cash
            closes=c["midnight_finance_checks"];assert len(closes)<=1
            ledger_cash=opening_cash[:];stores=[]
            for slot in range(10):
                off=0x12b2f8+slot*5080
                assert before[off]==after[off] and before[off+4:off+6]==after[off+4:off+6]
                if not before[off]:continue
                side=struct.unpack_from("<H",before,off+4)[0]>>15
                initial=list(struct.unpack_from("<5i",before,off+0xd88))
                current=list(struct.unpack_from("<5i",after,off+0xd88))
                closed=list(struct.unpack_from("<5i",after,off+0xd9c)) if closes else [0]*5
                sales=closed[4]+current[4]-initial[4];goods=closed[3]+current[3]-initial[3]
                expense=sum(closed[:3]);delta=sales-goods-expense
                ledger_cash[side]=i32(ledger_cash[side]+delta)
                stores.append(dict(slot=slot,company=side,opening_ledger=initial,current_ledger=current,closed_ledger=closed,
                                   additional_sales=sales,additional_goods=goods,expense=expense,cash_delta=delta))
            assert ledger_cash==cash,("cash ledger mismatch",name,ledger_cash,cash)
            staff=c.get("whole_staff_loop_checks",[]);effects=collections.Counter();coverage=collections.Counter()
            for r in staff:effects.update(r["effects"]);coverage[str(r["store_slot"])]+=1
            assert len(staff)==count*len(stores)
            customers=c.get("customer_loop_checks",[])
            rows.append(dict(snapshot=name,source=c["snapshot"],source_ram_sha256=im["ram_sha256"],final_ram_sha256=fm["ram_sha256"],
                             proof=str(p.relative_to(root)),proof_sha256=sha(p.read_bytes()),updates=count,
                             clock_before=c["opening_clock"],clock_after=c["steps"][-1]["clock"],
                             cash_before=opening_cash,cash_after=cash,cash_from_ledgers=ledger_cash,cash_write_count=writes,cash_delta_by_pc=dict(pcs),
                             stores=stores,midnight_count=len(closes),whole_staff_checks=len(staff),staff_calls_by_store=dict(coverage),staff_effects=dict(effects),
                             customer_checks=len(customers),restock_checks=len(c.get("restock_checks",[])),stock_postings=len(c.get("stock_posting_checks",[])),
                             single_conversion=True,appearance_verified=True))
    assert rows
    out=dict(all_passed=True,total_segments=len(rows),total_updates=sum(r["updates"] for r in rows),
             whole_staff_checks=sum(r["whole_staff_checks"] for r in rows),cases=rows,
             limits=["No new game cases: this is a second reconstruction of already recorded native trajectories.",
                     "Ledger reconciliation requires stable active stores/owners and at most one daily close per segment; those preconditions are asserted.",
                     "Cash writes and store ledgers are reconstructed separately, then compared with both companies' saved RAM.",
                     "Shared native children and modeled hardware boundaries remain as documented in each underlying proof."])
    (root/"cash-lineage-audit.json").write_text(json.dumps(out,ensure_ascii=False,indent=2)+"\n")
    print(json.dumps(dict(all_passed=True,segments=len(rows),updates=out["total_updates"],staff_checks=out["whole_staff_checks"])),flush=True)
if __name__=="__main__":main()
