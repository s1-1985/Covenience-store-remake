"""Export exactly the staged tree for a verified GitHub checkpoint.

This helper does not contact GitHub or claim a push succeeded. The caller
uploads each blob, checks its returned SHA, creates a tree, and compares that
tree SHA with expected_tree before moving the branch with an expected-head
lease. Use staged bytes rather than possibly newer working-copy bytes.
Keep the output in scratch; never commit the payload itself.
"""
import argparse, base64, json, subprocess
from pathlib import Path

def git(*args):
    return subprocess.check_output(['git',*args])

def main():
    p=argparse.ArgumentParser();p.add_argument('output',type=Path);args=p.parse_args()
    git('diff','--cached','--check')
    paths=git('diff','--cached','--name-only','-z').decode().strip('\0').split('\0')
    files=[]
    for path in filter(None,paths):
        entry=git('ls-files','--stage','--',path).decode()
        if not entry:
            files.append(dict(path=path,sha=None,mode='100644',type='blob'));continue
        mode,sha,stage=entry.split('\t')[0].split()
        assert stage=='0' and mode in ('100644','100755'),('unmerged or unsupported mode',path,entry)
        blob=git('show',':'+path)
        files.append(dict(path=path,sha=sha,mode=mode,type='blob',encoding='base64',content=base64.b64encode(blob).decode()))
    payload=dict(base_commit=git('rev-parse','HEAD').decode().strip(),base_tree=git('rev-parse','HEAD^{tree}').decode().strip(),expected_tree=git('write-tree').decode().strip(),files=files)
    args.output.write_text(json.dumps(payload,separators=(',',':')))
    print(json.dumps(dict(files=len(files),bytes=args.output.stat().st_size,expected_tree=payload['expected_tree'])))

if __name__=='__main__':main()
