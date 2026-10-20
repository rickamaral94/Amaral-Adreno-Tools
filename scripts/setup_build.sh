#!/usr/bin/env bash
set -euo pipefail
sudo apt-get update -qq
sudo apt-get install -y bison build-essential file flex glslang-tools pkg-config python3-venv unzip zip
python3 -m venv work/venv
work/venv/bin/pip install --requirement requirements-build.txt
printf '%s\n' "${GITHUB_WORKSPACE}/work/venv/bin" >> "${GITHUB_PATH}"
mkdir -p work/toolchains
archive=work/downloads/android-ndk-r29-linux.zip
mkdir -p work/downloads
if [[ ! -f "$archive" ]]; then
  curl --retry 3 --fail --location --output "$archive" https://dl.google.com/android/repository/android-ndk-r29-linux.zip
fi
# Validate cached downloads as well as fresh downloads. Never cache compiler outputs.
echo "87e2bb7e9be5d6a1c6cdf5ec40dd4e0c6d07c30b  $archive" | sha1sum --check
unzip -q "$archive" -d work/toolchains
mkdir -p dist
{ gcc --version; work/venv/bin/meson --version; work/venv/bin/ninja --version; glslangValidator --version; dpkg-query -W; cat work/toolchains/android-ndk-r29/source.properties; sha256sum "$archive"; } > "dist/BUILD_ENVIRONMENT_${DRIVER_VARIANT}.txt"
