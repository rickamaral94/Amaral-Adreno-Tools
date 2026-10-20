#!/usr/bin/env python3
"""Apply the reviewed manifest to a clean, pinned Mesa tree. Fail closed."""
import argparse
import hashlib
import json
import pathlib
import subprocess

ROOT = pathlib.Path(__file__).resolve().parents[1]


def apply(source, variant):
    lock = json.loads((ROOT / 'config/mesa-lock.json').read_text())
    manifest = json.loads((ROOT / 'config/patches.json').read_text())
    def git(*args):
        return subprocess.check_output(['git', '-C', str(source), *args], text=True).strip()
    if git('rev-parse', 'HEAD') != lock['mesa']['commit']:
        raise RuntimeError('Mesa SHA does not match lock')
    if git('status', '--porcelain'):
        raise RuntimeError('Mesa tree must be clean; use an independent fresh checkout')
    paths = manifest['standard'] + (manifest['oneui_extra'] if variant == 'oneui' else [])
    if set(paths) & set(manifest['research_only']):
        raise RuntimeError('Research patch cannot be distributed')
    for path in paths:
        patch = ROOT / path
        git('apply', '--check', str(patch))
        git('apply', str(patch))
        print(f'{variant}: {path} sha256={hashlib.sha256(patch.read_bytes()).hexdigest()}', flush=True)
    git('diff', '--check')
    subprocess.run(['python3', str(ROOT / 'tools/check_mesa_policy.py'), str(source), '--patched'], check=True)
    device = (source / 'src/freedreno/vulkan/tu_device.cc').read_text()
    # Research exposure must not silently reappear in a new upstream snapshot.
    for name in ('EXT_depth_bias_control', 'EXT_depth_range_unrestricted'):
        if f'.{name} =' in device:
            raise RuntimeError(f'{name} appeared: qualify upstream implementation before updating policy')


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('mesa_src', type=pathlib.Path)
    p.add_argument('--variant', choices=('standard', 'oneui'), required=True)
    a = p.parse_args()
    apply(a.mesa_src, a.variant)
