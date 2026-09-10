# Turnip Amaral 26.3.0-devel v4.6.1.3

## Classificação

**Latest estável.**

## Base rastreável

- Mesa: `26.3.0-devel`
- Mesa commit: `a64d13cf4061514a98ee7492c5c9e3f0bee36902`
- Mesa HEAD: ci,crnm: profiles for uprev VVL
- Commit anterior: `8355a57771bc94b7dbea6b496805a40751056508`
- Vulkan headers: `1.4.362`
- Backend: Turnip/Freedreno + KGSL
- ABI: Android AArch64 (`armv8-a`)
- Toolchain: Android NDK r29

## Superfície Mesa relevante (32 arquivos)

- `src/compiler/nir/nir.h`
- `src/compiler/nir/nir_clone.c`
- `src/compiler/nir/nir_divergence_analysis.c`
- `src/compiler/nir/nir_instr_set.c`
- `src/compiler/nir/nir_lower_non_uniform_access.c`
- `src/compiler/nir/nir_lower_tex.c`
- `src/compiler/nir/nir_opt_non_uniform_access.c`
- `src/compiler/nir/nir_serialize.c`
- `src/freedreno/ci/deqp-freedreno-a530.toml`
- `src/freedreno/ci/freedreno-a530-fails.txt`
- `src/freedreno/ci/gitlab-ci.yml`
- `src/freedreno/common/freedreno_dev_info.h`
- `src/freedreno/common/freedreno_devices.py`
- `src/freedreno/common/freedreno_rd_output.c`
- `src/freedreno/ir3/ir3.h`
- `src/freedreno/ir3/ir3_compiler_nir.c`
- `src/freedreno/ir3/ir3_legalize.c`
- `src/freedreno/ir3/ir3_nir.c`
- `src/freedreno/vulkan/tu_buffer.cc`
- `src/freedreno/vulkan/tu_cmd_buffer.cc`
- `src/freedreno/vulkan/tu_device.cc`
- `src/freedreno/vulkan/tu_device.h`
- `src/freedreno/vulkan/tu_image.cc`
- `src/freedreno/vulkan/tu_knl.cc`
- `src/freedreno/vulkan/tu_knl.h`
- `src/freedreno/vulkan/tu_knl_drm.cc`
- `src/freedreno/vulkan/tu_knl_drm.h`
- `src/freedreno/vulkan/tu_knl_drm_msm.cc`
- `src/freedreno/vulkan/tu_knl_drm_virtio.cc`
- `src/freedreno/vulkan/tu_knl_kgsl.cc`
- `src/freedreno/vulkan/tu_shader.cc`
- `src/vulkan/runtime/rmv/vk_rmv_exporter.c`

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
