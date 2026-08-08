#!/usr/bin/env bash
set -euo pipefail

[[ "$#" == 1 ]] || { echo "Uso: $0 driver.zip" >&2; exit 2; }
artifact="$(realpath "$1")"
test_root="$(mktemp -d)"
trap 'rm -rf "${test_root}"' EXIT

unzip -t "${artifact}" >/dev/null
mapfile -t entries < <(zipinfo -1 "${artifact}" | LC_ALL=C sort)
[[ "${entries[*]}" == "libvulkan_freedreno.so meta.json" ]]
unzip -q "${artifact}" -d "${test_root}"
driver="${test_root}/libvulkan_freedreno.so"
meta="${test_root}/meta.json"

file "${driver}" | grep -q "ARM aarch64"
readelf -h "${driver}" | grep -q "Machine:.*AArch64"
readelf -d "${driver}" | grep -q "SONAME.*libvulkan_freedreno.so"
readelf -d "${driver}" | grep -q "BIND_NOW"
readelf -W -l "${driver}" | grep -q "GNU_RELRO"
! readelf -W -l "${driver}" | grep "GNU_STACK" | grep -q "RWE"
! readelf -d "${driver}" | grep -q "TEXTREL"
python3 -m json.tool "${meta}" >/dev/null
python3 - "${meta}" <<'PY'
import json, sys
with open(sys.argv[1], encoding="utf-8") as stream:
    meta = json.load(stream)
assert meta["schemaVersion"] == 1
assert meta["libraryName"] == "libvulkan_freedreno.so"
assert meta["minApi"] == 29
assert meta["name"].startswith("Amaral Turnip Universal v")
PY
sha256sum "${artifact}" "${driver}"

