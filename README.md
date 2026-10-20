# Amaral Adreno Tools

Turnip universal para Android/Qualcomm A6xx, A7xx e A8xx.
**Compatibility first. Performance measured.**

A [Latest](https://github.com/rickamaral94/Amaral-Adreno-Tools/releases/latest)
permanece o controle estável publicado. A linha atual de desenvolvimento é uma
**candidata**, sem CTS/hardware/A-B concluídos. Não há promessa de ganho de FPS.

## Candidata atual: 5.7.9.1

Mesa `27.0.0-devel`, commit `4b0f64ceac6a86af38c1e69cd38cf29f84ba611d`.
Correções upstream de invalidação bindless, coleta de push constants e IR3
(offsets de constantes e ordem do lowering) justificam a avaliação.

Além disso, quatro correções upstream ainda pendentes, revisadas e presas à
família afetada (detalhes nas [notas](docs/releases/mesa-27.0.0-devel-v5.7.9.1.md)):

- **A8xx:** divisão de indirect draws grandes, que causavam GPU fault (MR !44352).
- **A7xx:** bounds check sem sinal na emulação de texel buffer usada por títulos
  D3D12 (MR !45204).
- **A6xx:** invalidação de cache antes da query de transform feedback (MR !41860).
- **Todas:** liberação de referência de BO nos patchpoints de visibility stream
  (MR !45369).

Nenhuma delas é tuning de desempenho ou nova capacidade Vulkan.

Os defaults de GCM, suballocadores e regras BOTW/TOTK voltam ao upstream.
As extensões Amaral de profundidade não são expostas sem qualificação do caminho
habilitado. Os patches anteriores ficam preservados como pesquisa, fora do build.
Essa retirada também pode afetar workloads: compare com a Latest anterior.

## Variantes e GPUs

- **Standard:** ponto de partida universal e variante para Odin 2 Portal/A740.
- **OneUI:** mesmo código, acrescentando somente o ajuste UBWC das duas entradas
  FD740/KGSL, quando o firmware Samsung precisar. Não altera X1-85 ou GPUId(740).
- A740/A750/A830 e demais GPUs seguem o suporte real do snapshot Mesa.
- A810 KGSL, A812 e A825 têm complementos externos isolados por chip ID.
  A825/A812 permanecem experimentais; inclusão no pacote não significa qualificação.
- A840 de dois e três slices usa perfis upstream independentes.

## Build e evidência

`config/mesa-lock.json` fixa Mesa/NDK/API/ABI/KGSL.
`config/patches.json` é a lista única de patches distribuídos e de pesquisa.
`config/version-state.json` separa candidata e último controle estável.

```sh
python3 -m venv work/venv
work/venv/bin/pip install -r requirements-build.txt
PATH="$PWD/work/venv/bin:$PATH" NDK_ROOT=/caminho/android-ndk-r29 \
  DRIVER_VARIANT=standard bash scripts/check_reproducibility.sh
```

Use `DRIVER_VARIANT=oneui` em diretórios de saída separados. Cada variante exige
ZIP, ELF e catálogo idênticos em duas árvores limpas. CI executa variantes em
paralelo e cacheia apenas o download verificado do NDK, nunca objetos compilados.
As releases preservam hashes, manifestos de build, ambiente e catálogos de GPU.
Logs completos ficam nos artifacts da execução por 30 dias.

## Releases

Toda mudança nasce como pre-release. O workflow de promoção exige qualificação
revisada, vinculada ao SHA Mesa, fingerprint e hashes dos artefatos, incluindo
CTS, VVL, hardware, regressões e A/B térmico. Build verde não prova compatibilidade.
A atualização quinzenal ocorre dias **1 e 16 às 07:07 BRT**, com execução manual,
e registra triagem upstream sem compilar automaticamente por número de versão.

Consulte [política](docs/EVIDENCE-POLICY.md), [processo](docs/UPSTREAM-UPDATES.md),
[pesquisa](docs/RESEARCH-PLAN.md) e [protocolo da candidata](docs/VALIDATION-PLAN.md).
