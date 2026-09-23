# Turnip Amaral 26.3.0-devel v4.7.2.4

## Classificação

**Latest estável.**

## Base rastreável

- Mesa: `26.3.0-devel`
- Mesa commit: `cdd0cc267728d474d13d30ebc5f345048d77f079`
- Mesa HEAD: aco/optimizer: apply neg/abs to trunc/rndne/floor/ceil/sin
- Commit anterior: `6ac7466d40be92bfec4fe3dfe21376a6af45a8e0`
- Vulkan headers: `1.4.363`
- Backend: Turnip/Freedreno + KGSL
- ABI: Android AArch64 (`armv8-a`)
- Toolchain: Android NDK r29

## Superfície Mesa relevante (44 arquivos)

- `meson.build`
- `src/compiler/nir/nir.h`
- `src/compiler/nir/nir_print.c`
- `src/compiler/nir/nir_range_analysis.c`
- `src/freedreno/ci/freedreno-a200-fails.txt`
- `src/freedreno/ci/freedreno-a200-flakes.txt`
- `src/freedreno/ci/freedreno-a702-fails.txt`
- `src/freedreno/ci/traces-freedreno-restricted.toml`
- `src/freedreno/ci/traces-freedreno.yml`
- `src/freedreno/common/freedreno_devices.py`
- `src/freedreno/drm-shim/freedreno_noop.c`
- `src/freedreno/ir3/ir3.c`
- `src/freedreno/ir3/ir3.h`
- `src/freedreno/ir3/ir3_compiler.c`
- `src/freedreno/ir3/ir3_compiler_nir.c`
- `src/freedreno/ir3/ir3_cp.c`
- `src/freedreno/ir3/ir3_nir.c`
- `src/freedreno/ir3/ir3_nir.h`
- `src/freedreno/ir3/ir3_nir_lower_driver_params_to_ubo.c`
- `src/freedreno/ir3/ir3_postsched.c`
- `src/freedreno/ir3/ir3_rpt.c`
- `src/freedreno/ir3/ir3_sched.c`
- `src/freedreno/ir3/ir3_shader.c`
- `src/freedreno/ir3/ir3_shader.h`
- `src/freedreno/isa/ir3-cat2.xml`
- `src/freedreno/registers/adreno/a2xx.xml`
- `src/freedreno/vulkan/tu_buffer.cc`
- `src/freedreno/vulkan/tu_clear_blit.cc`
- `src/freedreno/vulkan/tu_cmd_buffer.cc`
- `src/freedreno/vulkan/tu_cmd_buffer.h`
- `src/freedreno/vulkan/tu_device.cc`
- `src/freedreno/vulkan/tu_device.h`
- `src/freedreno/vulkan/tu_formats.cc`
- `src/freedreno/vulkan/tu_formats.h`
- `src/freedreno/vulkan/tu_image.cc`
- `src/freedreno/vulkan/tu_nir_lower_multiview.cc`
- `src/freedreno/vulkan/tu_pipeline.cc`
- `src/freedreno/vulkan/tu_shader.cc`
- `src/freedreno/vulkan/tu_shader.h`
- `src/freedreno/vulkan/tu_util.cc`
- … e mais 4 arquivos.

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
