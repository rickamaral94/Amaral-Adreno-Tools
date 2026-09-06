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
    "build-aux/*",
    "requirements-build.txt",
    "scripts/build_universal.sh",
    "scripts/check_reproducibility.sh",
    "scripts/validate_artifact.sh",
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

Atualizações exclusivas do Mesa upstream podem avançar para Latest depois dos
gates de compilação, aplicação dos patches, validação do pacote e
reprodutibilidade byte a byte. Mudanças próprias do Amaral permanecem como
pré-release até aprovação em testes A/B.

Não há `TU_DEBUG=sysmem` forçado nos perfis Zelda. O autotuner continua livre
para escolher GMEM/SYSMEM, com a preferência por GMEM já validada na v4.5.
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
    for item in evidence["candidates"]:
        if item.get("patch"):
            item["patch_apply_verified_on_mesa"] = commit
    save_json(EVIDENCE_PATH, evidence)


def prepare_upstream(args):
    lock = load_json(LOCK_PATH)
    state = load_json(STATE_PATH)
    meta = mesa_metadata(args.mesa_src)
    fingerprint = patchset_fingerprint()

    if fingerprint != state["stable_patchset_sha256"]:
        emit_output(
            args.github_output,
            {"update_available": "false", "blocked_by_candidate": "true"},
        )
        print(
            "Upstream release skipped: the current Amaral patch set still "
            "requires candidate publication or A/B promotion."
        )
        return 0

    if meta["commit"] == state["last_released_mesa_commit"]:
        emit_output(args.github_output, {"update_available": "false"})
        print("Mesa upstream is already released.")
        return 0

    previous_commit = state["last_released_mesa_commit"]
    changed_files = run_git(
        args.mesa_src, "diff", "--name-only", f"{previous_commit}..{meta['commit']}"
    ).splitlines()
    relevant_files = sorted(
        name
        for name in changed_files
        if name in RELEVANT_MESA_FILES
        or any(name.startswith(prefix) for prefix in RELEVANT_MESA_PREFIXES)
    )
    if not relevant_files:
        emit_output(args.github_output, {"update_available": "false"})
        print("New Mesa commits do not affect the Turnip build surface.")
        return 0

    version = advance_upstream_version(state, meta)
    state["last_released_mesa_commit"] = meta["commit"]
    state["stable_version"] = version
    state["candidate"] = None
    update_lock(lock, state, meta, version)
    note_path = release_note_path(meta, version)

    if args.write:
        save_json(LOCK_PATH, lock)
        save_json(STATE_PATH, state)
        update_patch_apply_evidence(meta["commit"])
        write_release_notes(
            note_path, meta, version, "latest", previous_commit, relevant_files
        )

    tag = f"mesa-{meta['version']}-v{version}"
    outputs = {
        "update_available": "true",
        "version": version,
        "mesa_version": meta["version"],
        "mesa_commit": meta["commit"],
        "vulkan_version": meta["vulkan_version"],
        "release_tag": tag,
        "release_title": f"Turnip Amaral {meta['version']} v{version}",
        "notes_file": note_path.relative_to(ROOT).as_posix(),
        "standard_file": f"turnip_amaral_{meta['version']}_v{version}.zip",
        "oneui_file": f"turnip_amaral_{meta['version']}_v{version}_oneUI.zip",
    }
    emit_output(args.github_output, outputs)
    print(json.dumps(outputs, indent=2))
    return 0


def prepare_candidate(args):
    lock = load_json(LOCK_PATH)
    state = load_json(STATE_PATH)
    meta = mesa_metadata(args.mesa_src)
    if meta["commit"] != lock["mesa"]["commit"]:
        raise RuntimeError(
            "Candidate Mesa source does not match config/mesa-lock.json"
        )
    fingerprint = patchset_fingerprint()
    if fingerprint == state["stable_patchset_sha256"]:
        emit_output(args.github_output, {"candidate_available": "false"})
        print("No Amaral patch-set change to publish.")
        return 0
    existing = state.get("candidate")
    if existing and existing.get("patchset_sha256") == fingerprint:
        emit_output(args.github_output, {"candidate_available": "false"})
        print("This Amaral patch set already has a candidate release.")
        return 0

    previous_commit = state["last_released_mesa_commit"]
    state["amaral_revision"] += 1
    state["upstream_revision"] = 1
    version = compose_version(state)
    state["candidate"] = {"version": version, "patchset_sha256": fingerprint}
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


def promote_candidate(args):
    state = load_json(STATE_PATH)
    candidate = state.get("candidate")
    if not candidate:
        raise RuntimeError("There is no candidate awaiting promotion")
    if candidate["patchset_sha256"] != patchset_fingerprint():
        raise RuntimeError("Current patch set differs from the published candidate")
    emit_output(args.github_output, {"version": candidate["version"]})
    if args.write:
        state["stable_patchset_sha256"] = candidate["patchset_sha256"]
        state["stable_version"] = candidate["version"]
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
    subparsers.add_parser("fingerprint")
    args = parser.parse_args()

    if args.command == "fingerprint":
        print(patchset_fingerprint())
        return 0
    if args.command == "upstream":
        return prepare_upstream(args)
    if args.command == "candidate":
        return prepare_candidate(args)
    return promote_candidate(args)


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (KeyError, ValueError, RuntimeError, subprocess.CalledProcessError) as exc:
        print(f"release version error: {exc}", file=sys.stderr)
        sys.exit(1)
