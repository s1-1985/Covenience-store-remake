#!/usr/bin/env python3
"""Compare every saved file in a commit with the corresponding local bytes.

Usage: python verify-git-readback.py /path/to/repository COMMIT
Git fetch must already have obtained COMMIT from the remote. Partial clones may
fetch missing blobs during git show. No comparison relies only on API metadata.
"""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

repo = Path(sys.argv[1]).resolve()
ref = sys.argv[2]
root = Path(__file__).resolve().parent
prefix = str(root.relative_to(repo))

def git(*args):
    return subprocess.run(['git', '-C', str(repo), *args], check=True,
                          stdout=subprocess.PIPE).stdout

commit = git('rev-parse', ref + '^{commit}').decode().strip()
paths = git('ls-tree', '-r', '--name-only', commit, '--', prefix).decode().splitlines()
assert paths
rows = []
for path in paths:
    saved = git('show', commit + ':' + path)
    assert saved == (repo / path).read_bytes(), path
    rows.append(dict(path=path, bytes=len(saved), sha256=hashlib.sha256(saved).hexdigest(),
                     full_byte_readback=True))
result = dict(all_passed=True, verified_commit=commit, total=len(rows), files=rows,
              note='Full saved bytes read through Git objects and compared with local bytes. This record does not certify its own later commit.')
(root / 'git-readback-verification.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps(dict(all_passed=True, files_verified=len(rows), commit=commit)))
