# Turnip Amaral 26.3.0-devel v4.6.1.6

## Classificação

**Latest estável.**

## Base rastreável

- Mesa: `26.3.0-devel`
- Mesa commit: `0d355084f070f8de919b9885a1d26296cd1897f6`
- Mesa HEAD: ac: explain FMASK
- Commit anterior: `812098cb7e971724203091cd8746dc7d1969c23f`
- Vulkan headers: `1.4.362`
- Backend: Turnip/Freedreno + KGSL
- ABI: Android AArch64 (`armv8-a`)
- Toolchain: Android NDK r29

## Superfície Mesa relevante (25 arquivos)

- `meson.build`
- `src/compiler/nir/nir.c`
- `src/compiler/nir/nir_divergence_analysis.c`
- `src/freedreno/common/freedreno_dev_info.h`
- `src/freedreno/common/freedreno_devices.py`
- `src/freedreno/vulkan/00-turnip-defaults.conf`
- `src/freedreno/vulkan/tu_clear_blit.cc`
- `src/freedreno/vulkan/tu_cmd_buffer.cc`
- `src/freedreno/vulkan/tu_cmd_buffer.h`
- `src/freedreno/vulkan/tu_device.cc`
- `src/freedreno/vulkan/tu_drirc_gen.py`
- `src/freedreno/vulkan/tu_image.cc`
- `src/freedreno/vulkan/tu_pass.cc`
- `src/freedreno/vulkan/tu_pass.h`
- `src/freedreno/vulkan/tu_query_pool.cc`
- `src/freedreno/vulkan/tu_shader.cc`
- `src/freedreno/vulkan/tu_shader.h`
- `src/util/u_gralloc/meson.build`
- `src/util/u_gralloc/u_gralloc_imapper4_api.cpp`
- `src/util/u_gralloc/u_gralloc_imapper5_api.cpp`
- `src/vulkan/runtime/meson.build`
- `src/vulkan/runtime/vk_debug_utils.c`
- `src/vulkan/runtime/vk_device.c`
- `src/vulkan/runtime/vk_device.h`
- `src/vulkan/wsi/wsi_common_metal_layer.m`

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
