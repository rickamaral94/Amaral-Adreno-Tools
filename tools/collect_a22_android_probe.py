#!/usr/bin/env python3
"""Collect a sanitized, no-root Android/KGSL snapshot for A22 validation.

The helper deliberately does not claim the injected Vulkan driver from shell
state. Pass --runtime-json with VkPhysicalDeviceDriverProperties captured by the
same app/session being benchmarked (Azahar/Eden or another per-app probe).
"""
import argparse
import datetime
import hashlib
import json
import pathlib
import re
import shutil
import subprocess

PROPERTIES = (
    "ro.product.manufacturer",
    "ro.product.model",
    "ro.product.device",
    "ro.board.platform",
    "ro.soc.model",
    "ro.vendor.qti.soc_model",
    "ro.vendor.qti.soc_name",
    "ro.build.display.id",
    "ro.build.version.incremental",
    "ro.build.version.release",
    "ro.build.version.sdk",
    "ro.build.fingerprint",
)
KGSL_FILES = {
    "gpu_model": "/sys/class/kgsl/kgsl-3d0/gpu_model",
    "gpu_id": "/sys/class/kgsl/kgsl-3d0/gpu_id",
    "gpu_chipid": "/sys/class/kgsl/kgsl-3d0/gpu_chipid",
    "chipid": "/sys/class/kgsl/kgsl-3d0/chipid",
    "chip_id": "/sys/class/kgsl/kgsl-3d0/chip_id",
    "gpuclk_hz": "/sys/class/kgsl/kgsl-3d0/gpuclk",
    "max_gpuclk_hz": "/sys/class/kgsl/kgsl-3d0/max_gpuclk",
    "cur_freq_hz": "/sys/class/kgsl/kgsl-3d0/devfreq/cur_freq",
    "available_frequencies_hz": "/sys/class/kgsl/kgsl-3d0/devfreq/available_frequencies",
}
RUNTIME_KEYS = (
    "deviceName",
    "driverName",
    "driverInfo",
    "driverID",
    "vendorID",
    "deviceID",
    "apiVersion",
)


def sha256_file(path):
    path = pathlib.Path(path)
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def parse_memtotal_kib(text):
    match = re.search(r"^MemTotal:\s+(\d+)\s+kB\s*$", text, re.MULTILINE)
    return int(match.group(1)) if match else None


def parse_intish(value):
    if value is None:
        return None
    value = str(value).strip()
    if not value:
        return None
    try:
        number = int(value, 0)
    except ValueError:
        return None
    return {
        "raw": value,
        "hex": f"0x{number:x}",
        "decimal": number,
    }


def adb_command(serial, *args):
    cmd = ["adb"]
    if serial:
        cmd += ["-s", serial]
    cmd += list(args)
    return cmd


def adb_text(serial, *args):
    result = subprocess.run(
        adb_command(serial, *args),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=15,
        check=False,
    )
    if result.returncode != 0:
        return None
    value = result.stdout.replace("\r", "").strip()
    return value or None


def load_runtime(path):
    if not path:
        return None
    data = json.loads(pathlib.Path(path).read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("runtime JSON must be an object")
    return {key: data.get(key) for key in RUNTIME_KEYS}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--serial", help="ADB serial; omitted means the default/only device")
    parser.add_argument("--driver-label", required=True,
                        help="e.g. qualcomm-native, amaral-5.8.17.1-standard, anbernic-dds")
    parser.add_argument("--runtime-json", type=pathlib.Path,
                        help="same-session VkPhysicalDeviceDriverProperties JSON")
    parser.add_argument("--driver-zip", type=pathlib.Path)
    parser.add_argument("--driver-elf", type=pathlib.Path)
    parser.add_argument("--output", type=pathlib.Path, required=True)
    args = parser.parse_args()

    if shutil.which("adb") is None:
        raise SystemExit("adb not found in PATH")

    state = adb_text(args.serial, "get-state")
    if state != "device":
        raise SystemExit(f"ADB device not ready: {state!r}")

    props = {}
    for prop in PROPERTIES:
        props[prop] = adb_text(args.serial, "shell", "getprop", prop)

    meminfo = adb_text(args.serial, "shell", "cat", "/proc/meminfo") or ""
    kgsl = {}
    for name, path in KGSL_FILES.items():
        kgsl[name] = adb_text(args.serial, "shell", "cat", path)

    chip_candidates = []
    for name in ("gpu_chipid", "chipid", "chip_id"):
        parsed = parse_intish(kgsl.get(name))
        if parsed:
            chip_candidates.append({"source": KGSL_FILES[name], **parsed})

    runtime = load_runtime(args.runtime_json)
    runtime_complete = bool(runtime) and all(
        runtime.get(key) is not None for key in
        ("driverName", "driverInfo", "driverID", "vendorID", "deviceID", "apiVersion")
    )

    artifact = {
        "zip_sha256": sha256_file(args.driver_zip) if args.driver_zip else None,
        "elf_sha256": sha256_file(args.driver_elf) if args.driver_elf else None,
    }
    report = {
        "schema": 1,
        "status": "observed-in-shell" if state == "device" else "pending",
        "captured_at_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "driver_label": args.driver_label,
        "adb_selector": "explicit" if args.serial else "default",
        "android": {
            "properties": props,
            "kernel": adb_text(args.serial, "shell", "uname", "-a"),
            "mem_total_kib": parse_memtotal_kib(meminfo),
        },
        "kgsl": {
            "sysfs": kgsl,
            "chip_id_candidates": chip_candidates,
            "note": (
                "A missing sysfs chip id is not evidence that KGSL lacks one. "
                "Turnip obtains its authoritative chip_id from KGSL_PROP_DEVICE_INFO."
            ),
        },
        "vulkan_runtime": runtime,
        "runtime_identity_complete": runtime_complete,
        "artifact": artifact,
        "classification": (
            "observed-in-hardware"
            if chip_candidates and runtime_complete
            else "pending-runtime-or-chip-id"
        ),
        "limitations": [
            "Shell/system Vulkan state does not prove which per-app AdrenoTools driver was loaded.",
            "Use VkPhysicalDeviceDriverProperties from the exact Azahar/Eden session.",
            "No performance conclusion is produced by this collector.",
            "Do not publish the ADB serial; it is intentionally omitted from the report.",
        ],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n",
                           encoding="utf-8")
    print(args.output)


if __name__ == "__main__":
    main()
