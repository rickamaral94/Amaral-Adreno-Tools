#!/usr/bin/env python3
"""Validate public, sanitized hardware observations without raw diagnostics."""
import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[1]
DATA = ROOT / "evidence" / "hardware-tests"
SHA256 = re.compile(r"[0-9a-f]{64}\Z")
SHA1 = re.compile(r"[0-9a-f]{40}\Z")
CAPTURE = re.compile(r"\d{8}-\d{6}-\d{4}\Z")


def validate_all():
    files = sorted(DATA.glob("*.json"))
    assert files, "hardware test register is empty"
    ids = set()
    for path in files:
        data = json.loads(path.read_text(encoding="utf-8"))
        assert data["schema"] == 1, path
        assert data["context"]["hardware"] and data["context"]["gpu"]
        assert data["context"]["game"] and data["context"]["frontend"]
        assert data["overall_assessment"]
        drivers = data["drivers"]
        assert drivers and data["captures"]
        for driver_id, driver in drivers.items():
            assert driver_id and driver["name"] and driver["proposal"], driver_id
            assert SHA1.fullmatch(driver["mesa_commit"]), driver_id
            assert SHA256.fullmatch(driver["elf_sha256"]), driver_id
            assert SHA256.fullmatch(driver["patchset_sha256"]), driver_id
            assert driver["source_url"].startswith("https://github.com/"), driver_id
            assert driver["status"] in {"observed", "awaiting-hardware"}
            if driver["status"] == "observed":
                assert driver["hardware_result"], driver_id
            else:
                assert driver["hardware_result"] is None, driver_id
        observed = set()
        for capture in data["captures"]:
            capture_id = capture["capture_id"]
            assert CAPTURE.fullmatch(capture_id) and capture_id not in ids
            ids.add(capture_id)
            driver_id = capture["driver_id"]
            assert driver_id in drivers, capture_id
            observed.add(driver_id)
            assert capture["comparison_grade"] in {"observation", "ab-qualified"}
            assert SHA1.fullmatch(capture["emulator_commit"]), capture_id
            assert SHA256.fullmatch(capture["settings_sha256"]), capture_id
            archive = capture["archive_sha256"]
            integrity = capture["payload_integrity"]
            if archive is None:
                assert integrity == "prior-review-only", capture_id
            else:
                assert SHA256.fullmatch(archive), capture_id
                assert integrity in {"payload-hashes-verified", "manifest-unavailable"}
            loaded = capture["loaded_elf_sha256"]
            identity = capture["driver_identity"]
            if identity == "elf-sha256":
                assert loaded == drivers[driver_id]["elf_sha256"], capture_id
            else:
                assert identity == "mesa-version-only" and loaded is None, capture_id
            assert capture["duration_s"] > 0 and capture["fps_avg"] > 0
            timing = [capture.get(f"gpu_ms_p{n}") for n in (50, 90, 99)]
            assert all(x is None for x in timing) or (
                all(isinstance(x, (int, float)) for x in timing)
                and 0 <= timing[0] <= timing[1] <= timing[2]
            ), capture_id
            assert capture["source"] and capture["notes"], capture_id
            source = capture["source"]
            if not source.startswith("https://"):
                assert (ROOT / source).is_file(), source
        for driver_id, driver in drivers.items():
            assert (driver_id in observed) == (driver["status"] == "observed"), driver_id
        document = ROOT / "docs" / "tests" / f"{path.stem}.md"
        assert document.is_file(), document
        article = document.read_text(encoding="utf-8")
        assert all(capture["capture_id"] in article for capture in data["captures"]), path
    return len(ids)


if __name__ == "__main__":
    print(f"Validated {validate_all()} hardware observations.")
