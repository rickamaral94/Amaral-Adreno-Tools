#!/usr/bin/env python3
"""Audit selected Vulkan Roadmap 2026 features against a pinned Mesa/Turnip tree.

This is intentionally a structural audit, not a conformance test.  It prevents us
from confusing a registry/header entry with a real Turnip feature and highlights
when an extension on the research watchlist appears in upstream source.
"""

from __future__ import annotations

import argparse
import json
import pathlib
import sys


ROOT = pathlib.Path(__file__).resolve().parents[1]
MATRIX = ROOT / "evidence/vulkan-roadmap-2026.json"


def marker_guard(lines: list[str], marker: str) -> str | None:
    """Return the closest active preprocessor guard when marker appears."""
    stack: list[str] = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("#ifdef "):
            stack.append(stripped.split(maxsplit=1)[1])
        elif stripped.startswith("#ifndef "):
            stack.append("!" + stripped.split(maxsplit=1)[1])
        elif stripped.startswith("#if "):
            stack.append(stripped[4:].strip())
        elif stripped.startswith("#endif"):
            if stack:
                stack.pop()
        if marker in line:
            return " && ".join(stack) if stack else ""
    return None


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("mesa_src", type=pathlib.Path)
    parser.add_argument(
        "--fail-on-new-support",
        action="store_true",
        help="Fail if a watchlisted extension unexpectedly appears in Turnip source.",
    )
    args = parser.parse_args()

    matrix = json.loads(MATRIX.read_text(encoding="utf-8"))
    mesa_src = args.mesa_src.resolve()
    tu_device = mesa_src / matrix["mesa"]["turnip_device_file"]
    meson_file = mesa_src / "src/freedreno/vulkan/meson.build"

    if not tu_device.is_file():
        raise SystemExit(f"missing Turnip device file: {tu_device}")
    if not meson_file.is_file():
        raise SystemExit(f"missing Turnip meson file: {meson_file}")

    lines = tu_device.read_text(encoding="utf-8").splitlines()
    meson = meson_file.read_text(encoding="utf-8")

    failures: list[str] = []
    discoveries: list[str] = []

    entries = matrix["strategic_extensions"] + matrix["qcom_watchlist"]
    for item in entries:
        marker = item["source_marker"]
        guard = marker_guard(lines, marker)
        present = guard is not None
        expected = bool(item["source_marker_expected"])

        if expected and not present:
            failures.append(f"{item['name']}: expected marker {marker!r} disappeared")
        elif not expected and present:
            discoveries.append(
                f"{item['name']}: marker {marker!r} is now present"
                + (f" under guard {guard}" if guard else "")
            )

        declared_guard = item.get("compile_guard")
        if present and declared_guard:
            if declared_guard not in (guard or ""):
                failures.append(
                    f"{item['name']}: expected guard {declared_guard}, found {guard or 'none'}"
                )

        print(
            f"{item['name']}: status={item['status']} "
            f"marker={'yes' if present else 'no'} "
            f"guard={guard if guard is not None else '-'} "
            f"action={item['action']}"
        )

    # Keep the Android-specific WSI assumption explicit.  If Mesa changes this,
    # the Roadmap matrix needs human review before we infer new Android support.
    if "if with_platform_android" in meson and "tu_wsi = true" in meson:
        discoveries.append(
            "Turnip Meson contains Android WSI logic; review TU_USE_WSI_PLATFORM assumptions."
        )

    for msg in discoveries:
        print(f"DISCOVERY: {msg}", file=sys.stderr)

    if failures:
        for msg in failures:
            print(f"ERROR: {msg}", file=sys.stderr)
        return 1

    if discoveries and args.fail_on_new_support:
        return 2

    print("Vulkan Roadmap structural audit: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
