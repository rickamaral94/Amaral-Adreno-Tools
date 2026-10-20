#!/usr/bin/env python3
"""Verify downloaded build outputs against source and locked configuration."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import zipfile
from release_version import patchset_fingerprint

ROOT = Path(__file__).resolve().parents[1]

def verify(directory, source_sha, qualification=None):
    lock = json.loads((ROOT / 'config/mesa-lock.json').read_text())
    for variant, suffix in [('standard', ''), ('oneui', '_oneUI')]:
        name = f'turnip_amaral_{lock["mesa"]["version"]}_v{lock["amaral_revision"]}{suffix}.zip'
        archive = directory / name
        manifest = json.loads((directory / f'BUILD_MANIFEST_{variant}.json').read_text())
        with zipfile.ZipFile(archive) as f:
            elf = hashlib.sha256(f.read('libvulkan_freedreno.so')).hexdigest()
        sha = hashlib.sha256(archive.read_bytes()).hexdigest()
        expected = {'variant': variant, 'source_commit': source_sha, 'lock': lock,
                    'patchset_sha256': patchset_fingerprint(), 'artifact': name,
                    'artifact_sha256': sha, 'elf_sha256': elf}
        for key, value in expected.items():
            if manifest.get(key) != value:
                raise RuntimeError(f'{variant}: manifest {key} mismatch')
        record = dict(line.split('=', 1) for line in (directory / f'REPRODUCIBILITY_{variant}.txt').read_text().splitlines())
        for key, value in {'variant': variant, 'artifact': name, 'artifact_sha256': sha,
                           'elf_sha256': elf, 'independent_builds': '2', 'reproducible': 'true'}.items():
            if record.get(key) != value:
                raise RuntimeError(f'{variant}: reproducibility {key} mismatch')
        if qualification:
            approved = qualification['artifacts'][variant]
            if approved['zip_sha256'] != sha or approved['elf_sha256'] != elf:
                raise RuntimeError('Qualification does not describe these artifacts')
        subprocess.run(['bash', str(ROOT / 'scripts/validate_artifact.sh'), str(archive)], check=True)
    print('Exact-source release bundle verified')

if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('directory', type=Path)
    p.add_argument('--source-sha')
    p.add_argument('--qualification', action='store_true')
    a = p.parse_args()
    qualification = None
    if a.qualification:
        from promotion_gate import validate_promotion
        state = json.loads((ROOT / 'config/version-state.json').read_text())
        qualification = validate_promotion(ROOT, state['candidate'], json.loads((ROOT / 'config/mesa-lock.json').read_text()))
    source = a.source_sha or subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip()
    verify(a.directory, source, qualification)
