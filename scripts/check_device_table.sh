#!/usr/bin/env bash
# Gera a device database do Freedreno numa árvore Mesa já corrigida, sem NDK.
#
# `git apply --check` só prova que o texto do patch casa com o Mesa. Os perfis
# de GPU são código Python executado no build, e uma mudança upstream na API
# do gerador (como a remoção de magic_regs em 17ca6174dcc) quebra o build com
# os patches aplicando limpo. Este passo pega essa classe de falha em segundos.
#
# Uso: check_device_table.sh <mesa_src> [saida.c]
# Requer Mako e PyYAML (requirements-build.txt); PYTHON escolhe o interpretador.
set -euo pipefail

mesa_src="$(cd "${1:?uso: check_device_table.sh <mesa_src> [saida.c]}" && pwd)"
output="${2:-/dev/null}"
python="${PYTHON:-python3}"

gen_dir="$(mktemp -d)"
trap 'rm -rf "${gen_dir}"' EXIT

(cd "${mesa_src}/src/freedreno/registers" &&
  "${python}" gen_header.py --rnn . --xml adreno/a6xx.xml py-defines \
    > "${gen_dir}/a6xx.py")
(cd "${mesa_src}/src/freedreno/common" &&
  "${python}" freedreno_devices.py -p "${gen_dir}" > "${gen_dir}/devices.c")

records="$(grep -c '^   { {' "${gen_dir}/devices.c")"
if [[ "${records}" -lt 1 ]]; then
  echo "Device database vazia em ${mesa_src}" >&2
  exit 1
fi
cp "${gen_dir}/devices.c" "${output}"
echo "Device database gerada: ${records} registros"
