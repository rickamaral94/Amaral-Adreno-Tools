#!/usr/bin/env python3
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]


def load(relative):
    with (ROOT / relative).open(encoding="utf-8") as stream:
        return json.load(stream)


def main():
    lock = load("config/mesa-lock.json")
    evidence = load("evidence/candidates.json")
    sources = load("evidence/sources.json")

    commit = lock["mesa"]["commit"]
    assert re.fullmatch(r"[0-9a-f]{40}", commit), "Mesa commit must be a full SHA"
    assert isinstance(lock["amaral_revision"], int)
    assert lock["amaral_revision"] >= 1
    assert lock["build"]["cpu"] == "armv8-a"
    assert lock["build"]["kmd"] == "kgsl"
    assert sources["primary"][0]["name"] == "Mesa 3D"

    ids = set()
    for item in evidence["candidates"]:
        assert item["id"] not in ids, f"duplicate candidate: {item['id']}"
        ids.add(item["id"])
        assert item["status"] in {
            "proposed", "testing", "approved", "active",
            "reference-only", "rejected"
        }
        if item["kind"].startswith("runtime") and item["status"] == "active":
            gate = item.get("gate", {})
            assert gate.get("visual_pass") is True
            assert gate.get("minimum_runs", 0) >= 5
            assert gate.get("confidence") in {"medium", "high"}
            assert gate.get("families") == ["A6xx", "A7xx", "A8xx"]
        if item.get("patch"):
            assert (ROOT / item["patch"]).is_file(), item["patch"]

    print("Project metadata and evidence gates are valid.")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (AssertionError, KeyError, json.JSONDecodeError) as exc:
        print(f"validation failed: {exc}", file=sys.stderr)
        sys.exit(1)
