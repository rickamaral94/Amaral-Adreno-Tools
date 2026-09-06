# Turnip Amaral 26.3.0-devel v4.5.1.1

## Classificação

**Latest estável.**

## Base rastreável

- Mesa: `26.3.0-devel`
- Mesa commit: `86158b8c7467cadcd24f8a8cf02aa3bc748f7e3f`
- Commit anterior: `eaa8cb690243d25c9b5ccc40e11a0d0d5a836d0f`
- Vulkan headers: `1.4.359`
- Backend: Turnip/Freedreno + KGSL
- ABI: Android AArch64 (`armv8-a`)
- Toolchain: Android NDK r29

## Superfície Mesa relevante (58 arquivos)

- `meson.build`
- `src/compiler/nir/meson.build`
- `src/compiler/nir/nir.h`
- `src/compiler/nir/nir_divergence_analysis.c`
- `src/compiler/nir/nir_gather_info.c`
- `src/compiler/nir/nir_gather_tcs_info.c`
- `src/compiler/nir/nir_intrinsics.py`
- `src/compiler/nir/nir_lower_atomics.c`
- `src/compiler/nir/nir_lower_explicit_io.c`
- `src/compiler/nir/nir_lower_image_atomics_to_global.c`
- `src/compiler/nir/nir_lower_mem_access_bit_sizes.c`
- `src/compiler/nir/nir_lower_ssbo.c`
- `src/compiler/nir/nir_opt_algebraic.py`
- `src/compiler/nir/nir_opt_barycentric.c`
- `src/compiler/nir/nir_opt_constant_folding.c`
- `src/compiler/nir/nir_opt_gcm.c`
- `src/compiler/nir/nir_opt_intrinsics.c`
- `src/compiler/nir/nir_opt_offsets.c`
- `src/compiler/nir/nir_opt_preamble.c`
- `src/compiler/nir/nir_opt_scalar_array_vars_to_vec.c`
- `src/compiler/nir/nir_opt_sink.c`
- `src/compiler/nir/nir_opt_uub.c`
- `src/compiler/nir/nir_opt_vectorize.c`
- `src/compiler/nir/nir_shader_compiler_options.h`
- `src/compiler/spirv/vtn_alu.c`
- `src/freedreno/ci/freedreno-a200-fails.txt`
- `src/freedreno/ci/freedreno-a750-fails.txt`
- `src/freedreno/computerator/a6xx.cc`
- `src/freedreno/drm-shim/freedreno_noop.c`
- `src/freedreno/fdl/fd6_layout.c`
- `src/freedreno/fdl/fd6_view.cc`
- `src/freedreno/fdl/freedreno_layout.h`
- `src/freedreno/ir3/ir3_a6xx.c`
- `src/freedreno/ir3/ir3_nir.c`
- `src/freedreno/registers/adreno/a5xx.xml`
- `src/freedreno/registers/adreno/a6xx.xml`
- `src/freedreno/registers/adreno/adreno_pm4.xml`
- `src/freedreno/vulkan/tu_buffer.cc`
- `src/freedreno/vulkan/tu_clear_blit.cc`
- `src/freedreno/vulkan/tu_cmd_buffer.cc`
- … e mais 18 arquivos.


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
