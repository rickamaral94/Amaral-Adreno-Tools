#!/usr/bin/env python3
"""Offline, read-only triage of Eden diagnostic ZIPs; never benchmark certification."""
import argparse
import hashlib
import json
from pathlib import Path
import zipfile


def pick(obj, names):
    return {name: obj[name] for name in names if name in obj}


def summarize(path):
    with zipfile.ZipFile(path) as archive:
        entries = archive.infolist()
        names = [entry.filename for entry in entries]
        if len(names) != len(set(names)):
            raise ValueError("duplicate ZIP entries")
        if sum(entry.file_size for entry in entries) > 64 * 1024 * 1024:
            raise ValueError("diagnostic exceeds 64 MiB uncompressed")
        integrity = "manifest-unavailable"
        if "manifest.json" in names:
            manifest = json.loads(archive.read("manifest.json"))
            listed = [entry["name"] for entry in manifest["files"]]
            if len(listed) != len(set(listed)) or set(listed) != set(names) - {"manifest.json"}:
                raise ValueError("manifest does not cover exactly the archive payload")
            for entry in manifest["files"]:
                data = archive.read(entry["name"])
                if len(data) != entry["bytes"] or hashlib.sha256(data).hexdigest() != entry["sha256"]:
                    raise ValueError("manifest size/hash mismatch")
            integrity = "payload-hashes-verified"
        report = json.loads(archive.read("report.json"))
    if report.get("generator") != "eden-android-diagnostics" or report.get("schema_version") not in (1, 2):
        raise ValueError("unsupported Eden schema")
    native = report["native_summary"]
    android = report["android_summary"]
    gpu = report.get("gpu_timing", {}).get("session", {})
    libraries = report.get("graphics_driver", {}).get("loaded", {}).get("libraries", [])
    driver_hashes = sorted({lib["sha256"] for lib in libraries
                            if Path(lib.get("path", "")).name == "libvulkan_freedreno.so"
                            and lib.get("sha256")})
    settings = report.get("settings", [])
    clock = next((s["value"] for s in settings if s["name"] == "force_max_clock"), None)
    windows = report.get("hitches", {}).get("windows", [])
    return {
        "archive_sha256": hashlib.sha256(Path(path).read_bytes()).hexdigest(),
        "schema": report["schema_version"],
        "integrity": integrity,
        "duration_ms": report["session"]["duration_ms"],
        "samples": report["session"]["samples"],
        "emulator_commit": report["build"]["revision"],
        "driver_elf_sha256": driver_hashes,
        "force_max_clock": clock,
        "settings_sha256": hashlib.sha256(json.dumps(
            sorted((s["category"], s["name"], s["value"]) for s in settings),
            separators=(",", ":")).encode()).hexdigest(),
        "guest_present_fps_avg": report["frame_rate"].get("guest_present_fps_avg"),
        "guest_intervals": pick(native.get("frames", {}).get("guest_present_interval", {}),
                                ["count", "p50_ms", "p99_ms", "max_ms", "skipped_across_pause"]),
        "gpu": pick(gpu, ["coverage_pct", "frames_complete", "frames_partial", "frame_gpu"]),
        "system": pick(android, ["gpu_clock_mhz_kgsl", "thermal_status_max",
                                "battery_temp_c_max", "sampler_cost_ms"]),
        "pipeline_counters": pick(native["counters"], [
            "graphics_pipeline_cache_miss", "compute_pipeline_cache_miss",
            "pipeline_create_failed", "shader_translate_failed",
            "driver_pipeline_cache_hits", "pipeline_feedback_valid"]),
        "waits_by_reason": native.get("fence_wait_by_reason"),
        "hitch_windows": len(windows),
        "hitch_windows_without_pipeline_misses": sum(
            w.get("graphics_pipeline_cache_miss") == 0 and
            w.get("compute_pipeline_cache_miss") == 0 for w in windows),
        "limitations": [
            "Observational capture; not a controlled driver A/B.",
            "Same-window correlation does not establish frame-level causality.",
            "GPU timestamps exclude present blit; waits overlap across threads.",
            "Histogram p99 is not 1% low FPS; missing metrics are not zero.",
            "Battery temperature and Android thermal status do not prove thermal equivalence.",
        ],
    }


def compare(a, b):
    """Report confounders without calculating a misleading speedup."""
    reasons = []
    for key in ("emulator_commit", "settings_sha256", "force_max_clock", "schema"):
        if a[key] != b[key]:
            reasons.append(f"different_{key}")
    if not a["driver_elf_sha256"] or not b["driver_elf_sha256"]:
        reasons.append("missing_loaded_driver_hash")
    elif a["driver_elf_sha256"] == b["driver_elf_sha256"]:
        reasons.append("same_driver_binary")
    if a["system"].get("gpu_clock_mhz_kgsl") != b["system"].get("gpu_clock_mhz_kgsl"):
        reasons.append("different_or_missing_clock_distribution")
    reasons.append("scene_cache_thermal_and_balanced_repetitions_not_established")
    return {"driver_ab_qualified": False, "reasons": reasons}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("archives", nargs="+", type=Path)
    args = parser.parse_args()
    captures = [summarize(path) for path in args.archives]
    comparisons = [{"a": i + 1, "b": j + 1, **compare(a, b)}
                   for i, a in enumerate(captures)
                   for j, b in enumerate(captures) if i < j]
    print(json.dumps({"schema": 1, "captures": captures, "comparisons": comparisons},
                     indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
