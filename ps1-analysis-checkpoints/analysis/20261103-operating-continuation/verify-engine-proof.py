#!/usr/bin/env python3
"""Verify that the already completed engine comparison still references exact proofs."""
from pathlib import Path
import hashlib,json
root=Path(__file__).resolve().parent
p=root/"mips-engine-crosscheck.json"
out=json.loads(p.read_text())
assert out["all_passed"] and out["total_cases"]==33 and len(out["cases"])==33
assert out["unicorn_version"]=="2.1.4"
assert out["source_exe_sha256"]=="d6a167a1c9e0fe98d7e44e12968caa489ac3eb7ed3b9e46012a188af8432b1fd"
for case in out["cases"]:
    proof=root.parent/case["existing_model_proof"]
    assert hashlib.sha256(proof.read_bytes()).hexdigest()==case["existing_proof_sha256"]
    assert case["passed"] and case["full_ram_bytes_compared"]==2097152
    assert case["gpr_registers_compared"]==32 and case["hi_lo_compared"]
print("Existing 33/33 two-engine comparisons retained; every referenced model proof matches its SHA256")
