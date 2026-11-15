# Reprodução de pipeline fora do aparelho

Ferramenta de pesquisa. Compila um par VS/FS em SPIR-V no Turnip, com o drm-shim emulando uma Adreno, e imprime as
estatísticas e as representações internas (`NIR from SPIRV`, `Final NIR`, `IR3 Assembly`). Serve para iterar
mudanças no NIR/ir3 sem depender de uma rodada no aparelho.

Os SPIR-V de jogos vêm dos zips do Rick e são derivados do jogo. **Eles não entram neste repositório.** Aqui ficam
só o harness e os números agregados nas auditorias.

## Build do Turnip para o host

A partir de uma árvore Mesa com o patchset aplicado (`tools/apply_patches.py`):

```sh
meson setup build-host-shim -Dbuildtype=debugoptimized -Dplatforms= -Dgallium-drivers= \
  -Dvulkan-drivers=freedreno -Dfreedreno-kmds=msm -Dtools=drm-shim -Dglx=disabled -Degl=disabled \
  -Dgbm=disabled -Dllvm=disabled -Dzstd=disabled -Dvalgrind=disabled -Dlibunwind=disabled
ninja -C build-host-shim
```

Dependências do host: `libdrm-dev`, `libexpat1-dev`, `zlib1g-dev`, `libvulkan-dev`, `bison`, `flex`, mais meson, mako e
pyyaml.

## Uso

```sh
gcc -O1 -o repro repro.c -lvulkan
export VK_ICD_FILENAMES=build-host-shim/src/freedreno/vulkan/freedreno_devenv_icd.x86_64.json
export LD_PRELOAD=build-host-shim/src/freedreno/drm-shim/libfreedreno_noop_drm_shim.so
export FD_GPU_ID=740 IR3_SHADER_DEBUG=nocache MESA_SHADER_CACHE_DISABLE=true
./repro vs.spv fs.spv        # só estatísticas
./repro vs.spv fs.spv ir     # estatísticas + NIR inicial, NIR final e IR3
```

`FD_GPU_ID` aceita os ids da tabela do drm-shim (`src/freedreno/drm-shim/freedreno_noop.c`). O `740` usa o chip id
`0x43050a01`, igual ao do Odin 2 Portal.

O layout do pipeline segue o do Gtavport móvel (`gtav-recomp`, `backend.cpp`):

| Set | Conteúdo |
| --- | --- |
| 0–2 | 32768 imagens amostradas, parcialmente vinculadas, com contagem variável e update-after-bind |
| 3 | 1024 samplers |
| 4 | três UBOs dinâmicos |
| push constant | 24 bytes |

O alvo é RGBA16F + D32, com spec constant 0 = 2. Se o port usar `early_tests`, insira
`OpExecutionMode %main EarlyFragmentTests` no FS antes, com `spirv-dis`/`spirv-as` na versão original do módulo. Para
outros ports, ajuste o layout e o estado no `repro.c`.

## Validação

Para o `EFEADDD82B576B06` do Gtavport (15/11), o harness reproduz as estatísticas do aparelho: 48 registradores,
4 waves, 400 STP, 636 LDP e ~8100 instruções.
