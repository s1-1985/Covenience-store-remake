"""Native save/load after source-created single-conversion UI changes."""
from verify_title_native_load_20261029 import compare,R,json
from operation_runtime import IMAGES
import sys,zlib,struct,hashlib
source=sys.argv[1] if len(sys.argv)>1 else 'TOWN0001-price-lower_limit-single'
b=zlib.decompress((R/'source/opened-snapshots-20261028'/(source+'.ram.zlib')).read_bytes())
assert all(struct.unpack_from('<12i',b,0x9ce14+j*88)==tuple(v) for j,v in enumerate(IMAGES))
row=compare('success',source,audit_runtime_tables=True);row['snapshot_sha256']=hashlib.sha256(b).hexdigest()
row['runtime_table_provenance']='single_conversion'
out=dict(total=1,all_passed=True,frames_verified=len(row['frames']),cases=[row],limits=row['limits'])
(R/f'title-native-load-roundtrip-{source}-verification-20261030.json').write_text(json.dumps(out,separators=(',',':')))
print('single-conversion source save/load passed',source,len(row['frames']),flush=True)
