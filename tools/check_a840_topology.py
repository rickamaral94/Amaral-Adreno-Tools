#!/usr/bin/env python3
"""Check that the two A840 IDs retain independent upstream topologies."""
import pathlib
import re
import sys

source = (pathlib.Path(sys.argv[1]) / "src/freedreno/common/freedreno_devices.py").read_text()
for chip_id, ccu, slices, width, max_width in (
    ("0xffff44050A21", 4, 2, 64, 16384),
    ("0xffff44050A31", 6, 3, 96, 16416),
):
    blocks = [block for block in source.split("add_gpus(") if chip_id in block.split("A6xxGPUInfo(")[0]]
    if len(blocks) != 1:
        raise SystemExit(f"Expected one independent profile for {chip_id}")
    block = blocks[0]
    if any(other in block.split("A6xxGPUInfo(")[0] for other in ("0xffff44050A21", "0xffff44050A31") if other != chip_id):
        raise SystemExit("A840 topologies must not share a profile")
    for field, expected in (("num_ccu", ccu), ("num_slices", slices), ("tile_align_w", width), ("tile_max_w", max_width)):
        match = re.search(rf"\b{field}\s*=\s*(\d+)", block)
        if not match or int(match.group(1)) != expected:
            raise SystemExit(f"Incorrect {field} for {chip_id}")
print("Independent A840 two/three-slice profiles verified.")
