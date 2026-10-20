#!/usr/bin/env python3
"""Record provenance outside the install ZIP; never claim hardware qualification."""
import argparse
import hashlib
import json
import pathlib
import subprocess
import zipfile
from release_version import patchset_fingerprint

ROOT = pathlib.Path(__file__).resolve().parents[1]
def sha(data):
    return hashlib.sha256(data).hexdigest()

if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('variant', choices=['standard', 'oneui'])
    p.add_argument('output', type=pathlib.Path)
    a = p.parse_args()
    files = list(a.output.glob('turnip_amaral_*.zip'))
    if len(files) != 1:
        raise SystemExit('Expected one archive per variant output')
    z = files[0]
    with zipfile.ZipFile(z) as f:
        elf_sha = sha(f.read('libvulkan_freedreno.so'))
        meta = json.loads(f.read('meta.json'))
    manifest = {
        'schema': 1, 'variant': a.variant,
        'source_commit': subprocess.check_output(['git', '-C', str(ROOT), 'rev-parse', 'HEAD'], text=True).strip(),
        'lock': json.loads((ROOT / 'config/mesa-lock.json').read_text()),
        'patchset_sha256': patchset_fingerprint(),
        'patches': json.loads((ROOT / 'config/patches.json').read_text()),
        'artifact': z.name, 'artifact_sha256': sha(z.read_bytes()), 'elf_sha256': elf_sha,
        'meta': meta, 'hardware': 'not-run', 'cts': 'not-run', 'vvl': 'not-run', 'performance': 'not-measured',
    }
    (a.output / f'BUILD_MANIFEST_{a.variant}.json').write_text(json.dumps(manifest, indent=2)+'\n')
