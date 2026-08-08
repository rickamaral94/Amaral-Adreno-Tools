#!/usr/bin/env python3
import argparse
import json
import pathlib
import urllib.parse
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[1]
API = "https://gitlab.freedesktop.org/api/v4/projects/mesa%2Fmesa/repository/commits/"


def fetch(ref):
    request = urllib.request.Request(API + urllib.parse.quote(ref, safe=""), headers={"User-Agent": "Amaral-Adreno-Tools"})
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.load(response)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--github-output", type=pathlib.Path)
    args = parser.parse_args()

    with (ROOT / "config/mesa-lock.json").open(encoding="utf-8") as stream:
        lock = json.load(stream)
    current = lock["mesa"]["commit"]
    latest = fetch(lock["mesa"]["branch"])
    changed = latest["id"] != current

    print(f"Pinned: {current}")
    print(f"Latest: {latest['id']} — {latest['title']}")
    print("Update available." if changed else "Already current.")

    if args.github_output:
        with args.github_output.open("a", encoding="utf-8") as stream:
            stream.write(f"update_available={'true' if changed else 'false'}\n")
            stream.write(f"pinned_sha={current}\nlatest_sha={latest['id']}\n")
            stream.write(f"latest_short={latest['short_id']}\n")
    return 2 if changed else 0


if __name__ == "__main__":
    raise SystemExit(main())

