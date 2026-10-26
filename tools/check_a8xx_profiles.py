#!/usr/bin/env python3
"""Validate evaluated Mesa profiles against the pristine pinned tree.

Runs Mesa's trusted Python generator, including inherited GPUProps. This is a
source/build gate, not CTS, hardware qualification or a Vulkan feature test.
"""
import argparse
import io
import json
import pathlib
import subprocess
import sys
import tarfile
import tempfile

FIELDS = ("num_ccu", "num_slices", "tile_align_w", "tile_align_h",
          "tile_max_w", "tile_max_h", "cs_shared_mem_size")
EXPECTED = {
    0x44010000: (1, 1, 32, 16, 16384, 16384, 32768),  # A810
    0x44010200: (1, 1, 32, 16, 16384, 16384, 32768),  # A812 (external alias)
    0x44030000: (4, 2, 64, 32, 16416, 16384, 65536),  # A825 (experimental)
    0x44030a20: (4, 2, 64, 32, 16384, 16384, 32768),  # A829
    0x44050000: (6, 3, 96, 32, 16416, 16384, 32768),  # A830
    0x44050001: (6, 3, 96, 32, 16416, 16384, 32768),  # A830 revision 1
    0x44050a21: (4, 2, 64, 32, 16384, 16384, 32768),  # A840 two slices
    0x44050a31: (6, 3, 96, 32, 16416, 16384, 32768),  # A840 three slices
}
EXTERNAL_IDS = {0x44010000, 0x44010200, 0xffff44010200, 0x44030000}
FUSE_MASK = 0xffff00000000
ONEUI_IDS = {0x43050a01, 0xffff43050a01}

# The chip-id arm of Mesa freedreno_dev_info.c:dev_id_compare (both locks).
# A8xx table entries use gpu_id=0. Do not infer an Adreno model from gpu_id.
def chip_matches(reference, actual):
    if reference == actual:
        return True
    if reference & 0xff == 0xff and reference & 0xffffff00 == actual & 0xffffff00:
        return True
    if reference & FUSE_MASK == FUSE_MASK:
        return reference == actual | FUSE_MASK or (
            reference & 0xff == 0xff and reference & 0xffffff00 == actual & 0xffffff00)
    return False


def index(records):
    result = {}
    for row in records:
        key = (row["gpu_id"], row["chip_id"])
        if key in result:
            raise ValueError(f"Duplicate GPU table entry: ({key[0]:#x}, {key[1]:#x})")
        result[key] = row
    return result


def resolve(records, chip):
    matches = [r for r in records if chip_matches(r["chip_id"], chip)]
    if not matches:
        raise ValueError(f"Missing profile for chip {chip:#x}")
    if any(r["info"] != matches[0]["info"] for r in matches[1:]):
        raise ValueError(f"Ambiguous profiles for chip {chip:#x}")
    return matches[0]["info"]


def validate(records, baseline, variant):
    current, original = index(records), index(baseline)
    if variant not in ("standard", "oneui"):
        raise ValueError("Unknown variant")
    for key, old in original.items():
        if key not in current:
            raise ValueError(f"Removed upstream GPU entry: ({key[0]:#x}, {key[1]:#x})")
        expected = json.loads(json.dumps(old))
        if variant == "oneui" and key[1] in ONEUI_IDS:
            expected["info"]["props"]["enable_tp_ubwc_flag_hint"] = True
        if current[key] != expected:
            raise ValueError(f"Unreviewed change to upstream profile: ({key[0]:#x}, {key[1]:#x})")
    for key in current.keys() - original.keys():
        if key[0] != 0 or key[1] not in EXTERNAL_IDS:
            raise ValueError(f"Unreviewed extra GPU entry: ({key[0]:#x}, {key[1]:#x})")
    for chip, values in EXPECTED.items():
        info = resolve(records, chip)
        if info["chip"] != 8:
            raise ValueError(f"Wrong generation for {chip:#x}")
        for field, value in zip(FIELDS, values):
            if info.get(field) != value:
                raise ValueError(f"{chip:#x}: {field} must be {value}, got {info.get(field)}")
    # The A812 addition is explicitly an experimental alias, not new tuning.
    if resolve(records, 0x44010200) != resolve(records, 0x44010000):
        raise ValueError("A812 no longer matches the reviewed A810 alias")
    # A825 is derived from gen1/A830 with exactly these reviewed overrides.
    # Compare the entire expanded object, not only a few topology fields.
    expected_a825 = json.loads(json.dumps(resolve(baseline, 0x44050000)))
    expected_a825.update(dict(zip(FIELDS, EXPECTED[0x44030000])))
    expected_a825["num_sp_cores"] = 4
    expected_a825["props"].update({
        "gmem_ccu_color_cache_fraction": 1,
        "gmem_per_ccu_color_cache_size": 131072,
        "gmem_ccu_depth_cache_fraction": 1,
        "gmem_per_ccu_depth_cache_size": 131072,
        "sysmem_ccu_color_cache_fraction": 0,
        "sysmem_per_ccu_color_cache_size": 131072,
        "sysmem_ccu_depth_cache_fraction": 3,
        "sysmem_per_ccu_depth_cache_size": 98304,
        "gmem_vpc_attr_buf_size": 49152,
        "gmem_vpc_pos_buf_size": 24576,
        "gmem_vpc_bv_pos_buf_size": 32768,
    })
    if resolve(records, 0x44030000) != expected_a825:
        raise ValueError("Unreviewed change to the expanded A825 profile")
    # Never turn a known topology into a catch-all for an unknown sibling.
    for chip in (0x44050a41, 0x44030001):
        if any(chip_matches(r["chip_id"], chip) for r in records):
            raise ValueError(f"Unreviewed matching of chip {chip:#x}")
    return [{"chip_id": f"0x{chip:08x}",
             **{k: resolve(records, chip)[k] for k in FIELDS},
             "hardware_qualified": False} for chip in EXPECTED]


def evaluate(source):
    """Expand the same Python device database used by the driver build."""
    with tempfile.TemporaryDirectory(prefix="amaral-registers-") as temp:
        registers = source / "src/freedreno/registers"
        with (pathlib.Path(temp) / "a6xx.py").open("w") as out:
            subprocess.run([sys.executable, str(registers / "gen_header.py"),
                            "--rnn", str(registers), "--xml",
                            str(registers / "adreno/a6xx.xml"), "py-defines"],
                           stdout=out, check=True)
        code = """import json, sys
sys.path.insert(0, sys.argv[1])
sys.argv = ['freedreno_devices.py', '-p', sys.argv[2]]
from freedreno_devices import s
print(json.dumps([dict(gpu_id=k.gpu_id, chip_id=k.chip_id, name=k.name, info=v)
                  for k,v in s.gpus.items()], default=vars, sort_keys=True))
"""
        return json.loads(subprocess.check_output(
            [sys.executable, "-c", code, str(source / "src/freedreno/common"), temp],
            text=True))


def check(source, variant):
    source = source.resolve()
    # HEAD must be the pinned Mesa before applying patches. No network or reset.
    archive = subprocess.check_output([
        "git", "-C", str(source), "archive", "HEAD",
        "src/freedreno/common", "src/freedreno/registers"])
    with tempfile.TemporaryDirectory(prefix="amaral-baseline-") as temp:
        with tarfile.open(fileobj=io.BytesIO(archive)) as tar:
            tar.extractall(temp, filter="data")
        baseline = evaluate(pathlib.Path(temp))
    return validate(evaluate(source), baseline, variant)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mesa_src", type=pathlib.Path)
    parser.add_argument("--variant", choices=("standard", "oneui"), required=True)
    parser.add_argument("--report", type=pathlib.Path)
    args = parser.parse_args()
    try:
        rows = check(args.mesa_src, args.variant)
    except (ValueError, KeyError, OSError, subprocess.CalledProcessError) as exc:
        parser.exit(1, f"A8xx profile validation failed: {exc}\n")
    if args.report:
        args.report.write_text(json.dumps({"schema": 1, "variant": args.variant,
            "scope": "source profile regression gate; not hardware qualification",
            "profiles": rows}, indent=2) + "\n")
    print(f"{args.variant}: {len(rows)} A8xx chip profiles verified; upstream profiles preserved.")


if __name__ == "__main__":
    main()
