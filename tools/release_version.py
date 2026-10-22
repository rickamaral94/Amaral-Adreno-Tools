#!/usr/bin/env python3
"""Resolve Amaral release versions and guard the stable patch set.

The public version is M.V.A.U:
  M: Mesa numeric-version generation
  V: Vulkan header-version generation
  A: Amaral patch/configuration revision
  U: upstream Mesa snapshot revision
"""

import argparse
import datetime as dt
import hashlib
import json
import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
LOCK_PATH = ROOT / "config/mesa-lock.json"
STATE_PATH = ROOT / "config/version-state.json"
EVIDENCE_PATH = ROOT / "evidence/candidates.json"
PATCHSET_PATTERNS = (
    "patches/*.patch",
    "config/patches.json",
    "tools/apply_patches.py",
    "tools/validate_elf.py",
    "tools/build_manifest.py",
    "build-aux/*",
    "requirements-build.txt",
    "scripts/*.sh",
    ".github/workflows/build-candidate.yml",
)
RELEVANT_MESA_PREFIXES = (
    "include/vulkan/",
    "src/android_stub/",
    "src/compiler/nir/",
    "src/compiler/spirv/",
    "src/freedreno/",
    "src/util/",
    "src/vulkan/",
)
RELEVANT_MESA_FILES = {"VERSION", "meson.build", "meson_options.txt"}


def load_json(path):
    with path.open(encoding="utf-8") as stream:
        return json.load(stream)


def save_json(path, value):
    serialized = json.dumps(value, indent=2, ensure_ascii=False) + "\n"
    path.write_text(serialized, encoding="utf-8")


def run_git(mesa_src, *args):
    return subprocess.check_output(
        ["git", "-C", str(mesa_src), *args], text=True
    ).strip()


def normalize_mesa_version(version):
    match = re.match(r"^(\d+)\.(\d+)\.(\d+)", version)
    if not match:
        raise ValueError(f"Unsupported Mesa version: {version}")
    return ".".join(match.groups())


def parse_vulkan_header(header):
    patch_match = re.search(r"^#define VK_HEADER_VERSION (\d+)$", header, re.MULTILINE)
    complete_match = re.search(
        r"#define VK_HEADER_VERSION_COMPLETE\s+"
        r"VK_MAKE_API_VERSION\(\s*0,\s*(\d+),\s*(\d+),\s*VK_HEADER_VERSION\s*\)",
        header,
        re.MULTILINE,
    )
    if not patch_match or not complete_match:
        raise ValueError("Could not determine Vulkan header version")
    return f"{complete_match.group(1)}.{complete_match.group(2)}.{patch_match.group(1)}"


def compose_version(state):
    return ".".join(
        str(value)
        for value in (
            state["mesa"]["generation"],
            state["vulkan"]["generation"],
            state["amaral_revision"],
            state["upstream_revision"],
        )
    )


def advance_upstream_version(state, meta):
    mesa_changed = meta["normalized_version"] != state["mesa"]["normalized_version"]
    vulkan_changed = meta["vulkan_version"] != state["vulkan"]["version"]
    if mesa_changed:
        state["mesa"]["generation"] += 1
    if vulkan_changed:
        state["vulkan"]["generation"] += 1
    state["upstream_revision"] = (
        1 if (mesa_changed or vulkan_changed) else state["upstream_revision"] + 1
    )
    return compose_version(state)


def patchset_files():
    paths = set()
    for pattern in PATCHSET_PATTERNS:
        paths.update(path for path in ROOT.glob(pattern) if path.is_file())
    return sorted(paths, key=lambda path: path.relative_to(ROOT).as_posix())


def patchset_fingerprint():
    digest = hashlib.sha256()
    for path in patchset_files():
        relative = path.relative_to(ROOT).as_posix().encode()
        digest.update(relative)
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    lock = load_json(LOCK_PATH)
    digest.update(json.dumps(lock["build"], sort_keys=True).encode())
    return digest.hexdigest()


def mesa_metadata(mesa_src):
    mesa_src = pathlib.Path(mesa_src)
    commit = run_git(mesa_src, "rev-parse", "HEAD")
    commit_date = run_git(mesa_src, "show", "-s", "--format=%cI", "HEAD")
    title = run_git(mesa_src, "show", "-s", "--format=%s", "HEAD")
    version = (mesa_src / "VERSION").read_text(encoding="utf-8").strip()
    normalized = normalize_mesa_version(version)

    header = (mesa_src / "include/vulkan/vulkan_core.h").read_text(encoding="utf-8")
    vulkan = parse_vulkan_header(header)
    return {
        "commit": commit,
        "commit_date_utc": commit_date,
        "title": title,
        "version": version,
        "normalized_version": normalized,
        "vulkan_version": vulkan,
    }


def emit_output(path, values):
    if not path:
        return
    with path.open("a", encoding="utf-8") as stream:
        for key, value in values.items():
            stream.write(f"{key}={value}\n")


def release_note_path(meta, version):
    return ROOT / "docs/releases" / f"mesa-{meta['version']}-v{version}.md"


def write_release_notes(
    path, meta, version, channel, previous_commit, relevant_files=None
):
    classification = "Latest estável" if channel == "latest" else "Pré-release para A/B"
    text = f"""# Turnip Amaral {meta['version']} v{version}

## Classificação

**{classification}.**

## Base rastreável

- Mesa: `{meta['version']}`
- Mesa commit: `{meta['commit']}`
- Mesa HEAD: {meta['title']}
- Commit anterior: `{previous_commit}`
- Vulkan headers: `{meta['vulkan_version']}`
- Backend: Turnip/Freedreno + KGSL
- ABI: Android AArch64 (`armv8-a`)
- Toolchain: Android NDK r29
"""
    if relevant_files:
        shown = relevant_files[:40]
        text += f"\n## Superfície Mesa relevante ({len(relevant_files)} arquivos)\n\n"
        text += "\n".join(f"- `{name}`" for name in shown) + "\n"
        if len(relevant_files) > len(shown):
            text += f"- … e mais {len(relevant_files) - len(shown)} arquivos.\n"
    text += """
## Variantes

- Standard: Android/KGSL universal.
- OneUI: mesmo código e recursos, com o ajuste UBWC isolado para FD740/KGSL.

## Política desta publicação

Toda mudança passa por candidata. Promoção exige evidência vinculada ao SHA
Mesa, fingerprint e hashes Standard/OneUI. Build reproduzível não prova
compatibilidade, conformidade ou ganho de desempenho. Defaults de compiler,
suballocadores e perfis por título permanecem upstream; patches de pesquisa
não são aplicados aos pacotes distribuídos.

"""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def update_lock(lock, state, meta, version):
    lock["amaral_revision"] = version
    lock["mesa"]["commit"] = meta["commit"]
    lock["mesa"]["version"] = meta["version"]
    lock["mesa"]["commit_date_utc"] = meta["commit_date_utc"]
    checked_at = dt.datetime.now(dt.timezone.utc).replace(microsecond=0)
    lock["mesa"]["checked_at_utc"] = checked_at.isoformat().replace("+00:00", "Z")
    state["current_version"] = version
    state["mesa"]["normalized_version"] = meta["normalized_version"]
    state["vulkan"]["version"] = meta["vulkan_version"]


def update_patch_apply_evidence(commit):
    evidence = load_json(EVIDENCE_PATH)
    manifest = load_json(ROOT / "config/patches.json")
    distributed = set(manifest["standard"] + manifest["oneui_extra"])
    for item in evidence["candidates"]:
        if item.get("patch") in distributed:
            item["patch_apply_verified_on_mesa"] = commit
    save_json(EVIDENCE_PATH, evidence)


def prepare_upstream(args):
    raise RuntimeError("Direct upstream Latest publication is disabled; prepare a reviewed candidate")


def prepare_candidate(args):
    lock = load_json(LOCK_PATH)
    state = load_json(STATE_PATH)
    meta = mesa_metadata(args.mesa_src)
    if meta["commit"] != lock["mesa"]["commit"]:
        raise RuntimeError(
            "Candidate Mesa source does not match config/mesa-lock.json"
        )
    fingerprint = patchset_fingerprint()
    if fingerprint == state["stable_patchset_sha256"] and meta["commit"] == state["last_released_mesa_commit"]:
        emit_output(args.github_output, {"candidate_available": "false"})
        print("No Amaral patch-set change to publish.")
        return 0
    existing = state.get("candidate")
    if existing and existing.get("patchset_sha256") == fingerprint and existing.get("mesa_commit") == meta["commit"]:
        emit_output(args.github_output, {"candidate_available": "false"})
        print("This Amaral patch set already has a candidate release.")
        return 0

    previous_commit = state["last_released_mesa_commit"]
    if meta["normalized_version"] != state["mesa"]["normalized_version"]:
        state["mesa"]["generation"] += 1
    if meta["vulkan_version"] != state["vulkan"]["version"]:
        state["vulkan"]["generation"] += 1
    state["amaral_revision"] += 1
    state["upstream_revision"] = 1
    version = compose_version(state)
    state["candidate"] = {"version": version, "patchset_sha256": fingerprint, "mesa_commit": meta["commit"]}
    update_lock(lock, state, meta, version)
    note_path = release_note_path(meta, version)
    if args.write:
        save_json(LOCK_PATH, lock)
        save_json(STATE_PATH, state)
        write_release_notes(note_path, meta, version, "prerelease", previous_commit)

    tag = f"mesa-{meta['version']}-v{version}"
    outputs = {
        "candidate_available": "true",
        "version": version,
        "release_tag": tag,
        "release_title": f"Turnip Amaral {meta['version']} v{version} Candidate",
        "notes_file": note_path.relative_to(ROOT).as_posix(),
        "standard_file": f"turnip_amaral_{meta['version']}_v{version}.zip",
        "oneui_file": f"turnip_amaral_{meta['version']}_v{version}_oneUI.zip",
    }
    emit_output(args.github_output, outputs)
    print(json.dumps(outputs, indent=2))
    return 0


def resume_release(args):
    """Describe the version already recorded on main for a failed publication retry."""
    lock = load_json(LOCK_PATH)
    state = load_json(STATE_PATH)
    version = state["current_version"]
    if lock["amaral_revision"] != version or version != compose_version(state):
        raise RuntimeError("Recorded release version and Mesa lock disagree")

    candidate = state.get("candidate")
    if args.channel == "upstream":
        if candidate or version != state["stable_version"]:
            emit_output(args.github_output, {"resume_available": "false"})
            return 0
        if patchset_fingerprint() != state["stable_patchset_sha256"]:
            emit_output(args.github_output, {"resume_available": "false"})
            return 0
    else:
        if not candidate or candidate["version"] != version:
            emit_output(args.github_output, {"resume_available": "false"})
            return 0
        if candidate["patchset_sha256"] != patchset_fingerprint():
            raise RuntimeError("Recorded candidate differs from the current patch set")

    meta = lock["mesa"]
    if args.channel == "upstream" and meta["commit"] != state["last_released_mesa_commit"]:
        raise RuntimeError("Recorded Mesa commit and version state disagree")
    note_path = release_note_path(meta, version)
    if not note_path.is_file():
        raise RuntimeError(f"Recorded release notes missing: {note_path}")
    tag = f"mesa-{meta['version']}-v{version}"
    emit_output(args.github_output, {
        "resume_available": "true",
        "version": version,
        "release_tag": tag,
        "release_title": f"Turnip Amaral {meta['version']} v{version}"
        + (" Candidate" if args.channel == "candidate" else ""),
        "notes_file": note_path.relative_to(ROOT).as_posix(),
        "standard_file": f"turnip_amaral_{meta['version']}_v{version}.zip",
        "oneui_file": f"turnip_amaral_{meta['version']}_v{version}_oneUI.zip",
        "mesa_commit": meta["commit"],
    })
    return 0


def promote_candidate(args):
    state = load_json(STATE_PATH)
    candidate = state.get("candidate")
    if not candidate:
        raise RuntimeError("There is no candidate awaiting promotion")
    if candidate["patchset_sha256"] != patchset_fingerprint():
        raise RuntimeError("Current patch set differs from the published candidate")
    from promotion_gate import validate_promotion
    validate_promotion(ROOT, candidate, load_json(LOCK_PATH))
    emit_output(args.github_output, {"version": candidate["version"]})
    if args.write:
        lock = load_json(LOCK_PATH)
        note_path = release_note_path(
            {"version": lock["mesa"]["version"]}, candidate["version"]
        )
        note = note_path.read_text(encoding="utf-8")
        prerelease = "**Pré-release para A/B.**"
        if prerelease not in note:
            raise RuntimeError(f"Candidate classification not found in {note_path}")
        note_path.write_text(
            note.replace(prerelease, "**Latest estável.**", 1), encoding="utf-8"
        )
        state["stable_patchset_sha256"] = candidate["patchset_sha256"]
        state["stable_version"] = candidate["version"]
        state["last_released_mesa_commit"] = lock["mesa"]["commit"]
        state["candidate"] = None
        save_json(STATE_PATH, state)
    print(candidate["version"])
    return 0


def main():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)
    for name in ("upstream", "candidate"):
        sub = subparsers.add_parser(name)
        sub.add_argument("--mesa-src", required=True, type=pathlib.Path)
        sub.add_argument("--github-output", type=pathlib.Path)
        sub.add_argument("--write", action="store_true")
    promote = subparsers.add_parser("promote")
    promote.add_argument("--github-output", type=pathlib.Path)
    promote.add_argument("--write", action="store_true")
    resume = subparsers.add_parser("resume")
    resume.add_argument("channel", choices=("upstream", "candidate"))
    resume.add_argument("--github-output", type=pathlib.Path)
    subparsers.add_parser("fingerprint")
    args = parser.parse_args()

    if args.command == "fingerprint":
        print(patchset_fingerprint())
        return 0
    if args.command == "upstream":
        return prepare_upstream(args)
    if args.command == "candidate":
        return prepare_candidate(args)
    if args.command == "resume":
        return resume_release(args)
    return promote_candidate(args)


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (KeyError, ValueError, RuntimeError, subprocess.CalledProcessError) as exc:
        print(f"release version error: {exc}", file=sys.stderr)
        sys.exit(1)
