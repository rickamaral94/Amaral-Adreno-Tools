#!/usr/bin/env python3
"""Publish a verified release at the commit that contains its Mesa lock.

An interrupted run may be retried. Existing assets must match exactly; tags and
assets are never moved or replaced by this script.
"""

import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys


def gh(*args, missing_ok=False):
    result = subprocess.run(["gh", *args], text=True, capture_output=True)
    if result.returncode:
        if missing_ok and ("HTTP 404" in result.stderr or "Not Found" in result.stderr):
            return None
        raise RuntimeError(f"gh {' '.join(args)} failed: {result.stderr.strip()}")
    return json.loads(result.stdout) if result.stdout.strip().startswith("{") else result.stdout.strip()


def release(repo, tag):
    return gh("api", f"repos/{repo}/releases/tags/{tag}", missing_ok=True)


def asset_digests(paths):
    return {path.name: "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()
            for path in paths}


def missing_assets(existing, expected):
    found = {asset["name"]: asset.get("digest") for asset in existing}
    for name, digest in expected.items():
        if name in found and found[name] != digest:
            raise RuntimeError(f"Published asset differs from tested build: {name}")
    return [name for name in expected if name not in found]


def tag_commit(repo, tag):
    ref = gh("api", f"repos/{repo}/git/ref/tags/{tag}", missing_ok=True)
    if ref is None:
        return None
    obj = ref["object"]
    while obj["type"] == "tag":
        obj = gh("api", f"repos/{repo}/git/tags/{obj['sha']}")["object"]
    if obj["type"] != "commit":
        raise RuntimeError(f"Tag {tag} does not point to a commit")
    return obj["sha"]


def check_archives(paths, standard, oneui):
    lines = (Path("dist") / "SHA256SUMS.txt").read_text().splitlines()
    expected = {name: digest.removeprefix("sha256:")
                for name, digest in asset_digests(paths).items()}
    checksum_lines = {name: digest for digest, name in
                      (line.split(maxsplit=1) for line in lines)}
    if checksum_lines != {name: expected[name] for name in (standard, oneui)}:
        raise RuntimeError("SHA256SUMS.txt does not match the two tested archives")
    for variant, name in (("standard", standard), ("oneui", oneui)):
        record = (Path("dist") / f"REPRODUCIBILITY_{variant}.txt").read_text()
        if not all(value in record for value in
                   ("reproducible=true", "independent_builds=2",
                    f"artifact={name}", f"artifact_sha256={expected[name]}")):
            raise RuntimeError(f"Reproducibility record does not match {name}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("status", nargs="?", choices=("status", "publish"), default="publish")
    parser.add_argument("--repo", default=os.environ.get("GITHUB_REPOSITORY"))
    parser.add_argument("--tag", required=True)
    parser.add_argument("--source-sha", required=True)
    parser.add_argument("--standard", required=True)
    parser.add_argument("--oneui", required=True)
    parser.add_argument("--title")
    parser.add_argument("--notes-file", type=Path)
    parser.add_argument("--channel", choices=("latest", "candidate"))
    args = parser.parse_args()
    if not args.repo:
        raise RuntimeError("GitHub repository is required")

    names = (args.standard, args.oneui, "SHA256SUMS.txt",
             "REPRODUCIBILITY_standard.txt", "REPRODUCIBILITY_oneui.txt")
    current = release(args.repo, args.tag)
    if args.status == "status":
        # A complete historical release needs no rebuilding. The publication
        # path checks tag ownership and all hashes before changing anything.
        print("complete" if current and {a["name"] for a in current["assets"]} >= set(names)
              else "incomplete")
        return

    if not args.title or not args.notes_file or not args.channel:
        raise RuntimeError("Publication requires title, notes and channel")
    paths = [Path("dist") / name for name in names]
    if any(not path.is_file() for path in paths):
        raise RuntimeError("A tested release asset is missing")
    check_archives(paths, args.standard, args.oneui)
    expected = asset_digests(paths)
    target = tag_commit(args.repo, args.tag)
    if target is not None and target != args.source_sha:
        raise RuntimeError(f"Tag {args.tag} points to {target}, expected {args.source_sha}")
    if current is None:
        if target is not None:
            raise RuntimeError(f"Tag {args.tag} exists without a release; inspect it before retry")
        flags = ["--prerelease", "--latest=false"] if args.channel == "candidate" else ["--latest"]
        gh("release", "create", args.tag, *(str(path) for path in paths), "--repo", args.repo,
           "--target", args.source_sha, "--title", args.title,
           "--notes-file", str(args.notes_file), *flags)
        current = release(args.repo, args.tag)
    if tag_commit(args.repo, args.tag) != args.source_sha:
        raise RuntimeError("Published tag does not match the recorded source")

    for name in missing_assets(current["assets"], expected):
        gh("release", "upload", args.tag, str(Path("dist") / name), "--repo", args.repo)
        current = release(args.repo, args.tag)
    if missing_assets(current["assets"], expected):
        raise RuntimeError("Published assets are incomplete")
    flags = ["--prerelease", "--latest=false"] if args.channel == "candidate" else ["--prerelease=false", "--latest"]
    gh("release", "edit", args.tag, "--repo", args.repo, "--title", args.title,
       "--notes-file", str(args.notes_file), *flags)
    current = release(args.repo, args.tag)
    if bool(current["prerelease"]) != (args.channel == "candidate"):
        raise RuntimeError("Published channel verification failed")
    if args.channel == "latest":
        latest = gh("api", f"repos/{args.repo}/releases/latest")
        if latest["tag_name"] != args.tag:
            raise RuntimeError("Latest points to another release")
    print(f"Verified {args.tag} at {args.source_sha}")


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, KeyError, RuntimeError) as exc:
        print(f"release publication error: {exc}", file=sys.stderr)
        sys.exit(1)
