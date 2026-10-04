#!/usr/bin/env python3
"""Reject upstream vendor overrides except the one explicitly removed by 0008."""
import pathlib
import re
import sys


def check(mesa_root: pathlib.Path, patched: bool = False) -> None:
    config = mesa_root / "src/freedreno/vulkan/00-turnip-defaults.conf"
    source = config.read_text(encoding="utf-8")
    vendor_rules = re.findall(r'<option\s+name="force_vk_vendor"[^>]*>', source)
    if patched:
        if vendor_rules:
            raise ValueError("force_vk_vendor remains in the final Turnip config")
    elif vendor_rules != ['<option name="force_vk_vendor" value="0x1002" />']:
        if vendor_rules:
            raise ValueError("unknown upstream force_vk_vendor rule; review before publication")
    elif 'application_name_match="mgs4.exe"' not in source:
        raise ValueError("vendor override moved away from the reviewed MGS4 rule")


if __name__ == "__main__":
    try:
        check(pathlib.Path(sys.argv[1]), "--patched" in sys.argv[2:])
    except (ValueError, FileNotFoundError) as error:
        raise SystemExit(str(error))
