#!/usr/bin/env python3
"""Fortnightly source triage: control update, never automatic compatibility claims."""
import json
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
source = pathlib.Path(sys.argv[1])
lock = json.loads((ROOT / 'config/mesa-lock.json').read_text())
def git(*args):
    return subprocess.check_output(['git', '-C', str(source), *args], text=True).strip()
head = git('rev-parse', 'HEAD')
paths = git('diff', '--name-only', lock['mesa']['commit'], head).splitlines()
relevant = [p for p in paths if p.startswith(('src/freedreno/', 'src/compiler/nir/', 'src/compiler/spirv/', 'src/vulkan/'))]
record = {'schema': 1, 'base_mesa': lock['mesa']['commit'], 'observed_mesa': head,
          'observed_commit_date': git('show', '-s', '--format=%cI', 'HEAD'),
          'decision': 'update-control' if relevant else 'maintain', 'candidate_requires_review': True,
          'changed_relevant_paths': relevant,
          'note': 'Paths are triage only. Review real diffs, regressions, GPU scope and CTS before selecting a candidate.'}
(ROOT / 'evidence/upstream-review.json').write_text(json.dumps(record, indent=2)+'\n')
print(json.dumps(record, indent=2))
