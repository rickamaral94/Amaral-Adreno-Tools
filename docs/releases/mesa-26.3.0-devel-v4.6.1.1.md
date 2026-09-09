# Turnip Amaral 26.3.0-devel v4.6.1.1

## Classificação

**Latest estável.**

## Base rastreável

- Mesa: `26.3.0-devel`
- Mesa commit: `cab1821ef75f20338424b8d2c66cdae87b345454`
- Mesa HEAD: broadcom/ci: update expected results
- Commit anterior: `04c9a2eefecff44ea087a445718402e71da4510d`
- Vulkan headers: `1.4.362`
- Backend: Turnip/Freedreno + KGSL
- ABI: Android AArch64 (`armv8-a`)
- Toolchain: Android NDK r29

## Superfície Mesa relevante (24 arquivos)

- `include/vulkan/vulkan_core.h`
- `include/vulkan/vulkan_ubm.h`
- `meson.build`
- `src/compiler/nir/nir.h`
- `src/compiler/nir/nir_builder.h`
- `src/compiler/nir/nir_opt_large_constants.c`
- `src/compiler/nir/nir_opt_load_store_vectorize.c`
- `src/compiler/nir/nir_opt_uub.c`
- `src/compiler/nir/nir_print.c`
- `src/compiler/nir/nir_range_analysis.c`
- `src/compiler/nir/nir_serialize.c`
- `src/compiler/spirv/spirv_to_nir.c`
- `src/freedreno/ci/freedreno-a306-fails.txt`
- `src/freedreno/ci/freedreno-a530-fails.txt`
- `src/freedreno/ci/freedreno-a618-fails.txt`
- `src/freedreno/ir3/ir3_compiler_nir.c`
- `src/freedreno/ir3/ir3_nir.c`
- `src/freedreno/ir3/ir3_nir_move_varying_inputs.c`
- `src/freedreno/ir3/meson.build`
- `src/util/shader_stats.xml`
- `src/util/u_hexdump.h`
- `src/vulkan/registry/vk.xml`
- `src/vulkan/runtime/vk_android.c`
- `src/vulkan/wsi/wsi_common_wayland.c`

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
