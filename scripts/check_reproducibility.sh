#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
repo_root="$(cd "${script_dir}/.." && pwd)"
repro_root="${REPRO_ROOT:-${repo_root}/work/reproducibility}"
final_output="${OUTPUT_ROOT:-${repo_root}/dist}"
driver_variant="${DRIVER_VARIANT:-standard}"
[[ "${driver_variant}" == "standard" || "${driver_variant}" == "oneui" ]] || {
  echo "DRIVER_VARIANT inválida: ${driver_variant}; use standard ou oneui" >&2
  exit 2
}

build_once() {
  local label="$1"
  local run_root="${repro_root}/${driver_variant}/${label}"
  WORK_ROOT="${run_root}/work" \
  MESA_SRC="${run_root}/mesa" \
  OUTPUT_ROOT="${run_root}/dist" \
  DRIVER_VARIANT="${driver_variant}" \
  NDK_ROOT="${NDK_ROOT:?NDK_ROOT precisa apontar para o Android NDK r29}" \
    "${repo_root}/scripts/build_universal.sh" >/dev/null
}

find_artifact() {
  local directory="$1"
  mapfile -t artifacts < <(find "${directory}" -maxdepth 1 -type f -name 'turnip_amaral_*.zip' | LC_ALL=C sort)
  [[ "${#artifacts[@]}" == 1 ]] || {
    echo "Esperado exatamente um ZIP em ${directory}; encontrados: ${#artifacts[@]}" >&2
    return 1
  }
  printf '%s\n' "${artifacts[0]}"
}

build_once first
build_once second

first_artifact="$(find_artifact "${repro_root}/${driver_variant}/first/dist")"
second_artifact="$(find_artifact "${repro_root}/${driver_variant}/second/dist")"
[[ "$(basename "${first_artifact}")" == "$(basename "${second_artifact}")" ]]
cmp --silent "${first_artifact}" "${second_artifact}" || {
  echo "Falha de reprodutibilidade: os ZIPs são diferentes." >&2
  sha256sum "${first_artifact}" "${second_artifact}" >&2
  exit 1
}

first_extract="${repro_root}/${driver_variant}/first/extracted"
second_extract="${repro_root}/${driver_variant}/second/extracted"
mkdir -p "${first_extract}" "${second_extract}" "${final_output}"
unzip -q "${first_artifact}" -d "${first_extract}"
unzip -q "${second_artifact}" -d "${second_extract}"
cmp --silent \
  "${first_extract}/libvulkan_freedreno.so" \
  "${second_extract}/libvulkan_freedreno.so" || {
  echo "Falha de reprodutibilidade: os ELFs são diferentes." >&2
  exit 1
}

cp "${first_artifact}" "${final_output}/$(basename "${first_artifact}")"
(
  cd "${final_output}"
  sha256sum turnip_amaral_*.zip > SHA256SUMS.txt
  {
    echo "reproducible=true"
    echo "independent_builds=2"
    echo "variant=${driver_variant}"
    echo "artifact=$(basename "${first_artifact}")"
    echo "artifact_sha256=$(sha256sum "$(basename "${first_artifact}")" | cut -d' ' -f1)"
    echo "elf_sha256=$(sha256sum "${first_extract}/libvulkan_freedreno.so" | cut -d' ' -f1)"
  } > "REPRODUCIBILITY_${driver_variant}.txt"
)

cat "${final_output}/REPRODUCIBILITY_${driver_variant}.txt"
