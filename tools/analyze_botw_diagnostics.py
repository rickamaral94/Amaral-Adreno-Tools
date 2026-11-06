#!/usr/bin/env python3
"""Extract selected BOTW diagnostics without exporting raw logs or device IDs.

CPU values labeled ms/frame by the thread section are per present, not per
real game frame. No causal or A/B verdict is inferred from these summaries.
"""
import argparse
import hashlib
import json
import re
import zipfile
from pathlib import Path

HEADER = re.compile(r'===== performance diagnosis: (\d+) s, (\d+) presents \((\d+) in gameplay, (\d+) in menus or events\)')
SUMMARY = re.compile(r'summary: ([\d.]+) real frames a second .*?GPU ([\d.]+) ms per real frame')


def parse(text):
    # Embedded reports have a time/[diag] prefix; standalone exports do not.
    lines = text.splitlines()
    if any('[diag]' in line for line in lines):
        lines = [line.split('[diag]', 1)[1].lstrip() for line in lines if '[diag]' in line]
    normalized = '\n'.join(lines)
    heads = list(HEADER.finditer(normalized))
    result = []
    for index, head in enumerate(heads):
        block = normalized[head.start():heads[index + 1].start() if index + 1 < len(heads) else len(normalized)]
        summary = SUMMARY.search(block)
        run = re.search(r'^run: (.*?)\| LRZ (on|off) \| internal resolution (.*?) \| frame generation (.*?) \|', block, re.M | re.S)
        if not summary or not run:
            continue
        seconds, presents, gameplay, other = map(int, head.groups())
        fps, gpu = map(float, summary.groups())
        label = run.group(1)
        driver = ('amaral-5.7.13.1' if 'v5.7.13.1' in label else
                  'turnio-26.2-R4' if 'Turnio_v26.2.0_R4' in label else 'other')
        row = dict(duration_s=seconds, presents=presents, gameplay_presents=gameplay,
                   other_presents=other, driver=driver, lrz=run.group(2),
                   real_fps_reported=fps, gpu_ms_per_real_frame_reported=gpu)
        # Only emit known resolution/FG values, never arbitrary user text.
        row['resolution'] = run.group(3) if re.fullmatch(r'(?:1x|Dynamic \(now [0-9.]+\))', run.group(3)) else 'other'
        row['frame_generation'] = run.group(4) if re.fullmatch(r'\d+x', run.group(4)) else 'other'
        screen = re.search(r'screen p50 ([\d.]+) p95 ([\d.]+) p99 ([\d.]+) ms', block)
        if screen:
            row['screen_ms_p50_p95_p99'] = list(map(float, screen.groups()))
        cpu = re.search(r'^thread render .*?\n\s*its own CPU clock: ([\d.]+)% of ([\d.]+) s busy \(([\d.]+) ms/frame\)', block, re.M)
        if cpu:
            percent, observed_seconds, per_present = map(float, cpu.groups())
            row['render_cpu_ms_per_present_reported'] = per_present
            row['render_cpu_seconds_observed'] = percent * observed_seconds / 100
            row['render_cpu_ms_per_real_frame_approx'] = (percent * observed_seconds * 10 / (seconds * fps)) if seconds * fps else None
            row['cpu_conversion_note'] = 'Approximation: CPU observation window versus reported real FPS window may differ.'
        stamps = re.search(r'GPU timestamps read in the window: (\d+) counted, (\d+) inside', block)
        if stamps:
            row['timestamp_count'], row['nested_intervals_reported'] = map(int, stamps.groups())
        # Identical summary fields are grouped, not declared independent runs.
        result.append(row)
    return result


def analyze(path):
    raw = Path(path).read_bytes()
    groups, payloads = {}, set()
    members = duplicates = 0
    with zipfile.ZipFile(path) as archive:
        infos = [i for i in archive.infolist() if not i.is_dir() and i.filename.endswith('.txt')]
        if sum(i.file_size for i in infos) > 64 * 1024 * 1024:
            raise ValueError('Text payload exceeds 64 MiB limit')
        for info in infos:
            data = archive.read(info)
            members += 1
            digest = hashlib.sha256(data).hexdigest()
            if digest in payloads:
                duplicates += 1
            payloads.add(digest)
            for row in parse(data.decode('utf-8', errors='replace')):
                key = json.dumps(row, sort_keys=True)
                entry = groups.setdefault(key, {'metrics': row, 'source_sha256': set(), 'occurrences': 0})
                entry['source_sha256'].add(digest)
                entry['occurrences'] += 1
    reports = []
    for entry in groups.values():
        entry['source_sha256'] = sorted(entry['source_sha256'])
        reports.append(entry)
    return dict(schema=1, archive_sha256=hashlib.sha256(raw).hexdigest(),
                text_members=members, exact_duplicate_text_members=duplicates,
                distinct_summary_groups=len(reports),
                qualification='observations only; matching summaries do not prove independent runs; GPU busy interpretation unverified',
                reports=reports)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('archive', type=Path)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    result = json.dumps(analyze(args.archive), indent=2, ensure_ascii=False) + '\n'
    if args.output:
        args.output.write_text(result, encoding='utf-8')
    else:
        print(result, end='')


if __name__ == '__main__':
    main()
