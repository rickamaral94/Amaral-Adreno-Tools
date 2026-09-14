# Turnip Amaral 26.3.0-devel v4.6.1.5

## Classificação

**Latest estável.**

## Base rastreável

- Mesa: `26.3.0-devel`
- Mesa commit: `812098cb7e971724203091cd8746dc7d1969c23f`
- Mesa HEAD: tu: Fix inline uniform update offset
- Commit anterior: `7cda7850edd103ace21aac37d416d2fdf7a282e1`
- Vulkan headers: `1.4.362`
- Backend: Turnip/Freedreno + KGSL
- ABI: Android AArch64 (`armv8-a`)
- Toolchain: Android NDK r29

## Superfície Mesa relevante (18 arquivos)

- `src/freedreno/common/freedreno_common.h`
- `src/freedreno/decode/replay.c`
- `src/freedreno/drm/meson.build`
- `src/freedreno/drm/msm/msm_bo.c`
- `src/freedreno/drm/msm/msm_common.h`
- `src/freedreno/drm/msm/msm_device.c`
- `src/freedreno/drm/msm/msm_pipe.c`
- `src/freedreno/drm/msm/msm_priv.h`
- `src/freedreno/drm/virtio/virtio_bo.c`
- `src/freedreno/ds/fd_pps_driver.cc`
- `src/freedreno/ds/fd_pps_driver.h`
- `src/freedreno/vulkan/tu_descriptor_set.cc`
- `src/freedreno/vulkan/tu_device.cc`
- `src/freedreno/vulkan/tu_knl_drm.h`
- `src/freedreno/vulkan/tu_knl_drm_msm.cc`
- `src/freedreno/vulkan/tu_knl_drm_virtio.cc`
- `src/util/bitpack_helpers.h`
- `src/util/drirc_gen.py`

## Variantes

- Standard: Android/KGSL universal.
- OneUI: mesmo código e recursos, com o ajuste UBWC isolado para FD740/KGSL.

## Política desta publicação

Atualizações exclusivas do Mesa upstream podem avançar para Latest depois dos
gates de compilação, aplicação dos patches, validação do pacote e
reprodutibilidade byte a byte. Mudanças próprias do Amaral permanecem como
pré-release até aprovação em testes A/B.

Não há `TU_DEBUG=sysmem` forçado nos perfis Zelda. O autotuner continua livre
para escolher GMEM/SYSMEM, com a preferência por GMEM já validada na v4.5.
