#!/usr/bin/env python3
"""Read every manifest entry from a fetched commit and verify full blob bytes.

Arguments: repository, uploaded-checkpoint-manifest-NN.json.
The manifest contains checksums calculated from the frozen local upload inputs.
"""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

repo, manifest_path = (Path(p).resolve() for p in sys.argv[1:3])
manifest = json.loads(manifest_path.read_text())
rows = []
for item in manifest['files']:
    data = subprocess.run(['git', '-C', str(repo), 'show', manifest['commit'] + ':' + item['path']],
                          stdout=subprocess.PIPE, check=True).stdout
    blob = hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()
    assert len(data) == item['bytes'] and blob == item['git_blob_sha1'], item['path']
    assert hashlib.sha256(data).hexdigest() == item['sha256'], item['path']
    rows.append(dict(**item, full_byte_readback=True))
result = dict(all_passed=True, commit=manifest['commit'], total=len(rows), files=rows,
              limits=['Expected checksums come from frozen pre-upload local bytes.',
                      'Reads fetched Git blob contents; not just GitHub API metadata.',
                      'This verification certifies the named checkpoint, not the later commit that stores the verification itself.'])
output = manifest_path.with_name(manifest_path.name.replace('uploaded-checkpoint-manifest-', 'git-readback-'))
output.write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps(dict(all_passed=True, total=len(rows), commit=manifest['commit'])))
