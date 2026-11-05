#!/usr/bin/env python3
"""Build the pinned third-party PS1VMC tool and cross-check all card images.

Tool source is unmodified, GPL-3.0, included with its LICENSE in the archive.
Upstream: https://github.com/bucanero/ps2vmc-tool
Commit: 32a024518586a47d685d8c4ea58b67dc4e4472ce
"""
import hashlib
import json
import subprocess
import tarfile
import tempfile
from pathlib import Path
from raw_card import RawCard, BLOCK

ROOT = Path(__file__).resolve().parent
sha = lambda data: hashlib.sha256(bytes(data)).hexdigest()
PATH = b'bu00:BISLPS-00782CONV'
archive = ROOT/'ps1vmc-source-32a0245.tar.gz'
records = []
with tempfile.TemporaryDirectory(prefix='conveni-ps1vmc-') as temporary:
    work = Path(temporary)
    with tarfile.open(archive) as source:
        source.extractall(work, filter='data')
    build = subprocess.run(['make', 'ps1'], cwd=work, capture_output=True, text=True)
    (ROOT/'external-build.log').write_text(build.stdout+build.stderr)
    assert build.returncode == 0
    tool = work/'ps1vmc-tool'
    def run(image, *args):
        process = subprocess.run([str(tool), str(image), *map(str, args)], cwd=ROOT, capture_output=True, text=True)
        records.append(dict(image=image.name, arguments=[str(a) if not isinstance(a, Path) else a.name for a in args],
                            returncode=process.returncode, stdout=process.stdout, stderr=process.stderr))
        assert process.returncode == 0
        return process.stdout
    outputs = []
    for layout, first_slot in [('contiguous', 0), ('fragmented', 14)]:
        for phase in range(2):
            stem = layout+'-'+str(phase)
            image = ROOT/(stem+'.mcr')
            before = image.read_bytes()
            listing = run(image, '--list')
            assert 'BISLPS-00782CONV' in listing and '114688' in listing
            exported = ROOT/(stem+'.external.raw')
            run(image, '--extract-save', first_slot, exported)
            expected = (ROOT/(stem+'.card-file.bin')).read_bytes()
            assert exported.read_bytes() == expected and image.read_bytes() == before
            outputs.append(dict(image=image.name, slot=first_slot, bytes=len(expected), sha256=sha(expected),
                                extracted_equal=True, input_image_unchanged=True))
        image = ROOT/layout/'operating-menu-save.mcr'
        before = image.read_bytes()
        exported = ROOT/layout/'operating-menu-save.external.raw'
        run(image, '--extract-save', first_slot, exported)
        expected = (ROOT/layout/'operating-menu-save.card-file.bin').read_bytes()
        assert exported.read_bytes() == expected and image.read_bytes() == before
        outputs.append(dict(image=layout+'/'+image.name, slot=first_slot, bytes=len(expected), sha256=sha(expected),
                            extracted_equal=True, input_image_unchanged=True, origin='original play UI'))
    original_image = ROOT/'fragmented-1.mcr'
    mcs = ROOT/'external-export.mcs'
    run(original_image, '--mcs-export', 14, mcs)
    expected = (ROOT/'fragmented-1.card-file.bin').read_bytes()
    assert mcs.read_bytes()[128:] == expected
    created = ROOT/'external-created.mcr'
    run(created, '--mc-create')
    run(created, '--inject-save', mcs)
    external = RawCard(created.read_bytes())
    assert external.validate()[PATH]['size'] == 114688
    assert external.read(PATH, 0, 114688, trace=False) == expected
    exported = ROOT/'external-created.raw'
    slot = external.validate()[PATH]['blocks'][0]-1
    run(created, '--extract-save', slot, exported)
    assert exported.read_bytes() == expected
    report = dict(all_passed=True, upstream='https://github.com/bucanero/ps2vmc-tool',
                  upstream_commit='32a024518586a47d685d8c4ea58b67dc4e4472ce',
                  source_archive=archive.name, source_archive_sha256=sha(archive.read_bytes()),
                  built_tool_sha256=sha(tool.read_bytes()), original_images=outputs,
                  external_created_directory={key.decode(): value for key, value in external.validate().items()},
                  external_created_file_sha256=sha(expected), invocations=records,
                  limits=['Independent filesystem reader/writer, not BIOS or physical SIO/hardware.',
                          'Third-party native CLI is not linked into the game or the raw-card Python model.',
                          'Compiler warnings retained in external-build.log; build exits zero.'])
    (ROOT/'external-results.json').write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n')
    print(json.dumps(dict(all_passed=True, external_reads=7, external_creates=1, external_imports=1)))
