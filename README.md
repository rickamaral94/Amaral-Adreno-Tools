# Amaral Adreno Tools

Turnip universal para Android/Qualcomm A6xx, A7xx e A8xx.
**Compatibility first. Performance measured.**

A [Latest](https://github.com/rickamaral94/Amaral-Adreno-Tools/releases/latest)
permanece o controle estável publicado. A linha atual de desenvolvimento é uma
**candidata**, sem CTS/hardware/A-B concluídos. Não há promessa de ganho de FPS.

## Candidata atual

**5.8.17.1**: Mesa `27.0.0-devel`, commit `fd8ef2befafd01190e33f12dbfd109b924c8ebc3`
(main de 31/10/2026), headers Vulkan `1.4.366`. Inclui as candidatas de teste
5.7.14.1 a 5.7.16.1 e o patch `0009`, que remove a cópia do estado do programa
a cada `vkCmdBindPipeline`. Hardware desta Mesa, CTS e VVL: not-run. Veja as
[notas](docs/releases/mesa-27.0.0-devel-v5.8.17.1.md).

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

Build e publicação são separados: pushes executam checks; `build-candidate.yml`
compila para avaliação e `publish-candidate.yml` publica somente por execução
manual após revisão técnica. Toda mudança nasce como pre-release. O workflow de promoção exige qualificação
revisada, vinculada ao SHA Mesa, fingerprint e hashes dos artefatos, incluindo
CTS, VVL, hardware, regressões e A/B térmico. Build verde não prova compatibilidade.
A atualização quinzenal ocorre dias **1 e 16 às 07:07 BRT**, com execução manual,
e registra triagem upstream sem compilar automaticamente por número de versão.

Consulte [política](docs/EVIDENCE-POLICY.md), [processo](docs/UPSTREAM-UPDATES.md),
[pesquisa](docs/RESEARCH-PLAN.md) e [protocolo da candidata](docs/VALIDATION-PLAN.md).

A [reavaliação com logs Eden e fontes Cemu](docs/audits/2026-10-20-diagnostics.md)
detalha o benefício esperado por família e as limitações da candidata 5.7.8.1.

## Testes em hardware

O [registro de testes](docs/tests/README.md) reúne driver, aparelho, proposta,
resultado observado e limites da comparação. Inclui as capturas de Little
Nightmares no Odin 2 Portal e um [modelo](docs/tests/TEMPLATE.md) para novos
testes A6xx, A7xx e A8xx. Os dados públicos são selecionados e não contêm logs
brutos ou informações privadas do dispositivo.

## Colaboração entre agentes

As IAs do projeto se coordenam pelo branch `collab/channel`; veja
[COLLABORATION.md](docs/COLLABORATION.md) e o prompt compartilhado.
