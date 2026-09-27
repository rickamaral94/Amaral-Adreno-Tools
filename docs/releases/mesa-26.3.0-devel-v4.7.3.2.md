# Turnip Amaral 26.3.0-devel v4.7.3.2

## Classificação

**Latest estável.**

## Base rastreável

- Mesa: `26.3.0-devel`
- Mesa commit: `90fae16e42e3f33043f1111b9a69a728241ba0b8`
- Mesa HEAD: isl: Drop a standard tiling assertion
- Commit anterior: `82d4f86a0a1e9f76b2de4fa77c6c8e6acaf06aa9`
- Vulkan headers: `1.4.363`
- Backend: Turnip/Freedreno + KGSL
- ABI: Android AArch64 (`armv8-a`)
- Toolchain: Android NDK r29

## Superfície Mesa relevante (12 arquivos)

- `src/compiler/nir/nir_lower_mem_access_bit_sizes.c`
- `src/freedreno/ci/freedreno-a306-fails.txt`
- `src/freedreno/ci/freedreno-a306-flakes.txt`
- `src/freedreno/ci/freedreno-a306-skips.txt`
- `src/freedreno/ci/gitlab-ci.yml`
- `src/freedreno/drm/msm/msm_priv.h`
- `src/util/00-mesa-defaults.conf`
- `src/util/driconf.dtd`
- `src/util/driconf.h`
- `src/util/xmlconfig.c`
- `src/vulkan/runtime/vk_video.c`
- `src/vulkan/runtime/vk_video.h`

## Variantes

- Standard: Android/KGSL universal.
- OneUI: mesmo código e recursos, com o ajuste UBWC isolado para FD740/KGSL.

## Política desta publicação

Atualizações exclusivas do Mesa upstream podem avançar para Latest depois dos
gates de compilação, aplicação dos patches, validação do pacote e
reprodutibilidade byte a byte. Correções comunitárias estritas de estabilidade
também podem ser promovidas após revisão de código e esses mesmos gates quando
já são distribuídas em outro driver e permanecem sem correção posterior
conhecida. Tuning, performance e workarounds continuam exigindo testes A/B.

Não há `TU_DEBUG=sysmem` forçado nos perfis Zelda. O autotuner continua livre
para escolher GMEM/SYSMEM, com a preferência por GMEM já validada na v4.5.
