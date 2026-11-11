#!/usr/bin/env python3
"""Verify that the pinned/patched Mesa keeps the known FD735/A22 chip-id coverage."""
import argparse
import json
import pathlib
import re

FUSE_MASK = 0x0000FFFF00000000
KNOWN = (
    {"name": "FD735", "chip_id": 0xFFFF43030B00},
    {"name": "Adreno (TM) 735", "chip_id": 0xFFFF43030E01},
)
SOURCE_RE = re.compile(
    r'GPUId\s*\(\s*chip_id\s*=\s*(0x[0-9a-fA-F]+)\s*,\s*name\s*=\s*"([^"]+)"\s*\)'
)
CATALOG_RE = re.compile(
    r'\{\s*\{\s*\d+\s*,\s*(0x[0-9a-fA-F]+)\s*\}\s*,\s*"([^"]+)"'
)


def parse_chip_id(value):
    chip_id = int(str(value), 0)
    if chip_id < 0 or chip_id > 0xFFFFFFFFFFFFFFFF:
        raise ValueError(f"chip id outside uint64: {value}")
    return chip_id


def dev_id_compare(reference, observed):
    """Mirror Mesa's chip-id path in freedreno_dev_info.c (gpu_id=0 table entries)."""
    if reference == observed:
        return True
    if (reference & 0xFF) == 0xFF and (
        (reference & 0xFFFFFF00) == (observed & 0xFFFFFF00)
    ):
        return True
    if (reference & FUSE_MASK) == FUSE_MASK:
        observed_with_wildcard_fuse = observed | FUSE_MASK
        if reference == observed_with_wildcard_fuse:
            return True
        if (reference & 0xFF) == 0xFF and (
            (reference & 0xFFFFFF00)
            == (observed_with_wildcard_fuse & 0xFFFFFF00)
        ):
            return True
    return False


def _entries(text, pattern):
    return [(parse_chip_id(chip_id), name) for chip_id, name in pattern.findall(text)]


def _require_known(entries, origin):
    found = {(chip_id, name) for chip_id, name in entries}
    missing = [
        item for item in KNOWN
        if (item["chip_id"], item["name"]) not in found
    ]
    if missing:
        wanted = ", ".join(
            f'{item["name"]}=0x{item["chip_id"]:012x}' for item in missing
        )
        raise ValueError(f"{origin}: missing required FD735 entries: {wanted}")


def validate_source(mesa_root):
    path = pathlib.Path(mesa_root) / "src/freedreno/common/freedreno_devices.py"
    entries = _entries(path.read_text(encoding="utf-8"), SOURCE_RE)
    _require_known(entries, path)
    return path


def validate_catalog(path):
    path = pathlib.Path(path)
    entries = _entries(path.read_text(encoding="utf-8"), CATALOG_RE)
    _require_known(entries, path)
    return path


def classify_chip(chip_id):
    chip_id = parse_chip_id(chip_id)
    matches = [
        item["name"] for item in KNOWN
        if dev_id_compare(item["chip_id"], chip_id)
    ]
    return {
        "chip_id": f"0x{chip_id:012x}",
        "matched": bool(matches),
        "profiles": matches,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mesa_root", type=pathlib.Path)
    parser.add_argument("--catalog", type=pathlib.Path)
    parser.add_argument("--chip-id", action="append", default=[])
    parser.add_argument("--require-chip-match", action="store_true")
    args = parser.parse_args()

    source = validate_source(args.mesa_root)
    catalog = validate_catalog(args.catalog) if args.catalog else None
    chips = [classify_chip(value) for value in args.chip_id]
    if args.require_chip_match and any(not item["matched"] for item in chips):
        raise SystemExit("one or more observed chip IDs are not covered by the known FD735 entries")

    print(json.dumps({
        "schema": 1,
        "status": "validated-in-code",
        "source": str(source),
        "catalog": str(catalog) if catalog else None,
        "known_profiles": [
            {"name": item["name"], "chip_id": f'0x{item["chip_id"]:012x}'}
            for item in KNOWN
        ],
        "observed_chip_ids": chips,
        "hardware_note": (
            "Code coverage does not prove the RG DDS or Pocket G2 chip ID. "
            "Capture KGSL_PROP_DEVICE_INFO on each physical device."
        ),
    }, indent=2))


if __name__ == "__main__":
    main()
