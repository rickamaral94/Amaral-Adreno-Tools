#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
repo_root="$(cd "${script_dir}/.." && pwd)"
work_root="${WORK_ROOT:-${repo_root}/work}"
driver_variant="${DRIVER_VARIANT:-standard}"
case "${driver_variant}" in
  standard)
    artifact_suffix=""
    driver_name_suffix=""
    ;;
  oneui)
    artifact_suffix="_oneUI"
    driver_name_suffix=" OneUI"
    ;;
  *)
    echo "DRIVER_VARIANT inválida: ${driver_variant}; use standard ou oneui" >&2
    exit 2
    ;;
esac
mesa_src="${MESA_SRC:-${work_root}/mesa-${driver_variant}}"
ndk_root="${NDK_ROOT:-${work_root}/toolchains/android-ndk-r29}"
output_root="${OUTPUT_ROOT:-${repo_root}/dist}"
build_dir="${work_root}/build-${driver_variant}"
install_root="${work_root}/install-${driver_variant}"
package_dir="${work_root}/package-${driver_variant}"
lock_file="${repo_root}/config/mesa-lock.json"

read_lock() {
  python3 - "${lock_file}" "$1" <<'PY'
import json, sys
with open(sys.argv[1], encoding="utf-8") as stream:
    value = json.load(stream)
for part in sys.argv[2].split("."):
    value = value[part]
print(value)
PY
}

expected_commit="$(read_lock mesa.commit)"
mesa_url="$(read_lock mesa.repository)"
amaral_revision="$(read_lock amaral_revision)"
android_api="$(read_lock build.android_api)"

if [[ ! -d "${mesa_src}/.git" ]]; then
  mkdir -p "$(dirname "${mesa_src}")"
  git init "${mesa_src}"
  git -C "${mesa_src}" remote add origin "${mesa_url}"
  git -C "${mesa_src}" fetch --depth=1 origin "${expected_commit}"
  git -C "${mesa_src}" checkout --detach FETCH_HEAD
fi

actual_commit="$(git -C "${mesa_src}" rev-parse HEAD)"
if [[ "${actual_commit}" != "${expected_commit}" ]]; then
  echo "Mesa incorreto: esperado ${expected_commit}, encontrado ${actual_commit}" >&2
  exit 1
fi

apply_patch_once() {
  local patch_file="$1"
  if ! git -C "${mesa_src}" apply --reverse --check "${patch_file}" >/dev/null 2>&1; then
    git -C "${mesa_src}" apply --check "${patch_file}"
    git -C "${mesa_src}" apply "${patch_file}"
  fi
}

apply_patch_once "${repo_root}/patches/0001-android-ndk-r29-compat.patch"
apply_patch_once "${repo_root}/patches/0002-a825-experimental.patch"
apply_patch_once "${repo_root}/patches/0004-depth-extensions.patch"
apply_patch_once "${repo_root}/patches/0005-a740-aurora-performance.patch"
apply_patch_once "${repo_root}/patches/0006-emulator-compat-driconf.patch"
if [[ "${driver_variant}" == "oneui" ]]; then
  apply_patch_once "${repo_root}/patches/0003-oneui-ubwc.patch"
elif git -C "${mesa_src}" apply --reverse --check \
    "${repo_root}/patches/0003-oneui-ubwc.patch" >/dev/null 2>&1; then
  echo "A árvore Mesa da variante standard contém o patch OneUI." >&2
  exit 1
fi
git -C "${mesa_src}" diff --check
mapfile -t changed_source_files < <(git -C "${mesa_src}" diff --name-only | LC_ALL=C sort)
expected_source_files=(
  "include/android_stub/cutils/native_handle.h"
  "src/freedreno/common/freedreno_devices.py"
  "src/freedreno/drm-shim/freedreno_noop.c"
  "src/freedreno/ir3/ir3_nir.c"
  "src/freedreno/vulkan/00-turnip-defaults.conf"
  "src/freedreno/vulkan/tu_device.cc"
  "src/freedreno/vulkan/tu_pipeline.cc"
  "src/util/u_gralloc/u_gralloc_fallback.c"
  "src/vulkan/runtime/vk_android.c"
)
if [[ "${changed_source_files[*]}" != "${expected_source_files[*]}" ]]; then
  echo "Alterações inesperadas na árvore Mesa:" >&2
  printf '  %s\n' "${changed_source_files[@]}" >&2
  exit 1
fi

ndk_bin="${ndk_root}/toolchains/llvm/prebuilt/linux-x86_64/bin"
ndk_sysroot="${ndk_root}/toolchains/llvm/prebuilt/linux-x86_64/sysroot"

ensure_ndk_symlink() {
  local link_path="$1"
  local expected_target="$2"

  if [[ -L "${link_path}" ]]; then
    [[ "$(readlink "${link_path}")" == "${expected_target}" ]]
    return
  fi
  if [[ -f "${link_path}" && "$(< "${link_path}")" == "${expected_target}" ]]; then
    ln -sf "${expected_target}" "${link_path}"
    return
  fi
  echo "Link do NDK inválido: ${link_path} -> ${expected_target}" >&2
  exit 1
}

ensure_ndk_symlink "${ndk_bin}/clang++" "clang"
ensure_ndk_symlink "${ndk_bin}/ld.lld" "lld"
ensure_ndk_symlink "${ndk_bin}/llvm-strip" "llvm-objcopy"

for required in meson ninja flex bison glslangValidator pkg-config python3 git zip unzip zipinfo file readelf sha256sum; do
  command -v "${required}" >/dev/null
done
test -x "${ndk_bin}/aarch64-linux-android${android_api}-clang" || {
  echo "Android NDK r29 não encontrado em ${ndk_root}" >&2
  exit 1
}

mkdir -p "${work_root}" "${output_root}" "${work_root}/pkgconfig-cross"
cross_file="${work_root}/android-universal.ini"
native_file="${work_root}/native-universal.ini"
pkg_config="$(command -v pkg-config)"

sed -e "s|@NDK_SYSROOT@|${ndk_sysroot}|g" -e "s|@ANDROID_API@|${android_api}|g" \
  "${repo_root}/build-aux/zlib.pc.in" > "${work_root}/pkgconfig-cross/zlib.pc"
sed -e "s|@NDK_BIN@|${ndk_bin}|g" -e "s|@NDK_SYSROOT@|${ndk_sysroot}|g" \
  -e "s|@ANDROID_API@|${android_api}|g" -e "s|@PKG_CONFIG@|${pkg_config}|g" \
  -e "s|@PKG_CONFIG_LIBDIR@|${work_root}/pkgconfig-cross|g" \
  "${repo_root}/build-aux/android-aarch64.ini.in" > "${cross_file}"
sed -e "s|@NATIVE_CC@|$(command -v gcc)|g" -e "s|@NATIVE_CPP@|$(command -v g++)|g" \
  -e "s|@NATIVE_AR@|$(command -v ar)|g" -e "s|@NATIVE_STRIP@|$(command -v strip)|g" \
  -e "s|@PKG_CONFIG@|${pkg_config}|g" \
  "${repo_root}/build-aux/native-linux.ini.in" > "${native_file}"

export SOURCE_DATE_EPOCH="$(git -C "${mesa_src}" show -s --format=%ct HEAD)"
export TZ=UTC LC_ALL=C PYTHONHASHSEED=0
setup_mode=()
[[ -f "${build_dir}/build.ninja" ]] && setup_mode+=(--wipe)

meson setup "${build_dir}" "${mesa_src}" "${setup_mode[@]}" \
  --wrap-mode=nofallback --cross-file "${cross_file}" --native-file "${native_file}" \
  --prefix "${install_root}" -Dbuildtype=release -Db_ndebug=true -Dstrip=true \
  -Dplatforms=android -Dvideo-codecs= -Dplatform-sdk-version=36 -Dandroid-stub=true \
  -Dgallium-drivers= -Dvulkan-drivers=freedreno -Dvulkan-beta=true \
  -Dfreedreno-kmds=kgsl -Degl=disabled -Dglx=disabled \
  -Dandroid-libbacktrace=disabled -Dzstd=disabled \
  -Dshader-cache=enabled
ninja -C "${build_dir}" install

driver_path="${install_root}/lib/libvulkan_freedreno.so"
test -f "${driver_path}"
mesa_version="$(tr -d '\r\n' < "${mesa_src}/VERSION")"
vk_header_version="$(sed -n 's/^#define VK_HEADER_VERSION \([0-9][0-9]*\)$/\1/p' "${mesa_src}/include/vulkan/vulkan_core.h")"
package_basename="turnip_amaral_${mesa_version}_v${amaral_revision}${artifact_suffix}"
artifact_path="${output_root}/${package_basename}.zip"

rm -rf "${package_dir}"
rm -f "${artifact_path}"
mkdir -p "${package_dir}"
cp "${driver_path}" "${package_dir}/libvulkan_freedreno.so"
sed -e "s|@AMARAL_REVISION@|${amaral_revision}|g" -e "s|@ANDROID_API@|${android_api}|g" \
  -e "s|@MESA_VERSION@|${mesa_version}|g" \
  -e "s|@DRIVER_NAME_SUFFIX@|${driver_name_suffix}|g" \
  -e "s|@VK_HEADER_VERSION@|${vk_header_version}|g" \
  "${repo_root}/build-aux/meta.json.in" > "${package_dir}/meta.json"
touch -d "@${SOURCE_DATE_EPOCH}" "${package_dir}/libvulkan_freedreno.so" "${package_dir}/meta.json"
(cd "${package_dir}" && zip -X -9 -q "${artifact_path}" libvulkan_freedreno.so meta.json)
(cd "${output_root}" && sha256sum "${package_basename}.zip" > SHA256SUMS.txt)
"${repo_root}/scripts/validate_artifact.sh" "${artifact_path}"
echo "${artifact_path}"
