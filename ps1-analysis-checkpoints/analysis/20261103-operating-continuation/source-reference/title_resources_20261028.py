"""Add original title background mode5 to the existing source-sector CD adapter."""
from newgame_resource_bridge import *
row=json.loads((R/'title-sector-asset-20261028.json').read_text())
blob=(R/row['source_file']).read_bytes();sector=blob+base64.b64decode(row['padding_base64'])
assert digest(blob)==row['sha256'] and digest(sector)==row['sector_sha256']
ASSETS[0,5]={**row,'blob':blob,'sector':sector,'descriptor':encode(row['lba'])+b'\0'+struct.pack('<I',len(blob))+b'KABEE.BGD'.ljust(16,b'\0')}
DESTINATIONS[5]=0x801ed600;POINTERS[5]=0x800cd894
for row in json.loads((R/'scenario-sector-assets-20261031.json').read_text())['assets']:
 blob=(R/row['source_file']).read_bytes();sector=blob+base64.b64decode(row['padding_base64'])
 assert digest(blob)==row['sha256'] and digest(sector)==row['sector_sha256']
 ASSETS[row['index'],row['mode']]={**row,'blob':blob,'sector':sector,'descriptor':encode(row['lba'])+b'\0'+struct.pack('<I',len(blob))+row['path'].split('\\')[-1].split(';')[0].encode().ljust(16,b'\0')}

