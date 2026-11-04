#!/usr/bin/env python3
"""Bind an uploaded MODE2/2352 disc to archived executable/resource evidence.

Usage: python verify-disc.py disc.bin disc.cue restored/algorithm-analysis
Outputs only hashes/metadata, never modifies the disc or archived sources.
"""
import base64
import hashlib
import json
import struct
import sys
from pathlib import Path


def digest(data):
    return hashlib.sha256(data).hexdigest()


def verify(bin_path, cue_path, algo):
    disc = bin_path.read_bytes()
    assert len(disc) % 2352 == 0
    count = len(disc) // 2352
    anomalies = []
    for lba in range(count):
        raw = disc[lba * 2352:(lba + 1) * 2352]
        if raw[:12] != b'\x00' + b'\xff' * 10 + b'\x00':
            anomalies.append([lba, 'sync'])
        if raw[15] != 2:
            anomalies.append([lba, 'mode'])
        if raw[16:20] != raw[20:24]:
            anomalies.append([lba, 'subheader'])

    def sector(lba):
        assert 0 <= lba < count
        raw = disc[lba * 2352:(lba + 1) * 2352]
        assert raw[15] == 2
        # ISO directory extents are Form 1 data. XA Form 2 audio is inventoried
        # below by its ISO allocation; it is not decoded as 2048-byte PCM.
        return raw[24:24 + 2048]

    def extent(lba, size):
        return b''.join(sector(i) for i in range(lba, lba + (size + 2047) // 2048))[:size]

    def both32(data, off):
        a = struct.unpack_from('<I', data, off)[0]
        assert a == struct.unpack_from('>I', data, off + 4)[0]
        return a

    def record(data):
        assert len(data) == data[0]
        return dict(lba=both32(data, 2), bytes=both32(data, 10),
                    flags=data[25], name=data[33:33 + data[32]])

    pvd = sector(16)
    assert pvd[:7] == b'\x01CD001\x01'
    block_size = struct.unpack_from('<H', pvd, 128)[0]
    assert block_size == struct.unpack_from('>H', pvd, 130)[0] == 2048
    root = record(pvd[156:156 + pvd[156]])
    files, visited = [], set()

    def directory(node, prefix=''):
        key = node['lba'], node['bytes']
        assert key not in visited
        visited.add(key)
        data = extent(*key)
        off = 0
        while off < len(data):
            length = data[off]
            if not length:
                off = (off // 2048 + 1) * 2048
                continue
            assert (off % 2048) + length <= 2048
            row = record(data[off:off + length])
            off += length
            if row['name'] in (b'\0', b'\1'):
                continue
            assert not row['flags'] & 0x80, 'multi-extent file requires separate handling'
            name = row.pop('name').decode('ascii')
            path = prefix + '/' + name
            if row['flags'] & 2:
                directory(row, path)
            else:
                size = row['bytes']
                n = (size + 2047) // 2048
                assert row['lba'] + n <= count
                forms = sorted({2 if disc[i * 2352 + 18] & 0x20 else 1
                                for i in range(row['lba'], row['lba'] + n)})
                content = extent(row['lba'], size)
                files.append(dict(path=path, **row, sector_forms=forms,
                                  iso_2048_projection_sha256=digest(content)))

    directory(root)
    by_path = {row['path'].upper(): row for row in files}
    assert len(by_path) == len(files)
    source_matches = []
    for row in files:
        # Require a unique disc basename before matching old flattened sources.
        basename = row['path'].rsplit('/', 1)[-1].split(';')[0]
        if sum(r['path'].rsplit('/', 1)[-1].split(';')[0] == basename for r in files) != 1:
            continue
        old = algo / 'source' / basename
        if old.is_file():
            assert row['sector_forms'] == [1], ('non-Form1 source', row['path'])
            content = extent(row['lba'], row['bytes'])
            archived = old.read_bytes()
            assert content == archived, ('archived source mismatch', row['path'])
            source_matches.append(dict(path=row['path'], archived_path='source/' + basename,
                                       bytes=len(content), sha256=digest(content)))
    assets = []
    manifests = ['newgame-sector-assets-20261016.json', 'title-sector-asset-20261028.json',
                 'scenario-sector-assets-20261031.json']
    for filename in manifests:
        source = json.loads((algo / filename).read_text())
        rows = source['assets'] if 'assets' in source else [source]
        for old in rows:
            path = '/' + old['path'].replace('\\', '/').lstrip('/') if 'path' in old else '/KABEE.BGD;1'
            row = by_path.get(path.upper())
            if row is None:
                candidates = [r for r in files if r['lba'] == old['lba'] and r['bytes'] == old['bytes']]
                assert len(candidates) == 1, (filename, path)
                row = candidates[0]
            assert row['lba'] == old['lba'] and row['bytes'] == old['bytes']
            content = extent(row['lba'], row['bytes'])
            assert digest(content) == old['sha256']
            assert content == (algo / old['source_file']).read_bytes()
            padded = extent(row['lba'], old['sector_bytes'])
            assert digest(padded) == old['sector_sha256']
            assert padded == content + base64.b64decode(old['padding_base64'])
            assets.append(dict(manifest=filename, path=row['path'], lba=row['lba'],
                               bytes=row['bytes'], sha256=old['sha256'],
                               sector_sha256=old['sector_sha256']))
    exe = next(r for r in source_matches if r['path'] == '/SLPS_007.82;1')
    assert exe['sha256'] == 'd6a167a1c9e0fe98d7e44e12968caa489ac3eb7ed3b9e46012a188af8432b1fd'
    cue = cue_path.read_text()
    assert 'TRACK 01 MODE2/2352' in cue and 'INDEX 01 00:00:00' in cue
    assert not anomalies, anomalies[:10]
    return dict(all_passed=True, disc=dict(filename=bin_path.name, bytes=len(disc),
                 sha256=digest(disc), sectors=count, volume_id=pvd[40:72].decode('ascii').strip(),
                 iso_volume_sectors=both32(pvd, 80), sector_header_anomalies=anomalies),
                cue=dict(filename=cue_path.name, sha256=digest(cue_path.read_bytes()), text=cue,
                         note='CUE references SLPS_00782.BIN; attachment has (1) in its filename. No bytes modified.'),
                executable=exe, file_count=len(files), directories=len(visited),
                files=files, archive_source_matches=source_matches, resource_manifest_matches=assets,
                limits=['Sync, mode and duplicated subheaders checked; EDC/ECC not recomputed.',
                        'Form 2 entries have an ISO 2048-byte projection hash, not a decoded audio hash.',
                        'Proves supplied disc matches executable and listed resources, not full gameplay emulation.'])


if __name__ == '__main__':
    result = verify(*(Path(p).resolve() for p in sys.argv[1:4]))
    output = Path(__file__).with_name('disc-verification.json')
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({k: result[k] for k in ('all_passed', 'file_count', 'directories')}))
    print('source matches', len(result['archive_source_matches']),
          'resource records', len(result['resource_manifest_matches']))
