#!/usr/bin/env python3
"""Restore the committed analysis inputs and latest natural CPU checkpoint.

Uses only Python's standard library. The destination must be empty. Runtime
dependencies are listed in the committed source-reference requirements file.
"""
import argparse
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
import zipfile
import zlib
from pathlib import Path


def restore(destination):
    root = Path(__file__).resolve().parent
    latest = json.loads((root / 'LATEST-ANALYSIS.json').read_text())
    destination = destination.resolve()
    if destination.exists() and (not destination.is_dir() or any(destination.iterdir())):
        raise ValueError('Destination must be an empty directory')
    destination.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='conveni-archive-') as temporary:
        archive = Path(temporary) / 'checkpoint.zip'
        subprocess.run([sys.executable, str(root / 'archives/20261103-r2/restore.py'),
                        '--restore', str(archive)], check=True)
        with zipfile.ZipFile(archive) as source:
            for entry in source.infolist():
                if not entry.filename.startswith('algorithm-analysis/'):
                    continue
                output = destination / entry.filename
                if not output.resolve().is_relative_to(destination):
                    raise ValueError('Unsafe archive entry')
                if entry.is_dir():
                    output.mkdir(parents=True, exist_ok=True)
                else:
                    output.parent.mkdir(parents=True, exist_ok=True)
                    with source.open(entry) as incoming, output.open('wb') as outgoing:
                        shutil.copyfileobj(incoming, outgoing)
    algo = destination / 'algorithm-analysis'
    reference = root / 'analysis/20261103-operating-continuation/source-reference'
    for source in reference.glob('*.py'):
        shutil.copy2(source, algo / source.name)
    snapshots = algo / 'source/opened-snapshots-20261028'
    for key in ('metadata', 'compressed_ram'):
        source = (root / latest[key]).resolve()
        if not source.is_relative_to(root):
            raise ValueError('Unsafe checkpoint path')
        shutil.copy2(source, snapshots / source.name)
    metadata = json.loads((root / latest['metadata']).read_text())
    ram = zlib.decompress((root / latest['compressed_ram']).read_bytes())
    assert len(ram) == 2097152
    assert hashlib.sha256(ram).hexdigest() == latest['ram_sha256'] == metadata['ram_sha256']
    assert hashlib.sha256((algo / 'source/SLPS_007.82').read_bytes()).hexdigest() == metadata['source_executable_sha256']
    assert metadata['completed_iterations'] == latest['completed_iterations']
    print(json.dumps(dict(algorithm_analysis=str(algo), snapshot=latest['snapshot'],
                          clock=latest['clock'], completed_iterations=latest['completed_iterations'],
                          ram_sha256=latest['ram_sha256']), indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--destination', required=True, type=Path)
    restore(parser.parse_args().destination)
