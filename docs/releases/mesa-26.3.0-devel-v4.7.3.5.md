# Turnip Amaral 26.3.0-devel v4.7.3.5

## Classificação

**Latest estável.**

## Base rastreável

- Mesa: `26.3.0-devel`
- Mesa commit: `8ea6e9dd417b99ef2e368436bfd567c81f23b0b2`
- Mesa HEAD: docs: add sha sum for 26.2.4
- Commit anterior: `cec59b299704edc442d930ea9e06ab2edcf5ad7b`
- Vulkan headers: `1.4.363`
- Backend: Turnip/Freedreno + KGSL
- ABI: Android AArch64 (`armv8-a`)
- Toolchain: Android NDK r29

## Superfície Mesa relevante (18 arquivos)

- `meson.build`
- `src/compiler/nir/meson.build`
- `src/freedreno/ir3/ir3_compiler.h`
- `src/freedreno/ir3/ir3_disk_cache.cpp`
- `src/freedreno/ir3/meson.build`
- `src/freedreno/perfcntrs/freedreno_perfcntr.c`
- `src/freedreno/vulkan/tu_clear_blit.cc`
- `src/freedreno/vulkan/tu_device.cc`
- `src/freedreno/vulkan/tu_device.h`
- `src/freedreno/vulkan/tu_knl_drm_msm.cc`
- `src/freedreno/vulkan/tu_knl_drm_virtio.cc`
- `src/freedreno/vulkan/tu_knl_kgsl.cc`
- `src/freedreno/vulkan/tu_queue.cc`
- `src/freedreno/vulkan/tu_shader.cc`
- `src/freedreno/vulkan/tu_suballoc.cc`
- `src/util/blob.h`
- `src/util/xmlconfig.c`
- `src/util/xmlconfig.h`

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
