#!/usr/bin/env python3
"""Promotion requires a reviewed, exact-artifact qualification record."""
import json
import re


def validate_promotion(root, candidate, lock):
    path = root / 'evidence/qualifications' / (candidate['version'] + '.json')
    if not path.is_file():
        raise RuntimeError(f'Qualification missing: {path}')
    data = json.loads(path.read_text())
    expected = {'version': candidate['version'], 'mesa_commit': lock['mesa']['commit'],
                'patchset_sha256': candidate['patchset_sha256']}
    for key, value in expected.items():
        if data.get(key) != value:
            raise RuntimeError(f'Qualification {key} differs from candidate')
    for variant in ('standard', 'oneui'):
        asset = data.get('artifacts', {}).get(variant, {})
        for key in ('zip_sha256', 'elf_sha256'):
            if not re.fullmatch('[0-9a-f]{64}', asset.get(key, '')):
                raise RuntimeError(f'Missing {variant} {key}')
    for key in ('ci', 'reproducibility', 'cts', 'vvl', 'hardware', 'regressions'):
        result = data.get(key, {})
        if result.get('status') != 'pass' or not result.get('evidence'):
            raise RuntimeError(f'{key} requires pass and evidence links')
    if not {'A6xx', 'A7xx', 'A8xx'} <= set(data['hardware'].get('families', [])):
        raise RuntimeError('Universal promotion requires A6xx/A7xx/A8xx coverage')
    if not data.get('reviewer') or not data.get('reviewed_at'):
        raise RuntimeError('Named technical review required')
    # This candidate changes defaults; future exemptions must have an explicit rationale.
    ab = data.get('ab', {})
    if ab.get('status') != 'pass' or ab.get('rounds', 0) < 5 or not ab.get('thermal_gate') or not ab.get('evidence'):
        raise RuntimeError('Balanced A/B, at least 5 rounds, thermal gate and evidence required')
    return data
