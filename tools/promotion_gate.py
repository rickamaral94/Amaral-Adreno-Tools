#!/usr/bin/env python3
"""Promotion requires a reviewed, exact-artifact qualification record."""
import json
import re

# The repository owner may accept a release without these gates. CI,
# reproducibility, hardware evidence and the exact artifact identity can never
# be waived, and every waived gate stays recorded as not-run.
WAIVABLE = {'cts', 'vvl', 'regressions', 'ab', 'hardware_families'}


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
    exception = data.get('owner_exception')
    waived = set()
    if exception is not None:
        if not exception.get('approved_by') or not exception.get('approved_at') or not exception.get('rationale'):
            raise RuntimeError('Owner exception needs approved_by, approved_at and rationale')
        waived = set(exception.get('waived', []))
        if not waived or not waived <= WAIVABLE:
            raise RuntimeError(f'Owner exception may only waive {sorted(WAIVABLE)}')
    for key in ('ci', 'reproducibility', 'cts', 'vvl', 'hardware', 'regressions'):
        result = data.get(key, {})
        if key in waived:
            if result.get('status') != 'not-run':
                raise RuntimeError(f'Waived {key} must be recorded as not-run')
            continue
        if result.get('status') != 'pass' or not result.get('evidence'):
            raise RuntimeError(f'{key} requires pass and evidence links')
    if 'hardware_families' not in waived and not {'A6xx', 'A7xx', 'A8xx'} <= set(data['hardware'].get('families', [])):
        raise RuntimeError('Universal promotion requires A6xx/A7xx/A8xx coverage')
    if not data['hardware'].get('families'):
        raise RuntimeError('Hardware evidence must name the families tested')
    if not data.get('reviewer') or not data.get('reviewed_at'):
        raise RuntimeError('Named technical review required')
    # This candidate changes defaults; future exemptions must have an explicit rationale.
    ab = data.get('ab', {})
    if 'ab' in waived:
        if ab.get('status') != 'not-run':
            raise RuntimeError('Waived ab must be recorded as not-run')
    elif ab.get('status') != 'pass' or ab.get('rounds', 0) < 5 or not ab.get('thermal_gate') or not ab.get('evidence'):
        raise RuntimeError('Balanced A/B, at least 5 rounds, thermal gate and evidence required')
    return data
